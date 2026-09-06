# TARGET(AI) plan

## Target

**Outcome:** standalone Markdown agent and mode definitions select prompts with explicit precedence and apply the same `{file:...}` / `{env:...}` substitution behavior as JSON configuration.

**Evidence gate:** prove empty-body frontmatter fallback, non-empty-body precedence, environment substitution, configuration-directory-relative file substitution, mode parity, and successful relevant test execution.

**Constraints:** preserve non-empty-body behavior; reuse the established resolver; localize the change; do not claim completion from source tracing or a non-targeted check.

## Assess

The agent and mode loaders constructed `{ ...md.data, prompt: md.content.trim() }`, so the body always overwrote `prompt:`. Neither loader invoked `ConfigVariable.substitute`; JSON configuration did. Exact dependencies could not initially be installed because the locked provider version was unavailable publicly.

## Reason

The initial hypothesis was that the smallest correction selects the body when non-empty, otherwise frontmatter `prompt:`, then applies the existing resolver.

A required second pass changed a material detail. The initial plan assumed `{file:...}` should resolve relative to the Markdown definition. The issue reproduction placed an agent at `.opencode/agent/foo.md` and the prompt file at `.opencode/prompts/foo.md`; equivalent JSON resolves from the configuration directory. The selected design therefore uses:

```ts
ConfigVariable.substitute({ type: "virtual", dir, source: item, text })
```

`dir` provides JSON-compatible relative resolution while `item` retains the Markdown file as the error source.

## Generate

Chosen: a small shared selected-prompt helper used by agent and mode loaders.

Rejected: a broad configuration refactor, a Markdown-specific resolver, changing non-empty-body precedence, and runtime warnings outside the reported defect.

## Execute and track

Implement only the selected behavior, add the predeclared regressions, then compare executable observations with the evidence gate. Treat dependency or runner availability as operational evidence, not as proof of the product behavior.
