# TARGET(AI) quick reference

TARGET(AI) is a goal-directed loop for engineering work where requirements, semantics, or verification are uncertain.

1. **Target** — Define the observable outcome, evidence standard, constraints, and stopping horizon.
2. **Assess** — Record current facts, unknowns, and environmental limits.
3. **Reason** — State a hypothesis; inspect the assumptions most likely to change the design.
4. **Generate** — Compare only options that satisfy the constraints; reject scope growth without evidence.
5. **Execute** — Implement the smallest selected correction.
6. **Track** — Compare results with the evidence standard and decide the next loop.

## Evidence rules

- Source tracing can explain a defect but cannot prove a correction.
- Define behavior-level evidence before editing.
- Separate compatibility-environment results from exact-environment verification.
- Preserve contradictory evidence, revised decisions, and unresolved limits.
- Classify a miss before reacting: operational setup, reasoning, or strategy.

Scale the process to risk. For mechanical work, keep a clear target and evidence gate; do not add ceremony that cannot alter a decision.
