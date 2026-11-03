# Worldgen Architecture Context

## Implemented architecture (authoritative)

Worldgen currently implements a filesystem-native world package with:
- Canonical JSON records by kind (World, Source, Observation, Entity, Relationship, Assertion, Evidence, Context, Proposal).
- Deterministic IDs/hashing for repeatable ingestion and idempotence.
- Derived SQLite index rebuilt from canonical files.
- Filesystem-native recipe definitions and recipe execution records.

Primary implementation references:
- `src/worldgen/world.py`
- `src/worldgen/ingest.py`
- `src/worldgen/contracts.py`
- `src/worldgen/indexer.py`
- `src/worldgen/recipes.py`

## Architectural invariants

- Canonical truth is local files, not a database service.
- Provenance is preserved through source, observation, evidence, and assertion links.
- Inference/interpretation is not silently promoted to accepted fact.
- Deterministic machinery is preferred where practical.
- Human review governs interpretive and organizational outcomes.

## Proposals and future direction (non-authoritative)

The Personal World POC architecture document contains broader and future-looking proposals:
- `docs/architecture/personal-world-poc.md`

Treat that file as design guidance, not guaranteed implemented behavior.
