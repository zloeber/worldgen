from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_text(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip().lower())
    return re.sub(r"[^a-z0-9 _-]", "", cleaned)


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_file():
        with path.open("rb") as fh:
            while chunk := fh.read(8192):
                digest.update(chunk)
        return digest.hexdigest()
    files = sorted([p for p in path.rglob("*") if p.is_file()])
    for file in files:
        digest.update(str(file.relative_to(path)).encode("utf-8"))
        with file.open("rb") as fh:
            while chunk := fh.read(8192):
                digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
