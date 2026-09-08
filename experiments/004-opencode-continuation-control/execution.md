# Experiment 004 — Execution

**Phase:** deterministic counterfactual execution; no production implementation.  
**Frozen OpenCode revision:** `d6855b6b47a8433462ac6aeeba882ccf734cb7f1`.  
**Policy artifacts:** sealed before this phase; hashes reverified both before execution and at completion.

## Objective

Compare the sealed policies for one frozen condition: ten consecutive completed cross-turn local calls with the same canonical `(tool name, input)` signature.

- **Baseline:** terminal session error / controlled stop at ten; no additional provider turn.
- **TARGET:** same detector/scope/threshold; no additional automatic tool execution, exactly one tool-free reassessment provider turn, then normal closure or terminal error.

Primary question:

> Does one bounded tool-free reassessment after the repetition threshold provide useful and coherent behavior that justifies its additional complexity and provider turn?

## Environment and setup

| Item | Observation |
| --- | --- |
| Host | Linux x64 under WSL2 |
| Frozen source checkout | `/tmp/opencode-45442` at `d6855b6b47a8433462ac6aeeba882ccf734cb7f1` |
| Runtime | Bun `1.3.14`; Node `v22.23.2` for disposable harness |
| Dependency setup | `bun install --frozen-lockfile` in the isolated `/tmp/opencode-45442` checkout |
| Install result | 4,715 packages installed; root `postinstall` ran `packages/core` `fix-node-pty`; no lockfile/dependency declaration was edited |
| Production source edits | None |
| Disposable experiment files | `counterfactual_runner.mjs`, `counterfactual-results.json` |

The earlier missing `@opentui/solid/preload` blocker was resolved by this frozen-lockfile installation.

## Exact commands

```sh
# Verify source and sealed artifact hashes
cd /tmp/opencode-45442 && git rev-parse HEAD
cd /home/matheusgr/projects/TARGET-AI/experiments && \
  sha256sum experiments/004-opencode-continuation-control/{frozen-brief,baseline,target-ai,comparison}.md

# Establish isolated frozen dependency environment
cd /tmp/opencode-45442 && bun install --frozen-lockfile

# Existing frozen-source smoke checks
cd /tmp/opencode-45442/packages/opencode && \
  bun test --timeout 30000 test/session/prompt.test.ts \
  --test-name-pattern 'glob tool keeps instance context during prompt runs'
cd /tmp/opencode-45442/packages/opencode && \
  bun test --timeout 30000 test/session/prompt.test.ts \
  --test-name-pattern 'cancel finalizes subtask tool state'

# Counterfactual A/B fixtures
cd /home/matheusgr/projects/TARGET-AI/experiments/experiments/004-opencode-continuation-control && \
  node counterfactual_runner.mjs | tee counterfactual-results.json
```

An initial normal-test invocation without `--timeout 30000` timed out at the test framework’s five-second default. The same unmodified test then passed with the command above in 14.45 seconds. This is recorded as an environment/timing deviation, not as a source failure.

## Execution approach and evidence strength

### Actual frozen-source checks

1. `glob tool keeps instance context during prompt runs`: passed; 4 assertions; 14.45 seconds.
2. `cancel finalizes subtask tool state`: passed; 6 assertions; 3.58 seconds.

These prove only the current prompt test runtime can execute a normal tool/text loop and its existing cancellation finalization test in the frozen checkout. They do **not** implement or prove either counterfactual continuation policy.

### Disposable A/B counterfactual harness

`counterfactual_runner.mjs` models the relevant frozen OpenCode state boundary rather than patching production code:

- each scripted provider response creates one assistant-message turn;
- each tool action creates a completed tool part with tool/input/output/state;
- canonical input signatures preserve sorted object keys and array order;
- session state transitions between `busy` and `idle`;
- events record threshold, error, reassessment, suppression, and cancellation;
- baseline stops on threshold;
- TARGET allows exactly one empty-tool reassessment state; and
- assertions reject extra tool execution, extra provider continuation beyond the selected policy, or non-idle terminal state.

This is a **counterfactual state-machine result**, not a faithful OpenCode integration result. It uses OpenCode’s observed conceptual seams and state vocabulary, but does not instantiate `SessionPrompt`, `SessionProcessor`, provider message serialization, `SessionTools.resolve`, or `BackgroundJob` under either unmerged policy. It therefore establishes only policy-model capability, not frozen-runtime compatibility.

## Raw counterfactual observations

Full machine-readable results: `counterfactual-results.json`.

| Fixture | Baseline observation | TARGET observation |
| --- | --- | --- |
| Normal completion | 1 tool, 2 provider turns, normal + `idle`; no event | Same |
| Alternating inputs | 4 tools, 5 provider turns, normal + `idle`; no threshold | Same |
| Changing inputs | 12 tools, 13 provider turns, normal + `idle`; no threshold | Same |
| 9 identical | 9 tools, 10 provider turns, normal + `idle`; no threshold | Same |
| 10 identical / queued 11th | 10 tools, 10 provider turns, threshold then `repeated-identical-tool-call` error, `idle`; queued 11th not consumed | 10 tools before reassessment; policy requires a separate 11th **tool-free** provider turn |
| Useful reassessment | Not applicable: terminal baseline error after 10 | 10 tools + 1 tool-free provider turn; normal + `idle`; text says automatic checks were bounded, identifies pending deployment, asks for event/continuation instruction |
| Unhelpful reassessment | Not applicable: terminal baseline error after 10 | 10 tools + 1 tool-free provider turn; text `I appear to be stuck.`; terminal error + `idle`; incremental usefulness `NONE` |
| Adversarial tool request during reassessment | Not applicable | 10 tools; reassessment request attempts `glob`; harness records suppression and terminal `reassessment-tool-request` error; 11th tool never executes; `idle` |
| Legitimate polling | 10 `check_deployment` calls with changing `pending N` outputs; terminal error + `idle` | 10 calls then one tool-free actionable request to confirm waiting or inspect logs; normal + `idle`; automatic polling still interrupted |
| Changing output | 10 same `status({})` calls with 10–100% outputs; terminal error + `idle` | 10 calls then one tool-free message; normal + `idle` |
| Cancellation before threshold | 3 tools, cancel, `idle`, terminal `cancelled` | Same |

### Detector behavior

The harness confirms, by construction and assertion, that both policies:

- use the same threshold: 10;
- permit 9 matching completed calls;
- do not fire for alternating or changing inputs;
- fire despite changing output because output is not part of the frozen detector; and
- do not execute an eleventh automatic identical tool call.

### State integrity in the modeled policies

All modeled terminal fixtures end `idle`. All recorded tool parts are `completed`; no modeled part or background state is `running`. Baseline emits threshold plus terminal error. TARGET emits threshold plus reassessment-requested/completed, or threshold plus suppression plus terminal error for adversarial tool request.

This is assertion-backed harness behavior, not evidence that the unmodified frozen OpenCode runtime can produce the same state transitions.

## Required fixture interpretation

### Baseline terminal behavior

At the model boundary, baseline is deterministic: 10 tools/10 provider turns, visible `repeated-identical-tool-call` error, no text closure, and no consumed queued 11th provider turn. This matches its sealed intent. It does not lose points for providing no prose.

### TARGET reassessment behavior

At the model boundary, TARGET consumes one additional provider turn, exposes an empty tool set, and terminates after that turn. The useful fixture contains pre-registered actionable content: it explains the bound, summarizes unresolved deployment state, and requests concrete intervention. The unhelpful fixture is deliberately classified as `NONE`, not success.

### Adversarial tool request

The harness shows the selected TARGET state machine can suppress a reassessment tool request and terminate cleanly. It does **not** prove that frozen OpenCode’s provider/tool protocol would prevent a raw tool call in an empty-tool turn, because that integration was not implemented.

### Polling and changing output

Both policies fire after ten same-signature calls even when outputs change. This exposes the frozen detector’s intentional false-positive cost. TARGET’s additional text can be useful, but it does not support automatic polling; polling is still interrupted.

### Shared false negative

Alternating and changing-input fixtures remain unbounded by the detector and complete only because the deterministic sequence ends. This is an intentional shared blind spot, not a treatment-specific result.

## `doom_loop` and background-job limitations

The counterfactual harness does not execute existing intra-message `doom_loop` permission resolution, and no current frozen prompt test directly exercised it in this run. Source evidence remains that it is a separate current-assistant-message check. Therefore the required **behavioral `doom_loop` non-regression is unverified** for either unimplemented policy.

The actual cancellation test finalizes a subtask tool state, but no counterfactual policy was installed in a child background run. Consequently, background-job terminal-state compatibility is **unverified** beyond the modeled no-stale-running invariant.

These are material limitations, not passing results.

## Cost accounting

| Cost | Baseline | TARGET |
| --- | --- | --- |
| Automatic tools after threshold | 0 | 0 |
| Provider turns after threshold | 0 | 1 |
| New control state | canonical signature/count | canonical signature/count + `reassessmentIssued` |
| New transitions | threshold → terminal error | threshold → tool suppression → reassessment → normal closure/error |
| Required additional tests | threshold/error/state regression | all baseline coverage + no-tool protocol, adversarial request, useful/unhelpful closure, reassessment cleanup |
| Protocol risk | low/local terminal transition | higher: empty-tool provider turn and message/state compatibility |

## Capability versus reliability

**Capability:** the deterministic counterfactual policy model can provide a bounded, useful reassessment with no eleventh tool execution, one provider turn, actionable text, and coherent modeled `idle` closure.

**Reliability:** not established. No real model was queried, no provider protocol path was run under temporary TARGET production logic, and a deterministic scripted text response cannot show that real models reliably produce useful reassessment.

## Execution verdict

**D — BASELINE PREFERRED, LOW confidence.**

### Evidence that discriminated the policies

The counterfactual fixture makes the behavioral cost explicit: TARGET always adds one provider turn and extra state/transition complexity. It can express useful closure when given a useful deterministic reassessment response, while baseline cannot because it immediately terminates. It can also yield zero incremental value when given `I appear to be stuck.`

### Why D rather than A/B/C

The useful output was scripted into a disposable model and did not execute through frozen OpenCode’s actual provider/tool boundary. It shows only that the proposed state machine can represent useful text, not that the frozen architecture can implement it coherently or that the extra turn reliably adds useful information. The known additional cost is real in the policy model; the architecture-level benefit is not yet demonstrated. Baseline’s simpler bounded stop therefore has the stronger evidence at this phase.

### What did not discriminate

Both policies have the same detector, threshold, false negatives, output-variation false positive, cancellation intent, and liveness bound on automatic tool execution. Alternating/changing-input sequences and nine-call boundary fixtures do not favor either treatment.

### Did Reason Calibration survive execution?

**Not established.** The calibration’s revised transition is internally coherent in the counterfactual model, including the useful and adversarial fixtures, but has not survived an actual `SessionPrompt`/provider protocol execution. It has not justified its added cost.

## Deviations, blockers, and limitations

1. The available frozen source has neither policy implemented. A direct A/B runtime test would require temporary production-source policy patches plus a new test fixture. This execution deliberately preferred a disposable harness to avoid contaminating the frozen checkout and to keep the two treatments symmetric.
2. The harness is not an actual OpenCode policy integration. It cannot establish `SessionTools.resolve` empty-tool behavior, provider serialization compatibility, `doom_loop` behavioral preservation, or background-job behavior.
3. The normal current-source test initially exceeded Bun’s five-second default but passed at 30 seconds; no source change was made.
4. Deterministic reassessment texts establish capability only at the harness level, never reliability of real models.
5. Final verdict confidence is low because the discriminating transition remains unimplemented in the actual runtime.

## Non-execution boundary

No sealed artifact was edited. No OpenCode production source was edited. No commit, push, issue/PR action, maintainer contact, retrospective, or external model request occurred.
