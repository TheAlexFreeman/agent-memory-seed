"""Session and governance semantic tools."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, cast

from ...path_policy import (
    KNOWN_COMMIT_PREFIXES,
    resolve_repo_path,
    validate_session_id,
    validate_slug,
)

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _tool_annotations(**kwargs: object) -> Any:
    return cast(Any, kwargs)


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


def _access_jsonl_for(rel_path: str) -> str | None:
    parts = PurePosixPath(rel_path).parts
    if not parts:
        return None
    root = parts[0]
    if root not in _ACCESS_ROOTS:
        return None
    if root == "knowledge" and len(parts) > 1 and parts[1] == "_unverified":
        return "knowledge/_unverified/ACCESS.jsonl"
    return f"{root}/ACCESS.jsonl"


def _load_task_categories(root: Path) -> set[str]:
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


def _append_markdown_block(existing: str, block: str) -> str:
    trimmed_existing = existing.rstrip()
    trimmed_block = block.strip()
    if not trimmed_block:
        return existing
    if not trimmed_existing:
        return trimmed_block + "\n"
    return trimmed_existing + "\n\n---\n\n" + trimmed_block + "\n"


def _update_last_periodic_review_date(content: str, review_date: str) -> str | None:
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
    settings = _PERIODIC_REVIEW_STAGE_SETTINGS[active_stage]
    updated = re.sub(
        r"(?m)^## Current active stage:\s*.+$",
        f"## Current active stage: {active_stage}",
        content,
        count=1,
    )
    assessed_line = f"_Last assessed: {review_date} — {assessment_summary}_"
    if re.search(r"(?m)^_Last assessed: .*_$", updated):
        updated = re.sub(r"(?m)^_Last assessed: .*_$", assessed_line, updated, count=1)
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
            value_str = (
                f"{value} traits/session"
                if label == "Identity churn alarm"
                else f"{value} files/day"
            )
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


def _is_revertable_memory_path(rel_path: str) -> bool:
    parts = PurePosixPath(rel_path).parts
    if not parts:
        return False
    if len(parts) == 1 and parts[0] in _REVERT_ALLOWED_FILES:
        return True
    return parts[0] in _REVERT_ALLOWED_TOP_LEVELS


def _is_revertable_system_path(rel_path: str) -> bool:
    parts = PurePosixPath(rel_path).parts
    if not parts:
        return False
    if len(parts) == 1 and parts[0] in _REVERT_SYSTEM_FILES:
        return True
    return parts[0] in _REVERT_SYSTEM_TOP_LEVELS


def _build_revert_preview(repo, sha: str) -> dict[str, object]:
    from ...errors import ValidationError

    try:
        commit = repo.inspect_commit(sha)
    except Exception as exc:
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


def register_tools(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register session and governance semantic tools."""

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
        target: str, content: str, section: str | None = None
    ) -> str:
        from ...errors import ValidationError
        from ...models import MemoryWriteResult

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
            section_heading = f"## {section}"
            if section_heading in existing:
                idx = existing.index(section_heading)
                next_heading = re.search(r"\n## ", existing[idx + 1 :])
                if next_heading:
                    insert_at = idx + 1 + next_heading.start() + 1
                    new_content = (
                        existing[:insert_at] + "\n" + content.strip() + "\n" + existing[insert_at:]
                    )
                else:
                    new_content = existing.rstrip() + "\n\n" + content.strip() + "\n"
            else:
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
        session_id: str, summary: str, key_topics: str = ""
    ) -> str:
        from ...frontmatter_utils import today_str
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        validate_session_id(session_id)
        session_summary_rel, abs_session_summary = resolve_repo_path(
            repo, f"{session_id}/SUMMARY.md", field_name="session_id"
        )
        abs_session_summary.parent.mkdir(parents=True, exist_ok=True)

        today = today_str()
        fm_dict: dict[str, object] = {
            "session": session_id,
            "date": today,
            "trust": "medium",
            "source": "agent-generated",
        }
        topics = [topic.strip() for topic in key_topics.split(",") if topic.strip()]
        if topics:
            fm_dict["key_topics"] = topics

        import frontmatter as fmlib  # type: ignore[import-untyped]

        post = fmlib.Post(summary, **fm_dict)
        abs_session_summary.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(session_summary_rel)

        files_changed = [session_summary_rel]
        chats_summary_rel = "chats/SUMMARY.md"
        abs_chats_summary = root / chats_summary_rel
        if abs_chats_summary.exists():
            chats_content = abs_chats_summary.read_text(encoding="utf-8")
            if session_id not in chats_content:
                mention = f"\nSee `{session_id}/` for session recorded {today}.\n"
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
    async def memory_flag_for_review(path: str, reason: str, priority: str = "normal") -> str:
        from ...errors import ValidationError
        from ...frontmatter_utils import today_str
        from ...models import MemoryWriteResult

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
        abs_queue.write_text(content.rstrip() + "\n" + entry, encoding="utf-8")
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
        import json as _json

        from ...errors import ValidationError
        from ...frontmatter_utils import today_str
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
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
                    "category cannot be set until meta/task-categories.md exists with a controlled vocabulary"
                )
            if category not in categories:
                raise ValidationError(
                    f"category must be one of {sorted(categories)}, got: {category}"
                )

        file, _ = resolve_repo_path(repo, file, field_name="file")
        access_jsonl = _access_jsonl_for(file)
        if access_jsonl is None:
            root_part = PurePosixPath(file).parts[0] if file else "(empty)"
            raise ValidationError(
                f"Cannot log access for '{file}': '{root_part}/' is not an access-tracked directory. Supported roots: {sorted(_ACCESS_ROOTS)}"
            )

        abs_access = root / access_jsonl
        abs_access.parent.mkdir(parents=True, exist_ok=True)
        entry: dict[str, object] = {
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
        from ...errors import ValidationError
        from ...models import MemoryWriteResult

        validate_session_id(session_id)
        repo = get_repo()
        root = get_root()

        session_dir = root / session_id
        if not session_dir.is_dir():
            raise ValidationError(
                f"Session folder does not exist: {session_id}. Create the chat summary first with memory_record_chat_summary."
            )

        reflection_rel = f"{session_id}/reflection.md"
        reflection_abs = root / reflection_rel
        if reflection_abs.exists():
            raise ValidationError(
                f"Reflection already exists for {session_id}. Edit it directly with memory_edit if an update is needed."
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
        from ...errors import NotFoundError, ValidationError
        from ...models import MemoryWriteResult

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
            _append_markdown_block(belief_diff_content, belief_diff_entry), encoding="utf-8"
        )
        repo.add(belief_diff_rel)

        files_changed = [quick_reference_rel, belief_diff_rel]
        review_queue_written = False
        if review_queue_entries.strip():
            review_queue_content = abs_review_queue.read_text(encoding="utf-8")
            abs_review_queue.write_text(
                _append_markdown_block(review_queue_content, review_queue_entries), encoding="utf-8"
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
        import re as _re

        from ...errors import ValidationError
        from ...models import MemoryWriteResult

        if not _re.fullmatch(r"[0-9a-f]{4,64}", sha, _re.IGNORECASE):
            raise ValidationError(f"Invalid SHA: {sha!r}. Must be a 4–64 character hex string.")

        repo = get_repo()
        preview = _build_revert_preview(repo, sha)
        if not confirm:
            result = MemoryWriteResult(
                files_changed=cast(list[str], preview["files_changed"]),
                commit_sha=None,
                commit_message=None,
                new_state={"mode": "preview", **preview},
                warnings=cast(list[str], preview["policy_reasons"]),
            )
            return result.to_json()

        if not preview_token:
            raise ValidationError(
                "preview_token is required when confirm=True. Call memory_revert_commit with confirm=False first."
            )

        current_head = repo.current_head()
        if preview_token != current_head:
            raise ValidationError(
                "Repository HEAD changed since preview. Re-run memory_revert_commit with confirm=False and review the new preview."
            )

        if not bool(preview["applies_cleanly"]):
            conflict_details = str(preview["conflict_details"] or "")
            detail_suffix = f" Details: {conflict_details}" if conflict_details else ""
            raise ValidationError(
                "Revert preview indicates conflicts at the current HEAD. Review conflict_details from preview output and re-run preview after resolving competing changes."
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

    return {
        "memory_append_scratchpad": memory_append_scratchpad,
        "memory_record_chat_summary": memory_record_chat_summary,
        "memory_flag_for_review": memory_flag_for_review,
        "memory_log_access": memory_log_access,
        "memory_record_reflection": memory_record_reflection,
        "memory_record_periodic_review": memory_record_periodic_review,
        "memory_revert_commit": memory_revert_commit,
    }


__all__ = ["register_tools"]
