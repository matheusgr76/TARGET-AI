# TARGET(AI) Treatment — Experiment 003

> **SEALED TARGET(AI) TREATMENT**
>
> Created from the frozen starting state before comparison. Do not revise after comparison begins; record later discoveries in a subsequent artifact.

## Method application

This treatment applied the TARGET cycle proportionately to a bounded parser/action-boundary problem:

- **Target:** define a safe state transition from malformed assistant text to a structured tool-call candidate.
- **Assess:** separate current source behavior and observed parser outputs from interpretations of intent.
- **Reason:** identify which evidence is sufficient to permit promotion and make predictions that can fail.
- **Generate:** consider strict normalization, permissive normalization, direct parsing, and rejection.
- **Execute:** use read-only source inspection and disposable local parser experiments; make no upstream source/test changes and invoke no provider.
- **Track:** record observed outcomes, revise the initial rule through an adversarial second Reason pass, and define evidence gates before proposing any implementation.

## Target

**Outcome:** recover the frozen raw wrapper into one structured SDK tool call only when the text is unambiguously a complete instance of the known non-native call grammar.

**Evidence:** recovery must preserve tool name and arguments; nearby non-action forms must not create a structured call; the resulting object must cross the existing safe dispatch path exactly once; malformed or ambiguous text must not become dispatch-eligible.

**Constraint:** false-positive action promotion is more harmful than a false negative. Preserve the one-call-per-message contract and the current canonical parsing/validation authority. Exclude the provider-owned GLM raw-channel-token case.

**Horizon:** decide the action boundary and required validation now. Implementation and runtime execution are out of scope for this treatment.

## Current state

At frozen revision `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1`, the converter recognizes canonical `<function=NAME>...</function>` syntax. `_preprocess_model_output()` removes a `<tool_call>` wrapper only when it directly surrounds an already-canonical opener. The frozen raw-name wrapper has no canonical opener, so `_find_function_match()` returns no match and the message remains content.

A successful converter match produces `message.tool_calls`. `classify_response()` gives any nonempty `tool_calls` priority over content, and dispatch then creates action events and may execute them. The conversion decision is therefore an action-promotion decision, even though it is not itself tool execution.

The current converter resolves names against the supplied tools with a limited alias map and raises `FunctionCallValidationError` for an unknown name. Parameter validation enforces allowed names and required fields, but repeated parameter names currently overwrite earlier values in a dictionary. That behavior predates this candidate; a normalizer must not silently make it broader or conceal it.

## Evidence

| Observation | Provenance | Treatment use |
| --- | --- | --- |
| Exact frozen wrapper remains text and yields no structured call. | Frozen local reproduction on current main | Establishes the recoverable false negative. |
| Current parser accepts canonical function grammar and existing preprocessing removes only canonical wrappers. | Current `fn_call_converter.py` | Locates the representation gap and shows where not to duplicate parsing. |
| Structured calls have priority over text in response classification and flow into action-event handling. | Current `response_dispatch.py` and `agent.py` | Establishes asymmetric promotion risk. |
| Public maintainer analysis separates the provider-owned GLM failure from the SDK-resolvable raw-wrapper case. | [Issue #4540](https://github.com/OpenHands/software-agent-sdk/issues/4540) | Keeps target scope bounded. |
| Public PR #4608 normalizes a bare name only when followed by a parameter tag and no canonical opener exists. | [PR #4608](https://github.com/OpenHands/software-agent-sdk/pull/4608) | Starting candidate, not accepted conclusion. |
| Public PR snapshot recovered the exact wrapper and preserved literal close-tag text inside an argument. | Disposable local screening run | Supports recovery feasibility, not safety sufficiency. |

## Unknowns and assumptions

### Unknowns

- Whether real non-native outputs reliably contain surrounding explanatory text, fenced examples, multiple wrappers, or truncation.
- Whether a future focused dispatch test can use existing project fixtures without a live provider or a real tool.
- Whether the current one-call semantics define behavior for multiple raw wrappers beyond the existing canonical-path constraints.
- Whether a raw wrapper located inside a code fence is ever intended to request action rather than illustrate syntax.

### Assumptions

1. Assistant-content text is untrusted with respect to action intent. The same text can be an instruction, a log, a quoted example, or a model-emitted action.
2. Text alone cannot supply semantic intent beyond its structure and its position in the expected response grammar.
3. The frozen exact wrapper is a known recovery grammar, not a license to recognize arbitrary XML-like content.
4. Existing tool lookup, argument validation, security analysis, confirmation, and dispatch remain required after any syntactic recovery.
5. A false negative is recoverable by another turn or fallback behavior; a false positive may initiate an unintended action. They are not symmetric errors.

## Initial Reason pass

### Candidate interpretations

1. **Dialect mismatch:** the raw wrapper is a known non-native spelling of the canonical function call and may be normalized before existing parsing.
2. **Ordinary text:** the same sequence might be documentation, Markdown, a log, a quoted message, or a code example; it must remain content.
3. **Incomplete/ambiguous action:** the sequence resembles an action but lacks enough boundary evidence; it must remain non-executable or fail explicitly.
4. **Provider protocol failure:** raw channel tokens are transport/provider data that the SDK cannot safely infer; excluded from this experiment.

### Generated options

| Option | Decision | Reason |
| --- | --- | --- |
| Treat every `<tool_call>` tag as an action | Reject | Tag presence is weak evidence and creates a broad text-to-action injection surface. |
| Expand the canonical parser to accept both forms | Reject | Mixes recovery grammar with the authoritative canonical grammar and obscures the action boundary. |
| Add a direct raw-wrapper-to-`tool_calls` parser | Reject | Duplicates existing name resolution, validation, ID construction, and content handling. |
| Normalize any bare-name wrapper plus parameter tag | Initially plausible; later rejected | It recovers the issue fixture, but the second Reason pass demonstrated unsafe matches. |
| Normalize only a complete, sole raw-wrapper message | Preferred | Makes the raw grammar itself the evidence for promotion and leaves ambiguous contexts as content. |
| Reject all malformed wrappers | Reject | The exact, provider-independent grammar is reproducible and can be safely recovered under a stricter boundary. |

### Initial proposed boundary

The initial reading favored the public PR’s constrained opener rule: a valid bare name followed by a parameter tag, no canonical opener, and a terminal outer closer. It preserved existing parsing and was narrower than general markup handling.

That rule was treated as a hypothesis, not completion. Prediction: it should recover the frozen form while declining text that is merely similar.

## Reason Calibration — adversarial second pass

A second Reason pass challenged whether a bare name plus parameter tag is enough evidence of action intent.

### Adversarial experiment

The public PR #4608 snapshot was run in a disposable local environment against forms beyond its stated happy path. No upstream file, test, provider, or external system was modified.

| Input shape | Observed PR-snapshot result | Consequence |
| --- | --- | --- |
| Exact frozen wrapper | One `terminal` call with `command=ls` | Recovery works. |
| Literal `</tool_call>` inside parameter, plus terminal outer close | One call; literal retained in the decoded argument | End-anchored outer-close handling avoids this corruption case. |
| Plain prose mentioning the tag without raw grammar | No call | Basic prose guard works. |
| Markdown-fenced exact wrapper with surrounding documentation | **One `terminal` call**; code-fence opener remained as content | The opener rule promotes an illustrative code block into an action candidate. Unsafe. |
| Complete parameter body but missing raw outer closer | **One `terminal` call** | Existing canonical stopword completion turns incomplete raw syntax into an action candidate. Boundary is too permissive for the frozen risk model. |
| Zero-parameter raw wrapper | No call | The parameter-tag lookahead blocks this form. |
| Two raw wrappers | **One call with the second wrapper’s `pwd` argument** | Multiple wrappers do not preserve one-call semantics; parser greediness plus last-write parameter behavior silently changes meaning. |
| Canonical call plus raw wrapper | One canonical call | The canonical-presence guard avoids raw normalization, but canonical-path trailing-content semantics remain a separate existing behavior. |

### Calibration result

The initial rule is insufficient. It proves syntactic resemblance but not a bounded action message. In particular, surrounding Markdown and a missing raw close remain indistinguishable to the proposed implementation from executable content once it rewrites the opener.

The revised conclusion is stricter:

> A malformed raw wrapper may be promoted only when the complete assistant text, after only pre-existing non-action cleanup, is exactly one complete instance of the known raw-wrapper grammar; the wrapper must have one valid tool name, at least one complete parameter tag, a terminal outer close, no canonical opener, and no additional non-whitespace content or second wrapper.

This is not a general statement that the string is semantically “an action.” It is a deliberately narrow operational rule: the parser may create an action candidate only for a whole response that is structurally indistinguishable from the bounded grammar it was asked to recover. All other forms remain content or take an explicit existing error path.

The condition sacrifices recovery of model outputs that include prose or truncation. That is intentional until public evidence establishes a safe grammar for those forms. A missed action can be retried; an invented action can cross classification and dispatch.

## Proposed normalization and action boundary

### Normalization boundary

Place recovery in preprocessing, before the canonical parser, but require a **full-message match**, not a search/substitution within arbitrary content.

The accepted raw grammar should have these properties:

1. Only optional whitespace surrounds the wrapper; no Markdown fence, quoted prose, log prefix, suffix, second wrapper, or arbitrary text.
2. It begins with `<tool_call>` and contains exactly one syntactically constrained name.
3. It contains at least one complete `<parameter=NAME>VALUE</parameter>` sequence.
4. The raw `</tool_call>` is present as the terminal outer boundary.
5. No canonical `<function=` opener occurs in the message.
6. The result is normalized once into canonical syntax and then processed by the existing parser, alias resolution, and parameter validation.

The full match must preserve parameter body text verbatim before existing parameter normalization. In particular, it must distinguish the terminal outer close from literal `</tool_call>` text inside a parameter.

### Execution/action threshold

Normalization creates only a **structured call candidate**. It is not proof of authorized execution. The candidate must then clear existing stages:

```text
full raw-grammar match
→ canonical parser
→ known-tool/alias resolution
→ schema and argument validation
→ response classification
→ action-event creation
→ existing security/confirmation policy
→ safe dispatch eligibility
```

Unknown tool names are not ordinary content after a full grammar match; they should follow the existing deterministic validation error path and must not produce a structured executable call. The normalizer should not invent a different fallback.

Malformed parameter syntax, missing required values, and repeated parameter names must not be silently repaired by the normalizer. The existing parser/validator owns them. Because repeated names currently resolve by last write, a future implementation must either preserve that established behavior explicitly in tests or reject duplicates through a separately justified, scope-controlled change; it must not accidentally change it while adding wrapper recovery.

## Evidence gates and stopping conditions

### Gate 1 — grammar admission

**Required evidence:** exact full-message raw grammar with one valid name, at least one complete parameter tag, terminal outer close, no canonical opener, and no non-whitespace envelope.

**Fail state:** leave the message content unchanged. Do not create `tool_calls`.

### Gate 2 — semantic conversion

**Required evidence:** existing canonical parser can resolve the tool name and validate arguments against the supplied tool schema.

**Fail state:** use the existing deterministic conversion/validation failure. Do not create an action event.

### Gate 3 — action boundary

**Required evidence:** the converted message is classified as exactly one tool call, and a safe test-local dispatch seam observes one eligible action with preserved name/arguments. Existing security and confirmation controls remain in force.

**Fail state:** no dispatch. The test must prove absence of an action event for ambiguous/raw-rejected forms.

### Stop conditions

- Stop recovery and preserve content if any grammar-admission condition is absent.
- Stop at validation if tool resolution or parameter validation fails.
- Stop this experiment’s scope if supporting real provider output, multi-call semantics, Markdown-aware parsing, or generic XML semantics requires a broader contract decision.
- Do not claim provider interoperability, safe execution of real tools, or upstream acceptance without corresponding evidence.

## Proposed validation boundary

### Layer A — recovery correctness

- Exact frozen raw wrapper yields exactly one call, intended name, and decoded arguments.
- Wrapper text is absent from the resulting assistant content.
- Canonical input remains unchanged in observable result.
- Existing aliases resolve after valid normalization.

### Layer B — parser precision

- Plain prose mentioning `<tool_call>` remains content.
- Markdown-fenced or quoted exact wrapper remains content.
- Leading/trailing non-whitespace prose around a raw wrapper remains content under the full-message rule.
- Literal `</tool_call>` inside a parameter survives exactly.
- Missing raw outer closer remains content; no stopword-assisted raw promotion.
- Zero-parameter wrapper remains content.
- Canonical-plus-raw input retains current canonical behavior and creates no additional call from recovery.
- Multiple raw wrappers remain content or fail explicitly under a deliberate one-call rule; they must never collapse into one call with silently selected parameters.

### Layer C — action transition

- A valid Layer-A result is classified as a tool-call response and reaches a safe test-local dispatch eligibility seam once.
- Unknown tool, schema-invalid arguments, incomplete wrapper, prose, fenced examples, and multiple wrappers create no action event.
- The test-local tool is non-destructive and has no provider, shell, network, or filesystem side effect.

These layers distinguish parsing success from safe action eligibility. Passing Layer A alone is insufficient.

## Remaining uncertainties

- The stricter full-message rule may reject genuine model outputs containing explanatory prose. No current public evidence establishes a safely distinguishable broader grammar.
- The appropriate handling of repeated parameter names is a pre-existing converter concern, not resolved here.
- Existing canonical behavior with trailing raw content is not altered by the recovery rule and needs separate scope if it is security-relevant.
- Integration fixtures may expose a repository-specific distinction between response classification, action-event creation, confirmation, and actual tool execution.
- Public PR #4608 is unmerged and based on an older branch; this treatment does not establish compatibility with current main.

## Tracking and process cost

The method changed the decision by requiring an adversarial parser experiment before treating the public recovery rule as safe. The additional work was one source/dispatch inspection and one disposable local run across five adversarial input classes. It avoided an unsupported claim that the PR’s positive and basic-negative tests established a safe action boundary.

Overhead: a compact explicit target, state/evidence separation, a second Reason pass, and a layered validation plan. The overhead is justified here because classification gives structured calls priority over content and can lead to tool handling.

## Conclusion

A recovery rule is justified, but only as a strict full-message grammar admission rule. The public opener-only normalization direction is sufficient for the frozen happy path but insufficient for action promotion: it converts fenced examples, accepts a missing raw outer close through canonical stopword repair, and collapses multiple wrappers into one altered call.

The safest minimal direction is therefore to normalize only a complete, sole, terminal raw-wrapper response and then reuse existing canonical parsing and all downstream validation/confirmation controls. Inputs that are incomplete, embedded, multiple, canonical-mixed, or otherwise ambiguous must remain non-executable until separate evidence supports a broader contract.