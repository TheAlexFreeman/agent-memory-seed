#!/usr/bin/env python3
"""Compatibility wrapper for the enhanced agent-memory MCP server."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

_server = importlib.import_module("tools.agent_memory_mcp.server")

__all__ = getattr(_server, "__all__", [])
globals().update({name: getattr(_server, name) for name in __all__})
mcp = _server.mcp


if __name__ == "__main__":
    mcp.run()
