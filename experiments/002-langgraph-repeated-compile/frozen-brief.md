# Experiment 002 — Frozen Brief

**Working title:** Repeated StateGraph compilation mutates builder state when default error handling is configured  
**Frozen:** 2026-09-07  
**Scope:** Starting state before either the conventional baseline or TARGET(AI) treatment. Do not revise this document after the treatment begins; record later discoveries separately.

## Problem

`StateGraph.compile()` must be safe to call repeatedly on the same builder. On the inspected revision, configuring `StateGraph.set_node_defaults(error_handler=...)` causes the first compilation to add an internal `__default_error_handler__` node to the builder. The next compilation treats that internal node as a user collision and raises `ValueError`.

This prevents a caller from compiling one authored graph repeatedly with legitimate compile-time choices such as different checkpointers.

## Source and inspected revision

| Item | Value |
| --- | --- |
| Issue | [langchain-ai/langgraph#8612](https://github.com/langchain-ai/langgraph/issues/8612) |
| Repository | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) |
| Branch | `main` |
| Inspected revision | `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1` |
| Revision commit | `fix(langgraph): type undeclared v3 stream projections (#8596)`; 2026-09-03T15:23:25Z |
| Candidate status at freeze | Issue open; current-main reproduction fails |

## Classification and starting evidence

### FACT — issue #8612

- Issue #8612 is open, created 2026-08-13 and last updated 2026-09-03.
- Its self-contained reproduction configures `set_node_defaults(error_handler=recover)`, then compiles and invokes the same builder twice.
- In the reported behavior, the first invocation returns `{'value': 'handled: boom'}` and the second `compile()` raises `ValueError: Auto-generated default error handler node '__default_error_handler__' already exists.`
- The issue says the defect was introduced with `set_node_defaults()` in merged PR #7747. It identifies #7996 as a separate `cache_policy=None` opt-out concern.
- The issue states that repeated compilation is independently exercised by `libs/langgraph/tests/test_parent_command.py` and its async equivalent; its reported per-node error-handler path remains repeatable.

### FACT — current source at inspected revision

- `libs/langgraph/langgraph/graph/state.py`, `StateGraph.set_node_defaults()`, stores graph-wide defaults and documents that they are applied at `compile()` time. Per-node values take precedence.
- `StateGraph.compile()` validates the builder, then at current lines 1287–1375:
  - checks `self.nodes` for `_DEFAULT_ERROR_HANDLER_NODE`;
  - writes a generated handler `StateNodeSpec` into `self.nodes` when an error-handler default exists;
  - mutates every `StateNodeSpec` in `self.nodes` to apply unset error-handler, retry, cache, and timeout defaults;
  - derives `node_error_handler_map` from `self.nodes`; and
  - attaches nodes by iterating `self.nodes`.
- `libs/langgraph/tests/test_parent_command.py` compiles the same `child_builder` twice. This establishes a current in-repository repeatable-compile use case, although that fixture has no configured node defaults.
- `libs/langgraph/tests/test_retry.py` contains default-policy tests, including collision coverage for a user node named `__default_error_handler__`, policy precedence, error-handler behavior, retry behavior, cache behavior, and timeout behavior. It has no current regression test for repeated compile with defaults.

### FACT — current-main reproduction performed during candidate screening

- A temporary sparse checkout at the inspected revision was installed editable and the issue's supplied program was run without source changes.
- First compile/invocation returned `{'value': 'handled: boom'}`.
- Immediately afterward, `builder.nodes` was `['__default_error_handler__', 'fail']`.
- The second `compile()` raised the issue's `ValueError` exactly.
- The temporary checkout and reproduction file were removed after validation. This is local evidence, not an upstream acceptance result.

### FACT — prior public proposed fixes

- [PR #8627](https://github.com/langchain-ai/langgraph/pull/8627), `fix(langgraph): allow repeated compilation with default error handler`, is closed and unmerged. Its patch creates `nodes = dict(self.nodes)`, generates/uses the handler in that local mapping, and makes maps/attachment use that mapping. It retains in-place mutation of `StateNodeSpec` instances, because the shallow mapping shares the original specs. Its proposed regression covers two compile-and-invoke operations.
- [PR #8800](https://github.com/langchain-ai/langgraph/pull/8800), `fix(langgraph): keep StateGraph.compile() from mutating the builder`, is closed and unmerged. Its patch creates a local node mapping and uses `dataclasses.replace()` for each spec receiving a default before deriving maps and attaching nodes. Its regression compiles and invokes twice, then checks that the generated handler and default handler routing have not leaked into the builder.
- No commit referencing `#8612` or `__default_error_handler__` was found in the upstream repository. Searches for related PRs found #8627 and #8800; neither merged. Current source retains the mutation.

### HYPOTHESIS — upstream issue discussion

- The immediate crash occurs because the first compile inserts the generated handler into `builder.nodes`; the next collision check cannot distinguish it from a user-authored node.
- More broadly, mutating stored node specifications during compilation makes a reused builder order-dependent and may leak all configured defaults, not only the generated node.
- Generated handler state should be local to the compilation artifact, or repeated compile should otherwise be idempotent without retaining stale defaults.

### PROPOSED SOLUTION — prior public PRs

- #8627: use a local `dict(self.nodes)` for generated-handler creation, routing-map construction, and node attachment.
- #8800: use the same local mapping and copy each affected `StateNodeSpec` with `dataclasses.replace()` before applying defaults, so both the generated node and default-policy fields remain outside builder state.

### UNKNOWN

- Whether any intentional public or internal consumer relies on `compiled.builder.nodes` exposing the generated handler after compilation.
- Whether every use of `CompiledStateGraph.builder.nodes`, including extension or dynamic attachment paths, remains safe when generated nodes exist only in the compiled graph's node mapping.
- Whether the maintainers prefer full compile purity for all four defaults or a narrower fix for the reported error-handler collision.
- Whether a local copy should be created before or after validation/serialization preparation to preserve all current error behavior.
- Whether hidden downstream tests impose additional compatibility constraints not observable from the public repository.

## Constraints

- This session performs Freeze and Baseline only. TARGET(AI) is not applied.
- No LangGraph source, test, commit, branch, pull request, issue, or external system may be modified.
- Baseline and future TARGET(AI) treatment may inspect the issue, current source/tests, history, and both unmerged PRs because all are public starting evidence.
- Baseline must be a competent conventional engineering analysis and must preserve the prompt verbatim.
- `baseline.md` becomes sealed when written; later corrections belong in subsequent artifacts.

## Frozen observable success criteria

A future implementation is successful only if evidence establishes all applicable criteria below:

1. **Repeated compilation:** the same `StateGraph` builder configured with a default error handler can be compiled repeatedly; at least two resulting compiled graphs can invoke the failing node and recover through that default handler.
2. **No builder mutation:** `compile()` does not add `__default_error_handler__` to the authored builder or write default-derived policy/routing fields into its existing node specifications.
3. **Default semantics preserved:** default error handling still applies to regular nodes without a per-node handler; handler nodes do not catch themselves. Existing retry, cache, and timeout default semantics and per-node precedence remain unchanged.
4. **User collision protection:** a user-authored node named `__default_error_handler__` continues to raise the existing collision `ValueError` when a default error handler is configured.
5. **Compiled graph integrity:** generated handler routing and node attachment exist in each compiled graph even though the generated node is not retained in the builder.
6. **Existing behavior preserved:** current valid single-compile/default-policy behavior and existing repeatable compilation behavior without defaults do not regress.
7. **Focused regression coverage:** tests exercise repeated compilation with node defaults and observable execution, plus builder purity where the chosen contract requires it.

## Environment and limitations

- Investigator environment: Linux x64 under WSL2; Python tooling was sufficient to install and run the current `libs/langgraph` package during candidate screening.
- The issue reporter's environment was macOS ARM64 with LangGraph 1.2.11 and Python 3.13.14; the current repository package version remains 1.2.11.
- Starting evidence is public issue/source/test/PR evidence plus one local reproduction. It does not include maintainer confirmation, hidden tests, or an upstream integration run.
- The two PR patches are candidate evidence, not accepted designs or proof of correctness.
