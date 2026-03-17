#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, cast


INDEXED_MARKDOWN_DIRS = ("identity", "knowledge", "skills", "chats")
ACCESS_DIRS = INDEXED_MARKDOWN_DIRS
DEFAULT_DB_NAME = ".memory.db"


@dataclass
class Inventory:
    indexed_files: list[dict[str, object]]
    access_entries: list[dict[str, object]]
    sessions: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 1 memory engine foundation")
    parser.add_argument("--repo-root", type=Path, default=None, help="Path to the memory repo root")
    parser.add_argument("--db-path", type=Path, default=None, help="Path to the derived SQLite database")

    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show repo and index status")
    status_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")

    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild the derived SQLite database")
    rebuild_parser.add_argument("--dry-run", action="store_true", help="Preview rebuild counts without writing the database")

    return parser.parse_args()


def detect_repo_root(explicit_root: Path | None) -> Path:
    if explicit_root is not None:
        root = explicit_root.resolve()
        ensure_repo_root(root)
        return root

    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if is_repo_root(candidate):
            return candidate
    raise SystemExit("Could not detect repository root. Pass --repo-root explicitly.")


def is_repo_root(path: Path) -> bool:
    return (path / "README.md").exists() and (path / "meta" / "quick-reference.md").exists()


def ensure_repo_root(path: Path) -> None:
    if not is_repo_root(path):
        raise SystemExit(
            f"{path} does not look like a memory repo root "
            "(expected README.md and meta/quick-reference.md)"
        )


def resolve_db_path(repo_root: Path, explicit_db_path: Path | None) -> Path:
    if explicit_db_path is not None:
        return explicit_db_path.resolve()
    return repo_root / DEFAULT_DB_NAME


def parse_quick_reference(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    stage = "unknown"
    last_review = "unknown"
    thresholds: dict[str, str] = {}
    in_active_thresholds = False

    for line in text.splitlines():
        if line.startswith("## Current active stage:"):
            stage = line.split(":", 1)[1].strip()
            continue
        if line.startswith("**Date:**"):
            raw_value = line.split(":", 1)[1].strip()
            last_review = re.sub(r"[*_`]", "", raw_value).strip()
            continue
        if line.startswith("## Active thresholds"):
            in_active_thresholds = True
            continue
        if line.startswith("## ") and not line.startswith("## Active thresholds"):
            in_active_thresholds = False
        if not in_active_thresholds:
            continue
        if not line.startswith("|"):
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != 3:
            continue
        if parts[0] in {"Parameter", "-----------"}:
            continue
        thresholds[parts[0]] = parts[1]

    return {
        "stage": stage,
        "last_periodic_review": last_review,
        "thresholds": thresholds,
    }


def determine_file_type(path: Path) -> str:
    if path.name == "SUMMARY.md":
        return "summary"
    if path.name == "reflection.md":
        return "reflection"
    if path.name == "transcript.md":
        return "transcript"
    return "content"


def parse_frontmatter(path: Path) -> dict[str, str]:
    if determine_file_type(path) != "content":
        return {}

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line.strip() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def iter_markdown_files(repo_root: Path) -> Iterable[Path]:
    for folder in INDEXED_MARKDOWN_DIRS:
        base = repo_root / folder
        if not base.exists():
            continue
        yield from sorted(base.rglob("*.md"))


def iter_access_files(repo_root: Path) -> Iterable[Path]:
    for folder in ACCESS_DIRS:
        base = repo_root / folder
        if not base.exists():
            continue
        yield from sorted(base.rglob("ACCESS*.jsonl"))


def load_inventory(repo_root: Path) -> Inventory:
    indexed_files: list[dict[str, object]] = []
    file_lookup: dict[str, int] = {}

    for file_id, path in enumerate(iter_markdown_files(repo_root), start=1):
        relative_path = path.relative_to(repo_root).as_posix()
        folder = relative_path.split("/", 1)[0]
        frontmatter = parse_frontmatter(path)
        indexed_files.append(
            {
                "id": file_id,
                "relative_path": relative_path,
                "folder": folder,
                "file_type": determine_file_type(path),
                "source": frontmatter.get("source"),
                "trust": frontmatter.get("trust"),
                "created": frontmatter.get("created"),
                "last_verified": frontmatter.get("last_verified"),
                "file_size_bytes": path.stat().st_size,
            }
        )
        file_lookup[relative_path] = file_id

    access_entries: list[dict[str, object]] = []
    for path in iter_access_files(repo_root):
        source_file = path.relative_to(repo_root).as_posix()
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                access_entries.append(
                    {
                        "file_id": file_lookup.get(payload["file"]),
                        "file": payload["file"],
                        "retrieval_date": payload["date"],
                        "session_id": payload.get("session_id"),
                        "task": payload["task"],
                        "helpfulness": float(payload["helpfulness"]),
                        "note": payload["note"],
                        "source_file": source_file,
                        "source_line": line_number,
                    }
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise SystemExit(
                    f"Error parsing {source_file} line {line_number}: {exc}"
                ) from exc

    chats_root = repo_root / "chats"
    sessions = sum(1 for path in chats_root.rglob("chat-*") if path.is_dir()) if chats_root.exists() else 0
    return Inventory(indexed_files=indexed_files, access_entries=access_entries, sessions=sessions)


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP TABLE IF EXISTS access_entries;
        DROP TABLE IF EXISTS files;
        DROP TABLE IF EXISTS aggregation_checkpoints;
        DROP TABLE IF EXISTS clusters;
        DROP TABLE IF EXISTS anomalies;
        DROP TABLE IF EXISTS system_state;

        CREATE TABLE files (
            id INTEGER PRIMARY KEY,
            relative_path TEXT UNIQUE NOT NULL,
            folder TEXT NOT NULL,
            file_type TEXT NOT NULL,
            source TEXT,
            trust TEXT,
            created TEXT,
            last_verified TEXT,
            file_size_bytes INTEGER NOT NULL
        );

        CREATE TABLE access_entries (
            id INTEGER PRIMARY KEY,
            file_id INTEGER,
            file TEXT NOT NULL,
            retrieval_date TEXT NOT NULL,
            session_id TEXT,
            task TEXT NOT NULL,
            helpfulness REAL NOT NULL,
            note TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_line INTEGER NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files(id)
        );

        CREATE TABLE aggregation_checkpoints (
            id INTEGER PRIMARY KEY,
            checkpoint_date TEXT NOT NULL,
            access_entries_count INTEGER NOT NULL,
            metadata_json TEXT
        );

        CREATE TABLE clusters (
            id INTEGER PRIMARY KEY,
            cluster_name TEXT UNIQUE NOT NULL,
            cluster_source TEXT NOT NULL,
            members_json TEXT NOT NULL,
            co_occurrence_count INTEGER NOT NULL,
            discovered_date TEXT NOT NULL,
            last_seen TEXT
        );

        CREATE TABLE anomalies (
            id INTEGER PRIMARY KEY,
            detected_date TEXT NOT NULL,
            anomaly_type TEXT NOT NULL,
            details_json TEXT NOT NULL,
            file_id INTEGER,
            session_id TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (file_id) REFERENCES files(id)
        );

        CREATE TABLE system_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            maturity_stage TEXT NOT NULL,
            last_periodic_review TEXT,
            total_sessions INTEGER NOT NULL,
            indexed_files_count INTEGER NOT NULL,
            access_entries_count INTEGER NOT NULL,
            thresholds_json TEXT NOT NULL
        );
        """
    )


def write_database(db_path: Path, inventory: Inventory, quick_reference: dict[str, object]) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        initialize_schema(connection)
        connection.executemany(
            """
            INSERT INTO files (
                id, relative_path, folder, file_type, source, trust, created, last_verified, file_size_bytes
            ) VALUES (
                :id, :relative_path, :folder, :file_type, :source, :trust, :created, :last_verified, :file_size_bytes
            )
            """,
            inventory.indexed_files,
        )
        connection.executemany(
            """
            INSERT INTO access_entries (
                file_id, file, retrieval_date, session_id, task, helpfulness, note, source_file, source_line
            ) VALUES (
                :file_id, :file, :retrieval_date, :session_id, :task, :helpfulness, :note, :source_file, :source_line
            )
            """,
            inventory.access_entries,
        )
        connection.execute(
            """
            INSERT INTO system_state (
                id, maturity_stage, last_periodic_review, total_sessions, indexed_files_count, access_entries_count, thresholds_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                quick_reference["stage"],
                quick_reference["last_periodic_review"],
                inventory.sessions,
                len(inventory.indexed_files),
                len(inventory.access_entries),
                json.dumps(quick_reference["thresholds"], sort_keys=True),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def format_status(repo_root: Path, db_path: Path, inventory: Inventory, quick_reference: dict[str, object]) -> dict[str, object]:
    status: dict[str, object] = {
        "repo_root": str(repo_root),
        "db_path": str(db_path),
        "db_exists": db_path.exists(),
        "stage": quick_reference["stage"],
        "last_periodic_review": quick_reference["last_periodic_review"],
        "thresholds": quick_reference["thresholds"],
        "inventory": {
            "indexed_files": len(inventory.indexed_files),
            "access_entries": len(inventory.access_entries),
            "sessions": inventory.sessions,
        },
    }

    if db_path.exists():
        connection = sqlite3.connect(db_path)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            status["database"] = {
                "indexed_files": connection.execute("SELECT COUNT(*) FROM files").fetchone()[0],
                "access_entries": connection.execute("SELECT COUNT(*) FROM access_entries").fetchone()[0],
            }
        finally:
            connection.close()

    return status


def print_status(status: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(status, indent=2, sort_keys=True))
        return

    inventory = cast(dict[str, Any], status["inventory"])
    database = cast(dict[str, Any] | None, status.get("database"))
    thresholds = cast(dict[str, str], status["thresholds"])

    print(f"Repo root: {status['repo_root']}")
    print(f"Derived DB: {status['db_path']}")
    print(f"DB exists: {'yes' if status['db_exists'] else 'no'}")
    print(f"Current stage: {status['stage']}")
    print(f"Last periodic review: {status['last_periodic_review']}")
    print("Inventory:")
    print(f"  Indexed markdown files: {inventory['indexed_files']}")
    print(f"  ACCESS entries: {inventory['access_entries']}")
    print(f"  Sessions: {inventory['sessions']}")
    if database is not None:
        print("Database snapshot:")
        print(f"  Indexed files: {database['indexed_files']}")
        print(f"  ACCESS entries: {database['access_entries']}")
    print("Active thresholds:")
    for parameter, value in thresholds.items():
        print(f"  - {parameter}: {value}")


def run_status(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    db_path = resolve_db_path(repo_root, args.db_path)
    quick_reference = parse_quick_reference(repo_root / "meta" / "quick-reference.md")
    inventory = load_inventory(repo_root)
    print_status(format_status(repo_root, db_path, inventory, quick_reference), args.json)
    return 0


def run_rebuild(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    db_path = resolve_db_path(repo_root, args.db_path)
    quick_reference = parse_quick_reference(repo_root / "meta" / "quick-reference.md")
    inventory = load_inventory(repo_root)

    if args.dry_run:
        print(f"Dry run: would rebuild {db_path}")
        print(f"  Indexed markdown files: {len(inventory.indexed_files)}")
        print(f"  ACCESS entries: {len(inventory.access_entries)}")
        print(f"  Current stage snapshot: {quick_reference['stage']}")
        return 0

    write_database(db_path, inventory, quick_reference)
    print(f"Rebuilt derived database at {db_path}")
    print(f"  Indexed markdown files: {len(inventory.indexed_files)}")
    print(f"  ACCESS entries: {len(inventory.access_entries)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "status":
        return run_status(args)
    if args.command == "rebuild":
        return run_rebuild(args)
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())