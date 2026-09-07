# Retrospective — Experiment 003

**Scope:** post-execution assessment of Experiment 003 evidence only. This artifact does not revise the frozen brief, sealed baseline, sealed TARGET(AI) treatment, sealed comparison, or execution record.

## 1. Overall verdict

Experiment 003 supports one narrow conclusion: for a synthetic corpus at OpenHands revision `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1`, an adversarial second Reason pass changed a plausible raw-wrapper normalization rule into a stricter admission policy, and the later counterfactual showed that this change alters which inputs become structured action candidates.

The value is real but bounded. TARGET(AI) did not discover the representation gap, converter location, canonical-parser reuse strategy, literal-closer requirement, canonical/raw guard, tool-resolution design, or need for a safe dispatch test. The conventional baseline already had those. TARGET(AI) added concrete counterexamples, a fail-closed admission choice, and reject-specific evidence requirements.

Strict whole-message admission is a defensible conservative policy for this corpus. It is **not** established as the uniquely correct production policy.

## 2. What the OpenHands defect teaches

The defect is a grammar gap at a high-consequence boundary: non-native assistant text is converted into `message.tool_calls`, which response classification prioritizes over ordinary text and can route toward action handling.

Current main recovered no raw-only wrapper. Both experimental policies recovered the exact desired wrapper. The decisive question was not “can the string parse?” but “what structural evidence is sufficient to change untrusted text into an action candidate?”

The experiment also exposed current canonical-path consequences that a normalizer inherits:

- canonical stopword completion can close a normalized function even if the raw outer wrapper was absent;
- canonical call stripping discards suffix text after the first function opener;
- repeated parameter extraction can select a later value when a body spans multiple wrappers.

Those are facts about this deterministic corpus and converter path, not claims about provider behavior or user intent.

## 3. What the conventional baseline got right

The sealed baseline correctly:

- framed the converter as the textual-representation to structured-action boundary;
- found the dialect mismatch and located repair in preprocessing rather than a new raw parser or generic markup support;
- preserved existing canonical parsing, aliases, resolution, validation, content stripping, and later controls;
- excluded provider-owned GLM channel-token behavior;
- required constrained names, parameter evidence, canonical precedence, terminal closer handling, literal-closer preservation, and one-call discipline;
- named documentation/code examples, absent closers, multiple wrappers, unknown tools, invalid schema, and dispatch eligibility as risks or test topics;
- rejected broad tag conversion, direct `tool_calls` construction, generic XML work, and immediate multi-call support;
- required focused converter and non-destructive integration testing.

The baseline was therefore not careless. It already understood the core action boundary and nearly all broad risk classes. It is inaccurate to credit TARGET(AI) for those shared findings.

## 4. What TARGET(AI) got right and materially added

TARGET(AI) initially accepted the baseline/public direction as plausible, then made it falsifiable and ran it against adversarial forms. That produced three concrete observations:

1. A fenced documentation example became a `terminal(ls)` structured call.
2. A complete parameter body without raw outer close became a call through canonical stopword completion.
3. Two raw wrappers became one `terminal(pwd)` call, silently selecting later content.

The treatment then changed its policy from opener-based recovery to full-message, complete, sole-wrapper admission. It also required a no-call/no-action-event outcome for those rejected forms rather than merely “no malformed arguments.”

This changed:

| Dimension | Changed? | Retrospective finding |
| --- | --- | --- |
| Root-cause identification | No | Both found the same non-native dialect gap. |
| Implementation location | No | Both normalize at preprocessing and reuse canonical parsing. |
| Implementation mechanism | Partly | Both rewrite to canonical syntax; TARGET changes the admission guard, not the downstream mechanism. |
| Action-admission policy | Yes | TARGET requires full-message, complete, sole raw-wrapper evidence. |
| Validation requirements | Yes | TARGET fixes reject outcomes for fenced, missing-close, and multi-wrapper forms and checks they do not reach the seam. |

The admission-policy and validation changes mattered in execution. They caused B to retain all three discriminators as content while A produced `TOOL_CALLS` responses and one inert action-seam event for each.

## 5. What execution confirmed

### Confirmed recovery and preservation

- A and B both recovered the exact valid wrapper into one `terminal({"command":"ls"})` call.
- A and B both preserved literal `</tool_call>` inside a parameter.
- Canonical and canonical-plus-raw handling remained canonical-path behavior in all controls.
- Unknown names and invalid parameters followed existing validation errors after A/B admission; no action event resulted.

### Confirmed policy separation

| Case | A — baseline/public | B — TARGET | Evidence meaning |
| --- | --- | --- | --- |
| Fenced documentation | Call/action seam reached | Content/no seam | Explicit synthetic false-positive prevention. |
| Missing raw outer close | Call/action seam reached | Content/no seam | B requires raw boundary completion. |
| Two wrappers | One later-value `pwd` call/action seam | Content/no seam | B prevents silent one-call semantic collapse. |
| Leading prose + valid wrapper | Call/action seam reached | Content/no seam | B rejects a plausible intended action. |
| Trailing prose + valid wrapper | Call/action seam reached; suffix discarded | Content/no seam | B rejects a plausible intended action; A loses suffix content. |

The execution therefore supports the comparison’s historical **A — MATERIAL IMPROVEMENT** classification only in a narrow, policy-difference sense. It does not prove B is universally safer or production-ready.

## 6. Was Reason Calibration genuinely useful?

**Yes, in this experiment.** It falsified this precise hypothesis:

> A constrained raw opener with parameter lookahead, no canonical opener, terminal raw-close rewriting, and existing stopword repair supplies enough evidence to promote a raw wrapper safely.

The happy path did not falsify that hypothesis. The fenced, missing-close, and multi-wrapper inputs did. Calibration therefore changed the admission policy and the required assertions, not merely the language used to justify an unchanged solution.

This is stronger than Experiment 002’s role for calibration, where it sharpened a state-invariant evidence requirement but did not change the selected implementation. It also differs from Experiment 001, where a second reasoning pass caught a material file-resolution issue before contribution. The common pattern is evidence challenging a plausible assumption; the mechanisms and strength of support differ.

## 7. Practical value and measurable cost

### Value

B prevented the three discriminating A transitions from becoming `TOOL_CALLS` responses in the synthetic corpus. The fenced case is explicitly documentation in the fixture. The missing-close and multi-wrapper cases are ambiguous rather than proven non-action intent, but B’s handling follows the frozen complete-boundary and one-call criteria.

### Cost

B rejected two plausible intended calls that A recovered:

- an exact wrapper with leading prose;
- an exact wrapper with trailing prose.

That is a concrete availability/recovery cost: **2 of 3** surrounding-material action-like fixtures promoted by A were retained as content by B. The third was a documentation fence, where rejection is desirable. A standard Markdown block quote was rejected by both variants because A’s parameter lookahead did not cross `>` prefixes.

B also has a policy cost: it treats structural context as insufficient intent evidence even when the raw wrapper itself is complete. That can cause extra turns, stalled automation, or incompatibility with a real model dialect that emits explanatory prose before a call.

## 8. Did TARGET(AI) overcorrect?

Possibly. The experiment supports this distinction:

- **Supported:** strict whole-message admission is a conservative sufficient policy for the tested content-to-action transition.
- **Not supported:** strict whole-message admission is the uniquely correct production policy.

A future policy might recover leading/trailing-prose calls while excluding fenced examples, raw truncation, and multi-wrapper collapse. Possible approaches include a separately specified trusted envelope, a model/protocol-specific response channel, or a carefully evidenced contextual grammar. This experiment does not establish that Markdown/context parsing is a safe substitute for whole-message admission, and it should not be retrofitted into B merely to improve its score.

Evidence needed before relaxing B includes representative provider/model output distributions, production or replayable traces with intent labels where available, upstream compatibility expectations, maintainer intent, a larger adversarial corpus, security/confirmation behavior, and full Agent action semantics. A parser rule alone cannot generally distinguish an un-fenced example at message end from an intended action without additional protocol evidence.

## 9. TARGET Applicability Gate — hindsight classification

**TARGET-Lite**, not direct execution, basic verification, or full TARGET as routine practice.

The problem earned more than basic verification because it combines:

- untrusted text promotion into structured action;
- asymmetric false-positive consequences;
- ambiguity between recovery syntax and illustrative content;
- a hidden downstream classification/action transition;
- realistic, inexpensive adversarial counterexamples that could change the decision.

It did not justify full TARGET as a default engineering workflow. The root cause, source location, and bounded candidate were quickly available, and the decisive incremental work was compact: define the promotion threshold, make a prediction, run adversarial examples, require a dispatch-boundary observation, and track the recovery cost. The full artifact set was appropriate for this controlled method experiment, but disproportionate for a normal one-file parser fix.

## 10. Process-overhead assessment

### Work that paid for itself

- Explicitly stating that the decision was action admission rather than formatting cleanup.
- Treating the public normalization as a hypothesis rather than a conclusion.
- One adversarial Reason Calibration pass.
- A controlled A/B execution matrix with current-main control.
- Separating parser recovery, classifier transition, and non-destructive action-seam evidence.
- Recording B’s false-negative cost rather than declaring every rejection a win.

### Overhead without demonstrated incremental value

- Repeating standard method terminology after the target and evidence gates were clear.
- Document volume beyond the decision, counterexamples, result matrix, and limitations.
- Formal stage transitions that did not alter the rule, evidence, or execution.
- The inability to run upstream pytest meant some ceremony did not yield repository-parity validation.

The useful minimum for a comparable high-consequence normalization is TARGET-Lite: short target/evidence gate, source-boundary inspection, one adversarial challenge, focused A/B or regression tests, and explicit recovery-cost reporting.

## 11. Cross-experiment interpretation

The emerging hypothesis is:

> TARGET(AI)’s practical value may lie less in generating solutions and more in challenging plausible assumptions, defining sufficient evidence, and controlling state/action transitions.

Experiment 003 **weakly supports** this hypothesis.

- Experiment 001 reports that an evidence gate and second reasoning pass caught a material file-resolution issue, while also finding the full document process excessive.
- Experiment 002 reports that the baseline selected the same patch, while TARGET’s stronger state-invariant evidence gate rejected a shallow-map counterfactual that behavior-only checks allowed.
- Experiment 003 shows the strongest policy change of the three: calibration changed action admission and the counterfactual made that difference observable.

Three curated local experiments are not a general evaluation, are not independent samples, and do not measure aggregate engineering quality, safety, latency, or cost. They support a bounded design hypothesis about where the method may add value; they do not establish the method’s general effectiveness.

## 12. Claim ladder

### A. Strongly supported claim

> In a synthetic corpus at the inspected OpenHands revision, a constrained opener-normalization policy converted a fenced documentation example, a raw wrapper missing its outer close, and two raw wrappers into `TOOL_CALLS` responses that reached an inert action-event seam. A strict complete, sole-message admission policy retained those three inputs as content, while also rejecting leading- and trailing-prose wrappers that the opener policy recovered.

### B. Plausible but not yet established

> For parser repairs that promote untrusted text into action candidates, a short adversarial second Reason pass and explicit admission evidence gate may expose consequential false-positive/false-negative trade-offs that happy-path reasoning misses.

### C. Not supported

The following claims must not be made:

- TARGET(AI) generally makes AI agents safer.
- TARGET(AI) found the correct OpenHands production fix.
- Strict whole-message admission should be merged upstream.
- PR #4608 is unsafe in production.
- Real Synthetic or other provider outputs exhibit all tested forms.
- TARGET(AI) always outperforms conventional reasoning.
- The non-destructive probe proves real tool execution would be prevented or safe.

## 13. Publication recommendation

**Suitable for publication in the public TARGET-AI repository: yes, as a bounded evidence-first case study.**

Recommended central story:

> A public normalization direction recovered malformed tool syntax, but adversarial calibration showed that the same direction promoted a fenced documentation example and ambiguous raw forms into action candidates in a synthetic corpus. A stricter policy prevented those transitions, at the measured cost of rejecting plausible calls with surrounding prose.

Publication should lead with the controlled corpus, the shared baseline strengths, the recovery cost, and the limits. It should not claim general agent safety, production unsafety of the public PR, or an upstream prescription.

## 14. Upstream contribution recommendation

**Not justified from this experiment.**

Reasons:

- B is intentionally conservative and has demonstrated recovery cost; its production compatibility is unknown.
- Representative real output, maintainer intent, and upstream parser-contract expectations are absent.
- Focused upstream pytest did not run because `pytest` and repository tooling were unavailable in the disposable environment.
- The action seam was inert and did not test full Agent execution semantics.
- Public PR #4608 already covers the basic upstream recovery direction; this experiment provides a reason for broader validation, not a basis to duplicate or supersede that proposal.

A later upstream contribution could become justified after broader validation and an evidence-backed compatibility decision. None should be performed from this retrospective.

## 15. Candidate methodology lessons — change control only

No TARGET or TARGET(AI) text is modified here. Candidate lessons for future revision:

| Candidate lesson | Classification | Basis and limit |
| --- | --- | --- |
| Explicit Applicability Gate | Supported by this experiment | It identifies why basic verification was insufficient and why full ceremony was excessive. |
| Proportional TARGET/TARGET-Lite choice | Supported by this experiment | The decisive value came from a compact subset, not the entire formal process. |
| Asymmetric-error reasoning | Supported by this experiment | B’s rejection protects a text-to-action boundary but has measured availability cost. |
| Promotion/authorization boundary | Supported by this experiment | `tool_calls` classification and inert action-seam evidence made the semantic transition observable. |
| Adversarial second Reason pass | Supported by this experiment | It falsified the opener-sufficiency hypothesis and changed the policy. |
| Behavioral recovery versus permission to act | Supported by this experiment | Exact syntax recovery was not sufficient evidence for promotion in contextual/ambiguous forms. |
| Cross-domain general superiority claim | Hypothesis requiring more experiments | Three curated experiments do not estimate general benefit or cost. |

## 16. Remaining evidence gaps

1. Real provider/model raw-wrapper distributions and intent contexts.
2. Upstream maintainer preference and compatibility contract for leading/trailing prose.
3. Current-main upstream pytest, repository-prescribed validation, and hidden-test results.
4. Full Agent `_get_action_event()`, security analyzer, user confirmation, and actual safe-tool execution semantics.
5. Larger adversarial grammar corpus, including more parameter layouts and content-list behavior.
6. Whether a less restrictive context-aware grammar can match B’s precision while recovering legitimate prose-wrapped calls.
7. Downstream consumer compatibility, performance, operational telemetry, review, merge, or release evidence.

## 17. Closing

Experiment 003 demonstrates a local trade-off, not a production recommendation: stricter admission prevented three synthetic action promotions and rejected two plausible recoveries. The most defensible methodological lesson is to challenge a plausible text-to-action promotion rule with adversarial examples when classification changes downstream authority, then report both prevented promotions and lost recoveries.

No publication, upstream contribution, commit, push, pull request, issue comment, or external contact was performed.