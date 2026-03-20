"""Compatibility shim — re-exports from engram_mcp.agent_memory_mcp.

This module is a temporary backward-compatibility alias created during
Phase 0 of the MCP reorganization plan.  All new code should import from
``engram_mcp.agent_memory_mcp`` directly.  This shim will be removed in
Phase 2 once every direct ``tools.agent_memory_mcp.*`` import has been
updated.

Do **not** add new exports to this shim.
"""

from engram_mcp.agent_memory_mcp import (  # noqa: F401
    GIT_REPO,
    REPO_ROOT,
    TOOLS,
    create_mcp,
    mcp,
)

__all__ = ["GIT_REPO", "REPO_ROOT", "TOOLS", "create_mcp", "mcp"]
