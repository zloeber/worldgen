from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from worldgen.contracts import validate_world
from worldgen.indexer import rebuild_index
from worldgen.ingest import ingest_source
from worldgen.proposals import generate_domain_proposals
from worldgen.world import init_world


FIXTURES = Path(__file__).parent / "fixtures"


def _entity_by_label(world_path: Path, label: str) -> dict | None:
    for path in (world_path / "entities").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload["label"] == label:
            return payload
    return None


def test_init_and_validate_world(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    errors = validate_world(world_path)
    assert errors == []
    assert (world_path / "sources" / "raw").exists()
    assert (world_path / ".gitignore").read_text(encoding="utf-8").strip() == "sources/raw/"


def test_ingestion_is_repeatable_and_idempotent(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    source = FIXTURES / "chatgpt_export"
    first = ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=source,
        origin="fixture://chatgpt",
    )
    second = ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=source,
        origin="fixture://chatgpt",
    )
    assert first is not None
    assert second is None
    assert first["observations"] > 0


def test_duplicate_entity_alias_and_cross_source_reconciliation(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=FIXTURES / "chatgpt_export",
        origin="fixture://chatgpt",
    )
    ingest_source(
        world_path,
        source_type="markdown_repo",
        source_name="hermes-fixture",
        source_path=FIXTURES / "hermes_repo",
        origin="fixture://hermes",
    )
    atlas_entities = []
    for path in (world_path / "entities").glob("*.json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload["normalized_label"] == "project atlas":
            atlas_entities.append(payload)
    assert len(atlas_entities) == 1
    hermes_entity = _entity_by_label(world_path, "Hermes Umbrella")
    assert hermes_entity is not None
    assert "Hermes" in hermes_entity["aliases"]


def test_conflicting_assertions_and_provenance(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=FIXTURES / "chatgpt_export",
        origin="fixture://chatgpt",
    )
    assertions = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (world_path / "assertions").glob("*.json")
    ]
    conflicting = [a for a in assertions if a["status"] == "conflicting"]
    assert conflicting
    evidence = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (world_path / "evidence").glob("*.json")
    ]
    assert evidence
    assert evidence[0]["source_reference"]


def test_index_rebuild_and_proposal_generation(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=FIXTURES / "chatgpt_export",
        origin="fixture://chatgpt",
    )
    ingest_source(
        world_path,
        source_type="markdown_repo",
        source_name="hermes-fixture",
        source_path=FIXTURES / "hermes_repo",
        origin="fixture://hermes",
    )
    proposal_ids = generate_domain_proposals(world_path)
    assert len(proposal_ids) == 2
    assert proposal_ids[0] != proposal_ids[1]

    db_path = rebuild_index(world_path)
    conn = sqlite3.connect(db_path)
    try:
        count = conn.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
    finally:
        conn.close()
    assert count >= 2


def test_validation_detects_malformed_records(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    malformed = world_path / "entities" / "bad.json"
    malformed.write_text(
        json.dumps({"id": "entity-bad", "kind": "Entity", "contract_version": "1.0.0"}),
        encoding="utf-8",
    )
    errors = validate_world(world_path)
    assert any("missing required field" in error.message for error in errors)
