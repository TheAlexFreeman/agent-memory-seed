"""Knowledge-oriented semantic tools."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from datetime import datetime, timezone
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


_MAX_BATCH_PROMOTIONS = 50
_REVIEW_VERDICTS = frozenset({"approve", "reject", "defer"})


@dataclass(frozen=True)
class _GovernedKnowledgeOperationMeta:
    name: str
    title: str
    change_class: str = "proposed"
    commit_category: str = "curation"


_PROMOTE_BATCH_META = _GovernedKnowledgeOperationMeta(
    name="memory_promote_knowledge_batch",
    title="Promote Knowledge Files In Batch",
)
_PROMOTE_SUBTREE_META = _GovernedKnowledgeOperationMeta(
    name="memory_promote_knowledge_subtree",
    title="Promote Knowledge Subtree",
)
_PROMOTE_SINGLE_META = _GovernedKnowledgeOperationMeta(
    name="memory_promote_knowledge",
    title="Promote Knowledge File to Verified",
)
_DEMOTE_META = _GovernedKnowledgeOperationMeta(
    name="memory_demote_knowledge",
    title="Demote Knowledge File to Unverified",
)
_ARCHIVE_META = _GovernedKnowledgeOperationMeta(
    name="memory_archive_knowledge",
    title="Archive Knowledge File",
)
_ADD_META = _GovernedKnowledgeOperationMeta(
    name="memory_add_knowledge_file",
    title="Add Knowledge File to Unverified",
    change_class="automatic",
    commit_category="knowledge",
)


def _governed_knowledge_annotations(meta: _GovernedKnowledgeOperationMeta) -> Any:
    return _tool_annotations(
        title=meta.title,
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    )


def _normalize_batch_source_paths(raw_source_paths: str, repo, root: Path) -> list[str]:
    from ...errors import ValidationError

    if not isinstance(raw_source_paths, str) or not raw_source_paths.strip():
        raise ValidationError("source_paths must be a non-empty string")

    stripped = raw_source_paths.strip()
    if stripped.startswith("["):
        import json

        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"source_paths must be a valid JSON array or folder path: {exc}")
        if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
            raise ValidationError("source_paths JSON form must be an array of repo-relative paths")
        return [resolve_repo_path(repo, item, field_name="source_paths")[0] for item in parsed]

    normalized_path, abs_path = resolve_repo_path(repo, stripped, field_name="source_paths")
    if abs_path.is_dir() or normalized_path.endswith("/"):
        folder = abs_path if abs_path.is_dir() else (root / normalized_path)
        paths = [
            child.relative_to(root).as_posix()
            for child in sorted(folder.glob("*.md"))
            if child.name != "SUMMARY.md"
        ]
        if not paths:
            raise ValidationError(
                f"No promotable markdown files found in folder: {normalized_path}"
            )
        return paths

    return [normalized_path]


def _prune_empty_summary_section(summary_content: str, section_id: str) -> str:
    from ...frontmatter_utils import find_section_bounds

    bounds = find_section_bounds(summary_content, section_id)
    if bounds is None:
        return summary_content

    lines = summary_content.splitlines(keepends=True)
    anchor_idx, end_idx = bounds
    section_body = [line for line in lines[anchor_idx + 1 : end_idx] if line.strip()]
    if any(line.lstrip().startswith("-") for line in section_body):
        return summary_content

    remove_end = end_idx
    while remove_end < len(lines) and not lines[remove_end].strip():
        remove_end += 1
    return "".join(lines[:anchor_idx] + lines[remove_end:])


def _summary_section_heading(section_id: str) -> str:
    words = [part for part in re.split(r"[-_]", section_id) if part]
    if not words:
        return "Misc"
    return " ".join(word.capitalize() for word in words)


def _append_summary_section(content: str, section_id: str, entry: str) -> str:
    stripped = content.rstrip()
    if stripped.endswith("---"):
        stripped = stripped[:-3].rstrip()

    block = f"<!-- section: {section_id} -->\n### {_summary_section_heading(section_id)}\n{entry}\n"
    if stripped:
        return f"{stripped}\n\n{block}\n---\n"
    return f"{block}\n---\n"


def _update_summary_with_entry(
    content: str,
    section_id: str,
    entry: str,
    *,
    allow_section_create: bool,
) -> tuple[str | None, bool]:
    from ...frontmatter_utils import insert_entry_in_section

    updated = insert_entry_in_section(content, section_id, entry)
    if updated is not None:
        return updated, False
    if not allow_section_create:
        return None, False
    return _append_summary_section(content, section_id, entry), True


def _default_summary_entry(filename: str, target_path: str, frontmatter: dict[str, Any]) -> str:
    title = frontmatter.get("title", filename.replace(".md", "").replace("-", " ").title())
    return f"- **[{filename}]({target_path})** — {title}"


def _update_source_summary_after_promotion(
    summary_content: str,
    source_summary_path: str,
    source_path: str,
    filename: str,
    warnings: list[str],
) -> str:
    from ...frontmatter_utils import infer_section_id_from_path, remove_entry_from_section

    source_section_id = infer_section_id_from_path(source_path)
    updated_source = remove_entry_from_section(summary_content, source_section_id, filename)
    if updated_source is None:
        warnings.append(
            f"Section '<!-- section: {source_section_id} -->' not found in {source_summary_path}."
        )
        return summary_content
    return _prune_empty_summary_section(updated_source, source_section_id)


def _update_target_summary_after_promotion(
    summary_content: str,
    target_summary_path: str,
    target_path: str,
    filename: str,
    frontmatter: dict[str, Any],
    warnings: list[str],
    *,
    summary_entry: str | None = None,
    allow_section_create: bool,
) -> str:
    from ...frontmatter_utils import infer_section_id_from_path

    target_section_id = infer_section_id_from_path(target_path)
    entry = summary_entry or _default_summary_entry(filename, target_path, frontmatter)
    updated_target, _ = _update_summary_with_entry(
        summary_content,
        target_section_id,
        entry,
        allow_section_create=allow_section_create,
    )
    if updated_target is None:
        warnings.append(
            f"Section '<!-- section: {target_section_id} -->' not found in {target_summary_path}. "
            "Entry not added — add manually."
        )
        return summary_content
    return updated_target


def _review_log_path(folder_path: str = "knowledge/_unverified") -> str:
    return f"{folder_path.rstrip('/')}/REVIEW_LOG.jsonl"


def _read_review_log_entries(abs_path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    if not abs_path.exists():
        return entries
    for raw_line in abs_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        try:
            parsed = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def register_tools(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register knowledge-oriented semantic tools."""

    @mcp.tool(
        name="memory_promote_knowledge_batch",
        annotations=_governed_knowledge_annotations(_PROMOTE_BATCH_META),
    )
    async def memory_promote_knowledge_batch(
        source_paths: str,
        trust_level: str = "medium",
        target_folder: str | None = None,
    ) -> str:
        """Promote multiple unverified knowledge files in one governed commit.

        Use this when several reviewed files should move together. Accepts either
        a JSON array of repo-relative paths or a folder path to expand into a
        flat batch. Missing target sections in knowledge/SUMMARY.md are
        auto-created with default entries so routine promotion work stays
        atomic.

        Prefer memory_promote_knowledge_subtree when the source is a nested topic
        tree whose internal subfolders should be preserved.
        """
        from ...errors import NotFoundError, ValidationError
        from ...frontmatter_utils import (
            read_with_frontmatter,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        if trust_level not in ("medium", "high"):
            raise ValidationError(f"trust_level must be 'medium' or 'high', got: {trust_level}")

        normalized_source_paths = _normalize_batch_source_paths(source_paths, repo, root)
        if len(normalized_source_paths) > _MAX_BATCH_PROMOTIONS:
            raise ValidationError(
                f"source_paths may contain at most {_MAX_BATCH_PROMOTIONS} files per batch"
            )

        explicit_target_folder: str | None = None
        if target_folder is not None:
            explicit_target_folder, _ = resolve_repo_path(
                repo, target_folder, field_name="target_folder"
            )
            validate_top_level_root(
                explicit_target_folder,
                allowed_roots=("knowledge",),
                field_name="target_folder",
            )
            forbid_prefix(
                explicit_target_folder,
                "knowledge/_unverified",
                field_name="target_folder",
            )

        seen_sources: set[str] = set()
        seen_targets: set[str] = set()
        inferred_target_folders: set[str] = set()
        validation_errors: list[str] = []
        prepared_files: list[dict[str, Any]] = []

        for source_path in normalized_source_paths:
            try:
                if source_path in seen_sources:
                    raise ValidationError(f"duplicate source path in batch: {source_path}")
                seen_sources.add(source_path)

                source_path, abs_source = resolve_repo_path(
                    repo, source_path, field_name="source_path"
                )
                require_under_prefix(source_path, "knowledge/_unverified", field_name="source_path")
                if source_path.endswith("/SUMMARY.md") or Path(source_path).name == "SUMMARY.md":
                    raise ValidationError(f"Cannot batch-promote SUMMARY.md: {source_path}")
                if not abs_source.exists():
                    raise NotFoundError(f"Source file not found: {source_path}")

                inferred_folder = Path(
                    source_path.replace("knowledge/_unverified/", "knowledge/", 1)
                ).parent.as_posix()
                inferred_target_folders.add(inferred_folder)
                resolved_target_folder = explicit_target_folder or inferred_folder
                target_path = f"{resolved_target_folder.rstrip('/')}/{abs_source.name}"
                target_path, abs_target = resolve_repo_path(
                    repo, target_path, field_name="target_path"
                )
                validate_top_level_root(
                    target_path,
                    allowed_roots=("knowledge",),
                    field_name="target_path",
                )
                forbid_prefix(target_path, "knowledge/_unverified", field_name="target_path")
                if target_path in seen_targets:
                    raise ValidationError(f"target path collision in batch: {target_path}")
                seen_targets.add(target_path)
                if abs_target.exists():
                    raise ValidationError(f"Target already exists: {target_path}")

                fm_dict, body = read_with_frontmatter(abs_source)
                prepared_files.append(
                    {
                        "source_path": source_path,
                        "abs_source": abs_source,
                        "target_path": target_path,
                        "filename": abs_source.name,
                        "frontmatter": fm_dict,
                        "body": body,
                    }
                )
            except Exception as exc:
                validation_errors.append(f"{source_path}: {exc}")

        if target_folder is None and len(inferred_target_folders) > 1:
            validation_errors.append(
                "source_paths span multiple inferred target folders; provide target_folder explicitly"
            )

        if validation_errors:
            raise ValidationError(
                "Batch promotion validation failed:\n"
                + "\n".join(f"- {msg}" for msg in validation_errors)
            )

        resolved_target_folder = explicit_target_folder or next(iter(inferred_target_folders))
        today = today_str()
        files_changed: list[str] = []
        promoted_files: list[str] = []

        source_summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_source_summary = root / source_summary_path
        source_summary_content = (
            abs_source_summary.read_text(encoding="utf-8") if abs_source_summary.exists() else None
        )

        target_summary_path = "knowledge/SUMMARY.md"
        abs_target_summary = root / target_summary_path
        target_summary_content = (
            abs_target_summary.read_text(encoding="utf-8") if abs_target_summary.exists() else None
        )

        for prepared in prepared_files:
            source_path = cast(str, prepared["source_path"])
            abs_source = cast(Path, prepared["abs_source"])
            target_path = cast(str, prepared["target_path"])
            filename = cast(str, prepared["filename"])
            fm_dict = cast(dict[str, Any], prepared["frontmatter"])
            body = cast(str, prepared["body"])

            fm_dict["trust"] = trust_level
            fm_dict["last_verified"] = today
            write_with_frontmatter(abs_source, fm_dict, body)
            repo.add(source_path)

            abs_target = repo.abs_path(target_path)
            abs_target.parent.mkdir(parents=True, exist_ok=True)
            repo.mv(source_path, target_path)
            files_changed.extend([source_path, target_path])
            promoted_files.append(filename)

            if source_summary_content is not None:
                source_summary_content = _update_source_summary_after_promotion(
                    source_summary_content,
                    source_summary_path,
                    source_path,
                    filename,
                    warnings,
                )

            if target_summary_content is not None:
                target_summary_content = _update_target_summary_after_promotion(
                    target_summary_content,
                    target_summary_path,
                    target_path,
                    filename,
                    fm_dict,
                    warnings,
                    allow_section_create=True,
                )

        summary_updates: list[str] = []
        if source_summary_content is not None and abs_source_summary.exists():
            abs_source_summary.write_text(source_summary_content, encoding="utf-8")
            repo.add(source_summary_path)
            files_changed.append(source_summary_path)
            summary_updates.append(source_summary_path)

        if target_summary_content is not None and abs_target_summary.exists():
            abs_target_summary.write_text(target_summary_content, encoding="utf-8")
            repo.add(target_summary_path)
            files_changed.append(target_summary_path)
            summary_updates.append(target_summary_path)

        files_changed = list(dict.fromkeys(files_changed))
        summary_updates = list(dict.fromkeys(summary_updates))
        promoted_files = sorted(promoted_files)

        commit_msg = (
            f"[curation] Batch promote {len(prepared_files)} files to "
            f"{resolved_target_folder} (trust: {trust_level})"
        )
        commit_result = repo.commit(commit_msg)
        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={
                "promoted_count": len(prepared_files),
                "target_folder": resolved_target_folder,
                "trust": trust_level,
                "promoted_files": promoted_files,
                "summary_updates": summary_updates,
            },
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_promote_knowledge_subtree",
        annotations=_governed_knowledge_annotations(_PROMOTE_SUBTREE_META),
    )
    async def memory_promote_knowledge_subtree(
        source_folder: str,
        dest_folder: str,
        trust_level: str = "medium",
        reason: str = "",
        dry_run: bool = False,
    ) -> str:
        """Promote an entire unverified knowledge subtree in one governed commit.

        Use this when a full topic tree should move together and nested paths
        must be preserved. The tool validates the whole subtree before moving
        anything, supports dry-run previews, and auto-creates missing target
        sections in knowledge/SUMMARY.md with default entries.

        Prefer this over memory_promote_knowledge_batch when the source is a
        nested folder hierarchy rather than a flat batch.
        """
        from ...errors import NotFoundError, ValidationError
        from ...frontmatter_utils import (
            read_with_frontmatter,
            today_str,
            write_with_frontmatter,
        )
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()
        warnings: list[str] = []

        if trust_level not in ("medium", "high"):
            raise ValidationError(f"trust_level must be 'medium' or 'high', got: {trust_level}")

        source_folder, abs_source_folder = resolve_repo_path(
            repo, source_folder, field_name="source_folder"
        )
        require_under_prefix(source_folder, "knowledge/_unverified", field_name="source_folder")
        if not abs_source_folder.exists():
            raise NotFoundError(f"Source folder not found: {source_folder}")
        if not abs_source_folder.is_dir():
            raise ValidationError(f"source_folder must be a directory: {source_folder}")

        dest_folder, _ = resolve_repo_path(repo, dest_folder, field_name="dest_folder")
        validate_top_level_root(dest_folder, allowed_roots=("knowledge",), field_name="dest_folder")
        forbid_prefix(dest_folder, "knowledge/_unverified", field_name="dest_folder")

        markdown_files = [
            child
            for child in sorted(abs_source_folder.rglob("*.md"))
            if child.is_file() and child.name != "SUMMARY.md"
        ]
        if not markdown_files:
            raise ValidationError(f"No promotable markdown files found in folder: {source_folder}")
        if len(markdown_files) > _MAX_BATCH_PROMOTIONS:
            raise ValidationError(
                f"source_folder may contain at most {_MAX_BATCH_PROMOTIONS} files per subtree promotion"
            )

        validation_errors: list[str] = []
        seen_targets: set[str] = set()
        prepared_files: list[dict[str, Any]] = []

        for abs_source in markdown_files:
            source_path = abs_source.relative_to(root).as_posix()
            rel_subpath = abs_source.relative_to(abs_source_folder).as_posix()
            target_path = f"{dest_folder.rstrip('/')}/{rel_subpath}"
            try:
                target_path, abs_target = resolve_repo_path(
                    repo, target_path, field_name="target_path"
                )
                validate_top_level_root(
                    target_path,
                    allowed_roots=("knowledge",),
                    field_name="target_path",
                )
                forbid_prefix(target_path, "knowledge/_unverified", field_name="target_path")
                if target_path in seen_targets:
                    raise ValidationError(f"target path collision in subtree: {target_path}")
                seen_targets.add(target_path)
                if abs_target.exists():
                    raise ValidationError(f"Target already exists: {target_path}")

                fm_dict, body = read_with_frontmatter(abs_source)
                missing = [key for key in ("created", "source", "trust") if not fm_dict.get(key)]
                if missing:
                    raise ValidationError(
                        f"missing required frontmatter fields: {', '.join(missing)}"
                    )
                prepared_files.append(
                    {
                        "source_path": source_path,
                        "abs_source": abs_source,
                        "target_path": target_path,
                        "filename": abs_source.name,
                        "frontmatter": fm_dict,
                        "body": body,
                        "relative_subpath": rel_subpath,
                    }
                )
            except Exception as exc:
                validation_errors.append(f"{source_path}: {exc}")

        if validation_errors:
            raise ValidationError(
                "Subtree promotion validation failed:\n"
                + "\n".join(f"- {msg}" for msg in validation_errors)
            )

        planned_moves = [
            {
                "source_path": cast(str, prepared["source_path"]),
                "target_path": cast(str, prepared["target_path"]),
            }
            for prepared in prepared_files
        ]
        if dry_run:
            return json.dumps(
                {
                    "source_folder": source_folder,
                    "dest_folder": dest_folder,
                    "dry_run": True,
                    "promoted_count": len(prepared_files),
                    "planned_moves": planned_moves,
                    "trust": trust_level,
                },
                indent=2,
            )

        today = today_str()
        files_changed: list[str] = []
        promoted_files: list[str] = []

        source_summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_source_summary = root / source_summary_path
        source_summary_content = (
            abs_source_summary.read_text(encoding="utf-8") if abs_source_summary.exists() else None
        )

        target_summary_path = "knowledge/SUMMARY.md"
        abs_target_summary = root / target_summary_path
        target_summary_content = (
            abs_target_summary.read_text(encoding="utf-8") if abs_target_summary.exists() else None
        )

        for prepared in prepared_files:
            source_path = cast(str, prepared["source_path"])
            abs_source = cast(Path, prepared["abs_source"])
            target_path = cast(str, prepared["target_path"])
            filename = cast(str, prepared["filename"])
            fm_dict = cast(dict[str, Any], prepared["frontmatter"])
            body = cast(str, prepared["body"])

            fm_dict["trust"] = trust_level
            fm_dict["last_verified"] = today
            write_with_frontmatter(abs_source, fm_dict, body)
            repo.add(source_path)

            abs_target = repo.abs_path(target_path)
            abs_target.parent.mkdir(parents=True, exist_ok=True)
            repo.mv(source_path, target_path)
            files_changed.extend([source_path, target_path])
            promoted_files.append(filename)

            if source_summary_content is not None:
                source_summary_content = _update_source_summary_after_promotion(
                    source_summary_content,
                    source_summary_path,
                    source_path,
                    filename,
                    warnings,
                )

            if target_summary_content is not None:
                target_summary_content = _update_target_summary_after_promotion(
                    target_summary_content,
                    target_summary_path,
                    target_path,
                    filename,
                    fm_dict,
                    warnings,
                    allow_section_create=True,
                )

        summary_updates: list[str] = []
        if source_summary_content is not None and abs_source_summary.exists():
            abs_source_summary.write_text(source_summary_content, encoding="utf-8")
            repo.add(source_summary_path)
            files_changed.append(source_summary_path)
            summary_updates.append(source_summary_path)

        if target_summary_content is not None and abs_target_summary.exists():
            abs_target_summary.write_text(target_summary_content, encoding="utf-8")
            repo.add(target_summary_path)
            files_changed.append(target_summary_path)
            summary_updates.append(target_summary_path)

        files_changed = list(dict.fromkeys(files_changed))
        summary_updates = list(dict.fromkeys(summary_updates))
        promoted_files = sorted(promoted_files)

        reason_str = f"; reason: {reason}" if reason else ""
        commit_msg = (
            f"[curation] Promote subtree {source_folder} -> {dest_folder} "
            f"({len(prepared_files)} files, trust: {trust_level}{reason_str})"
        )
        commit_result = repo.commit(commit_msg)
        result = MemoryWriteResult.from_commit(
            files_changed=files_changed,
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={
                "source_folder": source_folder,
                "target_folder": dest_folder,
                "promoted_count": len(prepared_files),
                "trust": trust_level,
                "promoted_files": promoted_files,
                "planned_moves": planned_moves,
                "summary_updates": summary_updates,
                "dry_run": False,
            },
            warnings=warnings,
        )
        return result.to_json()

    @mcp.tool(
        name="memory_promote_knowledge",
        annotations=_governed_knowledge_annotations(_PROMOTE_SINGLE_META),
    )
    async def memory_promote_knowledge(
        source_path: str,
        trust_level: str = "high",
        target_path: str | None = None,
        summary_entry: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move one file from knowledge/_unverified/ to knowledge/, updating trust.

        Use this for one-off promotions after a review decision. When
        summary_entry is provided, knowledge/SUMMARY.md is auto-updated even if
        the target section is missing: a stub section is appended and the entry
        is inserted there. Without summary_entry, missing target sections still
        produce a warning so callers can repair SUMMARY.md manually.

        See also: memory_promote_knowledge_batch to promote multiple files in one
        call, and memory_promote_knowledge_subtree to promote an entire folder tree.
        """
        from ...errors import NotFoundError, ValidationError
        from ...frontmatter_utils import (
            infer_section_id_from_path,
            read_with_frontmatter,
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

        source_summary_path = "knowledge/_unverified/SUMMARY.md"
        abs_src_summary = root / source_summary_path
        if abs_src_summary.exists():
            src_summary = abs_src_summary.read_text(encoding="utf-8")
            updated = _update_source_summary_after_promotion(
                src_summary,
                source_summary_path,
                source_path,
                filename,
                warnings,
            )
            abs_src_summary.write_text(updated, encoding="utf-8")
            repo.add(source_summary_path)
            files_changed.append(source_summary_path)

        target_summary_path = "knowledge/SUMMARY.md"
        abs_tgt_summary = root / target_summary_path
        if abs_tgt_summary.exists():
            tgt_summary = abs_tgt_summary.read_text(encoding="utf-8")
            updated = _update_target_summary_after_promotion(
                tgt_summary,
                target_summary_path,
                target_path,
                filename,
                fm_dict,
                warnings,
                summary_entry=summary_entry,
                allow_section_create=summary_entry is not None,
            )
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
        annotations=_governed_knowledge_annotations(_DEMOTE_META),
    )
    async def memory_demote_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a verified knowledge file back to _unverified/ with trust: low.

        Use this when a promoted file should re-enter the review queue. Prefer
        memory_archive_knowledge when the file should leave active review rather
        than be reconsidered.
        """
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
        annotations=_governed_knowledge_annotations(_ARCHIVE_META),
    )
    async def memory_archive_knowledge(
        source_path: str,
        reason: str | None = None,
        version_token: str | None = None,
    ) -> str:
        """Move a knowledge file to knowledge/_archive/ and mark it archived.

        Use this when content should leave the active retrieval path without
        being deleted from git history. Prefer demotion if the file still needs
        active review.
        """
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
        annotations=_governed_knowledge_annotations(_ADD_META),
    )
    async def memory_add_knowledge_file(
        path: str,
        content: str,
        source: str,
        session_id: str,
        trust: str = "low",
        summary_entry: str | None = None,
    ) -> str:
        """Create a new unverified knowledge file with frontmatter and SUMMARY entry.

        Use this for new material that has not yet been explicitly reviewed.
        The file is always written under knowledge/_unverified and indexed in
        the unverified summary when possible. Use a promotion tool only after
        review.
        """
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

    @mcp.tool(
        name="memory_mark_reviewed",
        annotations=_tool_annotations(
            title="Mark Unverified File Reviewed",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    async def memory_mark_reviewed(
        path: str,
        verdict: str,
        reviewer_notes: str = "",
        session_id: str = "",
    ) -> str:
        """Record a review verdict for an unverified knowledge file."""
        from ...errors import NotFoundError, ValidationError
        from ...models import MemoryWriteResult

        repo = get_repo()
        root = get_root()

        path, abs_path = resolve_repo_path(repo, path, field_name="path")
        require_under_prefix(path, "knowledge/_unverified", field_name="path")
        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")
        if verdict not in _REVIEW_VERDICTS:
            raise ValidationError(
                f"verdict must be one of {sorted(_REVIEW_VERDICTS)}, got: {verdict}"
            )
        if session_id:
            validate_session_id(session_id)

        log_path = _review_log_path()
        abs_log = root / log_path
        abs_log.parent.mkdir(parents=True, exist_ok=True)

        entry = {
            "path": path,
            "verdict": verdict,
            "reviewer_notes": reviewer_notes,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "reviewed_by": "agent",
        }
        with abs_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        repo.add(log_path)

        commit_msg = f"[curation] Mark {Path(path).name} reviewed ({verdict})"
        commit_result = repo.commit(commit_msg)
        result = MemoryWriteResult.from_commit(
            files_changed=[log_path],
            commit_result=commit_result,
            commit_message=commit_msg,
            new_state={
                "path": path,
                "verdict": verdict,
                "log_path": log_path,
                "session_id": session_id or None,
            },
        )
        return result.to_json()

    @mcp.tool(
        name="memory_list_pending_reviews",
        annotations=_tool_annotations(
            title="List Pending Review Verdicts",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    async def memory_list_pending_reviews(folder_path: str = "knowledge/_unverified") -> str:
        """List the latest pending review verdicts for unverified knowledge files."""
        from ...errors import ValidationError

        repo = get_repo()
        root = get_root()

        folder_path, abs_folder = resolve_repo_path(repo, folder_path, field_name="folder_path")
        if folder_path != "knowledge/_unverified":
            require_under_prefix(folder_path, "knowledge/_unverified", field_name="folder_path")
        if not abs_folder.exists() or not abs_folder.is_dir():
            raise ValidationError(f"folder_path must be an existing directory: {folder_path}")

        log_path = _review_log_path(folder_path)
        abs_log = root / log_path
        latest_by_path: dict[str, dict[str, Any]] = {}
        for entry in _read_review_log_entries(abs_log):
            entry_path = entry.get("path")
            if isinstance(entry_path, str):
                latest_by_path[entry_path] = entry

        grouped: dict[str, list[dict[str, Any]]] = {"approve": [], "defer": [], "reject": []}
        for entry_path, entry in latest_by_path.items():
            if not entry_path.startswith(folder_path.rstrip("/") + "/"):
                continue
            if not (root / entry_path).exists():
                continue
            verdict = entry.get("verdict")
            if verdict not in grouped:
                continue
            grouped[cast(str, verdict)].append(
                {
                    "path": entry_path,
                    "reviewer_notes": entry.get("reviewer_notes", ""),
                    "session_id": entry.get("session_id") or None,
                    "timestamp": entry.get("timestamp"),
                    "reviewed_by": entry.get("reviewed_by"),
                }
            )

        for verdict_entries in grouped.values():
            verdict_entries.sort(key=lambda item: str(item["path"]))

        return json.dumps(
            {
                "folder_path": folder_path,
                "log_path": log_path,
                "approve": grouped["approve"],
                "defer": grouped["defer"],
                "reject": grouped["reject"],
                "counts": {
                    "approve": len(grouped["approve"]),
                    "defer": len(grouped["defer"]),
                    "reject": len(grouped["reject"]),
                },
            },
            indent=2,
            default=str,
        )

    return {
        "memory_promote_knowledge_batch": memory_promote_knowledge_batch,
        "memory_promote_knowledge_subtree": memory_promote_knowledge_subtree,
        "memory_promote_knowledge": memory_promote_knowledge,
        "memory_demote_knowledge": memory_demote_knowledge,
        "memory_archive_knowledge": memory_archive_knowledge,
        "memory_add_knowledge_file": memory_add_knowledge_file,
        "memory_mark_reviewed": memory_mark_reviewed,
        "memory_list_pending_reviews": memory_list_pending_reviews,
    }


__all__ = ["register_tools"]
