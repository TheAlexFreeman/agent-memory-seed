"""Session-state helpers for semantic tools."""

from __future__ import annotations

from typing import TypedDict


_IDENTITY_CHURN_LIMIT = 5


class SessionState(TypedDict):
    identity_updates: int


def create_session_state() -> SessionState:
    return {"identity_updates": 0}


def get_identity_churn_limit() -> int:
    return _IDENTITY_CHURN_LIMIT


def get_identity_updates(session_state: SessionState) -> int:
    return session_state["identity_updates"]


def increment_identity_updates(session_state: SessionState) -> int:
    session_state["identity_updates"] += 1
    return session_state["identity_updates"]


def reset_session_state(session_state: SessionState) -> dict[str, int | bool]:
    session_state["identity_updates"] = 0
    return {
        "reset": True,
        "identity_updates_this_session": 0,
    }


__all__ = [
    "SessionState",
    "create_session_state",
    "get_identity_churn_limit",
    "get_identity_updates",
    "increment_identity_updates",
    "reset_session_state",
]
