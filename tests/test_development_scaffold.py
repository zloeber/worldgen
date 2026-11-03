from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def test_development_scaffold_files_exist() -> None:
    required_paths = [
        "AGENTS.md",
        ".mex/ROUTER.md",
        ".mex/context/architecture.md",
        ".mex/context/implementation.md",
        ".mex/context/conventions.md",
        ".mex/context/decisions.md",
        ".mex/context/roadmap.md",
        ".mex/continuity/CURRENT.md",
        ".mex/continuity/DEVELOPMENT.md",
        ".mex/patterns/INDEX.md",
        ".agents/skills/worldgen-development/SKILL.md",
        "docs/development/adr-0002-development-context-scaffold.md",
    ]
    for relpath in required_paths:
        assert (REPO_ROOT / relpath).exists(), f"missing {relpath}"


def test_agent_entrypoint_routes_to_router_and_continuity() -> None:
    agents = _read("AGENTS.md")
    assert ".mex/ROUTER.md" in agents
    assert ".mex/continuity/CURRENT.md" in agents
    assert "implemented behavior" in agents.lower()


def test_pattern_documents_follow_required_sections() -> None:
    required_sections = [
        "## Context",
        "## Steps",
        "## Gotchas",
        "## Verify",
        "## Debug",
        "## Update Scaffold",
    ]
    pattern_dir = REPO_ROOT / ".mex" / "patterns"
    for path in sorted(pattern_dir.glob("*.md")):
        if path.name == "INDEX.md":
            continue
        content = path.read_text(encoding="utf-8")
        assert content.startswith("# Pattern:"), f"{path.name} missing title format"
        for section in required_sections:
            assert section in content, f"{path.name} missing {section}"


def test_continuity_docs_are_distinct_roles() -> None:
    current = _read(".mex/continuity/CURRENT.md")
    development = _read(".mex/continuity/DEVELOPMENT.md")
    assert "## Current milestone and objective" in current
    assert "## 202" in development
    assert "Current Development Snapshot" in current
    assert "Development History" in development
