from __future__ import annotations

import asyncio
import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, ClassVar, Coroutine, cast

REPO_ROOT = Path(__file__).resolve().parents[2]
ToolCallable = Callable[..., Coroutine[Any, Any, str]]


def load_server_module() -> ModuleType:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("engram_mcp.agent_memory_mcp.server")
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(f"agent_memory_mcp dependencies unavailable: {exc.name}") from exc


class AgentMemoryWriteToolTests(unittest.TestCase):
    server: ClassVar[ModuleType]
    errors: ClassVar[ModuleType]
    frontmatter_utils: ClassVar[Any]
    git_repo_module: ClassVar[ModuleType]

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = load_server_module()
        cls.errors = importlib.import_module("engram_mcp.agent_memory_mcp.errors")
        cls.git_repo_module = importlib.import_module("engram_mcp.agent_memory_mcp.git_repo")
        try:
            cls.frontmatter_utils = importlib.import_module(
                "engram_mcp.agent_memory_mcp.frontmatter_utils"
            )
        except ModuleNotFoundError as exc:
            raise unittest.SkipTest(
                f"semantic write tool dependencies unavailable: {exc.name}"
            ) from exc

    def setUp(self) -> None:
        # Every test gets a fresh TemporaryDirectory; it's auto-deleted on teardown.
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)

    def _init_repo(
        self,
        files: dict[str, str],
        *,
        initial_commit_date: str | None = None,
    ) -> Path:
        temp_root = Path(self._tmpdir.name) / (f"repo_{id(files)}")
        temp_root.mkdir(parents=True, exist_ok=True)
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
        subprocess.run(
            ["git", "add", "."], cwd=temp_root, check=True, capture_output=True, text=True
        )
        commit_env = None
        if initial_commit_date is not None:
            commit_env = {
                **os.environ,
                "GIT_AUTHOR_DATE": initial_commit_date,
                "GIT_COMMITTER_DATE": initial_commit_date,
            }
        subprocess.run(
            ["git", "commit", "-m", "seed"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
            env=commit_env,
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
    ) -> dict[str, ToolCallable]:
        _, tools, _, _ = self.server.create_mcp(
            repo_root=repo_root,
            delete_permission_hook=delete_permission_hook,
            enable_raw_write_tools=enable_raw_write_tools,
        )
        return cast(dict[str, ToolCallable], tools)

    def test_create_mcp_accepts_git_subdirectory_root(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/README.md": "# Knowledge\n",
                "knowledge/topic/note.md": "# Note\n",
            }
        )
        _, tools, resolved_root, repo = self.server.create_mcp(
            repo_root=repo_root / "knowledge",
            enable_raw_write_tools=True,
        )

        self.assertEqual(resolved_root, repo_root)
        self.assertEqual(repo.root, repo_root)
        payload = json.loads(asyncio.run(tools["memory_read_file"](path="knowledge/topic/note.md")))
        self.assertIn("# Note", payload["content"])

    def _write_and_commit(
        self,
        repo_root: Path,
        files: dict[str, str],
        message: str,
        *,
        commit_date: str | None = None,
    ) -> str:
        for rel_path, content in files.items():
            target = repo_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            env=(
                {
                    **os.environ,
                    "GIT_AUTHOR_DATE": commit_date,
                    "GIT_COMMITTER_DATE": commit_date,
                }
                if commit_date is not None
                else None
            ),
        )
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    def _init_host_repo(
        self, files: dict[str, str], *, initial_commit_date: str | None = None
    ) -> Path:
        temp_root = Path(self._tmpdir.name) / (f"host_{id(files)}")
        temp_root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=temp_root, check=True, capture_output=True, text=True)
        subprocess.run(
            ["git", "config", "user.name", "Host User"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "host@example.com"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
        )
        for rel_path, content in files.items():
            target = temp_root / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        subprocess.run(
            ["git", "add", "."], cwd=temp_root, check=True, capture_output=True, text=True
        )
        commit_env = None
        if initial_commit_date is not None:
            commit_env = {
                **os.environ,
                "GIT_AUTHOR_DATE": initial_commit_date,
                "GIT_COMMITTER_DATE": initial_commit_date,
            }
        subprocess.run(
            ["git", "commit", "-m", "host seed"],
            cwd=temp_root,
            check=True,
            capture_output=True,
            text=True,
            env=commit_env,
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
Detail: plans/test-plan.md
Progress: 0/2 complete
Next: Do first step
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
        self.assertIn("### Test Plan · status: active · trust: medium", summary)
        self.assertIn("Progress: 1/2 complete", summary)
        self.assertIn("Next: Do second step", summary)

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
        unverified_summary = (repo_root / "knowledge" / "_unverified" / "SUMMARY.md").read_text(
            encoding="utf-8"
        )
        verified_summary = (repo_root / "knowledge" / "SUMMARY.md").read_text(encoding="utf-8")

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
Detail: plans/test-plan.md
Progress: 0/1 complete
Next: Original next action
<!-- END: test-plan -->
""",
            }
        )
        tools = self._create_tools(repo_root)
        read_payload = json.loads(asyncio.run(tools["memory_read_file"](path="plans/test-plan.md")))
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

    def test_memory_write_rejects_repo_root_files(self) -> None:
        repo_root = self._init_repo_with_file("README.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_write"](path="README.md", content="# Rewritten\n"))

    def test_memory_edit_rejects_repo_root_files(self) -> None:
        repo_root = self._init_repo({"agent-bootstrap.toml": 'router = "README.md"\n'})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_edit"](
                    path="agent-bootstrap.toml",
                    old_string="README.md",
                    new_string="meta/quick-reference.md",
                )
            )

    def test_memory_update_frontmatter_rejects_repo_root_files(self) -> None:
        repo_root = self._init_repo(
            {
                "README.md": "---\ntitle: README\n---\n\n# Project\n",
            }
        )
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_update_frontmatter"](
                    path="README.md",
                    updates='{"title": "Updated"}',
                )
            )

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

    def test_memory_move_rejects_protected_identity_destination(self) -> None:
        repo_root = self._init_repo_with_file("knowledge/note.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_move"](
                    source="knowledge/note.md",
                    dest="identity/note.md",
                )
            )

    def test_memory_move_rejects_protected_meta_destination(self) -> None:
        repo_root = self._init_repo_with_file("plans/note.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_move"](
                    source="plans/note.md",
                    dest="meta/note.md",
                )
            )

    def test_memory_move_rejects_protected_skills_destination(self) -> None:
        repo_root = self._init_repo_with_file("scratchpad/note.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_move"](
                    source="scratchpad/note.md",
                    dest="skills/note.md",
                )
            )

    def test_memory_move_rejects_protected_chats_destination(self) -> None:
        repo_root = self._init_repo_with_file("knowledge/note.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_move"](
                    source="knowledge/note.md",
                    dest="chats/2026/03/19/chat-001/note.md",
                )
            )

    def test_memory_move_allows_knowledge_destination(self) -> None:
        repo_root = self._init_repo_with_file("knowledge/old/note.md")
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        asyncio.run(
            tools["memory_move"](
                source="knowledge/old/note.md",
                dest="knowledge/new/note.md",
            )
        )

        self.assertTrue((repo_root / "knowledge" / "new" / "note.md").exists())

    def test_memory_delete_handles_dash_prefixed_filename(self) -> None:
        repo_root = self._init_repo({"knowledge/-danger.md": "# Danger\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        asyncio.run(tools["memory_delete"](path="knowledge/-danger.md"))

        self.assertFalse((repo_root / "knowledge" / "-danger.md").exists())

    def test_memory_move_handles_dash_prefixed_filename(self) -> None:
        repo_root = self._init_repo({"knowledge/-danger.md": "# Danger\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        asyncio.run(
            tools["memory_move"](
                source="knowledge/-danger.md",
                dest="knowledge/archive/safe.md",
            )
        )

        self.assertFalse((repo_root / "knowledge" / "-danger.md").exists())
        self.assertTrue((repo_root / "knowledge" / "archive" / "safe.md").exists())

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

    def test_memory_create_plan_uses_human_title_in_summary(self) -> None:
        repo_root = self._init_repo({"plans/SUMMARY.md": "# Plans\n\n## Active plans\n"})
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_create_plan"](
                plan_id="test-plan",
                title="Test Plan",
                description="Investigate regressions",
                content="# Test Plan\n\n## Context\n",
                next_action="Do the first thing",
                session_id="chats/2026/03/19/chat-001",
            )
        )

        plan_frontmatter, _ = self.frontmatter_utils.read_with_frontmatter(
            repo_root / "plans" / "test-plan.md"
        )
        summary = (repo_root / "plans" / "SUMMARY.md").read_text(encoding="utf-8")

        self.assertEqual(plan_frontmatter["title"], "Test Plan")
        self.assertIn("### Test Plan · status: active · trust: medium", summary)
        self.assertIn("Detail: plans/test-plan.md", summary)

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

    def test_memory_update_identity_trait_replaces_existing_body_section(self) -> None:
        repo_root = self._init_repo(
            {
                "identity/profile.md": """---
source: user-stated
origin_session: manual
created: 2026-03-17
trust: high
---

# Profile

## tone

Direct and concise.

## workflow

Structured.
""",
            }
        )
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_update_identity_trait"](
                file="profile",
                key="tone",
                value="Even more direct.",
                mode="upsert",
            )
        )

        updated = (repo_root / "identity" / "profile.md").read_text(encoding="utf-8")
        self.assertIn("## tone\n\nEven more direct.", updated)
        self.assertNotIn("Even more direct.\n\nDirect and concise.", updated)
        self.assertNotIn("Direct and concise.", updated)
        self.assertIn("## workflow\n\nStructured.", updated)

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

    def test_memory_record_session_writes_summary_reflection_and_access_in_one_commit(self) -> None:
        repo_root = self._init_repo(
            {
                "chats/SUMMARY.md": "# Chats\n## Structure\n",
                "knowledge/topic.md": "# Topic\n",
                "plans/demo.md": "# Demo\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_record_session"](
                session_id="chats/2026/03/20/chat-002",
                summary="# Session Summary\n\nDid the work.\n",
                reflection="Observed a cleaner wrap-up path.",
                key_topics="semantic-tools,wrapup",
                access_entries=[
                    {
                        "file": "knowledge/topic.md",
                        "task": "session wrap-up",
                        "helpfulness": 0.8,
                        "note": "Relevant context for summary.",
                    },
                    {
                        "file": "plans/demo.md",
                        "task": "session wrap-up",
                        "helpfulness": 0.6,
                        "note": "Referenced current work.",
                    },
                ],
            )
        )
        payload = json.loads(raw)

        session_summary = (
            repo_root / "chats" / "2026" / "03" / "20" / "chat-002" / "SUMMARY.md"
        ).read_text(encoding="utf-8")
        reflection = (
            repo_root / "chats" / "2026" / "03" / "20" / "chat-002" / "reflection.md"
        ).read_text(encoding="utf-8")
        chats_summary = (repo_root / "chats" / "SUMMARY.md").read_text(encoding="utf-8")
        knowledge_access = [
            json.loads(line)
            for line in (repo_root / "knowledge" / "ACCESS.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        plans_access = [
            json.loads(line)
            for line in (repo_root / "plans" / "ACCESS.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        log_count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertEqual(
            payload["commit_message"], "[chat] Record session chats/2026/03/20/chat-002"
        )
        self.assertEqual(payload["new_state"]["session_id"], "chats/2026/03/20/chat-002")
        self.assertIn("key_topics:", session_summary)
        self.assertIn("semantic-tools", session_summary)
        self.assertIn("## Session reflection\n\nObserved a cleaner wrap-up path.\n", reflection)
        self.assertIn("chats/2026/03/20/chat-002/", chats_summary)
        self.assertEqual(knowledge_access[0]["session_id"], "chats/2026/03/20/chat-002")
        self.assertEqual(plans_access[0]["session_id"], "chats/2026/03/20/chat-002")
        self.assertEqual(log_count, "2")

    def test_memory_append_scratchpad_accepts_dated_slug_and_creates_file(self) -> None:
        repo_root = self._init_repo({"scratchpad/CURRENT.md": "# Current\n"})
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_append_scratchpad"](
                target="scratchpad/2026-03-20-worklog.md",
                content="Initial note",
                section="Findings",
            )
        )
        payload = json.loads(raw)

        scratchpad = (repo_root / "scratchpad" / "2026-03-20-worklog.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            payload["new_state"]["target"],
            "scratchpad/2026-03-20-worklog.md",
        )
        self.assertIn("## Findings\n\nInitial note\n", scratchpad)

    def test_memory_append_scratchpad_rejects_invalid_target_format(self) -> None:
        repo_root = self._init_repo({"scratchpad/CURRENT.md": "# Current\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_append_scratchpad"](
                    target="scratchpad/not valid.md",
                    content="Invalid",
                )
            )

    def test_memory_flag_for_review_returns_item_id_and_uses_canonical_format(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/review-queue.md": "# Review Queue\n\n_No pending items._\n",
                "plans/demo.md": "# Demo\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_flag_for_review"](
                path="plans/demo.md",
                reason="Needs human review before promotion.",
                priority="urgent",
            )
        )
        payload = json.loads(raw)
        review_queue = (repo_root / "meta" / "review-queue.md").read_text(encoding="utf-8")

        self.assertEqual(payload["new_state"]["flagged_path"], "plans/demo.md")
        self.assertRegex(
            payload["new_state"]["item_id"],
            r"^\d{4}-\d{2}-\d{2}-review-plans-demo-md$",
        )
        self.assertIn("### [", review_queue)
        self.assertIn("**Item ID:** ", review_queue)
        self.assertIn("**Type:** proposed", review_queue)
        self.assertNotIn("_No pending items._", review_queue)

    def test_memory_resolve_review_item_moves_entry_to_resolved_section(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/review-queue.md": """# Review Queue

### [2026-03-20] Review plans/demo.md
**Item ID:** 2026-03-20-review-plans-demo-md
**Type:** proposed
**File:** plans/demo.md
**Priority:** normal
**Reason:** Review it.
**Status:** pending
""",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_resolve_review_item"](
                item_id="2026-03-20-review-plans-demo-md",
                resolution_note="Handled during maintenance.",
            )
        )
        payload = json.loads(raw)
        review_queue = (repo_root / "meta" / "review-queue.md").read_text(encoding="utf-8")

        self.assertEqual(payload["new_state"]["item_id"], "2026-03-20-review-plans-demo-md")
        self.assertEqual(
            payload["commit_message"],
            "[curation] Resolve review item: 2026-03-20-review-plans-demo-md",
        )
        self.assertIn("_No pending items._", review_queue)
        self.assertIn("## Resolved", review_queue)
        self.assertIn(
            "2026-03-20-review-plans-demo-md: Handled during maintenance.",
            review_queue,
        )
        self.assertNotIn("**Status:** pending", review_queue)

    def test_memory_update_skill_upserts_existing_section(self) -> None:
        repo_root = self._init_repo(
            {
                "skills/session-start.md": """---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Session Start

## Steps

Load compact context.
""",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_update_skill"](
                file="session-start",
                section="Steps",
                content="Load compact context and active plans.",
            )
        )
        payload = json.loads(raw)
        skill = (repo_root / "skills" / "session-start.md").read_text(encoding="utf-8")

        self.assertEqual(payload["new_state"]["section"], "Steps")
        self.assertIn("## Steps\n\nLoad compact context and active plans.", skill)
        self.assertIn(f"last_verified: '{date.today()}'", skill)

    def test_memory_update_skill_appends_existing_section(self) -> None:
        repo_root = self._init_repo(
            {
                "skills/session-sync.md": """---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Session Sync

## Steps

Capture a short checkpoint.
""",
            }
        )
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_update_skill"](
                file="session-sync",
                section="Steps",
                content="Record any open questions.",
                mode="append",
            )
        )
        skill = (repo_root / "skills" / "session-sync.md").read_text(encoding="utf-8")

        self.assertIn("Capture a short checkpoint.\nRecord any open questions.", skill)

    def test_memory_update_skill_replaces_existing_section(self) -> None:
        repo_root = self._init_repo(
            {
                "skills/session-wrapup.md": """---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Session Wrapup

## Steps

Old guidance.
""",
            }
        )
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_update_skill"](
                file="session-wrapup",
                section="Steps",
                content="Use the governed session recorder when available.",
                mode="replace",
            )
        )
        skill = (repo_root / "skills" / "session-wrapup.md").read_text(encoding="utf-8")

        self.assertIn("Use the governed session recorder when available.", skill)
        self.assertNotIn("Old guidance.", skill)

    def test_memory_update_skill_raises_for_missing_file_without_creation(self) -> None:
        repo_root = self._init_repo({"skills/SUMMARY.md": "# Skills\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.NotFoundError):
            asyncio.run(
                tools["memory_update_skill"](
                    file="missing-skill",
                    section="Steps",
                    content="Create guidance.",
                )
            )

    def test_memory_update_skill_can_create_missing_file(self) -> None:
        repo_root = self._init_repo({"skills/SUMMARY.md": "# Skills\n"})
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_update_skill"](
                file="new-skill",
                section="Steps",
                content="Create the first guidance block.",
                create_if_missing=True,
                source="agent-generated",
                trust="medium",
                origin_session="chats/2026/03/20/chat-001",
            )
        )
        payload = json.loads(raw)
        skill_path = repo_root / "skills" / "new-skill.md"
        skill = skill_path.read_text(encoding="utf-8")

        self.assertEqual(payload["new_state"]["section"], "Steps")
        self.assertTrue(skill_path.exists())
        self.assertIn("source: agent-generated", skill)
        self.assertIn("origin_session: chats/2026/03/20/chat-001", skill)
        self.assertIn("trust: medium", skill)
        self.assertIn("## Steps\n\nCreate the first guidance block.", skill)

    def test_memory_run_aggregation_dry_run_previews_without_writing_files(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/topic.md": "# Topic\n",
                "plans/demo.md": "# Demo\n",
                "skills/session-start.md": "# Session Start\n",
                "knowledge/SUMMARY.md": "# Knowledge\n\n## Usage patterns\n\n_No access data yet._\n",
                "plans/SUMMARY.md": "# Plans\n\n## Usage patterns\n\n_No access data yet._\n",
                "skills/SUMMARY.md": "# Skills\n\n## Usage patterns\n\n_No access data yet._\n",
                "knowledge/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "session_id": "chats/2026/03/19/chat-001",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                    ]
                )
                + "\n",
                "plans/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "session_id": "chats/2026/03/19/chat-001",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                    ]
                )
                + "\n",
                "skills/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "session_id": "chats/2026/03/19/chat-001",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                    ]
                )
                + "\n",
            }
        )
        tools = self._create_tools(repo_root)
        before_access = (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8")
        before_summary = (repo_root / "knowledge" / "SUMMARY.md").read_text(encoding="utf-8")

        raw = asyncio.run(tools["memory_run_aggregation"]())
        payload = json.loads(raw)

        self.assertIsNone(payload["commit_sha"])
        self.assertEqual(payload["new_state"]["entries_processed"], 9)
        self.assertEqual(payload["new_state"]["session_groups_processed"], 3)
        self.assertEqual(len(payload["new_state"]["clusters"]), 1)
        self.assertEqual(
            payload["new_state"]["clusters"][0]["files"],
            ["knowledge/topic.md", "plans/demo.md", "skills/session-start.md"],
        )
        self.assertEqual(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8"),
            before_access,
        )
        self.assertEqual(
            (repo_root / "knowledge" / "SUMMARY.md").read_text(encoding="utf-8"),
            before_summary,
        )

    def test_memory_run_aggregation_apply_updates_summaries_and_rotates_archives(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/topic.md": "# Topic\n",
                "plans/demo.md": "# Demo\n",
                "skills/session-start.md": "# Session Start\n",
                "knowledge/SUMMARY.md": "# Knowledge\n\n## Usage patterns\n\n_No access data yet._\n",
                "plans/SUMMARY.md": "# Plans\n\n## Usage patterns\n\n_No access data yet._\n",
                "skills/SUMMARY.md": "# Skills\n\n## Usage patterns\n\n_No access data yet._\n",
                "knowledge/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "knowledge/topic.md",
                                "helpfulness": 0.8,
                            }
                        ),
                    ]
                )
                + "\n",
                "plans/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "plans/demo.md",
                                "helpfulness": 0.7,
                            }
                        ),
                    ]
                )
                + "\n",
                "skills/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "date": "2026-03-18",
                                "session_id": "chats/2026/03/18/chat-001",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-19",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                        json.dumps(
                            {
                                "date": "2026-03-20",
                                "session_id": "chats/2026/03/20/chat-001",
                                "file": "skills/session-start.md",
                                "helpfulness": 0.9,
                            }
                        ),
                    ]
                )
                + "\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(tools["memory_run_aggregation"](dry_run=False))
        payload = json.loads(raw)

        knowledge_summary = (repo_root / "knowledge" / "SUMMARY.md").read_text(encoding="utf-8")
        plans_summary = (repo_root / "plans" / "SUMMARY.md").read_text(encoding="utf-8")
        skills_summary = (repo_root / "skills" / "SUMMARY.md").read_text(encoding="utf-8")
        knowledge_archive = (repo_root / "knowledge" / "ACCESS.archive.2026-03.jsonl").read_text(
            encoding="utf-8"
        )
        knowledge_access = (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8")
        log_count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertEqual(
            payload["commit_message"], f"[curation] Aggregate ACCESS logs ({date.today()})"
        )
        self.assertEqual(payload["new_state"]["entries_processed"], 9)
        self.assertEqual(payload["new_state"]["legacy_fallback_entries"], 3)
        self.assertIn(f"- Last aggregation: {date.today()}", knowledge_summary)
        self.assertIn(
            "knowledge/topic.md + plans/demo.md + skills/session-start.md", knowledge_summary
        )
        self.assertIn(f"- Last aggregation: {date.today()}", plans_summary)
        self.assertIn(f"- Last aggregation: {date.today()}", skills_summary)
        self.assertIn('"file": "knowledge/topic.md"', knowledge_archive)
        self.assertEqual(knowledge_access, "")
        self.assertEqual(log_count, "2")

    # ------------------------------------------------------------------
    # P0-1: memory_write / memory_edit protected-path enforcement
    # ------------------------------------------------------------------

    def test_memory_write_blocks_protected_identity_path(self) -> None:
        repo_root = self._init_repo({"identity/profile.md": "# Profile\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_write"](path="identity/profile.md", content="injected\n"))
        self.assertEqual(
            (repo_root / "identity" / "profile.md").read_text(encoding="utf-8"),
            "# Profile\n",
        )

    def test_memory_write_blocks_protected_skills_path(self) -> None:
        repo_root = self._init_repo({"skills/session-start.md": "# Skill\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_write"](path="skills/session-start.md", content="injected\n"))

    def test_memory_write_blocks_protected_meta_path(self) -> None:
        repo_root = self._init_repo({"meta/curation-policy.md": "# Policy\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(tools["memory_write"](path="meta/curation-policy.md", content="injected\n"))

    def test_memory_edit_blocks_protected_identity_path(self) -> None:
        repo_root = self._init_repo({"identity/profile.md": "# Profile\noriginal\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        with self.assertRaises(self.errors.MemoryPermissionError):
            asyncio.run(
                tools["memory_edit"](
                    path="identity/profile.md",
                    old_string="original",
                    new_string="injected",
                )
            )
        self.assertIn(
            "original", (repo_root / "identity" / "profile.md").read_text(encoding="utf-8")
        )

    def test_memory_commit_does_not_include_unrelated_pre_staged_changes(self) -> None:
        repo_root = self._init_repo(
            {
                "README.md": "# Project\n",
                "knowledge/README.md": "# Knowledge\n",
            }
        )
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        (repo_root / "README.md").write_text("# Unrelated staged change\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

        asyncio.run(
            tools["memory_write"](
                path="knowledge/_unverified/test.md",
                content="# Note\n",
            )
        )
        payload = json.loads(
            asyncio.run(tools["memory_commit"](message="[knowledge] Add test note"))
        )

        head_files = subprocess.run(
            ["git", "show", "--name-only", "--format=%s", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        still_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        self.assertIn("knowledge/_unverified/test.md", head_files)
        self.assertNotIn("README.md", head_files)
        self.assertIn("README.md", still_staged)
        self.assertEqual(payload["publication"]["mode"], "porcelain")
        self.assertFalse(payload["publication"]["degraded"])
        self.assertEqual(payload["publication"]["operation"], "commit")
        self.assertRegex(payload["publication"]["published_at"], r"\+00:00$")
        self.assertRegex(payload["publication"]["parent_sha"], r"^[0-9a-f]{40}$")
        self.assertEqual(payload["warnings"], [])

    def test_memory_commit_rejects_unstaged_changes_on_tracked_paths(self) -> None:
        repo_root = self._init_repo({"knowledge/README.md": "# Knowledge\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        asyncio.run(
            tools["memory_write"](
                path="knowledge/_unverified/test.md",
                content="# Staged version\n",
            )
        )
        (repo_root / "knowledge" / "_unverified" / "test.md").write_text(
            "# Unstaged version\n",
            encoding="utf-8",
        )

        with self.assertRaises(self.errors.StagingError):
            asyncio.run(tools["memory_commit"](message="[knowledge] Add test note"))

        head_subject = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(head_subject, "seed")

    def test_memory_commit_falls_back_to_plumbing_for_tracked_paths(self) -> None:
        repo_root = self._init_repo(
            {
                "README.md": "# Project\n",
                "knowledge/README.md": "# Knowledge\n",
            }
        )
        _, tools, _, repo = self.server.create_mcp(
            repo_root=repo_root,
            enable_raw_write_tools=True,
        )

        (repo_root / "README.md").write_text("# Unrelated staged change\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "README.md"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )

        asyncio.run(
            tools["memory_write"](
                path="knowledge/_unverified/test.md",
                content="# Note\n",
            )
        )

        original_run = repo._run
        commit_attempts = {"count": 0}

        def fail_porcelain_commit(
            args: list[str],
            check: bool = True,
            capture: bool = True,
            *,
            cwd: Path | None = None,
            env: dict[str, str] | None = None,
        ):
            if args[:2] == ["git", "commit"]:
                commit_attempts["count"] += 1
                raise self.errors.StagingError(
                    "`git commit -m` failed (exit 128): fatal: Unable to create '.git/index.lock': File exists.",
                    stderr="fatal: Unable to create '.git/index.lock': File exists.",
                )
            return original_run(args, check=check, capture=capture, cwd=cwd, env=env)

        repo._run = fail_porcelain_commit
        self.addCleanup(setattr, repo, "_run", original_run)

        payload = json.loads(
            asyncio.run(tools["memory_commit"](message="[knowledge] Add test note"))
        )

        head_files = subprocess.run(
            ["git", "show", "--name-only", "--format=%s", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        still_staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout

        self.assertEqual(commit_attempts["count"], 1)
        self.assertIn("knowledge/_unverified/test.md", head_files)
        self.assertNotIn("README.md", head_files)
        self.assertIn("README.md", still_staged)
        self.assertEqual(payload["publication"]["mode"], "plumbing")
        self.assertTrue(payload["publication"]["degraded"])
        self.assertEqual(payload["publication"]["operation"], "commit")
        self.assertRegex(payload["publication"]["published_at"], r"\+00:00$")
        self.assertRegex(payload["publication"]["parent_sha"], r"^[0-9a-f]{40}$")
        self.assertIn("degraded plumbing path", payload["warnings"][0])

    def test_memory_commit_blocks_when_single_writer_lock_is_held(self) -> None:
        repo_root = self._init_repo({"knowledge/README.md": "# Knowledge\n"})
        _, tools, _, repo = self.server.create_mcp(
            repo_root=repo_root,
            enable_raw_write_tools=True,
        )

        asyncio.run(
            tools["memory_write"](
                path="knowledge/_unverified/test.md",
                content="# Note\n",
            )
        )

        lock_path = repo.git_dir / getattr(self.git_repo_module, "_WRITE_LOCK_NAME")
        lock_path.write_text("pid=999\npurpose=test\n", encoding="utf-8")
        original_timeout = getattr(self.git_repo_module, "_WRITE_LOCK_TIMEOUT_SECONDS")
        setattr(self.git_repo_module, "_WRITE_LOCK_TIMEOUT_SECONDS", 0.0)
        self.addCleanup(
            setattr, self.git_repo_module, "_WRITE_LOCK_TIMEOUT_SECONDS", original_timeout
        )
        self.addCleanup(lock_path.unlink)

        with self.assertRaises(self.errors.StagingError) as ctx:
            asyncio.run(tools["memory_commit"](message="[knowledge] Add test note"))

        self.assertIn("Another writer is already publishing changes", str(ctx.exception))

    def test_memory_update_plan_next_action_uses_human_title_in_summary(self) -> None:
        repo_root = self._init_repo(
            {
                "plans/test-plan.md": """---
source: agent-generated
type: implementation-plan
title: Test Plan
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
Detail: plans/test-plan.md
Progress: 0/1 complete
Next: Original next action
<!-- END: test-plan -->
""",
            }
        )
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_update_plan_next_action"](
                plan_id="test-plan",
                next_action="Fresh next action",
            )
        )

        summary = (repo_root / "plans" / "SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("### Test Plan · status: active · trust: medium", summary)
        self.assertIn("Next: Fresh next action", summary)

    def test_memory_write_allows_knowledge_path(self) -> None:
        """Sanity check: knowledge/ writes still work after the policy change."""
        repo_root = self._init_repo({"knowledge/README.md": "# Knowledge\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        asyncio.run(
            tools["memory_write"](path="knowledge/_unverified/test/note.md", content="# Note\n")
        )
        self.assertTrue((repo_root / "knowledge" / "_unverified" / "test" / "note.md").exists())

    # ------------------------------------------------------------------
    # P1: File size limits
    # ------------------------------------------------------------------

    def test_memory_write_rejects_oversized_content(self) -> None:
        repo_root = self._init_repo({"knowledge/README.md": "# Knowledge\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        import os

        # Set a very small limit so we don't actually need a large payload
        original = os.environ.get("MEMORY_MAX_FILE_BYTES")
        try:
            os.environ["MEMORY_MAX_FILE_BYTES"] = "10"
            with self.assertRaises(self.errors.ValidationError) as ctx:
                asyncio.run(
                    tools["memory_write"](
                        path="knowledge/_unverified/test.md",
                        content="This content is much longer than ten bytes.",
                    )
                )
            self.assertIn("bytes", str(ctx.exception))
        finally:
            if original is None:
                os.environ.pop("MEMORY_MAX_FILE_BYTES", None)
            else:
                os.environ["MEMORY_MAX_FILE_BYTES"] = original

    def test_memory_add_knowledge_file_rejects_oversized_content(self) -> None:
        repo_root = self._init_repo(
            {"knowledge/_unverified/SUMMARY.md": "# Unverified\n\n<!-- section: test -->\n"}
        )
        tools = self._create_tools(repo_root)

        import os

        original = os.environ.get("MEMORY_MAX_FILE_BYTES")
        try:
            os.environ["MEMORY_MAX_FILE_BYTES"] = "10"
            with self.assertRaises(self.errors.ValidationError) as ctx:
                asyncio.run(
                    tools["memory_add_knowledge_file"](
                        path="knowledge/_unverified/test/note.md",
                        content="This content is much longer than ten bytes.",
                        source="external-research",
                        session_id="chats/2026/03/19/chat-001",
                    )
                )
            self.assertIn("bytes", str(ctx.exception))
        finally:
            if original is None:
                os.environ.pop("MEMORY_MAX_FILE_BYTES", None)
            else:
                os.environ["MEMORY_MAX_FILE_BYTES"] = original

    # ------------------------------------------------------------------
    # P1: memory_log_access
    # ------------------------------------------------------------------

    def test_memory_log_access_appends_valid_entry(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/literature/galatea.md": "# Galatea\n",
                "knowledge/ACCESS.jsonl": "",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_log_access"](
                file="knowledge/literature/galatea.md",
                task="User asked about AI literature references",
                helpfulness=0.8,
                note="Core reference, shaped the response framing",
                session_id="chats/2026/03/19/chat-001",
            )
        )
        payload = json.loads(raw)
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/ACCESS.jsonl")

        lines = [
            line
            for line in (repo_root / "knowledge" / "ACCESS.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertEqual(entry["file"], "knowledge/literature/galatea.md")
        self.assertEqual(entry["helpfulness"], 0.8)
        self.assertEqual(entry["session_id"], "chats/2026/03/19/chat-001")
        self.assertIn("task", entry)
        self.assertIn("note", entry)
        self.assertIn("date", entry)

    def test_memory_log_access_uses_unverified_access_jsonl(self) -> None:
        repo_root = self._init_repo({"knowledge/_unverified/django/foo.md": "# Foo\n"})
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_log_access"](
                file="knowledge/_unverified/django/foo.md",
                task="Django query test",
                helpfulness=0.3,
                note="Near-miss — adjacent topic",
            )
        )
        payload = json.loads(raw)
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/_unverified/ACCESS.jsonl")
        self.assertTrue((repo_root / "knowledge" / "_unverified" / "ACCESS.jsonl").exists())

    def test_memory_log_access_rejects_invalid_helpfulness(self) -> None:
        repo_root = self._init_repo({"knowledge/lit/foo.md": "# Foo\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_log_access"](
                    file="knowledge/lit/foo.md",
                    task="test",
                    helpfulness=1.5,
                    note="out of range",
                )
            )

    def test_memory_log_access_rejects_noncanonical_session_id(self) -> None:
        repo_root = self._init_repo({"knowledge/lit/foo.md": "# Foo\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_log_access"](
                    file="knowledge/lit/foo.md",
                    task="test",
                    helpfulness=0.5,
                    note="bad session id",
                    session_id="chat-001",
                )
            )

    def test_memory_log_access_rejects_category_without_vocabulary(self) -> None:
        repo_root = self._init_repo({"knowledge/lit/foo.md": "# Foo\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_log_access"](
                    file="knowledge/lit/foo.md",
                    task="test",
                    helpfulness=0.5,
                    note="category should be blocked",
                    category="react-performance",
                )
            )

    def test_memory_log_access_accepts_category_from_controlled_vocabulary(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/lit/foo.md": "# Foo\n",
                "meta/task-categories.md": "# Task Categories\n\n- `react-performance`\n- `uncategorized`\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_log_access"](
                file="knowledge/lit/foo.md",
                task="test",
                helpfulness=0.5,
                note="category should be accepted",
                category="react-performance",
            )
        )
        payload = json.loads(raw)

        entry = json.loads(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/ACCESS.jsonl")
        self.assertEqual(entry["category"], "react-performance")

    def test_memory_log_access_persists_mode_field(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/lit/foo.md": "# Foo\n",
                "knowledge/ACCESS.jsonl": "",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_log_access"](
                file="knowledge/lit/foo.md",
                task="test",
                helpfulness=0.7,
                note="mode should be persisted",
                mode="write",
            )
        )

        payload = json.loads(raw)
        entry = json.loads(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/ACCESS.jsonl")
        self.assertEqual(entry["mode"], "write")

    def test_memory_log_access_uses_environment_session_id_when_missing(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/lit/foo.md": "# Foo\n",
                "knowledge/ACCESS.jsonl": "",
            }
        )
        tools = self._create_tools(repo_root)
        original = os.environ.get("MEMORY_SESSION_ID")

        try:
            os.environ["MEMORY_SESSION_ID"] = "chats/2026/03/20/chat-007"
            raw = asyncio.run(
                tools["memory_log_access"](
                    file="knowledge/lit/foo.md",
                    task="test",
                    helpfulness=0.6,
                    note="session id should come from env",
                )
            )
        finally:
            if original is None:
                os.environ.pop("MEMORY_SESSION_ID", None)
            else:
                os.environ["MEMORY_SESSION_ID"] = original

        payload = json.loads(raw)
        entry = json.loads(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/ACCESS.jsonl")
        self.assertEqual(entry["session_id"], "chats/2026/03/20/chat-007")

    def test_memory_log_access_uses_current_session_sentinel_when_missing(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/lit/foo.md": "# Foo\n",
                "knowledge/ACCESS.jsonl": "",
                "chats/CURRENT_SESSION": "chats/2026/03/20/chat-008\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_log_access"](
                file="knowledge/lit/foo.md",
                task="test",
                helpfulness=0.6,
                note="session id should come from sentinel",
            )
        )

        payload = json.loads(raw)
        entry = json.loads(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )
        self.assertEqual(payload["new_state"]["access_jsonl"], "knowledge/ACCESS.jsonl")
        self.assertEqual(entry["session_id"], "chats/2026/03/20/chat-008")

    def test_memory_log_access_batch_writes_multiple_entries_in_single_commit(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/lit/foo.md": "# Foo\n",
                "plans/demo.md": "# Demo\n",
                "chats/CURRENT_SESSION": "chats/2026/03/20/chat-009\n",
            }
        )
        tools = self._create_tools(repo_root)
        before_count = int(
            subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )

        raw = asyncio.run(
            tools["memory_log_access_batch"](
                access_entries=[
                    {
                        "file": "knowledge/lit/foo.md",
                        "task": "batch test",
                        "helpfulness": 0.8,
                        "note": "knowledge entry",
                    },
                    {
                        "file": "plans/demo.md",
                        "task": "batch test",
                        "helpfulness": 0.4,
                        "note": "plan entry",
                    },
                ]
            )
        )

        after_count = int(
            subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        payload = json.loads(raw)

        knowledge_entry = json.loads(
            (repo_root / "knowledge" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )
        plan_entry = json.loads(
            (repo_root / "plans" / "ACCESS.jsonl").read_text(encoding="utf-8").strip()
        )

        self.assertEqual(after_count - before_count, 1)
        self.assertEqual(payload["new_state"]["entry_count"], 2)
        self.assertEqual(
            sorted(payload["new_state"]["access_jsonls"]),
            ["knowledge/ACCESS.jsonl", "plans/ACCESS.jsonl"],
        )
        self.assertEqual(knowledge_entry["session_id"], "chats/2026/03/20/chat-009")
        self.assertEqual(plan_entry["session_id"], "chats/2026/03/20/chat-009")

    def test_memory_log_access_batch_rejects_empty_entry_list(self) -> None:
        repo_root = self._init_repo({"knowledge/lit/foo.md": "# Foo\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(tools["memory_log_access_batch"](access_entries=[]))

    def test_memory_get_maturity_signals_reports_write_sessions(self) -> None:
        repo_root = self._init_repo(
            {
                "identity/profile.md": "# Profile\n",
                "knowledge/lit/foo.md": "# Foo\n",
                "plans/demo.md": "# Demo\n",
                "knowledge/ACCESS.jsonl": "\n".join(
                    [
                        json.dumps(
                            {
                                "file": "knowledge/lit/foo.md",
                                "date": "2026-03-20",
                                "task": "read test",
                                "helpfulness": 0.8,
                                "note": "baseline read",
                                "session_id": "chats/2026/03/20/chat-010",
                                "mode": "read",
                            }
                        ),
                        json.dumps(
                            {
                                "file": "knowledge/lit/foo.md",
                                "date": "2026-03-20",
                                "task": "write test",
                                "helpfulness": 0.9,
                                "note": "knowledge write",
                                "session_id": "chats/2026/03/20/chat-011",
                                "mode": "write",
                            }
                        ),
                    ]
                )
                + "\n",
                "plans/ACCESS.jsonl": json.dumps(
                    {
                        "file": "plans/demo.md",
                        "date": "2026-03-20",
                        "task": "plan update",
                        "helpfulness": 0.6,
                        "note": "plan updated",
                        "session_id": "chats/2026/03/20/chat-012",
                        "mode": "update",
                    }
                )
                + "\n",
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_get_maturity_signals"]()))

        self.assertEqual(payload["total_sessions"], 3)
        self.assertEqual(payload["write_sessions"], 2)
        self.assertEqual(payload["access_density"], 3)

    def test_memory_revert_commit_preview_returns_confirmation_metadata(self) -> None:
        repo_root = self._init_repo({"plans/demo.md": "# Demo\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nUpdated\n"},
            "[plan] Update demo plan",
        )
        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        tools = self._create_tools(repo_root)

        raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        payload = json.loads(raw)
        new_state = payload["new_state"]

        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertIsNone(payload["commit_sha"])
        self.assertEqual(new_state["mode"], "preview")
        self.assertTrue(new_state["eligible"])
        self.assertEqual(new_state["resolved_sha"], target_sha)
        self.assertEqual(new_state["preview_token"], head_before)
        self.assertTrue(new_state["applies_cleanly"])
        self.assertEqual(new_state["conflict_details"], "")
        self.assertIn("plans/demo.md", new_state["files_changed"])
        self.assertEqual(head_after, head_before)

    def test_memory_revert_commit_confirm_requires_preview_token(self) -> None:
        repo_root = self._init_repo({"plans/demo.md": "# Demo\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nUpdated\n"},
            "[plan] Update demo plan",
        )
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(tools["memory_revert_commit"](sha=target_sha, confirm=True))

    def test_memory_revert_commit_confirm_reverts_previewed_commit(self) -> None:
        repo_root = self._init_repo({"plans/demo.md": "# Demo\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nUpdated\n"},
            "[plan] Update demo plan",
        )
        tools = self._create_tools(repo_root)

        preview_raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        preview = json.loads(preview_raw)
        confirm_raw = asyncio.run(
            tools["memory_revert_commit"](
                sha=target_sha,
                confirm=True,
                preview_token=preview["new_state"]["preview_token"],
            )
        )
        payload = json.loads(confirm_raw)

        restored = (repo_root / "plans" / "demo.md").read_text(encoding="utf-8")
        log_subject = subprocess.run(
            ["git", "log", "-1", "--pretty=%s"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        self.assertEqual(payload["new_state"]["mode"], "confirm")
        self.assertEqual(payload["new_state"]["reverted_sha"], target_sha)
        self.assertIn("Original", restored)
        self.assertNotIn("Updated", restored)
        self.assertTrue(log_subject.startswith("Revert"))
        self.assertEqual(payload["publication"]["mode"], "porcelain")
        self.assertFalse(payload["publication"]["degraded"])
        self.assertEqual(payload["publication"]["operation"], "revert")
        self.assertRegex(payload["publication"]["published_at"], r"\+00:00$")
        self.assertRegex(payload["publication"]["parent_sha"], r"^[0-9a-f]{40}$")

    def test_memory_revert_commit_blocks_non_memory_paths_on_confirm(self) -> None:
        repo_root = self._init_repo({"tools/example.py": "print('before')\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"tools/example.py": "print('after')\n"},
            "[system] Update helper",
        )
        tools = self._create_tools(repo_root)

        preview_raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        preview = json.loads(preview_raw)

        self.assertFalse(preview["new_state"]["eligible"])
        self.assertIn("outside the governed memory surface", preview["warnings"][0])

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_revert_commit"](
                    sha=target_sha,
                    confirm=True,
                    preview_token=preview["new_state"]["preview_token"],
                )
            )

    def test_memory_revert_commit_blocks_system_commit_outside_governance_scope(self) -> None:
        repo_root = self._init_repo({"plans/demo.md": "# Demo\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nUpdated\n"},
            "[system] Update demo plan",
        )
        tools = self._create_tools(repo_root)

        preview_raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        preview = json.loads(preview_raw)

        self.assertFalse(preview["new_state"]["eligible"])
        self.assertIn("[system] commits may only touch governance files", preview["warnings"][0])

    def test_memory_revert_commit_preview_reports_conflict(self) -> None:
        repo_root = self._init_repo({"plans/demo.md": "# Demo\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nFirst update\n"},
            "[plan] Update demo plan",
        )
        self._write_and_commit(
            repo_root,
            {"plans/demo.md": "# Demo\n\nSecond update\n"},
            "[plan] Update demo plan again",
        )
        tools = self._create_tools(repo_root)

        preview_raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        preview = json.loads(preview_raw)
        new_state = preview["new_state"]

        self.assertFalse(new_state["applies_cleanly"])
        self.assertFalse(new_state["eligible"])
        self.assertTrue(new_state["conflict_details"])
        self.assertIn("does not apply cleanly", preview["warnings"][0])

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_revert_commit"](
                    sha=target_sha,
                    confirm=True,
                    preview_token=new_state["preview_token"],
                )
            )

    def test_memory_revert_commit_allows_governance_scoped_system_commit(self) -> None:
        repo_root = self._init_repo({"README.md": "# Project\n\nOriginal\n"})
        target_sha = self._write_and_commit(
            repo_root,
            {"README.md": "# Project\n\nUpdated\n"},
            "[system] Update readme guidance",
        )
        tools = self._create_tools(repo_root)

        preview_raw = asyncio.run(tools["memory_revert_commit"](sha=target_sha))
        preview = json.loads(preview_raw)
        preview_state = preview["new_state"]

        self.assertTrue(preview_state["eligible"])
        self.assertTrue(preview_state["applies_cleanly"])
        self.assertIn("README.md", preview_state["files_changed"])

        confirm_raw = asyncio.run(
            tools["memory_revert_commit"](
                sha=target_sha,
                confirm=True,
                preview_token=preview_state["preview_token"],
            )
        )
        payload = json.loads(confirm_raw)

        restored = (repo_root / "README.md").read_text(encoding="utf-8")
        self.assertEqual(payload["new_state"]["mode"], "confirm")
        self.assertEqual(payload["new_state"]["reverted_sha"], target_sha)
        self.assertIn("Original", restored)
        self.assertNotIn("Updated", restored)

    def test_memory_log_access_rejects_untracked_root(self) -> None:
        repo_root = self._init_repo({"scratchpad/CURRENT.md": "# Scratch\n"})
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(
                tools["memory_log_access"](
                    file="scratchpad/CURRENT.md",
                    task="test",
                    helpfulness=0.5,
                    note="scratchpad is not access-tracked",
                )
            )

    # ------------------------------------------------------------------
    # P0-2: memory_audit_trust frontmatterless files
    # ------------------------------------------------------------------

    def test_memory_audit_trust_flags_overdue_frontmatterless_file(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/legacy.md": "# Legacy\n",
            },
            initial_commit_date="2025-01-01T00:00:00+00:00",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_audit_trust"](include_categories="knowledge"))
        )

        self.assertEqual(payload["files_checked"], 1)
        self.assertEqual(len(payload["overdue_medium"]), 1)
        self.assertEqual(payload["overdue_medium"][0]["path"], "knowledge/legacy.md")
        self.assertTrue(payload["overdue_medium"][0]["implicit_trust"])

    def test_memory_audit_trust_skips_recent_frontmatterless_file_from_overdue(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/recent.md": "# Recent\n",
            },
            initial_commit_date="2026-02-20T00:00:00+00:00",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_audit_trust"](include_categories="knowledge"))
        )

        self.assertEqual(payload["files_checked"], 1)
        self.assertEqual(payload["overdue_medium"], [])
        self.assertEqual(payload["upcoming_medium"], [])
        self.assertEqual(payload["unevaluable"], [])

    def test_memory_audit_trust_reports_untracked_frontmatterless_file_as_unevaluable(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/tracked.md": "# Tracked\n",
            },
            initial_commit_date="2026-02-20T00:00:00+00:00",
        )
        (repo_root / "knowledge" / "draft.md").write_text("# Draft\n", encoding="utf-8")
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_audit_trust"](include_categories="knowledge"))
        )

        self.assertEqual(payload["files_checked"], 2)
        self.assertEqual(len(payload["unevaluable"]), 1)
        self.assertEqual(payload["unevaluable"][0]["path"], "knowledge/draft.md")
        self.assertEqual(
            payload["unevaluable"][0]["reason"],
            "untracked_without_frontmatter",
        )

    def test_memory_git_log_can_read_configured_host_repo(self) -> None:
        host_root = self._init_host_repo({"src/app.py": "print('host')\n"})
        self._write_and_commit(host_root, {"src/app.py": "print('host v2')\n"}, "host update")
        repo_root = self._init_repo(
            {
                "agent-bootstrap.toml": (
                    "version = 1\n"
                    'router = "meta/quick-reference.md"\n'
                    'default_mode = "returning"\n'
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n'
                    f'host_repo_root = "{host_root.as_posix()}"\n'
                ),
                "meta/quick-reference.md": "# Quick Reference\n",
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_git_log"](n=1, use_host_repo=True)))

        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["message"], "host update")
        self.assertIn("src/app.py", payload[0]["files_changed"])

    def test_memory_git_log_rejects_host_repo_inside_memory_worktree(self) -> None:
        repo_root = self._init_repo(
            {
                "agent-bootstrap.toml": (
                    "version = 1\n"
                    'router = "meta/quick-reference.md"\n'
                    'default_mode = "returning"\n'
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n'
                    'host_repo_root = "./nested-host"\n'
                ),
                "meta/quick-reference.md": "# Quick Reference\n",
            }
        )
        nested_host = repo_root / "nested-host"
        nested_host.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=nested_host, check=True, capture_output=True, text=True)
        tools = self._create_tools(repo_root)

        with self.assertRaises(self.errors.ValidationError):
            asyncio.run(tools["memory_git_log"](use_host_repo=True))

    def test_memory_check_knowledge_freshness_reports_stale_host_backed_note(self) -> None:
        host_root = self._init_host_repo(
            {"src/app.py": "print('host')\n"},
            initial_commit_date="2026-02-20T00:00:00+00:00",
        )
        initial_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=host_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        updated_head = self._write_and_commit(
            host_root,
            {"src/app.py": "print('host v2')\n"},
            "host update",
            commit_date="2026-03-10T00:00:00+00:00",
        )
        repo_root = self._init_repo(
            {
                "agent-bootstrap.toml": (
                    "version = 1\n"
                    'router = "meta/quick-reference.md"\n'
                    'default_mode = "returning"\n'
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n'
                    f'host_repo_root = "{host_root.as_posix()}"\n'
                ),
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/app.md": (
                    "---\n"
                    "trust: medium\n"
                    "last_verified: 2026-03-01\n"
                    f"verified_against_commit: {initial_head}\n"
                    "related:\n"
                    "  - src/app.py\n"
                    "---\n\n"
                    "# App\n"
                ),
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_check_knowledge_freshness"](paths="knowledge/app.md"))
        )

        self.assertEqual(payload["files_checked"], 1)
        report = payload["reports"][0]
        self.assertEqual(report["path"], "knowledge/app.md")
        self.assertEqual(report["status"], "stale")
        self.assertEqual(report["source_files"], ["src/app.py"])
        self.assertEqual(report["host_changes_since"], 1)
        self.assertEqual(report["current_head"], updated_head)
        self.assertEqual(report["suggested_action"], "reverify")

    def test_memory_check_knowledge_freshness_returns_unknown_without_host_repo(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": "# Quick Reference\n",
                "knowledge/app.md": (
                    "---\n"
                    "trust: medium\n"
                    "last_verified: 2026-03-01\n"
                    "related:\n"
                    "  - src/app.py\n"
                    "---\n\n"
                    "# App\n"
                ),
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_check_knowledge_freshness"](paths="knowledge/app.md"))
        )

        self.assertEqual(payload["files_checked"], 1)
        report = payload["reports"][0]
        self.assertEqual(report["status"], "unknown")
        self.assertEqual(report["source_files"], [])
        self.assertIsNone(report["current_head"])
        self.assertEqual(report["suggested_action"], "none")

    def test_memory_audit_trust_flags_recent_medium_note_when_host_sources_changed(self) -> None:
        host_root = self._init_host_repo(
            {"src/app.py": "print('host')\n"},
            initial_commit_date="2026-02-20T00:00:00+00:00",
        )
        initial_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=host_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self._write_and_commit(
            host_root,
            {"src/app.py": "print('host v2')\n"},
            "host update",
            commit_date="2026-03-10T00:00:00+00:00",
        )
        repo_root = self._init_repo(
            {
                "agent-bootstrap.toml": (
                    "version = 1\n"
                    'router = "meta/quick-reference.md"\n'
                    'default_mode = "returning"\n'
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n'
                    f'host_repo_root = "{host_root.as_posix()}"\n'
                ),
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/app.md": (
                    "---\n"
                    "trust: medium\n"
                    "last_verified: 2026-03-01\n"
                    f"verified_against_commit: {initial_head}\n"
                    "related:\n"
                    "  - src/app.py\n"
                    "---\n\n"
                    "# App\n"
                ),
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_audit_trust"](include_categories="knowledge"))
        )

        self.assertEqual(payload["overdue_medium"], [])
        self.assertEqual(len(payload["upcoming_medium"]), 1)
        entry = payload["upcoming_medium"][0]
        self.assertEqual(entry["path"], "knowledge/app.md")
        self.assertEqual(entry["freshness_status"], "stale")
        self.assertEqual(entry["host_changes_since"], 1)
        self.assertEqual(entry["action_required"], "reverify")

    def test_memory_audit_trust_downgrades_stale_age_when_host_sources_are_unchanged(self) -> None:
        host_root = self._init_host_repo(
            {"src/app.py": "print('host')\n"},
            initial_commit_date="2024-12-20T00:00:00+00:00",
        )
        current_head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=host_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        repo_root = self._init_repo(
            {
                "agent-bootstrap.toml": (
                    "version = 1\n"
                    'router = "meta/quick-reference.md"\n'
                    'default_mode = "returning"\n'
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n'
                    f'host_repo_root = "{host_root.as_posix()}"\n'
                ),
                "meta/quick-reference.md": (
                    "Low-trust retirement threshold | 120-day\n"
                    "Medium-trust flagging threshold | 180-day\n"
                ),
                "knowledge/legacy.md": (
                    "---\n"
                    "trust: medium\n"
                    "last_verified: 2025-01-01\n"
                    f"verified_against_commit: {current_head}\n"
                    "related:\n"
                    "  - src/app.py\n"
                    "---\n\n"
                    "# Legacy\n"
                ),
            },
            initial_commit_date="2025-01-01T00:00:00+00:00",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_audit_trust"](include_categories="knowledge"))
        )

        self.assertEqual(payload["overdue_medium"], [])
        self.assertEqual(len(payload["upcoming_medium"]), 1)
        entry = payload["upcoming_medium"][0]
        self.assertEqual(entry["path"], "knowledge/legacy.md")
        self.assertEqual(entry["freshness_status"], "fresh")
        self.assertEqual(entry["host_changes_since"], 0)
        self.assertEqual(entry["action_required"], "review")

    def test_memory_check_aggregation_triggers_reports_above_and_near_thresholds(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": "| Aggregation trigger | 15 entries | Exploration |\n",
                "plans/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": f"plans/item-{idx}.md",
                            "date": "2026-03-19",
                            "task": "periodic review",
                            "helpfulness": 0.7,
                            "note": "useful",
                            "session_id": f"chats/2026/03/19/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(15)
                ),
                "knowledge/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": f"knowledge/topic-{idx}.md",
                            "date": "2026-03-19",
                            "task": "research",
                            "helpfulness": 0.5,
                            "note": "context",
                        }
                    )
                    + "\n"
                    for idx in range(12)
                ),
                "identity/ACCESS.jsonl": json.dumps(
                    {
                        "file": "identity/profile.md",
                        "date": "2026-03-19",
                        "task": "profile lookup",
                        "helpfulness": 0.9,
                        "note": "critical",
                    }
                )
                + "\n",
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_check_aggregation_triggers"]()))

        self.assertEqual(payload["aggregation_trigger"], 15)
        self.assertEqual(payload["near_trigger_window"], 3)
        self.assertEqual(payload["above_trigger"], ["plans/ACCESS.jsonl"])
        self.assertEqual(payload["near_trigger"], ["knowledge/ACCESS.jsonl"])

        reports = {item["access_file"]: item for item in payload["reports"]}
        self.assertEqual(reports["plans/ACCESS.jsonl"]["status"], "above")
        self.assertEqual(reports["plans/ACCESS.jsonl"]["remaining_to_trigger"], 0)
        self.assertEqual(reports["knowledge/ACCESS.jsonl"]["status"], "near")
        self.assertEqual(reports["knowledge/ACCESS.jsonl"]["remaining_to_trigger"], 3)
        self.assertEqual(reports["identity/ACCESS.jsonl"]["status"], "below")

    def test_memory_check_aggregation_triggers_ignores_invalid_jsonl_lines(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": "| Aggregation trigger | 15 entries | Exploration |\n",
                "plans/ACCESS.jsonl": (
                    "not-json\n"
                    + json.dumps(
                        {
                            "file": "plans/demo.md",
                            "date": "2026-03-19",
                            "task": "planning",
                            "helpfulness": 0.6,
                            "note": "useful",
                        }
                    )
                    + "\n"
                ),
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_check_aggregation_triggers"]()))

        self.assertEqual(payload["files_checked"], 1)
        self.assertEqual(payload["reports"][0]["entries"], 1)
        self.assertEqual(payload["reports"][0]["invalid_lines"], 1)
        self.assertEqual(payload["reports"][0]["status"], "below")

    def test_memory_aggregate_access_reports_high_low_and_clusters(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": "| Aggregation trigger | 15 entries | Exploration |\n",
                "plans/ACCESS.jsonl": "".join(
                    [
                        json.dumps(
                            {
                                "file": "plans/high-value.md",
                                "date": "2026-03-19",
                                "task": "planning",
                                "helpfulness": 0.9,
                                "note": "core plan",
                                "session_id": f"chats/2026/03/19/chat-{idx:03d}",
                            }
                        )
                        + "\n"
                        for idx in range(5)
                    ]
                    + [
                        json.dumps(
                            {
                                "file": "plans/low-value.md",
                                "date": "2026-03-19",
                                "task": "planning",
                                "helpfulness": 0.2,
                                "note": "noise",
                                "session_id": f"chats/2026/03/19/chat-{idx:03d}",
                            }
                        )
                        + "\n"
                        for idx in range(3)
                    ]
                ),
                "knowledge/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "knowledge/topic-a.md",
                            "date": "2026-03-19",
                            "task": "planning",
                            "helpfulness": 0.8,
                            "note": "paired context",
                            "session_id": f"chats/2026/03/19/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(3)
                ),
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_aggregate_access"]()))

        self.assertEqual(payload["entries_considered"], 11)
        self.assertEqual(payload["files_considered"], 3)
        self.assertEqual(payload["high_value_files"][0]["file"], "plans/high-value.md")
        self.assertEqual(payload["low_value_files"][0]["file"], "plans/low-value.md")
        self.assertEqual(
            payload["co_retrieval_clusters"][0]["files"],
            ["knowledge/topic-a.md", "plans/high-value.md"],
        )
        self.assertIn("plans/SUMMARY.md", payload["proposed_outputs"]["summary_update_targets"])
        self.assertIn("knowledge/SUMMARY.md", payload["proposed_outputs"]["summary_update_targets"])
        self.assertEqual(
            payload["proposed_outputs"]["review_queue_candidates"][0]["file"],
            "plans/low-value.md",
        )

    def test_memory_aggregate_access_filters_by_folder_date_and_helpfulness(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": "| Aggregation trigger | 15 entries | Exploration |\n",
                "plans/ACCESS.jsonl": "".join(
                    [
                        json.dumps(
                            {
                                "file": "plans/in-range.md",
                                "date": "2026-03-10",
                                "task": "planning",
                                "helpfulness": 0.75,
                                "note": "keep",
                                "session_id": "chats/2026/03/10/chat-001",
                            }
                        )
                        + "\n",
                        json.dumps(
                            {
                                "file": "plans/too-old.md",
                                "date": "2026-02-01",
                                "task": "planning",
                                "helpfulness": 0.9,
                                "note": "old",
                                "session_id": "chats/2026/02/01/chat-001",
                            }
                        )
                        + "\n",
                    ]
                ),
                "knowledge/ACCESS.jsonl": json.dumps(
                    {
                        "file": "knowledge/out-of-folder.md",
                        "date": "2026-03-10",
                        "task": "research",
                        "helpfulness": 0.8,
                        "note": "other folder",
                    }
                )
                + "\n",
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(
                tools["memory_aggregate_access"](
                    folder="plans",
                    start_date="2026-03-01",
                    end_date="2026-03-31",
                    min_helpfulness=0.7,
                )
            )
        )

        self.assertEqual(payload["entries_considered"], 1)
        self.assertEqual(payload["files_considered"], 1)
        self.assertEqual(payload["file_summaries"][0]["file"], "plans/in-range.md")
        self.assertEqual(payload["filters"]["folder"], "plans")
        self.assertEqual(payload["filters"]["start_date"], "2026-03-01")

    def test_memory_run_periodic_review_recommends_stage_transition(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": """# Quick Reference

## Current active stage: Exploration

## Last periodic review

**Date:** 2026-01-01

| Aggregation trigger | 15 entries | Exploration |
""",
                "identity/profile.md": """---
source: user-stated
origin_session: chats/2026/01/01/chat-001
created: 2026-01-01
last_verified: 2026-01-01
trust: high
---

Alex profile.
""",
                "plans/alpha.md": """---
source: agent-generated
origin_session: chats/2026/03/01/chat-001
created: 2026-03-01
last_verified: 2026-03-01
trust: high
---

Alpha.
""",
                "plans/beta.md": """---
source: agent-generated
origin_session: chats/2026/03/01/chat-002
created: 2026-03-01
last_verified: 2026-03-01
trust: high
---

Beta.
""",
                "knowledge/topic-a.md": """---
source: external-research
origin_session: chats/2026/03/01/chat-003
created: 2026-03-01
last_verified: 2026-03-05
trust: high
---

Topic A.
""",
                "knowledge/topic-b.md": """---
source: external-research
origin_session: chats/2026/03/01/chat-004
created: 2026-03-01
last_verified: 2026-03-05
trust: medium
---

Topic B.
""",
                "knowledge/topic-c.md": """---
source: external-research
origin_session: chats/2026/03/01/chat-005
created: 2026-03-01
last_verified: 2026-03-05
trust: medium
---

Topic C.
""",
                "knowledge/topic-d.md": """---
source: external-research
origin_session: chats/2026/03/01/chat-006
created: 2026-03-01
last_verified: 2026-03-05
trust: medium
---

Topic D.
""",
                "skills/session-start.md": """---
source: skill-discovery
origin_session: chats/2026/03/01/chat-007
created: 2026-03-01
last_verified: 2026-03-05
trust: medium
---

Skill start.
""",
                "skills/session-sync.md": """---
source: skill-discovery
origin_session: chats/2026/03/01/chat-008
created: 2026-03-01
last_verified: 2026-03-05
trust: medium
---

Skill sync.
""",
                "plans/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "plans/alpha.md" if idx % 2 == 0 else "knowledge/topic-a.md",
                            "date": f"2026-03-{(idx % 20) + 1:02d}",
                            "task": "periodic review",
                            "helpfulness": 0.65,
                            "note": "useful",
                            "session_id": f"chats/2026/03/{(idx % 20) + 1:02d}/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(30)
                ),
                "knowledge/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "knowledge/topic-b.md"
                            if idx % 2 == 0
                            else "knowledge/topic-c.md",
                            "date": f"2026-03-{(idx % 20) + 1:02d}",
                            "task": "research",
                            "helpfulness": 0.62,
                            "note": "relevant",
                            "session_id": f"chats/2026/03/{(idx % 20) + 1:02d}/chat-k{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(30)
                ),
            },
            initial_commit_date="2026-01-01T00:00:00",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_run_periodic_review"]()))

        self.assertTrue(payload["review_due"]["due"])
        maturity = payload["ordered_checks"]["maturity_assessment"]
        self.assertEqual(maturity["current_stage"], "Exploration")
        self.assertEqual(maturity["recommended_stage"], "Calibration")
        self.assertTrue(maturity["transition_recommended"])
        self.assertIn(
            "meta/quick-reference.md",
            payload["proposed_outputs"]["deferred_write_targets"],
        )

    def test_memory_run_periodic_review_collects_review_findings(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": """# Quick Reference

## Current active stage: Exploration

## Last periodic review

**Date:** 2026-03-19

| Low-trust retirement threshold | 120 days | Exploration |
| Aggregation trigger | 15 entries | Exploration |
""",
                "meta/review-queue.md": """# Review Queue

### [2026-03-20] Security: Review dormant file spike
**Type:** security
**Trigger:** Sudden access spike on a dormant file.
**File:** knowledge/_unverified/old-note.md
**Recommended action:** Investigate access pattern
**Status:** pending

### [2026-03-20] Aggregate plans access log
**Type:** proposed
**Description:** Aggregate stale plans ACCESS log.
**Status:** pending
""",
                "identity/profile.md": """---
source: user-stated
origin_session: chats/2026/01/01/chat-001
created: 2026-01-01
last_verified: 2026-01-01
trust: high
---

Stable profile.
""",
                "knowledge/current.md": """---
source: external-research
origin_session: chats/2026/03/20/chat-001
created: 2026-03-20
trust: medium
---

Current note.
""",
                "knowledge/conflicted.md": """---
source: agent-inferred
origin_session: chats/2026/03/20/chat-001
created: 2026-03-20
trust: medium
---

[CONFLICT] Preference uncertain.
""",
                "knowledge/_unverified/old-note.md": """---
source: external-research
origin_session: chats/2025/10/01/chat-001
created: 2025-10-01
trust: low
---

Old note.
""",
                "plans/low-value.md": """---
source: agent-generated
origin_session: chats/2026/03/20/chat-010
created: 2026-03-20
trust: medium
---

Low value plan.
""",
                "knowledge/topic-a.md": """---
source: external-research
origin_session: chats/2026/03/20/chat-011
created: 2026-03-20
trust: medium
---

Topic A.
""",
                "plans/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "plans/low-value.md",
                            "date": "2026-03-20",
                            "task": "maintenance",
                            "helpfulness": 0.2,
                            "note": "noise",
                            "session_id": f"chats/2026/03/20/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(3)
                ),
                "knowledge/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "knowledge/topic-a.md",
                            "date": "2026-03-20",
                            "task": "maintenance",
                            "helpfulness": 0.8,
                            "note": "pair",
                            "session_id": f"chats/2026/03/20/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(3)
                ),
                "chats/2026/03/20/chat-001/reflection.md": "## Session reflection\n\nRecurring maintenance theme.\n",
            }
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_run_periodic_review"]()))

        ordered = payload["ordered_checks"]
        self.assertEqual(ordered["security_flags"]["pending_count"], 1)
        self.assertEqual(ordered["review_queue"]["pending_non_security_count"], 1)
        self.assertEqual(ordered["unverified_content"]["overdue_count"], 1)
        self.assertEqual(
            ordered["unverified_content"]["overdue_files"][0]["path"],
            "knowledge/_unverified/old-note.md",
        )
        self.assertEqual(ordered["conflict_resolution"]["files"], ["knowledge/conflicted.md"])
        self.assertEqual(ordered["unhelpful_memory"]["count"], 1)
        self.assertEqual(
            ordered["emergent_categorization"]["clusters"][0]["files"],
            ["knowledge/topic-a.md", "plans/low-value.md"],
        )
        self.assertEqual(ordered["session_reflection_themes"]["reflection_count"], 1)
        self.assertIn("meta/review-queue.md", payload["proposed_outputs"]["deferred_write_targets"])

    def test_memory_get_file_provenance_returns_frontmatter_access_and_history(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/topic.md": """---
source: external-research
origin_session: chats/2026/03/19/chat-001
created: 2026-03-19
trust: low
---

Initial note.
""",
                "knowledge/ACCESS.jsonl": "".join(
                    json.dumps(
                        {
                            "file": "knowledge/topic.md",
                            "date": "2026-03-19",
                            "task": "research",
                            "helpfulness": 0.8,
                            "note": "relevant",
                            "session_id": f"chats/2026/03/19/chat-{idx:03d}",
                        }
                    )
                    + "\n"
                    for idx in range(3)
                ),
            },
            initial_commit_date="2026-03-19T00:00:00",
        )
        self._write_and_commit(
            repo_root,
            {
                "knowledge/topic.md": """---
source: external-research
origin_session: chats/2026/03/19/chat-001
created: 2026-03-19
trust: low
---

Updated note.
"""
            },
            "[knowledge] update topic",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(
            asyncio.run(tools["memory_get_file_provenance"](path="knowledge/topic.md"))
        )

        self.assertEqual(payload["path"], "knowledge/topic.md")
        self.assertEqual(payload["frontmatter"]["source"], "external-research")
        self.assertTrue(payload["requires_provenance_pause"])
        self.assertEqual(payload["access_summary"]["entry_count"], 3)
        self.assertEqual(payload["access_summary"]["session_count"], 3)
        self.assertEqual(payload["latest_commit"]["message"], "[knowledge] update topic")
        self.assertGreaterEqual(len(payload["commit_history"]), 2)
        self.assertIsNotNone(payload["version_token"])

    def test_memory_inspect_commit_returns_scope_and_prefix_metadata(self) -> None:
        repo_root = self._init_repo(
            {
                "knowledge/topic.md": """---
source: external-research
origin_session: chats/2026/03/19/chat-001
created: 2026-03-19
trust: low
---

Initial note.
"""
            },
            initial_commit_date="2026-03-19T00:00:00",
        )
        commit_sha = self._write_and_commit(
            repo_root,
            {"knowledge/topic.md": "updated\n"},
            "[knowledge] rewrite topic",
        )
        tools = self._create_tools(repo_root)

        payload = json.loads(asyncio.run(tools["memory_inspect_commit"](sha=commit_sha[:8])))

        self.assertEqual(payload["requested_sha"], commit_sha[:8])
        self.assertEqual(payload["sha"], commit_sha)
        self.assertEqual(payload["recognized_prefix"], "[knowledge]")
        self.assertEqual(payload["file_count"], 1)
        self.assertEqual(payload["top_level_paths"], ["knowledge"])
        self.assertTrue(payload["is_head"])

    def test_memory_record_periodic_review_updates_meta_outputs(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": """# Quick Reference

## Current active stage: Exploration

_Last assessed: 2026-03-01 — Exploration retained_

## Last periodic review

**Date:** 2026-03-01

| Parameter | Active value | Stage |
|---|---|---|
| Low-trust retirement threshold | 120 days | Exploration |
| Medium-trust flagging threshold | 180 days | Exploration |
| Staleness trigger (no access) | 120 days | Exploration |
| Aggregation trigger | 15 entries | Exploration |
| Identity churn alarm | 5 traits/session | Exploration |
| Knowledge flooding alarm | 5 files/day | Exploration |
| Task similarity method | Session co-occurrence | Exploration |
| Cluster co-retrieval threshold | 3 sessions | Exploration |

## Active task similarity method

**Method:** Session co-occurrence
""",
                "meta/belief-diff-log.md": "# Belief Diff Log\n",
                "meta/review-queue.md": "# Review Queue\n\n_No pending items._\n",
            }
        )
        tools = self._create_tools(repo_root)

        raw = asyncio.run(
            tools["memory_record_periodic_review"](
                review_date="2026-03-19",
                assessment_summary="Exploration retained (signals still within bounds)",
                belief_diff_entry=(
                    "## [2026-03-19] Periodic review\n\n### Assessment\nExploration retained.\n"
                ),
                review_queue_entries=(
                    "### [2026-03-19] Aggregate plans access log\n"
                    "**Type:** proposed\n"
                    "**Description:** Aggregate plans/ACCESS.jsonl.\n"
                    "**Status:** pending\n"
                ),
            )
        )
        payload = json.loads(raw)

        quick_reference = (repo_root / "meta" / "quick-reference.md").read_text(encoding="utf-8")
        belief_diff = (repo_root / "meta" / "belief-diff-log.md").read_text(encoding="utf-8")
        review_queue = (repo_root / "meta" / "review-queue.md").read_text(encoding="utf-8")

        self.assertIn("**Date:** 2026-03-19", quick_reference)
        self.assertIn(
            "_Last assessed: 2026-03-19 — Exploration retained (signals still within bounds)_",
            quick_reference,
        )
        self.assertIn("## [2026-03-19] Periodic review", belief_diff)
        self.assertIn("Aggregate plans access log", review_queue)
        self.assertEqual(payload["commit_message"], "[system] Record periodic review 2026-03-19")
        self.assertEqual(payload["new_state"]["review_date"], "2026-03-19")
        self.assertTrue(payload["new_state"]["belief_diff_written"])
        self.assertTrue(payload["new_state"]["review_queue_written"])

    def test_memory_record_periodic_review_updates_stage_thresholds(self) -> None:
        repo_root = self._init_repo(
            {
                "meta/quick-reference.md": """# Quick Reference

## Current active stage: Exploration

_Last assessed: 2026-03-01 — Exploration retained_

## Last periodic review

**Date:** 2026-03-01

| Parameter | Active value | Stage |
|---|---|---|
| Low-trust retirement threshold | 120 days | Exploration |
| Medium-trust flagging threshold | 180 days | Exploration |
| Staleness trigger (no access) | 120 days | Exploration |
| Aggregation trigger | 15 entries | Exploration |
| Identity churn alarm | 5 traits/session | Exploration |
| Knowledge flooding alarm | 5 files/day | Exploration |
| Task similarity method | Session co-occurrence | Exploration |
| Cluster co-retrieval threshold | 3 sessions | Exploration |

## Active task similarity method

**Method:** Session co-occurrence
""",
                "meta/belief-diff-log.md": "# Belief Diff Log\n",
                "meta/review-queue.md": "# Review Queue\n\n_No pending items._\n",
            }
        )
        tools = self._create_tools(repo_root)

        asyncio.run(
            tools["memory_record_periodic_review"](
                review_date="2026-03-19",
                assessment_summary="Calibration selected after majority signal review",
                belief_diff_entry=(
                    "## [2026-03-19] Periodic review\n\n### Assessment\nCalibration selected.\n"
                ),
                active_stage="Calibration",
            )
        )

        quick_reference = (repo_root / "meta" / "quick-reference.md").read_text(encoding="utf-8")
        self.assertIn("## Current active stage: Calibration", quick_reference)
        self.assertIn(
            "| Aggregation trigger | 20 entries | Calibration |",
            quick_reference,
        )
        self.assertIn(
            "| Knowledge flooding alarm | 3 files/day | Calibration |",
            quick_reference,
        )
        self.assertIn("**Method:** Task-string normalization", quick_reference)

    # ------------------------------------------------------------------
    # P1: Identity churn alarm + memory_reset_session_state
    # ------------------------------------------------------------------

    def test_memory_update_identity_trait_churn_alarm_fires_at_limit(self) -> None:
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

        # Make 5 successful updates (at the limit)
        for i in range(5):
            asyncio.run(
                tools["memory_update_identity_trait"](
                    file="profile",
                    key=f"trait_{i}",
                    value=f"value_{i}",
                )
            )

        # The 6th update should raise the churn alarm
        with self.assertRaises(self.errors.ValidationError) as ctx:
            asyncio.run(
                tools["memory_update_identity_trait"](
                    file="profile",
                    key="trait_6",
                    value="value_6",
                )
            )
        self.assertIn("churn alarm", str(ctx.exception).lower())

    def test_memory_reset_session_state_clears_churn_counter(self) -> None:
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

        # Exhaust the counter
        for i in range(5):
            asyncio.run(
                tools["memory_update_identity_trait"](
                    file="profile",
                    key=f"trait_{i}",
                    value=f"value_{i}",
                )
            )

        # Reset
        reset_payload = json.loads(asyncio.run(tools["memory_reset_session_state"]()))
        self.assertTrue(reset_payload["reset"])
        self.assertEqual(reset_payload["identity_updates_this_session"], 0)

        # Should now succeed
        asyncio.run(
            tools["memory_update_identity_trait"](
                file="profile",
                key="trait_after_reset",
                value="allowed",
            )
        )

    def test_churn_counters_are_independent_per_server_instance(self) -> None:
        """Two separate create_mcp() calls must have independent counters."""
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

        tools_a = self._create_tools(repo_root)
        tools_b = self._create_tools(repo_root)

        # Exhaust counter on instance A
        for i in range(5):
            asyncio.run(
                tools_a["memory_update_identity_trait"](file="profile", key=f"a_{i}", value=f"v{i}")
            )

        # Instance B counter is independent — should not be affected
        asyncio.run(
            tools_b["memory_update_identity_trait"](file="profile", key="b_0", value="independent")
        )

    # ------------------------------------------------------------------
    # P2: Version-token conflict tests for raw write tools
    # ------------------------------------------------------------------

    def test_memory_write_rejects_stale_version_token(self) -> None:
        """Read a file, modify it out-of-band, then attempt a write with the old token."""
        repo_root = self._init_repo({"knowledge/test.md": "# Original\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        # Get the current token
        read_payload = json.loads(asyncio.run(tools["memory_read_file"](path="knowledge/test.md")))
        old_token = read_payload["version_token"]

        # Modify the file directly (bypassing the MCP layer)
        (repo_root / "knowledge" / "test.md").write_text(
            "# Modified out of band\n", encoding="utf-8"
        )

        # memory_write with stale token must raise ConflictError
        with self.assertRaises(self.errors.ConflictError):
            asyncio.run(
                tools["memory_write"](
                    path="knowledge/test.md",
                    content="# New content\n",
                    version_token=old_token,
                )
            )

    def test_memory_edit_rejects_stale_version_token(self) -> None:
        """Read a file, modify it out-of-band, then attempt an edit with the old token."""
        repo_root = self._init_repo({"knowledge/test.md": "# Hello\n\nSome text.\n"})
        tools = self._create_tools(repo_root, enable_raw_write_tools=True)

        read_payload = json.loads(asyncio.run(tools["memory_read_file"](path="knowledge/test.md")))
        old_token = read_payload["version_token"]

        # Modify the file directly
        (repo_root / "knowledge" / "test.md").write_text(
            "# Hello\n\nModified out of band.\n", encoding="utf-8"
        )

        # memory_edit with stale token must raise ConflictError
        with self.assertRaises(self.errors.ConflictError):
            asyncio.run(
                tools["memory_edit"](
                    path="knowledge/test.md",
                    old_string="Some text.",
                    new_string="Replaced text.",
                    version_token=old_token,
                )
            )


if __name__ == "__main__":
    unittest.main()
