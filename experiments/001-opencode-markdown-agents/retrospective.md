# Retrospective

## Outcome

The local correction introduced a `resolvePrompt` helper for Markdown agents and modes:

1. use the trimmed Markdown body when non-empty;
2. otherwise use frontmatter `prompt:`;
3. apply the existing `{env:...}` / `{file:...}` resolver to the selected text.

Five focused effective-configuration tests failed before the correction as predicted and passed after it. The complete sandbox configuration suite passed 113 tests.

## What TARGET(AI) changed

The baseline plan was faster and adequate as an implementation outline. TARGET(AI) was more reliable for this issue because it required semantic decisions and observable proof before implementation.

| Criterion | Baseline | TARGET(AI) result |
| --- | --- | --- |
| Prompt precedence | Selected a likely contract | Required evidence and preserved body compatibility |
| Relative file semantics | Initially incorrect | Second reasoning pass corrected the base to the configuration directory |
| Scope | Narrow by intent | Rejected broad config refactor and duplicate resolver from stated constraints |
| Verification | Focused tests planned | Predeclared outcomes separated source explanation from executable evidence |
| Publication | Not part of local plan | Tracked separately from technical results |

## Costs and limits

For a two-file correction, full PRD/TDD-length artifacts were disproportionate. The retained value was the target/evidence gate, short assessment, genuine second reasoning pass, focused regressions, and explicit tracking of environment limits.

The experiment demonstrates a local, sandbox-validated correction. It does not establish exact-upstream CI success or merged status. PR [#47635](https://github.com/anomalyco/opencode/pull/47635) remains open while the fork's exact-lockfile CI is queued.
