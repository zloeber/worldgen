# Initial Architecture Proposal: Personal World POC

## Purpose

This proposal defines the smallest architecture likely to test the central hypothesis: that a world representation can be progressively developed by agents without a predeclared ontology or directory taxonomy. It intentionally avoids building a full application. The goal is a reviewable, filesystem-native POC that can ingest real-world source material, preserve provenance, discover candidate organizational domains, and support human inspection before canonical changes are accepted.

## 1. Canonical Filesystem Structure

The canonical world should live in a stable, human-readable layout that is portable and Git-friendly. The filesystem is a storage mechanism, not the ontology itself.

```text
world/
  README.md                         # Purpose, conventions, developer guidance
  world.yaml                        # World metadata, identity, lifecycle state
  sources/
    manifests/
      source-<id>.yaml             # Source registration metadata
    raw/
      chatgpt/<source-id>/...      # Original exported material
      hermes/<source-id>/...        # Independent repo or project export
      other-ai/<source-id>/...
    excerpts/
      e-<id>.md                     # Source-derived excerpts with provenance
    ingest-log.jsonl               # Append-only ingest journal
  observations/
    obs-<id>.md                     # Normalized observations, unaccepted and traceable
  entities/
    entity-<id>.md                  # Canonical entity record with identity and aliases
  relationships/
    rel-<id>.md                     # Entity-to-entity relationships
  assertions/
    assertion-<id>.md               # Claims with confidence and status
  evidence/
    evidence-<id>.md                # Supporting evidence objects, source references, snippets
  contexts/
    context-<id>.md                 # Purpose-built views over selected world content
  proposals/
    proposal-<id>.md                # Candidate changes awaiting review
  ontology/
    domain-proposals/
      proposal-<id>.md             # Independent proposals for top-level organization
    clusters/
      cluster-<id>.md              # Discovered clusters and grouping notes
    schema/
      primitive-overview.md
  development/
    journal.md                      # Development decisions, findings, and open questions
    validation/
      report-<id>.md               # Deterministic validation reports
  indexes/
    sqlite/world.db                # Rebuildable SQLite index, not canonical truth
    search/
      fts.sqlite                   # Derived FTS index
  .gitignore
```

Key decisions:

- Keep a small, stable technical shell: `sources`, `entities`, `assertions`, and `proposals` are fixed. The conceptual domains are discovered inside `ontology/` or `contexts/`, not predetermined as top-level directories.
- Preserve raw source material and normalized observations separately. Raw evidence is never rewritten; the system increments by appending or creating new derived records.
- Use stable identifiers (`entity-<id>`, `obs-<id>`, etc.) independent from file paths so relationships and contexts can reference the same entity from multiple perspectives.
- Make indexes derived, not authoritative. SQLite and FTS data are rebuildable artifacts.

## 2. Source Ingestion Model

The ingestion model is deliberately layered to separate raw information from accepted world knowledge.

### 2.1 Source registration

Each source is registered with metadata before content is normalized:

- `source_id`
- `source_type` (`chatgpt`, `hermes`, `other_ai`, `repo`, `api`, etc.)
- `display_name`
- `origin_uri`
- `imported_at`
- `authority` and `confidence`
- `time_window` metadata
- `hash` or content fingerprint

This metadata should live in YAML frontmatter and/or a manifest file, with the original files retained under `sources/raw/`.

### 2.2 Observation pipeline

The flow is:

1. Preserve raw source material.
2. Create an `Observation` record for each significant chunk or event.
3. Attach provenance and timestamps.
4. Link the observation to one or more candidate entities or concepts.
5. Normalize into assertions only after human or machine review.

Observations are intentionally separate from canonical records. This means a source can be reprocessed or corrected without rewriting the original evidence chain.

### 2.3 Provenance model

Every canonical artifact should minimally carry:

- `id`
- `type`
- `created_at`
- `observed_at`
- `source_id`
- `source_reference`
- `confidence`
- `status` (`observed`, `interpreted`, `inferred`, `accepted`, `rejected`, `superseded`)
- `author` or `agent_id`
- `evidence_refs`

This ensures the world can explain why it believes something and where the claim came from.

### 2.4 Source-specific authority

Different sources have different weight:

- A direct user-authored note may be higher authority for personal preferences.
- A repository may be more authoritative for project structure.
- An AI conversation export may be more uncertain or more reflective in nature.

Authority is not collapsed into a single scalar; it is tracked as metadata so contradictions can be reviewed rather than silently resolved.

## 3. Foundational Data Primitives

The POC should begin with the smallest useful universal set. The important part is not the breadth of the schema, but the separation of concerns.

### Core primitives

- World: Top-level container with identity, scope, and lifecycle metadata.
- Entity: A distinct thing in the world (person, project, tool, idea, place, belief, system, etc.).
- Relationship: A connection between entities, with direction, strength, and evidence.
- Assertion: A factual or interpretive claim attached to an entity or relationship.
- Evidence: A quote, raw snippet, event, artifact, or document supporting an assertion.
- Context: A filtered, task-specific view over selected world facts.
- Source: The original origin of information.
- Observation: A discovered fact or event before it is accepted into the canonical world.
- Proposal: A candidate update to the canonical world awaiting review.

### Minimal metadata contract

Every primitive should have:

- stable `id`
- `kind`
- `status`
- `created_at`
- `updated_at`
- `source_refs`
- `confidence`
- `rejected_by` or `superseded_by` references when applicable

This is enough to support a human review workflow without premature abstraction.

### Important distinction to preserve

The data model must explicitly distinguish:

- what was observed,
- what was interpreted,
- what was inferred,
- what was proposed,
- what was accepted as canonical.

Without that distinction, the world drifts into unknowable assumptions.

## 4. Domain Discovery Process for Top-Level Organizational Structure

This is the riskiest and most important area of the POC.

### 4.1 Explicit objective

The system must not assume a fixed root taxonomy such as `people/`, `projects/`, `ideas/`, `systems/`. It must discover likely top-level domains from evidence.

### 4.2 Discovery pipeline

The proposed process is:

1. Extract entities, named concepts, project names, institutions, people, tools, and recurring themes from sources.
2. Build a relationship graph from co-occurrence, role references, and explicit statements.
3. Measure clustering signals: shared participants, recurring concepts, semantic similarity, co-mention patterns, and source agreement.
4. Generate several independent candidate root organizations from different heuristics.
5. Compare proposals for overlap, stability, blind spots, and ambiguity.
6. Present best candidates as `proposal-*` records for review.
7. Accept only reviewed, evidence-backed structural changes into the canonical world.

### 4.3 Candidate heuristics

The first implementation should test a few lightweight clustering approaches:

- co-occurrence graph clustering
- concept frequency + adjacency clustering
- entity community detection around people/projects
- source-anchored grouping (e.g., which concepts cluster together across ChatGPT and Hermes)

The first POC should not depend on a large LLM-generated taxonomy. Small deterministic heuristics are easier to inspect and validate.

### 4.4 Why this matters

A domain proposal is only useful if it improves retrieval, context compilation, and explanation. The architecture should therefore compare candidate structures based on their explanatory utility, not merely graph elegance.

### 4.5 Contact points with the filesystem

The root organization should remain emergent. We are not creating a conceptual taxonomy through folder names alone. The file system is a stable container for content, while the organization is expressed through discovered groupings, contexts, proposals, and indexes.

## 5. Smallest Architecture to Validate the Hypothesis

The POC can be built as four tightly scoped components:

### 5.1 World Package

- reads and writes canonical Markdown/YAML records
- maintains stable IDs and provenance
- supports Git-friendly review and diff

### 5.2 Ingestion Runtime

- registers sources
- preserves raw exports
- normalizes observations and evidence
- creates assertions and proposals
- indexes derived data into SQLite

### 5.3 Discovery Engine

- extracts entities and relationships
- clusters recurring concepts
- generates top-level domain proposals
- compares proposals for overlap and stability

### 5.4 Explorer / Review UI

- allows a human to inspect evidence
- review candidate domains and contradictions
- approve or reject changes
- compile bounded contexts for agent use

These are intentionally small boundaries. The architecture is designed to support a first human-readable experiment rather than a production graph platform.

## 6. Riskiest Assumptions

These are the assumptions most likely to fail and therefore deserve the smallest, fastest experiments:

1. Entity identity can be reconciled across independent sources without overfitting to a rigid schema.
2. Top-level world domains can be discovered from evidence rather than a predetermined taxonomy.
3. Human-readable canonical files are sufficient as the durable source of truth for early experimentation.
4. Source provenance can be preserved across normalization, indexing, and context compilation without becoming cumbersome.
5. The same discovered structure will help both humans and agents, not just one of them.
6. Candidate domain proposals will remain stable enough to justify review and acceptance.

## 7. Smallest Experiment to Validate the Hypothesis

Run a minimal POC using exactly three source classes:

- one ChatGPT export,
- one Hermes repository or umbrella project,
- one additional AI conversation export.

Procedure:

1. Initialize an empty world.
2. Register the three source manifests.
3. Ingest and preserve raw content without transformation.
4. Extract entities and claims from each source.
5. Run two independent clustering passes on the resulting relationship graph.
6. Generate domain proposals from each pass.
7. Compare them for overlap, missing topics, and contradictory grouping.
8. Have a human review the top proposals and confirm whether they are plausible.
9. Record the output and whether the proposals improved retrieval or context compilation.

What counts as success:

- the system produces at least two defensible candidate organic root structures,
- both are traceable to actual evidence,
- the proposals can be reviewed and revised,
- the resulting structure improves human understanding or agent context quality.

If all of these fail, the assumption that top-level structures emerge naturally from source data is not yet proven.

## 8. Suggested Tooling and Local Dev Setup

The project should prefer lightweight, local tooling:

- Python for the implementation language
- uv for package management
- mise for pinned toolchain management
- Taskfile for task execution
- SQLite for derived indexing
- Git for versioned changes and review
- Optional Ollama for local model inference
- Optional patternmaker integration for local dev pattern mapping when available

The repository should make these tools explicit in the project config rather than relying on ad hoc global setup.

## 9. Working Principles for the First Milestone

- Keep the canonical representation human-readable and portable.
- Treat the world as evidence-backed and reviewable.
- Separate raw source data, observations, assertions, and accepted knowledge.
- Prefer deterministic infrastructure for parsing and indexing.
- Use models only where ambiguity or synthesis is required.
- Make the world explainable and reviewable before it is considered meaningful.

## 10. Recommendation

The first milestone should not try to build a complete “knowledge graph product.” It should instead build a reviewable personal world that demonstrates:

- multiple source ingestion with provenance,
- entity reconciliation and contradiction tracking,
- emergent root-domain proposals,
- context compilation from evidence-backed world state,
- explicit human review before canonical acceptance.

If that small experiment succeeds, the architecture is ready to expand toward wider agent, repository, and organizational use cases.
