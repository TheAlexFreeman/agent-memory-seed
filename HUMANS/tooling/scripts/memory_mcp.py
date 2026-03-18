#!/usr/bin/env python3
"""
Agent Memory MCP Server — read-only tools for querying the agent-memory-seed repo.

SETUP
-----
Install:
    pip install mcp

Configure Claude Desktop (~/.config/claude/claude_desktop_config.json on Linux/Mac,
%APPDATA%\\Claude\\claude_desktop_config.json on Windows):

    {
      "mcpServers": {
        "agent-memory": {
          "command": "python",
          "args": ["/absolute/path/to/HUMANS/tooling/scripts/memory_mcp.py"],
          "env": {
            "AGENT_MEMORY_ROOT": "/absolute/path/to/your/agent-memory-seed"
          }
        }
      }
    }

REPO ROOT RESOLUTION
--------------------
Priority:
  1. AGENT_MEMORY_ROOT environment variable  (recommended)
  2. 3 levels up from this file             (fallback for in-repo invocation)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field


# ── Configuration ──────────────────────────────────────────────────────────────

def _resolve_repo_root() -> Path:
    """Resolve the memory repo root, with env var taking priority."""
    if env := os.environ.get("AGENT_MEMORY_ROOT"):
        root = Path(env).resolve()
        if root.is_dir():
            return root
        print(
            f"Warning: AGENT_MEMORY_ROOT='{env}' is not a directory — "
            "falling back to file-relative detection.",
            file=sys.stderr,
        )
    # Fallback: this file lives at HUMANS/tooling/scripts/, so parents[3] = repo root
    return Path(__file__).resolve().parents[3]


REPO_ROOT: Path = _resolve_repo_root()
VALIDATOR_PATH: Path = REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "validate_memory_repo.py"

# Folders to skip when listing or searching
IGNORED_NAMES: frozenset[str] = frozenset({
    ".git", ".claude", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
})
HUMANS_DIRNAME = "HUMANS"


# ── Server ─────────────────────────────────────────────────────────────────────

mcp = FastMCP("agent_memory_mcp")


# ── Shared utilities ────────────────────────────────────────────────────────────

def _safe_resolve(rel_path: str) -> Path:
    """Resolve a repo-relative path, raising ValueError on traversal attempts."""
    resolved = (REPO_ROOT / rel_path).resolve()
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        raise ValueError(
            f"Path '{rel_path}' resolves outside the repo root. "
            "Use paths relative to the repo root (e.g., 'identity/SUMMARY.md')."
        )
    return resolved


def _repo_relative(path: Path) -> Path:
    """Return a path relative to the repo root."""
    return path.relative_to(REPO_ROOT)


def _is_humans_path(path: Path) -> bool:
    """Return True when a path is under HUMANS/."""
    relative = _repo_relative(path)
    return bool(relative.parts) and relative.parts[0] == HUMANS_DIRNAME


def _format_size(n: int) -> str:
    """Return a human-readable file size string."""
    if n < 1024:
        return f"{n} B"
    if n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 ** 2:.1f} MB"


# ── Input models ───────────────────────────────────────────────────────────────

class ReadFileInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        ...,
        description=(
            "Repo-relative path to the file, e.g. 'identity/SUMMARY.md' or "
            "'meta/quick-reference.md'. Must point to a file, not a directory."
        ),
        min_length=1,
    )


class ListFolderInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    path: str = Field(
        default=".",
        description="Repo-relative folder to list. Use '.' for the repo root.",
    )
    include_hidden: bool = Field(
        default=False,
        description="Include dot-files and dot-folders (e.g. .github, .gitignore).",
    )
    include_humans: bool = Field(
        default=False,
        description="Include the human-facing HUMANS/ tree in ambient folder discovery.",
    )


class SearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    query: str = Field(
        ...,
        description="Search string or Python regex pattern to find in file contents.",
        min_length=1,
        max_length=200,
    )
    path: str = Field(
        default=".",
        description=(
            "Repo-relative folder to search within. Use '.' to search the entire repo, "
            "or narrow to a subtree (e.g., 'identity', 'knowledge', 'skills')."
        ),
    )
    glob_pattern: str = Field(
        default="**/*.md",
        description=(
            "Glob pattern controlling which files are searched. "
            "Examples: '**/*.md' (all Markdown), '**/*.py', '**/ACCESS.jsonl'."
        ),
    )
    case_sensitive: bool = Field(
        default=False,
        description="Whether the pattern match is case-sensitive.",
    )
    max_results: int = Field(
        default=30,
        description="Maximum number of matching lines to return (1–100).",
        ge=1,
        le=100,
    )
    include_humans: bool = Field(
        default=False,
        description="Include the human-facing HUMANS/ tree when searching broad scopes like '.'.",
    )


# ── Tools ──────────────────────────────────────────────────────────────────────

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
async def memory_read_file(params: ReadFileInput) -> str:
    """Read the full contents of a file in the agent memory repository.

    Use this to load identity profiles, knowledge entries, skill definitions,
    plan files, session summaries, governance docs, or scratchpad files.
    Always read a folder's SUMMARY.md first to orient before retrieving
    specific files. `HUMANS/` reads are allowed only through explicit paths;
    that tree is intentionally excluded from default discovery tooling.

    Args:
        params (ReadFileInput):
            - path (str): Repo-relative path to the file.

    Returns:
        str: File contents as plain text, or an actionable error message.

    Examples:
        - Orient on the user -> memory_read_file path='identity/SUMMARY.md'
        - Load context manifest -> memory_read_file path='meta/quick-reference.md'
        - Check user scratchpad -> memory_read_file path='scratchpad/USER.md'
        - Load onboarding skill -> memory_read_file path='skills/onboarding.md'

    Error cases:
        - Path does not exist: suggests using memory_list_folder to browse
        - Path is a directory: suggests using memory_list_folder instead
        - Binary file: reports that the file cannot be read as text
    """
    try:
        resolved = _safe_resolve(params.path)
    except ValueError as e:
        return f"Error: {e}"

    if not resolved.exists():
        return (
            f"Error: '{params.path}' does not exist. "
            "Use memory_list_folder to browse available files."
        )
    if resolved.is_dir():
        return (
            f"Error: '{params.path}' is a directory. "
            "Use memory_list_folder to list its contents."
        )
    try:
        return resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Error: '{params.path}' is not a UTF-8 text file."
    except OSError as e:
        return f"Error reading '{params.path}': {e}"


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
async def memory_list_folder(params: ListFolderInput) -> str:
    """List the contents of a folder in the agent memory repository.

    Returns a structured view of files and subdirectories. SUMMARY.md is always
    shown first — it is the agent's entry point for each folder. Use this to
    navigate the repo structure before reading specific files.

    Args:
        params (ListFolderInput):
            - path (str): Repo-relative folder path (default: '.', the repo root).
            - include_hidden (bool): Include dot-files/folders (default: False).

    Returns:
        str: Markdown-formatted directory listing with file sizes, or an error.

    Examples:
        - Get overall layout -> memory_list_folder path='.'
        - Browse identity files -> memory_list_folder path='identity'
        - Inspect governance docs -> memory_list_folder path='meta'
        - List chat history structure -> memory_list_folder path='chats'
        - Include the human docs tree explicitly -> memory_list_folder path='.' include_humans=True
    """
    try:
        resolved = _safe_resolve(params.path)
    except ValueError as e:
        return f"Error: {e}"

    if not resolved.exists():
        return f"Error: '{params.path}' does not exist."
    if not resolved.is_dir():
        return (
            f"Error: '{params.path}' is a file, not a folder. "
            "Use memory_read_file to read its contents."
        )

    try:
        all_entries = list(resolved.iterdir())
    except OSError as e:
        return f"Error listing '{params.path}': {e}"

    explicit_humans_request = _is_humans_path(resolved)

    def _keep(entry: Path) -> bool:
        if entry.name in IGNORED_NAMES:
            return False
        if not params.include_hidden and entry.name.startswith("."):
            return False
        if not explicit_humans_request and not params.include_humans and _is_humans_path(entry):
            return False
        return True

    entries = [e for e in all_entries if _keep(e)]
    dirs = sorted([e for e in entries if e.is_dir()], key=lambda e: e.name)
    files = sorted([e for e in entries if e.is_file()], key=lambda e: e.name)

    summary = next((f for f in files if f.name == "SUMMARY.md"), None)
    other_files = [f for f in files if f.name != "SUMMARY.md"]

    display_path = params.path if params.path != "." else "/ (repo root)"
    lines: list[str] = [f"## {display_path}", ""]

    if not entries:
        lines.append("_(empty)_")
        return "\n".join(lines)

    if summary:
        lines.append(f"📄 **SUMMARY.md** ({_format_size(summary.stat().st_size)}) ← start here")
    for d in dirs:
        lines.append(f"📁 {d.name}/")
    for f in other_files:
        lines.append(f"📄 {f.name} ({_format_size(f.stat().st_size)})")

    lines.append("")
    lines.append(f"_{len(files)} file(s), {len(dirs)} folder(s)_")
    return "\n".join(lines)


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
async def memory_search(params: SearchInput) -> str:
    """Search for a string or regex pattern across files in the agent memory repository.

    Use this to locate a specific topic, trait, preference, or keyword without
    loading each file individually. Supports Python regex patterns. Useful when
    you need to find where a particular concept is documented. `HUMANS/` is
    excluded from ambient searches unless explicitly opted in or searched directly.

    Args:
        params (SearchInput):
            - query (str): Search string or Python regex (e.g., 'React', 'trust: high', 'skill-\\w+').
            - path (str): Folder to search within (default: '.', the whole repo).
            - glob_pattern (str): File filter glob (default: '**/*.md').
            - case_sensitive (bool): Case-sensitive match (default: False).
            - max_results (int): Max matching lines to return, 1–100 (default: 30).

    Returns:
        str: Matching lines grouped by file with line numbers, or a not-found message.

    Examples:
        - "Where is the user's preferred stack documented?" -> query='React', path='identity'
        - "Find all high-trust entries" -> query='trust: high', glob_pattern='**/*.md'
        - "Search ACCESS logs for a topic" -> query='topic', glob_pattern='**/ACCESS.jsonl'
        - "Locate a specific skill step" -> query='onboard', path='skills'
        - "Search the human docs tree intentionally" -> query='routing', path='.' include_humans=True

    Error cases:
        - Invalid regex: reports the pattern error with the offending expression
        - No matches: reports the count of files searched
    """
    try:
        search_root = _safe_resolve(params.path)
    except ValueError as e:
        return f"Error: {e}"

    if not search_root.is_dir():
        return f"Error: '{params.path}' is not a directory."

    try:
        flags = 0 if params.case_sensitive else re.IGNORECASE
        pattern = re.compile(params.query, flags)
    except re.error as e:
        return f"Error: Invalid regex pattern '{params.query}': {e}"

    output_blocks: list[str] = []
    total_matches = 0
    files_searched = 0
    results_remaining = params.max_results
    explicit_humans_search = _is_humans_path(search_root)

    for file_path in sorted(search_root.rglob(params.glob_pattern)):
        if any(part in IGNORED_NAMES for part in file_path.parts):
            continue
        if not file_path.is_file():
            continue
        if (
            not explicit_humans_search
            and not params.include_humans
            and _is_humans_path(file_path)
        ):
            continue

        files_searched += 1
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        file_hits: list[str] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                total_matches += 1
                if results_remaining > 0:
                    file_hits.append(f"  line {lineno}: {line.rstrip()}")
                    results_remaining -= 1

        if file_hits:
            rel = _repo_relative(file_path).as_posix()
            output_blocks.append(f"### {rel}\n" + "\n".join(file_hits))

    if not output_blocks:
        return (
            f"No matches for '{params.query}' in '{params.path}' "
            f"({files_searched} file(s) searched)."
        )

    truncation_note = (
        f" — showing first {params.max_results} of {total_matches}"
        if total_matches > params.max_results
        else ""
    )
    header = (
        f"## Search: '{params.query}'\n"
        f"_{total_matches} match(es) across {files_searched} file(s) searched{truncation_note}_\n"
    )
    return header + "\n\n".join(output_blocks)


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
    """Run the structural validator against the agent memory repository.

    Checks frontmatter keys and values, ACCESS.jsonl structure, and
    runtime-guidance consistency across governance files. Use after editing
    memory or governance files to catch inconsistencies early.

    Returns:
        str: Validation report with errors and warnings, or a clean-pass message.

    Error cases:
        - Validator script not found: reports the expected path
        - Validator times out: reports the timeout threshold
        - OS error launching validator: reports the system error
    """
    if not VALIDATOR_PATH.exists():
        return (
            f"Error: Validator not found at '{VALIDATOR_PATH.relative_to(REPO_ROOT)}'.\n"
            "The repository structure may have changed."
        )
    try:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(REPO_ROOT)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        output = "\n\n".join(part for part in (stdout, stderr) if part)

        if result.returncode == 0:
            body = f"\n\n{output}" if output else ""
            return f"✅ Validation passed.{body}"
        return f"❌ Validation failed (exit code {result.returncode}).\n\n{output}"
    except subprocess.TimeoutExpired:
        return "Error: Validator timed out after 30 seconds."
    except OSError as e:
        return f"Error launching validator: {e}"


# ── Entry point ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
