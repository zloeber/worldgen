# Worldgen Implementation Context

## Current technical structure

- `src/worldgen/world.py`: world package initialization and required directory scaffold.
- `src/worldgen/ingest.py`: source registration, idempotent ingestion, record creation pipeline.
- `src/worldgen/adapters.py`: source-specific extractors for ChatGPT export and markdown repositories.
- `src/worldgen/contracts.py` + `src/worldgen/schemas.py`: contract validation and referential integrity checks.
- `src/worldgen/indexer.py`: deterministic rebuild of derived SQLite index.
- `src/worldgen/proposals.py`: deterministic proposal generation for organizational domains.
- `src/worldgen/recipes.py`: recipe contract/catalog, dependency composition, execution lifecycle records.
- `src/worldgen/cli.py`: CLI surface for init/ingest/validate/index/propose/explore/review and recipe commands.

## Boundary notes

- Canonical record writes happen through deterministic helpers (`stable_id`, `write_json`) in `src/worldgen/utils.py`.
- Recipe definitions/executions are separate from canonical world records and live under `recipes/`.
- Validation intentionally excludes derived and raw-source directories where appropriate.

## Test anchors

- `tests/test_world_foundation.py`: world lifecycle, ingestion behavior, conflict/provenance, index, JSON-LD round-trip.
- `tests/test_recipes.py`: recipe catalog, contract checks, composition, execution metadata and failure behavior.
