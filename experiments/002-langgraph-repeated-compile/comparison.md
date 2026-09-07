# Pre-Execution Comparison — Experiment 002

> **Comparison scope:** `frozen-brief.md`, sealed `baseline.md`, and sealed `target-ai.md` only. This document does not modify either treatment or claim an implementation outcome.
>
> **Classification: B — MODEST IMPROVEMENT.** TARGET(AI) did not change the preferred patch, files, or basic regression shape. It strengthened the current-core compatibility evidence, made the authored-versus-derived state boundary more precise, and made the all-default non-persistence check an explicit evidence gate. Those differences can prevent a partial repair from being accepted, but have not yet produced or validated a better implementation.

## Comparison standard

A difference counts only when the sealed artifacts show a changed decision, assumption, risk boundary, or validation requirement that could affect a future patch or its acceptance. More prose, named stages, confidence language, or repeated restatement does not count as improvement.

The frozen brief already supplied the issue reproduction, current source mutation of all four default-related fields, prior PR directions, unknowns, and success criteria. Both treatments relied on that same public starting state. TARGET(AI)'s later source audit is additional current-public evidence, not privileged evidence and not proof that the proposed patch works.

## Executive findings

| Question | Determination | Artifact evidence |
| --- | --- | --- |
| Did TARGET(AI) change the preferred implementation? | **No.** Both select the #8800-style ephemeral mapping plus copy-on-write replacement for nodes receiving defaults. | Baseline §§78–99; TARGET §§97, 102–111. |
| Did TARGET(AI) materially improve the invariant? | **Yes, but as a refinement, not a new direction.** It explicitly excludes intentional lifecycle/authoring persistence from the non-persistence requirement. | Baseline §§36–45 and 64–68 already distinguish authored builder from compile artifact; TARGET §§51–60 and 119–130 adds `self.compiled` and explicit per-node handlers as counterexamples to blanket purity. |
| Was the distinction substantively present in the baseline? | **Yes.** The baseline says compile-derived nodes/defaults belong to the compiled artifact and authored nodes/configuration stay in the builder. It does not expressly classify intentional `self.compiled` state or per-node handler generation. | Baseline §§36–45, 64–68. |
| Did TARGET(AI) materially strengthen validation? | **Yes.** It turns the all-default non-persistence concern from conditional/additional coverage into an explicit required evidence gate. | Baseline §§149–152 versus TARGET §§152–170. |
| Could the added tests catch a defect baseline validation could miss? | **Yes.** A patch that fixes only handler insertion/routing can pass baseline's listed error-handler-focused builder checks while still persisting inherited retry/cache/timeout fields. | Baseline §§136–152; TARGET §§121, 125, 154–156. |
| Did Reason Calibration change anything material? | **Partly.** It did not change the patch, but it replaced an overbroad purity rationale with a bounded state-ownership invariant and raised the acceptance evidence threshold. | TARGET §§119–132 compared with baseline's already-similar plan §§84–99. |
| Was the additional process worth it? | **Mixed.** The focused source audit and calibration were proportionate because they identified a real state-boundary qualification and an executable missing test gate. The methodology-reading and expanded process framing have no demonstrated incremental value for this small localized defect. | TARGET §§187–192; no implementation evidence exists. |

## Criterion-by-criterion comparison

| Criterion | Baseline | TARGET(AI) | Material difference and evidence-backed effect |
| --- | --- | --- | --- |
| **Problem framing** | Defines `StateGraph` as authored builder and compile as producing a compiled graph; repeated compile with compile-time choices is valid. | States an explicit bounded target: repeatable default-handler compile without turning derived configuration into authored state. | Equivalent substantive framing. TARGET adds a formal target/evidence/constraint/horizon record; no implementation decision follows from that format alone. Baseline §§36–45; TARGET §§18–25. |
| **Root cause** | Identifies direct use of `self.nodes` and mutable specs instead of an ephemeral compilation view; collision guard is correct. | Same diagnosis, with the generated handler’s namespace and mutable spec aliasing explained separately. | Equivalent root cause. TARGET's prediction that a collision-only fix can pass while leaks remain makes the failure mode more explicit, but baseline already rejects the shallow fix for exactly that reason. Baseline §§49–53, 74–80; TARGET §§64–87. |
| **State / invariant** | “Compile-derived nodes and compile-derived default values” belong to the compiled artifact; builder retains authored nodes/config. | Separates authored state, intentional lifecycle state (`self.compiled`), explicit per-node generated handlers, and compiler-derived defaults/handler/map. | Modest improvement. It prevents a future engineer from interpreting the repair as a mandate to eliminate all compile-time persistence. The baseline already had the central authoring/compiled boundary, so this is refinement rather than a new invariant. Baseline §§36–45, 64–68; TARGET §§51–60, 119–120. |
| **Assumptions exposed** | Names compile-time default semantics, generated-handler exposure risk, `replace()` suitability, and hidden compatibility uncertainty. | Repeats those assumptions, then tests them against source: mutable `StateNodeSpec`, no internal identity use, and actual builder-node readers. | TARGET converts two baseline implementation prerequisites into completed current-core evidence. It reduces uncertainty inside the repository but cannot resolve downstream consumers. Baseline §§55–60, 123–130, 156–167; TARGET §§41–49, 70–75, 122–124. |
| **Unknowns** | Enumerates external builder-reader compatibility, replacement semantics, full default coverage, attachment leakage, and hidden tests. | Retains downstream/hidden/combined-default/allocation unknowns; closes only the searched internal consumer and identity-use questions. | Modest improvement in uncertainty classification: “not found in core” is separated from “unknown downstream.” The uncertainty set is otherwise equivalent. Baseline §§162–167; TARGET §§47–49, 180–185. |
| **Evidence demanded** | Requires repeated execution, builder absence of default handler and routing, collision/semantic regressions; suggests broader default-field snapshots only if existing coverage is insufficient. | Requires execution plus explicit proof that all inherited default-policy fields do not persist; defines pass, ambiguous, and fail outcomes. | Material validation improvement. The explicit gate prevents accepting a #8627-like shallow-map repair merely because the issue reproduction passes. Baseline §§132–152; TARGET §§150–170. |
| **Alternatives / rejections** | Rejects collision suppression, cleanup, shallow copy, deep copy, persistent internal marking, API changes. | Rejects the same options, plus frames persistent idempotent helper insertion as stale configuration risk. | Equivalent decision space and rejection outcome. TARGET's wording adds no separate viable alternative or changed tradeoff. Baseline §§101–110; TARGET §§89–98. |
| **Preferred implementation** | Local map after validation; original collision guard; local generated handler; `replace()` changed specs; local map for routing/attachment; builder unchanged. | Same ordered steps and conditions. | Equivalent. No basis exists to credit TARGET(AI) with a better patch selection. Baseline §§84–99; TARGET §§100–111. |
| **Scope control** | Limits changes to `state.py` and focused retry tests; excludes public API/docs/checkpoints/unrelated builders. | Same files and exclusions, additionally says not to change builder ownership or explicit per-node handler generation. | Minor refinement. Both prevent scope expansion; TARGET's named exclusions follow from its state taxonomy. Baseline §§112–121; TARGET §§134–148. |
| **Compatibility risks** | Flags original builder reference, propagation loss, collision ordering, spec identity, and allocation cost; calls for audit. | Records the actual internal-reader audit and distinguishes low internal risk from unknown downstream risk. | Modest improvement. A future implementation can now preserve `CompiledStateGraph.builder` with evidence that known readers concern authored topology/schema. It is not proof of public compatibility. Baseline §§154–167; TARGET §§47–49, 122–124, 180–185. |
| **Validation strategy** | Strong focused behavior test plus existing semantic and repeat-compile regressions. Broader default-field checks are conditional on whether current coverage suffices. | Same core suite, but makes non-persistence of error handler/retry/cache/timeout a required focused check and establishes a decision gate for ambiguous results. | Materially stronger acceptance criterion, not a different runtime behavior target. It could expose a partial fix even if existing policy behavior tests pass. Baseline §§132–152; TARGET §§150–170. |
| **Stopping / evidence conditions** | Gives an implementation plan and test sequence; confidence 0.86 with bounded uncertainty. | Stops treatment only after target, competing options, second Reason pass, and pass/ambiguous/fail criteria are recorded. | TARGET has clearer pre-execution stopping evidence, but it is process control rather than a changed patch decision. Baseline §§123–130, 169–173; TARGET §§18–25, 166–178. |
| **Confidence** | Explicit high confidence, 0.86, tied to reproduction/source and bounded risks. | No numeric confidence; it records predictions and remaining uncertainties. | Baseline is better on concise calibrated confidence communication. TARGET avoids unsupported precision but does not provide an equally compact confidence decision. Baseline §§169–173; TARGET §§77–87, 180–185. |
| **Process overhead** | Conventional evidence review and implementation/validation plan in 173 lines. | Reads method sources, adds TARGET stages, performs a new source audit and a second Reason pass, then writes 192 lines. | Only the source audit and calibration produced decision-relevant additions. More terminology and artifact structure are overhead not demonstrated to improve this localized analysis. Baseline §§11–32; TARGET §§7–16, 187–192. |

## Claimed improvements, with required evidence chain

### 1. Narrower, safer state invariant — modest improvement

1. **Baseline:** identifies the authoring/compiled boundary and calls builder-purity preservation necessary for compile-derived nodes/defaults (baseline §§36–45, 64–68).
2. **TARGET(AI):** adds evidence that `self.compiled` and explicit per-node handler nodes are deliberate persistent state, then defines the prohibited state as compiler-derived default expansion (TARGET §§43–60, 119–130).
3. **Material difference:** TARGET prevents the phrase “builder purity” from being misread as a general no-mutation rule.
4. **Why it could affect implementation/validation:** without this distinction, a repair could accidentally remove intended lifecycle warnings or move explicit handler authoring into compilation. TARGET directs tests/change review to preserve those behaviors rather than treating all persistence as a defect.
5. **Supporting evidence:** the cited source findings were discovered during TARGET's source audit. The baseline had the core boundary already, so the gain is precision and risk control, not a new solution.

### 2. Explicit all-default non-persistence gate — material validation improvement

1. **Baseline:** requires absent generated handler and absent `error_handler_node`, while describing retry/cache/timeout state checks as additional only if existing behavior coverage does not suffice (baseline §§136–152).
2. **TARGET(AI):** requires tests proving inherited error handler, retry, cache, and timeout defaults do not persist in authored specs, with conditional async/direct coverage only for the practical timeout test form (TARGET §§152–170).
3. **Material difference:** the broader lifecycle property becomes mandatory instead of discretionary.
4. **Why it could affect implementation/validation:** a shallow mapping or partial copy-on-write implementation can remove the duplicate handler and preserve runtime behavior for one compile while leaving retry/cache/timeout values on `StateNodeSpec`. TARGET's gate would reject it.
5. **Supporting evidence:** both artifacts establish direct writes to all four fields; the frozen success criteria independently require no default-derived field mutation. Baseline §§21–24, 49–53, 149–152; frozen brief §§36–44, 91–97; TARGET §§121, 125, 154–156.

### 3. Completed current-core compatibility audit — modest improvement

1. **Baseline:** identifies `CompiledStateGraph.builder` as the principal compatibility boundary and schedules audit of all direct readers before implementation (baseline §§68, 82, 123–130, 154–167).
2. **TARGET(AI):** conducts the repository search and records the two production reads plus their authored topology/schema purposes (TARGET §§41–49, 122–123).
3. **Material difference:** an implementation no longer starts with that internal audit as an open prerequisite.
4. **Why it could affect implementation/validation:** it supports preserving the original builder while keeping the generated default handler exclusively in the compiled node mapping. It also identifies the boundary that should be smoke-tested if code changes.
5. **Supporting evidence:** TARGET’s explicitly scoped repository search. The result does not establish downstream compatibility, which TARGET retains as unknown.

## Equivalence, baseline advantages, and TARGET-only overhead

### Equivalent substantive reasoning

- Same immediate cause: generated helper insertion plus mutation of mutable specs.
- Same diagnosis that collision suppression or shallow copying is incomplete.
- Same preferred #8800-style local mapping/copy-on-write patch.
- Same narrow changed files and preservation of collision/default precedence semantics.
- Same principal compatibility risk: `CompiledStateGraph.builder` and possible external consumers.
- Same need to invoke both compiled graphs, retain collision coverage, and run existing default-policy/repeat-compile tests.

### Baseline better

- **Efficiency:** it reaches the correct implementation direction, rejected alternatives, risks, and focused test plan without methodology setup or a separate calibration artifact.
- **Confidence communication:** the baseline's explicit 0.86 confidence and justification is clearer than TARGET(AI)'s unquantified predictions/uncertainties.
- **Proportionality at the decision level:** for a localized visible mutation defect, the baseline already captures the important authoring-versus-compiled distinction and the complete fix direction.

### TARGET(AI) overhead or unnecessary reasoning

- TARGET(AI)'s formal stage labels, method-source documentation, and repeated option framing do not by themselves change the patch or runtime target.
- The treatment spends substantial text distinguishing full builder immutability from scoped non-persistence. This is useful guardrail reasoning, but the baseline's wording was already substantially aligned; it should not be counted as a novel root-cause discovery.
- The fallback discussion of a dedicated immutable compilation-view object is appropriate as a failure contingency, not current implementation scope. It must not be treated as a recommendation absent a failing evidence gate.

## Process-overhead assessment

**Decision:** partially worthwhile, not conclusively justified as a whole.

For this defect, the incremental effort with clear practical value was the source audit and adversarial calibration: they establish that intentional lifecycle state exists, identify current internal `builder.nodes` readers, and make non-persistence of all resolved defaults a required acceptance condition. Those are plausible correctness gains.

The additional method reading, formal stage structure, and length have no demonstrated causal value yet. Because no patch has run, the experiment cannot show that the process prevented a real implementation defect. The appropriate conclusion is therefore **B, modest improvement**, rather than material improvement.

## Required execution evidence to test practical value

A later authorized execution cycle must establish whether the comparison's reasoning differences matter in practice:

1. **Focused lifecycle regression:** compile/invoke the issue graph twice and prove both compiled graphs use the default handler.
2. **Authored-state snapshot:** before/after compile, verify no generated handler or inherited `error_handler_node`, `retry_policy`, `cache_policy`, or `timeout` persists on the authored node specs when those defaults apply.
3. **Combined-default behavior:** exercise default combinations sufficiently to prove copy-on-write preserved explicit precedence and the existing rule that handler nodes do not route/cache through the default handler while retry/timeout still apply as designed.
4. **Compatibility boundary:** exercise or inspect affected join-edge `defer` and branch source-schema paths after the local resolved mapping is introduced; retain the original `CompiledStateGraph.builder`.
5. **Existing behavior:** run existing error-handler, retry/cache/timeout, collision, and repeat-compile coverage.
6. **Counterfactual value:** if a deliberately incomplete shallow-map or handler-only repair would pass the baseline-focused checks but fail the added non-persistence checks, the added TARGET(AI) validation boundary has demonstrated practical discriminating value. Do not ship that counterfactual; it is a test-design criterion, not an implementation instruction.

## Pre-execution limit

This classification concerns reasoning and planned evidence only. It does **not** establish that TARGET(AI) yields a better implementation, prevents an actual future regression, or has favorable cost-benefit in production. Those claims require the authorized implementation and execution evidence above.
