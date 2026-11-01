from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .contracts import CONTRACT_VERSION
from .utils import normalize_text, read_json, stable_id, utc_now, write_json

STOPWORDS = {"the", "and", "with", "from", "for", "this", "that", "project"}


def _load_entities(world_path: Path) -> list[dict]:
    return [read_json(path) for path in sorted((world_path / "entities").glob("*.json"))]


def _load_relationships(world_path: Path) -> list[dict]:
    return [read_json(path) for path in sorted((world_path / "relationships").glob("*.json"))]


def generate_domain_proposals(world_path: Path) -> list[str]:
    proposal_ids = []
    proposal_ids.append(_proposal_by_token_frequency(world_path))
    proposal_ids.append(_proposal_by_connected_components(world_path))
    return proposal_ids


def _proposal_by_token_frequency(world_path: Path) -> str:
    entities = _load_entities(world_path)
    token_counter: Counter[str] = Counter()
    domain_members: dict[str, list[str]] = defaultdict(list)
    for entity in entities:
        for token in normalize_text(entity["label"]).split():
            if len(token) < 3 or token in STOPWORDS:
                continue
            token_counter[token] += 1
            domain_members[token].append(entity["id"])
    top_tokens = [token for token, count in token_counter.most_common(5) if count > 1]
    body = {
        "candidate_domains": [
            {"domain": token, "entity_ids": sorted(set(domain_members[token]))} for token in top_tokens
        ]
    }
    proposal_id = stable_id("proposal", "domain", "token-frequency", str(top_tokens))
    write_json(
        world_path / "proposals" / f"{proposal_id}.json",
        {
            "id": proposal_id,
            "kind": "Proposal",
            "contract_version": CONTRACT_VERSION,
            "created_at": utc_now(),
            "status": "proposed",
            "title": "Candidate conceptual domains from token frequency",
            "proposal_type": "organizational_structure",
            "approach": "token_frequency",
            "evidence_ids": [],
            "body": body,
        },
    )
    return proposal_id


def _proposal_by_connected_components(world_path: Path) -> str:
    entities = _load_entities(world_path)
    relationships = _load_relationships(world_path)
    graph: dict[str, set[str]] = {entity["id"]: set() for entity in entities}
    for rel in relationships:
        graph.setdefault(rel["from_entity_id"], set()).add(rel["to_entity_id"])
        graph.setdefault(rel["to_entity_id"], set()).add(rel["from_entity_id"])
    components: list[list[str]] = []
    visited: set[str] = set()
    for node in sorted(graph):
        if node in visited:
            continue
        stack = [node]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(sorted(graph.get(current, set()) - visited))
        if component:
            components.append(sorted(component))
    proposal_id = stable_id("proposal", "domain", "connected-components", str(components))
    write_json(
        world_path / "proposals" / f"{proposal_id}.json",
        {
            "id": proposal_id,
            "kind": "Proposal",
            "contract_version": CONTRACT_VERSION,
            "created_at": utc_now(),
            "status": "proposed",
            "title": "Candidate conceptual domains from relationship communities",
            "proposal_type": "organizational_structure",
            "approach": "connected_components",
            "evidence_ids": [],
            "body": {"candidate_domains": components},
        },
    )
    return proposal_id
