"""Knowledge-oriented semantic tools."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ...path_policy import (
    forbid_prefix,
    require_under_prefix,
    resolve_repo_path,
    validate_session_id,
    validate_top_level_root,
)


if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _tool_annotations(**kwargs: object) -> Any:
    return cast(Any, kwargs)


def register_tools(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register knowledge-oriented semantic tools."""

    @mcp.tool(
        name="memory_promote_knowledge",
        annotations=_tool_annotations(
            title="Promote Knowledge File to Verified",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_promote_knowledge(
        source_path: str,
        trust_level: str = "high",
        target_path: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a file from knowledge/_unverified/ to knowledge/, updating trust."""
        from ...errors import NotFoundError, ValidationError
        from ...frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        source_path, abs_source = resolve_repo_path(repo, source_path, field_name="source_path")
        require_under_prefix(source_path, "knowledge/_unverified", field_name="source_path")
        if trust_level not in ("medium", "high"):
            raise ValidationError(f"trust_level must be 'medium' or 'high', got: {trust_level}")

        if not abs_source.exists():
            raise NotFoundError(f"Source file not found: {source_path}")

        repo.check_version_token(source_path, version_token)

        if target_path is None:
            target_path = source_path.replace("knowledge/_unverified/", "knowledge/", 1)
        target_path, _ = resolve_repo_path(repo, target_path, field_name="target_path")
        validate_top_level_root(
            target_path,
            allowed_roots=("knowledge",),
            field_name="target_path",
        )
        forbid_prefix(target_path, "knowledge/_unverified", field_name="target_path")

        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["trust"] = trust_level
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        abs_target = repo.abs_path(target_path)
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, target_path)

        files_changed = [source_path, target_path]

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

        target_section_id = infer_section_id_from_path(target_path)
        target_summary_path = "knowledge/SUMMARY.md"
        abs_tgt_summary = root / target_summary_path
        if abs_tgt_summary.exists():
            tgt_summary = abs_tgt_summary.read_text(encoding="utf-8")
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
        commit_msg = f"[curation] Promote {filename} to knowledge/{subject}/ (trust: {trust_level})"
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"new_path": target_path, "trust": trust_level},
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_demote_knowledge",
        annotations=_tool_annotations(
            title="Demote Knowledge File to Unverified",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_demote_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a verified knowledge file back to _unverified/ with trust: low."""
        from ...errors import NotFoundError, ValidationError
        from ...frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

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

        target_path = source_path.replace("knowledge/", "knowledge/_unverified/", 1)
        filename = Path(source_path).name
        section_id = infer_section_id_from_path(source_path)

        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["trust"] = "low"
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        abs_target = repo.abs_path(target_path)
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, target_path)

        files_changed = [source_path, target_path]

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
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"new_path": target_path, "trust": "low"},
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_archive_knowledge",
        annotations=_tool_annotations(
            title="Archive Knowledge File",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_archive_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a knowledge file to knowledge/_archive/ and mark it archived."""
        from ...errors import NotFoundError
        from ...frontmatter_utils import (
            infer_section_id_from_path,
            read_with_frontmatter,
            remove_entry_from_section,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

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
        rel_to_knowledge = source_path[len("knowledge/") :]
        if rel_to_knowledge.startswith("_unverified/"):
            rel_to_knowledge = rel_to_knowledge[len("_unverified/") :]
        archive_path = f"knowledge/_archive/{rel_to_knowledge}"

        fm_dict, body = read_with_frontmatter(abs_source)
        fm_dict["status"] = "archived"
        fm_dict["last_verified"] = today_str()
        write_with_frontmatter(abs_source, fm_dict, body)
        repo.add(source_path)

        abs_archive = repo.abs_path(archive_path)
        abs_archive.parent.mkdir(parents=True, exist_ok=True)
        repo.mv(source_path, archive_path)

        files_changed = [source_path, archive_path]

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
        commit_result = repo.commit(commit_msg)

        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"archive_path": archive_path},
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_add_knowledge_file",
        annotations=_tool_annotations(
            title="Add Knowledge File to Unverified",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_add_knowledge_file(
        path: str,
        content: str,
        source: str,
        session_id: str,
        trust: str = "low",
        summary_entry: str | None = None,
    ) -> str:
        """Create a new knowledge file with correct frontmatter and SUMMARY entry."""
        from ...errors import ValidationError
        from ...frontmatter_utils import (
            infer_section_id_from_path,
            insert_entry_in_section,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

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
            raise ValidationError(f"File already exists: {path}. Use memory_write to overwrite.")

        today = today_str()
        fm_dict = {
            "source": source,
            "created": today,
            "trust": "low",
            "origin_session": session_id,
        }

        abs_path.parent.mkdir(parents=True, exist_ok=True)
        write_with_frontmatter(abs_path, fm_dict, content)
        repo.add(path)

        if summary_entry is None:
            h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            summary_entry = h1_match.group(1).strip() if h1_match else Path(path).stem

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
        commit_result = repo.commit(commit_msg)

        new_token = repo.hash_object(path)
        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={"version_token": new_token},
            warnings=warnings,
        )
        return result.to_json()

    return {
        "memory_promote_knowledge": memory_promote_knowledge,
        "memory_demote_knowledge": memory_demote_knowledge,
        "memory_archive_knowledge": memory_archive_knowledge,
        "memory_add_knowledge_file": memory_add_knowledge_file,
    }


__all__ = ["register_tools"]
