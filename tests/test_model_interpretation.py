from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from worldgen.contracts import validate_world
from worldgen.ingest import ingest_source
from worldgen.models import ModelConfig, complete_with_litellm, resolve_model_config
from worldgen.recipes import run_recipe
from worldgen.world import init_world

FIXTURES = Path(__file__).parent / "fixtures"


def _ingest(world_path: Path, **kwargs):
    return ingest_source(
        world_path,
        source_type="chatgpt_export",
        source_name="chatgpt-fixture",
        source_path=FIXTURES / "chatgpt_export",
        origin="fixture://chatgpt",
        **kwargs,
    )


def test_resolve_model_config_uses_ollama_base_when_flag_is_absent(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_API_BASE", "http://ollama.lan:11434")
    monkeypatch.delenv("OPENAI_API_BASE", raising=False)
    config = resolve_model_config("ollama/qwen2.5", None)
    assert config == ModelConfig(model="ollama/qwen2.5", api_base="http://ollama.lan:11434")
    assert resolve_model_config("  ", None) is None


def test_litellm_completion_targets_the_configured_api_base(monkeypatch) -> None:
    captured: dict = {}

    def fake_completion(**kwargs):
        captured.update(kwargs)
        message = SimpleNamespace(content='{"entities": [], "assertions": []}')
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    monkeypatch.setitem(__import__("sys").modules, "litellm", SimpleNamespace(completion=fake_completion))
    payload = complete_with_litellm(ModelConfig("ollama/qwen2.5", "http://10.0.0.5:11434"), "extract")
    assert payload == {"entities": [], "assertions": []}
    assert captured["model"] == "ollama/qwen2.5"
    assert captured["api_base"] == "http://10.0.0.5:11434"
    assert captured["messages"][0]["content"] == "extract"


def test_configured_model_adds_candidate_interpretations_once(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    calls: list[ModelConfig] = []

    def complete(config: ModelConfig, prompt: str) -> dict:
        calls.append(config)
        assert "Project Atlas is active." in prompt
        return {
            "entities": [{"label": "Project Atlas", "aliases": ["Atlas"]}],
            "assertions": [{"subject": "Project Atlas", "predicate": "is", "object": "a personal archive"}],
        }

    config = ModelConfig("ollama/qwen2.5", "http://10.0.0.5:11434")
    first = _ingest(world_path, model=config, complete=complete)
    assert first is not None
    assert calls and calls[0].api_base == "http://10.0.0.5:11434"
    assertions = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (world_path / "assertions").glob("*.json")
    ]
    interpreted = [item for item in assertions if item["interpretation_level"] == "interpretation"]
    assert len(interpreted) == 1
    assert interpreted[0]["status"] == "conflicting"
    assert interpreted[0]["conflicts_with"]
    assert interpreted[0]["object_text"] == "a personal archive"
    assert interpreted[0]["model"] == "ollama/qwen2.5"
    atlas = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (world_path / "entities").glob("*.json")
        if json.loads(path.read_text(encoding="utf-8"))["label"] == "Project Atlas"
    ]
    assert atlas and "Atlas" in atlas[0]["aliases"]
    assert validate_world(world_path) == []

    calls.clear()
    second = _ingest(world_path, model=config, complete=complete)
    assert second is None
    assert calls == []


def test_model_interpretation_can_follow_a_deterministic_ingest(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    assert _ingest(world_path) is not None
    before = len(list((world_path / "observations").glob("*.json")))

    def complete(_config: ModelConfig, _prompt: str) -> dict:
        return {
            "entities": [],
            "assertions": [{"subject": "Project Atlas", "predicate": "is", "object": "worth keeping"}],
        }

    second = _ingest(world_path, model=ModelConfig("ollama/qwen2.5", "http://10.0.0.5:11434"), complete=complete)
    assert second is not None
    assert second["interpreted_assertions"] == 1
    assert len(list((world_path / "observations").glob("*.json"))) == before


def test_recipe_ingest_passes_litellm_model_to_execution_metadata(tmp_path: Path, monkeypatch) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    seen: list[ModelConfig] = []

    def fake(config: ModelConfig, _prompt: str) -> dict:
        seen.append(config)
        return {"entities": [], "assertions": []}

    monkeypatch.setattr("worldgen.ingest.complete_with_litellm", fake)
    execution = run_recipe(
        world_path,
        "ingest-source",
        {
            "source_type": "chatgpt_export",
            "source_name": "chatgpt-fixture",
            "source_path": str(FIXTURES / "chatgpt_export"),
            "origin": "fixture://chatgpt",
            "model": "ollama/llama3.1",
            "model_api_base": "http://ollama.lan:11434",
        },
    )
    assert execution["status"] == "completed"
    assert seen == [ModelConfig(model="ollama/llama3.1", api_base="http://ollama.lan:11434")]
    assert execution["runtime"]["model_metadata"] == {
        "provider": "litellm",
        "model": "ollama/llama3.1",
        "api_base": "http://ollama.lan:11434",
    }
