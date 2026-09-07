# Baseline Analysis — Experiment 003

> **SEALED BASELINE**
>
> Created before TARGET(AI) treatment. This reasoning is immutable. Any later correction or discovery must be recorded in a subsequent experiment artifact, not by editing this document.

## Baseline prompt

> "Analyze this SDK defect and propose the safest minimal implementation and
> validation plan. Use the available repository evidence, current source and
> tests, issue discussion, and public unmerged PR #4608. Identify the exact
> representation boundary, likely root cause, preferred normalization rule,
> alternatives, false-positive risks, malformed-input risks, integration risks,
> and the tests required to establish correctness without turning ordinary text
> into executable tool actions."

## Investigation performed

### Starting evidence

- Read the [frozen brief](frozen-brief.md), [issue #4540](https://github.com/OpenHands/software-agent-sdk/issues/4540), its maintainer discussion, and the issue timeline.
- Used the screening reproduction on `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1`: the exact raw wrapper stayed in assistant content and produced no `tool_calls`.
- Treated the GLM raw-channel-token report as out of scope. The maintainer analysis places that behavior in Synthetic’s serving/parser stack, not this SDK converter.

### Current source and tests

- Inspected `openhands-sdk/openhands/sdk/llm/mixins/fn_call_converter.py`:
  - `FN_REGEX_PATTERN` recognizes only canonical `<function=NAME>...</function>` calls.
  - `_fix_stopword()` invokes `_preprocess_model_output()` before canonical matching and supplies only a missing canonical closer.
  - `_preprocess_model_output()` currently strips a `<tool_call>` wrapper only when a canonical `<function=` opener already follows it.
  - `_convert_assistant_to_fncall()` returns the message unchanged when there is no canonical match; otherwise it resolves the tool name, validates parameters, creates one structured call, and removes the call text from assistant content.
  - `convert_non_fncall_messages_to_fncall_messages()` deep-copies input and processes one assistant message at a time.
- Inspected `tests/sdk/llm/test_llm_fncall_converter.py`: canonical conversion, malformed canonical parameter handling, validation, aliases, and multiple-tool-call constraints are covered. The raw-name wrapper has no current-main regression coverage.
- Inspected the response classification path. A response containing `message.tool_calls` is classified as `TOOL_CALLS` and reaches tool-call handling; content that remains text follows a different path.

### Public proposal

- Inspected [PR #4608](https://github.com/OpenHands/software-agent-sdk/pull/4608), open and unmerged. It converts a raw wrapper only when no canonical `<function=` exists, requires a valid name followed by a parameter tag, and rewrites the outer closing tag only at the end of content.
- The PR’s later patch specifically corrects a false parsing boundary where literal `</tool_call>` within a parameter had been mistaken for the outer closer.
- The public PR snapshot passed the screening checks for recovery, literal closer preservation, and plain-prose non-conversion. That is useful evidence, not proof of acceptance or current-main compatibility.

## Problem understanding

The non-native function-calling converter is a representation gateway. It turns assistant text into an OpenAI-shaped structured call that the rest of the SDK may classify and dispatch. The raw `<tool_call>NAME` wrapper is semantically close to the SDK’s prompted dialect but does not satisfy the existing canonical grammar, so it falls through as text.

The repair is not general XML/markup parsing. It is a tightly bounded dialect normalization performed before the existing canonical parser. The central correctness question is whether the text carries enough evidence to become an action candidate. Recovery only matters when it does not enlarge the set of ordinary assistant content that becomes executable.

## Representation boundary

```text
non-native model-like assistant text
→ converter preprocessing
→ canonical function-call parser
→ tool-name resolution and parameter validation
→ structured message.tool_calls
→ response classification
→ safe tool-dispatch eligibility
```

The converter is the transition from untrusted textual representation to structured action representation. The normalizer must not bypass existing resolution, schema validation, aliases, or later dispatch controls.

## Root-cause analysis

**Root cause:** the current preprocessor handles `<tool_call>` only as a wrapper around an already-canonical `<function=...>` call. It has no rule for a wrapper whose bare name replaces the canonical opener. Consequently, `_find_function_match()` cannot match the raw form and `_convert_assistant_to_fncall()` returns the original content.

The issue is therefore a grammar gap between a narrowly observed model/provider output dialect and the SDK’s non-native canonical dialect. The canonical parser itself, tool lookup, and parameter extraction do not need to be broadened to diagnose the failure.

## Assumptions

1. The raw wrapper is a supported recovery input only when it has the exact structural evidence frozen for this experiment: wrapper opener, valid name token, parameter tag, and unambiguous outer boundary where applicable.
2. Existing canonical parsing, tool resolution, aliases, required-parameter validation, and content stripping are the intended authority after normalization.
3. One function call per assistant message remains the current contract. A normalizer must not silently expand that contract.
4. Creating a structured call is not tool execution, but it is sufficiently close to execution that false-positive promotion needs equally strong regression coverage.
5. The public maintainer analysis and PR are legitimate baseline evidence. A competent baseline should use rather than hide them.

## Interpretation of PR #4608

PR #4608 is directionally correct. It places the repair at `_preprocess_model_output()`, preserving the rest of the converter pipeline. Its essential constraints are also correct:

- do not apply recovery if canonical `<function=` syntax is present;
- require the bare wrapper name to be followed by a parameter tag;
- restrict the tool-name token to the existing tool-name domain rather than accepting arbitrary content;
- rewrite only the outer terminal close so parameter content survives;
- rely on existing stopword repair and schema validation rather than adding a parallel parser.

The PR should not be accepted mechanically. Its older base requires verification against current main, and its handling of absent closers and multiple wrappers must be made consistent with the frozen safety criteria before a later implementation is selected.

## Preferred implementation

Modify only `openhands-sdk/openhands/sdk/llm/mixins/fn_call_converter.py` and its focused tests.

1. Define one compiled pattern for the raw wrapper opener. It must require:
   - literal `<tool_call>`;
   - optional whitespace;
   - a syntactically constrained nonempty tool name;
   - a line boundary; and
   - a following `<parameter=` tag.
2. In `_preprocess_model_output()`, after existing canonical-wrapper cleanup, attempt this recovery only if the content contains no `<function=` opener.
3. Rewrite at most one valid raw opener to `<function=NAME>`.
4. Rewrite only a terminal outer `</tool_call>` to `</function>`. Do not replace a closer found in parameter content.
5. Let `_fix_stopword()` and the canonical parser determine the outcome of a missing terminal closer. Do not manufacture parameter values or a structured call directly.
6. Leave nonmatches unchanged so ordinary or ambiguous text cannot reach `tool_calls` through this rule.

This is smaller and safer than adding a second extraction pipeline. It preserves the current semantic authority of `_resolve_tool_name()`, `_extract_and_validate_params()`, and canonical content stripping.

## Rejected alternatives

| Alternative | Decision | Reason |
| --- | --- | --- |
| Parse every `<tool_call>` tag as an action | Reject | Promotes prose, documentation, code samples, and arbitrary markup into action candidates. |
| Strip wrapper tags without requiring a parameter tag | Reject | A bare tool-looking token is insufficient action evidence. |
| Broaden `FN_REGEX_PATTERN` to accept both dialects directly | Reject | Interleaves recovery grammar with canonical parsing and makes later ambiguity harder to constrain. |
| Parse directly into `tool_calls` from a new raw-wrapper parser | Reject | Duplicates existing alias resolution, parameter validation, ID creation, and content stripping paths. |
| Replace every `</tool_call>` occurrence | Reject | Corrupts literal parameter content; PR #4608 already demonstrates this failure mode. |
| Normalize when canonical `<function=` is also present | Reject | Can duplicate or conflict with an already-authoritative action representation. |
| Support multiple raw wrappers immediately | Reject for the initial patch | Current converter and prompt contract are one call per message. Preserve or explicitly reject this form rather than changing cardinality incidentally. |
| Repair GLM raw-channel tokens in the SDK | Reject | The frozen experiment excludes the provider-owned failure; there is no deterministic SDK-only evidence that the SDK can correctly interpret that transport-specific channel. |

## Parser and normalizer constraints

- The recovery pattern must be narrow, anchored to the malformed opener shape, and require a parameter-tag lookahead.
- It must never treat an arbitrary newline after `<tool_call>` as enough proof of action intent.
- A well-formed canonical call must win unchanged.
- Only the outer terminal close may be rewritten. Literal close text inside an argument is data.
- The normalizer must preserve leading prose; existing content stripping should remove only the actual normalized call.
- It must not add a second call or reorder calls.
- An incomplete or ambiguous wrapper must remain text or result in the existing explicit conversion/validation outcome; it must not yield a guessed argument payload.

## False-positive action risks

1. **Documentation/code example:** assistant content may explain or write the literal tag grammar. Parameter-tag adjacency is necessary but may not alone cover every quoted/example context; the test suite should include realistic prose.
2. **Canonical duplication:** a message with both raw and canonical forms could otherwise generate conflicting interpretations. The canonical-presence guard is mandatory.
3. **Argument corruption:** broad close-tag substitution can alter the command/content passed to a tool.
4. **Multiple action expansion:** accepting multiple wrappers can silently alter the one-call contract and execute actions in an unexpected order.
5. **Unknown tool names:** normalization should not make an unknown token executable; existing tool lookup must reject it.

## Malformed-input behavior

A raw wrapper with no sufficient structural evidence is not recoverable merely because it resembles a tool call. In particular:

- no parameter tag: retain as content;
- invalid or absent tool name: retain as content or fail under existing canonical validation only after a valid normalization path;
- no closing wrapper: do not invent arguments. If existing canonical stopword completion can safely close a fully formed parameter body, test and document that behavior; otherwise leave it non-executable;
- literal closing text inside a parameter: preserve it exactly;
- multiple wrappers: fail explicitly/deterministically or remain non-executable under current one-call semantics.

## Likely files and components

- `openhands-sdk/openhands/sdk/llm/mixins/fn_call_converter.py`
  - `_preprocess_model_output()` for narrow normalization;
  - a module-level compiled pattern next to existing parser patterns.
- `tests/sdk/llm/test_llm_fncall_converter.py`
  - raw-wrapper recovery, canonical preservation, prose non-conversion, literal closer preservation, truncation behavior, and multiple-wrapper behavior.
- Focused agent/response-dispatch test location, after examining existing fixtures during a future authorized implementation, to show a structured converter output is processed once through a safe dispatch-eligibility path.

No provider adapter, LiteLLM transform, public API, tool implementation, or Agent Canvas UI change is currently justified.

## Implementation plan

1. Confirm the current converter test fixtures and the least-invasive safe dispatch test seam.
2. Add focused failing behavioral tests for the frozen positive and negative criteria.
3. Implement the bounded preprocessing rewrite; do not alter canonical parser semantics.
4. Run converter tests and the focused integration test against current main.
5. Run the repository-required changed-file checks and the relevant LLM test selection.
6. Compare any behavior not covered by current tests against the frozen criteria rather than broadening scope to provider behavior.

## Validation strategy

### Converter recovery

- Exact raw `terminal` wrapper produces one call named `terminal` with decoded `{"command": "ls"}` arguments.
- Assistant content retains leading prose but not the normalized wrapper.
- Canonical function syntax produces its existing call unchanged.
- Aliased tool names follow the existing alias-resolution path after normalization.

### Safety and malformed input

- Plain prose mentioning `<tool_call>` creates no call.
- A literal `</tool_call>` inside a parameter remains in decoded arguments.
- A raw wrapper beside a canonical call does not produce a duplicate call.
- Truncated wrapper handling is asserted explicitly: no malformed structured arguments may reach dispatch eligibility.
- Multiple raw wrappers have deterministic current-contract behavior; expected cardinality/order must not be inferred from accidental regex behavior.
- Unknown tool and invalid parameter cases retain existing validation behavior after a valid normalization, rather than bypassing schema checks.

### Integration validation

Feed a converted message carrying exactly one safe, test-local tool definition into the established response classification/dispatch path. Assert that it is identified as a tool-call response and the safe dispatch seam observes exactly one eligible call with the same normalized name and decoded arguments. The fixture must not execute shell, network, filesystem-destructive, or provider activity.

### Quality checks

Run the focused converter test module, the focused integration test, and repository-prescribed format/lint/type checks for changed files. No provider test is required or sufficient for the bounded SDK claim.

## Regression risks

1. The recovery regex may be overly permissive and create action candidates from ordinary text.
2. It may be overly restrictive and fail valid observed output variants; broaden only with concrete public evidence and new negative tests.
3. Close-tag rewriting may damage payload strings or malformed canonical content.
4. A current-main difference from PR #4608’s base may expose type, import, or test-fixture incompatibilities.
5. The converter’s one-call invariant may be violated by accidental repeated substitution.
6. A successful converter test alone could hide a later response-classification or dispatch-count regression; hence the focused safe integration test.

## Unresolved questions

- Does current main have an existing agent-level test helper that proves dispatch eligibility without invoking a concrete tool?
- Is truncated raw-wrapper recovery safely covered by current stopword semantics, or should a truncated wrapper remain text by policy?
- Should a raw wrapper appearing inside fenced code or quoted content be explicitly non-executable beyond the frozen prose case?
- Is one raw wrapper plus unrelated trailing content currently intended to recover, preserve, or reject? The answer should follow observed canonical semantics, not a new assumption.
- Does the project require an eval/integration label or broader risk review for parser behavior that can create actions? The repository guidance calls parsing changes eval-risk, but no maintainer decision is available.

## Confidence

**High (0.84).**

The current failure is directly reproduced, the representation transition is visible in source, and the public maintainer analysis plus PR provide a narrowly compatible implementation direction. The principal uncertainty is not how to parse the happy path; it is the evidence boundary for safe promotion of text into an action candidate, especially truncated, duplicated, embedded, and close-tag-containing forms. The baseline therefore prefers the public normalization strategy but requires stronger negative and focused integration evidence before treating it as complete.