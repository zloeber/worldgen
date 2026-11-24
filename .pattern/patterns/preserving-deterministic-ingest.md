# Pattern: Preserving deterministic ingestion

## Context
Apply when adding or modifying source ingestion behavior, source adapters, or canonical record generation in `src/worldgen/ingest.py` and `src/worldgen/adapters.py`.

## Steps
1. Keep source identity stable (`stable_id("source", source_type, source_name, origin)`).
2. Compute content hash from exact input path and gate idempotence on unchanged hash.
3. Generate observation/evidence/entity/assertion/relationship IDs from deterministic inputs only.
4. Preserve provenance links (`source_id`, `source_reference`, `evidence_ids`, `observed_at`).
5. Record ingest outcome in `sources/ingest-log.jsonl`.
6. Normalize ChatGPT timestamps to UTC date-times and keep observation IDs based on source reference plus content, not model output.
7. Leave `valid_until` unset when the claim has no end time. The assertion schema accepts a date-time string and rejects null.

## Gotchas
- Introducing non-deterministic fields into ID inputs causes duplicate or drifting records.
- Writing candidate assertions without conflict checks can erase contradiction visibility.
- Source adapter changes can alter normalization unexpectedly and break repeatability.
- Optional LiteLLM interpretation is separate from observation identity. It writes `interpretation_level=interpretation` assertions and is skipped once completed for the same model and API base. Do not put free-form model text into observation or evidence IDs.

## Verify
- Run full tests (`uv run pytest`).
- Confirm repeat ingestion of identical source returns idempotent skip behavior.
- Confirm provenance fields remain populated and referential integrity stays valid.

## Debug
- Inspect source manifest (`sources/manifests/*.json`) for content hash changes.
- Compare generated IDs before/after the change for the same fixture input.
- Run `worldgen validate` to catch contract or reference breaks.

## Update Scaffold
- Update this pattern when ingestion identity inputs, provenance fields, or idempotence contract changes.
