from __future__ import annotations

from pathlib import Path

from .contracts import CONTRACT_VERSION
from .utils import stable_id, utc_now, write_json

WORLD_DIRS = [
    "sources/manifests",
    "sources/raw",
    "sources/excerpts",
    "observations",
    "entities",
    "relationships",
    "assertions",
    "evidence",
    "contexts",
    "proposals",
    "indexes/sqlite",
]


def init_world(path: Path, name: str, description: str) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    for directory in WORLD_DIRS:
        (path / directory).mkdir(parents=True, exist_ok=True)

    world_id = stable_id("world", name)
    write_json(
        path / "world.json",
        {
            "id": world_id,
            "kind": "World",
            "contract_version": CONTRACT_VERSION,
            "created_at": utc_now(),
            "status": "active",
            "name": name,
            "description": description,
        },
    )

    (path / "sources" / "ingest-log.jsonl").touch(exist_ok=True)
    (path / ".gitignore").write_text("sources/raw/\n", encoding="utf-8")
    return path
