---
name: worldgen-development
description: Orient on Worldgen implementation and decisions, then execute changes with evidence-backed continuity updates.
---

# worldgen-development

Use this workflow to perform substantial Worldgen repository work without drifting from implemented behavior or accepted decisions.

## Scope

- Repository development workflow for `worldgen` itself.
- Not a World Package recipe and not a runtime feature of `src/worldgen`.

## Workflow

1. **Orient**
   - Read `AGENTS.md` then `.mex/ROUTER.md`.
   - Read `.mex/continuity/CURRENT.md`.
   - Load only relevant files from `.mex/context/`, `.mex/patterns/`, `src/worldgen/`, `tests/`, and ADRs.

2. **Ground in implementation**
   - Inspect actual source and tests before editing.
   - Treat implemented behavior and tests as authoritative over proposals.

3. **Check decisions and conventions**
   - Confirm alignment with `.mex/context/conventions.md` and `.mex/context/decisions.md`.
   - If the change conflicts with an accepted ADR, explicitly surface and document the conflict.

4. **Apply and verify**
   - Implement focused changes.
   - Run full test suite (`PYTHONPATH=src python -m pytest`) unless the work is docs-only.
   - Avoid silent behavior shifts; update tests when behavior intentionally changes.

5. **Maintain development knowledge**
   - Update `.mex/continuity/CURRENT.md` after substantial work.
   - Append durable milestones/decisions to `.mex/continuity/DEVELOPMENT.md`.
   - Update context/pattern files only when supported by current repository evidence.

6. **Report outcome**
   - Summarize implemented changes, decisions made, unresolved questions, and follow-up work.

## Guardrails

- Do not auto-rewrite durable architectural decisions.
- Do not create broad generic patterns without repository evidence.
- Keep guidance concise; link to source-of-truth documents rather than duplicating them.

## Attribution

This workflow adapts ideas from `zloeber/patternmaker` (MIT License) for Worldgen’s local-first architecture and recipe boundaries, without introducing any Patternmaker runtime dependency.
