from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from .adapters import (
    extract_alias_pairs,
    extract_chatgpt_observations,
    extract_entity_candidates,
    extract_is_assertions,
    extract_markdown_repo_observations,
)
from .contracts import CONTRACT_VERSION
from .utils import file_hash, normalize_text, read_json, stable_id, utc_now, write_json


def _load_source_manifest(manifest_path: Path) -> dict | None:
    if not manifest_path.exists():
        return None
    return read_json(manifest_path)


def _append_ingest_log(world_path: Path, payload: dict) -> None:
    log_file = world_path / "sources" / "ingest-log.jsonl"
    with log_file.open("a", encoding="utf-8") as fh:
        import json

        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def _copy_raw_source(source_path: Path, target_path: Path) -> None:
    if target_path.exists():
        return
    if source_path.is_file():
        target_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path / source_path.name)
        return
    shutil.copytree(source_path, target_path, dirs_exist_ok=True)


def _entity_record(world_path: Path, label: str, source_id: str) -> str:
    normalized = normalize_text(label)
    entity_id = stable_id("entity", normalized)
    entity_path = world_path / "entities" / f"{entity_id}.json"
    if not entity_path.exists():
        write_json(
            entity_path,
            {
                "id": entity_id,
                "kind": "Entity",
                "contract_version": CONTRACT_VERSION,
                "created_at": utc_now(),
                "status": "candidate",
                "label": label,
                "normalized_label": normalized,
                "aliases": [],
                "source_ids": [source_id],
            },
        )
    else:
        record = read_json(entity_path)
        if source_id not in record.get("source_ids", []):
            record.setdefault("source_ids", []).append(source_id)
            write_json(entity_path, record)
    return entity_id


def _upsert_alias(world_path: Path, entity_id: str, alias: str) -> None:
    entity_path = world_path / "entities" / f"{entity_id}.json"
    record = read_json(entity_path)
    aliases = set(record.get("aliases", []))
    aliases.add(alias)
    record["aliases"] = sorted(aliases)
    write_json(entity_path, record)


def _existing_assertions(world_path: Path) -> dict[tuple[str, str], list[tuple[str, str, str]]]:
    out: dict[tuple[str, str], list[tuple[str, str, str]]] = {}
    for assertion_path in (world_path / "assertions").glob("*.json"):
        assertion = read_json(assertion_path)
        key = (assertion["subject_entity_id"], assertion["predicate"])
        out.setdefault(key, []).append((assertion["id"], assertion["object_text"], assertion["status"]))
    return out


def _ingest_observations(
    world_path: Path,
    source_id: str,
    observations: list,
) -> dict[str, int]:
    assertion_index = _existing_assertions(world_path)
    counts = {"observations": 0, "evidence": 0, "assertions": 0, "relationships": 0}
    for obs in observations:
        obs_id = stable_id("obs", source_id, obs.source_reference, obs.content)
        obs_path = world_path / "observations" / f"{obs_id}.json"
        if not obs_path.exists():
            write_json(
                obs_path,
                {
                    "id": obs_id,
                    "kind": "Observation",
                    "contract_version": CONTRACT_VERSION,
                    "created_at": utc_now(),
                    "status": "observed",
                    "source_id": source_id,
                    "source_reference": obs.source_reference,
                    "content": obs.content,
                    "observed_at": obs.observed_at,
                },
            )
            counts["observations"] += 1
        evidence_id = stable_id("evidence", source_id, obs.source_reference, obs.content)
        evidence_path = world_path / "evidence" / f"{evidence_id}.json"
        if not evidence_path.exists():
            write_json(
                evidence_path,
                {
                    "id": evidence_id,
                    "kind": "Evidence",
                    "contract_version": CONTRACT_VERSION,
                    "created_at": utc_now(),
                    "status": "recorded",
                    "source_id": source_id,
                    "source_reference": obs.source_reference,
                    "excerpt": obs.content[:500],
                    "observed_at": obs.observed_at,
                    "observation_id": obs_id,
                },
            )
            counts["evidence"] += 1

        entity_ids: list[str] = []
        for candidate in extract_entity_candidates(obs.content):
            entity_ids.append(_entity_record(world_path, candidate, source_id))
        for main, alias in extract_alias_pairs(obs.content):
            main_id = _entity_record(world_path, main, source_id)
            _upsert_alias(world_path, main_id, alias)

        if len(entity_ids) >= 2:
            rel_id = stable_id("rel", entity_ids[0], entity_ids[1], evidence_id)
            rel_path = world_path / "relationships" / f"{rel_id}.json"
            if not rel_path.exists():
                write_json(
                    rel_path,
                    {
                        "id": rel_id,
                        "kind": "Relationship",
                        "contract_version": CONTRACT_VERSION,
                        "created_at": utc_now(),
                        "status": "candidate",
                        "from_entity_id": entity_ids[0],
                        "to_entity_id": entity_ids[1],
                        "relationship_type": "co_mentioned",
                        "evidence_ids": [evidence_id],
                    },
                )
                counts["relationships"] += 1

        for subject, object_text in extract_is_assertions(obs.content):
            subject_id = _entity_record(world_path, subject, source_id)
            assertion_id = stable_id("assertion", subject_id, "is", normalize_text(object_text), evidence_id)
            assertion_path = world_path / "assertions" / f"{assertion_id}.json"
            if assertion_path.exists():
                continue
            conflict_ids = []
            for existing_id, existing_object, _status in assertion_index.get((subject_id, "is"), []):
                if normalize_text(existing_object) != normalize_text(object_text):
                    conflict_ids.append(existing_id)
            status = "conflicting" if conflict_ids else "candidate"
            payload = {
                "id": assertion_id,
                "kind": "Assertion",
                "contract_version": CONTRACT_VERSION,
                "created_at": utc_now(),
                "status": status,
                "subject_entity_id": subject_id,
                "predicate": "is",
                "object_text": object_text,
                "evidence_ids": [evidence_id],
                "interpretation_level": "source_claim",
                "conflicts_with": sorted(conflict_ids),
            }
            write_json(assertion_path, payload)
            assertion_index.setdefault((subject_id, "is"), []).append((assertion_id, object_text, status))
            counts["assertions"] += 1
    return counts


def ingest_source(
    world_path: Path,
    source_type: str,
    source_name: str,
    source_path: Path,
    origin: str,
) -> dict[str, int] | None:
    source_hash = file_hash(source_path)
    source_id = stable_id("source", source_type, source_name, origin)
    manifest_path = world_path / "sources" / "manifests" / f"{source_id}.json"
    manifest = _load_source_manifest(manifest_path)
    if manifest and manifest.get("content_hash") == source_hash:
        _append_ingest_log(
            world_path,
            {
                "timestamp": utc_now(),
                "source_id": source_id,
                "source_type": source_type,
                "status": "skipped_idempotent",
                "content_hash": source_hash,
            },
        )
        return None

    write_json(
        manifest_path,
        {
            "id": source_id,
            "kind": "Source",
            "contract_version": CONTRACT_VERSION,
            "created_at": utc_now(),
            "status": "registered",
            "source_type": source_type,
            "display_name": source_name,
            "origin": origin,
            "content_hash": source_hash,
        },
    )
    raw_target = world_path / "sources" / "raw" / source_id
    _copy_raw_source(source_path, raw_target)

    extractors: dict[str, Callable[[Path], list]] = {
        "chatgpt_export": extract_chatgpt_observations,
        "markdown_repo": extract_markdown_repo_observations,
    }
    extractor = extractors[source_type]
    observations = extractor(source_path)
    counts = _ingest_observations(world_path, source_id, observations)
    _append_ingest_log(
        world_path,
        {
            "timestamp": utc_now(),
            "source_id": source_id,
            "source_type": source_type,
            "status": "ingested",
            "content_hash": source_hash,
            **counts,
        },
    )
    return counts
