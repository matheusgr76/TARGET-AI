# Execution — Experiment 003

**Status:** controlled, disposable pre-merge experiment. This record does not modify or revise the sealed brief, baseline, TARGET treatment, or comparison.

## Objective and classification target

Test what two preprocessor admission policies classify as a structured action under the fixed synthetic corpus:

- **A — baseline/public admission:** constrained raw `<tool_call>NAME` opener with parameter lookahead, no canonical opener, one rewrite, terminal raw-close rewrite when present, then existing `_fix_stopword()` and canonical parser behavior.
- **B — TARGET(AI) admission:** a trimmed message must be one complete raw wrapper with a valid name, one-or-more complete parameter elements, terminal raw outer close, no canonical opener, no non-whitespace surrounding material, and no second wrapper; then use the same existing parser.

No policy was used to harden the other. Both variants are in-process, temporary replacements of `_preprocess_model_output()` and restore the original function after each fixture.

## Revision and environment

| Item | Value |
| --- | --- |
| Upstream source revision under test | `df2ea8fa5542d5d2a543e108bc8b2d4fbbab34b1` |
| Source import path | `<disposable current-main checkout>/openhands-sdk/openhands/sdk` via `PYTHONPATH` |
| SDK source metadata | `openhands-sdk` 1.45.0 |
| Interpreter | Disposable Python 3.12.3 virtual environment |
| Platform | Linux x64, WSL2 |
| Provider/model calls | None |
| Real tool execution | None |

The virtual environment originally referenced a public-PR checkout, so every experiment invocation explicitly prepended the disposable current-main checkout to `PYTHONPATH`. The runner confirmed that import path before execution.

## Disposable implementation

Created only inside this experiment directory:

- `counterfactual_runner.py` — runs the corpus and temporary variants.
- `counterfactual-results.json` — full machine-readable per-fixture observations.

### A — baseline/public variant

The runner applies the public proposal’s constrained opener expression:

```text
<tool_call> + valid name + line break + parameter lookahead
```

Only if no canonical `<function=` is present, it rewrites the first valid opener and rewrites a raw outer close only when it is terminal. It deliberately leaves the existing `_fix_stopword()` behavior in place. This is the comparison’s specified A boundary; it is not strengthened with whole-message, fence, truncation, or multiplicity guards.

### B — TARGET variant

The runner accepts raw recovery only through a full-message match. It validates the name token, requires at least one complete existing parameter element, removes those parameter elements to ensure the remaining wrapper body is whitespace only, rejects an inner `<tool_call>` opener, and converts only the final raw closer. That body check preserves literal `</tool_call>` text inside parameter values. It is deliberately not generic XML or Markdown parsing.

### Non-destructive Layer-C seam

After conversion, each output is converted to the SDK `Message` model and passed to the real pure `classify_response()` function. For `TOOL_CALLS`, the real `ResponseDispatchMixin._handle_tool_calls()` is invoked on `DispatchProbe`, a test-local host whose `_get_action_event()` records a call and returns an inert object; `_execute_actions()` records the inert batch only. No Agent, tool implementation, shell, filesystem action, network call, or provider is invoked.

`dispatch_eligible=true` and `action_events=1` therefore mean **one tool call crossed classification and reached this non-destructive action-event seam**, not that an SDK tool was actually executed.

## Corpus

The corpus contains the 15 required fixtures: exact raw, leading prose, trailing prose, fenced, Markdown block quote, missing outer close, parameter-truncated, two wrappers, plain prose, canonical, canonical plus raw, literal closer in a parameter, unknown tool, invalid parameter, and zero-parameter raw wrapper. It introduces no provider syntax, generic XML grammar, or multi-call feature behavior.

## Result notation

Each outcome records:

```text
content | calls | name / decoded args | raw normalization | classification | eligible/action events | error
```

- `C` = content classification; `T` = `tool_calls` classification.
- `Y/1` = the non-destructive seam observed one eligible call and one inert action event.
- `N/0` = no structured action reached the seam.
- `—` = no value because conversion raised deterministic validation error.

The exact full content strings and all raw fields are preserved in [counterfactual-results.json](counterfactual-results.json).

## Full current-main / A / B matrix

| Fixture | Current main control | A — baseline/public | B — TARGET | Interpretation |
| --- | --- | --- | --- | --- |
| Exact valid raw | Original raw content \| 0 \| — \| no \| C \| N/0 \| — | Empty \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 \| — | Empty \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 \| — | Shared desirable recovery. |
| Leading prose + valid raw | Full prose + raw \| 0 \| — \| no \| C \| N/0 | `I will inspect the directory.` \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 | Full prose + raw \| 0 \| — \| no \| C \| N/0 | Ambiguous trade-off; measured B recovery cost. |
| Trailing prose + valid raw | Full raw + suffix \| 0 \| — \| no \| C \| N/0 | Empty \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 | Full raw + suffix \| 0 \| — \| no \| C \| N/0 | Ambiguous trade-off; B cost; A also loses suffix text through existing canonical stripping. |
| Markdown-fenced wrapper | Full documentation fence \| 0 \| — \| no \| C \| N/0 | `Documentation example:\n```xml` \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 | Full documentation fence \| 0 \| — \| no \| C \| N/0 | Desirable rejection by B; A false positive for this synthetic example. |
| Markdown block-quoted documentation | Full quote \| 0 \| — \| no \| C \| N/0 | Full quote \| 0 \| — \| no \| C \| N/0 | Full quote \| 0 \| — \| no \| C \| N/0 | No difference: the `>` prefix blocks A’s parameter lookahead. |
| Complete parameter, no raw outer close | Original incomplete raw \| 0 \| — \| no \| C \| N/0 | Empty \| 1 \| `terminal {command: ls}` \| yes \| T \| Y/1 | Original incomplete raw \| 0 \| — \| no \| C \| N/0 | Desirable rejection by B under frozen complete-boundary criterion; A promotes it through stopword completion. |
| Truncated inside parameter | Original truncated raw \| 0 \| — \| no \| C \| N/0 | — \| 0 \| — \| yes \| — \| N/0 \| `FunctionCallValidationError`: missing `command` | Original truncated raw \| 0 \| — \| no \| C \| N/0 | No action for either. A normalizes then deterministically fails validation; B preserves content. |
| Two complete raw wrappers | Both raw wrappers \| 0 \| — \| no \| C \| N/0 | Empty \| 1 \| `terminal {command: pwd}` \| yes \| T \| Y/1 | Both raw wrappers \| 0 \| — \| no \| C \| N/0 | Desirable rejection by B; A silently collapses two calls into later `pwd`. |
| Plain prose mentioning tag | Same prose \| 0 \| — \| no \| C \| N/0 | Same prose \| 0 \| — \| no \| C \| N/0 | Same prose \| 0 \| — \| no \| C \| N/0 | No difference; shared ordinary-prose guard. |
| Existing canonical function | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Shared canonical preservation. |
| Canonical plus raw wrapper | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Empty \| 1 \| `terminal {command: ls}` \| no \| T \| Y/1 | Shared canonical authority; existing content stripping removes raw suffix. |
| Literal raw closer in parameter | Original raw \| 0 \| — \| no \| C \| N/0 | Empty \| 1 \| `terminal {command: "printf '</tool_call>'"}` \| yes \| T \| Y/1 | Empty \| 1 \| same argument \| yes \| T \| Y/1 | Shared desirable recovery; literal closer preserved. |
| Unknown tool | Original raw \| 0 \| — \| no \| C \| N/0 | — \| 0 \| — \| yes \| — \| N/0 \| `FunctionCallValidationError` unknown tool | Same deterministic error | Shared existing validation semantics after admission. |
| Invalid parameter name | Original raw \| 0 \| — \| no \| C \| N/0 | — \| 0 \| — \| yes \| — \| N/0 \| `FunctionCallValidationError` disallowed `not_command` | Same deterministic error | Shared existing schema validation after admission. |
| Zero-parameter raw wrapper | Original raw \| 0 \| — \| no \| C \| N/0 | Same raw \| 0 \| — \| no \| C \| N/0 | Same raw \| 0 \| — \| no \| C \| N/0 | No difference; excluded by both parameter-required grammars. |

## Layer A — recovery

**Pass for both A and B.** The exact frozen wrapper produced exactly one `terminal` call with decoded `{"command": "ls"}`, empty post-conversion assistant content, `TOOL_CALLS` classification, and one non-destructive seam action event. Existing canonical conversion also remained exactly one call with the same decoded argument for current main, A, and B.

Literal `</tool_call>` within a parameter was preserved by both variants as `printf '</tool_call>'`.

## Layer B — precision

The three calibration discriminators all separated A from B:

| Discriminator | A result | B result | Classification survives? |
| --- | --- | --- | --- |
| Markdown-fenced wrapper | One `terminal(ls)` call; action seam reached once. | Original content; zero calls/actions. | Yes: A `TOOL_CALLS`, B `CONTENT`. |
| Complete parameter, missing raw outer close | One `terminal(ls)` call via canonical stopword completion; action seam reached once. | Original content; zero calls/actions. | Yes: A `TOOL_CALLS`, B `CONTENT`. |
| Two raw wrappers | One `terminal(pwd)` call; action seam reached once. | Original content; zero calls/actions. | Yes: A `TOOL_CALLS`, B `CONTENT`. |

The first is a clear synthetic false positive for A because the fixture explicitly labels the wrapper as documentation inside a code fence. The latter two are ambiguous/incomplete action-like content, but B’s rejection is consistent with the frozen complete-boundary and one-call criteria. This experiment does not establish intent for real model output.

## Layer C — action transition

- Every accepted valid raw/canonical fixture had one structured call, `TOOL_CALLS` classification, and exactly one non-destructive probe action event.
- Every B-rejected raw form stayed `CONTENT` with no probe action event.
- Unknown tool and invalid-parameter forms reached existing converter validation errors after both A and B normalization; neither produced a structured call or action event.
- Parameter-truncated input differed in failure mode: A normalized, then raised `FunctionCallValidationError` for missing `command`; B retained content. Neither crossed the action seam.

This validates the conversion-to-classification-to-test-seam transition, not actual Agent `_get_action_event()` argument/tool validation or real action execution.

## False-positive observations

### A — baseline/public variant

Observed synthetic false-positive/unsafe-promotion candidates:

1. **Markdown-fenced documentation** became `terminal(ls)`, `TOOL_CALLS`, and one action-seam event.
2. **Missing raw outer close with a complete parameter** became `terminal(ls)` and one action-seam event through `_fix_stopword()`.
3. **Two wrappers** became one `terminal(pwd)` action, discarding the first `ls` wrapper and silently selecting the later parameter.

The first is explicitly non-action content in the corpus. The second and third are ambiguous rather than proven non-action intent; their classification as false positives is bounded to the frozen requirement that incomplete/ambiguous text not be promoted absent sufficient structural evidence.

### B — TARGET variant

No synthetic corpus fixture was promoted by B when it was fenced, surrounded by prose, incomplete, multiple, block-quoted, plain prose, or zero-parameter. This is not evidence that B has no false positives outside this corpus.

## False-negative / availability cost of B

B rejected two fixtures A recovered:

1. **Leading prose + exact wrapper:** A preserved the prose and produced one action; B retained all content with no call.
2. **Trailing prose + exact wrapper:** A produced one action but existing canonical stripping dropped the suffix; B retained all content with no call.

Both are plausible intended actions, so B’s behavior is a measurable recovery cost, not automatically a correctness win. In this corpus, B rejects **2 of 3** surrounding-material action-like cases that A promoted; the third surrounding-material case, the fenced documentation example, is desirable rejection. The block-quoted example was rejected by both due to A’s syntactic parameter-lookahead limitation.

## Current-main control

Unmodified current main classified every raw-only wrapper fixture as `CONTENT` with zero structured calls and zero action-seam events. It classified canonical and canonical-plus-raw fixtures as one canonical `TOOL_CALLS` response with one action-seam event. This confirms the controls distinguish current main from A/B recovery policies; it is not a re-evaluation of the sealed baseline reasoning.

## Tests and commands

| Command / check | Result |
| --- | --- |
| `<current-main checkout>/openhands-sdk` on `PYTHONPATH`, then `python counterfactual_runner.py` | Exit 0; 15 fixtures × current-main/A/B recorded in `counterfactual-results.json`. |
| Corpus assertions over the saved results | **11/11 passed.** Assertions cover exact recovery, canonical preservation, all three discriminators, B prose cost, literal closer, prose/quote guard, validation errors, and zero-parameter behavior. |
| `python -m py_compile counterfactual_runner.py` | Exit 0. |
| `python -m pytest tests/sdk/llm/test_llm_fncall_converter.py tests/sdk/agent/test_response_dispatch.py -q` | **Not run:** exit 1 before collection because the disposable virtual environment has no `pytest` module. `pytest` and `uv` were also unavailable on `PATH`; no dependency installation was attempted. |

The runner itself invokes current-main `convert_non_fncall_messages_to_fncall_messages()`, current-main `classify_response()`, and current-main `ResponseDispatchMixin._handle_tool_calls()` with the inert seam. It is not reported as an upstream pytest suite.

## Contradictions and unexpected findings

1. The comparison predicted a quoted/documentation wrapper might distinguish policies. A standard Markdown block quote did **not**: A’s parameter lookahead does not cross `>` prefixes, so both variants retained it as content.
2. A’s trailing-prose acceptance does not preserve that prose: existing canonical content stripping returns text before `<function=`, so the suffix vanished after promotion.
3. A normalized parameter-truncated content before producing a deterministic missing-required-parameter error. It did not create an action, while B simply retained the raw content.
4. Canonical-plus-raw content retains canonical authority in all policies, but existing canonical stripping removes the raw suffix. Neither counterfactual changes that existing behavior.

## Limitations

- Synthetic strings only; no claim about real provider/model emission or intended semantics of real prose/fenced content.
- B is an intentionally strict disposable representative of the sealed treatment, not a proposed upstream patch and not proof that whole-message matching is uniquely necessary.
- The non-destructive probe exercises the real mixin dispatch loop but not real Agent tool lookup/action construction, confirmation, security analysis, or tool execution.
- Focused upstream pytest suites could not run because the available disposable environment lacked `pytest`; no dependencies were installed.
- No formatter/linter beyond Python bytecode compilation was available/practical for the disposable runner.

## Conclusion

Under this synthetic corpus, A promoted the fenced example, missing-outer-close wrapper, and two-wrapper input into `TOOL_CALLS` responses that reached the non-destructive action seam. B retained all three as content. B also rejected leading- and trailing-prose wrappers that A recovered, demonstrating a real availability/recovery cost.

Execution therefore **supports the comparison’s Classification A** in the limited sense that the stricter admission rule materially changes action classification on the discriminating corpus. It does not establish that B is universally safer, that these forms occur in production, or that B should be merged upstream.

No external action occurred. Stop before retrospective or implementation work.