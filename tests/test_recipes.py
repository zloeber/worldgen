from __future__ import annotations

from pathlib import Path

from worldgen.contracts import validate_world
from worldgen.recipes import (
    compose_workflow,
    list_execution_history,
    recipe_catalog_by_id,
    run_recipe,
    validate_recipe_definition,
)
from worldgen.world import init_world

FIXTURES = Path(__file__).parent / "fixtures"


def test_world_includes_recipe_catalog_on_init(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    catalog = recipe_catalog_by_id(world_path)
    assert "ingest-source" in catalog
    assert (world_path / "recipes" / "definitions").exists()
    assert (world_path / "recipes" / "executions").exists()
    assert validate_world(world_path) == []


def test_recipe_definition_validation_errors() -> None:
    bad_definition = {
        "id": "",
        "version": "0.0.1",
        "inputs": {},
        "implementation_status": "invalid",
    }
    errors = validate_recipe_definition(bad_definition)
    assert any("missing field" in error for error in errors)
    assert "id must be a non-empty string" in errors
    assert "version must match recipe contract version" in errors
    assert "inputs.required must be a list" in errors
    assert "inputs.optional must be a list" in errors
    assert "implementation_status must be implemented or planned" in errors


def test_recipe_execution_history_and_reproducibility_metadata(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    seed_execution = run_recipe(
        world_path,
        "seed-foundation",
        {
            "perspective": "personal",
            "purpose": "organize project understanding",
            "boundaries": ["synthetic fixtures only"],
            "principles": ["evidence always"],
            "discovery_agenda": ["ingest first"],
        },
    )
    assert seed_execution["status"] == "completed"
    assert seed_execution["runtime"]["agent_independent"] is True
    assert seed_execution["reproducibility"]["execution_contract_version"] == "1.0.0"

    ingest_execution = run_recipe(
        world_path,
        "ingest-source",
        {
            "source_type": "chatgpt_export",
            "source_name": "chatgpt-fixture",
            "source_path": str(FIXTURES / "chatgpt_export"),
            "origin": "fixture://chatgpt",
            "model_metadata": {
                "provider": "none",
                "model": "none",
            },
        },
    )
    assert ingest_execution["status"] == "completed"
    assert ingest_execution["outputs"]["ingest_result"] is not None
    assert ingest_execution["outputs"]["source_id"].startswith("source-")
    history = list_execution_history(world_path)
    assert len(history) == 2
    recipe_ids = {item["recipe_id"] for item in history}
    assert recipe_ids == {"seed-foundation", "ingest-source"}


def test_recipe_failure_records_execution_without_world_mutation(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    execution = run_recipe(world_path, "ingest-source", {"source_type": "chatgpt_export"})
    assert execution["status"] == "failed"
    assert execution["failure"] is not None
    assert execution["proposed_mutations"] == []
    assert validate_world(world_path) == []


def test_recipe_composition_resolves_dependencies(tmp_path: Path) -> None:
    world_path = tmp_path / "world"
    init_world(world_path, name="Fixture World", description="Synthetic data world")
    order = compose_workflow(world_path, ["discover-domains"])
    assert order == ["seed-foundation", "ingest-source", "discover-domains"]
