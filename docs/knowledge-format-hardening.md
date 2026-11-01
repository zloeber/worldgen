# Worldgen knowledge format hardening

## Scope

This memo documents the Milestone 1 hardening work for the canonical world package. The goal is to preserve the charter’s local-first, portable, evidence-backed model without introducing an RDF database or an enterprise graph platform.

## 1. Open format and interoperability

### Canonical JSON remains the durable source of truth

The charter explicitly requires the canonical representation to be portable, human-readable, Git-friendly, and independent of any specific vendor or agent. Human-readable JSON remains a fit for Milestone 1. The implementation keeps the canonical records as files on disk and treats SQLite only as a derived, rebuildable index.

### JSON-LD compatibility

A lightweight mapping is sufficient for interoperability without forcing a graph database into the system:

- `id` maps to `@id`
- `kind` maps to `@type`
- `created_at` maps to `prov:generatedAtTime`
- `observed_at` maps to `prov:atTime`
- `source_id` and `source_reference` remain worldgen-specific metadata fields
- `relationship_type`, `predicate`, `object_text`, and `interpretation_level` remain as stand-alone semantic properties
- `aliases`, `evidence_ids`, `entity_ids`, and `assertion_ids` remain arrays of identifiers rather than hidden graph edges

This is compatible with JSON-LD tooling and still preserves the canonical file model. It does not require an RDF data store.

### W3C PROV-O

PROV-O is a good fit for provenance semantics. The key W3C concepts that map cleanly to Worldgen are:

- `prov:Entity` for Evidence and Source artifacts
- `prov:Activity` for ingestion and reprocessing events
- `prov:Generation` for source observations and derived assertions
- `prov:wasDerivedFrom` for evidence inheritance and chain-of-custody
- `prov:atTime` for observed times
- `prov:generatedAtTime` for recording times

Worldgen-specific distinctions that do not map 1:1 to PROV-O are:

- `interpretation_level` (`source_claim`, `interpretation`, `inference`, `accepted`)
- `relationship_basis` (`explicit`, `co_occurrence`, `inferred`)
- `identity_proposal_ids` and `canonical_entity_id`
- proposal and context lifecycle semantics

These remain part of the canonical schema because the charter explicitly requires separate treatment for observation, interpretation, inference, and accepted knowledge.

### Primitive representation without RDF infrastructure

The current primitives map well to a JSON document model:

- World: container/manifest
- Entity: node-like record with aliases and identity metadata
- Relationship: typed link with explicit versus inferred basis
- Assertion: claim record with provenance and evidence
- Evidence: source-backed quote or artifact
- Source: original origin plus hash/version metadata
- Observation: raw extracted fact tied to a source
- Proposal: reviewable candidate change
- Context: purpose-built projection over entities and assertions

These preserve their distinctions in canonical JSON and can be serialized to JSON-LD without losing meaning.

## 2. Strengthened data contract

The implementation now validates all canonical records with formal JSON Schemas, enforces required fields, and checks referential integrity across records. This covers:

- type validation
- enum validation
- ISO-8601 timestamps
- required fields per kind
- duplicate record IDs
- referential integrity for entity, evidence, context, and assertion links
- contract version enforcement

Backward compatibility policy:

- `contract_version` remains `1.0.0` for this milestone
- migrations are explicit and document-based when a new version is introduced
- existing canonical records remain readable as long as they satisfy the contract and the version declaration

## 3. Evidence and provenance improvements

Key enforcement in the implementation:

- source-backed evidence objects are created per observation
- assertion records keep evidence references and source lineage
- relationships are marked with `relationship_basis` to distinguish explicit from co-occurrence/inferred links
- proposal records include evidence references and explicit candidate metadata
- accepted knowledge is not silently promoted from raw inference; interpretation levels remain explicit

This matches the charter’s requirement that inferred information must not be silently promoted into accepted knowledge.

## 4. Identity and temporal semantics

Model improvements include:

- identity metadata on entity records: `canonical_entity_id` and `identity_proposal_ids`
- separate handling for alias metadata without auto-merging purely by normalized name
- `recorded_at` / `observed_at` / `valid_from` / `valid_until` semantics for temporal records
- source versioning via source metadata and content hashes
- a path for reprocessing and supersession without discarding historical provenance

The current prototype still uses a deterministic normalized-name key for entity IDs. That is a pragmatic implementation choice for the POC, but it must not be treated as a definitive identity resolution policy. Ambiguous matches still need proposal-based review rather than automatic merge.

## 5. Emergent organization and discovery

The proposal generation remains deliberately separate from filesystem structure. The canonical package has a small stable shell, while conceptual domains and clusters are expressed in proposal records and context projections. This preserves the charter’s separation between conceptual organization and physical structure.

The proposal payload now includes:

- candidate domain descriptions
- included entities
- supporting relationships
- supporting evidence
- source distribution
- ambiguous or excluded entities
- overlapping memberships
- alternative interpretations

## 6. Demonstration and interoperability

The repository includes a synthetic-world workflow that can generate canonical JSON, validate it, convert it to a JSON-LD-compatible document, and rebuild the SQLite index from canonical records. This demonstrates portability and round-trip stability without introducing infrastructure beyond the local SQLite index.

## 7. Implementation findings

### Validated assumptions

- Human-readable canonical JSON is sufficient for a portable, reviewable POC.
- SQLite is a valid derived index rather than the source of truth.
- Source provenance can be tracked through manifests, observation records, and evidence references.
- Domain proposals can be generated from multiple independent heuristics.

### Conflicts with the charter

- The initial version still shortens identity resolution into deterministic normalized-name keys; this is acceptable for small experiments but not a final identity policy.
- Some generated relationships are still treated as co-occurrence without strong semantic qualification; they need explicit human review when promoted.
- Proposal evidence is now strengthened, but an explicit review workflow would be the next improvement.

### Standards worth adopting

- JSON Schema 2020-12 for canonical validation
- JSON-LD for export compatibility and Linked Data interop
- PROV-O for provenance semantics, especially as a metadata vocabulary layer

### Worldgen-specific remains

- proposal-first ontology discovery
- context-driven interpretation
- emergent domain discovery rather than fixed folder taxonomy
- evidence + interpretation level separation
- local-first, filesystem-native portability

### Deferred to after the POC

- enterprise-scale graph reasoning
- global ontology governance
- heavyweight RDF storage
- broad identity resolution across heterogeneous sources
- productionized UI and workflow tooling

## 8. Summary

The Milestone 1 prototype remains aligned with the charter’s overall direction: a local-first, portable, evidence-backed world model. The improvements in this patch strengthen the canonical contract, provenance semantics, and interoperability story without expanding the system into a broader ontology or platform.
