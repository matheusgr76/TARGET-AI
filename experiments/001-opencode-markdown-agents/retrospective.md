# Retrospective

_Source: `target_ai_retrospective.md` from the OpenCode investigation workspace, curated to distinguish experiment-time evidence from later contribution activity._

## Experiment-time result

The correction selected the trimmed Markdown body when non-empty, otherwise frontmatter `prompt:`, then applied the existing `{env:...}` / `{file:...}` resolver. The same behavior was applied to Markdown modes because the loader and schema were duplicated.

Five focused resolved-configuration tests covered frontmatter fallback, body precedence, environment substitution, configuration-directory-relative file substitution, and mode fallback.

| Check | Experiment-time result |
|---|---|
| New tests before correction | 4 expected failures; body-precedence control passed |
| New tests after correction | 5 passed, 0 failed |
| Full sandbox configuration suite | 113 passed, 0 failed |
| Sandbox typecheck | Did not complete: unmodified `src/bus/global.ts` error under temporary compatibility dependencies |
| Exact authoritative dependency graph | Not locally installable because the public registry lacked the locked provider version |

## Methodological value

The evidence gate prevented overclaiming. The second reasoning pass caught the material file-resolution error before it reached the contribution. Constraints excluded runtime warnings, command-loader changes, dependency changes, and a configuration-system redesign.

## Cost

The process produced more planning material than the two-file correction required. PRD/TDD-length artifacts were excessive here; the useful minimum was a target/evidence gate, short assessment, genuine second reasoning pass, focused regressions, and explicit tracking of verification limits.

## Historical status versus current status

The source retrospective says publication was deferred because that was true when it was written. It is historical evidence, not current status.

Current locally verified state is `markdown-agent-prompts` at `cd8a3f6`; verified GitHub state is [PR #47635](https://github.com/anomalyco/opencode/pull/47635) open and not merged. Exact-lockfile CI is still incomplete in this record. No statement here claims maintainer acceptance, merge, or general validation of TARGET(AI).
