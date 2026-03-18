"""Runtime bootstrap for the enhanced agent-memory MCP server."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .git_repo import GitRepo
from .tools import read_tools, semantic_tools, write_tools


DeletePermissionHook = Callable[[str], None]


def resolve_repo_root(explicit_root: str | Path | None = None) -> Path:
    """Resolve the memory repo root, supporting old and new env var names."""
    if explicit_root is not None:
        root = Path(explicit_root).resolve()
        if not root.is_dir():
            raise ValueError(f"Repository root is not a directory: {root}")
        return root

    for env_var in ("MEMORY_REPO_ROOT", "AGENT_MEMORY_ROOT"):
        env_value = os.environ.get(env_var)
        if not env_value:
            continue
        root = Path(env_value).resolve()
        if root.is_dir():
            return root
        print(
            f"Warning: {env_var}='{env_value}' is not a directory; falling back to"
            " file-relative detection.",
            file=sys.stderr,
        )

    return Path(__file__).resolve().parents[2]


def _build_delete_permission_hook(root: Path) -> DeletePermissionHook | None:
    """Build an optional delete-permission helper from the environment.

    If MEMORY_DELETE_PERMISSION_HELPER is set, it is executed with the target
    repo-relative path as its first argument before memory_delete removes the
    file. A non-zero exit status blocks the delete.
    """
    helper = os.environ.get("MEMORY_DELETE_PERMISSION_HELPER")
    if not helper:
        return None

    helper_path = Path(helper).expanduser()
    helper_cmd = str(helper_path if helper_path.is_absolute() else helper)

    def _grant(path: str) -> None:
        result = subprocess.run(
            [helper_cmd, path],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            message = (result.stderr or result.stdout).strip() or (
                f"{helper_cmd} exited with {result.returncode}"
            )
            raise RuntimeError(message)

    return _grant


def create_mcp(
    repo_root: str | Path | None = None,
    delete_permission_hook: DeletePermissionHook | None = None,
) -> tuple[FastMCP, dict[str, object], Path, GitRepo]:
    """Create the FastMCP app, register tools, and expose their callables."""
    root = resolve_repo_root(repo_root)
    repo = GitRepo(root)
    mcp = FastMCP("agent_memory_mcp")
    delete_permission_hook = (
        delete_permission_hook
        if delete_permission_hook is not None
        else _build_delete_permission_hook(root)
    )

    def get_repo() -> GitRepo:
        return repo

    def get_root() -> Path:
        return root

    tools: dict[str, object] = {}
    tools.update(read_tools.register(mcp, get_repo, get_root))
    tools.update(
        write_tools.register(
            mcp,
            get_repo,
            get_root,
            grant_delete_permission=delete_permission_hook,
        )
    )
    tools.update(semantic_tools.register(mcp, get_repo, get_root))
    return mcp, tools, root, repo


mcp, TOOLS, REPO_ROOT, GIT_REPO = create_mcp()
globals().update(TOOLS)

__all__ = ["GIT_REPO", "REPO_ROOT", "TOOLS", "create_mcp", "mcp", *sorted(TOOLS)]


if __name__ == "__main__":
    mcp.run()
