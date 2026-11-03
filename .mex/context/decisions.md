# Worldgen Decisions Index

## Accepted ADRs

- `docs/development/adr-0001-world-foundation-decisions.md`  
  Milestone 1 foundation decisions: canonical format, contract versioning, raw-source handling, idempotent ingestion, derived SQLite index, proposal methods, claim-state separation.

- `docs/development/adr-0002-development-context-scaffold.md`  
  Development guidance scaffold decision: lightweight `.mex/` context + continuity + patterns and `worldgen-development` skill; no Patternmaker runtime dependency; no development-bootstrap world recipe.

## Decision status notes

- **Established implementation:** what is in `src/worldgen/` + tests.
- **Accepted architecture decisions:** ADRs in `docs/development/`.
- **Future/proposed direction:** `docs/architecture/personal-world-poc.md` and roadmap items not yet implemented.

## Attribution

The scaffold approach was adapted from concepts in `zloeber/patternmaker` (MIT License) and tailored to Worldgen's existing architecture and constraints.
