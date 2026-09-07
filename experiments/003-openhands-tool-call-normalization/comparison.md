# Pre-execution Comparison — Experiment 003

**Inputs compared:** [frozen brief](frozen-brief.md), sealed [baseline](baseline.md), and sealed TARGET(AI) [treatment](target-ai.md).

**Status:** pre-execution analysis only. Neither implementation has been applied. This comparison does not establish that either approach prevents unsafe execution.

## Classification

# A — MATERIAL IMPROVEMENT

TARGET(AI) changes the preferred **admission grammar** from an opener-based, at-most-one rewrite that delegates missing-close behavior to canonical stopword repair into a strict **complete, sole-message raw-wrapper** admission rule. That decision is material at the content-to-structured-action boundary. It is supported by three new, concrete parser outcomes recorded in the treatment: a fenced example promoted to a call, a raw wrapper with no outer close promoted through stopword repair, and two raw wrappers collapsed into one call with later parameter content.

This is a qualified result. The baseline was competent and already identified the relevant broad risk classes: examples, absent closers, and multiple wrappers. TARGET(AI) receives credit only for converting those concerns into observed counterexamples and a binding, stricter admission decision. Strict whole-message admission is a conservative sufficient policy, not yet proven to be the uniquely necessary policy.

## Shared ground

Both artifacts substantively agree on these points:

- The defect is a non-native dialect/representation gap at converter preprocessing, not a general XML parser or the excluded GLM provider-channel problem. Baseline §§42–66; TARGET §§28–34, 64–71.
- Recovery should normalize into canonical function syntax and reuse existing canonical parsing, aliases, tool resolution, parameter validation, content stripping, classification, and later controls. Baseline §§48–60, 88–104; TARGET §§121–155.
- Direct raw parsing into `tool_calls`, broad tag stripping, generic markup parsing, canonical-parser expansion, and provider work are out of scope. Baseline §§106–117; TARGET §§73–82, 177–182.
- Literal `</tool_call>` text within parameter data must be preserved; only an outer terminal closer may be changed. Baseline §§38–40, 119–127; TARGET §§100–107, 125–136.
- Canonical input must remain authoritative and recovery must not add a duplicate call. Baseline §§78–84, 119–127, 176–183; TARGET §§127–136, 193–202.
- A focused, non-destructive dispatch-eligibility test is required in addition to converter tests. Baseline §§185–191; TARGET §§171–175, 204–210.

The classification is therefore not based on terminology, added prose, basic representation understanding, literal-closer treatment, canonical/raw non-duplication, tool lookup, or the existence of an integration test. Those are already substantively present in the baseline.

## Coverage matrix

| Comparison dimension | Baseline | TARGET(AI) | Assessment |
| --- | --- | --- | --- |
| Problem framing | Representation gateway; dialect gap. | Same. | Equivalent. |
| Representation boundary | Text → preprocessing → canonical parse → validation → `tool_calls` → dispatch. | Same, with action-candidate terminology. | Equivalent. |
| Trust/action boundary | Calls are close enough to execution to require strong regression coverage. | False-positive promotion is more harmful than a false negative. | TARGET makes the priority operational; baseline recognizes the boundary. |
| False-positive/negative asymmetry | Says false positives need equally strong coverage; frozen brief says severity at least equal. | Explicitly prefers false negatives over false positives under ambiguity. | Material policy difference. |
| Assumptions | Exact structural evidence; one-call contract; existing parser authority. | Same plus text is not reliable semantic evidence of action intent. | TARGET tightens the inference rule. |
| Initial normalization | Public PR direction: constrained opener, no canonical input, terminal closer replacement, one rewrite. | Initially the same direction. | Equivalent before calibration. |
| Final normalization | Opener-oriented rewrite; preserve leading prose; `_fix_stopword()` decides missing closer outcome. | Whole-message match; whitespace-only envelope; complete terminal outer close; no prose/fence/quote/second wrapper. | Material difference. |
| Malformed input | Missing close: test/document whether stopword can safely complete it; otherwise non-executable. | Missing raw close: always retain content; no raw stopword promotion. | Material difference. |
| Prose/documentation | Rejects general markup; requires realistic prose test; explicitly preserves leading prose around a recovered wrapper. | All non-whitespace envelope, including leading/trailing prose, remains content. | Material behavior tradeoff. |
| Markdown/code examples | Identifies docs/code examples as a risk and leaves explicit fenced exclusion unresolved. | Observed fenced false positive; requires non-executable result. | Material evidence and rule difference. |
| Multiple wrappers | Says do not support immediately; must be deterministic/non-executable or explicitly fail; calls for test. | Observes collapse with later parameter; rejects full message before canonical parser. | Material enforcement/evidence difference. |
| Canonical + raw | Canonical-presence guard; test for no duplicate. | Same guard; preserve current canonical-path behavior. | Equivalent. |
| Literal closer | Terminal-only rewrite preserves data. | Same; local screening observed it. | Equivalent. |
| Tool-name resolution | Existing resolution/alias path remains authority. | Same; unknown full-match name takes existing validation error path. | Equivalent. |
| Dispatch eligibility | One safe tool-call classification/dispatch observation. | Same, divided into a separate Gate 3. | Equivalent implementation objective; TARGET makes gate ordering explicit. |
| Evidence requirements | Focused recovery, safety, and integration tests. | Three explicit admission/conversion/action gates and adversarial test cases. | Materially sharper evidence requirements. |
| Test strategy | Positive, prose, literal closer, canonical/raw, truncation, multiple wrappers, schema, integration. | Same foundations plus fenced, quoted, leading/trailing prose, required rejection of truncation/multiple forms. | Material only where expected outcomes are stricter. |
| Integration boundary | Converter output reaches safe dispatch once without destructive activity. | Same. | Equivalent. |
| Stopping conditions | Broadening requires concrete evidence; unresolved questions remain. | Explicitly stops at every failed gate and stops scope for broader grammar/provider/multi-call decisions. | Modest process improvement, not independent classification basis. |
| Scope control | No provider/API/UI changes; one call remains contract. | Same. | Equivalent. |
| Process overhead | Conventional source/PR analysis plus planned tests. | Adds explicit second Reason experiment, evidence-gate record, and whole-message policy. | Justified only by discovered counterexamples. |

## Material differences

| Material difference | 1. Baseline said | 2. TARGET(AI) said | 3. Exact difference | 4. Evidence | 5. Action-safety/correctness effect | 6. Execution-testable? |
| --- | --- | --- | --- | --- | --- | --- |
| Admission grammar | Constrained raw opener; no canonical opener; rewrite at most one; preserve leading prose (baseline §§92–102, 121–126). | Only one complete raw wrapper may occupy the full message except whitespace (TARGET §§113–136). | Baseline admits a raw opener embedded in surrounding content; TARGET rejects every non-whitespace envelope. | Baseline’s public-PR reading; TARGET’s fenced-example run, §§98–107. | Yes. Embedded documentation can become a `tool_calls` response under opener-only matching. | Yes: converter tests with fenced, quoted, prefixed, and suffixed raw wrappers. |
| Missing outer close | Let `_fix_stopword()` determine missing-closer outcome; test/document whether it is safe (baseline §101; §§139–145, 181–182, 204–207). | Missing raw outer close is a Gate-1 failure and remains content (TARGET §§159–169, 193–202). | Baseline leaves valid-parameter truncation potentially recoverable; TARGET forbids raw recovery absent an explicit raw terminator. | TARGET observed the public-PR snapshot create one call for this form, §104. | Yes. An incomplete raw message can become dispatch-eligible under the baseline direction. | Yes: complete parameter plus omitted `</tool_call>`; assert call count and dispatch observations. |
| Multiple wrappers | Do not support immediately; require deterministic/non-executable behavior or explicit failure, but implement only an at-most-one opener rewrite (baseline §§99–102, 116, 139–145, 181–182). | A second wrapper fails full-message admission; no collapse is permitted (TARGET §§115, 129, 193–202). | Baseline states the desired invariant but does not give the normalizer a rule that enforces it; TARGET makes admission rejection the mechanism. | TARGET observed two wrappers become one call using later `pwd`, §106. | Yes. Argument selection can silently change an action while preserving apparent cardinality. | Yes: two distinct tool/parameter wrappers; assert no call or explicit deterministic failure, never a later-value single call. |
| Fenced examples | Identifies code/documentation examples as a false-positive risk and asks whether fences should be explicit, but leaves it unresolved (baseline §§129–132, 202–208). | Fenced/quoted exact raw wrapper must remain content (TARGET §§103, 193–208). | Baseline recognizes equivalent class but does not prescribe a protective grammar or exact test. | TARGET’s observed fenced-example promotion, §103. | Yes. Example text can become an action candidate. | Yes: Markdown fence around otherwise valid wrapper; assert content path and zero action events. |
| False-negative policy | False positives merit equally strong regression coverage; preserve leading prose (baseline §§68–74, 125). | Missing or surrounded raw syntax is deliberately a false negative pending evidence for a broader grammar (TARGET §§58–62, 117–119). | Baseline balances coverage without choosing a rejection preference; TARGET commits to fail closed at raw admission. | Baseline’s leading-prose requirement versus TARGET’s whole-message condition. | Yes. Determines whether a real-but-prose-prefixed wrapper can become a call. | Yes: valid raw wrapper with explanatory prefix/suffix. |
| Evidence threshold | Tests truncation and multiple behavior, but expected outcomes remain open/deterministic rather than fixed (baseline §§176–191, 202–208). | Requires specific no-action outcomes for fenced, truncated, and multiple raw inputs before dispatch. | TARGET converts open safety questions into reject-by-default evidence gates. | TARGET calibration outputs and Gate 1/Layer B. | Yes. Prevents happy-path tests from being mistaken for boundary proof. | Yes: run the specified converter and test-local dispatch matrix. |

## Exact baseline coverage of TARGET(AI)’s three counterexamples

### 1. Markdown-fenced example

**Baseline coverage:** partial risk identification, not protection.

- Baseline §110 rejects treating every tag as an action because that promotes documentation and code samples.
- Baseline §§129–132 names documentation/code examples and says parameter adjacency may not cover every quoted/example context.
- Baseline §§205–206 asks, as unresolved, whether fenced/quoted raw wrappers should be explicitly non-executable.
- Its preferred rule nevertheless preserves leading prose and performs an opener-based rewrite; it contains no full-message condition and no fenced-example expected test.

**Finding:** the baseline identified an equivalent failure class but did not identify the exact fenced case, propose a normalization rule that prevents it, or require a test that necessarily exposes it. It would plausibly accept the observed public-PR behavior unless later implementation resolved its open question conservatively.

### 2. Missing raw outer close promoted by canonical stopword behavior

**Baseline coverage:** recognizes truncation; does not protect against this exact promotion.

- Baseline §101 explicitly delegates missing-terminal-closer outcome to `_fix_stopword()`.
- Baseline §143 permits testing/documenting stopword completion of a fully formed parameter body if “safe”; it does not require the raw outer closer for admission.
- Baseline §181 requires only that malformed structured arguments not reach dispatch eligibility.
- Baseline §205 presents the policy choice—recover or retain text—as unresolved.

**Finding:** the baseline identified the truncation class and proposed a test, but it did not identify that a syntactically complete parameter body with no raw outer close can become a valid structured call. Its stated rule plausibly accepts the observed behavior, because it delegates to stopword repair and the observed call has valid rather than malformed arguments.

### 3. Two raw wrappers collapse into one action using later parameter content

**Baseline coverage:** recognizes the contract risk and requests a test; does not supply an enforcing admission rule.

- Baseline §116 rejects immediate multi-wrapper support.
- Baseline §§125–127 says the normalizer must not add/reorder calls and ambiguous input must remain text or explicitly fail.
- Baseline §§145 and 182 require deterministic/non-executable behavior or explicit failure, without accidental cardinality/order semantics.
- But its preferred implementation is “rewrite at most one valid raw opener” followed by existing parsing (baseline §§98–102), not full-message rejection or a specific multi-wrapper detector.

**Finding:** the baseline identified the equivalent multiple-wrapper class and called for a test. It did not identify the exact later-parameter collapse and its preferred mechanics do not demonstrably prevent it. The public-PR snapshot outcome in TARGET §106 is therefore new evidence with a materially stronger resulting rule.

## Special questions — direct answers

1. **Did TARGET(AI) change the preferred implementation direction?**  
   **Yes.** Both place a small normalization in preprocessing and reuse canonical parsing. Baseline prefers an anchored opener rewrite that preserves leading prose and delegates absent close to `_fix_stopword()`; TARGET prefers full-message admission, mandatory raw terminal close, and no surrounding content. That is an implementation/admission-boundary change, not a cosmetic test expansion.

2. **Did TARGET(AI) materially narrow the admission grammar relative to the baseline?**  
   **Yes.** It rejects all raw forms with non-whitespace context, a missing raw closer, or a second wrapper. Baseline’s chosen opener rule admits at least some such context and leaves absent-close behavior to canonical repair.

3. **Did the baseline already protect against fenced examples?**  
   **No.** It identified the category and made it an unresolved question; it neither required a fenced test nor adopted a grammar that rejects fences.

4. **Did the baseline already protect against truncated raw wrappers becoming calls through canonical stopword behavior?**  
   **No.** It explicitly left stopword completion as a possible outcome if later found safe. Its test requirement prohibits malformed executable arguments, not a valid call built from a complete parameter body lacking the raw outer close.

5. **Did the baseline already protect against multiple raw wrappers collapsing into one action?**  
   **Not demonstrably.** It states the correct contract-level concern and requires deterministic behavior, but its actual preferred rewrite does not define a multi-wrapper rejection mechanism. It would need an additional guard or a test-induced redesign.

6. **Did the baseline treat false-positive action creation as more consequential than false-negative recovery?**  
   **No.** It treats false-positive promotion as serious and deserving equally strong coverage, but does not select an explicit fail-closed precedence. TARGET makes that asymmetry the basis for rejecting potentially genuine prose-prefixed or truncated calls.

7. **Did Reason Calibration discover genuinely new counterexamples, or merely instantiate risks already identified by the baseline?**  
   **Both, with a material distinction.** Baseline already identified the broad risk classes. Calibration supplied new exact, executable counterexamples for the public normalization: fenced action promotion, stopword-assisted no-close promotion, and later-value collapse. Those observations changed the chosen admission rule rather than merely restating a risk.

8. **Would the baseline’s proposed tests detect all three observed counterexamples?**  
   **No.** Its truncation and multiple-wrapper tests could detect the latter two only if their cases and assertions were strengthened to the observed forms. Its prose test does not necessarily include a valid raw wrapper inside a Markdown fence. No baseline assertion requires all three to yield zero calls/action events.

9. **Is strict whole-message admission supported by evidence, or is TARGET(AI) becoming unnecessarily conservative?**  
   **Supported as a conservative sufficient policy; not proven uniquely necessary.** The fenced, truncated, and multi-wrapper results show the opener-only rule is unsafe for this bounded action threshold. They do not prove that only whole-message matching can solve the problem. A narrower alternative—explicit fence/context recognition plus raw-close and multiplicity checks—might retain safe leading prose recovery, but no artifact provides evidence that such context recognition is reliable. TARGET accurately records the availability cost and remaining uncertainty.

10. **What counterfactual implementation/test would distinguish the approaches?**  
    Implement two disposable, test-only converter variants at the same preprocessing seam: **A**, baseline/public opener normalization with terminal-close rewriting and existing stopword behavior; **B**, TARGET full-message admission with mandatory raw close and one-wrapper condition. Run the shared matrix below, then observe converted content, structured call count/name/arguments, response classification, and a non-destructive action-event seam. Do not run real tools or providers.

## Counterfactual execution design

### Implementations under test

- **Implementation A — baseline/public boundary:** constrained raw opener with parameter lookahead, no canonical opener, at-most-one opener rewrite, terminal raw-close rewrite, and existing `_fix_stopword()` completion. Preserve leading prose.
- **Implementation B — TARGET boundary:** accept raw recovery only if the trimmed full message is exactly one complete raw wrapper with one valid name, one-or-more complete parameters, terminal raw close, no canonical opener, and no other content. Otherwise return original content to the existing conversion path.

Both variants must retain existing canonical parsing, aliases, tool/schema validation, confirmation/security controls, and single-call dispatch fixture. Neither performs a real action.

### Discriminating matrix

| Input | A expected observation | B expected observation | What distinguishes them |
| --- | --- | --- | --- |
| Exact raw wrapper | One structured `terminal(command=ls)` call. | Same. | Shared recovery requirement. |
| Markdown-fenced exact wrapper | Based on TARGET’s observed PR snapshot, one structured call is likely. | Content remains; zero recovered calls/action events. | Whether illustrative code is promoted. |
| Complete parameter, missing raw outer close | Based on TARGET’s observed PR snapshot, one call is likely through stopword completion. | Content remains; zero recovered calls/action events. | Whether incomplete raw framing may promote. |
| Two distinct raw wrappers | Based on TARGET’s observed PR snapshot, one call may use later parameter content. | Content remains or an explicit deterministic failure; no collapsed action. | Whether cardinality/argument meaning can collapse. |
| Prefix/suffix prose around valid raw wrapper | Baseline intends recovery while preserving prose. | Content remains; zero recovered call. | Availability versus fail-closed admission. |
| Plain prose mentioning tag | No call. | No call. | Shared ordinary-text guard. |
| Canonical function wrapper | Existing canonical result. | Same existing canonical result. | No regression. |
| Canonical plus raw | One existing canonical result, no recovery duplicate. | Same existing canonical result, no recovery duplicate. | Canonical authority. |
| Literal closer inside parameter, terminal outer close | One call preserving literal argument text. | Same. | Outer-boundary precision. |
| Unknown name / invalid parameter after valid raw grammar | Existing deterministic validation failure; no action event. | Same. | Existing authority retained. |

### Required observations before a stronger claim

1. Exact valid recovery yields one call with the intended tool, decoded arguments, and wrapper removal.
2. A/B converter outputs prove the stated discriminators, including content preservation for B’s rejections.
3. Classification sees exactly one tool-call response only for admitted/valid input.
4. The non-destructive action-event seam observes one eligible call for the valid case and zero action events for fenced, truncated, multiple, prose, unknown-tool, and schema-invalid cases.
5. Literal closer, canonical, canonical-plus-raw, aliases, and existing schema behavior remain unchanged.
6. Current-main tests establish the result without providers, external tools, or production claims.
7. If leading prose is a required real-world dialect, evidence must show a grammar that distinguishes it from examples before relaxing whole-message admission.

## Validation comparison

Baseline and TARGET both correctly require converter-level and focused dispatch-level checks. The difference is the assertion strength:

- Baseline requires explicit truncation/multiple behavior but leaves their acceptance/rejection policy unresolved; it requires realistic prose but not necessarily fenced raw syntax.
- TARGET fixes the expected results for the counterexamples: no recovered structured call and no action event.
- Both require no duplicate canonical conversion, literal closer preservation, existing resolution/alias behavior, and no destructive dispatch activity.

TARGET’s Layer A/B/C terminology is not itself an improvement. The material increment is that Gate 1 denies admission before canonical stopword parsing can reinterpret an incomplete or embedded raw form.

## Process-overhead assessment

The baseline already performed broad source/issue/PR analysis and proposed strong tests. TARGET added an explicit initial hypothesis, an adversarial local screening pass, a revised policy, and gate-oriented documentation.

The extra cost is justified for this experiment because the new pass changed the recommended action boundary based on concrete outputs. It would **not** be justified merely to restate the same risks in TARGET terminology. Conversely, whole-message admission adds an availability cost: it rejects leading-prose outputs that baseline intended to preserve. That cost must be measured in later execution before claiming it is the optimal production policy.

## What TARGET(AI) materially added

1. Three concrete counterexamples against the public opener-normalization boundary.
2. A changed, enforceable preferred admission rule: whole-message, complete, sole raw wrapper.
3. An explicit fail-closed policy for missing raw closure, surrounding prose/fences, and multi-wrapper ambiguity.
4. A validation matrix whose negative cases require zero structured calls/action events, not only absence of malformed arguments.
5. A clear separation between syntactic admission, existing semantic conversion, and safe dispatch eligibility.

## What TARGET(AI) did not add

- A new root cause, converter location, or downstream architecture.
- A better literal-closer rule, canonical/raw guard, alias/tool-resolution design, or non-destructive dispatch objective; those were already in baseline.
- Proof that whole-message admission is the only safe design, that it works on current main, or that it is compatible with all genuine non-native output layouts.
- Evidence of provider interoperability, real-tool safety, maintainer acceptance, or production behavior.

## Conclusion

TARGET(AI) materially improved the pre-execution decision because its Reason Calibration invalidated the baseline’s preferred public-normalization boundary on three concrete forms and changed the admission rule accordingly. The baseline had already identified the broad hazards, so the improvement is not superior general understanding; it is stronger evidence and a stricter action-boundary decision.

No implementation, test execution of the proposed counterfactual variants, provider invocation, or tool execution has occurred. Stop before implementation.