# Worldgen Current Development Snapshot

## Current milestone and objective

Milestone 1 implementation baseline is active. Current objective is to evolve implementation safely while preserving local-first determinism, provenance boundaries, and recipe/contract integrity.

## Current implementation state

- World package initialization, source ingestion, validation, indexing, and proposal generation are implemented.
- Recipe system is implemented for catalog/contract/composition with three implemented recipes (`seed-foundation`, `ingest-source`, `discover-domains`) and planned placeholders for others.
- Click CLI supports world operations and recipe lifecycle commands.
- The project builds and installs with uv (`uv sync`, `uv build`) using hatchling.
- ChatGPT ingestion accepts a directory, conversation JSON, split conversation files, or a zip export and validates afterwards.
- Optional LiteLLM interpretation can target an Ollama server. It is off unless a model is configured.

## Recently completed work

- Added repository-native development scaffold: root `AGENTS.md`, `.pattern` router/context/patterns/continuity, and `worldgen-development` skill.
- Added ADR 0002 documenting development-context governance and recipe-system boundary decision.

## Active architectural decisions

- ADR 0001: Milestone 1 foundation decisions (canonical format, idempotent ingest, derived index, proposal boundaries).
- ADR 0002: Lightweight development memory scaffold; no Patternmaker runtime dependency; development bootstrap remains a skill/workflow concern.
- ADR 0003: Click CLI, uv packaging, real ChatGPT export layouts, and optional LiteLLM interpretation. Default ingest stays deterministic.

## Known limitations

- Multi-file recipe mutations are not yet transactional.
- Identity resolution remains heuristic and conservative.
- Planned model-assisted recipes other than optional ingest interpretation are not implemented.

## Open questions

- How to stage/commit multi-file recipe writes safely while staying filesystem-native?
- Which reconciliation recipe (`reconcile-claims` vs. identity improvements) should be prioritized next?

## Immediate next steps

1. Implement `reconcile-claims` recipe with explicit conflict/supersession proposal outputs.
2. Add staged-write strategy for recipe mutation safety.
3. Expand decision/pattern coverage only as new implementation evidence appears.

## Reference links

- Source: `src/worldgen/`
- Tests: `tests/`
- ADRs: `docs/development/`
- Recipes: `docs/world-development-recipes.md`
- Charter: `docs/charter.md`
