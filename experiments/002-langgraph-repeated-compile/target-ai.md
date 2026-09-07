# TARGET(AI) Treatment — Experiment 002

> **SEALED TARGET(AI) TREATMENT**
>
> Completed 2026-09-07. This treatment begins from `frozen-brief.md`. It does not read or compare `baseline.md`. Later discoveries belong in subsequent artifacts; this document must not be rewritten.

## Method source and proportional application

### Authoritative sources confirmed and used

| Source | Exact path | Readability and role |
| --- | --- | --- |
| TARGET(AI), published final | `/home/matheusgr/target_framework/TARGET.AI/TARGET_AI_FINAL.epub` | Readable EPUB. Title, author, copyright, ISBN, and 2026-08-29 date were extracted. Primary methodology source. |
| TARGET, First Edition | `/home/matheusgr/target_framework/TARGET_Edition_1.pdf` | Readable PDF. Title, author, copyright, and First Edition August 2026 were extracted. Consulted only for core-stage/feedback-loop mechanics that TARGET(AI) revisits and depends on. |

The treatment applied the published `Target → Assess → Reason → Generate → Execute → Track` cycle, evidence-before-completion rule, three feedback loops, and Reason Calibration. This is a reversible, low-consequence engineering planning problem: human judgment retains Target, evidence standards, the treatment decision, and all source changes; AI performs evidence collection and bounded reasoning. No source change or external action is authorized in this treatment.

## Target

| Element | Treatment target |
| --- | --- |
| **Outcome** | Establish the smallest evidence-backed implementation and validation boundary that restores repeatable `StateGraph.compile()` for builders with default error handling, without turning compiler-derived state into persistent authored configuration or changing existing policy semantics. |
| **Evidence** | Current-main reproduction; source-level account of persistent versus compile-derived state; an adversarial Reason Calibration pass; and predeclared tests that would distinguish a true repair from a suppressed exception. |
| **Constraints** | Do not modify LangGraph, tests, Git history, issues, PRs, or external systems. Do not read `baseline.md`. Do not expand into a general builder-immutability redesign. Preserve current collision behavior and existing default-policy semantics. |
| **Horizon / stopping condition** | Stop this treatment when a preferred action, alternatives, risks, evidence gates, and a genuine second Reason pass are recorded and sealed. Implementation remains a later authorized cycle. |

## Assess — current state and evidence

### Frozen facts carried into the treatment

- Issue [#8612](https://github.com/langchain-ai/langgraph/issues/8612) is open.
- The inspected `main` revision is `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1`.
- The supplied reproduction succeeded on the first compile/invocation, added `__default_error_handler__` to `builder.nodes`, then failed on the second compile with the expected `ValueError`.
- `test_parent_command.py` already compiles the same builder twice without defaults.
- Closed/unmerged PRs [#8627](https://github.com/langchain-ai/langgraph/pull/8627) and [#8800](https://github.com/langchain-ai/langgraph/pull/8800) are public starting evidence. Neither is in current main.

### Treatment investigation — discovered during this treatment

All findings below came from a fresh, temporary sparse checkout of the same frozen revision on 2026-09-07. This is not privileged evidence: it is current public source available equally to both treatments. The checkout was used read-only and later removed.

| Observation | Evidence | Classification |
| --- | --- | --- |
| `StateNodeSpec` is a mutable `@dataclass(slots=True)` with the policy/routing fields affected by compile. | `libs/langgraph/langgraph/graph/_node.py` defines `retry_policy`, `cache_policy`, `error_handler_node`, and `timeout`. | FACT |
| Default resolution writes a generated handler to `self.nodes`, then writes default values directly into stored specs. | `StateGraph.compile()` lines 1287–1338. | FACT |
| Explicit per-node error handlers are generated and stored during `add_node()`, before compile. | `StateGraph.add_node()` lines 866–920. | FACT |
| `StateGraph.validate()` sets `self.compiled = True`; later builder edits warn that already-built compiled graphs will not reflect them. | `state.py` lines 788–791, 945–948, 1012–1015, and 1174. | FACT |
| Within `libs/langgraph`, the only production reads of `CompiledStateGraph.builder.nodes` are in `attach_edge()` and `attach_branch()`. | Repository-wide search found `state.py` lines 1563 and 1601–1603. | FACT |
| Those reads concern authored edge destinations and branch source schema selection. Generated default-handler nodes cannot be an authored endpoint: a user-authored same-name node raises before compile can proceed. | `validate()`, `compile()` collision guard, `attach_edge()`, and `attach_branch()` source. | INFERENCE, strongly supported |
| No identity-sensitive use of `StateNodeSpec` was found in `libs/langgraph`. | Repository search found no identity/type checks involving `StateNodeSpec`; compiled attachment converts field values into `PregelNode`. | FACT about searched repository scope; UNKNOWN for downstream consumers |

### State boundary identified

The treatment does **not** assume a fully immutable builder. Current source demonstrates one legitimate persistent compile lifecycle state: `self.compiled` becomes true and governs warnings for later topology edits. Explicit per-node handlers are also persistent because `add_node()` creates them as part of authored configuration.

The narrower boundary is:

- **Authored state:** user nodes, explicit per-node handler nodes, edges, branches, schemas, `_node_defaults`, and the `compiled` lifecycle marker.
- **Compile-derived state:** the graph-wide default handler node, default-resolution results on individual node specs, the handler-routing map, and attached compiled nodes.

The defect is not that `compile()` changes *anything*. It is that it persists compile-derived state in the authored node mapping and mutable authored specs.

## Reason — first pass

### Explanation

The second compile fails because the first compile stores its generated graph-wide handler in the same `self.nodes` namespace used to protect a user-authored reserved name. The guard is behaving correctly for user state; it is seeing state that should never have persisted.

The same state-management error also applies defaults directly to mutable stored specs. A shallow copy of the mapping prevents the generated node leak but cannot prevent the spec-field leak because both mappings refer to the same spec instances.

### Assumptions

1. “Defaults are applied at compile time” describes resolution into the compilation product, rather than permanent mutation of authored specs.
2. A generated graph-wide handler is an internal compile artifact, unlike the explicitly configured per-node handler node generated by `add_node()`.
3. Preserving the original builder for `CompiledStateGraph.builder` is compatible with generated nodes existing only in the compiled graph.
4. Replacing a spec for the compilation view preserves all semantic field values not being changed.

### Predictions

If the explanation is correct, then:

1. compiling from an ephemeral node view will allow two compilations with the same default handler;
2. both compiled graphs will retain handler routing and run the handler;
3. the authored builder will not acquire generated handler/policy/routing fields;
4. a user-authored `__default_error_handler__` will still raise; and
5. runtime semantics already tested for defaults will remain unchanged because attachment receives the same effective field values.

A fix that only ignores the name collision predicts the first condition may pass while conditions 3 and potentially later compile semantics still fail.

## Generate — competing actions

| Option | Expected value | Risk / evidence needed | Decision |
| --- | --- | --- | --- |
| Ignore the reserved-name collision when it was previously generated. | Removes the visible second-compile exception. | Leaves stale handler routing and other defaults on authored specs; must show why stale state is acceptable. No such evidence. | Reject. |
| Add the generated handler once to builder state and make it idempotent. | Small local change. | Makes the first compile bind later compiles to historic handler/default state; conflicts with configuration being resolved at compile time. | Reject. |
| Remove generated state from the builder after attach. | Can restore the name namespace. | Requires cleanup across failure paths and still leaves direct policy mutations. | Reject. |
| Create only `nodes = dict(self.nodes)` for compilation (PR #8627 direction). | Prevents generated-node persistence. | Mapping is shallow; mutable specs still leak resolved defaults. | Reject as incomplete. |
| Create an ephemeral mapping and copy-on-write only specs that inherit defaults (PR #8800 direction). | Preserves authored state while producing the same effective compile view. | Must verify builder-reference compatibility and copy semantics. | Preferred, subject to second Reason pass. |
| Deep-copy the entire builder or introduce a new builder/compiled-graph architecture. | Strong isolation. | Broader identity, performance, and API risks disproportionate to four resolved fields. | Reject. |

## Proposed action after first pass

In `StateGraph.compile()`, at the current default-resolution point after validation:

1. construct a local mapping from authored `self.nodes`;
2. test the reserved-name collision against authored nodes before local generated insertion;
3. add the graph-wide default handler only to the local mapping;
4. for each locally resolved node, use `dataclasses.replace()` only when a default must fill an unset field;
5. derive `node_error_handler_map` and attach compiled nodes from local resolved nodes;
6. leave `self.nodes` and its specs unchanged.

This keeps current default conditions: handler routing/cache only for regular nodes; retry/timeout also for handlers; explicit values win.

## Reason Calibration — adversarial second pass

The first-pass recommendation was deliberately challenged before action. The questions below were used to seek a different boundary or a smaller correct change.

| Challenge | Evidence considered | Calibration result |
| --- | --- | --- |
| **What would make “builder purity” the wrong invariant?** | `validate()` deliberately sets `self.compiled = True`, and later authoring calls warn. `add_node()` deliberately stores explicit per-node handler nodes. | **First-pass claim narrowed.** Absolute builder immutability is not the contract. The applicable invariant is non-persistence of compile-derived default resolution, not absence of every lifecycle mutation. |
| **Could the default handler legitimately remain persistent just like per-node handlers?** | Per-node handler creation occurs at authored `add_node()` time and uses a node-specific name. The graph-wide handler is created only while resolving a builder default inside compile. | No evidence supports persistence of the graph-wide helper. Its position in compile and the documented compile-time application of defaults support ephemeral ownership. |
| **Could the smaller #8627 mapping copy be enough?** | `StateNodeSpec` is mutable; `dict(self.nodes)` aliases each spec. Current compile writes four fields to those objects. | No. It cures the error symptom but not the state leak. Copy-on-write is the minimum correction that satisfies the scoped invariant. |
| **Could `dataclasses.replace()` alter identity-dependent behavior?** | The spec is a mutable dataclass. The production search found no spec identity use, and `attach_node()` transfers values into fresh `PregelNode` objects. `compiled.builder` remains the original builder. | Within inspected library code, risk is low and bounded. Downstream reliance on transient spec identity remains UNKNOWN; a shallow copy-on-write is lower risk than deep copy. |
| **Does `CompiledStateGraph.builder` make local handler nodes unsafe?** | Only two production reads of `builder.nodes` were found: authored join-target `defer` and branch-source schema selection. Generated handler nodes cannot appear in user-authored edges after collision validation. | This evidence strengthens the local-node approach. Do not replace `compiled.builder`; preserve its authored-state role. |
| **Are derived structures outside `self.nodes` also leaking compile results?** | Inspected compile flow: local `checkpointer`, `serde_allowlist`, output/stream channels, handler map, and `CompiledStateGraph` attachments. Persistent `self.compiled` is intentional lifecycle state. No other compile-time policy write was found. | Scope remains `self.nodes`/spec mutation. Do not expand the patch without new evidence. |
| **Could the main regression pass while a material defect remains?** | A test that only compiles twice with a default handler misses retry/cache/timeout leakage and could pass if an implementation masks the collision. | Validation must assert both observable execution and the relevant authored specs remain unchanged, with existing runtime policy tests retained. |
| **Is the prior stronger PR more change than needed?** | The four field assignments share the same mutable state boundary. Avoiding copies for any one leaves a documented default resolved persistently. | The stronger direction is the minimum complete correction, but the test scope should be proportional and avoid unrelated refactoring. |

### Second-pass conclusion

The preferred approach remains an ephemeral node mapping with copy-on-write replacement. The conclusion changed in one material way: the goal is **not** to make `StateGraph` immutable after compile. It is to preserve the distinction between authored builder state and derived compilation state while retaining the existing persistent lifecycle marker and explicit per-node configuration.

This calibration also strengthens the evidence threshold: passing the issue reproduction alone is insufficient. A repair must demonstrate that no resolved defaults leak into authored specs and that the original builder-reference compatibility is not disturbed.

## Proposed implementation boundary

**Change only:**

- `libs/langgraph/langgraph/graph/state.py`
- focused tests in `libs/langgraph/tests/test_retry.py`

**Do not change:**

- public error-handler/default APIs;
- graph validation ordering except for use of the resolved local mapping after validation;
- `CompiledStateGraph.builder` ownership;
- explicit per-node handler creation in `add_node()`;
- collision wording or user collision behavior;
- unrelated builder data or broad graph architecture.

## Predeclared validation boundary

### Required new focused evidence

1. Build the issue graph with `set_node_defaults(error_handler=...)`, compile twice, and invoke both compiled graphs. Both must route the failure through the default handler.
2. After one or more compiles, assert the authored builder does not contain `__default_error_handler__` and its original regular node has not gained default handler routing.
3. Assert default-policy fields resolved during compile do not persist in authored specs. Cover error handler plus retry/cache defaults in a deterministic focused case, and timeout with an async or direct policy-state case if existing behavior coverage cannot establish it.
4. Keep the user-reserved-name collision test: a user-authored `__default_error_handler__` must still raise.

### Required existing evidence to retain/run in an authorized implementation cycle

- Existing default-handler routing, per-node precedence, handler-failure, and `RunnableConfig` tests.
- Existing retry/cache/timeout default and per-node precedence tests, because the changed resolution loop applies all four.
- Existing repeated compile test(s), including `test_parent_command.py`; use the relevant async equivalent if present.
- Relevant package format/lint/test commands required by repository instructions after the change exists.

### Evidence interpretation gate

- **Pass:** both compiled artifacts work; authored default-derived node/spec state remains absent; collision and existing default semantics hold.
- **Ambiguous:** behavior passes but builder fields change, or a test exposes a `compiled.builder` dependency. Re-enter Reason; do not merge a symptom-only fix.
- **Fail:** local resolution changes routing, per-node precedence, handler exclusion, or policy behavior. Reassess whether a dedicated immutable compilation-view object is necessary.

## Track — treatment result and stopping condition

**Expected before any future execution:** ephemeral copy-on-write resolution will make default-handler compiles repeatable and stop all four default assignments from leaking into authored node specs, while leaving intended `self.compiled` lifecycle state intact.

**Actual in this treatment:** no implementation or source/test change was made. The target of this reasoning cycle is met only as an evidence-backed decision and validation boundary, not as a repaired LangGraph behavior.

**Stop now:** the sealed treatment contains a target, evidence separation, first and second Reason passes, competing options, a scoped action, and evidence gates. Comparison and implementation require separate authorization.

## Remaining uncertainties

1. Public source does not prove the absence of downstream users depending on generated handler visibility through `compiled.builder.nodes`.
2. Hidden tests may encode an expectation not expressed in public source/tests.
3. A future implementation must confirm the exact update order in copy-on-write logic preserves combined defaults, including generated handler retry/timeout semantics.
4. The treatment did not benchmark compile-time allocation. The expected added work is one shallow mapping and replacements only for inheriting nodes; this is an inference, not measurement.

## Process overhead observed

- Read the published TARGET(AI) methodology as primary source and the core TARGET book only for stages/loops.
- Performed one fresh, read-only source audit focused on state ownership, `StateNodeSpec` mutability, `CompiledStateGraph.builder` consumers, and lifecycle persistence.
- Performed a genuine adversarial second Reason pass that narrowed “builder purity” to the evidence-supported authored-versus-derived state boundary and raised the test threshold beyond the issue reproduction.
- Produced one treatment artifact. No extra planning documents, source edits, tests, or external actions were created.
