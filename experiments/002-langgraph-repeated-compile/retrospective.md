# Retrospective — Experiment 002

> **Scope:** post-execution assessment of the frozen brief, sealed baseline, sealed TARGET(AI) treatment, sealed comparison, and execution evidence. This document does not modify any earlier artifact.

## Verdict

Experiment 002 shows one bounded practical benefit from TARGET(AI): its stronger evidence gate required checking that *all* inherited compile defaults stay out of authored `StateNodeSpec` objects. A local #8627-style shallow-map counterfactual passed the behavior-only layer yet left exactly those fields persisted. The chosen copy-on-write implementation passed both layers.

This is not evidence that TARGET(AI) selected a better patch—the competent baseline selected the same patch—nor that TARGET(AI) generally improves engineering outcomes. It is evidence that, in this defect, the TARGET(AI) validation boundary rejected a plausible incomplete repair that behavior-only acceptance would allow.

## Evidence classes

| Class | What the experiment establishes | What it does not establish |
| --- | --- | --- |
| **Pre-execution reasoning** | Baseline and TARGET(AI) independently selected the same local compilation-view/copy-on-write implementation. TARGET(AI) made all-default non-persistence mandatory and completed a focused internal consumer audit. | That either treatment would produce a correct upstream change. |
| **Implementation evidence** | The local patch compiles/invokes twice, preserves collision/default behavior in selected tests, preserves authored specs in the Layer B regression, and passes selected compatibility tests. | Full-suite, service-backed, hidden-test, downstream, or maintainer acceptance. |
| **Counterfactual evidence** | A local shallow-map variant passes Layer A but leaves error-handler, retry, cache, and timeout values in authored specs. | That an upstream maintainer would have submitted or accepted that exact variant, or that every production caller observes the leak. |
| **External / upstream evidence** | The issue and former PRs establish public context only. | No upstream review, maintainer decision, CI result, downstream integration result, commit, PR, or release exists for this execution. |

## What the competent baseline got right

The baseline was already strong on the engineering core:

- It identified the authoring-versus-compilation boundary and the direct mutation of both `self.nodes` and mutable specs.
- It correctly identified the collision guard as correct and the compiler-owned insertion as the defect.
- It distinguished #8627’s shallow mapping from #8800’s copy-on-write mechanism.
- It selected the same minimal files, ordered implementation steps, alternatives, risk boundary, and public API scope as the executed patch.
- It required repeated invocation, user-name collision preservation, default-policy behavior, handler failure/configuration forwarding, and existing repeat-compile coverage.

Therefore TARGET(AI) did **not** improve implementation selection in this case. Crediting it for the copy-on-write decision would be hindsight reconstruction: the sealed baseline chose it before TARGET(AI) treatment.

## What TARGET(AI) materially added

### More precise state invariant

The baseline substantively separated authored builder state from compile artifacts. TARGET(AI) sharpened the boundary using additional source evidence:

- `self.compiled` is intentional persistent lifecycle state;
- explicit per-node error-handler nodes are intentional authored configuration;
- graph-wide handler insertion and inherited default resolution are compiler-derived state.

The resulting invariant is not “compile never mutates a builder.” It is “compile must not persist compiler-derived default resolution into authored configuration.” This did not change the patch, but it constrained future refactoring and avoided treating legitimate lifecycle state as a defect.

### Stronger mandatory evidence gate

The baseline’s focused checks require default-handler behavior, absent generated handler, and absent authored `error_handler_node`; it treats snapshots for retry/cache/timeout as conditional on whether existing coverage suffices. TARGET(AI) made non-persistence of all four fields required.

Execution showed that distinction has practical value in this precise sense: the shallow-map counterfactual passed repeated compile and invocation while retaining all four values in the authored spec. The stronger gate rejects that repair.

### Completed current-core compatibility audit

The baseline identified `CompiledStateGraph.builder` as an audit prerequisite. TARGET(AI) completed the core search and found the relevant production readers: deferred join target handling and branch source-schema selection. Selected deferred-join and branch-schema tests passed while retaining the original builder reference.

This narrows internal risk. It does not prove downstream compatibility.

## Reason Calibration: actual role

The genuine second Reason pass changed the rationale and acceptance threshold, not the patch:

1. It rejected broad “builder purity” after evidence showed legitimate `self.compiled` and per-node handler persistence.
2. It retained the ephemeral mapping/copy-on-write design because `StateNodeSpec` is mutable and shallow mappings alias its objects.
3. It required a test that distinguishes “duplicate handler collision is gone” from “compiler-derived state is gone.”

The counterfactual makes the third point operational. Calibration was not mere prose polish; it helped turn a previously conditional policy-state observation into a discriminating regression requirement. It did not discover the shallow-copy flaw—the baseline had already done that.

## Layer A versus Layer B

### Layer A alone

Layer A establishes the reported defect’s visible behavior:

- repeated compilation succeeds;
- both compiled graphs invoke and recover;
- generated handler is not present in `builder.nodes`.

The temporary shallow-map variant passed all of those observations.

### Layer B

Layer B establishes the state invariant after compilation:

- authored `error_handler_node` remains unset;
- authored `retry_policy`, `cache_policy`, and `timeout` remain unset;
- generated handler exclusions and explicit precedence still hold in the compiled graph.

The shallow-map variant failed this layer: all four fields were persisted. The copy-on-write implementation passed it.

**Conclusion:** Layer A alone would have allowed a plausible incomplete implementation to be accepted for this experiment’s stated contract. That is the strongest execution finding.

## Process cost and proportionality

### Useful activities

- Freezing the observed behavior and success criteria before treatment.
- Reviewing the actual spec mutability and concrete `compiled.builder.nodes` readers.
- Writing separate Layer A and Layer B regressions.
- Performing one adversarial Reason Calibration pass focused on the state boundary and test sufficiency.
- Tracking execution contradictions: synchronous timeout use was invalid, and compiled retry policies are normalized to tuples. Both adjusted test assertions, not production behavior.
- Using a temporary counterfactual to test the comparison’s proposed discriminating value.

### Overhead without demonstrated value

- Reading and documenting the full method-source context did not alter the patch, alternatives, or key root-cause finding.
- Formal stage names, repeated option presentation, and treatment length did not themselves add executable evidence.
- The experiment’s several pre-execution artifacts are valuable for auditability but are heavier than necessary for a localized two-file fix.

### Was full TARGET(AI) proportional?

**No, not as the default form for a defect of this size.** The full treatment was useful as an experiment measuring the method, but the evidence does not justify that level of ceremony for routine localized engineering work. The incremental value came from one bounded calibration and a stronger invariant test, not from the complete documentation process.

## Recommended lightweight form for similar defects

Adopt the following sequence **conditionally**, when a defect has mutable-state, lifecycle, ownership, or compatibility-boundary risk:

```text
Target + explicit evidence gate
→ focused Assess of mutable state and consumers
→ Reason: root cause, prediction, alternatives
→ one genuine Reason Calibration challenge
→ Execute
→ Layer A behavioral regression
→ Layer B state/invariant regression where the defect can be hidden
→ Track contradictions and adapt
→ short retrospective
```

Use it when a behavior-only test can plausibly mask state corruption, stale configuration, or ownership leakage. Do not apply the full artifact set automatically to straightforward input/output bugs with no such hidden-state boundary. The experiment supports the lightweight form’s focused audit, calibration, and two-layer tests; it does not support mandatory method-book reading or extended prose for every small change.

## Classification: pre-execution versus post-execution

### PRE-EXECUTION CLASSIFICATION

**B — MODEST IMPROVEMENT** remains historically correct and must not be rewritten. At that point, both approaches had selected the same patch, and the stronger evidence gate had not yet been tested.

### POST-EXECUTION EVIDENCE

Execution confirms that the specific stronger validation requirement had practical discriminating value: it failed a local shallow-map repair that passed the behavior layer. This strengthens confidence in the **specific Layer B addition**.

It does not retrospectively convert the classification to A. TARGET(AI) still did not change the implementation decision, and this is one local counterfactual on one defect rather than evidence of a broader outcome improvement.

## Remaining evidence gaps

| Gap | Consequence |
| --- | --- |
| Full LangGraph suite not run | Regressions outside selected default-policy/state/attachment paths remain unobserved. |
| PostgreSQL-backed parameterizations unavailable | Checkpointer-backed service variants did not run; no claim covers them. |
| Prescribed `make`/`uv` workflow unavailable | Equivalent local `pytest`/`ruff` evidence exists, but repository CI parity is incomplete. |
| No maintainer review | Correctness, style, scope, and desired contract have not been assessed by LangGraph maintainers. |
| No downstream evidence | Public or private integrations might depend on generated handler visibility through `compiled.builder.nodes`. |
| No performance measurement | The extra shallow mapping and conditional replacements are not benchmarked. |
| No upstream CI/release outcome | No claim about mergeability, acceptance, or shipped behavior is justified. |

## External contribution assessment

| Level | Assessment |
| --- | --- |
| **A. Experiment evidence sufficient locally** | Yes. The local implementation is focused, linted, `git diff --check` clean, passes selected existing coverage, passes both new layers, and has a direct counterfactual showing the Layer B regression’s value. |
| **B. Repository validation still desirable** | Yes. Run repository-prescribed checks with `uv`/`make`, the practical broader suite, and service-backed PostgreSQL parameterizations before proposing contribution. |
| **C. Upstream acceptance** | Unknown. No maintainer review, CI, downstream compatibility result, PR, or issue discussion was produced in this phase. |

A future upstream contribution is technically justified for local preparation after those validation gaps are addressed. It is not justified to claim merge readiness, maintainer preference, or downstream safety now.

## Strongest defensible public claim

> In a local experiment on LangGraph revision `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1`, a copy-on-write compile-time node view passed selected behavior and state-invariant tests. A controlled shallow-map variant also passed repeated compile/invocation behavior but persisted all four inherited default fields in authored node specs. For this defect, a state-invariant regression provided detection that behavior-only regression did not.

## Claims that would overstate the evidence

- “TARGET(AI) found the correct implementation.” The baseline selected the same design first.
- “TARGET(AI) generally improves engineering correctness.” One controlled local defect does not establish that.
- “Layer A is insufficient for every repeated-compilation defect.” The result is specific to mutable default resolution here.
- “The patch is ready to merge upstream.” Required workflow, service, full-suite, maintainer, and downstream evidence is missing.
- “The patch is accepted, production-safe, or released.” No external/upstream evidence exists.
- “The counterfactual is an upstream defect.” It is a deliberately local, temporary test variant.

## Publication decision

**Publish Experiment 002 in TARGET-AI: yes, as a bounded negative-and-positive case study.** It should report that the baseline chose the same implementation, the methodology added a test boundary rather than a solution, the counterfactual validated that boundary locally, and full TARGET(AI) was disproportionate for routine use. Publishing it as proof of general TARGET(AI) superiority would be misleading.

## Files created

- `002-langgraph-repeated-compile/retrospective.md`
- `002-langgraph-repeated-compile/execution.md` was created during the prior phase and retained at its requested experiment-directory location.
