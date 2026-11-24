# Worldgen Roadmap Snapshot

## Current milestone

Milestone 1 baseline is implemented: world initialization, ingestion, validation, indexing, proposal generation, and first-class recipe definitions/executions.

## Near-term priorities

1. Implement next planned recipes with high leverage (`reconcile-claims`, then `identify-gaps`).
2. Strengthen mutation safety for multi-file recipe operations (staged/atomic write approach).
3. Improve identity and conflict reconciliation beyond normalized-label heuristics.
4. Expand deterministic validation and review flows for proposal acceptance.

## Known unresolved areas

- Transaction-like handling for multi-file mutations.
- Richer execution/index visibility for larger worlds.
- Human review flow details for model-assisted planned recipes.

## Out of scope for current architecture

- Mandatory external services.
- Heavy runtime orchestration/workflow infrastructure.
- Patternmaker runtime coupling.
