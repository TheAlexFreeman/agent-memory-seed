from __future__ import annotations

import asyncio
import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_server_module():
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("tools.agent_memory_mcp.server")
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(
            f"agent_memory_mcp dependencies unavailable: {exc.name}"
        ) from exc


class AgentMemoryWriteToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = load_server_module()
        cls.errors = importlib.import_module("tools.agent_memory_mcp.errors")

    def _init_repo_with_file(self, rel_path: str) -> Path:
        temp_root = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init"], cwd=temp_root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )

        target = temp_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("# temp\n", encoding="utf-8")
        subprocess.run(["git", "add", rel_path], cwd=temp_root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "seed"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return temp_root

    def test_memory_delete_uses_permission_hook_for_allowed_paths(self) -> None:
        repo_root = self._init_repo_with_file("plans/delete-me.md")
        calls: list[str] = []

        def hook(path: str) -> None:
            calls.append(path)

        _, tools, _, _ = self.server.create_mcp(
            repo_root=repo_root,
            delete_permission_hook=hook,
        )

        asyncio.run(tools["memory_delete"](path="plans/delete-me.md"))

        self.assertEqual(calls, ["plans/delete-me.md"])
        self.assertFalse((repo_root / "plans" / "delete-me.md").exists())
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("D\tplans/delete-me.md", staged)

    def test_memory_delete_blocks_when_permission_hook_rejects(self) -> None:
        repo_root = self._init_repo_with_file("scratchpad/delete-me.md")

        def hook(path: str) -> None:
            raise RuntimeError(f"blocked {path}")

        _, tools, _, _ = self.server.create_mcp(
            repo_root=repo_root,
            delete_permission_hook=hook,
        )

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_delete"](path="scratchpad/delete-me.md"))

        self.assertTrue((repo_root / "scratchpad" / "delete-me.md").exists())


if __name__ == "__main__":
    unittest.main()
