from __future__ import annotations

import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_project_builds_with_uv_and_declares_runtime_dependencies() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["build-system"]["build-backend"] == "hatchling.build"
    assert "hatchling" in " ".join(project["build-system"]["requires"])
    dependencies = project["project"]["dependencies"]
    assert any(item.startswith("click") for item in dependencies)
    assert any(item.startswith("litellm") for item in dependencies)
    assert project["project"]["scripts"]["worldgen"] == "worldgen.cli:main"
