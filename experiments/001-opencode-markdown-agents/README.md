# Experiment 001 — OpenCode Markdown-agent prompts

## Problem

OpenCode issue [#47616](https://github.com/anomalyco/opencode/issues/47616) reported that Markdown agent frontmatter `prompt:` values were overwritten by the Markdown body and did not use the established `{env:...}` / `{file:...}` configuration substitution path.

## Documents

- [Baseline engineering plan](baseline.md)
- [TARGET(AI) plan](target-ai.md)
- [Retrospective](retrospective.md)

## Observed evidence

- Current-source tracing found that both Markdown agent and mode loaders unconditionally assigned `md.content.trim()` to `prompt` and bypassed `ConfigVariable.substitute`.
- Five behavior-level regressions covered frontmatter fallback, non-empty body precedence, environment substitution, configuration-directory-relative file substitution, and mode parity.
- Before the correction, four new regressions failed as expected; the body-precedence control passed.
- After the correction, the five focused regressions passed. The sandbox configuration suite passed 113 tests.
- The sandbox used a temporary compatibility dependency because the exact locked `gitlab-ai-provider@6.14.0` was unavailable from the public registry. Its typecheck failure in unmodified code is not treated as authoritative.

## Upstream contribution status

The correction is commit `cd8a3f6` on `matheusgr76/opencode:markdown-agent-prompts` and PR [anomalyco/opencode#47635](https://github.com/anomalyco/opencode/pull/47635) is open. It has **not** been merged. An exact-lockfile workflow run on the fork is queued; no CI completion claim is made here.
