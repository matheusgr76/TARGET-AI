# TARGET(AI) plan

_Source: `target_ai_plan.md` from the OpenCode investigation workspace. Experiment-time observations are retained; current contribution status is separated below._

## Target

**Outcome:** Markdown agent and mode definitions select prompts with explicit precedence and apply the same `{file:...}` / `{env:...}` substitution behavior as JSON configuration.

**Evidence standard:** demonstrate empty-body frontmatter fallback, non-empty-body precedence, environment substitution, configuration-directory-relative file substitution, mode parity, and successful relevant test execution.

**Constraints:** preserve non-empty-body behavior; reuse the established resolver; localize the correction; do not infer completion from source tracing or non-targeted checks.

## Assess

Both Markdown loaders constructed `{ ...md.data, prompt: md.content.trim() }`, so the body always overwrote `prompt:`. Neither used `ConfigVariable.substitute`; equivalent JSON configuration did. The exact dependency installation was initially blocked by an unavailable locked provider version.

## Reason

The first hypothesis selected the non-empty body, otherwise frontmatter `prompt:`, then routed that effective text through the existing resolver.

The required second pass overturned the initial file-base assumption. The reported `.opencode/agent/foo.md` → `{file:./prompts/foo.md}` case and JSON parity require `.opencode/prompts/foo.md`, not a path relative to the agent file. The selected call was:

```ts
ConfigVariable.substitute({ type: "virtual", dir, source: item, text })
```

`dir` gives the configuration-directory base; `item` remains the error source.

## Generate and execute

Chosen: a small shared selected-prompt helper for the duplicated agent/mode loaders. Rejected: a broad config refactor, Markdown-specific resolver, changed non-empty-body precedence, and unrelated runtime warnings.

The evidence plan added five resolved-configuration cases and compared executable results against the declared evidence standard.

## Experiment-time versus current contribution state

The source plan was written during a changing publication sequence and includes historical statements about absent/draft external work. Those statements are not current status. Locally verified contribution state is branch `markdown-agent-prompts` at `cd8a3f6`; current GitHub status is [PR #47635](https://github.com/anomalyco/opencode/pull/47635) open, not merged. Exact-lockfile CI has no completed result recorded in this repository.
