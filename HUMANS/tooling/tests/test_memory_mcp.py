from __future__ import annotations

import asyncio
import importlib.util
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "memory_mcp.py"


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
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_memory_mcp_module()

    def test_root_listing_hides_humans_by_default(self) -> None:
        output = asyncio.run(
            self.module.memory_list_folder(self.module.ListFolderInput(path="."))
        )

        self.assertNotIn("HUMANS/", output)
        self.assertIn("identity/", output)

    def test_root_listing_can_include_humans(self) -> None:
        output = asyncio.run(
            self.module.memory_list_folder(
                self.module.ListFolderInput(path=".", include_humans=True)
            )
        )

        self.assertIn("HUMANS/", output)

    def test_explicit_humans_listing_still_works(self) -> None:
        output = asyncio.run(
            self.module.memory_list_folder(self.module.ListFolderInput(path="HUMANS"))
        )

        self.assertIn("docs/", output)
        self.assertIn("tooling/", output)

    def test_search_hides_humans_by_default(self) -> None:
        output = asyncio.run(
            self.module.memory_search(
                self.module.SearchInput(query="Human-Focused Documentation", path=".")
            )
        )

        self.assertIn("No matches", output)

    def test_search_can_include_humans(self) -> None:
        output = asyncio.run(
            self.module.memory_search(
                self.module.SearchInput(
                    query="Human-Focused Documentation",
                    path=".",
                    include_humans=True,
                )
            )
        )

        self.assertIn("HUMANS/README.md", output)

    def test_explicit_humans_read_still_works(self) -> None:
        output = asyncio.run(
            self.module.memory_read_file(
                self.module.ReadFileInput(path="HUMANS/README.md")
            )
        )

        self.assertIn("Human-Focused Documentation", output)


if __name__ == "__main__":
    unittest.main()
