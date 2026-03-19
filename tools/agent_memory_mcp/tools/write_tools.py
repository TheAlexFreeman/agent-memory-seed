"""
Tier 2 — Low-level write tools (staged, no auto-commit).

These replace raw Edit/Write/Bash calls for memory writes. All tools:
  - Accept an optional version_token for optimistic locking
  - Stage changes but do NOT commit (call memory_commit when ready)
  - Return MemoryWriteResult JSON
  - Support an optional delete-permission hook for runtimes that need it

Directory restrictions:
  memory_delete and memory_move SOURCE paths must target:
    knowledge/, plans/, scratchpad/
  Protected paths under identity/, meta/, chats/, and skills/ are rejected
  before any filesystem access.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING

from ..path_policy import resolve_repo_path, validate_raw_mutation_source

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# Commit-prefix validation set (for memory_commit)
_KNOWN_PREFIXES = {
    "[knowledge]", "[plan]", "[identity]", "[chat]",
    "[curation]", "[scratchpad]", "[system]",
}


def register(
    mcp: "FastMCP",
    get_repo,
    get_root,
    grant_delete_permission: Callable[[str], None] | None = None,
) -> dict[str, object]:
    """Register all Tier 2 low-level write tools and return their callables."""

    # ------------------------------------------------------------------
    # memory_write
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_write",
        annotations={
            "title": "Write Memory File",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_write(
        path: str,
        content: str,
        version_token: str | None = None,
        create_dirs: bool = True,
    ) -> str:
        """Create or overwrite a file and stage it (no auto-commit).

        Call memory_commit when all related writes are staged.

        Args:
            path:          Repo-relative path (e.g. 'knowledge/_unverified/django/foo.md').
            content:       Full file content to write.
            version_token: If provided, checked against the current file hash before
                           writing. Pass the token returned by memory_read_file to
                           detect concurrent modifications (ConflictError on mismatch).
            create_dirs:   Create parent directories if they don't exist (default: True).

        Returns:
            MemoryWriteResult JSON with new_state.version_token for the written file.
        """
        from ..errors import NotFoundError
        from ..models import MemoryWriteResult

        repo = get_repo()
        path, abs_path = resolve_repo_path(repo, path)

        if version_token is not None:
            if not abs_path.exists():
                raise NotFoundError(f"Cannot check version_token: {path} does not exist")
            repo.check_version_token(path, version_token)

        if create_dirs:
            abs_path.parent.mkdir(parents=True, exist_ok=True)

        abs_path.write_text(content, encoding="utf-8")
        repo.add(path)
        new_token = repo.hash_object(path)

        result = MemoryWriteResult(
            files_changed=[path],
            commit_sha=None,
            commit_message=None,
            new_state={"version_token": new_token},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_edit
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_edit",
        annotations={
            "title": "Edit Memory File (String Replace)",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_edit(
        path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
        version_token: str | None = None,
    ) -> str:
        """Exact string replacement in a file, then stage (no auto-commit).

        Raises ValidationError if old_string is not found, or is not unique
        when replace_all=False.

        Args:
            path:          Repo-relative path to the file.
            old_string:    Exact string to find and replace.
            new_string:    Replacement text.
            replace_all:   Replace all occurrences (default: False — raises if >1).
            version_token: Optional — checked before writing.

        Returns:
            MemoryWriteResult JSON with new_state.version_token.
        """
        from ..errors import NotFoundError, ValidationError
        from ..models import MemoryWriteResult

        repo = get_repo()
        path, abs_path = resolve_repo_path(repo, path)

        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")

        repo.check_version_token(path, version_token)
        content = abs_path.read_text(encoding="utf-8")

        count = content.count(old_string)
        if count == 0:
            raise ValidationError(
                f"old_string not found in {path}. "
                "Ensure you're matching the exact text including whitespace."
            )
        if count > 1 and not replace_all:
            raise ValidationError(
                f"old_string appears {count} times in {path}. "
                "Use replace_all=True to replace all occurrences, or provide "
                "more surrounding context to make it unique."
            )

        if replace_all:
            new_content = content.replace(old_string, new_string)
        else:
            new_content = content.replace(old_string, new_string, 1)

        abs_path.write_text(new_content, encoding="utf-8")
        repo.add(path)
        new_token = repo.hash_object(path)

        result = MemoryWriteResult(
            files_changed=[path],
            commit_sha=None,
            commit_message=None,
            new_state={"version_token": new_token, "replacements": count if replace_all else 1},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_delete
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_delete",
        annotations={
            "title": "Delete Memory File",
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_delete(
        path: str,
        version_token: str | None = None,
    ) -> str:
        """Delete a file and stage the removal (no auto-commit).

        ALLOWED PATHS ONLY: knowledge/, plans/, scratchpad/.
        Attempts to delete files under identity/, meta/, chats/, or skills/
        raise PermissionError immediately, before any filesystem access.

        The deletion is staged via 'git rm'. Call memory_commit to finalise.
        When a delete-permission hook is configured by the runtime, it is
        called automatically for allowed paths before the file is removed.

        Args:
            path:          Repo-relative path to delete. Must be under
                           knowledge/, plans/, or scratchpad/.
            version_token: Optional — checked before deletion.

        Returns:
            MemoryWriteResult JSON.
        """
        from ..errors import NotFoundError, MemoryPermissionError
        from ..models import MemoryWriteResult

        repo = get_repo()
        path, abs_path = validate_raw_mutation_source(
            repo,
            path,
            operation="delete",
        )

        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")

        repo.check_version_token(path, version_token)

        if grant_delete_permission is not None:
            try:
                grant_delete_permission(path)
            except Exception as e:
                raise MemoryPermissionError(
                    f"Delete permission hook rejected '{path}': {e}",
                    path=path,
                ) from e

        try:
            repo.rm(path)
        except Exception as e:
            raise MemoryPermissionError(
                f"Could not delete {path}: {e}.",
                path=path,
            )

        result = MemoryWriteResult(
            files_changed=[path],
            commit_sha=None,
            commit_message=None,
            new_state={"deleted": path},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_move
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_move",
        annotations={
            "title": "Move/Rename Memory File",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_move(
        source: str,
        dest: str,
        version_token: str | None = None,
        create_dirs: bool = True,
    ) -> str:
        """Rename or move a file, preserving git history (git mv).

        SOURCE PATH RESTRICTIONS: Same as memory_delete — source paths in
        identity/, meta/, chats/, or skills/ are blocked. Destination paths
        are unrestricted (moving a file INTO a protected folder is additive).

        The move is staged. Call memory_commit to finalise.

        Args:
            source:        Repo-relative source path.
            dest:          Repo-relative destination path.
            version_token: Optional — checked against source before moving.
            create_dirs:   Create destination parent dirs if needed (default: True).

        Returns:
            MemoryWriteResult JSON with new_state.new_version_token.
        """
        from ..errors import NotFoundError
        from ..models import MemoryWriteResult

        repo = get_repo()
        source, abs_source = validate_raw_mutation_source(
            repo,
            source,
            operation="move from",
        )
        dest, abs_dest = resolve_repo_path(repo, dest, field_name="dest")

        if not abs_source.exists():
            raise NotFoundError(f"Source file not found: {source}")

        repo.check_version_token(source, version_token)

        if create_dirs:
            abs_dest.parent.mkdir(parents=True, exist_ok=True)

        repo.mv(source, dest)
        new_token = repo.hash_object(dest)

        result = MemoryWriteResult(
            files_changed=[source, dest],
            commit_sha=None,
            commit_message=None,
            new_state={"new_path": dest, "new_version_token": new_token},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_update_frontmatter
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_update_frontmatter",
        annotations={
            "title": "Update File Frontmatter",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_update_frontmatter(
        path: str,
        updates: str,
        version_token: str | None = None,
    ) -> str:
        """Merge key-value pairs into a file's YAML frontmatter (no auto-commit).

        Does not touch the file body. Always sets last_verified to today's date
        unless 'last_verified' is explicitly included in updates.

        Pass null as a value to remove a frontmatter key.

        Args:
            path:          Repo-relative file path.
            updates:       JSON object of frontmatter key-value pairs to set.
                           Use null values to remove keys.
                           Example: '{"status": "complete", "next_action": null}'
            version_token: Optional — checked before writing.

        Returns:
            MemoryWriteResult JSON with new_state containing the full updated frontmatter.
        """
        from ..errors import NotFoundError, ValidationError
        from ..frontmatter_utils import update_frontmatter_fields
        from ..models import MemoryWriteResult

        repo = get_repo()
        path, abs_path = resolve_repo_path(repo, path)

        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")

        try:
            updates_dict = json.loads(updates)
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON for updates: {e}")

        if not isinstance(updates_dict, dict):
            raise ValidationError("updates must be a JSON object")

        repo.check_version_token(path, version_token)

        updated_fm = update_frontmatter_fields(abs_path, updates_dict)
        repo.add(path)

        result = MemoryWriteResult(
            files_changed=[path],
            commit_sha=None,
            commit_message=None,
            new_state={"frontmatter": updated_fm},
        )
        return result.to_json()

    # ------------------------------------------------------------------
    # memory_commit
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_commit",
        annotations={
            "title": "Commit Staged Memory Changes",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    )
    async def memory_commit(
        message: str,
        allow_empty: bool = False,
    ) -> str:
        """Commit all staged changes to the memory repository.

        Should follow the memory commit convention:
          [{category}] {Verb} {description ≤60 chars}

        Known categories: [knowledge] [plan] [identity] [chat] [curation]
                          [scratchpad] [system]

        Warns (does not error) on unrecognised prefix — the warning appears
        in new_state.warnings so the agent can decide whether to revise.

        Args:
            message:     Commit message following the convention above.
            allow_empty: Allow committing with nothing staged (default: False).

        Returns:
            MemoryWriteResult JSON with commit_sha and any prefix warnings.
        """
        from ..errors import StagingError
        from ..models import MemoryWriteResult

        repo = get_repo()
        warnings = []

        if repo.nothing_staged() and not allow_empty:
            raise StagingError(
                "Nothing staged to commit. Use memory_write/memory_edit/memory_delete "
                "first, then call memory_commit."
            )

        # Validate prefix (warn, don't error)
        import re
        prefix_match = re.match(r"^\[([^\]]+)\]", message)
        if not prefix_match:
            warnings.append(
                f"Commit message '{message[:50]}...' does not start with a "
                f"recognised [category] prefix. Known prefixes: "
                f"{sorted(_KNOWN_PREFIXES)}"
            )
        else:
            full_prefix = f"[{prefix_match.group(1)}]"
            if full_prefix not in _KNOWN_PREFIXES:
                warnings.append(
                    f"Unrecognised commit prefix '{full_prefix}'. "
                    f"Known prefixes: {sorted(_KNOWN_PREFIXES)}. "
                    "Proceeding anyway."
                )

        sha = repo.commit(message)

        result = MemoryWriteResult(
            files_changed=[],  # already staged before this call
            commit_sha=sha,
            commit_message=message,
            new_state={},
            warnings=warnings,
        )
        return result.to_json()

    return {
        "memory_write": memory_write,
        "memory_edit": memory_edit,
        "memory_delete": memory_delete,
        "memory_move": memory_move,
        "memory_update_frontmatter": memory_update_frontmatter,
        "memory_commit": memory_commit,
    }
