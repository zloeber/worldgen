# Worldgen Development History

## 2026-11-01 — Milestone 1 baseline established

- Implemented local-first world package initialization and canonical record scaffold.
- Implemented source ingestion pipeline with deterministic IDs, content-hash idempotence, and provenance-linked observations/evidence/assertions.
- Implemented contract/schema validation, referential-integrity checks, and derived SQLite indexing.
- Implemented first organizational proposal generation methods and corresponding CLI surfaces.

Primary references:
- `src/worldgen/world.py`
- `src/worldgen/ingest.py`
- `src/worldgen/contracts.py`
- `src/worldgen/indexer.py`
- `src/worldgen/proposals.py`

## 2026-11-01 — World development recipes became first-class

- Added filesystem-native recipe definition and execution record model.
- Added recipe composition, run, and history surfaces.
- Implemented `seed-foundation`, `ingest-source`, and `discover-domains`.
- Kept planned recipes explicitly marked as planned rather than implied implemented.

Primary references:
- `src/worldgen/recipes.py`
- `src/worldgen/cli.py`
- `tests/test_recipes.py`
- `docs/world-development-recipes.md`

## 2026-11-01 — Development context bootstrap added

- Added root `AGENTS.md` and `.mex/ROUTER.md` to standardize session orientation.
- Added focused context, continuity, and pattern documents grounded in current implementation.
- Added `worldgen-development` reusable skill for orientation, evidence-backed updates, and continuity maintenance.
- Accepted ADR 0002: use skill/workflow for repository maintenance, not a world recipe.

Primary references:
- `AGENTS.md`
- `.mex/`
- `.agents/skills/worldgen-development/SKILL.md`
- `docs/development/adr-0002-development-context-scaffold.md`
