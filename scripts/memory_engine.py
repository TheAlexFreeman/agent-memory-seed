#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, cast

INDEXED_MARKDOWN_DIRS = ("identity", "knowledge", "skills", "chats")
ACCESS_DIRS = INDEXED_MARKDOWN_DIRS
DEFAULT_DB_NAME = ".memory.db"
TASK_GROUPS_PATH = Path("meta") / "task-groups.md"
TASK_GROUP_MERGE_THRESHOLD = 0.7
TASK_NAME_LIMIT = 6
TASK_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "at",
        "before",
        "by",
        "for",
        "from",
        "in",
        "into",
        "of",
        "on",
        "or",
        "the",
        "through",
        "to",
        "under",
        "with",
    }
)


@dataclass
class Inventory:
    indexed_files: list[dict[str, object]]
    access_entries: list[dict[str, object]]
    sessions: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Memory engine foundation")
    parser.add_argument(
        "--repo-root", type=Path, default=None, help="Path to the memory repo root"
    )
    parser.add_argument(
        "--db-path", type=Path, default=None, help="Path to the derived SQLite database"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    status_parser = subparsers.add_parser("status", help="Show repo and index status")
    status_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )

    rebuild_parser = subparsers.add_parser(
        "rebuild", help="Rebuild the derived SQLite database"
    )
    rebuild_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview rebuild counts without writing the database",
    )

    task_groups_parser = subparsers.add_parser(
        "task-groups", help="Preview normalized task groups from ACCESS history"
    )
    task_groups_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    task_groups_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of task groups to print",
    )

    aggregate_parser = subparsers.add_parser(
        "aggregate", help="Analyze ACCESS history and emit task-group state"
    )
    aggregate_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    aggregate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview aggregation output without writing task-group state",
    )
    aggregate_parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass the aggregation trigger threshold for the current stage",
    )

    query_parser = subparsers.add_parser(
        "query", help="Rank files using derived task-group matches"
    )
    query_parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Free-text query used to match task groups and files",
    )
    query_parser.add_argument(
        "--task-group",
        default=None,
        help="Restrict results to a specific derived task-group name",
    )
    query_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON"
    )
    query_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of ranked files to print",
    )
    query_parser.add_argument(
        "--group-limit",
        type=int,
        default=5,
        help="Maximum number of matched task groups to include in the report",
    )

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
    return (path / "README.md").exists() and (
        path / "meta" / "quick-reference.md"
    ).exists()


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
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
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
                        "is_archived": path.name != "ACCESS.jsonl",
                    }
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                raise SystemExit(
                    f"Error parsing {source_file} line {line_number}: {exc}"
                ) from exc

    chats_root = repo_root / "chats"
    sessions = (
        sum(1 for path in chats_root.rglob("chat-*") if path.is_dir())
        if chats_root.exists()
        else 0
    )
    return Inventory(
        indexed_files=indexed_files, access_entries=access_entries, sessions=sessions
    )


def strip_doubled_suffix(token: str) -> str:
    if len(token) >= 3 and token[-1] == token[-2]:
        return token[:-1]
    return token


def normalize_task_token(token: str) -> str:
    if len(token) <= 3:
        return token
    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"
    if token.endswith("ing") and len(token) > 5:
        return strip_doubled_suffix(token[:-3])
    if token.endswith("ed") and len(token) > 4:
        return strip_doubled_suffix(token[:-2])
    if (
        token.endswith("es")
        and len(token) > 4
        and not token.endswith(("ses", "xes", "zes", "ches", "shes"))
    ):
        return token[:-2]
    if (
        token.endswith("s")
        and len(token) > 3
        and not token.endswith(("ss", "us", "is"))
    ):
        return token[:-1]
    return token


def normalize_task(task: str) -> tuple[str, ...]:
    raw_tokens = re.findall(r"[a-z0-9]+", task.lower())
    filtered_tokens = [
        normalize_task_token(token)
        for token in raw_tokens
        if token not in TASK_STOPWORDS
    ]
    filtered_tokens = [token for token in filtered_tokens if token]
    if not filtered_tokens:
        filtered_tokens = [normalize_task_token(token) for token in raw_tokens if token]
    if not filtered_tokens:
        return ("untitled",)
    return tuple(sorted(set(filtered_tokens)))


def jaccard_similarity(left: tuple[str, ...], right: tuple[str, ...]) -> float:
    left_set = set(left)
    right_set = set(right)
    union = left_set | right_set
    if not union:
        return 1.0
    return len(left_set & right_set) / len(union)


def build_task_group_name(task: str, normalized_tokens: tuple[str, ...]) -> str:
    tokens = normalize_task(task)
    if tokens != ("untitled",):
        return "-".join(tokens[:TASK_NAME_LIMIT])
    if normalized_tokens != ("untitled",):
        return "-".join(normalized_tokens[:TASK_NAME_LIMIT])
    return "untitled-task"


def count_value(counter: Counter[str], value: str, amount: int = 1) -> None:
    counter[value] += amount


def parse_threshold_count(raw_value: str) -> int | None:
    match = re.search(r"(\d+)", raw_value)
    if match is None:
        return None
    return int(match.group(1))


def stage_supports_task_group_writes(stage: str) -> bool:
    return stage.lower() in {"calibration", "consolidation"}


def parse_iso_date(raw_value: object) -> date | None:
    if not isinstance(raw_value, str):
        return None
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        return None


def build_task_groups(
    access_entries: list[dict[str, object]],
) -> list[dict[str, object]]:
    exact_groups: dict[tuple[str, ...], dict[str, object]] = {}

    for entry in access_entries:
        task = str(entry["task"])
        normalized_tokens = normalize_task(task)
        entry["normalized_task"] = " ".join(normalized_tokens)
        group = exact_groups.setdefault(
            normalized_tokens,
            {
                "canonical_tokens": normalized_tokens,
                "task_counts": Counter(),
                "file_counts": Counter(),
                "dates": set(),
                "sessions": set(),
                "entries": [],
            },
        )
        task_counts = cast(Counter[str], group["task_counts"])
        file_counts = cast(Counter[str], group["file_counts"])
        dates = cast(set[str], group["dates"])
        sessions = cast(set[str], group["sessions"])
        entries = cast(list[dict[str, object]], group["entries"])

        count_value(task_counts, task)
        count_value(file_counts, str(entry["file"]))
        dates.add(str(entry["retrieval_date"]))
        session_id = str(entry.get("session_id") or "").strip()
        sessions.add(session_id or f"date:{entry['retrieval_date']}")
        entries.append(entry)

    merged_groups: list[dict[str, object]] = []
    sorted_exact_groups = sorted(
        exact_groups.values(),
        key=lambda group: (
            -len(cast(list[dict[str, object]], group["entries"])),
            cast(tuple[str, ...], group["canonical_tokens"]),
        ),
    )

    for exact_group in sorted_exact_groups:
        best_match: dict[str, object] | None = None
        best_similarity = 0.0
        exact_tokens = cast(tuple[str, ...], exact_group["canonical_tokens"])
        for merged_group in merged_groups:
            similarity = jaccard_similarity(
                exact_tokens, cast(tuple[str, ...], merged_group["canonical_tokens"])
            )
            if (
                similarity >= TASK_GROUP_MERGE_THRESHOLD
                and similarity > best_similarity
            ):
                best_match = merged_group
                best_similarity = similarity

        if best_match is None:
            merged_groups.append(
                {
                    "canonical_tokens": exact_tokens,
                    "task_counts": Counter(
                        cast(Counter[str], exact_group["task_counts"])
                    ),
                    "file_counts": Counter(
                        cast(Counter[str], exact_group["file_counts"])
                    ),
                    "dates": set(cast(set[str], exact_group["dates"])),
                    "sessions": set(cast(set[str], exact_group["sessions"])),
                    "entries": list(
                        cast(list[dict[str, object]], exact_group["entries"])
                    ),
                }
            )
            continue

        cast(Counter[str], best_match["task_counts"]).update(
            cast(Counter[str], exact_group["task_counts"])
        )
        cast(Counter[str], best_match["file_counts"]).update(
            cast(Counter[str], exact_group["file_counts"])
        )
        cast(set[str], best_match["dates"]).update(cast(set[str], exact_group["dates"]))
        cast(set[str], best_match["sessions"]).update(
            cast(set[str], exact_group["sessions"])
        )
        cast(list[dict[str, object]], best_match["entries"]).extend(
            cast(list[dict[str, object]], exact_group["entries"])
        )

    serialized_groups: list[dict[str, object]] = []
    used_names: set[str] = set()
    sorted_merged_groups = sorted(
        merged_groups,
        key=lambda group: (
            -len(cast(list[dict[str, object]], group["entries"])),
            cast(tuple[str, ...], group["canonical_tokens"]),
        ),
    )
    for group in sorted_merged_groups:
        task_counts = cast(Counter[str], group["task_counts"])
        file_counts = cast(Counter[str], group["file_counts"])
        sorted_dates = sorted(cast(set[str], group["dates"]))
        sessions = cast(set[str], group["sessions"])
        representative_tasks = [task for task, _count in task_counts.most_common(3)]
        group_name = build_task_group_name(
            representative_tasks[0] if representative_tasks else "",
            cast(tuple[str, ...], group["canonical_tokens"]),
        )
        original_name = group_name
        suffix = 2
        while group_name in used_names:
            group_name = f"{original_name}-{suffix}"
            suffix += 1
        used_names.add(group_name)

        serialized_group: dict[str, object] = {
            "group_name": group_name,
            "normalized_tokens": list(cast(tuple[str, ...], group["canonical_tokens"])),
            "representative_tasks": representative_tasks,
            "first_seen_date": sorted_dates[0] if sorted_dates else None,
            "last_seen_date": sorted_dates[-1] if sorted_dates else None,
            "entry_count": len(cast(list[dict[str, object]], group["entries"])),
            "session_count": len(sessions),
            "distinct_dates_count": len(sorted_dates),
            "common_files": [
                {"file": file_name, "count": count}
                for file_name, count in file_counts.most_common(5)
            ],
        }
        for entry in cast(list[dict[str, object]], group["entries"]):
            entry["task_group_name"] = group_name
        serialized_groups.append(serialized_group)

    return serialized_groups


def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        DROP TABLE IF EXISTS access_entries;
        DROP TABLE IF EXISTS files;
        DROP TABLE IF EXISTS task_groups;
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
            normalized_task TEXT NOT NULL,
            task_group_name TEXT NOT NULL,
            helpfulness REAL NOT NULL,
            note TEXT NOT NULL,
            source_file TEXT NOT NULL,
            source_line INTEGER NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files(id)
        );

        CREATE TABLE task_groups (
            id INTEGER PRIMARY KEY,
            group_name TEXT UNIQUE NOT NULL,
            normalized_tokens_json TEXT NOT NULL,
            representative_tasks_json TEXT NOT NULL,
            first_seen_date TEXT,
            last_seen_date TEXT,
            entry_count INTEGER NOT NULL,
            session_count INTEGER NOT NULL,
            distinct_dates_count INTEGER NOT NULL,
            common_files_json TEXT NOT NULL
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


def write_database(
    db_path: Path, inventory: Inventory, quick_reference: dict[str, object]
) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    task_groups = build_task_groups(inventory.access_entries)
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
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
                file_id, file, retrieval_date, session_id, task, normalized_task, task_group_name, helpfulness, note, source_file, source_line
            ) VALUES (
                :file_id, :file, :retrieval_date, :session_id, :task, :normalized_task, :task_group_name, :helpfulness, :note, :source_file, :source_line
            )
            """,
            inventory.access_entries,
        )
        connection.executemany(
            """
            INSERT INTO task_groups (
                group_name, normalized_tokens_json, representative_tasks_json, first_seen_date, last_seen_date,
                entry_count, session_count, distinct_dates_count, common_files_json
            ) VALUES (
                :group_name, :normalized_tokens_json, :representative_tasks_json, :first_seen_date, :last_seen_date,
                :entry_count, :session_count, :distinct_dates_count, :common_files_json
            )
            """,
            [
                {
                    "group_name": group["group_name"],
                    "normalized_tokens_json": json.dumps(
                        group["normalized_tokens"], sort_keys=True
                    ),
                    "representative_tasks_json": json.dumps(
                        group["representative_tasks"], sort_keys=True
                    ),
                    "first_seen_date": group["first_seen_date"],
                    "last_seen_date": group["last_seen_date"],
                    "entry_count": group["entry_count"],
                    "session_count": group["session_count"],
                    "distinct_dates_count": group["distinct_dates_count"],
                    "common_files_json": json.dumps(
                        group["common_files"], sort_keys=True
                    ),
                }
                for group in task_groups
            ],
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


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def format_status(
    repo_root: Path,
    db_path: Path,
    inventory: Inventory,
    quick_reference: dict[str, object],
) -> dict[str, object]:
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
            database_snapshot = {
                "indexed_files": connection.execute(
                    "SELECT COUNT(*) FROM files"
                ).fetchone()[0],
                "access_entries": connection.execute(
                    "SELECT COUNT(*) FROM access_entries"
                ).fetchone()[0],
            }
            if table_exists(connection, "task_groups"):
                database_snapshot["task_groups"] = connection.execute(
                    "SELECT COUNT(*) FROM task_groups"
                ).fetchone()[0]
            status["database"] = database_snapshot
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
        if "task_groups" in database:
            print(f"  Task groups: {database['task_groups']}")
    print("Active thresholds:")
    for parameter, value in thresholds.items():
        print(f"  - {parameter}: {value}")


def format_task_group_report(
    repo_root: Path, inventory: Inventory, limit: int
) -> dict[str, object]:
    task_groups = build_task_groups(inventory.access_entries)
    sorted_task_groups = sorted(
        task_groups,
        key=lambda group: (
            -cast(int, group["entry_count"]),
            -cast(int, group["session_count"]),
            cast(str, group["group_name"]),
        ),
    )
    return {
        "repo_root": str(repo_root),
        "entries_analyzed": len(inventory.access_entries),
        "task_groups_count": len(sorted_task_groups),
        "task_groups": sorted_task_groups[: max(limit, 0)],
    }


def render_task_groups_markdown(
    stage: str,
    aggregation_trigger: int | None,
    task_groups: list[dict[str, object]],
) -> str:
    lines = [
        "# Task Groups",
        "",
        "This file is machine-generated from ACCESS history during aggregation.",
        "",
        f"- Stage: {stage}",
        (
            f"- Aggregation trigger: {aggregation_trigger} entries"
            if aggregation_trigger is not None
            else "- Aggregation trigger: unavailable"
        ),
        f"- Recorded task groups: {len(task_groups)}",
        "",
        "Update source: `python scripts/memory_engine.py aggregate`",
        "",
    ]

    if not task_groups:
        lines.extend(
            [
                "No task groups met the current aggregation criteria.",
                "",
            ]
        )
        return "\n".join(lines)

    for group in task_groups:
        representative_tasks = cast(list[str], group["representative_tasks"])
        normalized_tokens = cast(list[str], group["normalized_tokens"])
        common_files = cast(list[dict[str, object]], group["common_files"])
        lines.extend(
            [
                f"## {group['group_name']}",
                "",
                f"- First seen: {group['first_seen_date'] or 'unknown'}",
                f"- Last seen: {group['last_seen_date'] or 'unknown'}",
                f"- Sessions: {group['session_count']}",
                f"- Entries: {group['entry_count']}",
                f"- Distinct dates: {group['distinct_dates_count']}",
                f"- Normalized tokens: {', '.join(normalized_tokens) if normalized_tokens else 'none'}",
                (
                    f"- Representative tasks: {'; '.join(representative_tasks)}"
                    if representative_tasks
                    else "- Representative tasks: none"
                ),
                "- Commonly co-retrieved files:",
            ]
        )
        if common_files:
            lines.extend(
                [f"  - {item['file']} ({item['count']})" for item in common_files]
            )
        else:
            lines.append("  - none")
        lines.append("")

    return "\n".join(lines)


def format_aggregation_report(
    repo_root: Path,
    quick_reference: dict[str, object],
    inventory: Inventory,
    force: bool,
) -> tuple[dict[str, object], str | None]:
    thresholds = cast(dict[str, str], quick_reference["thresholds"])
    aggregation_trigger = parse_threshold_count(
        str(thresholds.get("Aggregation trigger", ""))
    )
    pending_entries = [
        entry for entry in inventory.access_entries if not bool(entry.get("is_archived"))
    ]
    task_groups = build_task_groups(inventory.access_entries)
    supports_writes = stage_supports_task_group_writes(str(quick_reference["stage"]))
    meets_trigger = (
        aggregation_trigger is not None and len(pending_entries) >= aggregation_trigger
    )
    should_write = supports_writes and (meets_trigger or force)
    task_groups_markdown = None
    if should_write:
        task_groups_markdown = render_task_groups_markdown(
            str(quick_reference["stage"]), aggregation_trigger, task_groups
        )

    report = {
        "repo_root": str(repo_root),
        "stage": quick_reference["stage"],
        "aggregation_trigger": aggregation_trigger,
        "pending_entries": len(pending_entries),
        "historical_entries": len(inventory.access_entries),
        "task_groups_count": len(task_groups),
        "task_groups_path": str(repo_root / TASK_GROUPS_PATH),
        "supports_task_group_writes": supports_writes,
        "meets_trigger": meets_trigger,
        "would_write_task_groups": should_write,
        "task_groups": task_groups,
    }
    return report, task_groups_markdown


def write_task_groups_file(repo_root: Path, markdown: str) -> Path:
    output_path = repo_root / TASK_GROUPS_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def print_aggregation_report(report: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"Repo root: {report['repo_root']}")
    print(f"Current stage: {report['stage']}")
    print(f"Pending ACCESS entries: {report['pending_entries']}")
    print(f"Historical ACCESS entries: {report['historical_entries']}")
    print(f"Aggregation trigger: {report['aggregation_trigger']}")
    print(f"Task groups: {report['task_groups_count']}")
    print(
        "Task-group writes supported: "
        f"{'yes' if report['supports_task_group_writes'] else 'no'}"
    )
    print(f"Meets trigger: {'yes' if report['meets_trigger'] else 'no'}")
    print(
        "Would write task groups: "
        f"{'yes' if report['would_write_task_groups'] else 'no'}"
    )
    print(f"Task groups path: {report['task_groups_path']}")


def format_query_report(
    repo_root: Path,
    inventory: Inventory,
    raw_query: str,
    task_group_name: str | None,
    limit: int,
    group_limit: int,
) -> dict[str, object]:
    task_groups = build_task_groups(inventory.access_entries)
    task_group_by_name = {
        cast(str, group["group_name"]): group for group in task_groups
    }

    normalized_query_tokens = normalize_task(raw_query or task_group_name or "")
    if not raw_query and task_group_name is None:
        raise SystemExit("query requires a free-text query or --task-group")

    matched_groups: list[dict[str, object]] = []
    if task_group_name is not None:
        selected_group = task_group_by_name.get(task_group_name)
        if selected_group is None:
            raise SystemExit(f"Unknown task group: {task_group_name}")
        matched_groups.append({"group": selected_group, "score": 1.0})
    else:
        for group in task_groups:
            score = jaccard_similarity(
                normalized_query_tokens,
                tuple(cast(list[str], group["normalized_tokens"])),
            )
            if score > 0:
                matched_groups.append({"group": group, "score": score})
        matched_groups.sort(
            key=lambda item: (
                -cast(float, item["score"]),
                -cast(int, cast(dict[str, object], item["group"])["entry_count"]),
                cast(str, cast(dict[str, object], item["group"])["group_name"]),
            )
        )

    if not matched_groups and task_group_name is None:
        matched_groups = [
            {"group": group, "score": 0.0}
            for group in sorted(
                task_groups,
                key=lambda group: (
                    -cast(int, group["entry_count"]),
                    cast(str, group["group_name"]),
                ),
            )[: max(group_limit, 0)]
        ]

    selected_group_names = {
        cast(str, cast(dict[str, object], item["group"])["group_name"])
        for item in matched_groups[: max(group_limit, 0)]
    }
    selected_group_scores = {
        cast(str, cast(dict[str, object], item["group"])["group_name"]): cast(
            float, item["score"]
        )
        for item in matched_groups[: max(group_limit, 0)]
    }

    file_metadata = {
        cast(str, file_info["relative_path"]): file_info
        for file_info in inventory.indexed_files
    }
    file_scores: dict[str, dict[str, object]] = {}
    recent_dates: list[date] = []
    for entry in inventory.access_entries:
        group_name = cast(str, entry.get("task_group_name") or "")
        if group_name not in selected_group_names:
            continue
        file_name = cast(str, entry["file"])
        score_entry = file_scores.setdefault(
            file_name,
            {
                "file": file_name,
                "hit_count": 0,
                "helpfulness_total": 0.0,
                "last_seen_date": None,
                "task_groups": set(),
                "best_group_score": 0.0,
            },
        )
        score_entry["hit_count"] = cast(int, score_entry["hit_count"]) + 1
        score_entry["helpfulness_total"] = cast(float, score_entry["helpfulness_total"]) + cast(
            float, entry["helpfulness"]
        )
        cast(set[str], score_entry["task_groups"]).add(group_name)
        score_entry["best_group_score"] = max(
            cast(float, score_entry["best_group_score"]),
            selected_group_scores[group_name],
        )

        entry_date = parse_iso_date(entry["retrieval_date"])
        if entry_date is not None:
            recent_dates.append(entry_date)
            previous_date = parse_iso_date(score_entry["last_seen_date"])
            if previous_date is None or entry_date > previous_date:
                score_entry["last_seen_date"] = entry["retrieval_date"]

    latest_date = max(recent_dates) if recent_dates else None
    ranked_files: list[dict[str, object]] = []
    for file_name, score_entry in file_scores.items():
        hit_count = cast(int, score_entry["hit_count"])
        avg_helpfulness = cast(float, score_entry["helpfulness_total"]) / hit_count
        frequency_score = min(hit_count / 3, 1.0)
        last_seen = parse_iso_date(score_entry["last_seen_date"])
        recency_score = 0.0
        if latest_date is not None and last_seen is not None:
            age_days = max((latest_date - last_seen).days, 0)
            recency_score = max(0.0, 1.0 - min(age_days, 365) / 365)
        total_score = (
            cast(float, score_entry["best_group_score"]) * 0.5
            + frequency_score * 0.25
            + avg_helpfulness * 0.2
            + recency_score * 0.05
        )
        metadata = file_metadata.get(file_name, {})
        ranked_files.append(
            {
                "file": file_name,
                "folder": metadata.get("folder"),
                "file_type": metadata.get("file_type"),
                "score": round(total_score, 4),
                "hit_count": hit_count,
                "avg_helpfulness": round(avg_helpfulness, 4),
                "last_seen_date": score_entry["last_seen_date"],
                "task_groups": sorted(cast(set[str], score_entry["task_groups"])),
            }
        )

    ranked_files.sort(
        key=lambda item: (
            -cast(float, item["score"]),
            -cast(int, item["hit_count"]),
            cast(str, item["file"]),
        )
    )

    return {
        "repo_root": str(repo_root),
        "query": raw_query,
        "normalized_query_tokens": list(normalized_query_tokens),
        "task_group_filter": task_group_name,
        "matched_task_groups": [
            {
                "group_name": cast(dict[str, object], item["group"])["group_name"],
                "score": round(cast(float, item["score"]), 4),
                "entry_count": cast(dict[str, object], item["group"])["entry_count"],
            }
            for item in matched_groups[: max(group_limit, 0)]
        ],
        "results": ranked_files[: max(limit, 0)],
    }


def print_query_report(report: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"Repo root: {report['repo_root']}")
    print(f"Query: {report['query'] or '(task-group only)'}")
    print(
        "Normalized query tokens: "
        f"{', '.join(cast(list[str], report['normalized_query_tokens'])) or 'none'}"
    )
    if report["task_group_filter"] is not None:
        print(f"Task-group filter: {report['task_group_filter']}")
    print("Matched task groups:")
    matched_groups = cast(list[dict[str, object]], report["matched_task_groups"])
    if matched_groups:
        for group in matched_groups:
            print(
                f"  - {group['group_name']} (score={group['score']}, entries={group['entry_count']})"
            )
    else:
        print("  - none")

    print("Ranked files:")
    results = cast(list[dict[str, object]], report["results"])
    if results:
        for item in results:
            print(
                f"  - {item['file']} (score={item['score']}, hits={item['hit_count']}, avg_helpfulness={item['avg_helpfulness']}, groups={', '.join(cast(list[str], item['task_groups']))})"
            )
    else:
        print("  - none")


def print_task_group_report(report: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    print(f"Repo root: {report['repo_root']}")
    print(f"ACCESS entries analyzed: {report['entries_analyzed']}")
    print(f"Task groups: {report['task_groups_count']}")
    for group in cast(list[dict[str, object]], report["task_groups"]):
        representative_tasks = cast(list[str], group["representative_tasks"])
        normalized_tokens = cast(list[str], group["normalized_tokens"])
        common_files = cast(list[dict[str, object]], group["common_files"])
        print()
        print(f"[{group['group_name']}]")
        print(
            "  Entries: "
            f"{group['entry_count']} | Sessions: {group['session_count']} | Dates: {group['distinct_dates_count']}"
        )
        print(f"  Tokens: {', '.join(normalized_tokens)}")
        if representative_tasks:
            print(f"  Representative tasks: {'; '.join(representative_tasks)}")
        if common_files:
            formatted_files = ", ".join(
                f"{item['file']} ({item['count']})" for item in common_files
            )
            print(f"  Common files: {formatted_files}")


def run_status(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    db_path = resolve_db_path(repo_root, args.db_path)
    quick_reference = parse_quick_reference(repo_root / "meta" / "quick-reference.md")
    inventory = load_inventory(repo_root)
    print_status(
        format_status(repo_root, db_path, inventory, quick_reference), args.json
    )
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


def run_task_groups(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    inventory = load_inventory(repo_root)
    print_task_group_report(
        format_task_group_report(repo_root, inventory, args.limit), args.json
    )
    return 0


def run_aggregate(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    quick_reference = parse_quick_reference(repo_root / "meta" / "quick-reference.md")
    inventory = load_inventory(repo_root)
    report, markdown = format_aggregation_report(
        repo_root, quick_reference, inventory, args.force
    )
    wrote_task_groups = False
    if markdown is not None and not args.dry_run:
        write_task_groups_file(repo_root, markdown)
        wrote_task_groups = True
    report["wrote_task_groups"] = wrote_task_groups
    print_aggregation_report(report, args.json)
    return 0


def run_query(args: argparse.Namespace) -> int:
    repo_root = detect_repo_root(args.repo_root)
    inventory = load_inventory(repo_root)
    report = format_query_report(
        repo_root,
        inventory,
        args.query,
        args.task_group,
        args.limit,
        args.group_limit,
    )
    print_query_report(report, args.json)
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "status":
        return run_status(args)
    if args.command == "rebuild":
        return run_rebuild(args)
    if args.command == "task-groups":
        return run_task_groups(args)
    if args.command == "aggregate":
        return run_aggregate(args)
    if args.command == "query":
        return run_query(args)
    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
