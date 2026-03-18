#!/usr/bin/env python3
"""Resolve a repo bootstrap manifest into a concrete startup trace.

This is a repo-side prototype for the Codex desktop bootstrap-support plan.
It makes the manifest executable enough to test mode selection, preload order,
skip handling, and startup warnings before those behaviors exist app-side.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


BOOTSTRAP_MANIFEST = "agent-bootstrap.toml"
PLACEHOLDER_SNIPPETS = (
    "_Nothing here yet.",
    "_No pending items._",
    "_No current notes._",
)
EXPECTED_MODES = (
    "first_run",
    "returning",
    "full_bootstrap",
    "periodic_review",
    "automation",
)


@dataclass(frozen=True)
class GitState:
    current_branch: str | None
    detached_head: bool
    worktree_branch_drift: bool
    branch_checked_out_elsewhere: bool


@dataclass(frozen=True)
class StartupWarning:
    code: str
    message: str


@dataclass(frozen=True)
class StartupTraceStep:
    path: str
    role: str
    status: str
    required: bool
    cost: str
    reason: str | None = None


@dataclass(frozen=True)
class StartupResolution:
    router: str
    mode: str
    mode_source: str
    token_budget: int
    prefer_summaries: bool
    on_demand: list[str]
    maintenance_probes: list[str]
    git_state: GitState
    warnings: list[StartupWarning]
    trace: list[StartupTraceStep]


def normalize_manifest_path(raw_path: str) -> str:
    parts: list[str] = []
    for part in raw_path.replace("\\", "/").split("/"):
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def read_manifest(repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / BOOTSTRAP_MANIFEST
    return tomllib.loads(manifest_path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_frontmatter_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    text = read_text(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        candidate_key, candidate_value = line.split(":", 1)
        if candidate_key.strip() != key:
            continue
        return candidate_value.strip().strip('"')
    return None


def has_chat_history(repo_root: Path) -> bool:
    chats_root = repo_root / "chats"
    if not chats_root.exists():
        return False
    return any(chats_root.glob("*/*/*/chat-*"))


def repo_looks_first_run(repo_root: Path) -> bool:
    profile_source = parse_frontmatter_value(
        repo_root / "identity" / "profile.md", "source"
    )
    if has_chat_history(repo_root):
        return False
    return profile_source in {None, "template"}


def detect_mode(
    repo_root: Path,
    manifest: dict[str, Any],
    *,
    requested_mode: str = "auto",
    automation: bool = False,
    periodic_review: bool = False,
    fresh_instantiation: bool = False,
    full_bootstrap: bool = False,
) -> tuple[str, str]:
    if requested_mode != "auto":
        return requested_mode, "mode_override"
    if automation:
        return "automation", "automation_flag"
    if periodic_review:
        return "periodic_review", "periodic_review_flag"
    if repo_looks_first_run(repo_root):
        return "first_run", "first_run_heuristic"
    if fresh_instantiation:
        return "full_bootstrap", "fresh_instantiation_flag"
    if full_bootstrap:
        return "full_bootstrap", "full_bootstrap_flag"
    return str(manifest.get("default_mode", "returning")), "default_mode"


def run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def parse_worktree_list(output: str) -> list[dict[str, str]]:
    worktrees: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                worktrees.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value.strip()
    if current:
        worktrees.append(current)
    return worktrees


def detect_git_state(repo_root: Path, expected_branch: str | None = None) -> GitState:
    top_level = run_git(repo_root, "rev-parse", "--show-toplevel")
    if top_level.returncode != 0:
        return GitState(
            current_branch=None,
            detached_head=False,
            worktree_branch_drift=False,
            branch_checked_out_elsewhere=False,
        )

    branch_result = run_git(repo_root, "branch", "--show-current")
    current_branch = branch_result.stdout.strip() or None

    detached_head = False
    if current_branch is None:
        head_result = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")
        detached_head = head_result.returncode == 0 and head_result.stdout.strip() == "HEAD"

    worktree_branch_drift = False
    if expected_branch:
        if detached_head:
            worktree_branch_drift = True
        elif current_branch and current_branch != expected_branch:
            worktree_branch_drift = True

    target_branch = expected_branch or current_branch
    branch_checked_out_elsewhere = False
    if target_branch:
        worktree_result = run_git(repo_root, "worktree", "list", "--porcelain")
        if worktree_result.returncode == 0:
            current_worktree = top_level.stdout.strip()
            target_ref = f"refs/heads/{target_branch}"
            for worktree in parse_worktree_list(worktree_result.stdout):
                if worktree.get("branch") != target_ref:
                    continue
                if worktree.get("worktree") and worktree["worktree"] != current_worktree:
                    branch_checked_out_elsewhere = True
                    break

    return GitState(
        current_branch=current_branch,
        detached_head=detached_head,
        worktree_branch_drift=worktree_branch_drift,
        branch_checked_out_elsewhere=branch_checked_out_elsewhere,
    )


def is_placeholder_or_empty(path: Path) -> bool:
    if not path.exists():
        return True
    text = read_text(path).strip()
    if not text:
        return True
    return any(snippet in text for snippet in PLACEHOLDER_SNIPPETS)


def has_active_plans(path: Path) -> bool:
    if not path.exists():
        return False
    text = read_text(path)
    return "status: active" in text or "Priority order for active work:" in text


def resolve_skip_reason(path: Path, skip_if: str | None) -> str | None:
    if skip_if == "placeholder_or_empty" and is_placeholder_or_empty(path):
        return skip_if
    if skip_if == "no_active_plans" and not has_active_plans(path):
        return skip_if
    return None


def resolve_trace(
    repo_root: Path,
    steps: list[dict[str, Any]],
) -> list[StartupTraceStep]:
    trace: list[StartupTraceStep] = []
    seen_paths: set[str] = set()

    for step in steps:
        normalized_path = normalize_manifest_path(str(step["path"]))
        role = str(step["role"])
        required = bool(step["required"])
        cost = str(step["cost"])

        if normalized_path in seen_paths:
            trace.append(
                StartupTraceStep(
                    path=normalized_path,
                    role=role,
                    status="skipped",
                    required=required,
                    cost=cost,
                    reason="duplicate_path",
                )
            )
            continue

        seen_paths.add(normalized_path)
        target_path = repo_root / normalized_path
        if not target_path.exists():
            trace.append(
                StartupTraceStep(
                    path=normalized_path,
                    role=role,
                    status="missing",
                    required=required,
                    cost=cost,
                )
            )
            continue

        skip_reason = resolve_skip_reason(target_path, step.get("skip_if"))
        if skip_reason is not None:
            trace.append(
                StartupTraceStep(
                    path=normalized_path,
                    role=role,
                    status="skipped",
                    required=required,
                    cost=cost,
                    reason=skip_reason,
                )
            )
            continue

        trace.append(
            StartupTraceStep(
                path=normalized_path,
                role=role,
                status="loaded",
                required=required,
                cost=cost,
            )
        )

    return trace


def resolve_warnings(
    git_state: GitState,
    mode_detection: dict[str, Any],
    *,
    expected_branch: str | None = None,
) -> list[StartupWarning]:
    warnings: list[StartupWarning] = []

    if mode_detection.get("warn_on_detached_head") and git_state.detached_head:
        warnings.append(
            StartupWarning(
                code="detached_head",
                message="Repo is in detached HEAD state before startup.",
            )
        )

    if mode_detection.get("warn_on_worktree_branch_drift") and git_state.worktree_branch_drift:
        current = git_state.current_branch or "detached HEAD"
        target = expected_branch or "requested branch"
        warnings.append(
            StartupWarning(
                code="worktree_branch_drift",
                message=f"Current worktree is on {current}; expected {target}.",
            )
        )

    if (
        mode_detection.get("warn_on_branch_checked_out_elsewhere")
        and git_state.branch_checked_out_elsewhere
    ):
        target = expected_branch or git_state.current_branch or "requested branch"
        warnings.append(
            StartupWarning(
                code="branch_checked_out_elsewhere",
                message=f"Branch {target} is already checked out in another worktree.",
            )
        )

    return warnings


def resolve_startup(
    repo_root: Path,
    *,
    requested_mode: str = "auto",
    automation: bool = False,
    periodic_review: bool = False,
    fresh_instantiation: bool = False,
    full_bootstrap: bool = False,
    expected_branch: str | None = None,
    git_state: GitState | None = None,
) -> StartupResolution:
    manifest = read_manifest(repo_root)
    mode, mode_source = detect_mode(
        repo_root,
        manifest,
        requested_mode=requested_mode,
        automation=automation,
        periodic_review=periodic_review,
        fresh_instantiation=fresh_instantiation,
        full_bootstrap=full_bootstrap,
    )

    if mode not in EXPECTED_MODES:
        raise ValueError(f"Unsupported mode {mode!r}")

    mode_config = manifest["modes"][mode]
    current_git_state = git_state or detect_git_state(
        repo_root, expected_branch=expected_branch
    )
    return StartupResolution(
        router=str(manifest["router"]),
        mode=mode,
        mode_source=mode_source,
        token_budget=int(mode_config["token_budget"]),
        prefer_summaries=bool(mode_config["prefer_summaries"]),
        on_demand=[str(item) for item in mode_config.get("on_demand", [])],
        maintenance_probes=[
            str(item) for item in mode_config.get("maintenance_probes", [])
        ],
        git_state=current_git_state,
        warnings=resolve_warnings(
            current_git_state,
            manifest.get("mode_detection", {}),
            expected_branch=expected_branch,
        ),
        trace=resolve_trace(repo_root, list(mode_config["steps"])),
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve agent-bootstrap.toml into a concrete startup trace."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to the repo root containing agent-bootstrap.toml.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", *EXPECTED_MODES),
        default="auto",
        help="Force a mode instead of auto-detecting it.",
    )
    parser.add_argument(
        "--automation",
        action="store_true",
        help="Treat the run as a scheduled or recurring automation.",
    )
    parser.add_argument(
        "--periodic-review",
        action="store_true",
        help="Treat the run as a periodic governance review.",
    )
    parser.add_argument(
        "--fresh-instantiation",
        action="store_true",
        help="Treat the run as a fresh thread on a returning repo.",
    )
    parser.add_argument(
        "--full-bootstrap",
        action="store_true",
        help="Force the full-bootstrap route without using --mode.",
    )
    parser.add_argument(
        "--expected-branch",
        help="Expected branch for worktree-drift and branch-elsewhere warnings.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for output.",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv)
    repo_root = Path(args.repo_root).resolve()
    resolution = resolve_startup(
        repo_root,
        requested_mode=args.mode,
        automation=args.automation,
        periodic_review=args.periodic_review,
        fresh_instantiation=args.fresh_instantiation,
        full_bootstrap=args.full_bootstrap,
        expected_branch=args.expected_branch,
    )
    json.dump(asdict(resolution), sys.stdout, indent=args.indent)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
