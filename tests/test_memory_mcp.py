from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any, cast

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from memory_engine_service import (
    InvalidMemoryRequestError,
    InvalidRepositoryError,
    InventoryLoadError,
    MemoryEngineService,
    MemoryNotFoundError,
    UnsupportedMemoryTargetError,
)
from memory_mcp.server import MemoryMCPApplication, build_server
from tests.test_memory_engine import build_minimal_repo


class MemoryMCPTests(unittest.TestCase):
    def test_read_memory_returns_provenance_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            result = cast(dict[str, Any], service.read_memory("identity/profile.md"))
            frontmatter = cast(dict[str, Any], result["frontmatter"])

            self.assertEqual(result["path"], "identity/profile.md")
            self.assertEqual(frontmatter["trust"], "high")
            self.assertTrue(result["requires_access_log"])
            self.assertFalse(result["provenance_pause_required"])

    def test_read_memory_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            with self.assertRaises(InvalidMemoryRequestError):
                service.read_memory("../outside.md")

    def test_read_memory_rejects_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            with self.assertRaises(MemoryNotFoundError):
                service.read_memory("identity/missing.md")

    def test_read_memory_rejects_unsupported_file_type(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "identity" / "avatar.png").write_bytes(b"png")

            service = MemoryEngineService(root)
            with self.assertRaises(UnsupportedMemoryTargetError):
                service.read_memory("identity/avatar.png")

    def test_log_access_appends_and_reports_aggregation_state(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            result = cast(
                dict[str, Any],
                service.log_access(
                    "identity/profile.md",
                    "status follow-up",
                    0.9,
                    "used heavily",
                    session_id="chats/2026/03/16/chat-002",
                    access_date="2026-03-16",
                ),
            )
            entry = cast(dict[str, Any], result["entry"])
            aggregation = cast(dict[str, Any], result["aggregation"])

            self.assertEqual(result["access_log"], "identity/ACCESS.jsonl")
            self.assertEqual(entry["file"], "identity/profile.md")
            access_lines = (
                (root / "identity" / "ACCESS.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            self.assertEqual(len(access_lines), 1)
            self.assertEqual(aggregation["stage"], "Exploration")

    def test_log_access_rejects_invalid_helpfulness(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            with self.assertRaises(InvalidMemoryRequestError):
                service.log_access(
                    "identity/profile.md",
                    "status follow-up",
                    1.5,
                    "used heavily",
                )

    def test_log_access_rejects_access_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            with self.assertRaises(UnsupportedMemoryTargetError):
                service.log_access(
                    "identity/ACCESS.jsonl",
                    "status follow-up",
                    0.8,
                    "used heavily",
                )

    def test_status_raises_inventory_load_error_for_malformed_access(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "knowledge" / "ACCESS.jsonl").write_text(
                "not valid json\n", encoding="utf-8"
            )

            service = MemoryEngineService(root)
            with self.assertRaises(InventoryLoadError):
                service.status()

    def test_get_context_returns_ranked_excerpts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            context = cast(
                dict[str, Any],
                service.get_context("status test", limit=2, excerpt_chars=80),
            )
            context_items = cast(list[dict[str, Any]], context["context"])

            self.assertEqual(context["topic"], "status test")
            self.assertGreaterEqual(len(context_items), 1)
            self.assertEqual(context_items[0]["path"], "identity/profile.md")

    def test_get_context_skips_unreadable_ranked_hits(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "knowledge" / "ACCESS.jsonl").write_text(
                "\n".join(
                    [
                        '{"file":"identity/profile.md","date":"2026-03-16","task":"status test","helpfulness":0.8,"note":"used","session_id":"chats/2026/03/16/chat-001"}',
                        '{"file":"identity/missing.md","date":"2026-03-17","task":"status test","helpfulness":1.0,"note":"stale hit","session_id":"chats/2026/03/16/chat-001"}',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            service = MemoryEngineService(root)
            context = cast(
                dict[str, Any],
                service.get_context("status test", limit=3, excerpt_chars=80),
            )
            context_items = cast(list[dict[str, Any]], context["context"])

            self.assertEqual(len(context_items), 1)
            self.assertEqual(context_items[0]["path"], "identity/profile.md")

    def test_build_server_returns_fastmcp(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            server = build_server(root)
            self.assertIsInstance(server, FastMCP)

    def test_application_methods_delegate_to_service(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            app = MemoryMCPApplication(root)
            status = cast(dict[str, Any], app.status_memory())
            query = cast(dict[str, Any], app.query_memory("status test", limit=3))
            results = cast(list[dict[str, Any]], query["results"])

            self.assertEqual(status["stage"], "Exploration")
            self.assertEqual(results[0]["file"], "identity/profile.md")

    def test_application_raises_tool_error_for_invalid_read(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            app = MemoryMCPApplication(root)
            with self.assertRaises(ToolError) as ctx:
                app.read_memory("../outside.md")

            self.assertIn("invalid_request", str(ctx.exception))

    def test_application_raises_tool_error_for_invalid_query(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            app = MemoryMCPApplication(root)
            with self.assertRaises(ToolError) as ctx:
                app.query_memory("", limit=3)

            self.assertIn("invalid_request", str(ctx.exception))

    def test_service_rejects_invalid_repo_root(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)

            with self.assertRaises(InvalidRepositoryError):
                MemoryEngineService(root)
