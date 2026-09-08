# Experiment 004 — Conventional Baseline

**Treatment:** Conventional engineering analysis from the sealed frozen brief.  
**Status:** Sealed before any later TARGET(AI) treatment.  
**Scope:** Cross-turn continuation control for repeated completed local tool calls on OpenCode `dev` revision `d6855b6b47a8433462ac6aeeba882ccf734cb7f1`.

## Objective

Recommend a continuation policy for the frozen cross-turn identical-call problem:

> Which locally testable cross-turn continuation policy can bound repeated identical completed tool calls without disrupting non-identical sequences or existing intra-message loop-control semantics?

The recommendation addresses neither semantic progress detection nor a general agent-safety architecture.

## Architecture and constraints

`SessionPrompt.runLoop()` creates an assistant message per provider turn. `SessionProcessor` persists and executes the tool calls within that message. `doom_loop` examines only recent tool parts of that current assistant message, so it is a separate intra-message control boundary.

The runtime can observe tool name, structured input, output, state, timestamps, message boundaries, session status, events, and explicit cancellation. It cannot observe semantic information gain, model intent, plan completion, or a reliable generic heartbeat. A defensible policy must therefore use a syntactic boundary and state its limitations.

PR #46272 is relevant public prior art. Its cross-turn canonical-signature counter is the narrowest design aligned with current architecture. Its threshold and abort choice are proposals, not proof.

## Alternatives considered

### A. Consecutive canonical tool-signature counter

Track a canonical `(tool name, input)` signature across completed locally executed calls from separate assistant messages for one parent user-message run. Reset on a different qualifying call. This directly covers the known blind spot and has deterministic, local tests.

**Assessment:** preferred foundation. It is narrow, observable, and preserves existing intra-message `doom_loop` behavior.

### B. Same input plus same output counter

Require both equal canonical input and equal output before counting a repeat.

**Assessment:** rejected as the primary policy. Output equality can reduce some polling false positives, but output is not a reliable progress metric: an external system can change without appearing in output, and a changing timestamp or decorative field can defeat detection while providing no useful progress. It also creates normalization, truncation, attachment, and privacy/size questions outside the frozen scope. Output equality remains valuable later as a test observation, not an admission condition.

### C. Hard step budget

Terminate after a configured number of provider turns.

**Assessment:** rejected for this bounded defect. A total turn cap bounds all work, including productive long-running tasks, but does not distinguish the repeated-action failure. Current `agent.steps` is advisory prompt injection rather than a reliable cap, so converting it into a hard policy would broaden this experiment into generic max-step enforcement.

### D. Explicit polling/retry allowance

Recognize tools or calls as polling/retry operations and permit repeated invocations.

**Assessment:** rejected from the first implementation. Current tool contracts do not expose a universal polling/retry capability or expected-state-change signal. Adding one would need tool API and configuration design, and it would create a new exception surface. A future policy may add explicit tool metadata, but this experiment must make the ordinary bounded behavior clear first.

### E. Reassess or pause rather than immediate terminal control

Ask the model to reassess after a repeat threshold, potentially without tools.

**Assessment:** desirable in principle but unsupported as a standalone current runtime state. The existing loop can prompt the model again, which risks additional provider work and another tool call. There is no first-class paused/reassessment state. A visible terminal session error before another provider turn is more deterministic and preserves resource boundedness. The error message can advise user reassessment or resumption with a new user message.

### F. Parent-visible control event/watchdog

Add an automatic parent watchdog or heartbeat.

**Assessment:** rejected from scope. Explicit parent/child cancellation and session events already exist, but background jobs do not have first-class activity telemetry. A watchdog needs a separate ownership and durable-observation design. The local cross-turn guard should publish a normal session error event and thereby remain observable to a parent/client without inventing watchdog machinery.

### G. Combined policy

Combine signature count, output comparison, step budget, polling exceptions, and parent watchdog.

**Assessment:** rejected. It would obscure the causal policy under test, make false-positive behavior difficult to reason about, and violate the frozen narrow scope.

## Recommended policy

Implement a **hard, run-scoped, consecutive canonical tool-signature circuit breaker** for completed local tool calls crossing assistant-message boundaries.

### State tracked

For the active parent user-message run, retain:

- last qualifying signature: tool name plus recursively canonicalized input;
- count of consecutive qualifying completed calls with that signature; and
- the current parent user-message ID used as the scope key.

A qualifying call is a completed locally executed tool part. Provider-executed tool parts and cleanup-marked interrupted/orphaned parts are excluded, consistent with existing loop behavior. The policy does not compare output.

### State scope

State is scoped to one session, one active parent user message, and its provider-turn loop. It must not cross a subsequent user message, a new session, or unrelated child/parent session runs. It is evaluated after a completed tool result is available and before the next provider turn is requested.

### Equality rule

Two calls are equal only when:

1. their tool names are byte-for-byte equal; and
2. their inputs have equal canonical structural serialization.

Canonicalization must recursively sort object keys, preserve array order, distinguish `undefined` from absent/null as required by the existing part representation, and ignore no semantic fields beyond representation normalization. It must not attempt equivalence of shell commands, paths, regexes, or semantically equivalent but syntactically distinct requests.

### Threshold

**10 consecutive qualifying calls.**

This number is a **heuristic inherited from public PR #46272**, not calibrated by incident data. It is high enough to avoid replacing the existing three-call intra-message permission control and low enough to cap the documented hundreds-of-turn class. It must be named as a practical default rather than empirically optimal.

### Reset conditions

Reset the counter when:

- the active parent user-message ID changes;
- a qualifying completed local call has a different canonical signature; or
- the run reaches an ordinary terminal state.

A new user prompt starts a new run and therefore a new counter. Alternating calls never reach the threshold because each different signature resets the consecutive count.

A non-tool text/reasoning assistant turn does not itself establish a new tool signature. The implementation should retain the count through such a turn only while it remains the same active parent user-message run; otherwise a model could evade the exact cross-turn detector by emitting inert text between identical calls. This is intentionally a syntactic anti-evasion choice, not semantic progress analysis.

### Transition at threshold

Before requesting another provider turn after the tenth matching completed call:

1. publish a visible `Session.Event.Error` with a stable machine-readable reference such as `repeated-identical-tool-call`;
2. record an error that identifies the tool, count, and cross-turn reason;
3. terminate the current run loop normally, allowing the runner to set session status to `idle`; and
4. preserve each already completed tool part as `completed` rather than rewriting it as interrupted.

This is a **terminal session error / controlled stop**, not a provider abort, pause, or automatic parent escalation. The user or parent can inspect the event and explicitly continue with a new prompt or cancel as usual.

### Interaction with existing safeguards

- **`doom_loop`:** unchanged. It still controls three identical calls inside one assistant message through its configured permission (`ask` by default, optionally `deny`). The new guard only observes cross-message completed local calls and is not routed through `doom_loop` permission resolution.
- **Cancellation:** unchanged. Explicit cancellation can interrupt before the threshold and retains its current cleanup/error behavior. The threshold transition is not a substitute for cancellation.
- **Provider retries:** unchanged and separate. Transport/API retry count is not a tool-call continuation counter.
- **`agent.steps`:** unchanged. This policy must not retrofit it into a general step-cap feature.
- **Background jobs:** the child run ends normally with a terminal error result; parent/client visibility occurs through existing session error/result paths rather than a new watchdog.
- **Polling:** no automatic exception. A caller that needs more than nine identical ordinary tool calls must intervene with a new user message or use a future explicit polling contract.

### Configuration

Do **not** add configuration in the first bounded implementation. A fixed, documented heuristic makes the control behavior deterministic and testable. A public configuration surface would require decisions about defaults, per-agent overrides, disabling, interactions with `doom_loop`, and responsibility for polling—all unsupported by frozen evidence.

## Why this policy is preferred

It is the smallest runtime control that directly covers the confirmed message-boundary gap. It makes one observable, local decision before additional provider cost, without claiming to infer model intent or semantic progress. It preserves the existing permission-based intra-message safeguard and avoids expanding the experiment into global budgets, tool taxonomy, or parent-watchdog architecture.

## False-positive analysis

The strongest false positive is a legitimate long-running poll: for example, a deployment-status tool called ten times with unchanged input while the remote system is expected to become ready. The chosen policy stops that sequence even if each call is reasonable.

Other false positives:

- a transient failure requiring repeated same-argument retries;
- repeated reads of state that changes outside the returned payload;
- intentionally repeated idempotent tool calls; and
- workflows where a model legitimately rechecks an invariant more than nine times.

The policy limits this harm by requiring ten consecutive completed exact signatures, restricting scope to one user-message run, and making the transition visible. It does not claim to eliminate the harm. Explicit polling metadata would be the appropriate future solution if evidence establishes a real tool contract.

## False-negative analysis

The strongest false negative is an unbounded alternating loop: two tool calls can alternate forever, or the model can vary a meaningless argument, timestamp, path spelling, or command formatting on every turn. The counter also misses semantically equivalent but syntactically different inputs, same-input calls separated by a different qualifying call, and any sequence that remains below ten repeats.

Same input with changing output is also not stopped if the output changes but the call still reaches ten repeats, because output is deliberately not in the equality rule. Conversely, different input with no information gain is outside scope. Solving those cases would require a semantic or tool-specific progress contract that current architecture does not expose.

## Deterministic test plan

Use the existing `packages/opencode/test/session/prompt.test.ts` integration seam:

- `TestLLMServer` queues deterministic provider turns using `llm.tool(name, input)` and `llm.text(...)`.
- Existing local tool registry/test instance supplies deterministic tool execution.
- `llm.wait(n)` observes the number of provider turns consumed.
- `MessageV2.filterCompactedEffect(sessionID)` observes message and tool-part histories.
- `SessionStatus.Service.get(sessionID)` observes `busy`/`idle`.
- `EventV2Bridge.Service` subscription can capture `Session.Event.Error`.
- Existing cancellation tests demonstrate `prompt.cancel(sessionID)` and child-task cleanup.

Required cases:

1. **Cross-turn identical calls:** queue one identical completed tool call per separate provider response. Verify no unbounded continuation.
2. **Threshold minus one:** queue nine matching calls and then a text response. Verify all nine run and ordinary completion remains possible.
3. **Threshold reached:** queue ten matching calls followed by a text response. Verify the control transition occurs before the next provider response is consumed, emits the stable error reference, and reaches `idle`.
4. **Alternating inputs:** queue more than ten calls alternating canonical inputs. Verify normal completion and no control error.
5. **Same tool, changing inputs:** queue changing inputs for one tool. Verify normal completion and no control error.
6. **Existing intra-message `doom_loop`:** queue three identical calls in a single assistant response under a controlled permission rule. Verify its existing permission behavior is unchanged and the cross-turn counter is not used as a replacement.
7. **Explicit cancellation:** start a hanging or queued child/subagent sequence, cancel explicitly, and verify existing cancellation outcome remains valid.
8. **Final state integrity:** following a threshold transition, verify prior tool parts are completed, no relevant part is left `running`, the session becomes `idle`, and a background child reports a terminal error rather than stale `running` when the guard trips there.

The initial implementation should additionally test canonical object-key ordering if the signature serializer accepts object input. That behavior is needed for the stated structural equality rule and must not rely on incidental JSON insertion order.

## Evidence required before acceptance

Policy plausibility is insufficient. Accept the policy only after evidence shows:

1. **Unit behavior:** canonical signature equality and reset logic work for object-key order, arrays, primitive/null/undefined cases represented by tool parts, and different tool names.
2. **Integration behavior:** the deterministic cross-turn test reaches the threshold and prevents consumption of the queued next provider turn.
3. **State integrity:** emitted error, completed tool parts, terminal background result where applicable, and final `SessionStatus` agree; no stale `running` state remains.
4. **Regression protection:** existing `doom_loop` permission behavior, alternating calls, changed-input calls, cancellation, and ordinary terminal text completion remain valid.
5. **Compatibility:** focused existing prompt/session tests pass in the supported repository test environment.

No correctness claim is made before these executions complete.

## Intentional trade-off

This policy intentionally sacrifices some legitimate long polling and repeated idempotent work within one user-message run in exchange for a deterministic bound on exact repeated cross-turn continuation. It chooses simple, visible, local control over configurability, semantic sophistication, automatic recovery, and broad loop coverage.
