# TARGET(AI) quick reference

TARGET(AI) is a goal-directed engineering cycle for problems with meaningful uncertainty.

1. **Target** — State the observable outcome, evidence gate, constraints, and stopping horizon.
2. **Assess** — Record the current state, evidence, unknowns, and environmental limitations.
3. **Reason** — Form a hypothesis, then deliberately test the assumptions most likely to change the design.
4. **Generate** — Consider only options that satisfy the target constraints; reject scope expansion without evidence.
5. **Execute** — Make the smallest correction that implements the selected option.
6. **Track** — Compare observed outcomes with the evidence gate. Classify misses as operational, reasoning, or strategic before choosing the next loop.

## Evidence discipline

- A source trace explains a defect; it does not prove a correction works.
- Predeclare behavior-level evidence before editing.
- Preserve contradictory evidence and rejected alternatives.
- Separate local, compatibility, and exact-environment verification.
- Do not convert an unverified result into a completion claim.

## Scaling

Use the full cycle when behavior, scope, or environment is uncertain. For mechanical changes, retain the target and evidence gate but avoid ceremony that cannot change a decision.
