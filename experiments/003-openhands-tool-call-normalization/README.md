# Experiment 003 — OpenHands Tool-Call Normalization

## Problem

At OpenHands revision `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1`, the non-native converter leaves this raw wrapper as assistant text rather than structured tool input:

```text
<tool_call>TOOL_NAME
<parameter=...>...</parameter>
</tool_call>
```

The bounded question was how to recover that form without converting ordinary or ambiguous assistant text into a tool-call candidate.

## Baseline and TARGET(AI) treatment

The competent conventional baseline selected a small preprocessing normalization: recognize a constrained raw opener, reuse canonical parsing and validation, preserve canonical precedence, and test safe dispatch eligibility.

TARGET(AI) initially considered that direction plausible. Its Reason Calibration then exercised the admission boundary and changed the proposed policy after three counterexamples: a fenced documentation example became a call, a missing raw outer close became a call through canonical stopword completion, and two raw wrappers collapsed into one call using later parameter content.

## Counterfactual execution

A disposable synthetic corpus compared:

- **A — baseline/public-style admission:** constrained raw opener, parameter lookahead, no canonical opener, existing canonical stopword behavior.
- **B — TARGET(AI) admission:** one complete raw wrapper must occupy the full trimmed message before canonical parsing can proceed.

Both policies recovered the exact malformed wrapper. In the corpus, A promoted a Markdown-fenced documentation example, a wrapper missing the outer raw close, and two wrappers that collapsed into one action. B retained those three forms as content.

B also retained leading- and trailing-prose wrappers that A recovered. This is an admission-policy trade-off, not proof that B is the correct production policy.

## Result and limitations

The experiment shows that adversarial calibration changed action admission on a controlled corpus. It does not establish that TARGET(AI) generally improves agent safety, that OpenHands should merge the strict policy, that the public proposal is unsafe in production, or that real providers emit these forms.

The retrospective classifies this as a **TARGET-Lite** candidate in hindsight: the useful work was the action-boundary investigation, one adversarial challenge, and controlled validation—not the full formal process for every parser fix.

## Documents

- [Frozen brief](frozen-brief.md)
- [Competent conventional baseline](baseline.md)
- [TARGET(AI) treatment](target-ai.md)
- [Pre-execution comparison](comparison.md)
- [Execution evidence](execution.md)
- [Retrospective](retrospective.md)
- [Disposable counterfactual runner](counterfactual_runner.py)
- [Machine-readable counterfactual results](counterfactual-results.json)
