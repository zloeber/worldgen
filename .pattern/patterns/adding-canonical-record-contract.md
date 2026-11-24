# Pattern: Adding or changing canonical record contracts

## Context
Apply when introducing a new canonical record field/kind, changing schema constraints, or adjusting validation logic.

## Steps
1. Update shared contract expectations in `src/worldgen/contracts.py` (`KIND_REQUIRED_FIELDS` and validation flow).
2. Update JSON Schema definitions in `src/worldgen/schemas.py`.
3. Preserve referential-integrity checks for cross-record links.
4. Ensure ingestion/proposal/indexing code writes the updated fields consistently.
5. Extend tests in `tests/test_world_foundation.py` and/or `tests/test_recipes.py`.

## Gotchas
- Updating schema without writer code changes causes immediate validation breakage.
- Updating writer code without schema/required-field updates creates hidden drift.
- New references without integrity checks can pass ingest but fail later exploration/indexing.

## Verify
- Run full tests (`PYTHONPATH=src python -m pytest`).
- Run `worldgen validate` on a generated fixture world and confirm zero errors.
- Add or update malformed-record tests to prove failures are detected.

## Debug
- Inspect validation errors from `validate_world` for field/path detail.
- Check whether the failing JSON file is canonical, raw source, recipe definition, or execution record.
- Rebuild index to ensure downstream surfaces still ingest the updated canonical shape.

## Update Scaffold
- Update this pattern when contract version changes, new kinds are added, or validation boundaries change.
