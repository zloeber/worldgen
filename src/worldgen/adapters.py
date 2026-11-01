from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .utils import normalize_text


@dataclass(slots=True)
class ExtractedObservation:
    source_reference: str
    observed_at: str
    content: str


def _find_chatgpt_export_file(export_path: Path) -> Path:
    candidates = [
        export_path / "conversations.json",
        export_path / "data" / "conversations.json",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("could not locate conversations.json in ChatGPT export")


def extract_chatgpt_observations(export_path: Path) -> list[ExtractedObservation]:
    conversations_file = _find_chatgpt_export_file(export_path)
    payload = json.loads(conversations_file.read_text(encoding="utf-8"))
    observations: list[ExtractedObservation] = []
    for convo in payload:
        convo_id = convo.get("id") or convo.get("conversation_id") or "unknown-conversation"
        mapping = convo.get("mapping", {})
        for message_id, node in mapping.items():
            message = node.get("message") or {}
            content = message.get("content") or {}
            parts = content.get("parts") or []
            text = " ".join(part for part in parts if isinstance(part, str)).strip()
            if not text:
                continue
            observed_at = message.get("create_time") or convo.get("create_time") or "1970-01-01T00:00:00Z"
            observations.append(
                ExtractedObservation(
                    source_reference=f"conversation:{convo_id}:message:{message_id}",
                    observed_at=str(observed_at),
                    content=text,
                )
            )
    return observations


def extract_markdown_repo_observations(repo_path: Path) -> list[ExtractedObservation]:
    observations: list[ExtractedObservation] = []
    for md_file in sorted(repo_path.rglob("*.md")):
        rel = md_file.relative_to(repo_path)
        for line_no, line in enumerate(md_file.read_text(encoding="utf-8").splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            observations.append(
                ExtractedObservation(
                    source_reference=f"{rel}:L{line_no}",
                    observed_at="1970-01-01T00:00:00Z",
                    content=text,
                )
            )
    return observations


ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*)\b")
ALIAS_PATTERN = re.compile(r"(?P<main>[A-Z][\w ]+?)\s+(?:aka|AKA)\s+(?P<alias>[A-Z][\w ]+)")
IS_PATTERN = re.compile(r"(?P<subject>[A-Z][\w ]+?)\s+is\s+(?P<object>[^.]+)", re.IGNORECASE)


def extract_entity_candidates(text: str) -> list[str]:
    values = {match.group(1).strip() for match in ENTITY_PATTERN.finditer(text)}
    return sorted(v for v in values if len(normalize_text(v)) > 2)


def extract_alias_pairs(text: str) -> list[tuple[str, str]]:
    return [(m.group("main").strip(), m.group("alias").strip()) for m in ALIAS_PATTERN.finditer(text)]


def extract_is_assertions(text: str) -> Iterable[tuple[str, str]]:
    for match in IS_PATTERN.finditer(text):
        yield (match.group("subject").strip(), match.group("object").strip())
