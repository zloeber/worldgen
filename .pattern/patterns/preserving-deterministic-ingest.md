# Pattern: Preserving deterministic ingestion

## Context
Apply when adding or modifying source ingestion behavior, source adapters, or canonical record generation in `src/worldgen/ingest.py` and `src/worldgen/adapters.py`.

## Steps
1. Keep source identity stable (`stable_id("source", source_type, source_name, origin)`).
2. Compute content hash from exact input path and gate idempotence on unchanged hash.
3. Generate observation/evidence/entity/assertion/relationship IDs from deterministic inputs only.
4. Preserve provenance links (`source_id`, `source_reference`, `evidence_ids`, `observed_at`).
5. Record ingest outcome in `sources/ingest-log.jsonl`.

## Gotchas
- Introducing non-deterministic fields into ID inputs causes duplicate or drifting records.
- Writing candidate assertions without conflict checks can erase contradiction visibility.
- Source adapter changes can alter normalization unexpectedly and break repeatability.

## Verify
- Run full tests (`PYTHONPATH=src python -m pytest`).
- Confirm repeat ingestion of identical source returns idempotent skip behavior.
- Confirm provenance fields remain populated and referential integrity stays valid.

## Debug
- Inspect source manifest (`sources/manifests/*.json`) for content hash changes.
- Compare generated IDs before/after the change for the same fixture input.
- Run `worldgen validate` to catch contract or reference breaks.

## Update Scaffold
- Update this pattern when ingestion identity inputs, provenance fields, or idempotence contract changes.
