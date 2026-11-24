from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import click

from .contracts import validate_world
from .indexer import rebuild_index
from .ingest import ingest_source
from .models import resolve_model_config
from .proposals import generate_domain_proposals
from .recipes import compose_workflow, list_execution_history, recipe_catalog_by_id, run_recipe
from .world import init_world


@click.group()
def main() -> None:
    """Local-first world package tools."""


@main.command("init")
@click.argument("path")
@click.option("--name", required=True)
@click.option("--description", default="Personal world", show_default=True)
def init_cmd(path: str, name: str, description: str) -> None:
    """Initialize a world package."""
    init_world(Path(path), name=name, description=description)
    click.echo(f"initialized world at {path}")


@main.command("ingest")
@click.argument("path")
@click.argument("source_type", type=click.Choice(["chatgpt_export", "markdown_repo"]))
@click.argument("source_path")
@click.option("--source-name", required=True)
@click.option("--origin", required=True)
@click.option(
    "--model",
    default=None,
    envvar="WORLDGEN_MODEL",
    help="Optional LiteLLM model, such as ollama/llama3.1. Omit to keep ingestion deterministic.",
)
@click.option(
    "--model-api-base",
    default=None,
    envvar="WORLDGEN_MODEL_API_BASE",
    help="API base for the model. Use an Ollama server such as http://host:11434. Falls back to OLLAMA_API_BASE.",
)
def ingest_cmd(
    path: str,
    source_type: str,
    source_path: str,
    source_name: str,
    origin: str,
    model: str | None,
    model_api_base: str | None,
) -> None:
    """Ingest a ChatGPT export or markdown repository."""
    try:
        result = ingest_source(
            world_path=Path(path),
            source_type=source_type,
            source_name=source_name,
            source_path=Path(source_path),
            origin=origin,
            model=resolve_model_config(model, model_api_base),
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        raise click.ClickException(str(exc)) from exc
    if result is None:
        click.echo("source unchanged; ingestion skipped (idempotent)")
        return
    click.echo(json.dumps(result, sort_keys=True))


@main.command("validate")
@click.argument("path")
def validate_cmd(path: str) -> None:
    """Validate canonical world records."""
    errors = validate_world(Path(path))
    if errors:
        for error in errors:
            click.echo(f"ERROR {error.path}: {error.message}")
        raise SystemExit(1)
    click.echo("world is valid")


@main.command("index")
@click.argument("path")
def index_cmd(path: str) -> None:
    """Rebuild the derived SQLite index."""
    db = rebuild_index(Path(path))
    click.echo(f"rebuilt index at {db}")


@main.command("propose")
@click.argument("path")
def propose_cmd(path: str) -> None:
    """Generate organizational domain proposals."""
    proposal_ids = generate_domain_proposals(Path(path))
    click.echo("\n".join(proposal_ids))


def _print_query_rows(path: str, view: str) -> None:
    db_path = Path(path) / "indexes" / "sqlite" / "world.db"
    conn = sqlite3.connect(db_path)
    try:
        if view == "summary":
            for row in conn.execute("SELECT kind, COUNT(*) FROM records GROUP BY kind ORDER BY kind").fetchall():
                click.echo(f"{row[0]}: {row[1]}")
        elif view == "assertions":
            query = """
            SELECT a.id, e.label, a.predicate, a.object_text, a.status
            FROM assertions a
            JOIN entities e ON e.id = a.subject_entity_id
            ORDER BY e.label, a.object_text
            """
            for row in conn.execute(query).fetchall():
                click.echo(f"{row[0]} | {row[1]} {row[2]} {row[3]} [{row[4]}]")
        elif view == "proposals":
            for row in conn.execute("SELECT id, title, approach, status FROM proposals ORDER BY id").fetchall():
                click.echo(" | ".join(row))
        elif view == "conflicts":
            query = """
            SELECT a.id, e.label, a.object_text, a.conflicts_with_json
            FROM assertions a
            JOIN entities e ON e.id = a.subject_entity_id
            WHERE a.status = 'conflicting'
            ORDER BY e.label, a.id
            """
            for row in conn.execute(query).fetchall():
                click.echo(f"{row[0]} | {row[1]} is {row[2]} | conflicts_with={row[3]}")
    finally:
        conn.close()


@main.command("explore")
@click.argument("path")
@click.argument("view", type=click.Choice(["summary", "assertions", "proposals"]))
def explore_cmd(path: str, view: str) -> None:
    """Inspect the derived index."""
    _print_query_rows(path, view)


@main.command("review")
@click.argument("path")
@click.argument("topic", type=click.Choice(["proposals", "conflicts"]))
def review_cmd(path: str, topic: str) -> None:
    """Review proposals or conflicting assertions."""
    _print_query_rows(path, topic)


@main.group("recipe")
def recipe() -> None:
    """List, compose, run, and review recipe executions."""


@recipe.command("list")
@click.argument("path")
def recipe_list(path: str) -> None:
    """List recipes seeded in a world."""
    catalog = recipe_catalog_by_id(Path(path))
    payload = [
        {
            "id": item["id"],
            "version": item["version"],
            "name": item["name"],
            "implementation_status": item["implementation_status"],
            "depends_on": item["depends_on"],
        }
        for item in sorted(catalog.values(), key=lambda x: x["id"])
    ]
    click.echo(json.dumps(payload, indent=2, sort_keys=True))


@recipe.command("run")
@click.argument("path")
@click.argument("recipe_id")
@click.option("--inputs-json", default="{}", show_default=True)
@click.option("--include-dependencies", is_flag=True)
@click.option("--model", default=None, envvar="WORLDGEN_MODEL", help="Optional LiteLLM model, such as ollama/llama3.1.")
@click.option(
    "--model-api-base",
    default=None,
    envvar="WORLDGEN_MODEL_API_BASE",
    help="API base for the model, such as an Ollama server. Falls back to OLLAMA_API_BASE.",
)
def recipe_run(
    path: str,
    recipe_id: str,
    inputs_json: str,
    include_dependencies: bool,
    model: str | None,
    model_api_base: str | None,
) -> None:
    """Run a recipe, optionally including its dependencies."""
    workflow = [recipe_id]
    if include_dependencies:
        workflow = compose_workflow(Path(path), [recipe_id])
    try:
        input_payload = json.loads(inputs_json)
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"invalid inputs-json: {exc}") from exc
    if not isinstance(input_payload, dict):
        raise click.ClickException("inputs-json must be an object")
    if model:
        input_payload["model"] = model
    if model_api_base:
        input_payload["model_api_base"] = model_api_base
    executions = []
    for item_id in workflow:
        execution = run_recipe(
            Path(path),
            recipe_id=item_id,
            inputs=input_payload if item_id == recipe_id else {},
        )
        executions.append(
            {
                "recipe_id": execution["recipe_id"],
                "recipe_version": execution["recipe_version"],
                "execution_id": execution["execution_id"],
                "status": execution["status"],
                "execution_path": execution["execution_path"],
            }
        )
    click.echo(json.dumps(executions, indent=2, sort_keys=True))


@recipe.command("history")
@click.argument("path")
def recipe_history(path: str) -> None:
    """Show recipe execution history."""
    history = list_execution_history(Path(path))
    payload = [
        {
            "execution_id": item["execution_id"],
            "recipe_id": item["recipe_id"],
            "recipe_version": item["recipe_version"],
            "status": item["status"],
            "started_at": item["started_at"],
            "completed_at": item["completed_at"],
        }
        for item in history
    ]
    click.echo(json.dumps(payload, indent=2, sort_keys=True))


@recipe.command("compose")
@click.argument("path")
@click.argument("recipe_ids", nargs=-1, required=True)
def recipe_compose(path: str, recipe_ids: tuple[str, ...]) -> None:
    """Print a dependency-ordered recipe workflow."""
    order = compose_workflow(Path(path), list(recipe_ids))
    click.echo(json.dumps(order, indent=2))


if __name__ == "__main__":
    main()
