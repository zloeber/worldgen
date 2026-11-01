from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .utils import read_json

CONTRACT_VERSION = "1.0.0"

KIND_REQUIRED_FIELDS: dict[str, set[str]] = {
    "World": {"id", "kind", "contract_version", "created_at", "status", "name", "description"},
    "Source": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "source_type",
        "display_name",
        "origin",
        "content_hash",
    },
    "Observation": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "source_id",
        "source_reference",
        "content",
        "observed_at",
    },
    "Entity": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "label",
        "normalized_label",
        "aliases",
    },
    "Relationship": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "from_entity_id",
        "to_entity_id",
        "relationship_type",
        "evidence_ids",
    },
    "Assertion": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "subject_entity_id",
        "predicate",
        "object_text",
        "evidence_ids",
        "interpretation_level",
    },
    "Evidence": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "source_id",
        "source_reference",
        "excerpt",
        "observed_at",
    },
    "Context": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "title",
        "entity_ids",
        "assertion_ids",
    },
    "Proposal": {
        "id",
        "kind",
        "contract_version",
        "created_at",
        "status",
        "title",
        "proposal_type",
        "approach",
        "evidence_ids",
        "body",
    },
}


@dataclass(slots=True)
class ValidationError:
    path: Path
    message: str


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
        errors.extend(validate_record(record, json_file))
    return errors
