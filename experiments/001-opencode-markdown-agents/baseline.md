# Baseline engineering plan

_Source: `pre_target.md` from the OpenCode investigation workspace. This records the plan before the second reasoning pass._

## Goal

Make standalone Markdown agent definitions resolve prompts with explicit precedence and the same `{file:...}` / `{env:...}` expansion behavior as equivalent JSON agent configuration.

## Scope

- `packages/opencode/src/config/agent.ts`
- Focused configuration tests in `packages/opencode/test/config/config.test.ts`
- Documentation only if the resulting prompt contract requires it

No broad configuration refactor, unrelated command behavior, or dependency changes.

## Plan

1. Establish the contract from product evidence: a non-empty Markdown body wins; an empty body falls back to frontmatter `prompt:`.
2. Map `ConfigAgent.load()`, `ConfigAgent.loadMode()`, and the JSON variable-substitution boundary.
3. Select the effective prompt and reuse `ConfigVariable.substitute` rather than create a Markdown-only resolver.
4. Add effective-configuration coverage for fallback, precedence, environment expansion, file expansion, and mode parity.
5. Run focused tests and typecheck when dependency state permits; record any external blocker exactly.

## Experiment-time assumption later corrected

The baseline proposed resolving relative `{file:...}` values from the Markdown definition file. The second TARGET(AI) reasoning pass corrected this to the configuration directory, while retaining the Markdown file as the substitution error source. The original assumption is preserved here because its correction is central experiment evidence.
