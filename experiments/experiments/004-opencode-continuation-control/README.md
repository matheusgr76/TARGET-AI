# Experiment 004 — OpenCode Continuation Control

## Question

Can a locally testable cross-turn continuation policy bound repeated identical completed tool calls without disrupting non-identical sequences or existing intra-message loop-control semantics?

## Context

[OpenCode issue #45442](https://github.com/anomalyco/opencode/issues/45442) reported a background agent repeatedly issuing the same `grep` call. Frozen-source inspection found existing `doom_loop` protection, but that control operates within one assistant message. Repeated calls distributed across assistant-message turns can therefore be a different continuation-control problem.

The experiment was frozen against OpenCode `dev` revision `d6855b6b47a8433462ac6aeeba882ccf734cb7f1`. The reported incident was not reproduced with a real provider. This experiment does not claim OpenCode has no loop protection.

## Baseline

The conventional policy tracked 10 consecutive completed cross-turn calls with the same canonical `(tool name, input)` signature:

```text
threshold → deterministic terminal stop/error
```

The threshold of 10 was heuristic, inherited from public prior work, and not empirically calibrated.

## TARGET(AI) treatment

The treatment kept the same detector and threshold. Its second reasoning pass challenged whether repetition alone established task failure:

```text
threshold
→ stop further automatic tool execution
→ one bounded tool-free reassessment
→ closure or terminal error
```

## What execution showed

A disposable deterministic counterfactual harness modeled both policies.

- Both models bounded the eleventh identical automatic call.
- Baseline terminated deterministically at the threshold.
- TARGET could represent useful actionable closure in a scripted fixture.
- An unhelpful reassessment produced zero incremental value.
- Legitimate polling remained a false-positive case.
- Changing output did not affect the frozen input-based detector.
- Frozen-source normal-tool and cancellation smoke tests passed where reported.

The policies were **not** installed in OpenCode. Intra-message `doom_loop` regression was not behaviorally verified, and real-model reassessment reliability was not tested.

## Result

**D — BASELINE PREFERRED**

**Confidence: LOW**

The TARGET transition was conceptually meaningful, but its extra provider turn and reassessment/tool-suppression state were certain costs. Actual OpenCode runtime benefit was not established. The simpler baseline was therefore preferred.

## What TARGET contributed

TARGET exposed a useful distinction:

> Evidence sufficient to stop continued automatic action is not necessarily evidence sufficient to declare the objective itself failed.

The experiment also showed that a better conceptual distinction does not automatically justify a more complex runtime policy.

## Limitations

- Execution used a disposable counterfactual harness, not production OpenCode integration.
- No real provider/model loop was run.
- Real-model reassessment reliability is unknown.
- `doom_loop` regression was not behaviorally tested.
- Background-job integration was not validated.
- Exact repetition does not establish semantic no-progress.
- Legitimate polling remains unresolved.
- Threshold 10 is heuristic.

## Artifacts

- [Frozen brief](frozen-brief.md)
- [Competent conventional baseline](baseline.md)
- [TARGET(AI) treatment](target-ai.md)
- [Pre-execution comparison](comparison.md)
- [Execution evidence](execution.md)
- [Retrospective](retrospective.md)
- [Disposable counterfactual runner](counterfactual_runner.mjs)
- [Machine-readable counterfactual results](counterfactual-results.json)

## Status

Complete. No upstream OpenCode contribution resulted from this experiment.
