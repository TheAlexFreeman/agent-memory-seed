#!/usr/bin/env python3
"""Compatibility entrypoint for the repo-local Engram MCP server.

Prefer the installed ``engram-mcp`` CLI or
``python -m engram_mcp.agent_memory_mcp.server_main`` when available. This
wrapper remains for path-based client configs that launch the server directly
from a repository checkout.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_server = import_module("engram_mcp.agent_memory_mcp.server")

__all__ = getattr(_server, "__all__", [])
globals().update({name: getattr(_server, name) for name in __all__})
mcp = _server.mcp


if __name__ == "__main__":
    mcp.run()
