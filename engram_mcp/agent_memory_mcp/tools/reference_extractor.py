from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..frontmatter_utils import read_with_frontmatter

_GOVERNED_REFERENCE_ROOTS = ("identity", "knowledge", "plans", "skills", "meta")
_URL_PREFIXES = ("http://", "https://", "mailto:", "memory://", "file://", "vscode://")
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\n]+)\)")
_BODY_PATH_RE = re.compile(
    r"(?P<path>(?:\.\.?/|identity/|knowledge/|plans/|skills/|meta/)[^\s)\]>'\"]+)"
)


def _normalize_for_match(value: str) -> str:
    normalized = value.strip().replace("\\", "/").rstrip("/").lower()
    return normalized.replace("_", "-")


def _is_external_target(target: str) -> bool:
    lowered = target.strip().lower()
    return lowered.startswith(_URL_PREFIXES) or lowered.startswith("#")


def _strip_markdown_target(target: str) -> str:
    cleaned = target.strip()
    if cleaned.startswith("<") and ">" in cleaned:
        cleaned = cleaned[1 : cleaned.index(">")]
    if " " in cleaned and not cleaned.startswith(("./", "../")):
        cleaned = cleaned.split(" ", 1)[0]
    cleaned = cleaned.split("#", 1)[0].split("?", 1)[0].strip()
    return cleaned.replace("\\", "/")


def _resolve_reference(from_path: str, target: str, root: Path) -> str | None:
    cleaned = _strip_markdown_target(target)
    if not cleaned or _is_external_target(cleaned):
        return None
    if cleaned.startswith("/"):
        cleaned = cleaned.lstrip("/")

    base = root / from_path
    if cleaned.startswith(("./", "../")):
        resolved = (base.parent / cleaned).resolve()
    elif any(cleaned.startswith(f"{prefix}/") for prefix in _GOVERNED_REFERENCE_ROOTS):
        resolved = (root / cleaned).resolve()
    else:
        resolved = (base.parent / cleaned).resolve()

    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return None


def _looks_like_path(value: str) -> bool:
    cleaned = value.strip().replace("\\", "/")
    if not cleaned or _is_external_target(cleaned):
        return False
    return (
        cleaned.endswith(".md")
        or cleaned.startswith(("./", "../"))
        or any(cleaned.startswith(f"{prefix}/") for prefix in _GOVERNED_REFERENCE_ROOTS)
    )


def _first_line_number(text: str, needle: str) -> int | None:
    for index, line in enumerate(text.splitlines(), start=1):
        if needle in line:
            return index
    return None


def _iter_frontmatter_refs(value: Any, key_path: str = "") -> list[tuple[str, str]]:
    matches: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            next_key = f"{key_path}.{key}" if key_path else str(key)
            matches.extend(_iter_frontmatter_refs(nested, next_key))
        return matches
    if isinstance(value, list):
        for idx, nested in enumerate(value):
            next_key = f"{key_path}[{idx}]"
            matches.extend(_iter_frontmatter_refs(nested, next_key))
        return matches
    if isinstance(value, str) and _looks_like_path(value):
        matches.append((key_path, value))
    return matches


def _iter_governed_markdown_files(root: Path) -> list[str]:
    files: list[str] = []
    for folder in _GOVERNED_REFERENCE_ROOTS:
        folder_path = root / folder
        if not folder_path.is_dir():
            continue
        for md_file in sorted(folder_path.rglob("*.md")):
            try:
                files.append(md_file.relative_to(root).as_posix())
            except ValueError:
                continue
    return files


def _matches_query(query: str, raw_value: str, resolved_value: str | None = None) -> bool:
    normalized_query = _normalize_for_match(query)
    candidates = [raw_value]
    if resolved_value:
        candidates.append(resolved_value)
    for candidate in candidates:
        if normalized_query in _normalize_for_match(candidate):
            return True
    return False


def find_references(root: Path, query: str, include_body: bool = False) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for rel_path in _iter_governed_markdown_files(root):
        abs_path = root / rel_path
        try:
            content = abs_path.read_text(encoding="utf-8")
            frontmatter, body = read_with_frontmatter(abs_path)
        except OSError:
            continue

        for link_match in _MARKDOWN_LINK_RE.finditer(body):
            raw_target = link_match.group(2)
            resolved = _resolve_reference(rel_path, raw_target, root)
            if not _matches_query(query, raw_target, resolved):
                continue
            matches.append(
                {
                    "from_path": rel_path,
                    "ref_type": "markdown_link",
                    "ref_key": None,
                    "ref_value": raw_target,
                    "resolved_path": resolved,
                    "line": body[: link_match.start()].count("\n") + 1,
                    "snippet": link_match.group(0),
                }
            )

        for key_path, raw_value in _iter_frontmatter_refs(frontmatter):
            resolved = _resolve_reference(rel_path, raw_value, root)
            if not _matches_query(query, raw_value, resolved):
                continue
            matches.append(
                {
                    "from_path": rel_path,
                    "ref_type": "frontmatter_path",
                    "ref_key": key_path,
                    "ref_value": raw_value,
                    "resolved_path": resolved,
                    "line": _first_line_number(content, raw_value),
                    "snippet": raw_value,
                }
            )

        if include_body:
            for line_number, line in enumerate(body.splitlines(), start=1):
                for body_match in _BODY_PATH_RE.finditer(line):
                    raw_value = body_match.group("path")
                    resolved = _resolve_reference(rel_path, raw_value, root)
                    if not _matches_query(query, raw_value, resolved):
                        continue
                    matches.append(
                        {
                            "from_path": rel_path,
                            "ref_type": "body_path",
                            "ref_key": None,
                            "ref_value": raw_value,
                            "resolved_path": resolved,
                            "line": line_number,
                            "snippet": line.strip(),
                        }
                    )

    matches.sort(
        key=lambda item: (
            str(item["from_path"]),
            str(item["ref_type"]),
            int(item["line"] or 0),
            str(item["ref_value"]),
        )
    )
    return matches