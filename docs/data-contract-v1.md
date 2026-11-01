# Worldgen Data Contract v1.0.0

This contract defines the minimum canonical record structure for Milestone 1.

## Shared required fields

All record kinds must include:

- `id` (stable identifier)
- `kind` (one of: World, Source, Observation, Entity, Relationship, Assertion, Evidence, Context, Proposal)
- `contract_version` (`1.0.0` for this milestone)
- `created_at` (ISO-8601 UTC timestamp)
- `status` (lifecycle state, kind-specific but explicit)

## Kind-specific required fields

| Kind | Required fields |
|---|---|
| World | `name`, `description` |
| Source | `source_type`, `display_name`, `origin`, `content_hash` |
| Observation | `source_id`, `source_reference`, `content`, `observed_at` |
| Entity | `label`, `normalized_label`, `aliases` |
| Relationship | `from_entity_id`, `to_entity_id`, `relationship_type`, `evidence_ids` |
| Assertion | `subject_entity_id`, `predicate`, `object_text`, `evidence_ids`, `interpretation_level` |
| Evidence | `source_id`, `source_reference`, `excerpt`, `observed_at` |
| Context | `title`, `entity_ids`, `assertion_ids` |
| Proposal | `title`, `proposal_type`, `approach`, `evidence_ids`, `body` |

## Interpretation levels

Assertions use one of:

- `source_claim`
- `interpretation`
- `inference`
- `accepted`

Milestone 1 does not auto-promote to `accepted`.
