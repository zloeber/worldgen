from __future__ import annotations

import json
import zipfile
from pathlib import Path

from worldgen.adapters import extract_chatgpt_observations
from worldgen.contracts import validate_world
from worldgen.indexer import rebuild_index
from worldgen.ingest import ingest_source
from worldgen.world import init_world


def _conversation() -> dict:
    return {
        "id": "conv-1",
        "conversation_id": "conv-1",
        "title": "Atlas planning",
        "create_time": 1700000000,
        "current_node": "m-user",
        "mapping": {
            "root": {"id": "root", "message": None, "parent": None, "children": ["m-user"]},
            "m-user": {
                "id": "m-user",
                "message": {
                    "id": "m-user",
                    "author": {"role": "user"},
                    "create_time": 1700000000,
                    "content": {
                        "content_type": "multimodal_text",
                        "parts": [
                            "Project Atlas is active.",
                            {"content_type": "image_asset_pointer", "asset_pointer": "file-service://img"},
                        ],
                    },
                },
                "parent": "root",
                "children": ["m-code"],
            },
            "m-code": {
                "id": "m-code",
                "message": {
                    "id": "m-code",
                    "author": {"role": "assistant"},
                    "create_time": 1700000001,
                    "content": {"content_type": "code", "language": "unknown", "text": "Hermes Umbrella aka Hermes."},
                },
                "parent": "m-user",
                "children": ["m-image"],
            },
            "m-image": {
                "id": "m-image",
                "message": {
                    "id": "m-image",
                    "author": {"role": "user"},
                    "create_time": 1700000002,
                    "content": {
                        "content_type": "multimodal_text",
                        "parts": [{"content_type": "image_asset_pointer", "asset_pointer": "file-service://only"}],
                    },
                },
                "parent": "m-code",
                "children": ["m-context"],
            },
            "m-context": {
                "id": "m-context",
                "message": {
                    "id": "m-context",
                    "author": {"role": "system"},
                    "create_time": "1700000003",
                    "content": {
                        "content_type": "user_editable_context",
                        "user_profile": "Keeps a personal world.",
                        "user_instructions": "Prefer evidence.",
                    },
                },
                "parent": "m-image",
                "children": [],
            },
        },
    }


def test_split_export_directory_keeps_text_roles_and_utc_timestamps(tmp_path: Path) -> None:
    export = tmp_path / "export"
    export.mkdir()
    wrapped = {"conversations": [_conversation()]}
    (export / "conversations-000.json").write_text(json.dumps(wrapped), encoding="utf-8")

    observations = extract_chatgpt_observations(export)
    by_ref = {item.source_reference: item for item in observations}

    assert "conversation:conv-1:message:m-image" not in by_ref
    user = by_ref["conversation:conv-1:message:m-user"]
    assert user.content == "Project Atlas is active."
    assert user.author_role == "user"
    assert user.conversation_title == "Atlas planning"
    assert user.observed_at == "2023-11-14T22:13:20Z"
    assert by_ref["conversation:conv-1:message:m-code"].content == "Hermes Umbrella aka Hermes."
    assert by_ref["conversation:conv-1:message:m-code"].author_role == "assistant"
    context = by_ref["conversation:conv-1:message:m-context"]
    assert "Keeps a personal world." in context.content
    assert "Prefer evidence." in context.content
    assert context.observed_at == "2023-11-14T22:13:23Z"


def test_zip_and_direct_json_exports_ingest_into_a_valid_world(tmp_path: Path) -> None:
    conversation = _conversation()
    zip_path = tmp_path / "chatgpt-export.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("conversations.json", json.dumps([conversation]))
        archive.writestr("__MACOSX/conversations.json", json.dumps([{"id": "junk", "mapping": {}}]))

    direct = tmp_path / "conversations.json"
    direct.write_text(json.dumps({"conversations": [conversation]}), encoding="utf-8")

    for source in (zip_path, direct):
        world_path = tmp_path / f"world-{source.suffix.strip('.') or 'file'}"
        init_world(world_path, name="Export World", description="Real export shape")
        result = ingest_source(
            world_path,
            source_type="chatgpt_export",
            source_name=source.name,
            source_path=source,
            origin=f"fixture://{source.name}",
        )
        assert result is not None
        assert result["observations"] == 3
        errors = validate_world(world_path)
        assert errors == []
        assert rebuild_index(world_path).exists()
        stored = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in (world_path / "observations").glob("*.json")
        ]
        assert {item["author_role"] for item in stored} == {"user", "assistant", "system"}
        assert all(item["observed_at"].endswith("Z") for item in stored)
        aliases = []
        for path in (world_path / "entities").glob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if payload["label"] == "Hermes Umbrella":
                aliases = payload["aliases"]
        assert "Hermes" in aliases


def test_missing_conversations_file_reports_the_export_layout(tmp_path: Path) -> None:
    empty = tmp_path / "empty-export"
    empty.mkdir()
    try:
        extract_chatgpt_observations(empty)
    except FileNotFoundError as exc:
        assert "conversations" in str(exc)
    else:
        raise AssertionError("expected FileNotFoundError")
