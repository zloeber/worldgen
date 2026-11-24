from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Iterable

from .utils import normalize_text

_CONVERSATION_FILE = re.compile(r"conversations(?:-\d+)?\.json$", re.IGNORECASE)
_MISSING_EXPORT = "could not locate conversations.json or conversations-*.json in ChatGPT export"


@dataclass(slots=True)
class ExtractedObservation:
    source_reference: str
    observed_at: str
    content: str
    author_role: str | None = None
    conversation_title: str | None = None


def _to_observed_at(value: object) -> str:
    if isinstance(value, str):
        text = value.strip()
        if text.endswith("+00:00"):
            text = f"{text[:-6]}Z"
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z", text):
            return text
        try:
            value = float(text)
        except ValueError:
            return "1970-01-01T00:00:00Z"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        timestamp = float(value)
        if timestamp > 10_000_000_000:
            timestamp = timestamp / 1000.0
        if timestamp < 0:
            timestamp = 0
        moment = datetime.fromtimestamp(timestamp, UTC).replace(microsecond=0)
        return moment.isoformat().replace("+00:00", "Z")
    return "1970-01-01T00:00:00Z"


def _is_conversation_name(name: str) -> bool:
    path = PurePosixPath(name)
    if any(part == "__MACOSX" or part.startswith("._") for part in path.parts):
        return False
    if _CONVERSATION_FILE.fullmatch(path.name):
        return True
    return len(path.parts) >= 2 and path.parts[-2] == "conversations" and path.suffix.lower() == ".json"


def _coerce_conversations(payload: object, origin: str) -> list[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        conversations = payload.get("conversations")
        if isinstance(conversations, list):
            return [item for item in conversations if isinstance(item, dict)]
        if "mapping" in payload:
            return [payload]
    raise ValueError(f"unrecognized ChatGPT export JSON in {origin}")


def _load_conversation_text(text: str, origin: str) -> list[dict]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in ChatGPT export {origin}: {exc}") from exc
    return _coerce_conversations(payload, origin)


def _iter_conversation_documents(export_path: Path) -> list[tuple[str, str]]:
    if export_path.is_file() and export_path.suffix.lower() == ".zip":
        with zipfile.ZipFile(export_path) as archive:
            names = sorted(name for name in archive.namelist() if _is_conversation_name(name) and not name.endswith("/"))
            if not names:
                raise FileNotFoundError(_MISSING_EXPORT)
            return [(name, archive.read(name).decode("utf-8")) for name in names]
    if export_path.is_file() and export_path.suffix.lower() == ".json":
        return [(export_path.name, export_path.read_text(encoding="utf-8"))]
    if export_path.is_dir():
        files = sorted(
            path
            for path in export_path.rglob("*.json")
            if path.is_file() and _is_conversation_name(path.relative_to(export_path).as_posix())
        )
        if not files:
            raise FileNotFoundError(_MISSING_EXPORT)
        return [(path.relative_to(export_path).as_posix(), path.read_text(encoding="utf-8")) for path in files]
    raise FileNotFoundError(_MISSING_EXPORT)


def _text_from_part(part: object) -> str:
    if isinstance(part, str):
        return part.strip()
    if isinstance(part, dict):
        for key in ("text", "content", "result"):
            value = part.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _text_from_content(content: object) -> str:
    if not isinstance(content, dict):
        return ""
    chunks: list[str] = []
    parts = content.get("parts")
    if isinstance(parts, list):
        for part in parts:
            text = _text_from_part(part)
            if text and text not in chunks:
                chunks.append(text)
    for key in ("text", "result", "user_instructions", "user_profile", "thoughts"):
        value = content.get(key)
        if isinstance(value, str):
            text = value.strip()
            if text and text not in chunks:
                chunks.append(text)
    return " ".join(chunks).strip()


def _observations_from_conversation(convo: dict) -> list[ExtractedObservation]:
    convo_id = convo.get("id") or convo.get("conversation_id") or "unknown-conversation"
    title = convo.get("title")
    conversation_title = title.strip() if isinstance(title, str) and title.strip() else None
    mapping = convo.get("mapping") or {}
    if not isinstance(mapping, dict):
        return []
    observations: list[ExtractedObservation] = []
    for message_id, node in mapping.items():
        if not isinstance(node, dict):
            continue
        message = node.get("message") or {}
        if not isinstance(message, dict):
            continue
        content = _text_from_content(message.get("content"))
        if not content:
            continue
        author = message.get("author") if isinstance(message.get("author"), dict) else {}
        role = author.get("role") if isinstance(author, dict) else None
        author_role = role.strip() if isinstance(role, str) and role.strip() else None
        observations.append(
            ExtractedObservation(
                source_reference=f"conversation:{convo_id}:message:{message_id}",
                observed_at=_to_observed_at(message.get("create_time") if message.get("create_time") is not None else convo.get("create_time")),
                content=content,
                author_role=author_role,
                conversation_title=conversation_title,
            )
        )
    return observations


def extract_chatgpt_observations(export_path: Path) -> list[ExtractedObservation]:
    observations: list[ExtractedObservation] = []
    for origin, text in _iter_conversation_documents(export_path):
        for convo in _load_conversation_text(text, origin):
            observations.extend(_observations_from_conversation(convo))
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
