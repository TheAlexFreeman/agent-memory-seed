from __future__ import annotations

import asyncio
import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date
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
        try:
            cls.frontmatter_utils = importlib.import_module(
                "tools.agent_memory_mcp.frontmatter_utils"
            )
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(
                f"semantic write tool dependencies unavailable: {exc.name}"
            ) from exc

    def _init_repo(self, files: dict[str, str]) -> Path:
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

        for rel_path, content in files.items():
            target = temp_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=temp_root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "commit", "-m", "seed"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return temp_root

    def _init_repo_with_file(self, rel_path: str) -> Path:
        return self._init_repo({rel_path: "# temp\n"})

    def _create_tools(
        self,
        repo_root: Path,
        delete_permission_hook=None,
        *,
        enable_raw_write_tools: bool = False,
    ) -> dict[str, object]:
        _, tools, _, _ = self.server.create_mcp(
            repo_root=repo_root,
            delete_permission_hook=delete_permission_hook,
            enable_raw_write_tools=enable_raw_write_tools,
        )
        return tools

    def test_memory_delete_uses_permission_hook_for_allowed_paths(self) -> None:
        repo_root = self._init_repo_with_file("plans/delete-me.md")
        calls: list[str] = []

        def hook(path: str) -> None:
            calls.append(path)

        _, tools, _, _ = self.server.create_mcp(
            repo_root=repo_root,
            delete_permission_hook=hook,
            enable_raw_write_tools=True,
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
            enable_raw_write_tools=True,
        )

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_delete"](path="scratchpad/delete-me.md"))

        self.assertTrue((repo_root / "scratchpad" / "delete-me.md").exists())

    def test_mark_plan_item_complete_updates_frontmatter_and_summary(self) -> None:
        repo_root = self._init_repo(
            {
                "plans/test-plan.md": """---
source: agent-generated
type: implementation-plan
created: 2026-03-17
last_verified: 2026-03-17
trust: medium
status: active
next_action: Do first step
---

# Test Plan

### Phase 1 — Build core flow · ☐ 0/2 complete

1. ☐ Do first step
2. ☐ Do second step

## Progress log

| Date | Action |
|---|---|
""",
                "plans/SUMMARY.md": """# Plans — Summary

## Active plans

<!-- BEGIN: test-plan -->
### `test-plan.md` · status: active · trust: medium
**Progress:** 0/2 items complete
**Next action:** Do first step
<!-- END: test-plan -->
""",
            }
        )
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        raw = asyncio.run(
            tools["memory_mark_plan_item_complete"](
                plan_id="test-plan",
                phase_index=0,
                item_index=0,
            )
        )
        payload = json.loads(raw)
        frontmatter, body = self.frontmatter_utils.read_with_frontmatter(
            repo_root / "plans" / "test-plan.md"
        )
        summary = (repo_root / "plans" / "SUMMARY.md").read_text(encoding="utf-8")

        self.assertEqual(payload["new_state"]["next_action"], "Do second step")
        self.assertEqual(payload["new_state"]["phase_progress"], [1, 2])
        self.assertEqual(payload["new_state"]["plan_progress"], [1, 2])
        self.assertEqual(frontmatter["next_action"], "Do second step")
        self.assertEqual(str(frontmatter["last_verified"]), str(date.today()))
        self.assertIn("1. ☑ Do first step", body)
        self.assertIn("**Progress:** 1/2 items complete", summary)
        self.assertIn("**Next action:** Do second step", summary)

    def test_promote_knowledge_updates_frontmatter_and_both_summaries(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/_unverified/literature/test-note.md": """---
title: Test Note
source: agent-generated
created: 2026-03-17
last_verified: 2026-03-17
trust: low
origin_session: manual
---

# Test Note
""",
                "knowledge/_unverified/SUMMARY.md": """# Unverified Knowledge

<!-- section: literature -->
### Literature
- **[test-note.md](knowledge/_unverified/literature/test-note.md)** — Test Note

---
""",
                "knowledge/SUMMARY.md": """# Knowledge

<!-- section: literature -->
### Literature

---
""",
            }
        )
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        raw = asyncio.run(
            tools["memory_promote_knowledge"](
                source_path="knowledge/_unverified/literature/test-note.md",
                trust_level="high",
            )
        )
        payload = json.loads(raw)
        target_path = repo_root / "knowledge" / "literature" / "test-note.md"
        old_path = repo_root / "knowledge" / "_unverified" / "literature" / "test-note.md"
        frontmatter, _ = self.frontmatter_utils.read_with_frontmatter(target_path)
        unverified_summary = (
            repo_root / "knowledge" / "_unverified" / "SUMMARY.md"
        ).read_text(encoding="utf-8")
        verified_summary = (repo_root / "knowledge" / "SUMMARY.md").read_text(
            encoding="utf-8"
        )

        self.assertEqual(payload["new_state"]["new_path"], "knowledge/literature/test-note.md")
        self.assertEqual(payload["new_state"]["trust"], "high")
        self.assertFalse(old_path.exists())
        self.assertTrue(target_path.exists())
        self.assertEqual(frontmatter["trust"], "high")
        self.assertEqual(str(frontmatter["last_verified"]), str(date.today()))
        self.assertNotIn("knowledge/_unverified/literature/test-note.md", unverified_summary)
        self.assertIn("knowledge/literature/test-note.md", verified_summary)

    def test_memory_delete_blocks_protected_identity_paths(self) -> None:
        repo_root = self._init_repo(
            {
                "identity/profile.md": """---
source: user-stated
created: 2026-03-17
last_verified: 2026-03-17
trust: high
---

# Profile
""",
            }
        )
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_delete"](path="identity/profile.md"))

        self.assertTrue((repo_root / "identity" / "profile.md").exists())

    def test_update_plan_next_action_rejects_stale_version_token(self) -> None:
        repo_root = self._init_repo(
            {
                "plans/test-plan.md": """---
source: agent-generated
type: implementation-plan
created: 2026-03-17
last_verified: 2026-03-17
trust: medium
status: active
next_action: Original next action
---

# Test Plan

### Phase 1 — Build core flow · ☐ 0/1 complete

1. ☐ Original next action

## Progress log

| Date | Action |
|---|---|
""",
                "plans/SUMMARY.md": """# Plans — Summary

## Active plans

<!-- BEGIN: test-plan -->
### `test-plan.md` · status: active · trust: medium
**Progress:** 0/1 items complete
**Next action:** Original next action
<!-- END: test-plan -->
""",
            }
        )
        tools = self._create_tools(repo_root)
        read_payload = json.loads(
            asyncio.run(tools["memory_read_file"](path="plans/test-plan.md"))
        )
        old_token = read_payload["version_token"]

        plan_path = repo_root / "plans" / "test-plan.md"
        plan_path.write_text(
            plan_path.read_text(encoding="utf-8").replace(
                "Original next action",
                "Someone else changed this plan",
                1,
            ),
            encoding="utf-8",
        )

        with self.assertRaises(self.errors.ConflictError):
            asyncio.run(
                tools["memory_update_plan_next_action"](
                    plan_id="test-plan",
                    next_action="Fresh next action",
                    version_token=old_token,
                )
            )

    def test_raw_write_tools_are_disabled_by_default(self) -> None:
        repo_root = self._init_repo_with_file("plans/delete-me.md")
        tools = self._create_tools(repo_root)

        self.assertNotIn("memory_delete", tools)
        self.assertNotIn("memory_move", tools)
        self.assertIn("memory_mark_plan_item_complete", tools)

    def test_raw_write_tools_can_be_enabled_explicitly(self) -> None:
        repo_root = self._init_repo_with_file("plans/delete-me.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        self.assertIn("memory_delete", tools)
        self.assertIn("memory_move", tools)

    def test_memory_delete_rejects_repo_root_files(self) -> None:
        repo_root = self._init_repo_with_file("README.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_delete"](path="README.md"))

    def test_memory_move_rejects_repo_root_source_files(self) -> None:
        repo_root = self._init_repo_with_file("README.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_move"](
                    source="README.md",
                    dest="knowledge/README.md",
                )
            )

    def test_memory_add_knowledge_file_requires_low_trust_and_session_id(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/_unverified/SUMMARY.md": """# Unverified Knowledge

<!-- section: django -->
### Django

---
""",
            }
        )
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_add_knowledge_file"](
                    path="knowledge/_unverified/django/test.md",
                    content="# Test\n",
                    source="external-research",
                    session_id="chats/2026/03/19/chat-001",
                    trust="high",
                )
            )

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_add_knowledge_file"](
                    path="knowledge/_unverified/django/test.md",
                    content="# Test\n",
                    source="external-research",
                    session_id="chat-001",
                )
            )

    def test_memory_create_plan_rejects_noncanonical_session_id(self) -> None:
        repo_root = self._init_repo({"plans/SUMMARY.md": "# Plans\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_create_plan"](
                    plan_id="test-plan",
                    title="Test",
                    description="desc",
                    content="# Plan\n",
                    next_action="Do it",
                    session_id="chat-001",
                )
            )

    def test_memory_update_identity_trait_rejects_non_slug_filename(self) -> None:
        repo_root = self._init_repo(
            {
                "identity/profile.md": """---
source: user-stated
origin_session: manual
created: 2026-03-17
trust: high
---

# Profile
""",
            }
        )
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_update_identity_trait"](
                    file="../README",
                    key="tone",
                    value="direct",
                )
            )

    def test_memory_record_chat_summary_rejects_noncanonical_session_id(self) -> None:
        repo_root = self._init_repo({"chats/SUMMARY.md": "# Chats\n## Structure\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_record_chat_summary"](
                    session_id="../meta/chat-001",
                    summary="# Chat Summary\n",
                )
            )


if __name__ == "__main__":
    unittest.main()
