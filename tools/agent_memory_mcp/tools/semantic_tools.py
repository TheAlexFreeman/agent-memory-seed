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
from pathlib import Path
from typing import TYPE_CHECKING

from ..path_policy import (
    forbid_prefix,
    require_under_prefix,
    resolve_repo_path,
    validate_session_id,
    validate_slug,
    validate_top_level_root,
)

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# Identity churn alarm threshold per session
_IDENTITY_CHURN_LIMIT = 5

# ACCESS log folders — these directories each contain an ACCESS.jsonl file
_ACCESS_ROOTS = ("identity", "knowledge", "skills", "plans", "chats")


def _plan_path(plan_id: str) -> str:
    return f"plans/{validate_slug(plan_id, field_name='plan_id')}.md"


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


def register(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register all Tier 1 semantic tools and return their callables."""

    # Per-server-instance state.  Resets each time create_mcp() is called
    # (i.e. on server restart).  Agents should call memory_reset_session_state
    # at the start of each session to ensure a clean slate in long-running
    # server processes.
    _session_state: dict[str, int] = {"identity_updates": 0}

    # ------------------------------------------------------------------
    # memory_mark_plan_item_complete
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_mark_plan_item_complete",
        annotations={
            "title": "Mark Plan Item Complete",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_mark_plan_item_complete(
        plan_id: str,
        phase_index: int,
        item_index: int,
        version_token: str | None = None,
    ) -> str:
        """Mark a plan checklist item ☐→☑ and keep all invariants in sync.

        Invariants maintained (all atomically committed):
          1. ☐ → ☑ for the target item in the plan file
          2. Phase counter updated: N/M → (N+1)/M; phase → ☑ if all done
          3. next_action frontmatter updated to first remaining unchecked item;
             status → 'complete' if all phases done
          4. last_verified updated to today
          5. Progress log table gets a new row
          6. plans/SUMMARY.md BEGIN/END block updated

        Args:
            plan_id:       Plan identifier without .md extension
                           (e.g. 'react-stack-research').
            phase_index:   0-based phase number.
            item_index:    0-based item number within the phase.
            version_token: Optional version token for the plan file.

        Returns:
            MemoryWriteResult JSON with new_state:
              next_action    (str|null)  Description of next unchecked item
              phase_progress [done,total]
              plan_progress  [done,total]
              status         (str)       'active' or 'complete'
        """
        from ..errors import NotFoundError
        from ..frontmatter_utils import (
            add_progress_log_row,
            build_plan_summary_block,
            mark_plan_item_complete,
            read_with_frontmatter,
            replace_begin_end_block,
            today_str,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if not abs_plan.exists():
            raise NotFoundError(f"Plan not found: {plan_path}")

        repo.check_version_token(plan_path, version_token)

        content = abs_plan.read_text(encoding="utf-8")
        fm_dict, _ = read_with_frontmatter(abs_plan)

        # Mark item and get updated stats
        new_content, stats = mark_plan_item_complete(content, phase_index, item_index)

        # Determine item filename for commit message (extract from item text)
        # Re-parse to get item text
        from ..frontmatter_utils import parse_plan_items
        phases = parse_plan_items(content)
        item_text = phases[phase_index]["items"][item_index]["text"]
        # Extract likely filename (pattern: write knowledge/_unverified/foo/bar.md)
        fn_match = re.search(r'[\w./_-]+\.(?:md|py|ts|js)\b', item_text)
        item_filename = fn_match.group(0).split("/")[-1] if fn_match else item_text[:40]

        plan_done, plan_total = stats["plan_progress"]

        # Add progress log row
        action_desc = f"Completed {item_filename} ({plan_id} {plan_done}/{plan_total})"
        new_content = add_progress_log_row(new_content, action_desc)

        # Update frontmatter
        all_complete = stats["all_complete"]
        fm_updates = {
            "next_action": stats["next_action"],
            "last_verified": today_str(),
        }
        if all_complete:
            fm_updates["status"] = "complete"

        # Re-read frontmatter from new_content and apply updates
        import frontmatter as fmlib
        post = fmlib.loads(new_content)
        for k, v in fm_updates.items():
            if v is None:
                post.metadata.pop(k, None)
            else:
                post.metadata[k] = v
        final_content = fmlib.dumps(post)

        abs_plan.write_text(final_content, encoding="utf-8")
        repo.add(plan_path)

        # Update plans/SUMMARY.md
        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            trust = fm_dict.get("trust", "medium")
            status_str = "complete" if all_complete else "active"
            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=plan_id,
                status=status_str,
                trust=trust,
                next_action=stats["next_action"],
                plan_progress=(plan_done, plan_total),
            )
            updated_summary = replace_begin_end_block(summary_content, plan_id, new_block)
            if updated_summary is None:
                warnings.append(
                    f"BEGIN/END anchor for '{plan_id}' not found in plans/SUMMARY.md. "
                    "Summary not updated — add anchors manually."
                )
            else:
                abs_summary.write_text(updated_summary, encoding="utf-8")
                repo.add(summary_path)

        commit_msg = (
            f"[plan] Mark {item_filename} complete "
            f"({plan_id} {plan_done}/{plan_total})"
        )
        sha = repo.commit(commit_msg)

        new_state = {
            "next_action": stats["next_action"],
            "phase_progress": stats["phase_progress"],
            "plan_progress": stats["plan_progress"],
            "status": "complete" if all_complete else "active",
        }
        result = MemoryWriteResult(
            files_changed=[plan_path] + ([summary_path] if abs_summary.exists() else []),
            commit_sha=sha,
            commit_message=commit_msg,
            new_state=new_state,
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_promote_knowledge
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_promote_knowledge",
        annotations={
            "title": "Promote Knowledge File to Verified",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_promote_knowledge(
        source_path: str,
        trust_level: str = "high",
        target_path: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a file from knowledge/_unverified/ to knowledge/, updating trust.

        Invariants maintained:
          1. Frontmatter: trust → trust_level, last_verified → today
          2. File moved via git mv (history preserved)
          3. Source _unverified/SUMMARY.md entry removed
          4. Target knowledge/SUMMARY.md entry added in matching section
          5. Auto-committed

        Args:
            source_path:   Repo-relative path, must be under knowledge/_unverified/.
            trust_level:   'medium' or 'high' (default: 'high').
            target_path:   Destination path (default: inferred by removing _unverified/).
            version_token: Optional version token for source file.

        Returns:
            MemoryWriteResult JSON with new_state: {new_path, trust}.
        """
        from ..errors import NotFoundError, ValidationError
        from ..frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        source_path, abs_source = resolve_repo_path(repo, source_path, field_name="source_path")
        require_under_prefix(
            source_path,
            "knowledge/_unverified",
            field_name="source_path",
        )
        if trust_level not in ("medium", "high"):
            raise ValidationError(f"trust_level must be 'medium' or 'high', got: {trust_level}")

        if not abs_source.exists():
            raise NotFoundError(f"Source file not found: {source_path}")

        repo.check_version_token(source_path, version_token)

        # Infer target path
        if target_path is None:
            target_path = source_path.replace("knowledge/_unverified/", "knowledge/", 1)
        target_path, _ = resolve_repo_path(repo, target_path, field_name="target_path")
        validate_top_level_root(
            target_path,
            allowed_roots=("knowledge",),
            field_name="target_path",
        )
        forbid_prefix(
            target_path,
            "knowledge/_unverified",
            field_name="target_path",
        )

        # Update frontmatter before moving
        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["trust"] = trust_level
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        # Move file
        abs_target = repo.abs_path(target_path)
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, target_path)

        files_changed = [source_path, target_path]

        # Update source SUMMARY.md (_unverified)
        filename = Path(source_path).name
        section_id = infer_section_id_from_path(source_path)

        source_summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_src_summary = root / source_summary_path
        if abs_src_summary.exists():
            src_summary = abs_src_summary.read_text(encoding="utf-8")
            updated = remove_entry_from_section(src_summary, section_id, filename)
            if updated is None:
                warnings.append(
                    f"Section '<!-- section: {section_id} -->' not found in "
                    f"{source_summary_path}. Entry not removed."
                )
            else:
                abs_src_summary.write_text(updated, encoding="utf-8")
                repo.add(source_summary_path)
                files_changed.append(source_summary_path)

        # Update target SUMMARY.md (knowledge/)
        target_section_id = infer_section_id_from_path(target_path)
        target_summary_path = "knowledge/SUMMARY.md"
        abs_tgt_summary = root / target_summary_path
        if abs_tgt_summary.exists():
            tgt_summary = abs_tgt_summary.read_text(encoding="utf-8")
            # Build a summary entry line
            title = fm_dict.get("title", filename.replace(".md", "").replace("-", " ").title())
            entry = f"- **[{filename}]({target_path})** — {title}"
            updated = insert_entry_in_section(tgt_summary, target_section_id, entry)
            if updated is None:
                warnings.append(
                    f"Section '<!-- section: {target_section_id} -->' not found in "
                    f"{target_summary_path}. Entry not added — add manually."
                )
            else:
                abs_tgt_summary.write_text(updated, encoding="utf-8")
                repo.add(target_summary_path)
                files_changed.append(target_summary_path)

        subject = infer_section_id_from_path(target_path)
        commit_msg = (
            f"[curation] Promote {filename} to knowledge/{subject}/ "
            f"(trust: {trust_level})"
        )
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"new_path": target_path, "trust": trust_level},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_demote_knowledge
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_demote_knowledge",
        annotations={
            "title": "Demote Knowledge File to Unverified",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_demote_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a verified knowledge file back to _unverified/ with trust: low.

        Inverse of memory_promote_knowledge. Updates trust, moves file,
        updates both SUMMARY.md files, auto-commits.

        Args:
            source_path:   Repo-relative path under knowledge/ (not _unverified/).
            reason:        Optional reason appended to commit message.
            version_token: Optional version token.

        Returns:
            MemoryWriteResult JSON with new_state: {new_path, trust}.
        """
        from ..errors import NotFoundError, ValidationError
        from ..frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        source_path, abs_source = resolve_repo_path(repo, source_path, field_name="source_path")
        validate_top_level_root(
            source_path,
            allowed_roots=("knowledge",),
            field_name="source_path",
        )
        if source_path.startswith("knowledge/_unverified/"):
            raise ValidationError(
                f"source_path is already under _unverified/: {source_path}. "
                "Use memory_archive_knowledge instead if you want to archive it."
            )
        if not abs_source.exists():
            raise NotFoundError(f"File not found: {source_path}")

        repo.check_version_token(source_path, version_token)

        # Infer target path
        target_path = source_path.replace("knowledge/", "knowledge/_unverified/", 1)
        filename = Path(source_path).name
        section_id = infer_section_id_from_path(source_path)

        # Update frontmatter
        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["trust"] = "low"
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        # Move file
        abs_target = repo.abs_path(target_path)
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, target_path)

        files_changed = [source_path, target_path]

        # Remove from knowledge/SUMMARY.md
        src_summary_path = "knowledge/SUMMARY.md"
        abs_src_summary = root / src_summary_path
        if abs_src_summary.exists():
            content = abs_src_summary.read_text(encoding="utf-8")
            updated = remove_entry_from_section(content, section_id, filename)
            if updated is None:
                warnings.append(f"Section '{section_id}' not found in {src_summary_path}.")
            else:
                abs_src_summary.write_text(updated, encoding="utf-8")
                repo.add(src_summary_path)
                files_changed.append(src_summary_path)

        # Add to knowledge/_unverified/SUMMARY.md
        tgt_summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_tgt_summary = root / tgt_summary_path
        tgt_section_id = infer_section_id_from_path(target_path)
        if abs_tgt_summary.exists():
            content = abs_tgt_summary.read_text(encoding="utf-8")
            title = fm_dict.get("title", filename.replace(".md", "").replace("-", " ").title())
            entry = f"- **[{filename}]({target_path})** — {title} _(demoted)_"
            updated = insert_entry_in_section(content, tgt_section_id, entry)
            if updated is None:
                warnings.append(f"Section '{tgt_section_id}' not found in {tgt_summary_path}.")
            else:
                abs_tgt_summary.write_text(updated, encoding="utf-8")
                repo.add(tgt_summary_path)
                files_changed.append(tgt_summary_path)

        reason_str = f" ({reason})" if reason else ""
        commit_msg = f"[curation] Demote {filename} to _unverified/{reason_str}"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"new_path": target_path, "trust": "low"},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_archive_knowledge
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_archive_knowledge",
        annotations={
            "title": "Archive Knowledge File",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_archive_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a knowledge file to knowledge/_archive/ and mark it archived.

        Used by the trust decay workflow for low-trust files past 120 days.
        The archive is intentionally NOT listed in SUMMARY.md.

        Invariants: status→archived, last_verified→today, removed from
        source SUMMARY.md, moved to knowledge/_archive/.

        Args:
            source_path:   Repo-relative path under knowledge/.
            reason:        Optional reason for archival.
            version_token: Optional version token.

        Returns:
            MemoryWriteResult JSON with new_state: {archive_path}.
        """
        from ..errors import NotFoundError, ValidationError
        from ..frontmatter_utils import (
            infer_section_id_from_path,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        source_path, abs_source = resolve_repo_path(repo, source_path, field_name="source_path")
        validate_top_level_root(
            source_path,
            allowed_roots=("knowledge",),
            field_name="source_path",
        )
        if not abs_source.exists():
            raise NotFoundError(f"File not found: {source_path}")

        repo.check_version_token(source_path, version_token)

        filename = Path(source_path).name
        # Determine archive subfolder mirroring source structure
        rel_to_knowledge = source_path[len("knowledge/"):]
        if rel_to_knowledge.startswith("_unverified/"):
            rel_to_knowledge = rel_to_knowledge[len("_unverified/"):]
        archive_path = f"knowledge/_archive/{rel_to_knowledge}"

        # Update frontmatter
        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["status"] = "archived"
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        # Move to archive
        abs_archive = repo.abs_path(archive_path)
        abs_archive.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, archive_path)

        files_changed = [source_path, archive_path]

        # Remove from source SUMMARY.md
        section_id = infer_section_id_from_path(source_path)
        if source_path.startswith("knowledge/_unverified/"):
            summary_path = "knowledge/_unverified/SUMMARY.md"
        else:
            summary_path = "knowledge/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            content = abs_summary.read_text(encoding="utf-8")
            updated = remove_entry_from_section(content, section_id, filename)
            if updated is None:
                warnings.append(f"Section '{section_id}' not found in {summary_path}.")
            else:
                abs_summary.write_text(updated, encoding="utf-8")
                repo.add(summary_path)
                files_changed.append(summary_path)

        reason_str = f" ({reason})" if reason else ""
        commit_msg = f"[curation] Archive {filename}{reason_str}"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"archive_path": archive_path},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_add_knowledge_file
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_add_knowledge_file",
        annotations={
            "title": "Add Knowledge File to Unverified",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_add_knowledge_file(
        path: str,
        content: str,
        source: str,
        session_id: str,
        trust: str = "low",
        summary_entry: str | None = None,
    ) -> str:
        """Create a new knowledge file with correct frontmatter and SUMMARY entry.

        The file must be under knowledge/_unverified/ (all new knowledge is
        quarantined until verified by the user via memory_promote_knowledge).

        Invariants:
          1. Correct frontmatter: source, created, trust, origin_session
          2. _unverified/SUMMARY.md entry added in the matching section
          3. Auto-committed as [knowledge] Add {filename}

        Args:
            path:          Repo-relative path under knowledge/_unverified/.
            content:       File body (do NOT include frontmatter — this tool adds it).
            source:        Provenance string: 'external-research', 'agent-generated',
                           'user-stated', etc.
            session_id:    Current session path for origin_session frontmatter field
                           (e.g. 'chats/2026/03/18/chat-001').
            trust:         'low' (default) — use memory_promote_knowledge to elevate.
            summary_entry: One-line description for SUMMARY.md. Inferred from the
                           first H1 heading in content if not provided.

        Returns:
            MemoryWriteResult JSON with new_state: {version_token}.
        """
        import os

        from ..errors import ValidationError
        from ..frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            today_str,
            write_with_frontmatter,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        validate_session_id(session_id)
        path, abs_path = resolve_repo_path(repo, path)
        require_under_prefix(path, "knowledge/_unverified")
        if trust != "low":
            raise ValidationError("trust must be 'low' for new unverified knowledge")

        max_bytes = int(os.environ.get("MEMORY_MAX_FILE_BYTES", "512000"))
        content_bytes = len(content.encode("utf-8"))
        if content_bytes > max_bytes:
            raise ValidationError(
                f"Content is {content_bytes:,} bytes, which exceeds the "
                f"{max_bytes:,}-byte limit (set MEMORY_MAX_FILE_BYTES to override). "
                "Summarize or split the content before writing."
            )
        if abs_path.exists():
            raise ValidationError(
                f"File already exists: {path}. Use memory_write to overwrite."
            )

        # Build frontmatter
        today = today_str()
        fm_dict = {
            "source": source,
            "created": today,
            "trust": "low",
            "origin_session": session_id,
        }

        # Create file
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        write_with_frontmatter(abs_path, fm_dict, content)
        repo.add(path)

        # Infer summary entry from first H1 if not provided
        if summary_entry is None:
            h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            summary_entry = h1_match.group(1).strip() if h1_match else Path(path).stem

        # Update _unverified/SUMMARY.md
        section_id = infer_section_id_from_path(path)
        filename = Path(path).name
        summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            entry = f"- **[{filename}]({path})** — {summary_entry}"
            updated = insert_entry_in_section(summary_content, section_id, entry)
            if updated is None:
                warnings.append(
                    f"Section '<!-- section: {section_id} -->' not found in "
                    f"{summary_path}. Entry not added — add manually."
                )
            else:
                abs_summary.write_text(updated, encoding="utf-8")
                repo.add(summary_path)

        files_changed = [path] + ([summary_path] if abs_summary.exists() else [])
        commit_msg = f"[knowledge] Add {filename}"
        sha = repo.commit(commit_msg)

        new_token = repo.hash_object(path)
        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"version_token": new_token},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_append_scratchpad
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_append_scratchpad",
        annotations={
            "title": "Append to Scratchpad",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
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
                next_heading = re.search(r"\n## ", existing[idx + 1:])
                if next_heading:
                    insert_at = idx + 1 + next_heading.start() + 1
                    new_content = (
                        existing[:insert_at]
                        + "\n"
                        + content.strip()
                        + "\n"
                        + existing[insert_at:]
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
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=[rel_path],
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"target": rel_path},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_update_identity_trait
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_update_identity_trait",
        annotations={
            "title": "Update Identity Trait",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_update_identity_trait(
        file: str,
        key: str,
        value: str,
        mode: str = "upsert",
        version_token: str | None = None,
    ) -> str:
        """Update a named field in an identity file.

        Checks identity churn alarm: if ≥5 identity traits have been updated
        this session, raises ValidationError requiring confirmation.

        Modes:
          'upsert'  — update if key exists, create if not (default)
          'append'  — append value to existing content under the key
          'replace' — replace the entire section with value

        Args:
            file:          Identity filename without path or .md
                           (e.g. 'profile', 'professional', 'communication-style').
            key:           Frontmatter key or body section heading to update.
            value:         New value or content to write.
            mode:          'upsert', 'append', or 'replace'.
            version_token: Optional version token.

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import ValidationError
        from ..frontmatter_utils import read_with_frontmatter, write_with_frontmatter, today_str
        from ..models import MemoryWriteResult

        repo = get_repo()

        if mode not in ("upsert", "append", "replace"):
            raise ValidationError(f"mode must be 'upsert', 'append', or 'replace': {mode}")

        # Identity churn alarm
        if _session_state["identity_updates"] >= _IDENTITY_CHURN_LIMIT:
            raise ValidationError(
                f"Identity churn alarm: {_IDENTITY_CHURN_LIMIT} trait updates this session — "
                "call memory_reset_session_state to acknowledge and reset the counter, "
                "or restart the MCP server."
            )

        file = validate_slug(file, field_name="file")
        rel_path, abs_path = resolve_repo_path(repo, f"identity/{file}.md")
        if not abs_path.exists():
            raise ValidationError(f"Identity file not found: {rel_path}")

        repo.check_version_token(rel_path, version_token)

        fm_dict, body = read_with_frontmatter(abs_path)

        # Try frontmatter key first
        if key in fm_dict or (mode == "upsert" and key not in body):
            # Update as frontmatter
            if mode == "append" and key in fm_dict:
                existing = str(fm_dict[key])
                fm_dict[key] = existing + "\n" + value
            else:
                fm_dict[key] = value
            fm_dict["last_verified"] = today_str()
            write_with_frontmatter(abs_path, fm_dict, body)
        else:
            # Treat as body section heading
            section_heading = f"## {key}"
            if section_heading in body:
                if mode == "replace":
                    # Replace section content
                    parts = body.split(section_heading, 1)
                    after = parts[1]
                    next_section = re.search(r"\n## ", after)
                    if next_section:
                        body = (
                            parts[0]
                            + section_heading
                            + "\n\n"
                            + value.strip()
                            + "\n"
                            + after[next_section.start():]
                        )
                    else:
                        body = parts[0] + section_heading + "\n\n" + value.strip() + "\n"
                elif mode == "append":
                    parts = body.split(section_heading, 1)
                    after = parts[1]
                    next_section = re.search(r"\n## ", after)
                    if next_section:
                        body = (
                            parts[0]
                            + section_heading
                            + after[: next_section.start()]
                            + "\n"
                            + value.strip()
                            + "\n"
                            + after[next_section.start():]
                        )
                    else:
                        body = parts[0] + section_heading + after.rstrip() + "\n\n" + value.strip() + "\n"
                else:  # upsert
                    body = body.replace(section_heading, section_heading + "\n\n" + value.strip(), 1)
            else:
                # Create new section at end
                body = body.rstrip() + f"\n\n{section_heading}\n\n{value.strip()}\n"

            fm_dict["last_verified"] = today_str()
            write_with_frontmatter(abs_path, fm_dict, body)

        repo.add(rel_path)
        _session_state["identity_updates"] += 1

        commit_msg = f"[identity] Update {key} in identity/{file}.md"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=[rel_path],
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={
                "key": key,
                "mode": mode,
                "identity_updates_this_session": _session_state["identity_updates"],
            },
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_record_chat_summary
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_record_chat_summary",
        annotations={
            "title": "Record Chat Session Summary",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
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
        warnings = []

        validate_session_id(session_id)

        # Write session SUMMARY.md
        session_summary_rel, abs_session_summary = resolve_repo_path(
            repo,
            f"{session_id}/SUMMARY.md",
            field_name="session_id",
        )
        abs_session_summary.parent.mkdir(parents=True, exist_ok=True)

        today = today_str()
        fm_dict = {
            "session": session_id,
            "date": today,
            "trust": "medium",
            "source": "agent-generated",
        }
        topics = [t.strip() for t in key_topics.split(",") if t.strip()]
        if topics:
            fm_dict["key_topics"] = topics

        import frontmatter as fmlib
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
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"session_id": session_id},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_create_plan
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_create_plan",
        annotations={
            "title": "Create Research Plan",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_create_plan(
        plan_id: str,
        title: str,
        description: str,
        content: str,
        next_action: str,
        session_id: str,
        plan_type: str = "research-plan",
    ) -> str:
        """Create a new plan file and add it to plans/SUMMARY.md.

        Args:
            plan_id:     Kebab-case identifier → plans/{plan_id}.md.
            title:       Human-readable plan title.
            description: One-line description for plans/SUMMARY.md.
            content:     Full plan body (without frontmatter — added here).
            next_action: First action to take (written to frontmatter).
            session_id:  Current session path for origin_session frontmatter.
            plan_type:   Plan type (default: 'research-plan').

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import ValidationError
        from ..frontmatter_utils import append_plan_to_summary, build_plan_summary_block, today_str
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        validate_session_id(session_id)
        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if abs_plan.exists():
            raise ValidationError(
                f"Plan already exists: {plan_path}. "
                "Use memory_write to overwrite, or choose a different plan_id."
            )

        today = today_str()
        fm_dict = {
            "source": "agent-generated",
            "type": plan_type,
            "created": today,
            "last_verified": today,
            "trust": "medium",
            "status": "active",
            "next_action": next_action,
            "origin_session": session_id,
        }

        import frontmatter as fmlib
        post = fmlib.Post(content, **fm_dict)
        abs_plan.parent.mkdir(parents=True, exist_ok=True)
        abs_plan.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(plan_path)

        files_changed = [plan_path]

        # Add to plans/SUMMARY.md
        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=title,
                status="active",
                trust="medium",
                next_action=next_action,
                plan_progress=(0, 0),
                description=description,
            )
            updated = append_plan_to_summary(summary_content, new_block)
            abs_summary.write_text(updated, encoding="utf-8")
            repo.add(summary_path)
            files_changed.append(summary_path)
        else:
            warnings.append(f"{summary_path} not found — plan entry not added to index.")

        commit_msg = f"[plan] Create {plan_id}"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"plan_path": plan_path, "status": "active"},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_update_plan_next_action
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_update_plan_next_action",
        annotations={
            "title": "Update Plan Next Action",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_update_plan_next_action(
        plan_id: str,
        next_action: str,
        version_token: str | None = None,
    ) -> str:
        """Update only next_action and last_verified in a plan's frontmatter.

        Lighter-weight than memory_mark_plan_item_complete — use this to
        manually adjust the next_action pointer without completing an item.
        Also syncs the plans/SUMMARY.md entry.

        Args:
            plan_id:       Plan identifier (without .md).
            next_action:   New next_action string.
            version_token: Optional version token.

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import NotFoundError
        from ..frontmatter_utils import (
            build_plan_summary_block,
            parse_plan_items,
            read_with_frontmatter,
            replace_begin_end_block,
            today_str,
        )
        from ..models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings = []

        plan_path = _plan_path(plan_id)
        abs_plan = repo.abs_path(plan_path)
        if not abs_plan.exists():
            raise NotFoundError(f"Plan not found: {plan_path}")

        repo.check_version_token(plan_path, version_token)

        # Update frontmatter only
        import frontmatter as fmlib
        text = abs_plan.read_text(encoding="utf-8")
        post = fmlib.loads(text)
        post.metadata["next_action"] = next_action
        post.metadata["last_verified"] = today_str()
        abs_plan.write_text(fmlib.dumps(post), encoding="utf-8")
        repo.add(plan_path)

        files_changed = [plan_path]

        # Sync SUMMARY.md
        summary_path = "plans/SUMMARY.md"
        abs_summary = root / summary_path
        if abs_summary.exists():
            summary_content = abs_summary.read_text(encoding="utf-8")
            content = abs_plan.read_text(encoding="utf-8")
            phases = parse_plan_items(content)
            plan_done = sum(
                1 for ph in phases for it in ph["items"] if it["done"]
            )
            plan_total = sum(ph["total"] for ph in phases)
            fm_dict, _ = read_with_frontmatter(abs_plan)

            new_block = build_plan_summary_block(
                plan_id=plan_id,
                title=plan_id,
                status=fm_dict.get("status", "active"),
                trust=fm_dict.get("trust", "medium"),
                next_action=next_action,
                plan_progress=(plan_done, plan_total),
            )
            updated = replace_begin_end_block(summary_content, plan_id, new_block)
            if updated is None:
                warnings.append(f"BEGIN/END anchor for '{plan_id}' not found in {summary_path}.")
            else:
                abs_summary.write_text(updated, encoding="utf-8")
                repo.add(summary_path)
                files_changed.append(summary_path)

        commit_msg = f"[plan] Update next-action for {plan_id}"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=files_changed,
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"next_action": next_action},
            warnings=warnings,
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_flag_for_review
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_flag_for_review",
        annotations={
            "title": "Flag File for Review",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
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
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=[review_queue_rel],
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"flagged_path": path, "priority": priority},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_log_access
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_log_access",
        annotations={
            "title": "Log Memory File Access",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
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
            raise ValidationError(
                f"helpfulness must be between 0.0 and 1.0, got {helpfulness}"
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
        updated = (existing.rstrip("\n") + "\n" + new_line + "\n") if existing.strip() else new_line + "\n"
        abs_access.write_text(updated, encoding="utf-8")
        repo.add(access_jsonl)

        entry_count = updated.count("\n")
        commit_msg = f"[access] Log retrieval of {Path(file).name} (h={entry['helpfulness']:.1f})"
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=[access_jsonl],
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"access_jsonl": access_jsonl, "entry_count": entry_count},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_list_plans
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_list_plans",
        annotations={
            "title": "List Memory Plans",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_list_plans(
        status: str | None = None,
    ) -> str:
        """List all plans in the plans/ directory with their frontmatter metadata.

        Reads frontmatter from each .md file in plans/ (excluding SUMMARY.md and
        _archive/) and returns structured plan metadata.

        Args:
            status: Optional filter — 'active', 'complete', 'paused', etc.
                    If omitted all plans are returned.

        Returns:
            JSON list of plan objects, each with keys: plan_id, status, trust,
            next_action, created, last_verified. Sorted active-first, then by id.
        """
        import json as _json

        from ..frontmatter_utils import read_with_frontmatter

        root = get_root()
        plans_dir = root / "plans"
        if not plans_dir.is_dir():
            return _json.dumps([])

        plans = []
        for plan_file in sorted(plans_dir.glob("*.md")):
            if plan_file.name in ("SUMMARY.md",):
                continue
            try:
                fm, _ = read_with_frontmatter(plan_file)
            except Exception:
                fm = {}
            plan_id = plan_file.stem
            plan_status = fm.get("status", "unknown")
            if status is not None and plan_status != status:
                continue
            plans.append({
                "plan_id": plan_id,
                "status": plan_status,
                "trust": fm.get("trust", "unknown"),
                "next_action": fm.get("next_action", ""),
                "created": str(fm.get("created", "")),
                "last_verified": str(fm.get("last_verified", "")),
            })

        # Sort: active first, then alphabetically by plan_id
        plans.sort(key=lambda p: (0 if p["status"] == "active" else 1, p["plan_id"]))
        return _json.dumps(plans, indent=2)

    # ------------------------------------------------------------------
    # memory_record_reflection
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_record_reflection",
        annotations={
            "title": "Record Session Reflection",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
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
        sha = repo.commit(commit_msg)

        result = MemoryWriteResult(
            files_changed=[reflection_rel],
            commit_sha=sha,
            commit_message=commit_msg,
            new_state={"reflection_path": reflection_rel},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_revert_commit
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_revert_commit",
        annotations={
            "title": "Revert a Memory Commit",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_revert_commit(
        sha: str,
    ) -> str:
        """Create a revert commit that undoes the changes introduced by *sha*.

        Uses 'git revert --no-edit' — creates a new commit that inverts the
        target commit. Does not amend or delete history; the original commit
        and the revert commit both remain in the log.

        Use memory_git_log first to identify the commit SHA you want to revert.

        Args:
            sha: Full or abbreviated commit SHA to revert.

        Returns:
            MemoryWriteResult JSON with the new revert commit SHA.
        """
        import re as _re

        from ..errors import ValidationError
        from ..models import MemoryWriteResult

        if not _re.fullmatch(r"[0-9a-f]{4,64}", sha, _re.IGNORECASE):
            raise ValidationError(
                f"Invalid SHA: {sha!r}. Must be a 4–64 character hex string."
            )

        repo = get_repo()
        new_sha = repo.revert(sha)

        result = MemoryWriteResult(
            files_changed=[],
            commit_sha=new_sha,
            commit_message=f"Revert {sha}",
            new_state={"reverted_sha": sha, "new_sha": new_sha},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_reset_session_state
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_reset_session_state",
        annotations={
            "title": "Reset Per-Session State",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
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
        _session_state["identity_updates"] = 0
        return _json.dumps({
            "reset": True,
            "identity_updates_this_session": 0,
        })

    return {
        "memory_mark_plan_item_complete": memory_mark_plan_item_complete,
        "memory_promote_knowledge": memory_promote_knowledge,
        "memory_demote_knowledge": memory_demote_knowledge,
        "memory_archive_knowledge": memory_archive_knowledge,
        "memory_add_knowledge_file": memory_add_knowledge_file,
        "memory_append_scratchpad": memory_append_scratchpad,
        "memory_update_identity_trait": memory_update_identity_trait,
        "memory_record_chat_summary": memory_record_chat_summary,
        "memory_create_plan": memory_create_plan,
        "memory_update_plan_next_action": memory_update_plan_next_action,
        "memory_flag_for_review": memory_flag_for_review,
        "memory_log_access": memory_log_access,
        "memory_list_plans": memory_list_plans,
        "memory_record_reflection": memory_record_reflection,
        "memory_revert_commit": memory_revert_commit,
        "memory_reset_session_state": memory_reset_session_state,
    }
