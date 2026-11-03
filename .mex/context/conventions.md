# Worldgen Development Conventions

## Code and data conventions

- Keep canonical records as human-readable JSON with stable key ordering.
- Use deterministic identifiers (`stable_id`) and explicit UTC timestamps.
- Preserve provenance fields and evidence links when creating new records.
- Keep derived artifacts rebuildable from canonical files.

## Testing conventions

- Use synthetic fixtures only (`tests/fixtures/`).
- Validate behavior through end-to-end flow tests, not only unit helpers.
- Preserve idempotence and deterministic behavior across reruns.
- Do not weaken existing tests to accommodate new behavior.

## Documentation conventions

- Keep durable architecture decisions in ADRs under `docs/development/`.
- Keep `.mex/context/*` focused and link to canonical docs instead of duplicating them.
- Keep `.mex/patterns/*` evidence-backed and repository-specific.
- Keep continuity split between:
  - current snapshot (`.mex/continuity/CURRENT.md`)
  - chronological milestones (`.mex/continuity/DEVELOPMENT.md`)

## Agent workflow conventions

- Read router/context/continuity before substantive changes.
- Inspect relevant implementation and tests before editing.
- If a proposed change conflicts with an accepted ADR, surface the conflict explicitly.
