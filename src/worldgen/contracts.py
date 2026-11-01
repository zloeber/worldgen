from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .schemas import RECORD_SCHEMAS
from .utils import read_json

CONTRACT_VERSION = "1.0.0"

KIND_REQUIRED_FIELDS: dict[str, set[str]] = {
    "World": {"id", "kind", "contract_version", "created_at", "status", "name", "description"},
    "Source": {"id", "kind", "contract_version", "created_at", "status", "source_type", "display_name", "origin", "content_hash"},
    "Observation": {"id", "kind", "contract_version", "created_at", "status", "source_id", "source_reference", "content", "observed_at"},
    "Entity": {"id", "kind", "contract_version", "created_at", "status", "label", "normalized_label", "aliases"},
    "Relationship": {"id", "kind", "contract_version", "created_at", "status", "from_entity_id", "to_entity_id", "relationship_type", "relationship_basis", "evidence_ids"},
    "Assertion": {"id", "kind", "contract_version", "created_at", "status", "subject_entity_id", "predicate", "object_text", "evidence_ids", "interpretation_level"},
    "Evidence": {"id", "kind", "contract_version", "created_at", "status", "source_id", "source_reference", "excerpt", "observed_at"},
    "Context": {"id", "kind", "contract_version", "created_at", "status", "title", "entity_ids", "assertion_ids"},
    "Proposal": {"id", "kind", "contract_version", "created_at", "status", "title", "proposal_type", "approach", "evidence_ids", "body"},
}


@dataclass(slots=True)
class ValidationError:
    path: Path
    message: str


def _schema_errors(record: dict[str, Any], path: Path) -> list[ValidationError]:
    kind = record.get("kind")
    schema = RECORD_SCHEMAS.get(kind)
    if schema is None:
        return [ValidationError(path=path, message=f"unknown kind: {kind!r}")]
    validator = Draft202012Validator(schema)
    errors: list[ValidationError] = []
    for error in validator.iter_errors(record):
        location = ".".join(str(part) for part in error.absolute_path) if error.absolute_path else "$"
        errors.append(ValidationError(path=path, message=f"{location}: {error.message}"))
    return errors


def validate_record(record: dict[str, Any], path: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    kind = record.get("kind")
    if kind not in KIND_REQUIRED_FIELDS:
        errors.append(ValidationError(path=path, message=f"unknown kind: {kind!r}"))
        return errors
    if record.get("contract_version") != CONTRACT_VERSION:
        errors.append(ValidationError(path=path, message="invalid or missing contract_version"))
    missing = sorted(KIND_REQUIRED_FIELDS[kind] - set(record.keys()))
    for field in missing:
        errors.append(ValidationError(path=path, message=f"missing required field: {field}"))
    errors.extend(_schema_errors(record, path))
    return errors


def _check_referential_integrity(records_by_id: dict[str, dict], path: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for record in records_by_id.values():
        kind = record.get("kind")
        if kind == "Relationship":
            for field in ("from_entity_id", "to_entity_id"):
                if record.get(field) not in records_by_id:
                    errors.append(ValidationError(path=path, message=f"relationship {record.get('id')} references missing {field}: {record.get(field)!r}"))
            for evidence_id in record.get("evidence_ids", []):
                if evidence_id not in records_by_id:
                    errors.append(ValidationError(path=path, message=f"relationship {record.get('id')} references missing evidence_id: {evidence_id!r}"))
        elif kind == "Assertion":
            subject_id = record.get("subject_entity_id")
            if subject_id not in records_by_id:
                errors.append(ValidationError(path=path, message=f"assertion {record.get('id')} references missing subject_entity_id: {subject_id!r}"))
            for evidence_id in record.get("evidence_ids", []):
                if evidence_id not in records_by_id:
                    errors.append(ValidationError(path=path, message=f"assertion {record.get('id')} references missing evidence_id: {evidence_id!r}"))
        elif kind == "Context":
            for entity_id in record.get("entity_ids", []):
                if entity_id not in records_by_id:
                    errors.append(ValidationError(path=path, message=f"context {record.get('id')} references missing entity_id: {entity_id!r}"))
            for assertion_id in record.get("assertion_ids", []):
                if assertion_id not in records_by_id:
                    errors.append(ValidationError(path=path, message=f"context {record.get('id')} references missing assertion_id: {assertion_id!r}"))
        elif kind == "Evidence":
            source_id = record.get("source_id")
            if source_id not in records_by_id:
                errors.append(ValidationError(path=path, message=f"evidence {record.get('id')} references missing source_id: {source_id!r}"))
        elif kind == "Observation":
            source_id = record.get("source_id")
            if source_id not in records_by_id:
                errors.append(ValidationError(path=path, message=f"observation {record.get('id')} references missing source_id: {source_id!r}"))
    return errors


def validate_world(world_path: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required_paths = [
        world_path / "world.json",
        world_path / "sources" / "manifests",
        world_path / "sources" / "raw",
        world_path / "observations",
        world_path / "entities",
        world_path / "relationships",
        world_path / "assertions",
        world_path / "evidence",
        world_path / "proposals",
        world_path / "indexes" / "sqlite",
    ]
    for required in required_paths:
        if not required.exists():
            errors.append(ValidationError(path=required, message="missing required world path"))

    records_by_id: dict[str, dict[str, Any]] = {}
    for json_file in sorted(world_path.rglob("*.json")):
        rel = json_file.relative_to(world_path)
        if rel.parts[:2] == ("indexes", "sqlite"):
            continue
        if rel.parts[:2] == ("sources", "raw"):
            continue
        try:
            record = read_json(json_file)
        except Exception as exc:  # noqa: BLE001
            errors.append(ValidationError(path=json_file, message=f"invalid JSON: {exc}"))
            continue
        if not isinstance(record, dict):
            errors.append(ValidationError(path=json_file, message="JSON root must be an object"))
            continue
        record_id = record.get("id")
        if isinstance(record_id, str):
            if record_id in records_by_id:
                errors.append(ValidationError(path=json_file, message=f"duplicate record id: {record_id}"))
            records_by_id[record_id] = record
        errors.extend(validate_record(record, json_file))
    errors.extend(_check_referential_integrity(records_by_id, world_path / "world.json"))
    return errors
