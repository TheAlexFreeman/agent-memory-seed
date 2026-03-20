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


REPO_ROOT = Path(__file__).resolve().parents[3]
ToolCallable = Callable[..., Coroutine[Any, Any, str]]


def load_server_module() -> ModuleType:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        return importlib.import_module("tools.agent_memory_mcp.server")
    except ModuleNotFoundError as exc:
        raise unittest.SkipTest(f"agent_memory_mcp dependencies unavailable: {exc.name}") from exc


class AgentMemoryWriteToolTests(unittest.TestCase):
    server: ClassVar[ModuleType]
    errors: ClassVar[ModuleType]
    frontmatter_utils: ClassVar[Any]

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

    def _write_and_commit(
        self,
        repo_root: Path,
        files: dict[str, str],
        message: str,
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
        )
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

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
**Progress:** 0/1 items complete
**Next action:** Original next action
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
            l
            for l in (repo_root / "knowledge" / "ACCESS.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if l.strip()
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
