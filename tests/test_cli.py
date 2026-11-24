from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from worldgen.cli import main

FIXTURES = Path(__file__).parent / "fixtures"


def test_click_cli_init_ingest_and_validate_fixture_export(tmp_path: Path) -> None:
    runner = CliRunner()
    world_path = tmp_path / "world"
    env = {"WORLDGEN_MODEL": "", "WORLDGEN_MODEL_API_BASE": "", "OLLAMA_API_BASE": "", "OPENAI_API_BASE": ""}

    init = runner.invoke(
        main,
        ["init", str(world_path), "--name", "Demo World", "--description", "Synthetic demo"],
        env=env,
    )
    assert init.exit_code == 0, init.output
    assert "initialized world" in init.output

    ingest = runner.invoke(
        main,
        [
            "ingest",
            str(world_path),
            "chatgpt_export",
            str(FIXTURES / "chatgpt_export"),
            "--source-name",
            "chatgpt fixture",
            "--origin",
            "fixture://chatgpt",
        ],
        env=env,
    )
    assert ingest.exit_code == 0, ingest.output
    payload = json.loads(ingest.output)
    assert payload["observations"] > 0

    validate = runner.invoke(main, ["validate", str(world_path)], env=env)
    assert validate.exit_code == 0, validate.output
    assert "world is valid" in validate.output

    help_result = runner.invoke(main, ["--help"], env=env)
    assert help_result.exit_code == 0
    assert "recipe" in help_result.output
    assert "ingest" in help_result.output


def test_ingest_help_documents_optional_ollama_model() -> None:
    result = CliRunner().invoke(main, ["ingest", "--help"])
    assert result.exit_code == 0
    assert "--model" in result.output
    assert "--model-api-base" in result.output
    assert "ollama" in result.output.lower()
