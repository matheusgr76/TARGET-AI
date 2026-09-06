# TARGET(AI)

Experiments in goal-directed AI engineering under uncertainty.

TARGET(AI) applies TARGET — a goal-directed method built around explicit objectives, reasoning, evidence, feedback, and adaptation — to AI-assisted engineering. Rather than assuming the initial plan is correct, the process uses feedback loops to expose assumptions, test them against evidence, and adjust the next action.

This repository tests TARGET(AI) against real problems.

The objective is not to prove that the method works.
The objective is to discover when it works, when it does not, and why.

## Scope

Each experiment preserves its plans, observed evidence, limitations, and retrospective. This is an evidence repository, not a book mirror, product pitch, or endorsement claim.

## Experiments

| # | Problem | Project | Status | Main finding |
|---|---|---|---|---|
| 001 | Markdown agent configuration | OpenCode | [PR #47635](https://github.com/anomalyco/opencode/pull/47635) open; exact-lockfile CI incomplete | Second reasoning pass corrected a path-resolution assumption |

## Method

See the [methodology overview](methodology/overview.md).

## Further reading

TARGET(AI) is part of the TARGET series by Matheus G. Reis.

- **[TARGET: A General Method for Goal-Directed Action, Learning, and Adaptation](https://www.amazon.com/dp/B0HGGT666T)** — the core methodology
- **[TARGET(AI): A Method for Goal-Directed Action, Tested Against AI and Autonomy](https://www.amazon.com/dp/B0HH8J89J8)** — applying the methodology to AI-assisted and agentic systems
