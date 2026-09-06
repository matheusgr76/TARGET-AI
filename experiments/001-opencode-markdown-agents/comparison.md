# Plan comparison

_Source: `plan_comparison.md` from the OpenCode investigation workspace._

## Decision

Use the TARGET(AI) plan for this issue. The baseline remains a useful, fair execution outline; TARGET(AI) adds an explicit evidence gate and a required second reasoning pass where semantic uncertainty can change the implementation.

| Criterion | Baseline plan | TARGET(AI) plan | Observation |
|---|---|---|---|
| Completion claims | Focused tests and typecheck planned | Observable results predeclared | Prevented treating source tracing as proof |
| Semantic uncertainty | Likely precedence chosen | Precedence, mode parity, substitution scope, and file base rechecked | Corrected the file-resolution base |
| Scope | Broad refactor avoided | Constraints and rejected alternatives explicit | Kept work to loaders and focused tests |
| Verification failure | Dependency blocker recorded | Miss classified before next action | Sandbox result remained distinct from exact verification |
| Review record | Final result summarized | Hypothesis, contradiction, and re-evaluation trigger preserved | Made the changed design decision inspectable |
| Speed | Shorter | Adds deliberate assessment and tracking | Baseline is preferable when behavior is already mechanical |

## Conclusion

TARGET(AI) was the safer plan for this defect because a plausible local implementation could have encoded the wrong relative-file contract. Its added process cost is justified only where the behavior and evidence boundary are genuinely uncertain.
