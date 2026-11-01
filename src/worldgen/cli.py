from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from .contracts import validate_world
from .indexer import rebuild_index
from .ingest import ingest_source
from .proposals import generate_domain_proposals
from .recipes import compose_workflow, list_execution_history, recipe_catalog_by_id, run_recipe
from .world import init_world


def _cmd_init(args: argparse.Namespace) -> int:
    init_world(Path(args.path), name=args.name, description=args.description)
    print(f"initialized world at {args.path}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    errors = validate_world(Path(args.path))
    if errors:
        for error in errors:
            print(f"ERROR {error.path}: {error.message}")
        return 1
    print("world is valid")
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    result = ingest_source(
        world_path=Path(args.path),
        source_type=args.source_type,
        source_name=args.source_name,
        source_path=Path(args.source_path),
        origin=args.origin,
    )
    if result is None:
        print("source unchanged; ingestion skipped (idempotent)")
        return 0
    print(json.dumps(result, sort_keys=True))
    return 0


def _cmd_index(args: argparse.Namespace) -> int:
    db = rebuild_index(Path(args.path))
    print(f"rebuilt index at {db}")
    return 0


def _cmd_propose(args: argparse.Namespace) -> int:
    proposal_ids = generate_domain_proposals(Path(args.path))
    print("\n".join(proposal_ids))
    return 0


def _cmd_explore(args: argparse.Namespace) -> int:
    db_path = Path(args.path) / "indexes" / "sqlite" / "world.db"
    conn = sqlite3.connect(db_path)
    try:
        if args.view == "summary":
            for row in conn.execute(
                "SELECT kind, COUNT(*) FROM records GROUP BY kind ORDER BY kind"
            ).fetchall():
                print(f"{row[0]}: {row[1]}")
        elif args.view == "assertions":
            query = """
            SELECT a.id, e.label, a.predicate, a.object_text, a.status
            FROM assertions a
            JOIN entities e ON e.id = a.subject_entity_id
            ORDER BY e.label, a.object_text
            """
            for row in conn.execute(query).fetchall():
                print(f"{row[0]} | {row[1]} {row[2]} {row[3]} [{row[4]}]")
        elif args.view == "proposals":
            for row in conn.execute(
                "SELECT id, title, approach, status FROM proposals ORDER BY id"
            ).fetchall():
                print(" | ".join(row))
    finally:
        conn.close()
    return 0


def _cmd_review(args: argparse.Namespace) -> int:
    db_path = Path(args.path) / "indexes" / "sqlite" / "world.db"
    conn = sqlite3.connect(db_path)
    try:
        if args.topic == "proposals":
            for row in conn.execute(
                "SELECT id, title, approach, status FROM proposals ORDER BY id"
            ).fetchall():
                print(" | ".join(row))
        elif args.topic == "conflicts":
            query = """
            SELECT a.id, e.label, a.object_text, a.conflicts_with_json
            FROM assertions a
            JOIN entities e ON e.id = a.subject_entity_id
            WHERE a.status = 'conflicting'
            ORDER BY e.label, a.id
            """
            for row in conn.execute(query).fetchall():
                print(f"{row[0]} | {row[1]} is {row[2]} | conflicts_with={row[3]}")
    finally:
        conn.close()
    return 0


def _cmd_recipe_list(args: argparse.Namespace) -> int:
    catalog = recipe_catalog_by_id(Path(args.path))
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
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _cmd_recipe_run(args: argparse.Namespace) -> int:
    workflow = [args.recipe_id]
    if args.include_dependencies:
        workflow = compose_workflow(Path(args.path), [args.recipe_id])
    input_payload = {}
    if args.inputs_json:
        input_payload = json.loads(args.inputs_json)
    executions = []
    for recipe_id in workflow:
        execution = run_recipe(Path(args.path), recipe_id=recipe_id, inputs=input_payload if recipe_id == args.recipe_id else {})
        executions.append(
            {
                "recipe_id": execution["recipe_id"],
                "recipe_version": execution["recipe_version"],
                "execution_id": execution["execution_id"],
                "status": execution["status"],
                "execution_path": execution["execution_path"],
            }
        )
    print(json.dumps(executions, indent=2, sort_keys=True))
    return 0


def _cmd_recipe_history(args: argparse.Namespace) -> int:
    history = list_execution_history(Path(args.path))
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
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _cmd_recipe_compose(args: argparse.Namespace) -> int:
    order = compose_workflow(Path(args.path), args.recipe_ids)
    print(json.dumps(order, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="worldgen")
    sub = parser.add_subparsers(dest="command", required=True)

    init_p = sub.add_parser("init")
    init_p.add_argument("path")
    init_p.add_argument("--name", required=True)
    init_p.add_argument("--description", default="Personal world")
    init_p.set_defaults(func=_cmd_init)

    ingest_p = sub.add_parser("ingest")
    ingest_p.add_argument("path")
    ingest_p.add_argument("source_type", choices=["chatgpt_export", "markdown_repo"])
    ingest_p.add_argument("source_path")
    ingest_p.add_argument("--source-name", required=True)
    ingest_p.add_argument("--origin", required=True)
    ingest_p.set_defaults(func=_cmd_ingest)

    validate_p = sub.add_parser("validate")
    validate_p.add_argument("path")
    validate_p.set_defaults(func=_cmd_validate)

    index_p = sub.add_parser("index")
    index_p.add_argument("path")
    index_p.set_defaults(func=_cmd_index)

    propose_p = sub.add_parser("propose")
    propose_p.add_argument("path")
    propose_p.set_defaults(func=_cmd_propose)

    explore_p = sub.add_parser("explore")
    explore_p.add_argument("path")
    explore_p.add_argument("view", choices=["summary", "assertions", "proposals"])
    explore_p.set_defaults(func=_cmd_explore)

    review_p = sub.add_parser("review")
    review_p.add_argument("path")
    review_p.add_argument("topic", choices=["proposals", "conflicts"])
    review_p.set_defaults(func=_cmd_review)

    recipe_p = sub.add_parser("recipe")
    recipe_sub = recipe_p.add_subparsers(dest="recipe_command", required=True)

    recipe_list_p = recipe_sub.add_parser("list")
    recipe_list_p.add_argument("path")
    recipe_list_p.set_defaults(func=_cmd_recipe_list)

    recipe_run_p = recipe_sub.add_parser("run")
    recipe_run_p.add_argument("path")
    recipe_run_p.add_argument("recipe_id")
    recipe_run_p.add_argument("--inputs-json", default="{}")
    recipe_run_p.add_argument("--include-dependencies", action="store_true")
    recipe_run_p.set_defaults(func=_cmd_recipe_run)

    recipe_history_p = recipe_sub.add_parser("history")
    recipe_history_p.add_argument("path")
    recipe_history_p.set_defaults(func=_cmd_recipe_history)

    recipe_compose_p = recipe_sub.add_parser("compose")
    recipe_compose_p.add_argument("path")
    recipe_compose_p.add_argument("recipe_ids", nargs="+")
    recipe_compose_p.set_defaults(func=_cmd_recipe_compose)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
