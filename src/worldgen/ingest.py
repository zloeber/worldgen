from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from .adapters import (
    extract_alias_pairs,
    extract_chatgpt_observations,
    extract_entity_candidates,
    extract_is_assertions,
    extract_markdown_repo_observations,
)
from .contracts import CONTRACT_VERSION
from .models import ModelConfig, complete_with_litellm
from .utils import file_hash, normalize_text, read_json, stable_id, utc_now, write_json

CompleteFn = Callable[[ModelConfig, str], dict]
_INTERPRET_PROMPT = """Extract candidate knowledge from this conversation excerpt.
Return only JSON with this shape:
{"entities":[{"label":"...","aliases":["..."]}],"assertions":[{"subject":"...","predicate":"is","object":"..."}]}
Use short labels. Omit uncertain items.
Excerpt:
{excerpt}
"""


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
                "canonical_entity_id": None,
                "identity_proposal_ids": [],
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
            payload = {
                "id": obs_id,
                "kind": "Observation",
                "contract_version": CONTRACT_VERSION,
                "created_at": utc_now(),
                "status": "observed",
                "source_id": source_id,
                "source_reference": obs.source_reference,
                "content": obs.content,
                "observed_at": obs.observed_at,
            }
            if obs.author_role:
                payload["author_role"] = obs.author_role
            if obs.conversation_title:
                payload["conversation_title"] = obs.conversation_title
            write_json(obs_path, payload)
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
                        "relationship_basis": "co_occurrence",
                        "evidence_ids": [evidence_id],
                        "confidence": 0.5,
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
                "confidence": 0.7,
                "source_id": source_id,
                "conflicts_with": sorted(conflict_ids),
                "valid_from": obs.observed_at,
            }
            write_json(assertion_path, payload)
            assertion_index.setdefault((subject_id, "is"), []).append((assertion_id, object_text, status))
            counts["assertions"] += 1
    return counts


def _conversation_key(source_reference: str) -> str:
    prefix = "conversation:"
    marker = ":message:"
    if source_reference.startswith(prefix) and marker in source_reference:
        return source_reference[len(prefix) : source_reference.rfind(marker)]
    return source_reference


def _chunk_observations(observations: list[dict], limit: int = 6000) -> list[list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for record in observations:
        grouped.setdefault(_conversation_key(str(record.get("source_reference", ""))), []).append(record)
    chunks: list[list[dict]] = []
    for records in grouped.values():
        current: list[dict] = []
        size = 0
        for record in records:
            line = f"{record.get('author_role') or 'unknown'}: {record.get('content', '')}"
            if current and size + len(line) > limit:
                chunks.append(current)
                current = []
                size = 0
            current.append(record)
            size += len(line) + 1
        if current:
            chunks.append(current)
    return chunks


def _interpretation_done(manifest: dict, config: ModelConfig) -> bool:
    for item in manifest.get("model_interpretations") or []:
        if (
            item.get("model") == config.model
            and item.get("api_base") == config.api_base
            and item.get("status") == "completed"
        ):
            return True
    return False


def _mark_interpretation(manifest_path: Path, config: ModelConfig) -> None:
    manifest = read_json(manifest_path)
    kept = [
        item
        for item in manifest.get("model_interpretations") or []
        if not (item.get("model") == config.model and item.get("api_base") == config.api_base)
    ]
    kept.append({"model": config.model, "api_base": config.api_base, "status": "completed", "provider": "litellm"})
    manifest["model_interpretations"] = kept
    write_json(manifest_path, manifest)


def _observations_for_source(world_path: Path, source_id: str) -> list[dict]:
    records = []
    for path in sorted((world_path / "observations").glob("*.json")):
        record = read_json(path)
        if record.get("source_id") == source_id:
            records.append(record)
    return records


def _evidence_for_source(world_path: Path, source_id: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path in (world_path / "evidence").glob("*.json"):
        record = read_json(path)
        observation_id = record.get("observation_id")
        if record.get("source_id") == source_id and isinstance(observation_id, str):
            mapping[observation_id] = record["id"]
    return mapping


def _record_interpretation_assertion(
    world_path: Path,
    assertion_index: dict[tuple[str, str], list[tuple[str, str, str]]],
    *,
    source_id: str,
    config: ModelConfig,
    subject: str,
    predicate: str,
    object_text: str,
    evidence_ids: list[str],
    observed_at: str,
) -> bool:
    subject_id = _entity_record(world_path, subject, source_id)
    evidence_key = ",".join(sorted(evidence_ids))
    assertion_id = stable_id(
        "assertion",
        subject_id,
        predicate,
        normalize_text(object_text),
        evidence_key,
        config.model,
        "interpretation",
    )
    assertion_path = world_path / "assertions" / f"{assertion_id}.json"
    if assertion_path.exists():
        return False
    conflict_ids = []
    for existing_id, existing_object, _status in assertion_index.get((subject_id, predicate), []):
        if normalize_text(existing_object) != normalize_text(object_text):
            conflict_ids.append(existing_id)
    status = "conflicting" if conflict_ids else "candidate"
    write_json(
        assertion_path,
        {
            "id": assertion_id,
            "kind": "Assertion",
            "contract_version": CONTRACT_VERSION,
            "created_at": utc_now(),
            "status": status,
            "subject_entity_id": subject_id,
            "predicate": predicate,
            "object_text": object_text,
            "evidence_ids": sorted(set(evidence_ids)),
            "interpretation_level": "interpretation",
            "confidence": 0.4,
            "source_id": source_id,
            "conflicts_with": sorted(set(conflict_ids)),
            "valid_from": observed_at,
            "model": config.model,
            "model_provider": "litellm",
        },
    )
    assertion_index.setdefault((subject_id, predicate), []).append((assertion_id, object_text, status))
    return True


def _apply_model_interpretation(
    world_path: Path,
    source_id: str,
    config: ModelConfig,
    complete: CompleteFn,
) -> dict[str, int]:
    observations = _observations_for_source(world_path, source_id)
    evidence_by_observation = _evidence_for_source(world_path, source_id)
    assertion_index = _existing_assertions(world_path)
    counts = {"interpreted_entities": 0, "interpreted_assertions": 0}
    for chunk in _chunk_observations(observations):
        excerpt = "\n".join(
            f"{item.get('author_role') or 'unknown'}: {item.get('content', '')}" for item in chunk
        )
        payload = complete(config, _INTERPRET_PROMPT.replace("{excerpt}", excerpt))
        evidence_ids = []
        for item in chunk:
            evidence_id = evidence_by_observation.get(item["id"])
            if evidence_id and evidence_id not in evidence_ids:
                evidence_ids.append(evidence_id)
        for entity in payload.get("entities") or []:
            if not isinstance(entity, dict):
                continue
            label = str(entity.get("label") or "").strip()
            if not label or len(label) > 200:
                continue
            entity_id = _entity_record(world_path, label, source_id)
            counts["interpreted_entities"] += 1
            aliases = entity.get("aliases") or []
            if isinstance(aliases, list):
                for alias in aliases:
                    if isinstance(alias, str) and alias.strip():
                        _upsert_alias(world_path, entity_id, alias.strip())
        if not evidence_ids:
            continue
        observed_at = str(chunk[0].get("observed_at") or "1970-01-01T00:00:00Z")
        for claim in payload.get("assertions") or []:
            if not isinstance(claim, dict):
                continue
            subject = str(claim.get("subject") or "").strip()
            predicate = str(claim.get("predicate") or "is").strip() or "is"
            object_text = str(claim.get("object") or claim.get("object_text") or "").strip()
            if not subject or not object_text or len(subject) > 200 or len(object_text) > 500:
                continue
            created = _record_interpretation_assertion(
                world_path,
                assertion_index,
                source_id=source_id,
                config=config,
                subject=subject,
                predicate=predicate,
                object_text=object_text,
                evidence_ids=evidence_ids,
                observed_at=observed_at,
            )
            if created:
                counts["interpreted_assertions"] += 1
    return counts


def ingest_source(
    world_path: Path,
    source_type: str,
    source_name: str,
    source_path: Path,
    origin: str,
    *,
    model: ModelConfig | None = None,
    complete: CompleteFn | None = None,
) -> dict[str, int | str] | None:
    extractors: dict[str, Callable[[Path], list]] = {
        "chatgpt_export": extract_chatgpt_observations,
        "markdown_repo": extract_markdown_repo_observations,
    }
    if source_type not in extractors:
        raise ValueError(f"unsupported source_type: {source_type}")

    source_hash = file_hash(source_path)
    source_id = stable_id("source", source_type, source_name, origin)
    manifest_path = world_path / "sources" / "manifests" / f"{source_id}.json"
    manifest = _load_source_manifest(manifest_path)
    completer = complete or complete_with_litellm
    if manifest and manifest.get("content_hash") == source_hash:
        if model is not None and not _interpretation_done(manifest, model):
            counts = _apply_model_interpretation(world_path, source_id, model, completer)
            _mark_interpretation(manifest_path, model)
            _append_ingest_log(
                world_path,
                {
                    "timestamp": utc_now(),
                    "source_id": source_id,
                    "source_type": source_type,
                    "status": "interpreted",
                    "content_hash": source_hash,
                    **counts,
                },
            )
            return {**counts, "source_id": source_id, "content_hash": source_hash, "status": "interpreted"}
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

    extractor = extractors[source_type]
    observations = extractor(source_path)
    counts = _ingest_observations(world_path, source_id, observations)
    if model is not None:
        counts.update(_apply_model_interpretation(world_path, source_id, model, completer))
        _mark_interpretation(manifest_path, model)
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
    return {
        **counts,
        "source_id": source_id,
        "content_hash": source_hash,
    }
