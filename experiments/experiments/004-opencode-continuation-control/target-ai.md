# Experiment 004 — TARGET(AI) Treatment

**Treatment scope:** TARGET-Lite design selection only. No production source, tests, OpenCode configuration, external issue, or pull request was modified.  
**Starting evidence:** sealed `frozen-brief.md`, SHA-256 `d6000212cef18f121f9b45fd36737d57f0c083d6c006f16f2ae3f5db2aeb8356`, and the same frozen public evidence available to the conventional baseline.  
**Frozen OpenCode revision:** `d6855b6b47a8433462ac6aeeba882ccf734cb7f1` on `dev`.

## T — Target

### Decision

Select a locally testable continuation policy for this bounded runtime condition:

> A single parent user-message run receives repeated completed local tool calls with the same canonical tool name/input across separate assistant turns.

### Desired outcome

Before the sequence can consume provider turns indefinitely, the runtime creates a visible and bounded control transition. The transition must preserve ordinary non-identical continuation and existing intra-message `doom_loop` semantics.

### Unacceptable outcomes

- treating every repeated action as proof of no progress;
- replacing or changing `doom_loop` permission behavior;
- adding generic semantic-progress, parent-watchdog, global budget, or provider-quality machinery;
- silently leaving tool, session, or background state `running`; or
- adding an unbounded “reassess” loop that merely changes the form of token burn.

### Scope and non-goals

Scope is one frozen OpenCode revision, one local runtime boundary, one session/user-message run, and completed local calls. Non-goals are generic runaway-agent prevention, semantic information-gain inference, a durable heartbeat, automatic polling taxonomy, global token/step budgets, and provider/model remediation.

### Trade-off and improvement threshold

Repeated action is not automatically pathological. The decision is whether continued execution remains justified when exact syntactic evidence repeats. Intervention is justified only if it both imposes a deterministic upper bound on pathological continuation and gives a legitimate repeated workflow a bounded, visible opportunity to explain or conclude rather than silently treating it as a confirmed failure.

## A — Assess

### Facts

- `SessionPrompt.runLoop()` creates a new assistant message per provider turn.
- `SessionProcessor` processes the tool calls within that assistant message.
- `doom_loop` inspects the last three tool parts of the current assistant message only. It is intra-message control and does not aggregate cross-turn history.
- Tool name, input, output, state, timestamps, assistant-message boundaries, session status, events, child relation, and explicit abort are observable.
- Session status is `busy`, `retry`, or `idle`; background jobs are `running` or terminal. Neither supplies a first-class progress/heartbeat metric.
- Explicit cancellation exists and provider-error retries are bounded.
- `agent.steps` is not a reliable hard cap on this path; the default `general` effective limit is unbounded.
- PR #46272 publicly proposes a 10-call, canonical-name/input, cross-turn terminal-error guard. It is open and unmerged. Its threshold is heuristic and it does not compare outputs.
- Legitimate polling, transient retries, and repeated idempotent reads can have identical inputs.

### Assumptions

- A completed local tool call is a better accounting boundary than an input-start event: it records that work actually occurred and provides durable state for a run-level decision.
- Ten exact consecutive calls are strong enough evidence of questionable continuation to require a control boundary, but not proof of semantic no-progress.
- A model can provide useful human-facing closure if presented one constrained, tool-free reassessment opportunity.
- Passing an empty tool set for exactly one provider turn is implementable in the current prompt/processor flow; this is a design assumption to validate later, not an executed result.

### Decision-changing unknowns

1. **Can a tool-free reassessment turn be introduced without changing provider protocol invariants or leaving a malformed tool/result history?** If not, a terminal visible error is the only honest bounded transition supported by the frozen path.
2. **Does one constrained reassessment response materially improve the false-positive cost for legitimate repetition?** If it does not reliably produce a useful conclusion, it adds cost without reducing interruption harm.
3. **Can session error/warning visibility be expressed without incorrectly marking a still-valid reassessment turn as terminal?** If no nonterminal event exists, an explicit terminal error may be preferable.

These uncertainties can change the selected transition, unlike unknowns about generic semantic progress that this architecture cannot currently resolve.

### Constraints

- Only frozen evidence is admissible.
- Existing `doom_loop` semantics must remain unchanged.
- The policy must be deterministic and locally testable.
- No production implementation occurs in this treatment.
- The strongest claim remains local and experimental.

## R — Reason

### Pass 1 — initial recommendation

**Initial policy:** match PR #46272’s smallest cross-turn control: count consecutive completed local calls by canonical `(tool name, input)` within the parent user-message run; at ten, publish a terminal session error and stop before the next provider turn.

Reasoning: it closes the specific message-boundary gap, is entirely observable, does not pretend to know semantic progress, is cheap to test, and preserves `doom_loop`. Output equality is excluded because it is not a reliable generic progress signal. A fixed terminal error avoids an unbounded model-mediated recovery path.

**Strongest initial assumption:** ten exact repetitions provide sufficient evidence to terminate a task rather than merely challenge its continuation.

### Reason Calibration — adversarial second pass

The initial policy was challenged against the frozen counterexamples.

| Challenge | What it shows | Effect on initial policy |
| --- | --- | --- |
| Legitimate deployment polling | Ten exact calls can be intentional and external state may change later | A terminal error is a high-cost false positive; repetition is evidence for review, not proof of failure |
| Same input, changing output | Different output may represent progress, but may also be irrelevant decoration | Output equality should not be a required detector signal |
| Same input, same output while external state may change | Identical output is still not proof that continued polling is useless | A same-input/output counter would falsely claim semantic certainty |
| Alternating two calls forever | Exact consecutive counting does not bound all loops | Preserve narrow scope; do not broaden to semantic or global control |
| Syntactically varied equivalent calls | Canonical structural equality cannot identify semantic equivalence | Do not claim coverage beyond exact canonical representation |
| Repeated idempotent local reads | Reads can be deliberate rechecks, though ten exact turns are suspicious | Favor an explainable reassessment boundary over immediate terminal failure |
| Transient failure retry | Repetition can be correct if a retry contract exists | Do not infer retry intent absent tool metadata; retain explicit cancellation/new prompt path |
| Long valid task | A global step cap would halt productive diverse work | Reject general hard-step policy |

**Calibration conclusion:** the initial detector survives, but the **terminal transition does not**. The evidence at ten exact completed calls is sufficient to deny unlimited continuation, but insufficient to assert confirmed no-progress or immediate task failure. Current architecture has no honest general pause state, but it does have the prompt/tool boundary needed for one bounded tool-free reassessment turn.

**Initial policy**

> Ten exact cross-turn completed calls → terminal session error and stop.

**Contradicting reasoning**

> Exact repetition is a strong liveness signal but not proof of semantic failure. Immediate termination makes a legitimate long poll indistinguishable from a confirmed pathological loop and loses a cheap opportunity for the model to summarize, request input, or state why it is waiting.

**Revised policy**

> Ten exact cross-turn completed calls → visible continuation-control event plus exactly one tool-free reassessment turn. That turn must produce text-only closure, a blocker, or an explicit request for new user instruction; it cannot issue another tool. If the constrained turn cannot be completed correctly, record a terminal session error. No additional automatic tool turn is permitted under the same control state.

The detector stayed the same; the action semantics became more precise. This is a genuine change, not a terminology substitution.

## G — Generate

| Policy | Detection / state | Transition | False-positive risk | False-negative risk | Architecture fit / testability |
| --- | --- | --- | --- | --- | --- |
| Exact canonical counter, terminal error | Per-run last signature and count | Stop before next provider turn | High for legitimate polling | Alternation, syntactic variation, <10 calls | Direct fit; easy deterministic test; matches public PR direction |
| Exact canonical plus same output | Canonical signature, output normalization/equality, count | Stop or warn | Still high for external polling; output equality can mislead | Output variation evades; normalization is fragile | Poorer fit; extra representation and privacy/size decisions |
| Hard turn/step budget | Global run turn count | Stop | High for long productive work | Does not target repetition | Out of frozen scope; current `agent.steps` is advisory |
| Explicit polling/retry allowance | Tool capability/metadata and policy state | Continue allowed repeats | Low for marked polling | Unmarked loops escape; metadata can be abused/misclassified | No frozen universal contract; expansion not justified |
| Exact counter, one tool-free reassessment **(selected)** | Same detector plus `reassessmentIssued` state | Visible event; one no-tool provider turn; then terminal closure/error | Lower than immediate stop because it permits explanation, but still interrupts polling | Alternation, syntactic variation, reassessment may be unhelpful | Local prompt/tool boundary; needs deterministic protocol/state tests |
| Parent watchdog / heartbeat | Child activity and durable parent observation | Parent escalation/cancel | Unknown; risks false stale classification | Cross-turn action loop may still run | First-class progress data absent; out of scope |

### Evidence gate

The minimum evidence to justify the **detector** is different from the evidence to justify each transition:

| Claim | Minimum evidence required |
| --- | --- |
| Exact repetition exists | deterministic queued separate assistant turns carrying same completed local tool name/input |
| Continuation is plausibly pathological | count reaches a predetermined threshold without a different qualifying action; tool state/output history remains inspectable |
| Unlimited continuation should be denied | test proves that threshold state blocks all further automatic tool turns for the run |
| A reassessment turn is justified | test proves one tool-free provider turn can be delivered without malformed history, consumes no tool action, and produces an observable closure/error state |
| Immediate terminal failure is justified | stronger evidence than currently frozen: either tool-specific contract says repeats are invalid, or constrained reassessment is technically unsupported/unsafe |
| Generic semantic no-progress decision | unavailable: current architecture lacks the required semantic signal |

The asymmetry is material. A false positive interrupts legitimate repeated work, but is reversible by new user input; a false negative allows potentially expensive continuation. The selected policy puts the irreversible/resource-sensitive decision at the boundary of **automatic tools**, not at the boundary of all model output. It buys one bounded response to reduce false-positive severity without allowing unbounded recovery.

## E — Execute decision

### Selected experimental policy

**Cross-turn exact-repeat detector with one tool-free reassessment transition.** This is an experimental policy candidate, not a production-correct fix.

#### Tracked state

- `parentUserMessageID` for scope;
- last completed qualifying canonical signature: tool name plus recursively canonicalized structured input;
- `consecutiveCount`; and
- `reassessmentIssued: boolean` for this scope.

A qualifying part is a completed locally executed tool part. Provider-executed parts and cleanup-marked interrupted/orphan parts are excluded.

#### Scope and equality

State is local to one session and one parent user-message run. It does not cross a new user message, session, or unrelated parent/child run.

Equality is byte-equal tool name plus canonical structural input equality: object keys sorted recursively, array ordering preserved, and null/undefined/absence retained according to the stored representation. It makes no shell, path, regex, or semantic-equivalence inference.

#### Threshold

**10 consecutive matching completed calls.** This is an uncalibrated heuristic inherited from public prior art, chosen as a bounded experiment constant, not an empirical optimum.

#### Output equality

**Output equality does not decide admission.** Outputs remain observable evidence in execution review. Requiring equal output would confuse a representation property with semantic progress and would not resolve legitimate external polling.

#### Reset conditions

Reset on a new parent user-message ID, a different qualifying signature, ordinary terminal completion, explicit cancellation, or completion of the bounded reassessment transition. A non-tool assistant response does not reset the signature during the same parent run; otherwise inert text could evade an exact-repeat guard.

#### Legitimate-repeat treatment

No automatic polling exception is introduced. At threshold the runtime gives one text-only opportunity to state the wait condition, summarize, request user instruction, or report a blocker. Continuing identical polling automatically requires a new user prompt or a future explicit tool-level polling contract.

#### Transition at threshold

1. Publish a visible continuation-control event/error-equivalent with stable reference and tool/count context.
2. Mark `reassessmentIssued` before another provider request.
3. Make exactly one provider request with tools unavailable and an explicit instruction that the same completed action repeated ten times; require a text-only conclusion, blocker, or request for user instruction.
4. If that response is valid text, end the active run normally and let runner status become `idle`.
5. If it cannot complete under the constrained protocol, record a terminal session error and end the run.
6. Do not make any further automatic tool/provider continuation under this control state.

The event must distinguish **continuation intervention** from a tool failure. Completed earlier tool parts stay completed. No tool/session/background state may remain falsely running.

#### Existing controls and visibility

- **`doom_loop`:** unchanged; it remains the permission-governed intra-message guard. The new detector does not alter its threshold, permissions, or response path.
- **Explicit cancellation:** remains immediately valid before/during the reassessment transition and wins over automatic continuation.
- **Parent visibility:** no watchdog is required. Existing session error/event and child terminal result are sufficient visibility for this bounded policy.
- **Configuration:** not required initially. A fixed threshold avoids premature public configuration semantics. A future setting must be justified by calibration evidence.

### Action gate

| Gate question | Result |
| --- | --- |
| Supporting evidence sufficient for a production recommendation? | **No.** The detector is supported by source evidence, but tool-free reassessment protocol compatibility and usefulness are unexecuted assumptions. |
| Unresolved assumptions | Empty-tool provider behavior, nonterminal event representation, message/history invariants, and usefulness of one reassessment response. |
| Cost if wrong | A valid polling workflow is interrupted after ten repeats; a malformed reassessment could confuse session state. |
| Reversible/local? | Yes, if implemented at the prompt-loop continuation boundary with focused tests. A new user prompt/cancel recovers user control. |
| Smaller evidence-generating action? | Yes: deterministic harness tests of the detector and one no-tool reassessment turn before any broader design. |
| Exceeds frozen scope? | No. It only changes the response to the frozen exact cross-turn condition. |
| Does current architecture support the claimed behavior? | The prompt/tool boundary makes it plausible, but not yet demonstrated. |

**Action-gate result:** approve only as an **experimental implementation candidate** after focused deterministic seam validation. Do not treat it as a production fix until that evidence exists.

## T — Track / expected feedback

### Later execution must observe

1. threshold count and exact provider-turn count for queued repeated calls;
2. no automatic tool turn after the tenth matching completed call;
3. exactly one tool-free reassessment provider turn, or a visible terminal error when it cannot be completed;
4. final `SessionStatus` of `idle`;
5. completed historical tool-part state with no stale `running` part;
6. visible continuation-control event/error reference and contextual count/tool;
7. unchanged intra-message `doom_loop` behavior;
8. normal alternating-call behavior;
9. normal changed-input behavior;
10. modeled same-input/changing-output and same-input/same-output behavior, recorded without claiming semantic interpretation;
11. explicit cancellation during a child/background run and during reassessment; and
12. child/background terminal state and parent-visible result where the guard trips in a subagent.

### Feedback decision rules

- **CONTINUE:** exact cross-turn repeats trigger at the fixed boundary; no later automatic tool turn is consumed; one no-tool reassessment is protocol-valid; ordinary sequences and `doom_loop` regressions pass; final states are coherent.
- **ADJUST:** detector works but reassessment fails to produce a usable text result, event semantics misrepresent state, or a deterministic legitimate-repeat fixture exposes an avoidable false positive. Reconsider terminal error versus an explicit tool capability/exception; do not add generic semantic progress machinery.
- **REJECT:** empty-tool reassessment violates provider/history invariants, leaves stale running state, requires broad architecture changes, or costs more provider work without a bounded/observable benefit. Fall back for comparison purposes to the simpler terminal-error candidate or reject the intervention altogether.

## TARGET-Lite proportionality check

The method added useful reasoning beyond an option list:

- The calibration pass identified that the detector signal supports denying **unbounded automatic tools**, but not asserting semantic failure.
- That changed the selected transition from immediate terminal error to one bounded, tool-free reassessment opportunity.
- The evidence gate prevented this design from being represented as production-ready and identified a smaller deterministic validation action.
- The action semantics are now explicit: stop automatic tools, reason once without tools, then terminate rather than continue indefinitely.

The overhead is proportional only if later tests can validate the reassessment boundary with focused existing seams. If those tests show that one tool-free turn is not viable or does not improve closure, this added analysis is overhead and the simpler baseline policy should remain preferable. No comparison against the baseline is made in this artifact.

## Claim discipline

This treatment does not claim to solve runaway agents, improve agent safety generally, prove OpenCode unsafe, prove PR #46272 wrong, prove that identical calls imply no progress, or establish a production-correct policy. It is a reasoned local experimental policy awaiting comparison and execution.
