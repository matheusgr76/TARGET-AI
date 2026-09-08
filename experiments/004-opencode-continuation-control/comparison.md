# Experiment 004 — Pre-Execution Comparison

**Scope:** Comparison of the sealed conventional baseline and sealed TARGET(AI) treatment before implementation or behavioral execution.  
**Frozen OpenCode revision:** `d6855b6b47a8433462ac6aeeba882ccf734cb7f1`.  
**Admissible information:** only `frozen-brief.md`, `baseline.md`, and `target-ai.md`.

## Integrity and evidence boundary

| Artifact | Verified SHA-256 |
| --- | --- |
| `frozen-brief.md` | `d6000212cef18f121f9b45fd36737d57f0c083d6c006f16f2ae3f5db2aeb8356` |
| `baseline.md` | `4dac8956fc5b839254c55ab0278844224c8f0ed44b8db3ca2ed91f64f11f5e88` |
| `target-ai.md` | `838d30c47e5ea5d87af58ca0619a666c1dfe2c3ad7954db54018054c2f16ca31` |

No later repository revision, GitHub activity, maintainer comment, provider behavior, implementation result, or behavioral test result is used here.

## Policies stated fairly

### Baseline

The baseline recommends a hard, run-scoped consecutive canonical signature circuit breaker for completed locally executed tool calls. It tracks canonical `(tool name, input)` signatures over assistant-message boundaries within one parent user-message run. At **10** matching consecutive calls—an uncalibrated heuristic inherited from PR #46272—it publishes a stable session error and terminates the current loop before another provider turn. Existing intra-message `doom_loop` permission behavior remains unchanged. Output equality is not an admission criterion.

Source: sealed baseline, “Recommended policy,” “Threshold,” “Transition at threshold,” and “Interaction with existing safeguards.”

### TARGET

The TARGET treatment retains the same basic run-scoped, canonical `(tool name, input)` detector and the same heuristic threshold of **10**. It treats that threshold as sufficient to withdraw permission for further automatic tool execution, but insufficient by itself to declare semantic task failure. At threshold it emits visible continuation-control information, allows exactly one tool-free reassessment provider turn, and then requires normal text closure or a terminal error. No further automatic tool continuation is allowed. Existing intra-message `doom_loop` remains unchanged. Output equality is not an admission criterion.

Source: sealed TARGET treatment, “Reason Calibration,” “Selected experimental policy,” and “Transition at threshold.”

## Actual difference

The policies substantially agree on the problem boundary, exact canonical-signature detector, per-run scope, threshold 10, heuristic status of that threshold, preservation of `doom_loop`, and the need to bound automatic continuation.

The central difference is what the threshold **means**:

```text
Baseline
10 repeats → sufficient basis for terminal stop/error.

TARGET
10 repeats → sufficient basis to withdraw further automatic tool execution
           → insufficient basis alone to declare task failure
           → exactly one bounded tool-free reassessment
           → normal closure or terminal error.
```

This is not a different repetition detector. It is a different continuation/stopping transition after the same detector fires.

## Reasoning comparison

| Dimension | Baseline | TARGET | Pre-execution assessment |
| --- | --- | --- | --- |
| A. Problem framing | Exact cross-turn repeated completed calls are a narrow liveness defect. | Same framing; explicitly asks whether continued execution remains justified. | Aligned. TARGET makes the action-versus-task-failure distinction explicit. |
| B. Assumptions identified | Assumes a fixed threshold can act as a hard circuit breaker; calls 10 heuristic. | Identifies the decision-changing assumption: whether 10 repeats proves failure versus only justifies withdrawing tools. | TARGET refines one material assumption. |
| C. Legitimate repeated work | Acknowledges polling/retry false positives; accepts interruption and advises new user prompt/future contract. | Same limitation; adds one no-tool chance to explain wait state/request input. | TARGET changes response severity, not polling support. |
| D. Repetition vs semantic no-progress | Refuses output equality as generic progress and scopes policy syntactically. | Makes the inference boundary central: repetition is not semantic failure evidence. | TARGET is clearer; both remain semantically humble. |
| E. Evidence sufficiency | 10 matching calls is enough to stop automatic execution and declare terminal session error. | 10 matching calls is enough only to stop automatic tools; reassessment viability needs execution evidence. | Materially different evidence threshold for declaring failure. |
| F. Continuation semantics | No further provider turn. | Exactly one provider turn, tools unavailable; no further automatic tools afterward. | Material behavioral difference. |
| G. Stopping semantics | Terminal controlled stop/error immediately. | Stop automatic tool continuation first; then normal closure or terminal error. | TARGET separates tool stopping from task failure. |
| H. False-positive awareness | Strong explicit polling false positive and deliberate sacrifice. | Same examples drive calibration and revised transition. | TARGET responds to the same risk with extra behavior; superiority unproven. |
| I. False-negative awareness | Alternation, varied arguments, semantic equivalence, and <10 calls escape. | Same shared blind spots. | No treatment-specific advantage pre-execution. |
| J. Observable architecture | Uses durable tool parts, run loop, event, status, cancellation. | Requires same plus an unproven tool-free prompt transition and nonterminal visibility semantics. | Baseline has stronger established architecture fit. |
| K. Implementation complexity | One counter and terminal transition. | Counter, `reassessmentIssued`, temporary tool suppression, constrained provider turn, closure/error path. | TARGET is materially more complex. |
| L. Testability | Deterministic fixture can prove threshold blocks next provider turn. | Requires all baseline tests plus exact-one no-tool-turn and protocol/state tests. | Both testable at proposed seam; TARGET has more failure modes. |
| M. Resource cost | No extra provider turn after threshold. | One additional provider turn, plus potential existing provider retry behavior. | TARGET has known additional cost. |
| N. Reversibility | Local error transition; new user input can resume work. | Local bounded transition; new user input/cancel can recover. | Both local/reversible; TARGET has more state to unwind. |
| O. Process overhead | Conventional analysis selected the minimal guard. | Second pass and evidence gate changed the post-threshold policy. | Added reasoning is justified only if execution validates useful reassessment. |

Citations are to the sealed artifacts named in the policy statements and to `target-ai.md` “Reason Calibration,” “Action gate,” and “TARGET-Lite proportionality check.”

## What TARGET actually changed

| Item | Classification | Evidence from sealed artifacts |
| --- | --- | --- |
| Detector | **UNCHANGED** | Both use cross-turn consecutive canonical `(tool name, input)` signatures for completed local calls. |
| State scope | **UNCHANGED** | Both scope state to a session and active parent user-message run. |
| Threshold | **UNCHANGED** | Both use 10, explicitly heuristic and inherited from PR #46272. |
| Equality rule | **UNCHANGED** | Both use byte-equal tool name plus canonical structural input; neither uses semantic equivalence. |
| Interpretation of threshold | **MATERIALLY CHANGED** | Baseline treats it as sufficient terminal-error evidence; TARGET treats it as sufficient only to stop automatic tools. |
| Transition after threshold | **MATERIALLY CHANGED** | Baseline stops before another provider turn; TARGET permits exactly one tool-free reassessment turn. |
| Evidence standard | **REFINED** | TARGET requires protocol-valid reassessment and coherent closure before accepting the richer transition. |
| Expected test evidence | **MATERIALLY CHANGED** | TARGET adds exact-one reassessment turn, no tools during it, and useful/invalid closure outcomes. |
| False-positive/false-negative trade-off | **REFINED** | Shared detector blind spots remain; TARGET reduces immediate terminality but adds a failure surface. |
| Implementation complexity | **MATERIALLY CHANGED** | TARGET adds reassessment state, temporary tool suppression, and state/transition tests. |

## Reason Calibration contribution

**Classification: C — material behavioral policy change.**

It is more than semantic reframing because the selected TARGET policy consumes one additional provider turn, requires temporary removal of tools, introduces `reassessmentIssued` state, creates a distinct closure/error transition, and requires new protocol/state tests. It is not merely conceptual clarification with no runtime consequence.

The calibration challenge was the sealed treatment’s legitimate-polling case: external state can still change after ten identical calls, so exact repetition is a liveness signal but not proof that the task has failed. The revised policy changes the system from “terminal error now” to “no more automatic tools, one bounded explanation/closure attempt, then terminal state.”

This classification does not decide whether TARGET is better. The extra behavior could prove useful, redundant, incompatible, or harmful.

## Pre-execution trade-off

### Baseline advantages

- Simpler counter and state machine.
- Deterministic terminal result at threshold.
- No additional provider turn after the intervention boundary.
- Lower protocol and cleanup complexity.
- Stronger fit with already observed event/error and run-loop behavior.

### Baseline risks

- A heuristic exact-repeat threshold is treated as sufficient evidence of terminal task failure.
- Legitimate polling/retry/idempotent rechecks become a terminal error, not merely bounded automatic action.
- Any useful explanation, blocker summary, or intervention request must come from the user/client after termination.

### TARGET advantages

- Separates “stop automatic action” from “declare task failure.”
- Supplies one bounded opportunity to summarize unresolved state, explain the bound, request intervention, or close normally.
- Keeps resource liveness bounded: it never restores automatic tools and cannot create an unbounded reassessment loop.

### TARGET risks

- Exactly one extra provider turn and associated provider cost.
- Additional `reassessmentIssued` state and a more complex transition graph.
- Tool-free provider turn may be incompatible with message/protocol invariants.
- The model may generate useless prose, fabricate a conclusion, or fail to close coherently.
- Session/tool/background cleanup and event semantics may become harder to keep coherent.
- It still does not support generic polling semantics; it only may fail more gracefully.

## Pre-registered discriminating evidence

The core execution question is:

> Does one bounded tool-free reassessment after the repetition threshold provide useful and coherent behavior that justifies its additional complexity and provider turn?

The following evidence distinguishes the policies:

1. Both detect the same deterministic cross-turn threshold from the same queued fixture.
2. Both prevent an eleventh automatic identical tool call.
3. Baseline reaches its intended terminal error/idle state coherently, with prior calls completed.
4. TARGET permits exactly one reassessment provider turn after threshold.
5. TARGET exposes no tool to that turn and cannot regain automatic tool execution.
6. TARGET’s reassessment produces a protocol-valid outcome, not malformed message/tool history.
7. TARGET reaches coherent `idle` or terminal state afterward.
8. Neither leaves a stale running tool part, session runner, or background job.
9. Event/error/status visibility identifies the correct control state and is not contradictory.
10. Existing intra-message `doom_loop` semantics remain unchanged.
11. Alternating and changing-input sequences remain unaffected.
12. Explicit cancellation remains valid before/during the relevant transitions.

### Pre-registered useful reassessment definition

Text alone is not success. A reassessment is useful only when it does at least one meaningful thing unavailable under the baseline’s immediate termination:

- explains that further automatic execution was bounded;
- summarizes the unresolved state using existing context;
- identifies why progress cannot continue safely;
- requests concrete user intervention or information;
- closes normally and coherently rather than only forcing an error; or
- exposes actionable information otherwise lost by immediate stop.

It must not call a tool, silently resume the loop, fabricate success, merely repeat prior reasoning, leave the session busy, or require multiple additional provider turns.

A message equivalent only to “I appear to be stuck,” followed by an error and no actionable state, has **weak or zero** incremental value.

## Pre-registered outcome classification

### A — Material TARGET improvement

Require all of the following:

- TARGET changes runtime behavior rather than terminology;
- one tool-free reassessment is protocol-valid and state-clean;
- it produces meaningful closure, recovery, or actionable information unavailable under baseline;
- all frozen liveness, regression, visibility, and integrity conditions hold; and
- the benefit reasonably justifies the extra provider turn, state, tests, and complexity.

### B — Modest TARGET improvement

Use when reassessment is valid and adds some useful closure/information, but its practical advantage over terminal baseline behavior is limited, uncertain, or narrowly situational.

### C — Tie / no material difference

Use when both policies bound the frozen continuation condition, while reassessment adds little meaningful information or the difference is primarily conceptual in the observed fixture.

### D — Baseline preferred

Use when baseline cleanly bounds continuation and TARGET’s extra turn/complexity supplies no useful benefit, is redundant, confusing, or operationally inferior.

### E — TARGET policy invalid

Use when tool-free reassessment cannot be implemented coherently in this frozen architecture, violates protocol/state assumptions, permits another tool continuation, leaves inconsistent state, or fails frozen success criteria.

These definitions are sealed before execution and must not be revised after execution begins.

## Polling and false-negative interpretation

### Polling

Neither policy solves generic polling semantics. At threshold the baseline terminates; TARGET interrupts automatic polling and offers one tool-free reassessment. Execution must not claim TARGET “supports polling.” The bounded question is whether TARGET fails more gracefully when an exact-repeat detector encounters legitimate repetition.

### Shared false negatives

Both policies intentionally miss alternating calls, changing arguments, and syntactically different but semantically equivalent inputs. These shared limits must not be attributed to one treatment more than the other unless later execution demonstrates a treatment-specific interaction.

## Cost accounting

TARGET’s costs must count in the verdict:

- one additional provider turn;
- `reassessmentIssued` state;
- temporary tool suppression;
- an additional transition and closure/error path;
- more tests;
- protocol complexity; and
- possible user confusion.

Richer behavior does not establish a win. The additional behavior must create pre-registered useful reassessment and preserve state/protocol integrity.

## Provisional pre-execution verdict

**C — Tie / no material difference, LOW confidence.**

Both policies credibly address the frozen exact cross-turn liveness boundary on paper. TARGET makes a real behavioral change and has a defensible rationale, but no execution evidence establishes that a tool-free reassessment is protocol-valid or usefully informative. Its added cost and complexity are certain; its benefit is only plausible.

Evidence most likely to overturn this verdict:

- **toward A/B:** a deterministic reassessment produces a concise, actionable blocker/summary or coherent normal closure that immediate baseline termination cannot provide, with no state/protocol regression;
- **toward D:** reassessment is valid but reliably redundant or unhelpful relative to baseline’s error;
- **toward E:** tool suppression/reassessment violates history/provider invariants, permits another tool call, or leaves stale running state.

## Later execution plan — do not run in this phase

Use the existing `packages/opencode/test/session/prompt.test.ts` seam with `TestLLMServer`, queued `llm.tool()` responses, `llm.wait(n)`, `MessageV2`, `SessionStatus`, and session-event subscriptions. Run both policies against identical deterministic fixtures.

| Fixture | Expected observation |
| --- | --- |
| Control 1 — normal completion | Ordinary tool/text sequence completes under both policies. |
| Control 2 — alternating tool inputs | No threshold control transition. |
| Control 3 — changing tool inputs | No threshold control transition. |
| Boundary 1 — 9 identical cross-turn calls | No threshold transition; queued normal completion remains possible. |
| Boundary 2 — 10 identical cross-turn calls | Both detect the same boundary; baseline errors/stops, TARGET enters one reassessment. |
| Boundary 3 — queued 11th identical call | Neither policy executes the eleventh automatic identical tool call. |
| TARGET-specific — exact one tool-free response | TARGET consumes one constrained provider response only. |
| TARGET-specific — attempted tool request in reassessment | No tool executes; outcome becomes defined closure/error, never resumed loop. |
| TARGET-specific — useful normal closure | Assert actionable summary/request/normal closure under a deterministic response. |
| TARGET-specific — unhelpful/non-closing response | Assert clean terminal error, no extra turn, no stale state. |
| State | No stale running tool/session/background state; event/error/status agree. |
| Regression | Existing intra-message `doom_loop` semantics unchanged. |
| Cancellation | Explicit cancellation remains coherent through normal and reassessment paths. |

A smaller disposable harness may be useful only if it can exercise the actual `SessionPrompt`/`SessionProcessor` tool-boundary behavior more cleanly than the existing prompt test fixture. A pure counter-only harness cannot distinguish the policy transitions and is insufficient for the A/B question.

## Non-execution confirmation

No policy was implemented. No OpenCode production source was modified. No behavioral test, execution artifact, retrospective, commit, push, issue/PR action, or maintainer contact occurred in this phase.
