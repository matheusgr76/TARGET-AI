# Experiment 002 — Repeated LangGraph Compilation

## Problem

[LangGraph issue #8612](https://github.com/langchain-ai/langgraph/issues/8612) reports that `StateGraph.compile()` fails on repeated compilation when graph-wide default error handling is configured. Compilation-derived state is persisted into the authored builder: a later compile treats the generated `__default_error_handler__` as a user-name collision.

## Why this experiment

This is a real open-source problem with reproducible behavior, mutable-state uncertainty, competing public fix attempts, and observable correctness criteria. It evaluates whether TARGET(AI) materially improves engineering reasoning over a competent conventional baseline.

Public upstream context:

- [Issue #8612](https://github.com/langchain-ai/langgraph/issues/8612)
- [Unmerged PR #8627](https://github.com/langchain-ai/langgraph/pull/8627) — local mapping only
- [Unmerged PR #8800](https://github.com/langchain-ai/langgraph/pull/8800) — local mapping plus copy-on-write specs

These links are upstream public evidence, not TARGET(AI) contributions.

## Baseline result

The competent conventional baseline already identified mutable `StateNodeSpec` leakage, rejected a shallow-copy-only repair, and selected a local compilation mapping with `dataclasses.replace()` for specs inheriting defaults. It also preserved collision and default-policy semantics.

TARGET(AI) did not improve implementation selection in this experiment.

## TARGET(AI) result

TARGET(AI) reached the same implementation decision. Its additional contribution was to refine the state invariant:

- authored builder state remains authored;
- `self.compiled` and explicit per-node handlers are intentional persistent state;
- graph-wide handler insertion and inherited default resolution are compiler-derived state and must not persist in authored specs.

It also required stronger state-preservation evidence for all inherited default fields.

## Execution result

The local implementation was evaluated against LangGraph revision `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1`.

| Evidence layer | Result |
| --- | --- |
| Layer A: repeated compile and invocation | **PASS** — both compiled graphs recovered through the default handler. |
| Layer B: authored-state invariant | **PASS** — generated handler and inherited error-handler, retry, cache, and timeout values did not persist in authored specs. |
| Controlled shallow-map counterfactual | **Layer A PASS; Layer B FAIL** — repeated behavior worked, but `error_handler_node`, `retry_policy`, `cache_policy`, and `timeout` remained in the authored `StateNodeSpec`. |

The counterfactual was local and temporary. It demonstrates that behavior-only coverage can accept an incomplete repair for this specific mutable-default-resolution defect; it does not represent an upstream implementation or acceptance decision.

## Conclusion

TARGET(AI) did not improve implementation selection in this experiment. The competent baseline selected the same repair. Its additional validation boundary did, however, demonstrate practical value locally: a plausible shallow-map implementation passed the behavioral regression while failing the state-invariant regression.

## Limitations

- The full LangGraph suite was not run.
- PostgreSQL-backed parameterizations were unavailable.
- The prescribed `uv`/`make` workflow was unavailable; equivalent local `pytest` and `ruff` commands were used.
- No LangGraph maintainer review occurred.
- No downstream compatibility evidence exists.
- No upstream merge, release, or production evidence exists.

## Upstream status

The experiment used a local implementation at revision `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1`. No LangGraph pull request was opened, and no upstream contribution was submitted or accepted as part of this experiment.

## Documents

- [Frozen brief](frozen-brief.md)
- [Competent conventional baseline](baseline.md)
- [TARGET(AI) treatment](target-ai.md)
- [Pre-execution comparison](comparison.md)
- [Execution evidence](execution.md)
- [Retrospective](retrospective.md)
