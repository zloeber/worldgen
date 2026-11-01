# World Development Recipes (Milestone Contract)

World Development Recipes are now a first-class, filesystem-native capability in Worldgen.

- **Recipe definitions:** `recipes/definitions/<recipe-id>@1.0.0.json`
- **Execution history:** `recipes/executions/recipe-exec-<id>.json`

Recipe definitions and recipe executions are distinct artifacts so the capability contract and each run can be inspected independently.

## 1) Recipe contract (`version: 1.0.0`)

Each recipe definition includes:

- Stable identifier and version (`id`, `version`)
- Name and purpose (`name`, `purpose`)
- Inputs and prerequisites (`inputs.required`, `inputs.optional`, `prerequisites`)
- Expected outputs (`outputs`)
- Applicable record kinds (`applicable_record_kinds`)
- Deterministic operations (`deterministic_operations`)
- Model-assisted operations (`model_assisted_operations`)
- Validation requirements (`validation_requirements`)
- Evidence and provenance requirements (`evidence_and_provenance_requirements`)
- Side effects and mutations (`side_effects_and_mutations`)
- Human review governance (`human_review_requirements`)
- Execution metadata requirements (`execution_metadata_requirements`)
- Reproducibility expectations (`reproducibility`)
- Composition dependencies (`depends_on`)
- Implementation status (`implemented` or `planned`)

## 2) Recipe execution record contract (`execution_contract_version: 1.0.0`)

Each execution record includes:

- Execution identity and resolved recipe version (`execution_id`, `recipe_id`, `recipe_version`)
- Link to definition (`recipe_definition_path`)
- Lifecycle status and timestamps (`status`, `started_at`, `completed_at`)
- Input snapshot (`inputs`)
- Outputs (`outputs`)
- Lifecycle step statuses (`lifecycle`)
- Side effects as proposed/observed file mutations (`proposed_mutations`)
- Failure and unresolved data (`failure`, `warnings`, `unresolved_questions`)
- Runtime metadata (`runtime.deterministic_operations`, `runtime.model_assisted_operations`, `runtime.model_metadata`)
- Reproducibility metadata (`reproducibility.input_fingerprint`, contract versions, deterministic flag)

Lifecycle steps follow:

1. resolve recipe version
2. inspect prerequisites and state
3. gather inputs
4. execute operations
5. validate outputs
6. record results and provenance
7. generate proposals or changes
8. report warnings and opportunities

Failed executions record the failure and skipped steps; they do not silently promote inferred outputs.

## 3) Initial recipe catalog

The catalog includes:

- `seed-foundation` (**implemented**)
- `evaluate-foundation` (planned)
- `ingest-source` (**implemented**)
- `reconcile-source` (planned)
- `resolve-identities` (planned)
- `discover-relationships` (planned)
- `reconcile-claims` (planned)
- `discover-domains` (**implemented**)
- `identify-gaps` (planned)
- `compile-context` (planned)
- `evaluate-world` (planned)

## 4) Mapping current POC functionality to recipes

| Existing capability | Current command/function | Recipe mapping |
|---|---|---|
| World initialization | `worldgen init` / `init_world` | Enables recipe substrate; seeds recipe catalog |
| Foundation seeding | `worldgen recipe run ... seed-foundation` | `seed-foundation` |
| Source registration + ingest | `worldgen ingest` / `ingest_source` | `ingest-source` |
| Candidate domain proposals | `worldgen propose` / `generate_domain_proposals` | `discover-domains` |
| Contract validation | `worldgen validate` / `validate_world` | deterministic validation stage for all recipes |
| Index rebuild + inspection | `worldgen index`, `explore`, `review` | post-recipe inspection and review surfaces |

## 5) Composition and discovery

- Recipe discovery: `worldgen recipe list <world-path>`
- Dependency composition: `worldgen recipe compose <world-path> <recipe-id>...`
- Execution with dependency inclusion: `worldgen recipe run <world-path> <recipe-id> --include-dependencies`

Composition is dependency-ordered and intentionally simple (no workflow engine).

## 6) Canonical records vs proposals

- Recipes may update canonical records when the input is explicit and deterministic (for example `seed-foundation`).
- Recipes generating interpretive or organizational outcomes should prefer proposals (`Proposal`) and candidate statuses over silent promotion.
- Existing ingestion behavior remains aligned with this principle: assertions/relationships/entities are created as `candidate`/`conflicting` states, not auto-accepted.

## 7) Implemented milestone changes

- Added `src/worldgen/recipes.py`:
  - recipe catalog definition
  - contract validation
  - composition helper
  - execution lifecycle recording
  - implemented runners for `seed-foundation`, `ingest-source`, and `discover-domains`
- Updated world initialization:
  - creates `recipes/definitions` and `recipes/executions`
  - seeds catalog definitions on init
- Updated world validation:
  - requires recipe directories
  - validates recipe catalog definitions and dependencies
- Extended CLI:
  - `worldgen recipe list`
  - `worldgen recipe compose`
  - `worldgen recipe run`
  - `worldgen recipe history`

## 8) Architectural conflicts and unresolved decisions

- **Atomicity for multi-file recipe mutations:** current implementation records failures and mutation paths, but does not implement transactional rollback for partially written files. A next step is staged writes with commit/abort semantics.
- **Execution ordering visibility:** history is persisted per execution record, but not additionally indexed; this is acceptable for filesystem-native scope, but could later use a derived index table.
- **Model metadata policy:** contract supports model metadata capture, but model-assisted recipe implementations are still planned.

## 9) Recommendation for next recipe implementation

Implement **`reconcile-claims`** next.

It directly builds on already-ingested assertions and evidence, strengthens conflict/supersession lineage, and provides high leverage for both `identify-gaps` and `evaluate-world`.

