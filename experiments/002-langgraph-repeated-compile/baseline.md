# Baseline Analysis — Experiment 002

> **SEALED BASELINE**
>
> Created before TARGET(AI) treatment. This reasoning is immutable. Any later correction or discovery must be recorded in a subsequent experiment artifact, not by editing this document.

## Baseline prompt

> "Analyze this bug and propose the best implementation and validation plan. Use the available repository evidence, existing source, tests, issue discussion, and prior unmerged fix attempts. Identify the likely root cause, preferred fix, alternatives, risks, and the tests required to establish correctness."

## Investigation performed

### Issue and starting-state evidence

- Read [issue #8612](https://github.com/langchain-ai/langgraph/issues/8612), including its reproduction, reporter-provided analysis, and discussion.
- Used the pre-baseline screening result: the supplied reproduction was executed against current `main` and failed exactly on the second compile after the first added `__default_error_handler__` to `builder.nodes`.
- Read the frozen brief before analysis.

### Current source and tests

- Inspected `libs/langgraph/langgraph/graph/state.py` in revision `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1`:
  - `StateGraph.set_node_defaults()` documents graph-wide defaults applied at compile time, per-node precedence, handler exclusion from handler routing/cache, and application of retry/timeout to handler nodes.
  - `StateGraph.compile()` mutates `self.nodes` by adding the generated default handler and mutates stored `StateNodeSpec` objects while applying all defaults.
  - `CompiledStateGraph` retains `builder=self`; `attach_edge()` and `attach_branch()` read `self.builder.nodes` for authored graph topology/schema data.
- Inspected `libs/langgraph/tests/test_retry.py` default-error-handler coverage: all-node routing, per-node handler precedence, handler failure semantics, `RunnableConfig` forwarding, user-reserved-name collision, retry, cache, and timeout default behavior.
- Inspected `libs/langgraph/tests/test_parent_command.py`, which compiles one builder twice; it establishes repeated compile as an existing repository behavior.

### Prior public proposals

- Inspected closed/unmerged [PR #8627](https://github.com/langchain-ai/langgraph/pull/8627): local node dictionary for generated-node creation and compilation wiring, but still mutates the original spec instances.
- Inspected closed/unmerged [PR #8800](https://github.com/langchain-ai/langgraph/pull/8800): local node dictionary plus `dataclasses.replace()` for each spec whose defaults are applied, along with a repeat-compile and builder-purity regression.
- Confirmed at freeze that neither proposal was merged and current source contains neither equivalent change.

## Problem understanding

`StateGraph` is an authored builder. `compile()` produces a `CompiledStateGraph` from that builder and accepts compile-time choices such as a checkpointer. Repeated compile is already a valid in-tree operation.

With an error-handler default, current `compile()` crosses the authoring/compiled boundary:

1. It creates an internal handler spec directly in `self.nodes`.
2. It assigns that generated node name to authored node specs that lack a per-node error handler.
3. It assigns retry, cache, and timeout defaults directly to authored node specs where unset.
4. On a later compile, the generated internal name is present in `self.nodes`, so the collision guard correctly sees a name collision but incorrectly attributes the compiler-created node to the user.

The visible failure is therefore one symptom of a broader builder-state leak. The appropriate contract is that compile-derived nodes and compile-derived default values are part of the compiled artifact, not persistent changes to the authored builder.

## Root-cause analysis

**Root cause:** `StateGraph.compile()` operates on `self.nodes` and the mutable `StateNodeSpec` instances stored in it, instead of an ephemeral compilation view.

The collision guard itself is not faulty. It protects a real user-authored node named `__default_error_handler__`. The defect is that the compiler first writes its own generated node into the same namespace that the guard uses to detect user ownership.

A shallow copy of the mapping alone solves the immediate generated-name leak but not the spec mutation: `dict(self.nodes)` copies references, so assigning `spec.error_handler_node`, `spec.retry_policy`, `spec.cache_policy`, or `spec.timeout` still alters the builder. This is the material distinction between #8627 and #8800.

## Assumptions

1. The documented “defaults are applied at compile time” semantics mean default application must not persist in builder state. This is consistent with the issue, current API documentation, and repeated-compile fixture.
2. The generated default handler is an implementation detail rather than a supported authored node exposed through `compiled.builder.nodes`. Current code’s exposure is an incidental effect of mutation, not an explicit API contract. This needs targeted verification through repository call sites and tests during implementation.
3. `StateNodeSpec` can be safely copied with `dataclasses.replace()` while preserving its runnable, metadata, schemas, and explicit per-node values. The existing PR #8800 uses that mechanism; its suitability should still be verified against the actual declaration before implementation.
4. The public, current-source evidence is sufficient to select a plan, but not proof against hidden downstream compatibility expectations.

## Interpretation of current `compile()` behavior

Current compilation needs a node collection containing both authored nodes and any generated default handler. It then needs to apply defaults, derive `node_error_handler_map`, and attach the resulting nodes to the compiled graph.

The compiled graph must retain the generated handler because error routing targets it. The builder should retain only authored nodes and authored per-node configuration.

`CompiledStateGraph.builder` remaining the original builder is not inherently a problem. The code paths observed through `attach_edge()` and `attach_branch()` consult builder nodes for user-authored edge endpoints and source schemas. A generated handler is not a user-authored edge endpoint because a user collision causes compilation to fail before attachment. Still, this is the principal compatibility boundary to audit before accepting the patch.

## Interpretation of prior unmerged PRs

### PR #8627

Useful partial diagnosis: it isolates generated-handler insertion, routing-map creation, and node attachment in a local mapping. It directly resolves the second-compile exception.

It is insufficient as the preferred solution because its shallow mapping leaves mutable `StateNodeSpec` instances shared with `builder.nodes`. Default error-handler routing and retry/cache/timeout defaults still leak into the builder. That contradicts the compile-time default contract and leaves repeated compile semantically order-dependent even after the visible error is removed.

### PR #8800

Preferred direction. It retains the generated node only in a local mapping and replaces only specs that need a default applied. This preserves the existing default precedence and conditional application logic while preventing mutation of authored specs. It also proposes the right regression shape: execute both compiled graphs and assert builder purity.

The implementation should be independently reviewed rather than copied wholesale. In particular, it needs a targeted audit of all `compiled.builder.nodes` reads and must preserve the collision check against the original authored mapping.

## Preferred implementation approach

Modify only `libs/langgraph/langgraph/graph/state.py` and the focused default-policy regression tests.

Within `StateGraph.compile()`:

1. Build a local `nodes` mapping from `self.nodes` after the existing validation and before generated-node/default processing.
2. Keep the collision check against the original authored mapping, or equivalently against the just-created local map before any generated insertion. This continues to reject a user node called `__default_error_handler__`.
3. Insert the generated handler spec only into local `nodes`.
4. Iterate local nodes. For every default that applies to a spec, construct a replacement spec with `dataclasses.replace()`; write it back to local `nodes` only if changed.
   - Preserve current conditions exactly: default error handler and cache apply only to regular nodes; retry and timeout also apply to error-handler nodes; explicit per-node values win.
5. Derive `node_error_handler_map` from local `nodes`.
6. Attach nodes from local `nodes` into the compiled graph.
7. Leave `self.nodes` and all stored specs untouched.

This is deliberately a focused compiler-lifecycle correction. It does not introduce a new public API, rename the internal handler, change default precedence, or alter unrelated builder data.

## Rejected alternatives

| Alternative | Decision | Reason |
| --- | --- | --- |
| Ignore the generated name on the second compile | Reject | Hides only the collision while preserving leaked handler routing and default policies in builder state. It risks stale configuration and weakens the meaningful user-name collision boundary. |
| Delete generated node from `self.nodes` at compile exit | Reject | Requires cleanup across success/error paths and still leaves in-place policy mutations. It also makes compilation stateful during execution and complicates reentrancy/error handling. |
| Use only `nodes = dict(self.nodes)` (#8627) | Reject | Shallow mapping copies keys/references, not `StateNodeSpec` objects; default application remains a mutation of authored specs. |
| Deep-copy the entire graph/builder | Reject | Broad, expensive, and likely changes identity/behavior for runnables or schemas. Only the specs receiving compile defaults need replacement. |
| Make `compile()` permanently retain generated nodes and mark them internal | Reject | Maintains the authoring/compiled-state leak and does not satisfy builder purity. |
| Change the public error-handler API or remove collision protection | Reject | The issue is lifecycle behavior, not API design. Existing collision semantics are intentional and tested. |

## Files/components likely to change

- `libs/langgraph/langgraph/graph/state.py`
  - Imports `replace` from `dataclasses`.
  - The default-node/default-policy block in `StateGraph.compile()`.
  - Use of node collection for handler map and `attach_node()`.
- `libs/langgraph/tests/test_retry.py`
  - Add a focused test next to existing `set_node_defaults` error-handler and collision tests.

No changes are currently justified to public documentation, typing surface, checkpoint implementations, or unrelated graph builders.

## Implementation plan

1. Inspect the actual `StateNodeSpec` declaration and all direct uses of `CompiledStateGraph.builder.nodes` to validate that replacement copies are sufficient and generated-handler absence from the builder is safe.
2. Add/adjust only the focused regression test first if the repository workflow supports it; demonstrate it fails on current main.
3. Implement the local compilation node mapping and copy-on-default application in `StateGraph.compile()`.
4. Ensure all compilation products (`node_error_handler_map`, node attachment) use local nodes while graph validation and authored-graph topology behavior retain their existing source.
5. Run the focused regression plus existing default-policy/collision tests.
6. Run the package’s prescribed relevant checks only after implementation; do not expand scope unless verification exposes a real dependency.

## Validation plan

### Required focused behavior

1. Build the issue’s graph with `set_node_defaults(error_handler=...)`.
2. Compile it twice from the same builder.
3. Invoke both compiled graphs and assert both route the failed node to the default handler and return the expected state.
4. Assert `__default_error_handler__` is absent from `builder.nodes` after compilation.
5. Assert the authored failing node has not gained `error_handler_node` through compilation.

### Required semantic regressions

- Retain `test_set_node_defaults_error_handler_collides_with_user_node`: a user-authored `__default_error_handler__` must still raise.
- Run current default-handler tests for routing across nodes, per-node handler precedence, handler failure behavior, and `RunnableConfig` forwarding.
- Run current default retry/cache/timeout and per-node-precedence tests. The proposed fix explicitly touches their application path.
- Run `test_parent_command.py` (and async counterpart if separate) to preserve established repeatable compilation without defaults.

### Implementation-quality checks

- Run the focused `test_retry.py` selection while developing, then the relevant package test target and lint/format commands required by repository instructions if implementation occurs in a later authorized session.
- A test should additionally cover multiple defaults or independently snapshot default fields only if existing coverage does not prove the copy-on-write invariant for those fields. This is useful because the root cause affects all four defaults, but tests should remain behavior-oriented and not become source-structure assertions.

## Regression risks

1. **Builder reference compatibility:** `CompiledStateGraph.builder` remains the original builder. Any unobserved code that expects generated handler nodes there could break. Audit references before implementation.
2. **Default propagation loss:** moving to a local copy could accidentally omit retry/cache/timeout assignment, change handler exclusions, or ignore per-node explicit configuration.
3. **Collision semantics:** checking after injecting the generated node would make every default-handler compile fail; checking a mutated builder would retain the original bug. The guard must distinguish authored state from generated compile state.
4. **Identity-sensitive spec behavior:** replacement changes a spec object’s identity for the compiled graph. That is desired for purity but needs review of any identity-based consumers.
5. **Performance:** a shallow node-map allocation occurs per compile; `replace()` should occur only for specs that actually inherit a default. This cost appears proportional to compile work and smaller than a deep copy, but no benchmark evidence is available.

## Unresolved questions

- Are there external, supported integrations relying on `compiled.builder.nodes` containing generated compiler nodes? Public evidence does not establish one.
- Does `StateNodeSpec` include fields whose copy semantics make `dataclasses.replace()` inadequate or require a dedicated helper?
- Should the regression explicitly prove every default remains nonpersistent, or is a targeted error-handler test plus existing per-policy runtime behavior proportionate? The issue comments identify all four; the final test set should balance complete lifecycle coverage and focused maintenance burden.
- Are compile failures during later attachment guaranteed not to leak any other mutable builder state? This change removes mutation from the default block but does not prove global compile purity beyond its scope.

## Confidence

**High (0.86).**

The failure is locally reproduced on current main, the precise mutation is visible in the current source, and the preferred local copy-on-write design directly preserves existing semantics while solving both the reported crash and the broader policy leak. The remaining uncertainty is concentrated in compatibility of `compiled.builder.nodes` and the complete copy semantics of `StateNodeSpec`; both are bounded, reviewable implementation risks rather than uncertainty about the root cause.
