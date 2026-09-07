# Experiment 003 — Frozen Brief

**Working title:** Safe recovery of malformed non-native tool-call wrappers  
**Frozen:** 2026-09-07  
**Scope:** Starting state before the competent conventional baseline and TARGET(AI) treatment. Do not revise this document after the treatment begins; record later discoveries separately.

## Problem statement

In the non-native function-calling path, `convert_non_fncall_messages_to_fncall_messages()` accepts assistant content and may promote it into a structured SDK `tool_calls` entry. At the inspected revision, a deterministic malformed wrapper of this exact shape is not recognized:

```text
<tool_call>TOOL_NAME
<parameter=...>...</parameter>
</tool_call>
```

The canonical parser expects `<function=TOOL_NAME>...</function>`. The malformed wrapper therefore remains assistant text and produces no structured tool call. The bounded problem is to decide how this specific representation may be recovered safely without promoting ordinary assistant text into an executable agent action.

## Exact bounded scope and explicit exclusion

**In scope:** deterministic SDK conversion of the raw wrapper above under the non-native function-calling path, including the conversion result’s use as the structured-call input to a focused safe dispatch path.

**Explicitly excluded:** the GLM raw-channel-token form (`<|open|>...<|sep|>`) discussed in issue #4540. A maintainer’s issue analysis attributes that form to Synthetic’s inference-server/parser configuration and says LiteLLM treats Synthetic as an OpenAI-compatible passthrough. It is not an SDK converter repair target for this experiment.

This experiment does not test paid/provider infrastructure, model quality, or a production Synthetic endpoint.

## Source and inspected revision

| Item | Value |
| --- | --- |
| Issue | [OpenHands/software-agent-sdk#4540](https://github.com/OpenHands/software-agent-sdk/issues/4540) |
| Repository | [OpenHands/software-agent-sdk](https://github.com/OpenHands/software-agent-sdk) |
| Branch | `main` |
| Inspected revision | `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1` |
| Revision commit | `fix(ci): centralize release publication dispatches (#4886)` |
| Candidate status at freeze | Issue open; deterministic converter reproduction fails on current `main` |
| Related public proposal | [PR #4608](https://github.com/OpenHands/software-agent-sdk/pull/4608), open and unmerged, head `4f3b6473342d320cc720afbbaead1c9e7deec823` |

## Classification and starting evidence

### FACT — issue and reproduction

- **Provenance:** [issue #4540](https://github.com/OpenHands/software-agent-sdk/issues/4540), opened 2026-08-19 and open at freeze. Its acceptance criteria require recovery of a `<tool_call>`-wrapped response and non-conversion of plain prose.
- **Provenance:** local candidate-screening execution against the inspected revision. Given `terminal` and `command=ls`, the supplied wrapper produced no `tool_calls`; the raw wrapper remained assistant content. This used a disposable local virtual environment and no provider credentials, source modifications, or upstream actions.
- **Provenance:** current `fn_call_converter.py` lines 83–86, 585–611, and 780–911. The canonical function regex accepts `<function=...>...</function>`; preprocessing strips a `<tool_call>` wrapper only when it immediately precedes an existing canonical opener. The raw-name wrapper has no canonical opener, so no function match is found and the original message is returned.

### FACT — representation and runtime boundary

- **Provenance:** `convert_non_fncall_messages_to_fncall_messages()` deep-copies messages, then delegates assistant content to `_convert_assistant_to_fncall()`. A match yields a structured call containing a name and JSON arguments; no match returns the message as content.
- **Provenance:** `openhands-sdk/openhands/sdk/agent/response_dispatch.py` classifies a response with `message.tool_calls` as `TOOL_CALLS`, which enters tool-call handling. Promotion is therefore a security-relevant content-to-action boundary, not cosmetic text cleanup.
- **Provenance:** current converter prompt suffix instructs models to emit one function call per message. The existing converter constructs one call per assistant message with index `1`.

### FACT — current tests and history

- **Provenance:** current `tests/sdk/llm/test_llm_fncall_converter.py`. The module covers canonical conversion, invalid function calls, parameter validation, multiple input tool-call rejection, content handling, and serialization. It has no current regression that recognizes the raw-name `<tool_call>` wrapper.
- **Provenance:** current source history after the issue opened. No equivalent merged change to `openhands-sdk/openhands/sdk/llm/mixins/fn_call_converter.py` was found; current source retains the behavior above.
- **Provenance:** issue timeline. Related issue [#4541](https://github.com/OpenHands/software-agent-sdk/issues/4541) was a separate `<think>` formatting problem and is closed; it is not a duplicate or solution for #4540.

### FACT — public maintainer analysis and PR #4608

- **Provenance:** [maintainer issue comment](https://github.com/OpenHands/software-agent-sdk/issues/4540#issuecomment-5341804230). The issue comprises two failure modes: provider-owned GLM channel leakage and an SDK-resolvable Kimi-style wrapper in non-native calling.
- **Provenance:** [maintainer proposed normalization](https://github.com/OpenHands/software-agent-sdk/issues/4540#issuecomment-5341804273). It proposes recognizing a bare tool name only when followed by a parameter tag, only when no canonical `<function=` is present.
- **Provenance:** [PR #4608](https://github.com/OpenHands/software-agent-sdk/pull/4608). The unmerged proposal rewrites the constrained wrapper to canonical function syntax before existing parsing, adds recovery/prose/truncation tests, and later adds a test preserving literal `</tool_call>` inside parameter content.
- **Provenance:** local candidate-screening execution of the public PR snapshot. Its converter recovered the wrapper into one `terminal` call, retained a literal closer inside the argument, and did not convert prose. This is local evidence for that snapshot, not current-main compatibility or maintainer acceptance.

### HYPOTHESIS

- The immediate SDK failure is a dialect mismatch: `_preprocess_model_output()` understands wrapper tags around a canonical function call but not a wrapper that replaces the canonical opener.
- The appropriate acceptance threshold is stricter than “the happy-path string parses.” A normalizer must establish enough structural evidence before creating an executable action.
- The narrowest viable recovery is an anchored, single-wrapper rewrite requiring a valid tool-name token and an immediately following parameter tag, then reuse of existing function parsing, tool resolution, parameter validation, and content stripping.

### PROPOSED SOLUTION

- Adapt the public #4608 direction in the converter’s preprocessing boundary: recognize only `<tool_call>NAME` followed by a parameter tag when the content contains no canonical `<function=` call; rewrite it to the canonical representation; rewrite only the terminal outer closer; and leave existing parser/validation/alias behavior responsible for the resulting call.
- Add focused behavior tests adjacent to converter tests and a safe integration test that verifies a single resulting structured call is eligible for dispatch exactly once without executing a destructive tool.

### UNKNOWN

- Whether real non-native model outputs include additional valid wrapper layouts that the bounded grammar should support.
- Whether one assistant message containing multiple raw wrappers is a supported converter input. Current instructions say one function call per message, but the exact rejection behavior for multiple raw wrappers is not frozen by existing coverage.
- Whether current agent-level test utilities can demonstrate dispatch eligibility without a live model or a real external tool.
- Whether the public PR patch applies cleanly to current main, whose version is newer than the PR branch’s package version.
- Whether hidden consumers rely on raw wrapper text being preserved rather than rejected when it is ambiguous.

## Constraints

- This session performs Freeze and Baseline only. TARGET(AI) must not be applied.
- No upstream source/test modifications, commits, branches, pull requests, issue comments, or external contact are permitted.
- The future baseline and TARGET(AI) treatment receive the same public evidence: issue #4540, current source/tests/history, maintainer analysis, and PR #4608 including its patch.
- The experiment must not claim to validate provider-owned GLM parsing or a live Synthetic endpoint.
- Any future implementation must be minimal, use the existing converter conventions, and preserve the current one-call-per-message contract unless evidence justifies a deliberate contract change.

## Safety concerns

1. A false-positive conversion changes inert assistant content into an action candidate. Its severity is at least equal to a false negative.
2. A naive closer replacement can corrupt an argument containing literal `</tool_call>` text.
3. Broad tag stripping can reinterpret documentation, code snippets, or user-requested file contents as tool calls.
4. Normalizing text that already contains a canonical/native call can duplicate or conflict with an existing action.
5. Ambiguous or malformed input must remain content or fail explicitly; it must not silently produce malformed executable arguments.

## Frozen observable success criteria

A future implementation is successful only if evidence establishes all applicable criteria below:

### Positive / recovery behavior

1. The malformed raw wrapper produces exactly one structured tool call.
2. The intended tool name is preserved.
3. Arguments are decoded correctly.
4. The malformed wrapper is removed from assistant text after successful conversion.
5. Canonical `<function=...>` input retains existing behavior.
6. The resulting structured call reaches safe tool-dispatch eligibility exactly once in a focused integration path.

### Negative / safety behavior

7. Plain prose mentioning `<tool_call>` does **not** create a tool call.
8. Literal `</tool_call>` text inside parameter content is preserved and does not terminate parsing incorrectly.
9. A truncated malformed wrapper does not silently create executable malformed arguments.
10. Ambiguous text remains non-executable unless the converter has sufficient structural evidence to classify it as a tool call.
11. Normalization does not duplicate an already-canonical/native call.
12. Multiple wrappers preserve exact call count/order if current semantics support them; otherwise they fail explicitly and deterministically.

## Environment and limitations

- Investigator environment: Linux x64 under WSL2. The current SDK was cloned to a disposable `/tmp` checkout and installed in a disposable virtual environment for the converter-level reproduction.
- Current repository package metadata reports `openhands-sdk` version `1.45.0`; the public PR branch reports an older version. This difference is an implementation-stage compatibility risk.
- Evidence is public issue/source/test/history/PR evidence plus local deterministic converter runs. It does not include a maintainer decision, hidden tests, a live Synthetic account, paid model output, or production telemetry.
- The frozen target is the deterministic SDK converter boundary only; it does not imply ownership of provider parser behavior.