# Worldgen

Milestone 1 now includes a functioning local-first prototype that can initialize a World Package, ingest synthetic sources, preserve provenance, extract candidate knowledge, build a deterministic SQLite index, and generate emergent organizational proposals.

## Core docs

- `docs/charter.md`
- `docs/architecture/personal-world-poc.md`
- `docs/development/adr-0001-world-foundation-decisions.md`
- `docs/data-contract-v1.md`

## Implementation highlights

- Canonical, versioned JSON contract for: World, Source, Observation, Entity, Relationship, Assertion, Evidence, Context, Proposal.
- World package initializer with local raw-source gitignore defaults.
- Idempotent ingestion with source content hashing and deterministic IDs.
- Source adapters:
  - ChatGPT export adapter (`conversations.json` style export)
  - Markdown repository adapter (for Hermes-style source repositories)
- Provenance-preserving observation/evidence/assertion pipeline.
- SQLite index rebuild from canonical files (`indexes/sqlite/world.db`).
- Two independent organizational proposal approaches:
  - token-frequency conceptual domains
  - relationship connected components
- CLI commands for init, ingest, validate, index, propose, and explore.

## Quickstart

```bash
python -m pip install -e .
worldgen init ./demo-world --name "Demo World" --description "Synthetic demo"
worldgen ingest ./demo-world chatgpt_export ./tests/fixtures/chatgpt_export --source-name "chatgpt fixture" --origin "fixture://chatgpt"
worldgen ingest ./demo-world markdown_repo ./tests/fixtures/hermes_repo --source-name "hermes fixture" --origin "fixture://hermes"
worldgen validate ./demo-world
worldgen index ./demo-world
worldgen propose ./demo-world
worldgen explore ./demo-world summary
worldgen explore ./demo-world assertions
worldgen explore ./demo-world proposals
worldgen review ./demo-world conflicts
```

## Testing

The test suite uses synthetic fixtures only:

```bash
PYTHONPATH=src python -m pytest
```

Coverage includes:

- Duplicate entity detection
- Alias handling
- Cross-source identity reconciliation
- Conflicting assertions
- Provenance preservation
- Repeated ingestion and idempotence
- Index rebuilding
- Organizational proposal generation
- Validation of malformed records