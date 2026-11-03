# Worldgen Agent Entry Point

Worldgen builds a **local-first, filesystem-native** world model with deterministic ingestion, explicit provenance, and human-governed acceptance of knowledge.

Before any change:
1. Read `.mex/ROUTER.md`.
2. Read `.mex/continuity/CURRENT.md`.
3. Inspect relevant implementation and tests directly.

Working rules:
- Treat implemented behavior in `src/` and `tests/` as authoritative over proposals.
- Distinguish clearly between implemented behavior, accepted decisions, and future proposals.
- Document meaningful architectural or workflow changes in `.mex/context/*`, continuity files, and ADRs when needed.
- Do not rewrite durable decisions silently; surface conflicts explicitly.

Project context, patterns, decisions, and development continuity live under `.mex/`.
