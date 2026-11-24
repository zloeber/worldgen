# Worldgen

Milestone 1 now includes a functioning local-first prototype that can initialize a World Package, ingest synthetic sources, preserve provenance, extract candidate knowledge, build a deterministic SQLite index, and generate emergent organizational proposals.

## Core docs

- `docs/charter.md`
- `docs/architecture/personal-world-poc.md`
- `docs/development/adr-0001-world-foundation-decisions.md`
- `docs/development/adr-0002-development-context-scaffold.md`
- `docs/data-contract-v1.md`
- `docs/world-development-recipes.md`

## Development orientation

Worldgen now includes a lightweight repository-native development scaffold:

- Root entrypoint: `AGENTS.md`
- Project router: `.pattern/ROUTER.md`
- Focused context and decision index: `.pattern/context/`
- Evidence-backed patterns: `.pattern/patterns/`
- Development continuity: `.pattern/continuity/`
- Reusable workflow skill: `.agents/skills/worldgen-development/SKILL.md`

This scaffold is inspired by Patternmaker concepts and adapted for Worldgen's existing architecture without introducing external runtime dependencies.

## Implementation highlights

- Canonical, versioned JSON contract for: World, Source, Observation, Entity, Relationship, Assertion, Evidence, Context, Proposal.
- World package initializer with local raw-source gitignore defaults.
- Idempotent ingestion with source content hashing and deterministic IDs.
- Source adapters:
  - ChatGPT export adapter for a directory, `conversations.json`, split `conversations-*.json` files, or a data-export zip
  - Markdown repository adapter (for Hermes-style source repositories)
- Provenance-preserving observation/evidence/assertion pipeline.
- SQLite index rebuild from canonical files (`indexes/sqlite/world.db`).
- Two independent organizational proposal approaches:
  - token-frequency conceptual domains
  - relationship connected components
- Click CLI commands for init, ingest, validate, index, propose, and explore.
- Optional LiteLLM interpretation during ingest, including an Ollama server on the network. Ingestion stays deterministic when no model is configured.
- First-class filesystem-native recipe definitions and execution history (`recipes/definitions`, `recipes/executions`).
- Recipe CLI for discovery, composition, execution, and history inspection.

## Quickstart

```bash
uv sync
uv run worldgen init ./demo-world --name "Demo World" --description "Synthetic demo"
uv run worldgen ingest ./demo-world chatgpt_export ./tests/fixtures/chatgpt_export --source-name "chatgpt fixture" --origin "fixture://chatgpt"
uv run worldgen ingest ./demo-world markdown_repo ./tests/fixtures/hermes_repo --source-name "hermes fixture" --origin "fixture://hermes"
uv run worldgen validate ./demo-world
uv run worldgen index ./demo-world
uv run worldgen propose ./demo-world
uv run worldgen explore ./demo-world summary
uv run worldgen explore ./demo-world assertions
uv run worldgen explore ./demo-world proposals
uv run worldgen review ./demo-world conflicts
uv run worldgen recipe list ./demo-world
uv run worldgen recipe compose ./demo-world discover-domains
uv run worldgen recipe run ./demo-world seed-foundation --inputs-json '{"perspective":"personal","purpose":"Build a traceable world","boundaries":["fixtures"],"principles":["evidence always"],"discovery_agenda":["ingest and reconcile"]}'
uv run worldgen recipe run ./demo-world ingest-source --inputs-json '{"source_type":"chatgpt_export","source_name":"chatgpt fixture","source_path":"./tests/fixtures/chatgpt_export","origin":"fixture://chatgpt"}'
uv run worldgen recipe history ./demo-world
```

A ChatGPT data export can be a directory, a `conversations.json` file, split `conversations-*.json` files, or the original `.zip`. Text is kept from message parts, code, and user context. Image-only parts are skipped. Unix timestamps are stored as UTC date-times.

## Packaging

```bash
uv sync
uv build
```

`uv build` writes an sdist and wheel under `dist/`. The `worldgen` console script points at the Click command group.

## Optional model interpretation

Parsing a ChatGPT export does not require a model. To ask LiteLLM for additional candidate entities and assertions, pass a model and, when needed, the server URL. For Ollama on another machine:

```bash
uv run worldgen ingest ./demo-world chatgpt_export ./chatgpt-export.zip \
  --source-name "ChatGPT export" \
  --origin "export://chatgpt" \
  --model ollama/llama3.1 \
  --model-api-base http://192.168.1.20:11434
```

`WORLDGEN_MODEL` and `WORLDGEN_MODEL_API_BASE` provide the same values. When the API base flag is omitted, `OLLAMA_API_BASE` is used. Interpretations are stored as candidate or conflicting assertions with `interpretation_level` set to `interpretation`. They are not accepted automatically. The same model and server are not called again while the source bytes are unchanged.

## Testing

The test suite uses synthetic fixtures only:

```bash
uv run pytest
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