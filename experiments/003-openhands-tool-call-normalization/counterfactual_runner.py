#!/usr/bin/env python3
"""Disposable, non-destructive admission-policy experiment for Experiment 003.

This file does not modify OpenHands. It temporarily replaces the converter's
preprocessor in-process, runs a fixed corpus, and observes a test-local
ResponseDispatchMixin seam that never invokes a real Agent action.
"""

from __future__ import annotations

import json
import re
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from types import SimpleNamespace
from typing import Callable

from openhands.sdk.agent.response_dispatch import (
    LLMResponseType,
    ResponseDispatchMixin,
    classify_response,
)
from openhands.sdk.llm import Message, MessageToolCall, TextContent
from openhands.sdk.llm.exceptions import FunctionCallConversionError, FunctionCallValidationError
from openhands.sdk.llm.mixins import fn_call_converter as converter

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "terminal",
            "description": "Test-local terminal schema; never executed.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": "Test-local finish schema; never executed.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
    },
]

VALID = "<tool_call>terminal\n<parameter=command>ls</parameter>\n</tool_call>"
RAW_PWD = "<tool_call>terminal\n<parameter=command>pwd</parameter>\n</tool_call>"

FIXTURES = {
    "exact_raw": VALID,
    "leading_prose": "I will inspect the directory.\n" + VALID,
    "trailing_prose": VALID + "\nThis is the command I chose.",
    "markdown_fenced": "Documentation example:\n```xml\n" + VALID + "\n```",
    "quoted_documentation": "> Example action:\n> " + VALID.replace("\n", "\n> "),
    "missing_outer_close": "<tool_call>terminal\n<parameter=command>ls</parameter>",
    "truncated_parameter": "<tool_call>terminal\n<parameter=command>ls",
    "two_raw_wrappers": VALID + "\n" + RAW_PWD,
    "plain_prose": "The literal <tool_call>NAME syntax is documented here.",
    "canonical": "<function=terminal>\n<parameter=command>ls</parameter>\n</function>",
    "canonical_plus_raw": "<function=terminal>\n<parameter=command>ls</parameter>\n</function>\n" + VALID,
    "literal_closer": "<tool_call>terminal\n<parameter=command>printf '</tool_call>'</parameter>\n</tool_call>",
    "unknown_tool": "<tool_call>unknown_tool\n<parameter=command>ls</parameter>\n</tool_call>",
    "invalid_parameter": "<tool_call>terminal\n<parameter=not_command>ls</parameter>\n</tool_call>",
    "zero_parameter": "<tool_call>finish\n</tool_call>",
}

A_OPEN = re.compile(r"<tool_call>\s*([A-Za-z_][\w.-]*)\s*\n(?=\s*<parameter=)")
RAW_NAME = re.compile(r"[A-Za-z_][\w.-]*\Z")
PARAM = re.compile(converter.FN_PARAM_REGEX_PATTERN, re.DOTALL)


def baseline_preprocess(original: Callable[[str], str]) -> Callable[[str], str]:
    """Public-PR-style constrained opener rewrite; intentionally not hardened."""

    def preprocess(content: str) -> str:
        content = original(content)
        if "<function=" in content:
            return content
        content, replaced = A_OPEN.subn(r"<function=\1>\n", content, count=1)
        if replaced:
            content = re.sub(r"</tool_call>(\s*)\Z", r"</function>\1", content, count=1)
        return content

    return preprocess


def target_preprocess(original: Callable[[str], str]) -> Callable[[str], str]:
    """Whole-message raw-wrapper admission; only canonical syntax remains broad."""

    def preprocess(content: str) -> str:
        content = original(content)
        if "<function=" in content:
            return content

        match = re.fullmatch(
            r"\s*<tool_call>\s*([^>\s]+)\s*\n(.*)</tool_call>\s*", content, re.DOTALL
        )
        if not match:
            return content

        name, body = match.groups()
        if not RAW_NAME.fullmatch(name) or "<tool_call>" in body:
            return content

        parameter_matches = list(PARAM.finditer(body))
        if not parameter_matches:
            return content
        remaining = PARAM.sub("", body)
        if remaining.strip():
            return content

        return f"<function={name}>\n{body}</function>"

    return preprocess


@contextmanager
def patched_preprocess(replacement: Callable[[Callable[[str], str]], Callable[[str], str]] | None):
    original = converter._preprocess_model_output
    if replacement is not None:
        converter._preprocess_model_output = replacement(original)
    try:
        yield
    finally:
        converter._preprocess_model_output = original


class DispatchProbe(ResponseDispatchMixin):
    """Test-only dispatch seam: records action eligibility and never runs tools."""

    def __init__(self) -> None:
        self.eligible_calls: list[MessageToolCall] = []
        self.executed_batches: list[list[object]] = []

    def _get_action_event(self, tool_call: MessageToolCall, **_: object) -> object:
        self.eligible_calls.append(tool_call)
        return object()

    def _requires_user_confirmation(self, *_: object) -> bool:
        return False

    def _execute_actions(self, _conversation: object, action_events: list[object], _on_event: object) -> None:
        self.executed_batches.append(action_events)

    def _maybe_emit_vllm_tokens(self, *_: object) -> None:
        return None


@dataclass
class Result:
    content: str | None
    tool_call_count: int
    tool_name: str | None
    arguments: dict[str, object] | None
    normalization_occurred: bool
    classification: str | None
    dispatch_eligible: bool
    action_event_count: int
    error: str | None


def as_message(output: dict) -> Message:
    content = output.get("content") or ""
    text = content if isinstance(content, str) else str(content)
    calls = [
        MessageToolCall(
            id=call["id"],
            name=call["function"]["name"],
            arguments=call["function"]["arguments"],
            origin="completion",
        )
        for call in output.get("tool_calls", [])
    ]
    return Message(
        role="assistant",
        content=[TextContent(text=text)] if text else [],
        tool_calls=calls or None,
    )


def run_one(content: str, replacement: Callable[[Callable[[str], str]], Callable[[str], str]] | None) -> Result:
    with patched_preprocess(replacement):
        preprocessed = converter._preprocess_model_output(content)
        normalized = (
            "<tool_call>" in content
            and "<function=" not in content
            and "<function=" in preprocessed
        )
        try:
            output = converter.convert_non_fncall_messages_to_fncall_messages(
                [{"role": "assistant", "content": content}], TOOLS
            )[0]
        except (FunctionCallConversionError, FunctionCallValidationError, ValueError, KeyError) as exc:
            return Result(None, 0, None, None, normalized, None, False, 0, f"{type(exc).__name__}: {exc}")
    calls = output.get("tool_calls", [])
    message = as_message(output)
    classification = classify_response(message)
    probe = DispatchProbe()
    if classification is LLMResponseType.TOOL_CALLS:
        probe._handle_tool_calls(
            message,
            SimpleNamespace(id="counterfactual"),
            SimpleNamespace(),
            SimpleNamespace(security_analyzer=None),
            lambda _event: None,
        )
    call = calls[0] if calls else None
    return Result(
        content=output.get("content"),
        tool_call_count=len(calls),
        tool_name=call["function"]["name"] if call else None,
        arguments=json.loads(call["function"]["arguments"]) if call else None,
        normalization_occurred=normalized,
        classification=classification.value,
        dispatch_eligible=bool(probe.eligible_calls),
        action_event_count=sum(len(batch) for batch in probe.executed_batches),
        error=None,
    )


def main() -> None:
    policies = {"current_main": None, "baseline_A": baseline_preprocess, "target_B": target_preprocess}
    results = {
        fixture: {policy: asdict(run_one(content, replacement)) for policy, replacement in policies.items()}
        for fixture, content in FIXTURES.items()
    }
    print(json.dumps({"fixtures": FIXTURES, "results": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
