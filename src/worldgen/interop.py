from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import read_json

JSONLD_CONTEXT = {
    "@context": {
        "@vocab": "https://worldgen.dev/ns/",
        "worldgen": "https://worldgen.dev/ns/",
        "prov": "http://www.w3.org/ns/prov#",
        "schema": "https://schema.org/",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "id": "@id",
        "kind": "@type",
        "created_at": {"@id": "prov:generatedAtTime", "@type": "xsd:dateTime"},
        "observed_at": {"@id": "prov:atTime", "@type": "xsd:dateTime"},
        "source_id": "worldgen:source_id",
        "source_reference": "worldgen:source_reference",
        "source_ids": "worldgen:source_ids",
        "evidence_ids": "worldgen:evidence_ids",
        "entity_ids": "worldgen:entity_ids",
        "assertion_ids": "worldgen:assertion_ids",
        "normalized_label": "worldgen:normalized_label",
        "aliases": "worldgen:aliases",
        "predicate": "worldgen:predicate",
        "object_text": "worldgen:object_text",
        "relationship_type": "worldgen:relationship_type",
        "relationship_basis": "worldgen:relationship_basis",
        "interpretation_level": "worldgen:interpretation_level",
        "status": "worldgen:status",
        "contract_version": "worldgen:contract_version",
    }
}


def _iter_canonical_records(world_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for json_file in sorted(world_path.rglob("*.json")):
        rel = json_file.relative_to(world_path)
        if rel.parts[:2] == ("indexes", "sqlite"):
            continue
        if rel.parts[:2] == ("sources", "raw"):
            continue
        record = read_json(json_file)
        if isinstance(record, dict) and record.get("id") and record.get("kind"):
            records.append(record)
    return records


def canonical_to_jsonld(world_path: Path) -> dict[str, Any]:
    graph: list[dict[str, Any]] = []
    for record in _iter_canonical_records(world_path):
        payload = {
            "@id": f"urn:worldgen:{record['kind'].lower()}:{record['id']}",
            "id": record["id"],
            "kind": record["kind"],
            **{key: value for key, value in record.items() if key not in {"id", "kind"}},
        }
        graph.append(payload)
    return {"@context": JSONLD_CONTEXT["@context"], "@graph": graph}


def jsonld_to_canonical(jsonld_doc: dict[str, Any]) -> list[dict[str, Any]]:
    graph = jsonld_doc.get("@graph") or [jsonld_doc]
    canonical: list[dict[str, Any]] = []
    for item in graph:
        if not isinstance(item, dict):
            continue
        if "id" in item and "kind" in item:
            record = {k: v for k, v in item.items() if k not in {"@id", "@type"}}
            record["id"] = item["id"]
            record["kind"] = item["kind"]
            canonical.append(record)
    return canonical
