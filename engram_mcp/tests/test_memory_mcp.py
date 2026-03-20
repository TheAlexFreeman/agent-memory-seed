from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from types import ModuleType
from typing import Any, ClassVar, cast

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "engram_mcp" / "memory_mcp.py"
VENV_PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"


def load_memory_mcp_module():
    spec = importlib.util.spec_from_file_location("memory_mcp", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(f"memory_mcp dependencies unavailable: {exc.name}")
    return module


class MemoryMCPTests(unittest.TestCase):
    module: ClassVar[ModuleType]

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_memory_mcp_module()

    def test_root_listing_hides_humans_by_default(self) -> None:
        output = asyncio.run(self.module.memory_list_folder(path="."))

        self.assertNotIn("HUMANS/", output)
        self.assertIn("identity/", output)

    def test_root_listing_can_include_humans(self) -> None:
        output = asyncio.run(self.module.memory_list_folder(path=".", include_humans=True))

        self.assertIn("HUMANS/", output)

    def test_explicit_humans_listing_still_works(self) -> None:
        output = asyncio.run(self.module.memory_list_folder(path="HUMANS"))

        self.assertIn("docs/", output)
        self.assertIn("tooling/", output)

    def test_search_hides_humans_by_default(self) -> None:
        output = asyncio.run(
            self.module.memory_search(query="Human-Focused Documentation", path=".")
        )

        self.assertIn("No matches", output)

    def test_search_can_include_humans(self) -> None:
        output = asyncio.run(
            self.module.memory_search(
                query="Human-Focused Documentation",
                path=".",
                include_humans=True,
            )
        )

        self.assertIn("HUMANS/README.md", output)

    def test_explicit_humans_read_still_works(self) -> None:
        raw = asyncio.run(self.module.memory_read_file(path="HUMANS/README.md"))
        output = json.loads(raw)

        self.assertIn("Human-Focused Documentation", output["content"])
        self.assertIn("version_token", output)

    def test_read_file_returns_structured_payload(self) -> None:
        raw = asyncio.run(self.module.memory_read_file(path="meta/quick-reference.md"))
        payload = json.loads(raw)

        self.assertIn("version_token", payload)
        self.assertIsNone(payload["frontmatter"])
        self.assertIn("Quick Reference", payload["content"])

    def test_read_file_works_over_stdio_transport(self) -> None:
        if not VENV_PYTHON.exists():
            raise unittest.SkipTest(f"venv interpreter not found: {VENV_PYTHON}")

        server = StdioServerParameters(
            command=str(VENV_PYTHON),
            args=[str(SCRIPT_PATH)],
            cwd=str(REPO_ROOT),
            env={"MEMORY_REPO_ROOT": str(REPO_ROOT)},
        )

        async def run_call() -> dict[str, object]:
            async with stdio_client(server) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    result = await session.call_tool(
                        "memory_read_file",
                        {"path": "AGENTS.md"},
                    )
                    text_block = cast(Any, result.content[0])
                    return cast(dict[str, object], json.loads(text_block.text))

        payload = anyio.run(run_call)

        self.assertIn("Agent Memory System", cast(str, payload["content"]))
        self.assertIn("version_token", payload)

    def test_new_tools_are_exported(self) -> None:
        for name in (
            "memory_git_log",
            "memory_check_knowledge_freshness",
            "memory_check_aggregation_triggers",
            "memory_aggregate_access",
            "memory_run_periodic_review",
            "memory_get_file_provenance",
            "memory_inspect_commit",
            "memory_record_periodic_review",
            "memory_mark_plan_item_complete",
            "memory_create_plan",
        ):
            self.assertTrue(callable(getattr(self.module, name)))
        self.assertFalse(hasattr(self.module, "memory_write"))
        self.assertFalse(hasattr(self.module, "memory_commit"))


if __name__ == "__main__":
    unittest.main()
