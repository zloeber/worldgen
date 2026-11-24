# Pattern: Implementing recipe lifecycle behavior

## Context
Apply when adding or changing recipe definitions, recipe execution metadata, composition rules, or recipe CLI behavior.

## Steps
1. Define or update recipe contract fields in `src/worldgen/recipes.py` with explicit `implementation_status`.
2. Keep recipe definition files (`recipes/definitions/*.json`) and execution records (`recipes/executions/*.json`) separate.
3. Enforce required inputs before execution and record lifecycle step statuses.
4. Capture reproducibility metadata (deterministic flag, input fingerprint, contract versions).
5. On failure, record failure status and skipped lifecycle stages instead of silent partial success.

## Gotchas
- Missing lifecycle/failure recording hides debugging and audit signals.
- Dependency composition changes can reorder workflows unexpectedly if not tested.
- Mixing model-assisted metadata into deterministic-only paths can blur reproducibility.

## Verify
- Run full tests (`PYTHONPATH=src python -m pytest`).
- Validate recipe definition schema checks and dependency composition behavior.
- Confirm execution history includes both success and failure records with lifecycle state.

## Debug
- Inspect `recipes/definitions/*.json` for missing contract fields.
- Inspect `recipes/executions/*.json` for lifecycle transitions and failure payloads.
- Run `worldgen recipe compose` and `worldgen recipe history` against a fixture world.

## Update Scaffold
- Update this pattern when recipe contract versions, lifecycle steps, or execution metadata expectations change.
