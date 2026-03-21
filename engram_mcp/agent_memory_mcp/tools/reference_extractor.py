from __future__ import annotations

import re
from pathlib import Path
from posixpath import relpath as posix_relpath
from typing import Any

from ..frontmatter_utils import read_with_frontmatter

_GOVERNED_REFERENCE_ROOTS = ("identity", "knowledge", "plans", "skills", "meta")
_URL_PREFIXES = ("http://", "https://", "mailto:", "memory://", "file://", "vscode://")
_MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\n]+)\)")
_BODY_PATH_RE = re.compile(
    r"(?P<path>(?:\.\.?/|identity/|knowledge/|plans/|skills/|meta/)[^\s)\]>'\"]+)"
)
_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<text>.+?)\s*$", re.MULTILINE)


def _normalize_for_match(value: str) -> str:
    normalized = value.strip().replace("\\", "/").rstrip("/").lower()
    return normalized.replace("_", "-")


def _is_external_target(target: str) -> bool:
    lowered = target.strip().lower()
    return lowered.startswith(_URL_PREFIXES) or lowered.startswith("#")


def _is_external_or_anchor_target(target: str) -> bool:
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


def _split_target_and_anchor(target: str) -> tuple[str, str | None]:
    cleaned = target.strip()
    if cleaned.startswith("<") and ">" in cleaned:
        cleaned = cleaned[1 : cleaned.index(">")]
    if " " in cleaned and not cleaned.startswith(("./", "../")):
        cleaned = cleaned.split(" ", 1)[0]
    path_part, anchor = cleaned, None
    if "#" in cleaned:
        path_part, anchor = cleaned.split("#", 1)
    return path_part.replace("\\", "/").strip(), (anchor.strip() or None) if anchor else None


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


def _resolve_target_path(from_path: str, target: str, root: Path) -> tuple[str | None, str | None, str | None]:
    raw_path, anchor = _split_target_and_anchor(target)
    if not raw_path and anchor:
        return from_path, anchor, None
    if not raw_path:
        return None, anchor, "empty target"
    if _is_external_or_anchor_target(target):
        return None, anchor, None
    cleaned = raw_path.lstrip("/") if raw_path.startswith("/") else raw_path
    base = root / from_path
    if cleaned.startswith(("./", "../")):
        resolved = (base.parent / cleaned).resolve()
    elif any(cleaned.startswith(f"{prefix}/") for prefix in _GOVERNED_REFERENCE_ROOTS):
        resolved = (root / cleaned).resolve()
    else:
        resolved = (base.parent / cleaned).resolve()

    try:
        rel_path = resolved.relative_to(root).as_posix()
    except ValueError:
        return None, anchor, "target escapes repository root"
    return rel_path, anchor, None


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


def _iter_governed_markdown_files_in_scope(root: Path, scope: str = "") -> list[str]:
    normalized_scope = scope.strip().replace("\\", "/").strip("/")
    if not normalized_scope:
        return _iter_governed_markdown_files(root)

    scope_path = root / normalized_scope
    if not scope_path.exists():
        return []
    if scope_path.is_file():
        if scope_path.suffix.lower() != ".md":
            return []
        return [scope_path.relative_to(root).as_posix()]

    files: list[str] = []
    for md_file in sorted(scope_path.rglob("*.md")):
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


def _slugify_heading(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9\s-]", "", lowered)
    return re.sub(r"\s+", "-", lowered).strip("-")


def _extract_heading_anchors(markdown_text: str) -> set[str]:
    anchors: set[str] = set()
    for match in _HEADING_RE.finditer(markdown_text):
        anchor = _slugify_heading(match.group("text"))
        if anchor:
            anchors.add(anchor)
    return anchors


def _iter_validation_targets(root: Path, scope: str = "") -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for rel_path in _iter_governed_markdown_files_in_scope(root, scope):
        abs_path = root / rel_path
        try:
            content = abs_path.read_text(encoding="utf-8")
            frontmatter, body = read_with_frontmatter(abs_path)
        except OSError:
            continue

        for link_match in _MARKDOWN_LINK_RE.finditer(body):
            raw_target = link_match.group(2)
            resolved_path, anchor, error = _resolve_target_path(rel_path, raw_target, root)
            targets.append(
                {
                    "from_path": rel_path,
                    "ref_type": "markdown_link",
                    "target": raw_target,
                    "resolved_path": resolved_path,
                    "anchor": anchor,
                    "line": body[: link_match.start()].count("\n") + 1,
                    "snippet": link_match.group(0),
                    "error": error,
                }
            )

        for key_path, raw_value in _iter_frontmatter_refs(frontmatter):
            resolved_path, anchor, error = _resolve_target_path(rel_path, raw_value, root)
            targets.append(
                {
                    "from_path": rel_path,
                    "ref_type": "frontmatter_path",
                    "ref_key": key_path,
                    "target": raw_value,
                    "resolved_path": resolved_path,
                    "anchor": anchor,
                    "line": _first_line_number(content, raw_value),
                    "snippet": raw_value,
                    "error": error,
                }
            )

    targets.sort(
        key=lambda item: (
            str(item["from_path"]),
            str(item["ref_type"]),
            int(item["line"] or 0),
            str(item["target"]),
        )
    )
    return targets


def validate_links(root: Path, scope: str = "") -> dict[str, Any]:
    targets = _iter_validation_targets(root, scope)
    heading_cache: dict[str, set[str]] = {}
    broken: list[dict[str, Any]] = []
    ok_count = 0

    for item in targets:
        if item["error"] is not None:
            broken.append(
                {
                    "from_path": item["from_path"],
                    "ref_type": item["ref_type"],
                    "target": item["target"],
                    "resolved_path": item["resolved_path"],
                    "reason": item["error"],
                    "line": item["line"],
                }
            )
            continue

        resolved_path = item["resolved_path"]
        anchor = item.get("anchor")
        if resolved_path is None:
            continue

        target_path = root / resolved_path
        if not target_path.exists():
            broken.append(
                {
                    "from_path": item["from_path"],
                    "ref_type": item["ref_type"],
                    "target": item["target"],
                    "resolved_path": resolved_path,
                    "reason": "target not found",
                    "line": item["line"],
                }
            )
            continue

        if anchor:
            if resolved_path not in heading_cache:
                try:
                    heading_cache[resolved_path] = _extract_heading_anchors(
                        target_path.read_text(encoding="utf-8")
                    )
                except OSError:
                    heading_cache[resolved_path] = set()
            if anchor not in heading_cache[resolved_path]:
                broken.append(
                    {
                        "from_path": item["from_path"],
                        "ref_type": item["ref_type"],
                        "target": item["target"],
                        "resolved_path": resolved_path,
                        "reason": f"anchor not found: #{anchor}",
                        "line": item["line"],
                    }
                )
                continue

        ok_count += 1

    result: dict[str, Any] = {
        "scope": scope.strip().replace("\\", "/") or ".",
        "checked": len(targets),
        "ok_count": ok_count,
        "broken": broken[:200],
    }
    if len(broken) > 200:
        result["truncated"] = True
        result["total_broken"] = len(broken)
    return result


def _normalize_repo_path(path: str) -> str:
    return path.strip().replace("\\", "/").strip("/")


def _replace_path_prefix(path: str, source: str, dest: str) -> str:
    if path == source:
        return dest
    return f"{dest}/{path[len(source) + 1:]}"


def _source_descendants(root: Path, source: str) -> list[str]:
    source_path = root / source
    if source_path.is_file():
        return [source]

    descendants: list[str] = []
    for child in sorted(source_path.rglob("*")):
        if not child.is_file():
            continue
        try:
            descendants.append(child.relative_to(root).as_posix())
        except ValueError:
            continue
    return descendants


def _is_repo_absolute_target(target: str) -> bool:
    cleaned, _ = _split_target_and_anchor(target)
    cleaned = cleaned.lstrip("/")
    return any(cleaned.startswith(f"{prefix}/") for prefix in _GOVERNED_REFERENCE_ROOTS)


def _rewrite_reference_target(from_path: str, target: str, new_resolved_path: str) -> str:
    raw_path, anchor = _split_target_and_anchor(target)
    if not raw_path:
        return target

    if target.strip().startswith("/"):
        rewritten = f"/{new_resolved_path}"
    elif _is_repo_absolute_target(target):
        rewritten = new_resolved_path
    else:
        from_parent = Path(from_path).parent.as_posix()
        rewritten = posix_relpath(new_resolved_path, start=from_parent or ".")
    if anchor:
        rewritten = f"{rewritten}#{anchor}"
    return rewritten


def _summary_targets_for_reorganization(source: str, dest: str) -> list[str]:
    targets: set[str] = set()
    for candidate in (source, dest):
        parts = Path(candidate).parts
        if not parts or parts[0] != "knowledge":
            continue
        targets.add("knowledge/SUMMARY.md")
        parent = Path(candidate).parent.as_posix()
        if parent and parent != "." and parent != "knowledge":
            targets.add(f"{parent}/SUMMARY.md")
    return sorted(targets)


def preview_reorganization(root: Path, source: str, dest: str) -> dict[str, Any]:
    normalized_source = _normalize_repo_path(source)
    normalized_dest = _normalize_repo_path(dest)
    files_to_move = _source_descendants(root, normalized_source)
    file_moves = [
        {
            "source": path,
            "dest": _replace_path_prefix(path, normalized_source, normalized_dest),
        }
        for path in files_to_move
    ]

    source_refs = find_references(root, normalized_source, include_body=True)
    refs_by_file: dict[str, list[dict[str, Any]]] = {}
    for match in source_refs:
        resolved_path = match.get("resolved_path")
        if not isinstance(resolved_path, str) or not (
            resolved_path == normalized_source
            or resolved_path.startswith(f"{normalized_source}/")
        ):
            continue
        new_resolved_path = _replace_path_prefix(resolved_path, normalized_source, normalized_dest)
        refs_by_file.setdefault(str(match["from_path"]), []).append(
            {
                "type": match["ref_type"],
                "old": match["ref_value"],
                "new": _rewrite_reference_target(
                    str(match["from_path"]),
                    str(match["ref_value"]),
                    new_resolved_path,
                ),
                "resolved_old": resolved_path,
                "resolved_new": new_resolved_path,
                "line": match.get("line"),
            }
        )

    files_with_references = [
        {
            "path": from_path,
            "refs": refs,
        }
        for from_path, refs in sorted(refs_by_file.items())
    ]

    warnings: list[str] = []
    dest_path = root / normalized_dest
    if dest_path.exists() and normalized_dest != normalized_source:
        warnings.append(f"Destination already exists: {normalized_dest}")
    for move in file_moves:
        if move["source"] == move["dest"]:
            continue
        if (root / move["dest"]).exists():
            warnings.append(f"Destination conflict: {move['dest']}")

    return {
        "source": normalized_source,
        "dest": normalized_dest,
        "files_to_move": files_to_move,
        "file_moves": file_moves,
        "files_with_references": files_with_references,
        "summary_updates": _summary_targets_for_reorganization(
            normalized_source,
            normalized_dest,
        ),
        "warnings": sorted(set(warnings)),
    }