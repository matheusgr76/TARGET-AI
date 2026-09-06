# Experiment 001 — OpenCode Markdown Agent Configuration

## Problem

OpenCode issue [#47616](https://github.com/anomalyco/opencode/issues/47616) reported that Markdown-defined agents could silently lose frontmatter `prompt:` configuration and the established `{file:...}` / `{env:...}` variable-substitution behavior. Related issue [#41712](https://github.com/anomalyco/opencode/issues/41712) belongs to the broader Markdown configuration-resolution family; source tracing found it already resolved on the investigated `dev` state, so it was not modified in this experiment.

## Why this experiment

This was a real external open-source defect used to evaluate whether TARGET(AI) improved reasoning quality over a conventional engineering plan. The code change was small, but prompt precedence, mode parity, and relative-file semantics were materially uncertain.

## Baseline

The baseline plan fairly scoped a localized correction: preserve a non-empty Markdown body, fall back to frontmatter `prompt:`, reuse the existing resolver, cover behavior with focused tests, and avoid a broad configuration refactor. Its initial relative-file assumption was later shown to be wrong.

## TARGET(AI) intervention

The work used Target / Assess / Reason / Generate / Execute / Track. It predeclared resolved-configuration evidence, traced the current loader behavior, required a second reasoning pass on precedence and relative files, rejected broader alternatives, implemented the smallest shared correction for agents and modes, and tracked verification limits separately from code results.

## Key finding

The initial assumption was to resolve relative `{file:...}` references from the Markdown definition file. The second reasoning pass changed that design:

- resolve relative file references from the configuration directory;
- retain the Markdown definition file as the error source.

The selected resolver call therefore used a virtual source with `dir` as the resolution base and the Markdown file as `source`.

## Evidence

| Observation | Result |
|---|---|
| Before correction | 4 expected failures; 1 body-precedence control pass |
| After correction | 5 targeted tests passed |
| Full sandbox configuration suite | 113 passed, 0 failed |

The sandbox used a temporary compatibility dependency because the exact locked provider version was unavailable publicly. Exact-lockfile CI is incomplete: a fork workflow run has been queued and no completed upstream CI result is recorded here.

## What TARGET(AI) changed

The main benefit was not code generation. It exposed assumptions, imposed an evidence standard, corrected a plausible but wrong path-resolution design, prevented overclaiming from a compatibility sandbox, and controlled scope to the affected loaders and tests.

## Limitations

This is one small experiment. TARGET(AI) added process overhead, and PRD/TDD-level ceremony is probably excessive for small defects. The method should scale with uncertainty and risk.

## Upstream contribution

Local contribution state: branch `markdown-agent-prompts`, commit `cd8a3f6`. Verified GitHub state: [PR #47635](https://github.com/anomalyco/opencode/pull/47635) is open and its compliance bot accepted the updated template. It is not merged; no acceptance claim is made.

## Documents

- [Baseline engineering plan](baseline.md)
- [TARGET(AI) plan](target-ai.md)
- [Plan comparison](comparison.md)
- [Retrospective](retrospective.md)
