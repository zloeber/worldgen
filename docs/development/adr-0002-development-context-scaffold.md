# ADR 0002: Development Context Scaffold and Governance

## Status

Accepted.

## Context

Worldgen now has a substantial implementation surface (world initialization, ingestion, contracts, indexing, proposals, recipe lifecycle), but no repository-native orientation scaffold for repeatable human/agent development sessions.

Without a durable router, context index, continuity records, and evidence-backed patterns, each session must rediscover architecture and conventions, increasing drift risk.

Patternmaker provides useful ideas (small routing surface, context files, pattern discovery discipline), but Worldgen must remain independent of external runtime dependencies and must avoid conflating repository-maintenance workflows with World Package recipes.

## Decision

Adopt a lightweight repository-native development scaffold:

- Root `AGENTS.md` as concise always-loaded entrypoint.
- `.mex/ROUTER.md` as orientation router.
- Focused context files under `.mex/context/`.
- Evidence-backed implementation patterns under `.mex/patterns/`.
- Continuity documents under `.mex/continuity/`.
- Reusable workflow skill at `.agents/skills/worldgen-development/SKILL.md`.

Also decide that development bootstrap/maintenance is **not** a Worldgen recipe at this stage.

## Rationale

- World recipes are designed to mutate/assess a target World Package with explicit recipe contracts and execution records.
- Repository development guidance is meta-work about maintaining the codebase and documentation process.
- Forcing repository maintenance into the world recipe runtime would expand scope and couple unrelated concerns.
- A skill/workflow preserves agent/runtime independence while keeping updates reviewable in Git.

## Consequences

### Positive

- Faster and more consistent session startup.
- Lower architectural drift by routing through current context + ADRs + tests.
- Better resumability through explicit current snapshot and milestone history.
- No new runtime services or package dependencies.

### Tradeoffs

- Scaffold must be maintained with discipline; stale context is possible.
- Continuity files require human/agent judgment on what is “substantial.”

## Recipe-system evaluation outcome

No new recipe is added for development bootstrap now.

If revisited later, a candidate `maintain-development-context` recipe would need to define:
- inputs (changed files + decision references),
- outputs (proposed context/pattern/continuity updates),
- mutation boundaries (documentation-only, proposal-first),
- execution history requirements,
- model-assisted interpretation flags,
- mandatory human review before acceptance.

Current decision: keep this as a skill/workflow concern until a strong in-repo use case justifies runtime integration.

## Attribution

Scaffold approach adapted from `zloeber/patternmaker` concepts and skill structure, under the MIT License.
