from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from memory_engine_service import MemoryEngineService
from memory_mcp.server import MemoryMCPApplication, build_server
from tests.test_memory_engine import build_minimal_repo


class MemoryMCPTests(unittest.TestCase):
    def test_read_memory_returns_provenance_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            result = service.read_memory("identity/profile.md")

            self.assertEqual(result["path"], "identity/profile.md")
            self.assertEqual(result["frontmatter"]["trust"], "high")
            self.assertTrue(result["requires_access_log"])
            self.assertFalse(result["provenance_pause_required"])

    def test_read_memory_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            with self.assertRaises(ValueError):
                service.read_memory("../outside.md")

    def test_log_access_appends_and_reports_aggregation_state(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            result = service.log_access(
                "identity/profile.md",
                "status follow-up",
                0.9,
                "used heavily",
                session_id="chats/2026/03/16/chat-002",
                access_date="2026-03-16",
            )

            self.assertEqual(result["access_log"], "identity/ACCESS.jsonl")
            self.assertEqual(result["entry"]["file"], "identity/profile.md")
            access_lines = (
                (root / "identity" / "ACCESS.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
            )
            self.assertEqual(len(access_lines), 1)
            self.assertEqual(result["aggregation"]["stage"], "Exploration")

    def test_get_context_returns_ranked_excerpts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)

            service = MemoryEngineService(root)
            context = service.get_context("status test", limit=2, excerpt_chars=80)

            self.assertEqual(context["topic"], "status test")
            self.assertGreaterEqual(len(context["context"]), 1)
            self.assertEqual(context["context"][0]["path"], "identity/profile.md")

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
            status = app.status_memory()
            query = app.query_memory("status test", limit=3)

            self.assertEqual(status["stage"], "Exploration")
            self.assertEqual(query["results"][0]["file"], "identity/profile.md")
