"""Phase 3 semantic tool package.

This package becomes the stable import surface for Tier 1 semantic tools while
`semantic_tools.py` is gradually split into domain modules.
"""

from __future__ import annotations

from . import _session
from . import identity_tools
from . import knowledge_tools
from . import plan_tools


def register(mcp, get_repo, get_root):
    """Register semantic tools through the new package surface.

    During the transition, delegate the full tool surface to the legacy module
    while the split proceeds incrementally.
    """
    from .. import semantic_tools as legacy_semantic_tools

    session_state = _session.create_session_state()
    tools = {}
    tools.update(_session.register_tools(mcp, session_state))
    tools.update(plan_tools.register_tools(mcp, get_repo, get_root))
    tools.update(knowledge_tools.register_tools(mcp, get_repo, get_root))
    tools.update(identity_tools.register_tools(mcp, get_repo, session_state))
    tools.update(
        legacy_semantic_tools.register(
            mcp,
            get_repo,
            get_root,
            session_state=session_state,
            include_reset_tool=False,
            include_plan_tools=False,
            include_knowledge_tools=False,
            include_identity_tools=False,
        )
    )
    return tools


__all__ = ["register", "_session", "plan_tools", "knowledge_tools", "identity_tools"]
