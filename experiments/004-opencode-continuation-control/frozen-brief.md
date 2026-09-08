# Experiment 004 — Frozen Brief

**Working title:** Cross-turn continuation control for repeated completed tool calls  
**Frozen:** 2026-09-08  
**Scope:** Starting evidence before either conventional baseline or later TARGET(AI) treatment. This file is sealed after creation. Do not revise it except for an explicitly documented mechanical repository requirement.

## Experiment question

> Which locally testable cross-turn continuation policy can bound repeated identical completed tool calls without disrupting non-identical sequences or existing intra-message loop-control semantics?

This experiment is not generic runaway-agent prevention, semantic progress detection, parent-watchdog architecture, autonomous-agent safety, provider/model quality, global token-budget design, or generic max-step enforcement.

## Frozen source and current state

| Item | Value |
| --- | --- |
| Issue | [anomalyco/opencode#45442](https://github.com/anomalyco/opencode/issues/45442) |
| Repository | [anomalyco/opencode](https://github.com/anomalyco/opencode) |
| Branch | `dev` |
| Frozen revision | `d6855b6b47a8433462ac6aeeba882ccf734cb7f1` |
| Revision subject | `chore: generate` |
| Revision timestamp | `2026-09-08T06:51:49+00:00` |
| Linked public proposal | [PR #46272](https://github.com/anomalyco/opencode/pull/46272), open and unmerged at Collect time |

### Confirmed source behavior

The following was traced on the frozen revision:

- `packages/opencode/src/session/prompt.ts`, `SessionPrompt.runLoop()`, creates a new assistant message for each provider turn before it calls `SessionProcessor.process()`.
- `packages/opencode/src/session/processor.ts` processes streamed tool calls within that assistant message. Its `DOOM_LOOP_THRESHOLD` is `3`; the check reads `MessageV2.parts(ctx.assistantMessage.id)` and considers only the three most-recent parts of that message.
- `doom_loop` is therefore intra-message repetition control. It does not aggregate same-tool/same-input calls across separately created assistant messages.
- The normal loop remains active while processor results are `continue`; session status is set to `busy` on loop/processor execution. A cross-turn sequence can therefore remain active while provider turns continue.
- The persisted/evented runtime representation exposes tool name, input, output, state, start/end timestamps, assistant-message boundaries, session events, and explicit abort.
- `SessionStatus` exposes `busy`, `retry`, and `idle`; it has no no-progress or heartbeat state.
- `BackgroundJob.Info` exposes `running` or terminal state, start/completion timestamps, output/error, and metadata. It has no first-class heartbeat or progress metric.
- Explicit cancellation exists. The session abort HTTP route calls `SessionPrompt.cancel()`. `SessionRunState.cancel()` cancels matching child background jobs and session runners.
- Provider-error retries are bounded by `RETRY_MAX_RETRIES = 5` in `session/retry.ts`.
- `Agent.Info.steps` is configurable. In `runLoop()`, `agent.steps ?? Infinity` only controls whether `MAX_STEPS_PROMPT` is appended to model messages; it does not disable tools or terminate the loop. The default `general` agent has no configured `steps`, so its effective value is unbounded.
- Compaction/overflow handling and child-session nesting depth controls exist.

### Reporter observations — not established reproduction

Issue #45442 reports a background `general` subagent that made 364 identical `grep` calls over approximately 50 minutes at approximately five-second cadence. The reporter attributes approximately 184k input tokens, approximately 40k output tokens, and approximately 142M cache-read tokens to the incident. The task reportedly remained `running` until manual interruption.

Reported environment: a private OpenAI-compatible DeepSeek variant, beta desktop, reported CLI version 1.18.18, macOS arm64, and no plugins.

The exact reporter incident is **not** the experimental reproduction target. The experiment tests the narrower runtime control boundary observable on this frozen revision.

## Existing safeguards and exact gap

Known safeguards at freeze:

1. **`doom_loop`:** three same tool calls with identical input within the current assistant message invoke the `doom_loop` permission. The documented default is `ask`; configuring `deny` blocks that call class.
2. **Explicit abort/cancellation:** users and API clients can abort sessions; parent cancellation propagates to matching child background jobs.
3. **Bounded provider-error retry:** retry policy has a maximum of five retries.
4. **Configurable `agent.steps`:** advisory maximum-step prompt injection, not a hard execution cap on this path.
5. **Compaction/overflow handling.**
6. **Child-session nesting controls:** `subagent_depth` bounds nesting.

OpenCode must not be described as having no loop protection. The frozen gap is specifically **cross-turn continuation state**: identical completed local calls can cross assistant-message boundaries without the intra-message detector accumulating their history.

## Public prior art available to both treatments

PR #46272 is public evidence available to both baseline and later TARGET(AI) treatment. It proposes:

- inspecting tool calls across assistant turns belonging to the current user request;
- canonicalizing tool input;
- counting consecutive identical tool-name/input signatures;
- a fixed threshold of 10;
- stopping before another provider turn;
- emitting a session error; and
- focused tests for 10 identical calls, 9 permitted calls, and alternating arguments.

Its limitations and unresolved questions are also frozen:

- 10 is not calibrated by published evidence;
- it overlaps with `doom_loop`, although its cross-turn scope differs;
- legitimate polling may repeat identical calls;
- immediate abort versus reassessment remains unresolved;
- configuration semantics remain unresolved;
- parent visibility/control remains unresolved;
- equality of outputs is not part of its core criterion; and
- it is open and unmerged: evidence, not authoritative design.

No later treatment may receive non-frozen evidence unavailable to the baseline.

## Observable signals and semantic constraint

### Available signals

- tool name;
- tool input;
- tool output;
- tool state;
- tool start/end timestamps;
- assistant-message boundaries;
- session `busy` / `retry` / `idle`;
- background-job `running` / terminal state;
- parent-child session relation;
- session/part events; and
- explicit abort.

### Not first-class observable

- semantic information gain;
- plan advancement;
- completion probability;
- model intent;
- reason for retry;
- generic semantic progress; and
- a durable heartbeat/progress signal.

**Frozen constraint:** “same input + same output” may be used as syntactic evidence in a treatment, but must not be assumed to be a universal definition of no progress.

## Legitimate repeat counterexamples

Repeated action is not automatically pathological. Counterexamples frozen for both treatments:

- polling a build, deployment, queue, lock, or remote operation;
- retrying after a transient failure;
- sampling mutable status;
- repeating an action while external state may change; and
- an identical invocation where relevant state changes outside returned output.

## Frozen observable success criteria

A later implementation is acceptable only if evidence establishes all applicable criteria:

A. **Cross-turn liveness:** a deterministic same-tool/canonical-same-input sequence across separate assistant turns cannot consume provider turns indefinitely.

B. **Scope correctness:** continuation state spans assistant-message boundaries while remaining scoped to the appropriate parent user-message/run.

C. **Existing safeguard preservation:** current intra-message `doom_loop` semantics remain unchanged.

D. **Non-repeat preservation:** alternating/non-identical tool inputs continue normally.

E. **State integrity:** a control transition does not leave tool, session, or background state falsely `running`.

F. **Visibility:** the decision is observable through an appropriate current error, status, event, or equivalent mechanism.

G. **Cancellation compatibility:** existing explicit cancellation remains valid.

H. **Semantic humility:** no claim is made to solve generic semantic no-progress detection.

## Experimental fairness

- Baseline runs first and must be competent.
- Baseline may use every frozen public item, including PR #46272.
- Baseline must not be weakened to make a later treatment look better.
- After baseline is sealed, TARGET(AI) starts fresh from exactly this frozen brief and the same public evidence.
- Baseline is not edited after TARGET treatment begins.
- A difference between treatments is not automatically improvement; identical conclusions are valid.
- Later TARGET overhead counts against it.

## Claim boundary

The strongest possible future result is local to this frozen OpenCode revision and bounded continuation-control policy. The experiment must not claim that TARGET(AI) prevents runaway agents, solves autonomous-agent loops, proves OpenCode unsafe, proves PR #46272 incorrect, or proves that identical calls imply no progress.
