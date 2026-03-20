"""Phase 3 semantic tool package.

This package becomes the stable import surface for Tier 1 semantic tools while
`semantic_tools.py` is gradually split into domain modules.
"""

from __future__ import annotations

from . import _session


def register(mcp, get_repo, get_root):
    """Register semantic tools through the new package surface.

    During the transition, delegate the full tool surface to the legacy module
    while the split proceeds incrementally.
    """
    from .. import semantic_tools as legacy_semantic_tools

    return legacy_semantic_tools.register(mcp, get_repo, get_root)


__all__ = ["register", "_session"]
