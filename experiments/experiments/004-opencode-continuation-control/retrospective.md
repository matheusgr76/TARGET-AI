# Experiment 004 — Retrospective

**Scope:** Assessment of the five sealed Experiment 004 artifacts only. This document does not revise the frozen brief, baseline, TARGET treatment, comparison, execution verdict, or sealed success criteria.

## Experiment summary

The frozen problem was a local OpenCode continuation-control gap: the current intra-message `doom_loop` guard did not aggregate identical completed local tool calls across separate assistant-message turns. The competent baseline chose a canonical `(tool name, input)` counter scoped to one parent user-message run, with heuristic threshold 10 and immediate terminal error before another provider turn.

TARGET retained the detector, scope, equality rule, and threshold. It changed only the threshold interpretation: ten repeats would stop further automatic tool execution but permit exactly one tool-free reassessment turn before normal closure or terminal error.

Execution used an isolated frozen dependency checkout, two existing frozen-source smoke tests, and a disposable counterfactual state-machine harness. Neither policy was installed in production OpenCode. The execution verdict remains **D — BASELINE PREFERRED, LOW confidence**. The strongest limitation is that the discriminating tool-free reassessment transition was not exercised through actual `SessionPrompt`/`SessionProcessor` and provider protocol behavior.

## What the baseline got right

The baseline was strong conventional engineering, not a straw man. It correctly:

- narrowed the issue to cross-turn continuation rather than generic runaway agents;
- selected an exact observable detector: completed local calls with canonical tool name/input signatures;
- scoped state to one session and parent user-message run;
- preserved existing intra-message `doom_loop` semantics;
- stated that threshold 10 was a heuristic inherited from public prior art, not a calibrated constant;
- named legitimate polling/retry/idempotent reads as false positives and alternating/varied calls as false negatives;
- chose deterministic terminal behavior with no post-threshold provider turn;
- kept implementation, provider, state-machine, and test cost lower; and
- predeclared focused acceptance evidence for threshold behavior, state integrity, cancellation, and existing-control preservation.

The counterfactual execution matched that intended simple behavior: ten tools, zero post-threshold provider turns, visible error, and modeled idle completion. No evidence supports diminishing the baseline’s quality.

## What TARGET added

### Conceptual contribution

TARGET made one real distinction explicit:

> Evidence sufficient to withdraw permission for continued automatic action is not necessarily evidence sufficient to declare the task itself failed.

The legitimate-polling challenge supports that distinction. Exact repetition is a liveness signal, not a universal proof of semantic no-progress.

### Behavioral contribution

TARGET materially changed the policy transition:

```text
terminal error
→ one bounded tool-free reassessment
→ normal closure or terminal error
```

This added a provider turn, `reassessmentIssued` state, tool suppression, and a second closure/error path.

### Evidence contribution

TARGET raised the required evidence for the richer transition: it required a protocol-valid no-tool turn, exact-one reassessment behavior, adversarial tool-request handling, meaningful versus unhelpful closure distinction, and coherent final state. It sharpened false-positive reasoning and stopping semantics. These are contributions; document length or stage labels are not.

## Did Reason Calibration pay for itself?

| Question | Finding |
| --- | --- |
| Did calibration reveal a real distinction? | **Yes.** It separated stopping automatic tools from declaring task failure. |
| Did it materially change the policy? | **Yes.** It changed the runtime transition and cost model. |
| Did execution show changed policy was better? | **No.** Useful closure was scripted only in the disposable model; actual-runtime usefulness was not established. |
| Did practical value justify cost? | **Uncertain; execution verdict prefers no.** Added provider/state/protocol cost was certain, benefit remained unproved. |

Changed reasoning is not improved outcome. Calibration was intellectually productive but did not establish that the richer operational policy should replace the baseline.

## Why baseline won

Baseline won the sealed D verdict because it solved the bounded liveness question with the least state and no extra provider turn. TARGET added a reassessment state, temporary tool suppression, an extra transition, and one provider turn.

The harness showed two opposite deterministic possibilities:

- a scripted useful reassessment could state that automatic work was bounded, summarize unresolved deployment state, and ask for concrete intervention;
- a scripted `I appear to be stuck.` reassessment had zero incremental value and still ended in error.

The useful case proves only that the modelled policy **can represent** useful closure. It does not show that frozen OpenCode can execute the tool-free protocol coherently or that a real model will reliably produce useful closure. TARGET’s cost was certain; actual-runtime benefit and reliability were not. That asymmetry supports D at low confidence.

### Capability versus reliability

- **Capability demonstrated:** only in the disposable counterfactual model. The selected state machine can represent one no-tool reassessment, suppress an attempted reassessment tool call, and reach modeled idle closure/error.
- **Reliability demonstrated:** no. No real model, installed policy, or actual provider/tool protocol exercised useful reassessment.

## What neither treatment solved

Shared limits remain shared:

- legitimate long polling is interrupted at threshold;
- changing output still reaches threshold because detector equality excludes output;
- alternating calls escape;
- syntactically different but semantically equivalent calls escape;
- generic semantic no-progress is not solved;
- no parent heartbeat/progress model exists; and
- no production integration evidence exists.

These are not evidence that one treatment uniquely failed.

## Changing-output finding

The changing-output fixture used the same tool and same input with output progressing from pending 10% to 100%. Both policies fired at ten because output is outside the frozen detector.

It demonstrates that repeated action and lack of progress are not equivalent. Neither policy was designed to resolve that distinction. This is a future research/design question, **not** evidence that TARGET won or baseline lost, and does not justify retrofitting Experiment 004.

## TARGET-Lite process cost

**Assessment: PARTIALLY.**

Useful cost:

- calibration exposed a real action-versus-failure distinction;
- pre-registration prevented useful scripted prose from being miscounted as real-model reliability;
- comparison/execution recorded provider/state/protocol cost rather than assuming richer control wins; and
- the process permitted a baseline-preferred result without rewriting the treatment.

Cost without established return:

- frozen treatment and comparison artifacts;
- second-pass analysis;
- expanded fixtures and conceptual transition complexity;
- proposed runtime provider turn and suppression state; and
- a large amount of process for a narrow detector already closely anticipated by public prior art.

TARGET-Lite added enough value to reveal why a richer policy was tempting and what it would need to prove. It did not add enough executed value to displace the simpler baseline.

## Applicability Gate hindsight

**Hindsight classification: BASIC VERIFICATION would likely have been enough for the engineering decision; TARGET-LITE was justified as a method experiment, not as a default engineering workflow.**

The original TARGET-Lite classification was reasonable: the defect was bounded, resource consequence mattered, several policy transitions were plausible, and deterministic local signals existed. In hindsight, public prior art already supplied the core exact-repeat guard, the conventional baseline was strong, and the discriminating transition could not be validated in actual runtime without temporary implementation work. A smaller A/B protocol feasibility check would likely have answered the engineering choice more directly.

This is not a claim that TARGET-Lite was a mistake. It produced a valid negative result: additional control structure should pay for itself. Full TARGET would have been excessive; direct execution would have been too weak to expose the transition trade-off.

## Cross-experiment interpretation

Existing conclusions support only a cautious pattern:

- **001:** a second reasoning pass caught a material path-resolution assumption; full process documentation was excessive for the small correction.
- **002:** baseline selected the same patch; TARGET strengthened the state-invariant evidence boundary and its counterfactual rejected a shallow incomplete repair.
- **003:** adversarial calibration materially changed a text-to-action admission policy, and a synthetic counterfactual made the different transitions observable.
- **004:** calibration materially changed continuation semantics, but the controlled execution evidence preferred the simpler baseline because richer behavior lacked proven runtime value.

Experiment 004 refines rather than contradicts the emerging hypothesis. It supports the idea that TARGET(AI) can challenge assumptions and control evidence/action transitions, while showing that more transition structure is not automatically operationally valuable. Four curated local experiments do not estimate general engineering quality, safety, cost, or method superiority.

## Candidate methodology lessons

| Candidate lesson | Classification | Basis and limit |
| --- | --- | --- |
| A. Control structure has a cost | **SUPPORTED HERE** | TARGET’s extra provider turn/state was certain; benefit was not. |
| B. Stopping action differs from declaring objective failure | **WEAKLY SUPPORTED** | The distinction is conceptually real; viable useful recovery was not proven in frozen runtime. |
| C. Capability differs from reliability | **SUPPORTED HERE** | Scripted model capability did not establish real-model/runtime reliability. |
| D. Continuation deserves its own evidence threshold | **WEAKLY SUPPORTED** | Exact repetition justified bounded-action review in the model, but no production transition was validated. |
| E. Applicability/proportionality should govern TARGET itself | **SUPPORTED HERE** | Baseline strength and unproven richer transition support stepping down in routine similar work. |

## Should the methodology change?

### Published TARGET/TARGET(AI)

**NO.** One local, low-confidence baseline-preferred experiment is not sufficient evidence to change published methodology.

### Future-edition candidates

Record, but do not adopt:

1. Require an explicit distinction between capability and reliability whenever a deterministic fixture scripts a model’s “helpful” response.
2. Before selecting a richer control transition, require a focused protocol-feasibility check where the claimed value depends on tool suppression, recovery, or reassessment.
3. Count added runtime turns/state transitions as first-class costs in method comparisons.

### TARGET Applicability Gate

The experiment strengthens proportionality: when public prior art and a strong conventional design already cover the primary bounded defect, basic verification may be preferable unless a new transition has an inexpensive discriminating test.

### TARGET-Lite

No adjustment is required. TARGET-Lite behaved correctly by generating a challenger policy, pre-registering its cost and evidence requirements, and allowing that policy to lose. The lesson is to apply it proportionally, not to force it to win.

## Public claim boundary

### Strongest supported claim

> In a frozen local counterfactual experiment on OpenCode continuation control, TARGET-Lite changed the interpretation of ten repeated completed calls from immediate terminal failure to one bounded tool-free reassessment opportunity. The modelled reassessment could express useful scripted closure, but its additional provider turn and state complexity were certain while frozen-runtime compatibility and real-model benefit were not established; the simpler baseline was therefore preferred at low confidence.

### Supported but weaker observations

- Exact canonical repetition can be modeled as a bounded automatic-continuation signal without claiming semantic no-progress.
- A useful text response and an unhelpful `I appear to be stuck.` response have materially different incremental value under the pre-registered definition.
- Output variation does not prevent either frozen detector from firing.
- Existing prompt normal-tool and cancellation tests ran after frozen-lockfile dependency installation, but they did not validate either unimplemented policy.

### Unsupported claims

- TARGET prevents runaway agents.
- TARGET is generally safer than conventional engineering.
- Reassessment is generally better than stopping.
- OpenCode’s public PR direction is wrong.
- Semantic progress was solved.
- TARGET wins most experiments.
- The experiment validates general agent safety.
- The selected TARGET transition is production-correct or real-model reliable.

## Publication value

**PUBLISH WITH STRONG LIMITATIONS.**

The negative result has audit value: TARGET proposed a richer intervention, pre-registered its additional cost, execution preferred the simpler baseline, and methodology did not “win.” Publication should lead with the counterfactual-only evidence level, the low-confidence D verdict, and the absence of actual-runtime policy integration. It should not present the result as a production policy evaluation.

## Future experiment questions

1. Can output-sensitive repetition distinguish observable progress from looping without creating unsafe or evasive semantics?
2. How should a tool explicitly declare polling/retry expectations?
3. When can an actual runtime safely convert a continuation threshold into reassessment rather than stop?
4. Can real-model reassessment be made reliable across providers and tool protocols?
5. How should parent agents observe child progress without inventing misleading heartbeat signals?
6. Can resource budgets complement exact-repeat detection without punishing long productive tasks?
7. What local, observable signals can approximate information gain in agent loops?

## Cross-experiment hypothesis update

**Before 004:** TARGET(AI) tentatively appeared most useful for challenging plausible assumptions, strengthening evidence boundaries, and controlling action transitions.

**After 004:** TARGET(AI) may add value by challenging assumptions and governing evidence/action transitions under uncertainty, but additional control structure is beneficial only when measurable value exceeds operational cost.

**Confidence: LOW.** The hypothesis reflects four curated local experiments with heterogeneous evidence levels; Experiment 004’s policy difference was not integrated into frozen runtime.

## Retrospective verdict

| Item | Judgment |
| --- | --- |
| Experiment result | **D — BASELINE PREFERRED** |
| TARGET contribution | **CONCEPTUAL** |
| TARGET-Lite process value | **LIMITED** |
| Methodology change | **CANDIDATE ONLY** |
| Publication | **PUBLISH WITH STRONG LIMITATIONS** |

No sealed prior artifact was modified. No commit, push, pull request, issue action, or maintainer contact occurred.
