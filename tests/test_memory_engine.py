from __future__ import annotations

import importlib.util
import sqlite3
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE_PATH = REPO_ROOT / "scripts" / "memory_engine.py"

SPEC = importlib.util.spec_from_file_location("memory_engine", ENGINE_PATH)
assert SPEC is not None
memory_engine = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = memory_engine
SPEC.loader.exec_module(memory_engine)


VALID_QUICK_REFERENCE = textwrap.dedent(
    """\
    # Quick Reference

    ## Current active stage: Exploration

    ## Last periodic review

    **Date:** Not yet run

    ## Active thresholds

    | Parameter | Active value | Stage |
    |-----------|-------------|-------|
    | Low-trust retirement threshold | 120 days | Exploration |
    | Medium-trust flagging threshold | 180 days | Exploration |
    | Staleness trigger (no access) | 120 days | Exploration |
    | Aggregation trigger | 15 entries | Exploration |
    | Identity churn alarm | 5 traits/session | Exploration |
    | Knowledge flooding alarm | 5 files/day | Exploration |
    | Task similarity method | Session co-occurrence | Exploration |
    | Cluster co-retrieval threshold | 3 sessions | Exploration |
    """
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_minimal_repo(root: Path) -> None:
    write(root / "README.md", "# README\n")
    write(root / "QUICKSTART.md", "# Quickstart\n")
    write(root / "meta" / "quick-reference.md", VALID_QUICK_REFERENCE)
    write(root / "identity" / "SUMMARY.md", "# Identity summary\n")
    write(root / "identity" / "ACCESS.jsonl", "")
    write(root / "knowledge" / "SUMMARY.md", "# Knowledge summary\n")
    write(
        root / "knowledge" / "ACCESS.jsonl",
        '{"file":"identity/profile.md","date":"2026-03-16","task":"status test","helpfulness":0.8,"note":"used","session_id":"chats/2026/03/16/chat-001"}\n',
    )
    write(root / "skills" / "SUMMARY.md", "# Skills summary\n")
    write(root / "skills" / "ACCESS.jsonl", "")
    write(root / "chats" / "SUMMARY.md", "# Chats summary\n")
    write(root / "chats" / "ACCESS.jsonl", "")
    write(
        root / "identity" / "profile.md",
        textwrap.dedent(
            """\
            ---
            source: user-stated
            origin_session: manual
            created: 2026-03-16
            last_verified: 2026-03-16
            trust: high
            ---

            # Profile
            """
        ),
    )
    write(
        root / "chats" / "2026" / "03" / "16" / "chat-001" / "SUMMARY.md",
        "# Chat summary\n",
    )


def calibration_quick_reference(aggregation_trigger: int = 2) -> str:
    return textwrap.dedent(
        f"""\
        # Quick Reference

        ## Current active stage: Calibration

        ## Last periodic review

        **Date:** 2026-03-16

        ## Active thresholds

        | Parameter | Active value | Stage |
        |-----------|-------------|-------|
        | Low-trust retirement threshold | 90 days | Calibration |
        | Medium-trust flagging threshold | 150 days | Calibration |
        | Staleness trigger (no access) | 90 days | Calibration |
        | Aggregation trigger | {aggregation_trigger} entries | Calibration |
        | Identity churn alarm | 4 traits/session | Calibration |
        | Knowledge flooding alarm | 4 files/day | Calibration |
        | Task similarity method | Task-string normalization | Calibration |
        | Cluster co-retrieval threshold | 3 sessions | Calibration |
        """
    )


class MemoryEngineTests(unittest.TestCase):
    def test_status_reports_stage_and_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            inventory = memory_engine.load_inventory(root)
            quick_reference = memory_engine.parse_quick_reference(
                root / "meta" / "quick-reference.md"
            )
            status = memory_engine.format_status(
                root, root / ".memory.db", inventory, quick_reference
            )

            self.assertEqual(status["stage"], "Exploration")
            self.assertEqual(status["inventory"]["access_entries"], 1)
            self.assertEqual(status["inventory"]["sessions"], 1)
            self.assertFalse(status["db_exists"])

    def test_rebuild_dry_run_does_not_create_db(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            db_path = root / ".memory.db"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    "--repo-root",
                    str(root),
                    "rebuild",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertIn("Dry run: would rebuild", completed.stdout)
            self.assertFalse(db_path.exists())

    def test_rebuild_creates_and_populates_database(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            db_path = root / ".memory.db"

            completed = subprocess.run(
                [sys.executable, str(ENGINE_PATH), "--repo-root", str(root), "rebuild"],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertTrue(db_path.exists())
            self.assertIn("Rebuilt derived database", completed.stdout)

            connection = sqlite3.connect(db_path)
            try:
                indexed_files = connection.execute(
                    "SELECT COUNT(*) FROM files"
                ).fetchone()[0]
                access_entries = connection.execute(
                    "SELECT COUNT(*) FROM access_entries"
                ).fetchone()[0]
                task_groups = connection.execute(
                    "SELECT COUNT(*) FROM task_groups"
                ).fetchone()[0]
                stage = connection.execute(
                    "SELECT maturity_stage FROM system_state WHERE id = 1"
                ).fetchone()[0]
                task_group_name = connection.execute(
                    "SELECT task_group_name FROM access_entries LIMIT 1"
                ).fetchone()[0]
            finally:
                connection.close()

            self.assertGreaterEqual(indexed_files, 6)
            self.assertEqual(access_entries, 1)
            self.assertEqual(task_groups, 1)
            self.assertEqual(stage, "Exploration")
            self.assertEqual(task_group_name, "status-test")

    def test_task_group_report_merges_similar_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.archive.jsonl",
                "\n".join(
                    [
                        '{"file":"identity/profile.md","date":"2026-03-16","task":"Debugging the React performance bug","helpfulness":0.9,"note":"used","session_id":"chats/2026/03/16/chat-001"}',
                        '{"file":"knowledge/SUMMARY.md","date":"2026-03-17","task":"Debug React performance bugs","helpfulness":0.7,"note":"used","session_id":"chats/2026/03/17/chat-001"}',
                        '{"file":"skills/SUMMARY.md","date":"2026-03-18","task":"Plan release checklist","helpfulness":0.6,"note":"used","session_id":"chats/2026/03/18/chat-001"}',
                    ]
                )
                + "\n",
            )

            inventory = memory_engine.load_inventory(root)
            report = memory_engine.format_task_group_report(root, inventory, limit=10)

            self.assertEqual(report["entries_analyzed"], 4)
            self.assertEqual(report["task_groups_count"], 3)

            first_group = report["task_groups"][0]
            self.assertEqual(first_group["group_name"], "bug-debug-performance-react")
            self.assertEqual(first_group["entry_count"], 2)
            self.assertEqual(
                first_group["normalized_tokens"],
                ["bug", "debug", "performance", "react"],
            )

    def test_status_includes_task_groups_after_rebuild(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            db_path = root / ".memory.db"

            memory_engine.write_database(
                db_path,
                memory_engine.load_inventory(root),
                memory_engine.parse_quick_reference(
                    root / "meta" / "quick-reference.md"
                ),
            )

            status = memory_engine.format_status(
                root,
                db_path,
                memory_engine.load_inventory(root),
                memory_engine.parse_quick_reference(
                    root / "meta" / "quick-reference.md"
                ),
            )

            self.assertEqual(status["database"]["task_groups"], 1)

    def test_aggregate_writes_task_groups_in_calibration(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "meta" / "quick-reference.md",
                calibration_quick_reference(aggregation_trigger=2),
            )
            write(
                root / "skills" / "ACCESS.jsonl",
                "\n".join(
                    [
                        '{"file":"identity/profile.md","date":"2026-03-16","task":"Debug React performance bug","helpfulness":0.8,"note":"used","session_id":"chats/2026/03/16/chat-001"}',
                        '{"file":"knowledge/SUMMARY.md","date":"2026-03-17","task":"Debugging React performance bugs","helpfulness":0.7,"note":"used","session_id":"chats/2026/03/17/chat-001"}',
                    ]
                )
                + "\n",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    "--repo-root",
                    str(root),
                    "aggregate",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            task_groups_path = root / "meta" / "task-groups.md"
            self.assertTrue(task_groups_path.exists())
            self.assertIn("Would write task groups: yes", completed.stdout)
            self.assertIn(
                "## bug-debug-performance-react",
                task_groups_path.read_text(encoding="utf-8"),
            )

    def test_aggregate_dry_run_does_not_write_task_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "meta" / "quick-reference.md",
                calibration_quick_reference(aggregation_trigger=1),
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ENGINE_PATH),
                    "--repo-root",
                    str(root),
                    "aggregate",
                    "--dry-run",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            self.assertIn("Would write task groups: yes", completed.stdout)
            self.assertFalse((root / "meta" / "task-groups.md").exists())

    def test_query_ranks_files_from_matching_task_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.archive.jsonl",
                "\n".join(
                    [
                        '{"file":"identity/profile.md","date":"2026-03-16","task":"Debug React performance bug","helpfulness":0.9,"note":"used","session_id":"chats/2026/03/16/chat-001"}',
                        '{"file":"identity/profile.md","date":"2026-03-17","task":"Debugging React performance bugs","helpfulness":0.7,"note":"used","session_id":"chats/2026/03/17/chat-001"}',
                        '{"file":"skills/SUMMARY.md","date":"2026-03-18","task":"Plan release checklist","helpfulness":0.6,"note":"used","session_id":"chats/2026/03/18/chat-001"}',
                    ]
                )
                + "\n",
            )

            inventory = memory_engine.load_inventory(root)
            report = memory_engine.format_query_report(
                root,
                inventory,
                "react debug performance",
                None,
                limit=5,
                group_limit=3,
            )

            self.assertEqual(
                report["matched_task_groups"][0]["group_name"],
                "bug-debug-performance-react",
            )
            self.assertEqual(report["results"][0]["file"], "identity/profile.md")

    def test_query_supports_explicit_task_group_filter(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.archive.jsonl",
                '{"file":"identity/profile.md","date":"2026-03-16","task":"Debug React performance bug","helpfulness":0.9,"note":"used","session_id":"chats/2026/03/16/chat-001"}\n',
            )

            inventory = memory_engine.load_inventory(root)
            report = memory_engine.format_query_report(
                root,
                inventory,
                "",
                "bug-debug-performance-react",
                limit=5,
                group_limit=3,
            )

            self.assertEqual(report["matched_task_groups"][0]["score"], 1.0)
            self.assertEqual(report["results"][0]["file"], "identity/profile.md")

    def test_malformed_access_jsonl_exits_with_context(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            access_file = root / "knowledge" / "ACCESS.jsonl"
            access_file.write_text("not valid json\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                memory_engine.load_inventory(root)

            message = str(ctx.exception)
            self.assertIn("knowledge/ACCESS.jsonl", message)
            self.assertIn("line 1", message)

    def test_ensure_repo_root_message_describes_sentinel_files(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            with self.assertRaises(SystemExit) as ctx:
                memory_engine.ensure_repo_root(root)

            message = str(ctx.exception)
            self.assertIn("README.md", message)
            self.assertIn("meta/quick-reference.md", message)


if __name__ == "__main__":
    unittest.main()
