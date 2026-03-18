"""
Return types for all write tools.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryWriteResult:
    """Structured result returned by every write tool.

    Attributes:
        files_changed:  Repo-relative paths of all files written or staged.
        commit_sha:     Commit SHA if the operation auto-committed; None for
                        Tier 2 staged-only tools (call memory_commit to seal).
        commit_message: The commit message used, or None.
        new_state:      Operation-specific fields — eliminates read-after-write.
                        Examples:
                          mark_plan_item_complete → next_action, phase_progress, plan_progress, status
                          promote_knowledge       → new_path, trust
                          write                   → version_token
        warnings:       Non-fatal issues (e.g. SUMMARY.md section not found,
                        unrecognised commit prefix).
    """

    files_changed: list[str]
    commit_sha: str | None
    commit_message: str | None
    new_state: dict[str, Any]
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "files_changed": self.files_changed,
            "commit_sha": self.commit_sha,
            "commit_message": self.commit_message,
            "new_state": self.new_state,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
