"""
Tier 0 — Enhanced read tools.

These extend the existing read-only tool set with:
  - memory_read_file   : returns version_token + parsed frontmatter
  - memory_list_folder : unchanged from existing (re-implemented here)
  - memory_search      : unchanged from existing (re-implemented here)
  - memory_git_log     : recent commit history
  - memory_diff        : working tree status
  - memory_audit_trust : trust decay audit

All tools are registered onto the FastMCP instance passed in via register().
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# Known commit-prefix categories (for memory_commit validation)
KNOWN_PREFIXES = {
    "[knowledge]", "[plan]", "[identity]", "[chat]",
    "[curation]", "[scratchpad]", "[system]",
}

# Trust decay thresholds (days) — defaults; runtime reads from quick-reference.md
_DEFAULT_LOW_THRESHOLD = 120
_DEFAULT_MEDIUM_THRESHOLD = 180
_IGNORED_NAMES = frozenset({
    ".git", ".claude", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
})
_HUMANS_DIRNAME = "HUMANS"


def _parse_trust_thresholds(repo_root: Path) -> tuple[int, int]:
    """Try to read low/medium trust thresholds from meta/quick-reference.md."""
    qr_path = repo_root / "meta" / "quick-reference.md"
    if not qr_path.exists():
        return _DEFAULT_LOW_THRESHOLD, _DEFAULT_MEDIUM_THRESHOLD
    text = qr_path.read_text(encoding="utf-8")
    low = _DEFAULT_LOW_THRESHOLD
    medium = _DEFAULT_MEDIUM_THRESHOLD
    # Look for patterns like "low: 120 days" or "120-day" near "low trust"
    low_m = re.search(r"low.*?(\d+)[- ]day", text, re.IGNORECASE)
    medium_m = re.search(r"medium.*?(\d+)[- ]day", text, re.IGNORECASE)
    if low_m:
        low = int(low_m.group(1))
    if medium_m:
        medium = int(medium_m.group(1))
    return low, medium


def _effective_date(fm: dict) -> date | None:
    """Return last_verified if present, else created, else None."""
    for key in ("last_verified", "created"):
        val = fm.get(key)
        if val:
            try:
                if isinstance(val, date):
                    return val
                return datetime.strptime(str(val), "%Y-%m-%d").date()
            except ValueError:
                pass
    return None


def _repo_relative(path: Path, root: Path) -> Path:
    """Return a path relative to the repo root."""
    return path.relative_to(root)


def _is_humans_path(path: Path, root: Path) -> bool:
    """Return True when a path is under HUMANS/."""
    relative = _repo_relative(path, root)
    return bool(relative.parts) and relative.parts[0] == _HUMANS_DIRNAME


def register(mcp: "FastMCP", get_repo, get_root) -> dict[str, object]:
    """Register all Tier 0 read tools and return their callables."""

    # ------------------------------------------------------------------
    # memory_read_file
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_read_file",
        annotations={
            "title": "Read Memory File",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_read_file(path: str) -> str:
        """Read a file from the memory repository.

        Returns the file content along with a version_token (git object hash)
        for optimistic locking, and parsed frontmatter if present.

        Args:
            path: Repo-relative path (e.g. 'identity/profile.md',
                  'knowledge/_unverified/django/celery-canvas.md').

        Returns:
            JSON with keys:
              content      (str)       Full file text
              version_token (str)      Git SHA-1 of the file; pass back to write
                                       tools to detect concurrent modifications
              frontmatter  (dict|null) Parsed YAML frontmatter, or null
        """
        from ..errors import NotFoundError
        from ..frontmatter_utils import read_with_frontmatter

        repo = get_repo()
        abs_path = repo.abs_path(path)
        if not abs_path.exists():
            raise NotFoundError(f"File not found: {path}")

        fm_dict, body = read_with_frontmatter(abs_path)
        version_token = repo.hash_object(path)

        result = {
            "content": abs_path.read_text(encoding="utf-8"),
            "version_token": version_token,
            "frontmatter": fm_dict or None,
        }
        return json.dumps(result, indent=2, default=str)

    # ------------------------------------------------------------------
    # memory_list_folder
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_list_folder",
        annotations={
            "title": "List Memory Folder",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_list_folder(
        path: str = ".",
        include_hidden: bool = False,
        include_humans: bool = False,
    ) -> str:
        """List the contents of a folder in the memory repository.

        Args:
            path:           Repo-relative folder path (default: repo root '.').
            include_hidden: Include dot-files/folders (default: False).
            include_humans: Include the human-facing HUMANS/ tree when browsing
                            broad scopes like '.' (default: False).

        Returns:
            Markdown-formatted directory listing with file sizes.
        """
        root = get_root()
        folder = (root / path).resolve()
        if not folder.exists():
            return f"Error: Folder not found: {path}"
        if not folder.is_dir():
            return f"Error: Not a directory: {path}"

        explicit_humans_request = _is_humans_path(folder, root)
        lines = [f"# {path}/\n"]
        try:
            all_entries = list(folder.iterdir())
        except PermissionError:
            return f"Error: Permission denied reading {path}"

        def _keep(entry: Path) -> bool:
            if entry.name in _IGNORED_NAMES:
                return False
            if not include_hidden and entry.name.startswith("."):
                return False
            if (
                not explicit_humans_request
                and not include_humans
                and _is_humans_path(entry, root)
            ):
                return False
            return True

        entries = sorted(
            [entry for entry in all_entries if _keep(entry)],
            key=lambda p: (p.is_file(), p.name),
        )

        for entry in entries:
            rel = str(entry.relative_to(root))
            if entry.is_dir():
                lines.append(f"📁 {entry.name}/")
            else:
                size = entry.stat().st_size
                lines.append(f"📄 {entry.name}  ({size:,} bytes)  `{rel}`")

        if len(lines) == 1:
            lines.append("_(empty)_")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # memory_search
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_search",
        annotations={
            "title": "Search Memory Files",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_search(
        query: str,
        path: str = ".",
        glob_pattern: str = "**/*.md",
        case_sensitive: bool = False,
        max_results: int = 30,
        include_humans: bool = False,
    ) -> str:
        """Search for a pattern across files in the memory repository.

        Args:
            query:          Search string or Python regex.
            path:           Folder to search within (default: '.').
            glob_pattern:   File filter (default: '**/*.md').
            case_sensitive: Case-sensitive match (default: False).
            max_results:    Max matching lines to return (default: 30, max 100).
            include_humans: Include the human-facing HUMANS/ tree when searching
                            broad scopes like '.' (default: False).

        Returns:
            Matching lines grouped by file with line numbers, or a not-found message.
        """
        root = get_root()
        search_root = (root / path).resolve()
        if not search_root.exists():
            return f"Error: Path not found: {path}"

        flags = 0 if case_sensitive else re.IGNORECASE
        try:
            pattern = re.compile(query, flags)
        except re.error as e:
            return f"Error: Invalid regex pattern: {e}"

        max_results = min(max_results, 100)
        results: list[str] = []
        total_matches = 0
        explicit_humans_search = _is_humans_path(search_root, root)

        for file_path in sorted(search_root.glob(glob_pattern)):
            if any(part in _IGNORED_NAMES for part in file_path.parts):
                continue
            if not file_path.is_file():
                continue
            if (
                not explicit_humans_search
                and not include_humans
                and _is_humans_path(file_path, root)
            ):
                continue
            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            file_matches = []
            for line_no, line in enumerate(text.splitlines(), 1):
                if pattern.search(line):
                    file_matches.append(f"  {line_no}: {line.rstrip()}")
                    total_matches += 1
                    if total_matches >= max_results:
                        break

            if file_matches:
                rel = file_path.relative_to(root).as_posix()
                results.append(f"\n**{rel}**")
                results.extend(file_matches)

            if total_matches >= max_results:
                results.append(f"\n_(truncated at {max_results} matches)_")
                break

        if not results:
            files_checked = len(list(search_root.glob(glob_pattern)))
            return f"No matches found (searched {files_checked} files)."

        return "\n".join(results)

    # ------------------------------------------------------------------
    # memory_git_log
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_git_log",
        annotations={
            "title": "Git Log for Memory Repo",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_git_log(n: int = 10) -> str:
        """Return recent commit history for the memory repository.

        Useful at session start to see what changed since the last session.

        Args:
            n: Number of commits to return (default: 10, max: 50).

        Returns:
            JSON list of commits, each with sha, message, date, files_changed.
        """
        repo = get_repo()
        n = min(n, 50)
        commits = repo.log(n)
        return json.dumps(commits, indent=2)

    # ------------------------------------------------------------------
    # memory_diff
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_diff",
        annotations={
            "title": "Working Tree Diff Status",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_diff() -> str:
        """Show working tree status — staged, unstaged, and untracked files.

        Call before memory_commit to verify what will be included in the commit.

        Returns:
            JSON with keys staged, unstaged, untracked (each a list of paths).
        """
        repo = get_repo()
        status = repo.diff_status()
        return json.dumps(status, indent=2)

    # ------------------------------------------------------------------
    # memory_audit_trust
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_audit_trust",
        annotations={
            "title": "Trust Decay Audit",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_audit_trust(
        include_categories: str = "",
    ) -> str:
        """Audit trust decay across the memory repository.

        Checks all files with frontmatter trust fields against the decay
        thresholds from meta/quick-reference.md:
          - low-trust files:    overdue at 120 days, flagged at 90 days
          - medium-trust files: overdue at 180 days, flagged at 150 days

        Does not modify any files — pure read operation.

        Args:
            include_categories: Comma-separated list of top-level folders to scan
                                 (e.g. 'knowledge,plans'). Empty = scan all.

        Returns:
            JSON with overdue_low, overdue_medium, upcoming_low, upcoming_medium,
            checked_at, and files_checked count.
        """
        from ..frontmatter_utils import read_with_frontmatter

        root = get_root()
        low_threshold, medium_threshold = _parse_trust_thresholds(root)
        low_warn = low_threshold - 30
        medium_warn = medium_threshold - 30

        categories = [c.strip() for c in include_categories.split(",") if c.strip()]
        if not categories:
            categories = ["knowledge", "plans", "identity", "skills"]

        today = date.today()
        overdue_low = []
        overdue_medium = []
        upcoming_low = []
        upcoming_medium = []
        files_checked = 0

        for cat in categories:
            cat_path = root / cat
            if not cat_path.is_dir():
                continue
            for md_file in cat_path.rglob("*.md"):
                if not md_file.is_file():
                    continue
                try:
                    fm_dict, _ = read_with_frontmatter(md_file)
                except Exception:
                    continue

                trust = fm_dict.get("trust")
                if trust not in ("low", "medium", "high"):
                    continue

                files_checked += 1
                eff_date = _effective_date(fm_dict)
                if eff_date is None:
                    continue

                days = (today - eff_date).days
                rel = str(md_file.relative_to(root))

                entry = {
                    "path": rel,
                    "trust": trust,
                    "effective_date": str(eff_date),
                    "days_since_verified": days,
                }

                if trust == "low":
                    threshold = low_threshold
                    warn = low_warn
                    entry["days_until_threshold"] = max(0, threshold - days)
                    if days >= threshold:
                        entry["action_required"] = "archive"
                        overdue_low.append(entry)
                    elif days >= warn:
                        entry["action_required"] = "review"
                        upcoming_low.append(entry)
                elif trust == "medium":
                    threshold = medium_threshold
                    warn = medium_warn
                    entry["days_until_threshold"] = max(0, threshold - days)
                    if days >= threshold:
                        entry["action_required"] = "flag"
                        overdue_medium.append(entry)
                    elif days >= warn:
                        entry["action_required"] = "review"
                        upcoming_medium.append(entry)

        result = {
            "overdue_low": overdue_low,
            "overdue_medium": overdue_medium,
            "upcoming_low": upcoming_low,
            "upcoming_medium": upcoming_medium,
            "checked_at": str(today),
            "files_checked": files_checked,
            "thresholds": {
                "low_days": low_threshold,
                "medium_days": medium_threshold,
            },
        }
        return json.dumps(result, indent=2)

    # ------------------------------------------------------------------
    # memory_validate
    # ------------------------------------------------------------------
    @mcp.tool(
        name="memory_validate",
        annotations={
            "title": "Validate Memory Repository",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    )
    async def memory_validate() -> str:
        """Run the structural validator against the memory repository.

        Checks frontmatter keys, ACCESS.jsonl structure, and governance
        consistency. Returns a validation report.

        Returns:
            Validation report with errors and warnings, or a clean-pass message.
        """
        root = get_root()
        validator_path = root / "HUMANS" / "tooling" / "scripts" / "validate_memory_repo.py"
        if not validator_path.exists():
            return "Validator not found at HUMANS/tooling/scripts/validate_memory_repo.py"
        try:
            result = subprocess.run(
                [sys.executable, str(validator_path), str(root)],
                cwd=str(root),
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout + result.stderr
            return output.strip() or "Validation complete (no output)."
        except subprocess.TimeoutExpired:
            return "Error: Validator timed out after 30 seconds."
        except Exception as e:
            return f"Error running validator: {e}"

    return {
        "memory_read_file": memory_read_file,
        "memory_list_folder": memory_list_folder,
        "memory_search": memory_search,
        "memory_git_log": memory_git_log,
        "memory_diff": memory_diff,
        "memory_audit_trust": memory_audit_trust,
        "memory_validate": memory_validate,
    }
