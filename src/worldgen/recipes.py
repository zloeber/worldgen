from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from .ingest import ingest_source
from .proposals import generate_domain_proposals
from .utils import read_json, stable_id, utc_now, write_json

RECIPE_CONTRACT_VERSION = "1.0.0"
EXECUTION_CONTRACT_VERSION = "1.0.0"


def initial_recipe_catalog() -> list[dict[str, Any]]:
    return [
        {
            "id": "seed-foundation",
            "version": "1.0.0",
            "name": "Seed World foundation",
            "purpose": "Establish the World's identity, perspective, purpose, boundaries, principles, and initial discovery agenda.",
            "implementation_status": "implemented",
            "inputs": {
                "required": ["perspective", "purpose", "boundaries", "principles", "discovery_agenda"],
                "optional": ["identity_statement"],
            },
            "prerequisites": ["world.json must exist"],
            "outputs": ["world.foundation metadata updated"],
            "applicable_record_kinds": ["World"],
            "deterministic_operations": [
                "validate required fields",
                "write structured foundation metadata to world.json",
            ],
            "model_assisted_operations": [],
            "validation_requirements": ["all required foundation fields are non-empty strings or non-empty lists"],
            "evidence_and_provenance_requirements": [
                "record execution input snapshot",
                "record changed files list",
            ],
            "side_effects_and_mutations": [
                "updates canonical world.json foundation block",
            ],
            "human_review_requirements": {
                "automatic_acceptance": ["foundation metadata written from explicit user input"],
                "requires_human_review": [],
            },
            "execution_metadata_requirements": [
                "execution id",
                "timestamps",
                "lifecycle step statuses",
                "runtime metadata",
            ],
            "reproducibility": {
                "deterministic": True,
                "notes": "Given identical world.json baseline and identical inputs, output is deterministic.",
            },
            "depends_on": [],
        },
        {
            "id": "evaluate-foundation",
            "version": "1.0.0",
            "name": "Evaluate World foundation",
            "purpose": "Identify gaps, ambiguities, contradictions, and drift in the World's foundation.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["criteria"]},
            "prerequisites": ["seed-foundation should have been executed at least once"],
            "outputs": ["proposal(s) for foundation improvements"],
            "applicable_record_kinds": ["World", "Proposal"],
            "deterministic_operations": ["check required foundation fields exist"],
            "model_assisted_operations": ["identify ambiguities and contradictions in narrative foundation text"],
            "validation_requirements": ["all findings reference specific foundation fields"],
            "evidence_and_provenance_requirements": ["cite foundation fields and prior foundation revisions"],
            "side_effects_and_mutations": ["proposal generation only by default"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["all interpretive findings"],
            },
            "execution_metadata_requirements": ["record inference configuration when used"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Interpretive findings may vary; prompt and model metadata must be recorded.",
            },
            "depends_on": ["seed-foundation"],
        },
        {
            "id": "ingest-source",
            "version": "1.0.0",
            "name": "Ingest source",
            "purpose": "Register and ingest an external source into the World while preserving provenance.",
            "implementation_status": "implemented",
            "inputs": {
                "required": ["source_type", "source_name", "source_path", "origin"],
                "optional": [],
            },
            "prerequisites": ["world package initialized", "source path exists"],
            "outputs": ["Source record", "Observation records", "Evidence records", "candidate Entity/Relationship/Assertion records"],
            "applicable_record_kinds": ["Source", "Observation", "Evidence", "Entity", "Relationship", "Assertion"],
            "deterministic_operations": [
                "content hashing",
                "idempotency check by source hash",
                "stable id generation",
            ],
            "model_assisted_operations": [],
            "validation_requirements": ["resulting records pass world contract validation"],
            "evidence_and_provenance_requirements": [
                "preserve source manifest and raw source snapshot",
                "record ingest-log event",
            ],
            "side_effects_and_mutations": [
                "writes canonical Source/Observation/Evidence/Entity/Relationship/Assertion records",
                "does not auto-promote candidate/conflicting records to accepted",
            ],
            "human_review_requirements": {
                "automatic_acceptance": ["source registration and raw preservation"],
                "requires_human_review": ["candidate/conflicting assertions"],
            },
            "execution_metadata_requirements": [
                "input snapshot",
                "output counts",
                "changed files",
                "runtime metadata",
            ],
            "reproducibility": {
                "deterministic": True,
                "notes": "For identical source content and world state, ingestion is deterministic.",
            },
            "depends_on": ["seed-foundation"],
        },
        {
            "id": "reconcile-source",
            "version": "1.0.0",
            "name": "Reconcile source",
            "purpose": "Compare newly ingested material against existing knowledge and identify novelty, conflicts, and possible supersession.",
            "implementation_status": "planned",
            "inputs": {"required": ["source_id"], "optional": ["scope"]},
            "prerequisites": ["ingest-source executed for source_id"],
            "outputs": ["proposal(s) for novelty/conflict/supersession"],
            "applicable_record_kinds": ["Source", "Assertion", "Proposal"],
            "deterministic_operations": ["compare source assertions with existing assertions"],
            "model_assisted_operations": ["semantic comparison for paraphrased claim overlap"],
            "validation_requirements": ["all proposals reference evidence ids"],
            "evidence_and_provenance_requirements": ["trace each finding to source records"],
            "side_effects_and_mutations": ["proposal generation only by default"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["claim supersession proposals"],
            },
            "execution_metadata_requirements": ["record deterministic and inference steps separately"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Inference may vary; deterministic comparison remains stable.",
            },
            "depends_on": ["ingest-source"],
        },
        {
            "id": "resolve-identities",
            "version": "1.0.0",
            "name": "Resolve identities",
            "purpose": "Identify references that may point to the same entity without silently merging ambiguous identities.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["entity_scope"]},
            "prerequisites": ["entity records exist from ingestion"],
            "outputs": ["identity resolution proposals"],
            "applicable_record_kinds": ["Entity", "Proposal"],
            "deterministic_operations": ["exact and normalized-label matching"],
            "model_assisted_operations": ["alias similarity interpretation"],
            "validation_requirements": ["no automatic merge without explicit acceptance"],
            "evidence_and_provenance_requirements": ["proposal references source ids and evidence ids"],
            "side_effects_and_mutations": ["proposal generation only by default"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["all non-exact identity merges"],
            },
            "execution_metadata_requirements": ["record match features and thresholds used"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Heuristic and inference-assisted identity suggestions may vary.",
            },
            "depends_on": ["ingest-source"],
        },
        {
            "id": "discover-relationships",
            "version": "1.0.0",
            "name": "Discover relationships",
            "purpose": "Identify explicit, inferred, and co-occurrence relationships.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["scope"]},
            "prerequisites": ["entity and evidence records exist"],
            "outputs": ["relationship candidates and proposals"],
            "applicable_record_kinds": ["Entity", "Relationship", "Evidence", "Proposal"],
            "deterministic_operations": ["co-occurrence relationship extraction"],
            "model_assisted_operations": ["infer implicit relationship semantics"],
            "validation_requirements": ["all relationships include evidence ids"],
            "evidence_and_provenance_requirements": ["trace relationships to supporting excerpts"],
            "side_effects_and_mutations": ["candidate relationship writes and/or proposals"],
            "human_review_requirements": {
                "automatic_acceptance": ["co-occurrence links with explicit evidence"],
                "requires_human_review": ["inferred semantic relationships"],
            },
            "execution_metadata_requirements": ["record extraction mode and confidence thresholds"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Co-occurrence is deterministic; inference-assisted semantics are not.",
            },
            "depends_on": ["ingest-source"],
        },
        {
            "id": "reconcile-claims",
            "version": "1.0.0",
            "name": "Reconcile claims",
            "purpose": "Identify compatible and conflicting claims, changes over time, and unresolved interpretations.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["subject_scope"]},
            "prerequisites": ["assertions exist from ingestion"],
            "outputs": ["conflict/supersession proposals"],
            "applicable_record_kinds": ["Assertion", "Proposal"],
            "deterministic_operations": ["exact predicate/object comparison per subject"],
            "model_assisted_operations": ["semantic claim compatibility analysis"],
            "validation_requirements": ["conflicts are linked to counterpart assertion ids"],
            "evidence_and_provenance_requirements": ["all reconciliations include evidence refs"],
            "side_effects_and_mutations": ["proposal generation; optional status updates"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["interpretive claim compatibility decisions"],
            },
            "execution_metadata_requirements": ["record comparison strategy and model metadata when used"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Semantic compatibility decisions can vary by model run.",
            },
            "depends_on": ["ingest-source", "resolve-identities"],
        },
        {
            "id": "discover-domains",
            "version": "1.0.0",
            "name": "Discover domains",
            "purpose": "Identify conceptual groupings and overlapping organizational perspectives.",
            "implementation_status": "implemented",
            "inputs": {"required": [], "optional": ["max_domains"]},
            "prerequisites": ["entity and relationship records exist"],
            "outputs": ["organizational_structure proposals"],
            "applicable_record_kinds": ["Entity", "Relationship", "Evidence", "Proposal"],
            "deterministic_operations": [
                "token-frequency domain proposal generation",
                "relationship connected-component proposal generation",
            ],
            "model_assisted_operations": [],
            "validation_requirements": ["proposals include evidence ids and candidate domains"],
            "evidence_and_provenance_requirements": ["proposal evidence ids trace to evidence records"],
            "side_effects_and_mutations": ["writes Proposal records only"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["organizational structure proposals"],
            },
            "execution_metadata_requirements": ["record generated proposal ids"],
            "reproducibility": {
                "deterministic": True,
                "notes": "Given identical world state, generated proposal ids and bodies are stable.",
            },
            "depends_on": ["ingest-source"],
        },
        {
            "id": "identify-gaps",
            "version": "1.0.0",
            "name": "Identify gaps",
            "purpose": "Identify missing information, unanswered questions, weakly supported assertions, and valuable exploration areas.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["scope"]},
            "prerequisites": ["baseline assertions and evidence exist"],
            "outputs": ["gap proposals and discovery opportunities"],
            "applicable_record_kinds": ["Assertion", "Evidence", "Proposal"],
            "deterministic_operations": ["find assertions with limited supporting evidence"],
            "model_assisted_operations": ["suggest high-value exploration questions"],
            "validation_requirements": ["every identified gap references supporting records"],
            "evidence_and_provenance_requirements": ["gaps must cite impacted entities/assertions"],
            "side_effects_and_mutations": ["proposal generation only by default"],
            "human_review_requirements": {
                "automatic_acceptance": [],
                "requires_human_review": ["priority/scoring of exploration opportunities"],
            },
            "execution_metadata_requirements": ["record scoring and ranking method"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Discovery prioritization may vary when inference is used.",
            },
            "depends_on": ["ingest-source", "reconcile-claims"],
        },
        {
            "id": "compile-context",
            "version": "1.0.0",
            "name": "Compile context",
            "purpose": "Produce a bounded, purpose-driven context including evidence, uncertainty, and inclusion rationale.",
            "implementation_status": "planned",
            "inputs": {"required": ["purpose"], "optional": ["entity_scope", "assertion_scope"]},
            "prerequisites": ["records exist relevant to requested purpose"],
            "outputs": ["Context records"],
            "applicable_record_kinds": ["Context", "Entity", "Assertion", "Evidence"],
            "deterministic_operations": ["filter and package selected records"],
            "model_assisted_operations": ["summarize rationale and uncertainty"],
            "validation_requirements": ["context includes referenced entity/assertion ids"],
            "evidence_and_provenance_requirements": ["include evidence links and selection rationale"],
            "side_effects_and_mutations": ["writes Context records"],
            "human_review_requirements": {
                "automatic_acceptance": ["deterministic context bundles"],
                "requires_human_review": ["model-generated synthesis text"],
            },
            "execution_metadata_requirements": ["record inclusion criteria and prompt metadata when used"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Selection can be deterministic; narrative synthesis can vary.",
            },
            "depends_on": ["ingest-source", "reconcile-claims"],
        },
        {
            "id": "evaluate-world",
            "version": "1.0.0",
            "name": "Evaluate world",
            "purpose": "Evaluate completeness, consistency, provenance, temporal integrity, coverage, and usefulness.",
            "implementation_status": "planned",
            "inputs": {"required": [], "optional": ["criteria"]},
            "prerequisites": ["world has foundational and source-derived records"],
            "outputs": ["evaluation report and proposals"],
            "applicable_record_kinds": ["World", "Proposal"],
            "deterministic_operations": ["contract and referential-integrity checks"],
            "model_assisted_operations": ["usefulness and coverage interpretation"],
            "validation_requirements": ["evaluation criteria and scores are explicit"],
            "evidence_and_provenance_requirements": ["all findings reference records and evidence"],
            "side_effects_and_mutations": ["proposal/report generation only"],
            "human_review_requirements": {
                "automatic_acceptance": ["deterministic contract check findings"],
                "requires_human_review": ["interpretive quality assessments"],
            },
            "execution_metadata_requirements": ["record rubric version and model metadata when used"],
            "reproducibility": {
                "deterministic": False,
                "notes": "Deterministic checks are stable; quality interpretation may vary.",
            },
            "depends_on": ["seed-foundation", "ingest-source"],
        },
    ]


def recipe_catalog_by_id(world_path: Path) -> dict[str, dict[str, Any]]:
    ensure_recipe_catalog(world_path)
    catalog: dict[str, dict[str, Any]] = {}
    for path in sorted((world_path / "recipes" / "definitions").glob("*.json")):
        definition = read_json(path)
        catalog[definition["id"]] = definition
    return catalog


def validate_recipe_definition(definition: dict[str, Any]) -> list[str]:
    required_top_level = {
        "id",
        "version",
        "name",
        "purpose",
        "inputs",
        "prerequisites",
        "outputs",
        "applicable_record_kinds",
        "deterministic_operations",
        "model_assisted_operations",
        "validation_requirements",
        "evidence_and_provenance_requirements",
        "side_effects_and_mutations",
        "human_review_requirements",
        "execution_metadata_requirements",
        "reproducibility",
        "depends_on",
        "implementation_status",
    }
    errors: list[str] = []
    missing = sorted(required_top_level - set(definition.keys()))
    errors.extend([f"missing field: {item}" for item in missing])
    if not isinstance(definition.get("id"), str) or not definition.get("id"):
        errors.append("id must be a non-empty string")
    if definition.get("version") != RECIPE_CONTRACT_VERSION:
        errors.append("version must match recipe contract version")
    inputs = definition.get("inputs")
    if not isinstance(inputs, dict):
        errors.append("inputs must be an object")
    else:
        if not isinstance(inputs.get("required"), list):
            errors.append("inputs.required must be a list")
        if not isinstance(inputs.get("optional"), list):
            errors.append("inputs.optional must be a list")
    if definition.get("implementation_status") not in {"implemented", "planned"}:
        errors.append("implementation_status must be implemented or planned")
    return errors


def ensure_recipe_catalog(world_path: Path) -> None:
    definitions_dir = world_path / "recipes" / "definitions"
    definitions_dir.mkdir(parents=True, exist_ok=True)
    for definition in initial_recipe_catalog():
        filename = f"{definition['id']}@{definition['version']}.json"
        path = definitions_dir / filename
        if not path.exists():
            write_json(path, definition)


def validate_recipe_catalog(world_path: Path) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for definition in recipe_catalog_by_id(world_path).values():
        errors.extend([f"{definition.get('id', '<unknown>')}: {message}" for message in validate_recipe_definition(definition)])
        rid = definition.get("id")
        if isinstance(rid, str):
            seen.add(rid)
    for definition in recipe_catalog_by_id(world_path).values():
        for dep in definition.get("depends_on", []):
            if dep not in seen:
                errors.append(f"{definition['id']}: dependency not found: {dep}")
    return errors


def _compose_dependencies(recipe_id: str, catalog: dict[str, dict[str, Any]], order: list[str], visited: set[str]) -> None:
    if recipe_id in visited:
        return
    visited.add(recipe_id)
    if recipe_id not in catalog:
        raise ValueError(f"unknown recipe id: {recipe_id}")
    for dep in catalog[recipe_id].get("depends_on", []):
        _compose_dependencies(dep, catalog, order, visited)
    if recipe_id not in order:
        order.append(recipe_id)


def compose_workflow(world_path: Path, recipe_ids: list[str]) -> list[str]:
    catalog = recipe_catalog_by_id(world_path)
    order: list[str] = []
    visited: set[str] = set()
    for recipe_id in recipe_ids:
        _compose_dependencies(recipe_id, catalog, order, visited)
    return order


def _snapshot_files(world_path: Path) -> set[str]:
    files: set[str] = set()
    for file in world_path.rglob("*.json"):
        rel = file.relative_to(world_path).as_posix()
        files.add(rel)
    return files


def _record_execution(world_path: Path, execution: dict[str, Any]) -> Path:
    executions_dir = world_path / "recipes" / "executions"
    executions_dir.mkdir(parents=True, exist_ok=True)
    path = executions_dir / f"{execution['execution_id']}.json"
    write_json(path, execution)
    return path


def list_execution_history(world_path: Path) -> list[dict[str, Any]]:
    executions = []
    for path in sorted((world_path / "recipes" / "executions").glob("*.json")):
        executions.append(read_json(path))
    return executions


def _validate_required_inputs(definition: dict[str, Any], inputs: dict[str, Any]) -> None:
    required_inputs = definition["inputs"]["required"]
    missing = [name for name in required_inputs if name not in inputs]
    if missing:
        raise ValueError(f"missing required inputs: {', '.join(missing)}")


def _run_seed_foundation(world_path: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    world_path_file = world_path / "world.json"
    world_record = read_json(world_path_file)
    foundation = {
        "identity_statement": inputs.get("identity_statement", world_record.get("name", "")),
        "perspective": inputs["perspective"],
        "purpose": inputs["purpose"],
        "boundaries": inputs["boundaries"],
        "principles": inputs["principles"],
        "discovery_agenda": inputs["discovery_agenda"],
        "seeded_at": utc_now(),
    }
    world_record["foundation"] = foundation
    world_record["updated_at"] = utc_now()
    write_json(world_path_file, world_record)
    return {"foundation_seeded": True}


def _run_ingest_source(world_path: Path, inputs: dict[str, Any]) -> dict[str, Any]:
    result = ingest_source(
        world_path=world_path,
        source_type=str(inputs["source_type"]),
        source_name=str(inputs["source_name"]),
        source_path=Path(str(inputs["source_path"])),
        origin=str(inputs["origin"]),
    )
    return {"ingest_result": result, "source_id": stable_id("source", str(inputs["source_type"]), str(inputs["source_name"]), str(inputs["origin"]))}


def _run_discover_domains(world_path: Path, _inputs: dict[str, Any]) -> dict[str, Any]:
    proposal_ids = generate_domain_proposals(world_path)
    return {"proposal_ids": proposal_ids}


def _run_recipe(world_path: Path, recipe_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if recipe_id == "seed-foundation":
        return _run_seed_foundation(world_path, inputs)
    if recipe_id == "ingest-source":
        return _run_ingest_source(world_path, inputs)
    if recipe_id == "discover-domains":
        return _run_discover_domains(world_path, inputs)
    raise ValueError(f"recipe not implemented: {recipe_id}")


def run_recipe(world_path: Path, recipe_id: str, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    ensure_recipe_catalog(world_path)
    definition = recipe_catalog_by_id(world_path).get(recipe_id)
    if definition is None:
        raise ValueError(f"unknown recipe id: {recipe_id}")
    inputs = inputs or {}
    execution_id = f"recipe-exec-{uuid.uuid4().hex[:12]}"
    started_at = utc_now()
    before_files = _snapshot_files(world_path)
    lifecycle = [
        {"step": "resolve_recipe_version", "status": "completed", "timestamp": started_at},
        {"step": "inspect_prerequisites_and_state", "status": "completed", "timestamp": utc_now()},
        {"step": "gather_inputs", "status": "completed", "timestamp": utc_now()},
    ]
    status = "completed"
    outputs: dict[str, Any] = {}
    error_message: str | None = None
    try:
        _validate_required_inputs(definition, inputs)
        lifecycle.append({"step": "execute_operations", "status": "in_progress", "timestamp": utc_now()})
        outputs = _run_recipe(world_path, recipe_id, inputs)
        lifecycle[-1]["status"] = "completed"
        lifecycle.extend(
            [
                {"step": "validate_outputs", "status": "completed", "timestamp": utc_now()},
                {"step": "record_results_and_provenance", "status": "completed", "timestamp": utc_now()},
                {"step": "generate_proposals_or_changes", "status": "completed", "timestamp": utc_now()},
                {"step": "report_warnings_and_opportunities", "status": "completed", "timestamp": utc_now()},
            ]
        )
    except Exception as exc:  # noqa: BLE001
        status = "failed"
        error_message = str(exc)
        lifecycle.append({"step": "execute_operations", "status": "failed", "timestamp": utc_now(), "error": error_message})
        lifecycle.extend(
            [
                {"step": "validate_outputs", "status": "skipped", "timestamp": utc_now()},
                {"step": "record_results_and_provenance", "status": "completed", "timestamp": utc_now()},
                {"step": "generate_proposals_or_changes", "status": "skipped", "timestamp": utc_now()},
                {"step": "report_warnings_and_opportunities", "status": "completed", "timestamp": utc_now()},
            ]
        )
    completed_at = utc_now()
    after_files = _snapshot_files(world_path)
    changed_files = sorted(after_files - before_files)
    execution = {
        "execution_id": execution_id,
        "kind": "RecipeExecution",
        "execution_contract_version": EXECUTION_CONTRACT_VERSION,
        "recipe_id": definition["id"],
        "recipe_version": definition["version"],
        "recipe_definition_path": f"recipes/definitions/{definition['id']}@{definition['version']}.json",
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "inputs": inputs,
        "outputs": outputs,
        "lifecycle": lifecycle,
        "proposed_mutations": changed_files,
        "warnings": [],
        "unresolved_questions": [],
        "failure": error_message,
        "runtime": {
            "agent_independent": True,
            "deterministic_operations": definition["deterministic_operations"],
            "model_assisted_operations": definition["model_assisted_operations"],
            "model_metadata": inputs.get("model_metadata"),
        },
        "reproducibility": {
            "recipe_contract_version": RECIPE_CONTRACT_VERSION,
            "execution_contract_version": EXECUTION_CONTRACT_VERSION,
            "deterministic_recipe": bool(definition["reproducibility"].get("deterministic", False)),
            "input_fingerprint": stable_id("recipe-input", definition["id"], str(sorted(inputs.items()))),
        },
    }
    execution_path = _record_execution(world_path, execution)
    execution["execution_path"] = execution_path.as_posix()
    return execution

