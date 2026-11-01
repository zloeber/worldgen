# Worldgen is the project charter and initial architecture proposal for a local-first Personal World POC.

## Included

- `docs/charter.md` — the full project development charter
- `docs/architecture/personal-world-poc.md` — the initial architecture proposal focused on canonical filesystem structure, ingestion, primitives, and emergent domain discovery
- `.mise.toml` — binary/tool management via mise
- `Taskfile.yml` — project task runner and validation commands

## Local tooling

This repository intentionally uses:

- `mise` for tool version management
- `task` for project tasks
- optional `patternmaker` integration for local pattern mapping

Use `task` to inspect available project commands and validate the repo configuration.