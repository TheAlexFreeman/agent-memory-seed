"""
Tier 1 — Semantic write+commit tools.

Each tool encapsulates a named, atomic operation on the memory model:
  - Owns all invariants for that operation
  - Auto-commits on success
  - Returns MemoryWriteResult with operation-specific new_state

These are the primary interface for routine memory operations. Internally
they use the GitRepo and frontmatter_utils helpers directly (not the Tier 2
MCP tools, to avoid coupling).
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from ..path_policy import (
    KNOWN_COMMIT_PREFIXES,
    forbid_prefix,
    require_under_prefix,
    resolve_repo_path,
    validate_session_id,
    validate_slug,
    validate_top_level_root,
)
from .semantic._session import (
    SessionState,
    create_session_state,
    get_identity_churn_limit,
    get_identity_updates,
    increment_identity_updates,
    reset_session_state,
)
from .semantic import identity_tools as semantic_identity_tools
from .semantic import knowledge_tools as semantic_knowledge_tools
from .semantic import plan_tools as semantic_plan_tools

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _tool_annotations(**kwargs: object) -> Any:
    """Return MCP tool annotations with a relaxed runtime-only type surface."""
    return cast(Any, kwargs)


# ACCESS log folders — these directories each contain an ACCESS.jsonl file
_ACCESS_ROOTS = ("identity", "knowledge", "skills", "plans", "chats")
_CATEGORY_CODE_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`")
_CATEGORY_LIST_RE = re.compile(r"^(?:[-*]|\d+\.)\s+([a-z0-9]+(?:-[a-z0-9]+)*)\s*$")
_REVERT_ALLOWED_TOP_LEVELS = frozenset(
    {"identity", "knowledge", "skills", "plans", "chats", "meta", "scratchpad"}
)
_REVERT_ALLOWED_FILES = frozenset({"CHANGELOG.md"})
_REVERT_SYSTEM_TOP_LEVELS = frozenset({"meta"})
_REVERT_SYSTEM_FILES = frozenset(
    {"AGENTS.md", "CHANGELOG.md", "CLAUDE.md", "README.md", "agent-bootstrap.toml"}
)
_PERIODIC_REVIEW_STAGE_SETTINGS: dict[str, dict[str, str | int]] = {
    "Exploration": {
        "Low-trust retirement threshold": 120,
        "Medium-trust flagging threshold": 180,
        "Staleness trigger (no access)": 120,
        "Aggregation trigger": 15,
        "Identity churn alarm": 5,
        "Knowledge flooding alarm": 5,
        "Task similarity method": "Session co-occurrence",
        "Cluster co-retrieval threshold": 3,
    },
    "Calibration": {
        "Low-trust retirement threshold": 60,
        "Medium-trust flagging threshold": 120,
        "Staleness trigger (no access)": 90,
        "Aggregation trigger": 20,
        "Identity churn alarm": 3,
        "Knowledge flooding alarm": 3,
        "Task similarity method": "Task-string normalization",
        "Cluster co-retrieval threshold": 3,
    },
    "Consolidation": {
        "Low-trust retirement threshold": 45,
        "Medium-trust flagging threshold": 90,
        "Staleness trigger (no access)": 60,
        "Aggregation trigger": 25,
        "Identity churn alarm": 2,
        "Knowledge flooding alarm": 2,
        "Task similarity method": "Controlled category vocabulary",
        "Cluster co-retrieval threshold": 4,
    },
}


def _plan_path(plan_id: str) -> str:
    return f"plans/{validate_slug(plan_id, field_name='plan_id')}.md"


def _plan_summary_title(fm_dict: dict[str, object], body: str, plan_id: str) -> str:
    """Resolve a human-readable plan title for plans/SUMMARY.md."""
    title = fm_dict.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    heading_match = re.search(r"(?m)^#\s+(.+?)\s*$", body)
    if heading_match is not None:
        return heading_match.group(1).strip()

    return plan_id


def _access_jsonl_for(rel_path: str) -> str | None:
    """Return the repo-relative ACCESS.jsonl path for a content file, or None."""
    from pathlib import PurePosixPath

    parts = PurePosixPath(rel_path).parts
    if not parts:
        return None
    root = parts[0]
    if root not in _ACCESS_ROOTS:
        return None
    # knowledge/_unverified/ has its own ACCESS.jsonl
    if root == "knowledge" and len(parts) > 1 and parts[1] == "_unverified":
        return "knowledge/_unverified/ACCESS.jsonl"
    return f"{root}/ACCESS.jsonl"


def _replace_markdown_section(body: str, section_name: str, new_value: str) -> str | None:
    """Replace a ## section body, returning None when the section is absent."""
    section_heading = f"## {section_name}"
    match = re.search(rf"(?m)^##\s+{re.escape(section_name)}\s*$", body)
    if match is None:
        return None

    content_start = match.end()
    next_heading = re.search(r"(?m)^## ", body[content_start:])
    section_end = content_start + next_heading.start() if next_heading else len(body)
    replacement = f"{section_heading}\n\n{new_value.strip()}\n"
    if next_heading:
        replacement += "\n"
    return body[: match.start()] + replacement + body[section_end:]


def _append_markdown_section(body: str, section_name: str, value: str) -> str | None:
    """Append content to a ## section body, returning None when the section is absent."""
    match = re.search(rf"(?m)^##\s+{re.escape(section_name)}\s*$", body)
    if match is None:
        return None

    content_start = match.end()
    next_heading = re.search(r"(?m)^## ", body[content_start:])
    section_end = content_start + next_heading.start() if next_heading else len(body)
    existing = body[content_start:section_end].strip()
    appended = f"{existing}\n{value.strip()}" if existing else value.strip()
    return _replace_markdown_section(body, section_name, appended)


def _load_task_categories(root: Path) -> set[str]:
    """Load the controlled category vocabulary from meta/task-categories.md."""
    categories_path = root / "meta" / "task-categories.md"
    if not categories_path.exists():
        return set()

    text = categories_path.read_text(encoding="utf-8")
    categories = set(_CATEGORY_CODE_RE.findall(text))
    if categories:
        return categories

    for line in text.splitlines():
        stripped = line.strip()
        match = _CATEGORY_LIST_RE.match(stripped)
        if match:
            categories.add(match.group(1))
    return categories


def _is_revertable_memory_path(rel_path: str) -> bool:
    """Return True when the path is inside the governed memory surface."""
    parts = PurePosixPath(rel_path).parts
    if not parts:
        return False
    if len(parts) == 1 and parts[0] in _REVERT_ALLOWED_FILES:
        return True
    return parts[0] in _REVERT_ALLOWED_TOP_LEVELS


def _is_revertable_system_path(rel_path: str) -> bool:
    """Return True when a [system] commit path stays in governance scope."""
    parts = PurePosixPath(rel_path).parts
    if not parts:
        return False
    if len(parts) == 1 and parts[0] in _REVERT_SYSTEM_FILES:
        return True
    return parts[0] in _REVERT_SYSTEM_TOP_LEVELS


def _build_revert_preview(repo, sha: str) -> dict[str, object]:
    """Inspect a target commit and describe whether it is safe to confirm."""
    from ..errors import ValidationError

    try:
        commit = repo.inspect_commit(sha)
    except Exception as exc:  # pragma: no cover - normalized below
        raise ValidationError(f"Commit not found or not inspectable: {sha}") from exc

    resolved_sha = str(commit["sha"])
    message = str(commit["message"])
    parents = [str(parent) for parent in cast(list[object], commit["parents"])]
    files_changed = [str(path) for path in cast(list[object], commit["files_changed"])]

    prefix_match = re.match(r"^\[[^\]]+\]", message)
    prefix = prefix_match.group(0) if prefix_match else None
    if prefix == "[system]":
        disallowed_files = [
            path
            for path in files_changed
            if not (_is_revertable_memory_path(path) or _is_revertable_system_path(path))
        ]
    else:
        disallowed_files = [path for path in files_changed if not _is_revertable_memory_path(path)]
    disallowed_system_files = (
        [path for path in files_changed if not _is_revertable_system_path(path)]
        if prefix == "[system]"
        else []
    )
    preview_status = repo.revert_preview_status(resolved_sha)
    applies_cleanly = bool(preview_status["applies_cleanly"])
    conflict_details = str(preview_status["details"] or "")

    reasons: list[str] = []
    if len(parents) > 1:
        reasons.append("merge commits are not supported")
    if prefix is None:
        reasons.append("commit message is missing a recognized [category] prefix")
    elif prefix not in KNOWN_COMMIT_PREFIXES:
        reasons.append(f"commit prefix {prefix!r} is not in the allowed memory prefix set")
    if disallowed_files:
        reasons.append(
            "commit touches files outside the governed memory surface: "
            + ", ".join(disallowed_files)
        )
    if disallowed_system_files:
        reasons.append(
            "[system] commits may only touch governance files: "
            + ", ".join(disallowed_system_files)
        )
    if not applies_cleanly:
        reasons.append("revert does not apply cleanly at the current HEAD")

    return {
        "resolved_sha": resolved_sha,
        "target_message": message,
        "target_prefix": prefix,
        "target_parents": parents,
        "files_changed": files_changed,
        "preview_token": repo.current_head(),
        "applies_cleanly": applies_cleanly,
        "conflict_details": conflict_details,
        "eligible": not reasons,
        "policy_reasons": reasons,
    }


def _append_markdown_block(existing: str, block: str) -> str:
    """Append a markdown block separated by the repo's standard divider."""
    trimmed_existing = existing.rstrip()
    trimmed_block = block.strip()
    if not trimmed_block:
        return existing
    if not trimmed_existing:
        return trimmed_block + "\n"
    return trimmed_existing + "\n\n---\n\n" + trimmed_block + "\n"


def _update_last_periodic_review_date(content: str, review_date: str) -> str | None:
    """Replace the quick-reference periodic review date."""
    updated = re.sub(
        r"(## Last periodic review\s*\n\s*\n\*\*Date:\*\*\s*)([^\n]+)",
        rf"\g<1>{review_date}",
        content,
        count=1,
    )
    return updated if updated != content else None


def _update_current_stage_block(
    content: str,
    review_date: str,
    active_stage: str,
    assessment_summary: str,
) -> str:
    """Update quick-reference current-stage metadata and thresholds."""
    settings = _PERIODIC_REVIEW_STAGE_SETTINGS[active_stage]
    updated = re.sub(
        r"(?m)^## Current active stage:\s*.+$",
        f"## Current active stage: {active_stage}",
        content,
        count=1,
    )
    assessed_line = f"_Last assessed: {review_date} — {assessment_summary}_"
    if re.search(r"(?m)^_Last assessed: .*_$", updated):
        updated = re.sub(
            r"(?m)^_Last assessed: .*_$",
            assessed_line,
            updated,
            count=1,
        )
    else:
        updated = updated.replace(
            f"## Current active stage: {active_stage}\n",
            f"## Current active stage: {active_stage}\n\n{assessed_line}\n",
            1,
        )

    for label, value in settings.items():
        value_str = f"{value} entries" if label == "Aggregation trigger" else str(value)
        if label in {
            "Low-trust retirement threshold",
            "Medium-trust flagging threshold",
            "Staleness trigger (no access)",
        }:
            value_str = f"{value} days"
        if label in {"Identity churn alarm", "Knowledge flooding alarm"}:
            if label == "Identity churn alarm":
                value_str = f"{value} traits/session"
            else:
                value_str = f"{value} files/day"
        if label == "Cluster co-retrieval threshold":
            value_str = f"{value} sessions"
        updated = re.sub(
            rf"(?m)^\| {re.escape(label)} \| .* \| .* \|$",
            f"| {label} | {value_str} | {active_stage} |",
            updated,
            count=1,
        )

    updated = re.sub(
        r"(?m)^\*\*Method:\*\*\s*.+$",
        f"**Method:** {settings['Task similarity method']}",
        updated,
        count=1,
    )
    return updated


def register(
    mcp: "FastMCP",
    get_repo,
    get_root,
    *,
    session_state: SessionState | None = None,
    include_reset_tool: bool = True,
    include_plan_tools: bool = True,
    include_knowledge_tools: bool = True,
    include_identity_tools: bool = True,
) -> dict[str, object]:
    """Register all Tier 1 semantic tools and return their callables."""

    session_state = create_session_state() if session_state is None else session_state
    plan_tool_map: dict[str, object] = {}
    if include_plan_tools:
        plan_tool_map = semantic_plan_tools.register_tools(mcp, get_repo, get_root)
    knowledge_tool_map: dict[str, object] = {}
    if include_knowledge_tools:
        knowledge_tool_map = semantic_knowledge_tools.register_tools(mcp, get_repo, get_root)

    identity_tool_map: dict[str, object] = {}
    if include_identity_tools:
        identity_tool_map = semantic_identity_tools.register_tools(mcp, get_repo, session_state)

    # ------------------------------------------------------------------
    # memory_append_scratchpad
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_append_scratchpad",
        annotations=_tool_annotations(
            title="Append to Scratchpad",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_append_scratchpad(
        target: str,
        content: str,
        section: str | None = None,
    ) -> str:
        """Append content to a scratchpad file (append-only, no conflicts).

        Targets:
          'user'    → scratchpad/USER.md
          'current' → scratchpad/CURRENT.md

        A '---' separator is prepended if the file is non-empty.
        If section is provided, appends under the matching ## {section} heading.

        Args:
            target:  'user' or 'current'.
            content: Markdown content to append.
            section: Optional section heading to append under.

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import ValidationError
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()

        target_map = {"user": "scratchpad/USER.md", "current": "scratchpad/CURRENT.md"}
        if target not in target_map:
            raise ValidationError(f"target must be 'user' or 'current', got: {target}")

        rel_path = target_map[target]
        abs_path = root / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        existing = abs_path.read_text(encoding="utf-8") if abs_path.exists() else ""

        if section and existing:
            # Find ## {section} heading and append under it
            section_heading = f"## {section}"
            if section_heading in existing:
                idx = existing.index(section_heading)
                # Find next ## heading or EOF
                next_heading = re.search(r"\n## ", existing[idx + 1 :])
                if next_heading:
                    insert_at = idx + 1 + next_heading.start() + 1
                    new_content = (
                        existing[:insert_at] + "\n" + content.strip() + "\n" + existing[insert_at:]
                    )
                else:
                    new_content = existing.rstrip() + "\n\n" + content.strip() + "\n"
            else:
                # Create the section
                sep = "\n\n---\n\n" if existing.strip() else ""
                new_content = existing + sep + section_heading + "\n\n" + content.strip() + "\n"
        else:
            sep = "\n\n---\n\n" if existing.strip() else ""
            new_content = existing + sep + content.strip() + "\n"

        abs_path.write_text(new_content, encoding="utf-8")
        repo.add(rel_path)

        commit_msg = f"[scratchpad] Append to {target}"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=[rel_path],
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"target": rel_path},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_record_chat_summary
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_record_chat_summary",
        annotations=_tool_annotations(
            title="Record Chat Session Summary",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_record_chat_summary(
        session_id: str,
        summary: str,
        key_topics: str = "",
    ) -> str:
        """Create or replace a chat session SUMMARY.md and update chats/SUMMARY.md.

        Args:
            session_id:  Session path e.g. 'chats/2026/03/18/chat-001'.
            summary:     Full SUMMARY.md content (without frontmatter — added here).
            key_topics:  Comma-separated list of key topics for the index.

        Returns:
            MemoryWriteResult JSON.
        """
        from ..frontmatter_utils import today_str
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        validate_session_id(session_id)

        # Write session SUMMARY.md
        session_summary_rel, abs_session_summary = resolve_repo_path(
            repo,
            f"{session_id}/SUMMARY.md",
            field_name="session_id",
        )
        abs_session_summary.parent.mkdir(parents=True, exist_ok=True)

        today = today_str()
        fm_dict: dict[str, object] = {
            "session": session_id,
            "date": today,
            "trust": "medium",
            "source": "agent-generated",
        }
        topics = [t.strip() for t in key_topics.split(",") if t.strip()]
        if topics:
            fm_dict["key_topics"] = topics

        import frontmatter as fmlib  # type: ignore[import-untyped]

        post = fmlib.Post(summary, **fm_dict)
        abs_session_summary.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(session_summary_rel)

        files_changed = [session_summary_rel]

        # Update chats/SUMMARY.md — add/update reference to this session
        chats_summary_rel = "chats/SUMMARY.md"
        abs_chats_summary = root / chats_summary_rel
        if abs_chats_summary.exists():
            chats_content = abs_chats_summary.read_text(encoding="utf-8")
            # If session already mentioned, leave it (don't duplicate)
            if session_id not in chats_content:
                # Add brief mention to "Overall history"
                mention = f"\nSee `{session_id}/` for session recorded {today}.\n"
                # Append before ## Structure
                if "## Structure" in chats_content:
                    chats_content = chats_content.replace(
                        "## Structure", mention + "\n## Structure", 1
                    )
                else:
                    chats_content = chats_content.rstrip() + mention
                abs_chats_summary.write_text(chats_content, encoding="utf-8")
                repo.add(chats_summary_rel)
                files_changed.append(chats_summary_rel)

        commit_msg = f"[chat] Record summary for {session_id}"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"session_id": session_id},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_flag_for_review
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_flag_for_review",
        annotations=_tool_annotations(
            title="Flag File for Review",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_flag_for_review(
        path: str,
        reason: str,
        priority: str = "normal",
    ) -> str:
        """Add an entry to meta/review-queue.md flagging a file for review.

        Does not modify the flagged file itself.
        Used by the trust decay workflow and anomaly detection.

        Args:
            path:     Repo-relative path of the file to flag.
            reason:   Why this file needs review.
            priority: 'normal' or 'urgent' (default: 'normal').

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import ValidationError
        from ..frontmatter_utils import today_str
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()

        if priority not in ("normal", "urgent"):
            raise ValidationError(f"priority must be 'normal' or 'urgent': {priority}")

        review_queue_rel = "meta/review-queue.md"
        abs_queue = root / review_queue_rel
        if not abs_queue.exists():
            raise ValidationError(f"Review queue not found: {review_queue_rel}")

        today = today_str()
        priority_tag = "🚨 urgent" if priority == "urgent" else "normal"
        entry = (
            f"\n### {today} — {path} ({priority_tag})\n\n"
            f"**File:** `{path}`  \n"
            f"**Date:** {today}  \n"
            f"**Priority:** {priority}  \n"
            f"**Reason:** {reason}\n"
        )

        content = abs_queue.read_text(encoding="utf-8")
        # Append after last existing entry or at end
        content = content.rstrip() + "\n" + entry
        abs_queue.write_text(content, encoding="utf-8")
        repo.add(review_queue_rel)

        commit_msg = f"[curation] Flag {path} for review ({priority})"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=[review_queue_rel],
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"flagged_path": path, "priority": priority},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_log_access
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_log_access",
        annotations=_tool_annotations(
            title="Log Memory File Access",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_log_access(
        file: str,
        task: str,
        helpfulness: float,
        note: str,
        session_id: str | None = None,
        category: str | None = None,
    ) -> str:
        """Append an access note to the relevant ACCESS.jsonl file and auto-commit.

        This is the canonical way to record that a memory file was retrieved
        during a session. Consistent logging drives the ACCESS-pattern feedback
        loop: access notes → aggregated usage patterns → better summaries →
        smarter retrieval.

        The date field is set automatically to today's date.

        Supported folders (each has its own ACCESS.jsonl):
          identity/, knowledge/, knowledge/_unverified/,
          skills/, plans/, chats/

        Args:
            file:        Repo-relative path of the content file that was accessed
                         (e.g. 'knowledge/literature/galatea-2-2.md').
            task:        Brief description of what the user asked (1–2 sentences).
            helpfulness: Float 0.0–1.0 rating of how useful this file was.
                           0.0–0.1 wrong context; 0.2–0.4 near-miss;
                           0.5–0.6 useful; 0.7–0.8 highly relevant;
                           0.9–1.0 critical.
            note:        One sentence explaining relevance or lack thereof.
            session_id:  Current session path (e.g. 'chats/2026/03/18/chat-001').
                         Optional but strongly recommended.
            category:    Controlled-vocabulary task category. Only set at
                         Consolidation stage once meta/task-categories.md exists.

        Returns:
            MemoryWriteResult JSON with new_state: {access_jsonl, entry_count}.
        """
        import json as _json

        from ..errors import ValidationError
        from ..frontmatter_utils import today_str
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()

        # Validate required fields
        if not isinstance(task, str) or not task.strip():
            raise ValidationError("task must be a non-empty string")
        if not isinstance(note, str) or not note.strip():
            raise ValidationError("note must be a non-empty string")
        if not isinstance(helpfulness, (int, float)):
            raise ValidationError("helpfulness must be a float between 0.0 and 1.0")
        helpfulness = float(helpfulness)
        if not (0.0 <= helpfulness <= 1.0):
            raise ValidationError(f"helpfulness must be between 0.0 and 1.0, got {helpfulness}")
        if session_id is not None:
            validate_session_id(session_id)
        if category is not None:
            category = validate_slug(category, field_name="category")
            categories = _load_task_categories(root)
            if not categories:
                raise ValidationError(
                    "category cannot be set until meta/task-categories.md exists "
                    "with a controlled vocabulary"
                )
            if category not in categories:
                raise ValidationError(
                    f"category must be one of {sorted(categories)}, got: {category}"
                )

        # Resolve and validate the target file path
        file, _ = resolve_repo_path(repo, file, field_name="file")

        # Determine the ACCESS.jsonl path
        access_jsonl = _access_jsonl_for(file)
        if access_jsonl is None:
            from pathlib import PurePosixPath

            root_part = PurePosixPath(file).parts[0] if file else "(empty)"
            raise ValidationError(
                f"Cannot log access for '{file}': '{root_part}/' is not an "
                f"access-tracked directory. Supported roots: {sorted(_ACCESS_ROOTS)}"
            )

        abs_access = root / access_jsonl
        abs_access.parent.mkdir(parents=True, exist_ok=True)

        # Build the JSONL entry
        entry: dict = {
            "file": file,
            "date": today_str(),
            "task": task.strip(),
            "helpfulness": round(helpfulness, 2),
            "note": note.strip(),
        }
        if session_id is not None:
            entry["session_id"] = session_id
        if category is not None:
            entry["category"] = category

        # Append to ACCESS.jsonl
        existing = abs_access.read_text(encoding="utf-8") if abs_access.exists() else ""
        new_line = _json.dumps(entry, ensure_ascii=False)
        updated = (
            (existing.rstrip("\n") + "\n" + new_line + "\n")
            if existing.strip()
            else new_line + "\n"
        )
        abs_access.write_text(updated, encoding="utf-8")
        repo.add(access_jsonl)

        entry_count = updated.count("\n")
        commit_msg = f"[access] Log retrieval of {Path(file).name} (h={entry['helpfulness']:.1f})"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=[access_jsonl],
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"access_jsonl": access_jsonl, "entry_count": entry_count},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_record_reflection
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_record_reflection",
        annotations=_tool_annotations(
            title="Record Session Reflection",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_record_reflection(
        session_id: str,
        memory_retrieved: str,
        memory_influence: str,
        outcome_quality: str,
        gaps_noticed: str,
        system_observations: str = "",
    ) -> str:
        """Write a reflection.md note to the session's chat folder and auto-commit.

        Session reflection is the meta-level self-observation that captures
        *how the memory system performed*, not just what happened. Distinct
        from the chat SUMMARY.md which records what was discussed.

        The reflection format mirrors README § "Session reflection".

        Args:
            session_id:           Canonical session path, e.g. 'chats/2026/03/19/chat-001'.
            memory_retrieved:     List of files accessed and their helpfulness scores (freeform).
            memory_influence:     1–2 sentences on how retrieved memory shaped responses.
            outcome_quality:      Brief assessment of session quality and memory contribution.
            gaps_noticed:         Moments where memory was missing or irrelevant content intruded.
            system_observations:  Optional: patterns about the memory system itself.

        Returns:
            MemoryWriteResult JSON with the written reflection path.
        """
        from ..errors import ValidationError
        from ..models import MemoryWriteResult
        from ..path_policy import validate_session_id

        validate_session_id(session_id)
        repo = get_repo()
        root = get_root()

        session_dir = root / session_id
        if not session_dir.is_dir():
            raise ValidationError(
                f"Session folder does not exist: {session_id}. "
                "Create the chat summary first with memory_record_chat_summary."
            )

        reflection_rel = f"{session_id}/reflection.md"
        reflection_abs = root / reflection_rel

        if reflection_abs.exists():
            raise ValidationError(
                f"Reflection already exists for {session_id}. "
                "Edit it directly with memory_edit if an update is needed."
            )

        lines = [
            "## Session reflection\n",
            "\n",
            f"**Memory retrieved:** {memory_retrieved}\n",
            f"**Memory influence:** {memory_influence}\n",
            f"**Outcome quality:** {outcome_quality}\n",
            f"**Gaps noticed:** {gaps_noticed}\n",
        ]
        if system_observations:
            lines.append(f"**System observations:** {system_observations}\n")

        reflection_abs.write_text("".join(lines), encoding="utf-8")
        repo.add(reflection_rel)
        commit_msg = f"[chat] Add session reflection for {session_id}"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=[reflection_rel],
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"reflection_path": reflection_rel},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_record_periodic_review
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_record_periodic_review",
        annotations=_tool_annotations(
            title="Record Periodic Review Outputs",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_record_periodic_review(
        review_date: str,
        assessment_summary: str,
        belief_diff_entry: str,
        review_queue_entries: str = "",
        active_stage: str = "",
    ) -> str:
        """Apply approved periodic-review outputs to governed meta files.

        Writes are limited to:
          - meta/belief-diff-log.md
          - meta/review-queue.md (optional append)
          - meta/quick-reference.md

        The tool updates the last periodic review date in quick-reference,
        appends a dated belief-diff entry, optionally appends review-queue
        entries, and can update the active stage plus threshold table when the
        review concluded that a stage transition or reaffirmation should be
        recorded.
        """
        from ..errors import NotFoundError, ValidationError
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()

        try:
            date.fromisoformat(review_date)
        except ValueError as exc:
            raise ValidationError(f"review_date must be YYYY-MM-DD, got: {review_date!r}") from exc
        if not assessment_summary.strip():
            raise ValidationError("assessment_summary must be non-empty")
        if not belief_diff_entry.strip():
            raise ValidationError("belief_diff_entry must be non-empty")

        normalized_stage = active_stage.strip()
        if normalized_stage and normalized_stage not in _PERIODIC_REVIEW_STAGE_SETTINGS:
            raise ValidationError(
                "active_stage must be one of Exploration, Calibration, Consolidation"
            )

        quick_reference_rel = "meta/quick-reference.md"
        belief_diff_rel = "meta/belief-diff-log.md"
        review_queue_rel = "meta/review-queue.md"

        abs_quick_reference = root / quick_reference_rel
        abs_belief_diff = root / belief_diff_rel
        abs_review_queue = root / review_queue_rel
        for rel_path, abs_path in (
            (quick_reference_rel, abs_quick_reference),
            (belief_diff_rel, abs_belief_diff),
            (review_queue_rel, abs_review_queue),
        ):
            if not abs_path.exists():
                raise NotFoundError(f"Required periodic-review file not found: {rel_path}")

        quick_reference_content = abs_quick_reference.read_text(encoding="utf-8")
        updated_quick_reference = _update_last_periodic_review_date(
            quick_reference_content, review_date
        )
        if updated_quick_reference is None:
            raise ValidationError(
                "Could not locate the 'Last periodic review' date block in meta/quick-reference.md"
            )

        current_stage_match = re.search(
            r"(?m)^## Current active stage:\s*([^\n]+)$", quick_reference_content
        )
        current_stage = (
            current_stage_match.group(1).strip() if current_stage_match else "Exploration"
        )
        stage_to_record = normalized_stage or current_stage
        updated_quick_reference = _update_current_stage_block(
            updated_quick_reference,
            review_date,
            stage_to_record,
            assessment_summary,
        )
        abs_quick_reference.write_text(updated_quick_reference, encoding="utf-8")
        repo.add(quick_reference_rel)

        belief_diff_content = abs_belief_diff.read_text(encoding="utf-8")
        abs_belief_diff.write_text(
            _append_markdown_block(belief_diff_content, belief_diff_entry),
            encoding="utf-8",
        )
        repo.add(belief_diff_rel)

        files_changed = [quick_reference_rel, belief_diff_rel]
        review_queue_written = False
        if review_queue_entries.strip():
            review_queue_content = abs_review_queue.read_text(encoding="utf-8")
            abs_review_queue.write_text(
                _append_markdown_block(review_queue_content, review_queue_entries),
                encoding="utf-8",
            )
            repo.add(review_queue_rel)
            files_changed.append(review_queue_rel)
            review_queue_written = True

        commit_msg = f"[system] Record periodic review {review_date}"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={
                "review_date": review_date,
                "active_stage": stage_to_record,
                "belief_diff_written": True,
                "review_queue_written": review_queue_written,
            },
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_revert_commit
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_revert_commit",
        annotations=_tool_annotations(
            title="Revert a Memory Commit",
            readOnlyHint=False,
            destructiveHint=True,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_revert_commit(
        sha: str,
        confirm: bool = False,
        preview_token: str | None = None,
    ) -> str:
        """Preview or create a revert commit for a prior memory-domain commit.

        Preview mode (default) inspects the target commit, reports the files
        that would be affected, and returns a preview token tied to the current
        HEAD. Confirm mode requires that preview token and will only proceed if
        the repo has not moved since preview and the target commit passes the
        memory-domain safety checks.

        Use memory_git_log first to identify the commit SHA you want to revert.

        Args:
            sha:           Full or abbreviated commit SHA to inspect or revert.
            confirm:       False returns a preview only. True performs the revert.
            preview_token: Required when confirm=True. Must match the HEAD SHA
                           returned by the most recent preview.

        Returns:
            MemoryWriteResult JSON with preview metadata or the new revert SHA.
        """
        import re as _re

        from ..errors import ValidationError
        from ..models import MemoryWriteResult

        if not _re.fullmatch(r"[0-9a-f]{4,64}", sha, _re.IGNORECASE):
            raise ValidationError(f"Invalid SHA: {sha!r}. Must be a 4–64 character hex string.")

        repo = get_repo()
        preview = _build_revert_preview(repo, sha)

        if not confirm:
            result = MemoryWriteResult(
                files_changed=cast(list[str], preview["files_changed"]),
                commit_sha=None,
                commit_message=None,
                new_state={
                    "mode": "preview",
                    **preview,
                },
                warnings=cast(list[str], preview["policy_reasons"]),
            )
            return result.to_json()

        if not preview_token:
            raise ValidationError(
                "preview_token is required when confirm=True. "
                "Call memory_revert_commit with confirm=False first."
            )

        current_head = repo.current_head()
        if preview_token != current_head:
            raise ValidationError(
                "Repository HEAD changed since preview. "
                "Re-run memory_revert_commit with confirm=False and review the new preview."
            )

        if not bool(preview["applies_cleanly"]):
            conflict_details = str(preview["conflict_details"] or "")
            detail_suffix = f" Details: {conflict_details}" if conflict_details else ""
            raise ValidationError(
                "Revert preview indicates conflicts at the current HEAD. "
                "Review conflict_details from preview output and re-run preview after resolving competing changes."
                + detail_suffix
            )

        policy_reasons = cast(list[str], preview["policy_reasons"])
        if policy_reasons:
            raise ValidationError(
                "Commit cannot be reverted by memory_revert_commit: " + "; ".join(policy_reasons)
            )

        resolved_sha = str(preview["resolved_sha"])
        commit_result = repo.revert(resolved_sha)

        result = MemoryWriteResult.from_commit(
            files_changed=cast(list[str], preview["files_changed"]),
            commit_result=commit_result,
            commit_message=f"Revert {resolved_sha}",
            new_state={
                "mode": "confirm",
                "reverted_sha": resolved_sha,
                "new_sha": commit_result.sha,
                "preview_token": preview_token,
            },
        )
        return result.to_json()

    if include_reset_tool:
        # ------------------------------------------------------------------
        # memory_reset_session_state
        # ------------------------------------------------------------------
        @mcp.tool(
            name="memory_reset_session_state",
            annotations=_tool_annotations(
                title="Reset Per-Session State",
                readOnlyHint=False,
                destructiveHint=False,
                idempotentHint=True,
                openWorldHint=False,
            ),
        )
        async def memory_reset_session_state() -> str:
            """Reset per-session counters (identity churn alarm) to their initial values.

            Call this at the start of each new session to ensure a clean slate,
            particularly in long-running MCP server processes where the server is
            not restarted between sessions.

            Returns:
                JSON object with the reset state values.
            """
            import json as _json

            return _json.dumps(reset_session_state(session_state))

    tools: dict[str, object] = {
        "memory_append_scratchpad": memory_append_scratchpad,
        "memory_record_chat_summary": memory_record_chat_summary,
        "memory_flag_for_review": memory_flag_for_review,
        "memory_log_access": memory_log_access,
        "memory_record_reflection": memory_record_reflection,
        "memory_record_periodic_review": memory_record_periodic_review,
        "memory_revert_commit": memory_revert_commit,
    }
    tools.update(plan_tool_map)
    tools.update(knowledge_tool_map)
    tools.update(identity_tool_map)
    if include_reset_tool:
        tools["memory_reset_session_state"] = memory_reset_session_state
    return tools
