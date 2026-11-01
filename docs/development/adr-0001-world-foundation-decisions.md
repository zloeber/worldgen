# ADR 0001: Milestone 1 World Foundation Decisions

## Status

Accepted for Milestone 1 implementation.

## Context

Milestone 1 requires a local-first, filesystem-native prototype that preserves provenance, supports repeatable ingestion, and proposes emergent organization without imposing a rigid taxonomy.

The following foundational decisions were unresolved before implementation and needed concrete choices.

## Decision 1: Canonical record format

- **Choice:** Canonical records are JSON files (pretty printed, stable key order) grouped by kind-specific directories.
- **Why now:** JSON can be validated with the Python standard library and keeps contract enforcement deterministic while remaining human-readable and portable.
- **Tradeoff:** Less ergonomic for long-form authoring than Markdown frontmatter; acceptable for the prototype.

## Decision 2: Contract versioning approach

- **Choice:** All canonical records include `contract_version`, with initial version `1.0.0`.
- **Why now:** Enables explicit migration boundaries and deterministic validation across record kinds.
- **Tradeoff:** Requires migration tooling later when versions diverge.

## Decision 3: Raw source handling and Git defaults

- **Choice:** Raw imported sources are copied to `sources/raw/<source_id>/` inside the world package, and that subtree is gitignored by world-package initialization.
- **Why now:** Preserves immutable source material while minimizing accidental commits of personal exports.
- **Tradeoff:** Raw content is local by default and not collaboratively shared unless explicitly copied elsewhere.

## Decision 4: Idempotent ingestion strategy

- **Choice:** Source ingestion uses content hashing + deterministic IDs derived from source references and normalized text.
- **Why now:** Guarantees repeatable runs and safe reprocessing without duplicate canonical records.
- **Tradeoff:** Contract stability depends on deterministic normalization behavior.

## Decision 5: Indexing architecture

- **Choice:** SQLite index is derived and rebuildable from canonical JSON data at any time.
- **Why now:** Supports deterministic exploration and conflict checks while keeping canonical state filesystem-native.
- **Tradeoff:** Rebuild cost grows with corpus size; acceptable for prototype scope.

## Decision 6: Domain proposal discovery methods

- **Choice:** Implement two independent approaches:
  1. Token-frequency concept domains.
  2. Relationship graph connected components.
- **Why now:** Satisfies emergent-organization requirement with inspectable, deterministic heuristics.
- **Tradeoff:** Coarse early proposals; richer clustering can be introduced after validating baseline utility.

## Decision 7: Claim-state separation

- **Choice:** Keep Source, Observation, Assertion, Evidence, and Proposal as separate record kinds with explicit status fields.
- **Why now:** Prevents silent promotion of inferred information into accepted knowledge.
- **Tradeoff:** More files and joins to reason across, but much clearer governance and auditability.
