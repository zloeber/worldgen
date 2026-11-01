# Worldgen — Project Development Charter

## 1. Mission

Build a local-first, agent-developed representation of an environment that progressively develops an understanding of the world it represents.

Worldgen explores how multiple independent sources of information—conversations, documents, repositories, APIs, memory systems, and human interaction—can be reconciled into a persistent, evolving, inspectable model of an environment.

The initial experiment is a Personal World: a representation of one person's life, interests, relationships, projects, ideas, decisions, preferences, and working environment, developed from years of accumulated information across multiple AI systems.

The long-term ambition extends beyond personal knowledge. The same architecture should be capable of representing organizations, teams, technical environments, businesses, projects, and other complex domains.

The central hypothesis:

A useful model of an environment can be progressively developed by agents without requiring a human to define its ontology or organizational structure in advance.

## 2. Core Philosophy

Three concepts define the system:

- World: The persistent representation of everything the system knows or represents about an environment.
- Context: A meaningful, purpose-driven view into the world, assembled from relevant entities, relationships, evidence, constraints, and history.
- Development: The ongoing process through which the world is observed, interpreted, reconciled, enriched, and improved.

Guiding principle:

> The world is the substrate. Contexts are how we make sense of it. Development is how it grows.

Additional principles:

1. Ontology-light, not ontology-less. Begin with minimal universal primitives and allow useful concepts and schemas to emerge.
2. Discover before organizing. Do not impose conventional knowledge-management categories or a rigid folder hierarchy.
3. Evidence before assertion. Preserve the origin and confidence of information.
4. Separate observation, interpretation, inference, and accepted knowledge.
5. Never silently promote an agent's assumption into an established fact.
6. Prefer deterministic machinery over repeated inference wherever possible.
7. Use inference for ambiguity, interpretation, discovery, and synthesis.
8. Preserve human inspectability, explainability, and governance.
9. The canonical representation must be portable, human-readable, and independent of any particular agent.
10. Multiple agents and systems should be able to contribute to and consume the same world.
11. Avoid unnecessary infrastructure and premature enterprise complexity.
12. The system must be able to explain what it knows, why it believes it, what remains uncertain, and how its understanding has changed.

## 3. What Worldgen Is Building

Worldgen consists of several related architectural components.

### World Package

The canonical, portable representation of a world.

It should be:
- Filesystem-native.
- Human-readable.
- Git-friendly.
- Portable between machines and runtimes.
- Independent of any specific LLM, agent, database, or vendor.
- Rebuildable and inspectable.

Explore Markdown with YAML frontmatter, YAML documents, and JSONL journals as foundational formats.

SQLite and other indexes should be derived, rebuildable representations rather than the sole source of truth.

### World Runtime

The machinery that reads, develops, validates, navigates, and compiles a world.

Responsibilities include:
- Source ingestion.
- Extraction and interpretation.
- Entity identity and resolution.
- Relationship discovery.
- Assertion and evidence management.
- Reconciliation and contradiction detection.
- Ontology discovery and evolution.
- Context compilation.
- Development history.
- Validation and controlled commits.
- CLI, API, and MCP interfaces.

### World Explorer

A human-facing interface for understanding and governing a world.

Explore:
- Entity and relationship navigation.
- Evidence inspection.
- Context exploration.
- Candidate ontology review.
- Organizational structure discovery.
- Contradiction and uncertainty review.
- Proposed changes and development history.

The Explorer should help people understand the model, not merely visualize a graph.

## 4. Foundational Data Model

Start with the smallest useful set of universal primitives.

Candidate primitives:

- World
- Entity
- Relationship
- Assertion
- Evidence
- Context
- Source
- Observation
- Proposal

Do not overdesign this model before testing it against actual source material.

Important distinctions:

Entity: Something represented in the world.

Relationship: A connection between entities.

Assertion: A claim about an entity or relationship.

Evidence: The material supporting an assertion.

Source: The origin of evidence, such as a conversation, repository, document, or API.

Observation: Information discovered through interaction or ingestion.

Proposal: A candidate change to the canonical world.

Context: A purpose-driven selection and interpretation of parts of the world.

Support temporal information where appropriate:
- When something was observed or said.
- When something was believed to be true.
- When the system learned about it.

Preserve distinctions between:
- User-provided information.
- External source information.
- Agent-generated interpretations.
- Inferences.
- Accepted canonical knowledge.

## 5. Ontology and Organizational Discovery

This is one of the most important research and implementation areas.

Do not prescribe top-level world folders, domains, entity categories, or relationship taxonomies in advance.

The system should progressively discover useful organizational structures through the development process.

For example, ingestion of personal information might reveal:
- People and relationships.
- Family and personal life.
- Professional responsibilities.
- Projects and initiatives.
- Technical systems.
- Interests and knowledge domains.
- Ideas and philosophies.
- Goals and aspirations.

These are examples, not a predefined taxonomy.

The system should be able to:
1. Identify recurring concepts and entities.
2. Discover clusters and natural groupings.
3. Identify overlapping domains.
4. Propose candidate organizational structures.
5. Explain the evidence supporting each proposal.
6. Identify ambiguous boundaries and alternative structures.
7. Reconcile overlapping or conflicting classifications.
8. Formalize useful concepts into reusable schemas.
9. Revise its organizational structure as the world develops.

### Filesystem organization

Explore a hybrid approach:

- Keep a small, stable technical filesystem structure.
- Allow conceptual domains and organizational structures to emerge within the world.
- Do not assume that filesystem directories must represent the complete conceptual organization.
- Avoid duplicating entities merely because they belong to multiple contexts.
- Use stable identifiers independent of file paths.
- Allow multiple contexts and projections to reference the same entities.

Treat the filesystem as a storage and portability mechanism, not the definition of the ontology.

## 6. World Development Lifecycle

The runtime should support a repeatable development process:

1. Observe.
2. Interpret.
3. Discover.
4. Reconcile.
5. Propose.
6. Validate.
7. Commit.
8. Reflect.

Development recipes should eventually support operations such as:
- Discover entities.
- Resolve identities.
- Discover relationships.
- Enrich existing entities.
- Identify contradictions.
- Identify missing information.
- Discover conceptual clusters.
- Propose organizational structures.
- Propose ontology changes.
- Compile contexts.
- Reflect on world quality and completeness.

The system should distinguish between discovering information and accepting it into the canonical model.

Support reviewable changes, provenance, and version history.

## 7. Source Ingestion and Integration

Worldgen must support multiple independent information sources.

Initial sources for the Personal World POC:

### ChatGPT
An exported archive of conversations and accumulated user context.

### Other AI systems
Conversation exports from other assistants and systems.

### Hermes
An existing personal Hermes agent and its associated umbrella-style repository.

This repository already contains structured information about:
- Projects.
- Ideas.
- Relationships.
- Working practices.
- Technical environments.
- Decisions.
- Ongoing initiatives.

Treat it as an independent knowledge source, not as the canonical definition of the World.

### Future sources
- Markdown and YAML repositories.
- Git repositories.
- MemPalace.
- APIs.
- MCP servers.
- Documents.
- Other agent memory systems.

### Ingestion requirements

Preserve original sources and their identities.

Do not flatten all sources into untraceable text.

Support:
- Source metadata.
- Original timestamps.
- Stable source references.
- Incremental ingestion.
- Duplicate detection.
- Reprocessing.
- Provenance.
- Source-specific confidence and authority.

Treat imported information as evidence, not automatically accepted truth.

## 8. MemPalace Integration

Explore MemPalace as a complementary episodic-memory system.

Conceptual separation:

- MemPalace remembers what happened.
- World represents what those experiences tell us about the environment.

MemPalace may provide:
- Conversation histories.
- Memories and events.
- Palaces, wings, and rooms.
- Historical timelines.
- Semantic retrieval.
- Memory-based entity relationships.

Do not recreate MemPalace functionality unnecessarily.

Do not assume that its palace, wing, or room structure should map directly to World filesystem directories.

Instead, investigate how World entities, assertions, and evidence can reference MemPalace records.

Build an adapter using supported interfaces rather than depending on internal database implementation details.

## 9. Agent Integration

Worldgen must be agent-agnostic.

Hermes is an important initial integration, but the architecture should eventually support other agents and tools.

Provide a small, deliberate interface.

Candidate operations:

- world_search
- world_get
- world_explore
- world_compile
- world_observe
- world_propose
- world_commit
- world_history
- world_validate

Agents should be able to:
- Retrieve relevant world information.
- Explore relationships.
- Compile task-specific contexts.
- Record observations.
- Submit proposed updates.
- Inspect evidence.
- Understand uncertainty.
- Review development history.

Agents should not need to load the entire world into their context windows.

### Context compilation

This is a central runtime capability.

Given a task or intent, compile a bounded, agent-ready context containing relevant:
- Entities.
- Relationships.
- Decisions.
- Constraints.
- Evidence.
- Historical information.
- Unknowns.
- Dependencies.
- Relevant contexts.

The compiler should be able to explain why particular information was included.

## 10. Initial Technical Direction

Prefer a simple, local-first implementation.

Candidate starting stack:

| Area | Initial direction |
|---|---|
| Language | Python |
| Package management | uv |
| Local inference | Ollama or compatible model server |
| Canonical data | Markdown, YAML, JSONL |
| Structured indexing | SQLite |
| Search | SQLite FTS initially |
| Vector search | Optional, only when justified |
| Agent interface | CLI and MCP |
| UI | Lightweight local web application |
| Versioning | Git |

Do not treat this as a fixed technology mandate. Evaluate alternatives where there is a clear reason.

Prefer deterministic code for:
- Parsing.
- Validation.
- Identity management.
- Persistence.
- Indexing.
- Graph traversal.
- Reconciliation rules where deterministic resolution is possible.

Use models for:
- Interpretation.
- Semantic extraction.
- Ambiguous identity resolution.
- Relationship discovery.
- Conceptual clustering.
- Ontology suggestions.
- Contradiction analysis.
- Synthesis.

Avoid introducing distributed databases, complex orchestration platforms, or elaborate infrastructure prematurely.

## 11. The Initial Proof of Concept

The first milestone is a Personal World developed from multiple existing sources.

The POC should demonstrate that Worldgen can develop a coherent and useful representation of a person from independently maintained sources.

### Initial experiment

1. Initialize an empty Personal World.
2. Import a ChatGPT export.
3. Import the Hermes umbrella repository.
4. Import at least one additional AI conversation export.
5. Preserve all source material and provenance.
6. Extract candidate entities, assertions, relationships, and concepts.
7. Discover potential conceptual clusters and organizational structures.
8. Identify duplicate entities and conflicting assertions.
9. Generate candidate top-level organizational structures.
10. Present the proposals for inspection.
11. Allow reviewed changes to be committed into the canonical World.
12. Compile useful contexts from the resulting World.

### Questions the POC must answer

- What projects am I developing?
- What ideas connect those projects?
- How have my ideas and decisions evolved?
- Which people are connected to which initiatives?
- What do different systems know about me?
- Where do my sources disagree?
- What information exists in one source but not another?
- What recurring preferences and principles can be supported by evidence?
- What are the natural conceptual domains of this world?
- How should the world organize itself?
- What information is missing?
- Can the system explain why it believes something?

### Special experiment: Emergent root structure

Make the discovery of top-level organizational structure an explicit POC objective.

Compare independently generated organizational proposals.

Explore whether multiple agents can discover similar conceptual boundaries from the same source material.

Measure:
- Stability of proposed domains.
- Degree of overlap.
- Missing concepts.
- Classification ambiguity.
- Structural changes as new sources arrive.
- Whether the resulting organization improves retrieval and context compilation.

Do not optimize for a predetermined folder hierarchy.

## 12. Development Methodology

Build incrementally and validate assumptions through working experiments.

Before implementation:
1. Examine relevant existing projects and standards.
2. Research existing tools that may provide capabilities we should reuse.
3. Identify the smallest viable architecture.
4. Document important decisions and unresolved questions.
5. Establish clear interfaces between components.

During implementation:
- Prefer small, testable components.
- Keep interfaces explicit.
- Maintain human-readable artifacts.
- Write tests for deterministic operations.
- Preserve provenance throughout the pipeline.
- Make operations repeatable and inspectable.
- Avoid unnecessary abstraction.
- Document actual behavior rather than intended future behavior.

Maintain a development journal containing:
- Architectural decisions.
- Experiments.
- Findings.
- Rejected approaches.
- Open questions.
- Changes to foundational assumptions.

Use Git as the primary development history and collaboration mechanism.

## 13. Non-Goals

The initial project is not intended to become:
- A general-purpose autonomous agent.
- Another agent framework.
- A conventional personal knowledge-management application.
- A replacement for MemPalace.
- A replacement for Hermes memory.
- A giant predefined ontology.
- A predictive AI world model for physical simulation.
- An enterprise knowledge graph standard.
- A complex distributed platform.

Keep the focus on the persistent representation and its development process.

## 14. Success Criteria

The POC is successful if:

1. Multiple independent sources can be ingested without losing provenance.
2. The system can identify and reconcile entities across sources.
3. It can distinguish source claims from its own interpretations.
4. It can discover useful conceptual groupings without a predefined taxonomy.
5. It can propose and explain a useful organizational structure.
6. Humans can inspect and govern canonical changes.
7. The resulting world is portable and human-readable.
8. Agents can retrieve useful context without ingesting the entire world.
9. The world can continue developing as new sources and observations arrive.

The most important test:

Can an agent progressively develop a useful model of an unfamiliar environment without first being told how that environment should be organized?

## 15. Instructions to the Development Agent

Act as a pragmatic architectural collaborator and implementation partner.

Do not immediately generate a large application or impose an elaborate architecture.

Start by examining the problem, identifying existing capabilities worth reusing, and designing a small experiment that tests the central hypothesis.

Challenge assumptions, identify hidden complexity, and distinguish proven decisions from hypotheses.

When proposing architecture:
- Explain why a component exists.
- Identify its ownership boundaries.
- Avoid overlapping responsibilities.
- Prefer established standards and reusable tools.
- Keep the canonical representation independent of implementation details.

Do not silently expand scope.

Do not confuse a compelling architecture diagram with a working system.

Prioritize a functioning, inspectable Personal World POC over speculative future capabilities.

The objective is to discover how a World develops, not to build an elaborate system that assumes we already know.
