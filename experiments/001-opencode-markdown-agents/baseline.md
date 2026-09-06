# Baseline engineering plan

## Goal

Make standalone Markdown agent definitions resolve prompts with documented precedence and the same `{file:...}` / `{env:...}` expansion behavior as equivalent JSON configuration.

## Scope

- `packages/opencode/src/config/agent.ts`
- Focused resolved-configuration tests
- Documentation only if it contradicts the resulting contract

No broad configuration refactor, unrelated command/mode semantics, or dependency changes.

## Plan

1. Establish the product contract: a non-empty Markdown body wins; an empty body falls back to frontmatter `prompt:`.
2. Map `ConfigAgent.load()`, `ConfigAgent.loadMode()`, and the existing JSON substitution boundary.
3. Select the effective prompt, then reuse `ConfigVariable.substitute` instead of implementing a Markdown-only resolver.
4. Add behavior-level regressions for fallback, precedence, environment expansion, file expansion, and mode parity.
5. Run focused tests and typecheck when dependencies permit; record any external dependency blocker precisely.

## Initial risk assessment

The original baseline assumed a relative `{file:...}` path should resolve from the Markdown definition file. The TARGET(AI) second reasoning pass later disproved that assumption: issue reproduction and JSON parity require resolution from the configuration directory. This correction is retained as experiment evidence, not hidden as a revised baseline.
