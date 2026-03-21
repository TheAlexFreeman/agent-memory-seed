"""Shared path validation helpers for MCP tool inputs."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from typing import Iterable

from .errors import MemoryPermissionError, ValidationError

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SESSION_ID_RE = re.compile(r"^chats/\d{4}/\d{2}/\d{2}/chat-\d{3}$")

# Shared commit-prefix vocabulary used by both read_tools and write_tools.
KNOWN_COMMIT_PREFIXES: frozenset[str] = frozenset(
    {
        "[knowledge]",
        "[plan]",
        "[skill]",
        "[identity]",
        "[chat]",
        "[curation]",
        "[scratchpad]",
        "[system]",
        "[access]",
    }
)

_PROTECTED_ROOTS = ("identity", "meta", "chats", "skills")
_RAW_MUTATION_ROOTS = ("knowledge", "plans", "projects", "scratchpad")


def resolve_repo_path(repo, raw_path: str, *, field_name: str = "path") -> tuple[str, Path]:
    """Normalize an input path to a repo-relative POSIX path plus abs path."""
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise ValidationError(f"{field_name} must be a non-empty repo-relative path")

    abs_path = repo.abs_path(raw_path)
    rel_path = repo.rel_path(abs_path).replace("\\", "/")
    return rel_path, abs_path


def validate_raw_write_target(repo, raw_path: str, *, field_name: str = "path") -> tuple[str, Path]:
    """Normalize and validate write targets against the protected-directory policy.

    Protected directories (identity/, meta/, chats/, skills/) are blocked for
    raw Tier 2 writes. Tier 2 writes must stay under knowledge/, plans/,
    projects/, or scratchpad/. Use Tier 1 semantic tools for governed writes to protected
    directories (e.g. memory_update_identity_trait,
    memory_record_chat_summary).

    Returns the repo-relative path and absolute path on success.
    """
    rel_path, abs_path = resolve_repo_path(repo, raw_path, field_name=field_name)
    top = PurePosixPath(rel_path).parts[0] if rel_path else ""

    if top in _PROTECTED_ROOTS:
        raise MemoryPermissionError(
            f"Cannot raw-write to '{rel_path}': '{top}/' is a protected directory. "
            f"Use the appropriate Tier 1 semantic tool instead. "
            f"Protected directories: {sorted(_PROTECTED_ROOTS)}",
            path=rel_path,
        )

    if top not in _RAW_MUTATION_ROOTS:
        allowed = ", ".join(f"{root}/" for root in _RAW_MUTATION_ROOTS)
        raise MemoryPermissionError(
            f"Cannot raw-write to '{rel_path}': path must be under {allowed}.",
            path=rel_path,
        )

    return rel_path, abs_path


def validate_raw_move_destination(
    repo,
    raw_path: str,
    *,
    field_name: str = "dest",
) -> tuple[str, Path]:
    """Normalize and validate move destinations against the protected-directory policy.

    Tier 2 moves must not target protected directories (identity/, meta/,
    chats/, skills/). Use Tier 1 semantic tools for governed writes there.
    """
    rel_path, abs_path = resolve_repo_path(repo, raw_path, field_name=field_name)
    top = PurePosixPath(rel_path).parts[0] if rel_path else ""

    if top in _PROTECTED_ROOTS:
        raise MemoryPermissionError(
            f"Cannot move to '{rel_path}': '{top}/' is a protected directory. "
            f"Use the appropriate Tier 1 semantic tool instead. "
            f"Protected directories: {sorted(_PROTECTED_ROOTS)}",
            path=rel_path,
        )

    return rel_path, abs_path


def require_under_prefix(
    rel_path: str,
    prefix: str,
    *,
    field_name: str = "path",
) -> str:
    """Require that *rel_path* is inside the exact directory prefix."""
    normalized_prefix = prefix.rstrip("/") + "/"
    if not rel_path.startswith(normalized_prefix):
        raise ValidationError(f"{field_name} must be under {normalized_prefix}: {rel_path}")
    return rel_path


def forbid_prefix(
    rel_path: str,
    prefix: str,
    *,
    field_name: str = "path",
) -> str:
    """Reject repo-relative paths inside the exact directory prefix."""
    normalized_prefix = prefix.rstrip("/") + "/"
    if rel_path.startswith(normalized_prefix):
        raise ValidationError(f"{field_name} must not be under {normalized_prefix}: {rel_path}")
    return rel_path


def validate_slug(value: str, *, field_name: str) -> str:
    """Validate a bare kebab-case identifier."""
    if not isinstance(value, str) or not _SLUG_RE.fullmatch(value):
        raise ValidationError(f"{field_name} must be a bare kebab-case slug: {value!r}")
    return value


def validate_session_id(session_id: str) -> str:
    """Validate canonical session ids: chats/YYYY/MM/DD/chat-NNN."""
    if not isinstance(session_id, str) or not _SESSION_ID_RE.fullmatch(session_id):
        raise ValidationError("session_id must match chats/YYYY/MM/DD/chat-NNN")
    return session_id


def validate_raw_mutation_source(repo, raw_path: str, *, operation: str) -> tuple[str, Path]:
    """Normalize and validate raw delete/move source paths."""
    rel_path, abs_path = resolve_repo_path(repo, raw_path)
    top = PurePosixPath(rel_path).parts[0] if rel_path else ""

    if top in _PROTECTED_ROOTS:
        raise MemoryPermissionError(
            f"Cannot {operation} '{rel_path}': '{top}/' is a protected directory. "
            f"Protected directories: {sorted(_PROTECTED_ROOTS)}",
            path=rel_path,
        )

    if top not in _RAW_MUTATION_ROOTS:
        allowed = ", ".join(f"{root}/" for root in _RAW_MUTATION_ROOTS)
        raise MemoryPermissionError(
            f"Cannot {operation} '{rel_path}': source must be under {allowed}.",
            path=rel_path,
        )

    return rel_path, abs_path


def validate_top_level_root(
    rel_path: str,
    *,
    allowed_roots: Iterable[str],
    field_name: str = "path",
) -> str:
    """Require a normalized repo path to start at one of the allowed roots."""
    top = PurePosixPath(rel_path).parts[0] if rel_path else ""
    allowed = tuple(root.rstrip("/") for root in allowed_roots)
    if top not in allowed:
        pretty = ", ".join(f"{root}/" for root in allowed)
        raise ValidationError(f"{field_name} must be under one of {pretty}: {rel_path}")
    return rel_path
