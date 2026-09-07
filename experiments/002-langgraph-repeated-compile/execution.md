# Execution + Observe — Experiment 002

> **Execution evidence.** This document records local execution against the frozen revision. It does not alter or reinterpret the sealed brief, baseline, TARGET(AI) treatment, or comparison.

## Result

Implemented the shared local compile-time node-view decision in a local detached checkout. The patch passes both behavior evidence (Layer A) and the stronger authored-state evidence (Layer B). A temporary #8627-style shallow-map counterfactual passed Layer A while demonstrably failing Layer B.

## Revision and environment

| Item | Value |
| --- | --- |
| Repository checkout | `/tmp/langgraph-8612-exec` |
| Revision | `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1` |
| Package | `langgraph` 1.2.11, installed editable from the checkout |
| Python | Python 3.12.3 |
| Platform | Linux x64 under WSL2 |
| Test environment | Local `/tmp/langgraph-8612-exec/libs/langgraph/.venv` |
| Repository-prescribed runner | `uv` was unavailable; `make` targets could not run. Equivalent local `pytest` and `ruff` commands were used. |

## Implementation performed

### `libs/langgraph/langgraph/graph/state.py`

- Imported `dataclasses.replace`.
- Created `nodes = dict(self.nodes)` after validation as the local compilation mapping.
- Kept the reserved-name collision guard against `self.nodes`, before generated-node insertion.
- Added `__default_error_handler__` only to local `nodes`.
- Replaced a node spec only when one or more inherited defaults apply; the replacement receives the resolved error handler, retry, cache, and/or timeout values.
- Derived `node_error_handler_map` and attached compiled nodes from local `nodes`.
- Left `self.nodes` untouched. `validate()` still sets the intentional lifecycle marker `self.compiled`.

### `libs/langgraph/tests/test_retry.py`

Added two focused regressions:

1. `test_set_node_defaults_repeated_compile_runs_both_graphs` — **Layer A** only. Compiles the default-handler graph twice and invokes both compiled graphs.
2. `test_set_node_defaults_repeated_compile_keeps_authored_specs_unchanged` — **Layer B**. Uses combined inherited defaults and explicit per-node policies, asserts both compiled graphs execute, verifies the authored spec retains `None` for all four inherited fields, verifies default handler absence from `builder.nodes`, and verifies resolved compiled-node policy/exclusion/precedence configuration.

The Layer B test is async because LangGraph rejects timeout configuration for synchronous Python nodes. This was execution evidence requiring a test adaptation, not an implementation change.

## Layer A — behavior result

**PASS.**

- The new Layer A regression compiled the same default-handler builder twice.
- Both compiled graphs returned `{'value': 'handled'}` through the default handler.
- Existing user-reserved-name collision coverage passed as part of the selected default-policy suite.
- Existing repeat compilation without defaults passed through `tests/test_parent_command.py`.

Focused command:

```text
.venv/bin/python -m pytest tests/test_retry.py -k 'test_set_node_defaults_repeated_compile_runs_both_graphs or test_set_node_defaults_repeated_compile_keeps_authored_specs_unchanged' -q
2 passed, 105 deselected in 1.01s
```

## Layer B — stronger authored-state result

**PASS.**

After two compiles with inherited error-handler, retry, cache, and timeout defaults:

- `__default_error_handler__` was absent from `builder.nodes`.
- The original authored `fail` spec retained `None` for `error_handler_node`, `retry_policy`, `cache_policy`, and `timeout`.
- The compiled regular node retained the resolved defaults.
- The compiled generated handler retained retry/timeout but no handler routing/cache policy, preserving generated-handler exclusions.
- The compiled node with explicit policy values retained its explicit retry/cache/timeout values.

## Counterfactual: Layer A can pass while Layer B fails

**Confirmed.**

A temporary local-only counterfactual copied the implementation and changed only default application to the #8627-style shallow-map behavior: generated handler remained local, but shared `StateNodeSpec` instances were mutated in place. It was not committed or retained as a proposed fix.

Counterfactual command:

```text
PYTHONPATH=/tmp/langgraph-8612-shallow-root \
  /tmp/langgraph-8612-exec/libs/langgraph/.venv/bin/python \
  /tmp/langgraph-8612-shallow-counterfactual.py
```

Observed output:

```text
layer_a= {'value': 'handled'} {'value': 'handled'} generated_in_builder= False
layer_b_behavior= {'value': 'handled'} {'value': 'handled'}
layer_b_authored_fields= {
  'error_handler_node': '__default_error_handler__',
  'retry_policy': True,
  'cache_policy': True,
  'timeout': True,
  'generated_in_builder': False
}
```

Therefore a shallow-map repair fixes the reported repeated-compilation behavior while leaving all four compile-derived fields in authored specs. The stronger Layer B boundary has concrete discriminating value; this is execution evidence supporting the pre-execution B classification.

## Existing-test and compatibility results

| Command | Result | Coverage relevance |
| --- | --- | --- |
| `.venv/bin/python -m pytest tests/test_retry.py -k 'set_node_defaults or node_error_handler' tests/test_parent_command.py -q` | `15 passed, 93 deselected` | Default handlers, handler failures/exclusions, configuration forwarding, collision, retry/cache/timeout default and precedence, repeated compile. |
| `.venv/bin/python -m pytest tests/test_retry.py tests/test_parent_command.py -q` | `108 passed in 5.61s` | Complete retry/default-policy file plus existing repeated compilation case. |
| `NO_DOCKER=true .venv/bin/python -m pytest tests/test_pregel.py::test_in_one_fan_out_state_graph_defer_node tests/test_state.py -q` | `24 passed in 4.45s`; 2 snapshots passed | Multi-start deferred join reads `builder.nodes[end].defer`; branch input-schema consumer coverage in `test_state.py`. |
| `.venv/bin/ruff format langgraph/graph/state.py tests/test_retry.py && .venv/bin/ruff check langgraph/graph/state.py tests/test_retry.py` | Pass; one file reformatted, one unchanged; `All checks passed!` | Formatting and lint for changed files. |
| `git diff --check` | Pass; no output | Whitespace integrity. |

`CompiledStateGraph.builder` remains the original builder. The passing deferred-join and branch-schema tests exercise the two current production reads identified during treatment; the patch changes neither reader.

## Unexpected evidence and adaptation

1. The first combined-default regression used synchronous nodes with a timeout default. Compilation correctly failed because LangGraph supports node timeout only for async Python nodes. The test was converted to async; production code did not change.
2. `PregelNode` normalizes `RetryPolicy` to a one-item tuple. The Layer B assertion was corrected from identity with a single policy object to equality with `(policy,)`. This preserves the intended observation: resolved compiled values are present while authored specs remain unchanged.
3. An initial graph-attachment command attempted PostgreSQL-backed parameterizations without a running database and lacked `pycryptodome` for encrypted SQLite. It reported `24 passed, 8 errors`: six PostgreSQL connection-refused cases and two missing-crypto cases. After installing `pycryptodome` in the isolated venv and setting `NO_DOCKER=true`, the available memory/SQLite/encrypted-SQLite variants and all `test_state.py` cases passed: `24 passed`.

No sealed artifact was changed. No evidence required changing the implementation plan.

## Limitations

- `uv` is absent, so repository `make format`, `make lint`, and `make test` commands were not run verbatim.
- No Docker/PostgreSQL service was running. PostgreSQL-specific parameterizations were not executed successfully; they are unrelated to the changed default-resolution path but remain unverified in this environment.
- The full LangGraph test suite was not run. Relevant default-policy, repeat-compile, state/branch-schema, and deferred-join coverage ran locally.
- Internal current-core compatibility was exercised; downstream consumers of generated-handler visibility through `compiled.builder.nodes` remain unknown.

## Diff summary

```text
libs/langgraph/langgraph/graph/state.py |  30 +++++----
libs/langgraph/tests/test_retry.py      | 107 ++++++++++++++++++++++++++++++++
2 files changed, 124 insertions(+), 13 deletions(-)
```

The larger test addition includes distinct Layer A and Layer B regressions plus explicit combined-default and authored-state assertions.

## Execution conclusion

The implementation still matches the shared baseline/TARGET(AI) plan: a minimal local compilation mapping, copy-on-write only for inherited defaults, preserved collision semantics, preserved `self.compiled`, and unchanged public API. The stronger validation boundary caught a real defect class that the behavior layer alone accepts. Local external contribution now appears technically justified, subject to running the repository-prescribed full checks in a complete environment and explicit approval before any publication.
