from __future__ import annotations

import sqlite3
from pathlib import Path

from .utils import read_json

SCHEMA = """
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS entities;
DROP TABLE IF EXISTS assertions;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS proposals;

CREATE TABLE records (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  status TEXT NOT NULL
);

CREATE TABLE entities (
  id TEXT PRIMARY KEY,
  label TEXT NOT NULL,
  normalized_label TEXT NOT NULL,
  aliases_json TEXT NOT NULL
);

CREATE TABLE assertions (
  id TEXT PRIMARY KEY,
  subject_entity_id TEXT NOT NULL,
  predicate TEXT NOT NULL,
  object_text TEXT NOT NULL,
  status TEXT NOT NULL,
  interpretation_level TEXT NOT NULL,
  confidence REAL NOT NULL,
  source_id TEXT,
  conflicts_with_json TEXT NOT NULL
);

CREATE TABLE evidence (
  id TEXT PRIMARY KEY,
  source_id TEXT NOT NULL,
  source_reference TEXT NOT NULL,
  excerpt TEXT NOT NULL
);

CREATE TABLE proposals (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  approach TEXT NOT NULL,
  status TEXT NOT NULL,
  evidence_ids_json TEXT NOT NULL
);
"""


def rebuild_index(world_path: Path) -> Path:
    db_path = world_path / "indexes" / "sqlite" / "world.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        for file in sorted(world_path.rglob("*.json")):
            if file == db_path:
                continue
            rel = file.relative_to(world_path)
            if rel.parts[:2] == ("indexes", "sqlite"):
                continue
            if rel.parts[:2] == ("sources", "raw"):
                continue
            record = read_json(file)
            if not isinstance(record, dict) or "id" not in record or "kind" not in record:
                continue
            conn.execute(
                "INSERT OR REPLACE INTO records (id, kind, status) VALUES (?, ?, ?)",
                (record["id"], record["kind"], record.get("status", "unknown")),
            )
            if record["kind"] == "Entity":
                import json

                conn.execute(
                    "INSERT OR REPLACE INTO entities (id, label, normalized_label, aliases_json) VALUES (?, ?, ?, ?)",
                    (
                        record["id"],
                        record["label"],
                        record["normalized_label"],
                        json.dumps(record.get("aliases", []), sort_keys=True),
                    ),
                )
            elif record["kind"] == "Assertion":
                import json

                conn.execute(
                    "INSERT OR REPLACE INTO assertions (id, subject_entity_id, predicate, object_text, status, interpretation_level, confidence, source_id, conflicts_with_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        record["id"],
                        record["subject_entity_id"],
                        record["predicate"],
                        record["object_text"],
                        record["status"],
                        record.get("interpretation_level", "source_claim"),
                        float(record.get("confidence", 0.0)),
                        record.get("source_id"),
                        json.dumps(record.get("conflicts_with", []), sort_keys=True),
                    ),
                )
            elif record["kind"] == "Evidence":
                conn.execute(
                    "INSERT OR REPLACE INTO evidence (id, source_id, source_reference, excerpt) VALUES (?, ?, ?, ?)",
                    (
                        record["id"],
                        record["source_id"],
                        record["source_reference"],
                        record["excerpt"],
                    ),
                )
            elif record["kind"] == "Proposal":
                import json

                conn.execute(
                    "INSERT OR REPLACE INTO proposals (id, title, approach, status, evidence_ids_json) VALUES (?, ?, ?, ?, ?)",
                    (
                        record["id"],
                        record["title"],
                        record["approach"],
                        record["status"],
                        json.dumps(record["evidence_ids"], sort_keys=True),
                    ),
                )
        conn.commit()
    finally:
        conn.close()
    return db_path
