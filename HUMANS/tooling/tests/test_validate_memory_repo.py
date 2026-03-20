from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "validate_memory_repo.py"

SPEC = importlib.util.spec_from_file_location("validate_memory_repo", VALIDATOR_PATH)
assert SPEC is not None
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

INSPECTOR_PATH = (
    REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "inspect_compact_budget.py"
)
INSPECTOR_SPEC = importlib.util.spec_from_file_location("inspect_compact_budget", INSPECTOR_PATH)
assert INSPECTOR_SPEC is not None
inspector = importlib.util.module_from_spec(INSPECTOR_SPEC)
assert INSPECTOR_SPEC.loader is not None
sys.modules[INSPECTOR_SPEC.name] = inspector
INSPECTOR_SPEC.loader.exec_module(inspector)

PROMPT_START_LINE = validator.PROMPT_START_LINE
PROMPT_ROUTE_LINE = validator.PROMPT_ROUTE_LINE
PROMPT_MCP_LINE = validator.PROMPT_MCP_LINE
LIVE_CONFIG_LINE = validator.LIVE_CONFIG_LINE
ADAPTER_ROUTING_LINE = validator.ADAPTER_ROUTING_PHRASE
ADAPTER_MCP_LINE = validator.ADAPTER_MCP_PHRASE
FIRST_RUN_MCP_LINE = validator.FIRST_RUN_MCP_PHRASE
SESSION_CHECKLISTS_MCP_LINE = validator.SESSION_CHECKLISTS_MCP_PHRASE
SKILLS_SUMMARY_MCP_LINE = validator.SKILLS_SUMMARY_MCP_PHRASE
ONBOARDING_SKILL_MCP_LINE = validator.ONBOARDING_SKILL_MCP_PHRASE
SESSION_START_SKILL_MCP_LINE = validator.SESSION_START_SKILL_MCP_PHRASE
SESSION_SYNC_SKILL_MCP_LINE = validator.SESSION_SYNC_SKILL_MCP_PHRASE
SESSION_WRAPUP_SKILL_MCP_LINE = validator.SESSION_WRAPUP_SKILL_MCP_PHRASE
SETUP_GUIDANCE_LINE = "live routing in `meta/quick-reference.md`"


VALID_QUICK_REFERENCE = textwrap.dedent(
    """\
    # Quick Reference

    **Read this file at the start of every session before applying any thresholds or curation rules.**

    This is the single authoritative source for active operational parameters.

    ## Session routing

    Use this file as the operational router for every session:

    1. Start here.
    2. If this is a fresh instantiation on a blank or template-backed repo, read `README.md` and then `meta/first-run.md`.
    3. If this is a fresh instantiation on a returning system, or you intentionally need the full governance stack, read `README.md` and then follow the **Full bootstrap** manifest below.
    4. Otherwise, use the **Compact returning** manifest below and keep additional loads task-driven.

    ## Context loading manifest

    | Session type | Files to load |
    |---|---|
    | **First run** | `README.md` → `meta/first-run.md` |
    | **Compact returning** | this file → `identity/SUMMARY.md` → `chats/SUMMARY.md` _(skip if empty)_ → `plans/SUMMARY.md` _(skip if no active plans)_ → `scratchpad/USER.md` _(skip if only placeholder)_ → `scratchpad/CURRENT.md` _(skip if only placeholder)_ → task-relevant `knowledge/SUMMARY.md` and/or `skills/SUMMARY.md` only when the current task or recent history makes them relevant |
    | **Full bootstrap** | `README.md` → Compact returning files + `CHANGELOG.md`, `meta/curation-policy.md`, `meta/update-guidelines.md` |
    | **Periodic review** | Full bootstrap files + `meta/system-maturity.md`, `meta/belief-diff-log.md`, `meta/review-queue.md`, `meta/integrity-checklist.md` |
    | **ACCESS aggregation** | This file + `meta/curation-algorithms.md` |
    | **Stage transition** | Periodic review files + `meta/curation-algorithms.md` |

    **Do not load** `HUMANS/docs/*`. `meta/session-checklists.md` and `meta/scratchpad-guidelines.md` are on-demand only.

    ### Compact returning notes

    - Run metadata-first maintenance probes before loading extra governance files.
    - Check whether `meta/review-queue.md` still contains only its placeholder.
    - Count non-empty lines in `ACCESS.jsonl` files to see whether any folder has reached the aggregation trigger.
    - `knowledge/SUMMARY.md` and `skills/SUMMARY.md` are task-driven context, not unconditional startup reads.
    - In worktree mode, use `host_repo_root` from `agent-bootstrap.toml` for host-code git operations and the worktree path for memory files and governance.

    ## Compact bootstrap contract

    **Startup strategy:** Whole-file compact mode.

    | File | Keep in compact path | Move to drill-down files | Target budget |
    |---|---|---|---|
    | `meta/quick-reference.md` | Routing and thresholds | Longer rationale | ~2,600 tokens |
    | `identity/SUMMARY.md` | User portrait | Detailed evidence | ~450 tokens |
    | `chats/SUMMARY.md` | Themes and retrieval guidance | Narrative history | ~750 tokens |
    | `plans/SUMMARY.md` | Active plans and next actions | Full plan detail | ~1,700 tokens |
    | `scratchpad/USER.md` | Current user notes | Older context | ~400 tokens |
    | `scratchpad/CURRENT.md` | Active threads and refs | Extended analysis | ~650 tokens |

    ## Compact file success criteria

    - `plans/SUMMARY.md` must preserve active-plan priority and next actions.
    - `chats/SUMMARY.md` must preserve current themes and retrieval guidance.
    - `scratchpad/CURRENT.md` must preserve active threads and drill-down refs.

    ## Current active stage: Exploration

    _Last assessed: not yet assessed — Exploration defaults apply_

    ## Active thresholds

    | Parameter | Active value | Stage |
    |-----------|-------------|-------|
    | Low-trust retirement threshold | 120 days | Exploration |
    | Medium-trust flagging threshold | 180 days | Exploration |
    | Staleness trigger (no access) | 120 days | Exploration |
    | Aggregation trigger | 15 entries | Exploration |
    | Identity churn alarm | 5 traits/session | Exploration |
    | Knowledge flooding alarm | 5 files/day | Exploration |
    | Task similarity method | Session co-occurrence | Exploration |
    | Cluster co-retrieval threshold | 3 sessions | Exploration |

    ## Active task similarity method

    **Grouping precedence:** Group ACCESS entries by `session_id` when present, then fall back to `date`.

    ## Context budget guideline

    | Session mode | Typical token cost | When |
    | --- | --- | --- |
    | First-run onboarding bootstrap | ~15,000–20,000 | Fresh model instantiation on a blank or template-backed repo |
    | Returning compact session | ~3,000–7,000 | Normal day-to-day use via the compact returning manifest in this file |
    | Full bootstrap / periodic review | ~18,000–25,000 | Fresh model on a returning system, or sessions that reopen the full governance stack and review artifacts |
    """
)

VALID_BOOTSTRAP_MANIFEST = textwrap.dedent(
    """\
    version = 1
    router = "meta/quick-reference.md"
    default_mode = "returning"
    adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]

    [mode_detection]
    automation = "scheduled_or_recurring_run"
    periodic_review = "explicit_or_scheduled_governance_review"
    first_run = "blank_or_template_backed_repo"
    full_bootstrap = "fresh_instantiation_on_returning_repo"
    returning = "default_existing_repo_session"
    warn_on_detached_head = true
    warn_on_worktree_branch_drift = true
    warn_on_branch_checked_out_elsewhere = true

    [modes.first_run]
    token_budget = 20000
    prefer_summaries = false

    [[modes.first_run.steps]]
    path = "meta/quick-reference.md"
    role = "router"
    required = true
    cost = "light"

    [[modes.first_run.steps]]
    path = "README.md"
    role = "architecture-reference"
    required = true
    cost = "medium"

    [[modes.first_run.steps]]
    path = "meta/first-run.md"
    role = "first-run-manifest"
    required = true
    cost = "light"

    [modes.returning]
    token_budget = 7000
    prefer_summaries = true
    maintenance_probes = [
      "meta/review-queue.md:load_only_when_non_placeholder",
      "ACCESS.jsonl:count_non_empty_lines",
    ]
    on_demand = ["knowledge/SUMMARY.md", "skills/SUMMARY.md"]

    [[modes.returning.steps]]
    path = "meta/quick-reference.md"
    role = "router"
    required = true
    cost = "light"

    [[modes.returning.steps]]
    path = "identity/SUMMARY.md"
    role = "identity-summary"
    required = true
    cost = "light"

    [[modes.returning.steps]]
    path = "chats/SUMMARY.md"
    role = "chat-summary"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.returning.steps]]
    path = "plans/SUMMARY.md"
    role = "plan-summary"
    required = false
    skip_if = "no_active_plans"
    cost = "light"

    [[modes.returning.steps]]
    path = "scratchpad/USER.md"
    role = "scratchpad-user"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.returning.steps]]
    path = "scratchpad/CURRENT.md"
    role = "scratchpad-current"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [modes.full_bootstrap]
    token_budget = 25000
    prefer_summaries = true
    maintenance_probes = [
      "meta/review-queue.md:load_only_when_non_placeholder",
      "ACCESS.jsonl:count_non_empty_lines",
    ]
    on_demand = ["knowledge/SUMMARY.md", "skills/SUMMARY.md"]

    [[modes.full_bootstrap.steps]]
    path = "meta/quick-reference.md"
    role = "router"
    required = true
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "README.md"
    role = "architecture-reference"
    required = true
    cost = "medium"

    [[modes.full_bootstrap.steps]]
    path = "identity/SUMMARY.md"
    role = "identity-summary"
    required = true
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "chats/SUMMARY.md"
    role = "chat-summary"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "plans/SUMMARY.md"
    role = "plan-summary"
    required = false
    skip_if = "no_active_plans"
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "scratchpad/USER.md"
    role = "scratchpad-user"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "scratchpad/CURRENT.md"
    role = "scratchpad-current"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.full_bootstrap.steps]]
    path = "CHANGELOG.md"
    role = "system-history"
    required = true
    cost = "medium"

    [[modes.full_bootstrap.steps]]
    path = "meta/curation-policy.md"
    role = "governance-reference"
    required = true
    cost = "medium"

    [[modes.full_bootstrap.steps]]
    path = "meta/update-guidelines.md"
    role = "change-control"
    required = true
    cost = "medium"

    [modes.periodic_review]
    token_budget = 25000
    prefer_summaries = true
    maintenance_probes = [
      "meta/review-queue.md:load_only_when_non_placeholder",
      "ACCESS.jsonl:count_non_empty_lines",
    ]
    on_demand = ["knowledge/SUMMARY.md", "skills/SUMMARY.md"]

    [[modes.periodic_review.steps]]
    path = "meta/quick-reference.md"
    role = "router"
    required = true
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "README.md"
    role = "architecture-reference"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "identity/SUMMARY.md"
    role = "identity-summary"
    required = true
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "chats/SUMMARY.md"
    role = "chat-summary"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "plans/SUMMARY.md"
    role = "plan-summary"
    required = false
    skip_if = "no_active_plans"
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "scratchpad/USER.md"
    role = "scratchpad-user"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "scratchpad/CURRENT.md"
    role = "scratchpad-current"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "CHANGELOG.md"
    role = "system-history"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "meta/curation-policy.md"
    role = "governance-reference"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "meta/update-guidelines.md"
    role = "change-control"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "meta/system-maturity.md"
    role = "stage-reference"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "meta/belief-diff-log.md"
    role = "drift-audit"
    required = true
    cost = "medium"

    [[modes.periodic_review.steps]]
    path = "meta/review-queue.md"
    role = "pending-proposals"
    required = true
    cost = "light"

    [[modes.periodic_review.steps]]
    path = "meta/integrity-checklist.md"
    role = "integrity-audit"
    required = true
    cost = "medium"

    [modes.automation]
    token_budget = 7000
    prefer_summaries = true
    maintenance_probes = [
      "meta/review-queue.md:load_only_when_non_placeholder",
      "ACCESS.jsonl:count_non_empty_lines",
    ]
    on_demand = ["knowledge/SUMMARY.md", "skills/SUMMARY.md"]

    [[modes.automation.steps]]
    path = "meta/quick-reference.md"
    role = "router"
    required = true
    cost = "light"

    [[modes.automation.steps]]
    path = "scratchpad/USER.md"
    role = "scratchpad-user"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.automation.steps]]
    path = "scratchpad/CURRENT.md"
    role = "scratchpad-current"
    required = false
    skip_if = "placeholder_or_empty"
    cost = "light"

    [[modes.automation.steps]]
    path = "plans/SUMMARY.md"
    role = "plan-summary"
    required = false
    skip_if = "no_active_plans"
    cost = "light"
    """
)
VALID_TASK_READINESS_MANIFEST = (
    REPO_ROOT / "HUMANS" / "tooling" / "agent-task-readiness.toml"
).read_text(encoding="utf-8")
VALID_CAPABILITIES_MANIFEST = (
    REPO_ROOT / "HUMANS" / "tooling" / "agent-memory-capabilities.toml"
).read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def git_available() -> bool:
    return shutil.which("git") is not None


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def build_minimal_repo(root: Path) -> None:
    write(root / "agent-bootstrap.toml", VALID_BOOTSTRAP_MANIFEST)
    write(
        root / "HUMANS" / "tooling" / "agent-task-readiness.toml",
        VALID_TASK_READINESS_MANIFEST,
    )
    write(
        root / "HUMANS" / "tooling" / "scripts" / "resolve_task_readiness.py",
        "#!/usr/bin/env python3\n",
    )
    write(root / "HUMANS" / "tooling" / "agent-memory-capabilities.toml", VALID_CAPABILITIES_MANIFEST)
    write(root / "engram_mcp" / "__init__.py", "\n")
    write(root / "engram_mcp" / "memory_mcp.py", "#!/usr/bin/env python3\n")
    write(
        root / "README.md",
        textwrap.dedent(
            """\
            # README

            Start every session with `meta/quick-reference.md`.
            Read this file in full when `meta/quick-reference.md` routes you to a first run, full bootstrap, or periodic review.
            When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation.
            """
        ),
    )
    write(root / "CHANGELOG.md", "# Changelog\n")
    write(
        root / "setup.sh",
        textwrap.dedent(
            """\
            #!/usr/bin/env bash
            set -euo pipefail
            exec bash "$(pwd)/setup/setup.sh" "$@"
            """
        ),
    )
    write(
        root / "setup.html",
        '<!DOCTYPE html><html><body><a href="setup/setup.html">setup/setup.html</a></body></html>\n',
    )
    write(
        root / "setup" / "setup.sh",
        textwrap.dedent(
            f"""\
            #!/usr/bin/env bash
            {PROMPT_START_LINE}
            {PROMPT_ROUTE_LINE}
            {PROMPT_MCP_LINE}
            {LIVE_CONFIG_LINE}
            {SETUP_GUIDANCE_LINE}
            """
        ),
    )
    write(
        root / "setup" / "setup.html",
        textwrap.dedent(
            f"""\
            <!DOCTYPE html>
            <html>
            <body>
            <p>{PROMPT_START_LINE}</p>
            <p>{PROMPT_ROUTE_LINE}</p>
            <p>{PROMPT_MCP_LINE}</p>
            <p>{LIVE_CONFIG_LINE}</p>
            git remote setup stays manual
            </body>
            </html>
            """
        ),
    )
    write(
        root / "AGENTS.md",
        (
            "# Agent Memory System\n\n"
            f"This repository is a persistent AI memory system. At the start of every session, {ADAPTER_ROUTING_LINE}. "
            f"{ADAPTER_MCP_LINE}; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation. "
            "Do not duplicate the full rule list here — `README.md` and `meta/` are the single source of truth.\n"
        ),
    )
    write(root / "CLAUDE.md", (root / "AGENTS.md").read_text(encoding="utf-8"))
    write(root / ".cursorrules", (root / "AGENTS.md").read_text(encoding="utf-8"))

    (root / "HUMANS" / "docs").mkdir(parents=True, exist_ok=True)
    write(
        root / "HUMANS" / "docs" / "QUICKSTART.md",
        textwrap.dedent(
            f"""\
            # Quickstart

            ```bash
            bash setup.sh
            ```

            Open `setup.html` in any browser. Git remote setup stays manual.

            {PROMPT_START_LINE}
            {PROMPT_ROUTE_LINE}
            {PROMPT_MCP_LINE}
            {LIVE_CONFIG_LINE}
            {SETUP_GUIDANCE_LINE}

            | Session mode | Typical token cost | When |
            | --- | --- | --- |
            | First-run onboarding bootstrap | ~15,000–20,000 | Fresh model instantiation on a blank or template-backed repo |
            | Returning compact session | ~3,000–7,000 | Normal day-to-day use via the compact returning manifest in `meta/quick-reference.md` |
            | Full bootstrap / periodic review | ~18,000–25,000 | Fresh model on a returning system, or sessions that reopen the full governance stack and review artifacts |
            """
        ),
    )
    write(
        root / "HUMANS" / "tooling" / "onboard-export-template.md",
        textwrap.dedent(
            """\
            # Onboarding Export

            Save it to a file and run `bash HUMANS/tooling/scripts/onboard-export.sh <file>`.
            """
        ),
    )

    write(root / "meta" / "quick-reference.md", VALID_QUICK_REFERENCE)
    write(
        root / "meta" / "first-run.md",
        f"# First run\n\n{FIRST_RUN_MCP_LINE}\n",
    )
    write(
        root / "meta" / "curation-policy.md",
        "# Curation Policy\nUse `meta/quick-reference.md` for live thresholds.\n",
    )
    write(
        root / "meta" / "update-guidelines.md",
        "# Update Guidelines\nRead-only operation is documented here.\n",
    )
    write(
        root / "meta" / "session-checklists.md",
        (
            "# Session checklists\n"
            "Load this file on demand when you need more detail than the compact manifest in `meta/quick-reference.md`.\n\n"
            f"{SESSION_CHECKLISTS_MCP_LINE}\n"
        ),
    )
    write(root / "meta" / "review-queue.md", "# Review Queue\n\n_No pending items._\n")
    write(root / "meta" / "system-maturity.md", "# System maturity\n")
    write(root / "meta" / "belief-diff-log.md", "# Belief diff log\n")
    write(root / "meta" / "integrity-checklist.md", "# Integrity checklist\n")

    for dirname in ("identity", "knowledge", "skills", "plans", "chats"):
        write(root / dirname / "SUMMARY.md", f"# {dirname} summary\n")
        write(root / dirname / "ACCESS.jsonl", "")

    write(
        root / "chats" / "SUMMARY.md",
        "# Chats Summary\n\n_Nothing here yet._\n",
    )
    write(
        root / "plans" / "SUMMARY.md",
        "# Plans — Summary\n\n## Active plans\n\n_No active plans._\n\n## Recent completions\n\n_None yet._\n",
    )

    write(
        root / "skills" / "SUMMARY.md",
        f"# Skills summary\n\n{SKILLS_SUMMARY_MCP_LINE}\n",
    )
    write(
        root / "skills" / "onboarding.md",
        textwrap.dedent(
            f"""\
            ---
            source: user-stated
            origin_session: manual
            created: 2026-03-16
            last_verified: 2026-03-16
            trust: high
            ---

            # Onboarding

            {ONBOARDING_SKILL_MCP_LINE}
            """
        ),
    )
    write(
        root / "skills" / "session-sync.md",
        textwrap.dedent(
            f"""\
            ---
            source: user-stated
            origin_session: manual
            created: 2026-03-16
            last_verified: 2026-03-16
            trust: high
            ---

            # Session sync

            {SESSION_SYNC_SKILL_MCP_LINE}
            """
        ),
    )

    write(
        root / "scratchpad" / "USER.md",
        "# User notes\n\n_Nothing here yet. Add any context you'd like the agent to pick up at session start._\n",
    )
    write(
        root / "scratchpad" / "CURRENT.md",
        "# Agent working notes\n\n_No current notes._\n",
    )


def init_host_git_repo(root: Path) -> None:
    git(root, "init", "--initial-branch=core")
    git(root, "config", "user.name", "Test User")
    git(root, "config", "user.email", "test@example.com")
    write(root / "src" / "app.py", "print('host repo')\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "host init")


def add_host_repo_root(manifest_path: Path, host_root: Path) -> None:
    text = manifest_path.read_text(encoding="utf-8")
    host_line = f'host_repo_root = "{host_root.as_posix()}"'
    if "host_repo_root = " in text:
        text = re.sub(r'^host_repo_root = ".*"$', host_line, text, count=1, flags=re.MULTILINE)
    else:
        text = text.replace(
            'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]',
            'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\n' + host_line,
            1,
        )
    manifest_path.write_text(text, encoding="utf-8")


def write_host_adapter_files(host_root: Path, *, duplicate_from: Path | None = None) -> None:
    for relative_path in ("AGENTS.md", "CLAUDE.md", ".cursorrules"):
        target = host_root / relative_path
        if duplicate_from is not None:
            target.write_text(
                (duplicate_from / relative_path).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        else:
            target.write_text(
                f"# Host adapter\n\nThis host repo stores memory in a separate worktree. ({relative_path})\n",
                encoding="utf-8",
            )


def build_worktree_repo(
    host_root: Path,
    memory_root: Path,
    *,
    orphan_branch: bool = True,
    include_host_repo_root: bool = True,
) -> None:
    if not git_available():
        raise unittest.SkipTest("git is not available in this environment")

    init_host_git_repo(host_root)
    temp_worktree = host_root / ".git" / "validator-memory-temp"

    if orphan_branch:
        git(host_root, "worktree", "add", "--detach", str(temp_worktree), "HEAD")
        git(temp_worktree, "checkout", "--orphan", "agent-memory")
    else:
        git(host_root, "worktree", "add", "-b", "agent-memory", str(temp_worktree), "core")

    subprocess.run(
        ["git", "rm", "-rf", "--ignore-unmatch", "."],
        cwd=temp_worktree,
        check=True,
        capture_output=True,
        text=True,
    )

    build_minimal_repo(temp_worktree)
    if include_host_repo_root:
        add_host_repo_root(temp_worktree / "agent-bootstrap.toml", host_root)
    write_host_adapter_files(host_root)

    git(temp_worktree, "add", "--all")
    git(temp_worktree, "commit", "-m", "seed memory")
    git(host_root, "worktree", "remove", "--force", str(temp_worktree))
    git(host_root, "worktree", "add", str(memory_root), "agent-memory")


class ValidateMemoryRepoTests(unittest.TestCase):
    def test_current_seed_repo_passes_validation(self) -> None:
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_access_entries_with_and_without_session_id_and_unknown_source_pass(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "example.md",
                textwrap.dedent(
                    """\
                    ---
                    source: unknown
                    origin_session: unknown
                    created: 2026-03-16
                    trust: medium
                    ---

                    # Example
                    """
                ),
            )
            write(
                root / "skills" / "ACCESS.jsonl",
                "\n".join(
                    (
                        '{"file":"skills/example.md","date":"2026-03-16","task":"test","helpfulness":0.7,"note":"used"}',
                        '{"file":"skills/example.md","date":"2026-03-16","task":"test","helpfulness":0.8,"note":"used","session_id":"chats/2026/03/16/chat-001"}',
                    )
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_missing_bootstrap_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "agent-bootstrap.toml").unlink()

            result = validator.validate_repo(root)
            self.assertTrue(any("missing bootstrap manifest" in error for error in result.errors))

    def test_missing_mcp_entrypoint_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "engram_mcp" / "memory_mcp.py").unlink()

            result = validator.validate_repo(root)
            self.assertTrue(
                any("missing MCP entrypoint script" in error for error in result.errors)
            )

    def test_legacy_tools_runtime_directory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "tools").mkdir(parents=True, exist_ok=True)

            result = validator.validate_repo(root)
            self.assertTrue(
                any("legacy tools/ runtime directory must not exist" in error for error in result.errors)
            )

    def test_capabilities_manifest_with_wrong_mcp_entrypoint_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "HUMANS" / "tooling" / "agent-memory-capabilities.toml",
                VALID_CAPABILITIES_MANIFEST.replace(
                    'mcp_entrypoint = "engram_mcp/memory_mcp.py"',
                    'mcp_entrypoint = "HUMANS/tooling/scripts/memory_mcp.py"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("mcp_entrypoint must be 'engram_mcp/memory_mcp.py'" in error for error in result.errors)
            )

    def test_missing_task_readiness_manifest_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            (root / "HUMANS" / "tooling" / "agent-task-readiness.toml").unlink()

            result = validator.validate_repo(root)
            self.assertTrue(
                any("missing task-readiness manifest" in error for error in result.errors)
            )

    def test_task_readiness_manifest_with_wrong_default_profile_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "HUMANS" / "tooling" / "agent-task-readiness.toml",
                VALID_TASK_READINESS_MANIFEST.replace(
                    'default_profile = "workspace_general"',
                    'default_profile = "pull_request"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "task_detection.default_profile must be 'workspace_general'" in error
                    for error in result.errors
                )
            )

    def test_task_readiness_manifest_with_unknown_check_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "HUMANS" / "tooling" / "agent-task-readiness.toml",
                VALID_TASK_READINESS_MANIFEST.replace(
                    'checks = ["git_cli", "git_remote", "git_push_dry_run", "gh_auth", "remote_network"]',
                    'checks = ["git_cli", "missing_check"]',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("references unknown check 'missing_check'" in error for error in result.errors)
            )

    def test_bootstrap_manifest_with_wrong_router_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "agent-bootstrap.toml",
                VALID_BOOTSTRAP_MANIFEST.replace(
                    'router = "meta/quick-reference.md"',
                    'router = "README.md"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("router must be 'meta/quick-reference.md'" in error for error in result.errors)
            )

    def test_bootstrap_manifest_with_wrong_returning_order_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "agent-bootstrap.toml",
                VALID_BOOTSTRAP_MANIFEST.replace(
                    'path = "identity/SUMMARY.md"',
                    'path = "knowledge/SUMMARY.md"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("modes.returning.steps must load" in error for error in result.errors)
            )

    def test_bootstrap_manifest_with_relative_host_repo_root_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "agent-bootstrap.toml",
                VALID_BOOTSTRAP_MANIFEST.replace(
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]',
                    'adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]\nhost_repo_root = "../host-repo"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("host_repo_root must be an absolute path" in error for error in result.errors)
            )

    def test_valid_worktree_bootstrap_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            host_root = Path(tempdir) / "host"
            memory_root = Path(tempdir) / "memory"
            host_root.mkdir(parents=True, exist_ok=True)
            build_worktree_repo(host_root, memory_root)

            result = validator.validate_repo(memory_root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertEqual(result.warnings, [], "\n".join(result.warnings))

    def test_worktree_without_host_repo_root_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            host_root = Path(tempdir) / "host"
            memory_root = Path(tempdir) / "memory"
            host_root.mkdir(parents=True, exist_ok=True)
            build_worktree_repo(host_root, memory_root, include_host_repo_root=False)

            result = validator.validate_repo(memory_root)
            self.assertTrue(
                any("host_repo_root is required when validating a git worktree checkout" in error for error in result.errors)
            )

    def test_worktree_host_repo_root_inside_memory_root_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            host_root = Path(tempdir) / "host"
            memory_root = Path(tempdir) / "memory"
            host_root.mkdir(parents=True, exist_ok=True)
            build_worktree_repo(host_root, memory_root)
            add_host_repo_root(memory_root / "agent-bootstrap.toml", memory_root / "knowledge")

            result = validator.validate_repo(memory_root)
            self.assertTrue(
                any("host_repo_root must not point inside the memory repo root" in error for error in result.errors)
            )

    def test_worktree_shared_history_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            host_root = Path(tempdir) / "host"
            memory_root = Path(tempdir) / "memory"
            host_root.mkdir(parents=True, exist_ok=True)
            build_worktree_repo(host_root, memory_root, orphan_branch=False)

            result = validator.validate_repo(memory_root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(
                any("shares history with host default branch" in warning for warning in result.warnings)
            )

    def test_worktree_duplicate_host_adapters_warn(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            host_root = Path(tempdir) / "host"
            memory_root = Path(tempdir) / "memory"
            host_root.mkdir(parents=True, exist_ok=True)
            build_worktree_repo(host_root, memory_root)
            write_host_adapter_files(host_root, duplicate_from=memory_root)

            result = validator.validate_repo(memory_root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(
                any("duplicates host-root adapter file" in warning for warning in result.warnings)
            )

    def test_compact_startup_budget_overrun_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "scratchpad" / "CURRENT.md",
                "# Agent working notes\n\n"
                + "## Active threads\n\n- "
                + ("very long note " * 800)
                + "\n\n## Immediate next actions\n\n- Trim this file\n\n## Open questions\n\n- How much is too much?\n\n## Drill-down refs\n\n- plans/compact-bootstrap-efficiency.md\n",
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "compact startup file uses ~" in error
                    or "compact returning startup uses ~" in error
                    for error in result.errors
                )
            )

    def test_chats_summary_with_chat_by_chat_heading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "chats" / "SUMMARY.md",
                textwrap.dedent(
                    """\
                    # Chats Summary

                    ## Live themes

                    - Theme

                    ## Recent continuity

                    - Continuity

                    ## Retrieval guide

                    - Load dated summaries when needed.

                    ### chat-001

                    Too much narrative.
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "chat-by-chat narrative headings are too detailed" in error
                    for error in result.errors
                )
            )

    def test_plans_summary_without_detail_reference_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "plans" / "SUMMARY.md",
                textwrap.dedent(
                    """\
                    # Plans — Summary

                    ## Active plans

                    <!-- BEGIN: example -->
                    ### `example.md` · status: active · trust: medium
                    Scope: Example scope
                    Progress: 0/2 complete
                    Next: Do first step
                    <!-- END: example -->

                    ## Recent completions

                    - [done.md](done.md) — done
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "must include a drill-down reference to plans/example.md" in error
                    for error in result.errors
                )
            )

    def test_bootstrap_manifest_missing_optional_skip_rule_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "agent-bootstrap.toml",
                VALID_BOOTSTRAP_MANIFEST.replace(
                    '[[modes.returning.steps]]\npath = "chats/SUMMARY.md"\nrole = "chat-summary"\nrequired = false\nskip_if = "placeholder_or_empty"\ncost = "light"',
                    '[[modes.returning.steps]]\npath = "chats/SUMMARY.md"\nrole = "chat-summary"\nrequired = false\ncost = "light"',
                    1,
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "must use skip_if = 'placeholder_or_empty'" in error
                    for error in result.errors
                )
            )

    def test_compact_budget_inspector_reports_file_breakdown(self) -> None:
        report = inspector.build_report(REPO_ROOT)

        self.assertIn("status", report)
        self.assertIn("total_tokens", report)
        self.assertIn("files", report)
        self.assertTrue(any(entry["path"] == "meta/quick-reference.md" for entry in report["files"]))
        self.assertEqual(
            report["budget_limit"],
            validator.COMPACT_RETURNING_BUDGET,
        )

    def test_access_entry_with_malformed_session_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "example.md",
                textwrap.dedent(
                    """\
                    ---
                    source: unknown
                    origin_session: unknown
                    created: 2026-03-16
                    trust: medium
                    ---

                    # Example
                    """
                ),
            )
            write(
                root / "skills" / "ACCESS.jsonl",
                '{"file":"skills/example.md","date":"2026-03-16","task":"test","helpfulness":0.8,"note":"used","session_id":"chat-001"}',
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "session_id must match chats/YYYY/MM/DD/chat-NNN" in error
                    for error in result.errors
                )
            )

    def test_invalid_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "example.md",
                textwrap.dedent(
                    """\
                    ---
                    source: generated
                    origin_session: unknown
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: medium
                    ---

                    # Example
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(any("invalid source" in error for error in result.errors))

    def test_template_source_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: template
                    origin_session: setup
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: medium
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_agent_generated_plan_with_required_fields_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "plans" / "roadmap.md",
                textwrap.dedent(
                    """\
                    ---
                    source: agent-generated
                    type: implementation-plan
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: medium
                    status: active
                    next_action: "Implement phase 1"
                    ---

                    # Roadmap
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_plan_missing_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "plans" / "roadmap.md",
                textwrap.dedent(
                    """\
                    ---
                    source: agent-generated
                    type: implementation-plan
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: medium
                    next_action: "Implement phase 1"
                    ---

                    # Roadmap
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "plan files must define frontmatter key 'status'" in error
                    for error in result.errors
                )
            )

    def test_missing_optional_last_verified_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertEqual(result.warnings, [], "\n".join(result.warnings))

    def test_invalid_optional_last_verified_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: not-a-date
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "last_verified must be a valid YYYY-MM-DD date" in error
                    for error in result.errors
                )
            )

    def test_malformed_access_jsonl_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.jsonl",
                '{"file":"skills/example.md","date":"2026-03-16","task":"test"',
            )

            result = validator.validate_repo(root)
            self.assertTrue(any("malformed JSON" in error for error in result.errors))

    def test_missing_frontmatter_key_fails_when_frontmatter_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "example.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    ---

                    # Example
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("missing required frontmatter keys" in error for error in result.errors)
            )

    def test_canonical_origin_session_path_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertEqual(result.warnings, [], "\n".join(result.warnings))

    def test_legacy_origin_session_warns_but_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(any("legacy origin_session" in warning for warning in result.warnings))

    def test_malformed_origin_session_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: chats/2026/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(any("origin_session must be" in error for error in result.errors))

    def test_runtime_guidance_pointing_to_system_maturity_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "meta" / "curation-policy.md",
                "# Curation Policy\nCheck the current maturity stage in `meta/system-maturity.md`.\n",
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("forbidden runtime guidance pattern" in error for error in result.errors)
            )

    def test_session_start_skill_with_readme_bootstrap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "session-start.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: manual
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    Run at the beginning of every session after the bootstrap sequence completes (i.e., after README.md has been read and the agent is oriented).

                    - Read `meta/review-queue.md`. Are there pending proposals the user hasn't reviewed?
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("forbidden startup-skill pattern" in error for error in result.errors)
            )

    def test_session_start_skill_with_compact_manifest_guidance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "session-start.md",
                textwrap.dedent(
                    f"""\
                    ---
                    source: user-stated
                    origin_session: manual
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    For normal returning sessions, follow the compact returning manifest in `meta/quick-reference.md`. Load `meta/session-checklists.md` only when you want more detail than that compact path.
                    {SESSION_START_SKILL_MCP_LINE}

                    Run at the beginning of returning sessions after the compact returning manifest in `meta/quick-reference.md` has oriented the agent.

                    - Use metadata-first maintenance checks. If `meta/review-queue.md` still contains only its placeholder, skip it. Load it only when there are real pending items or the user asks about them.
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_session_wrapup_skill_with_stale_checklist_default_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "session-wrapup.md",
                textwrap.dedent(
                    """\
                    ---
                    source: user-stated
                    origin_session: manual
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    For normal sessions, the compact checklist in `meta/session-checklists.md` is sufficient.
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("forbidden wrapup-skill pattern" in error for error in result.errors)
            )

    def test_session_wrapup_skill_with_on_demand_guidance_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "session-wrapup.md",
                textwrap.dedent(
                    f"""\
                    ---
                    source: user-stated
                    origin_session: manual
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: high
                    ---

                    Load `meta/session-checklists.md` only when you want the shorter session-end runbook there.
                    {SESSION_WRAPUP_SKILL_MCP_LINE}
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))

    def test_setup_guidance_with_bootstrap_sequence_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "setup" / "setup.sh",
                textwrap.dedent(
                    f"""\
                    #!/usr/bin/env bash
                    {PROMPT_START_LINE}
                    {PROMPT_ROUTE_LINE}
                    {LIVE_CONFIG_LINE}
                    follow the bootstrap sequence
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("forbidden setup-guidance pattern" in error for error in result.errors)
            )

    def test_onboarding_export_template_with_stale_script_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "HUMANS" / "tooling" / "onboard-export-template.md",
                "# Onboarding Export\n\nRun `bash scripts/onboard-export.sh <file>`.\n",
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("forbidden onboarding-export pattern" in error for error in result.errors)
            )

    def test_quarantine_file_with_wrong_trust_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "knowledge" / "_unverified" / "suspect.md",
                textwrap.dedent(
                    """\
                    ---
                    source: external-research
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: medium
                    ---

                    # Suspect
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("quarantine file must have trust: low" in error for error in result.errors)
            )

    def test_quarantine_file_with_last_verified_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "knowledge" / "_unverified" / "suspect.md",
                textwrap.dedent(
                    """\
                    ---
                    source: external-research
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    last_verified: 2026-03-16
                    trust: low
                    ---

                    # Suspect
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any("quarantine file must omit last_verified" in error for error in result.errors)
            )

    def test_quarantine_file_with_correct_trust_and_source_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "knowledge" / "_unverified" / "legit.md",
                textwrap.dedent(
                    """\
                    ---
                    source: external-research
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    trust: low
                    ---

                    # Legit external content
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertEqual(result.warnings, [], "\n".join(result.warnings))

    def test_quarantine_file_with_wrong_source_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "knowledge" / "_unverified" / "odd-source.md",
                textwrap.dedent(
                    """\
                    ---
                    source: agent-inferred
                    origin_session: chats/2026/03/16/chat-001
                    created: 2026-03-16
                    trust: low
                    ---

                    # Odd source in quarantine
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(
                any(
                    "quarantine file expected source: external-research" in w
                    for w in result.warnings
                )
            )

    def test_single_quoted_frontmatter_dates_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "identity" / "profile.md",
                textwrap.dedent(
                    """\
                    ---
                    source: 'user-stated'
                    origin_session: manual
                    created: '2026-03-16'
                    last_verified: '2026-03-16'
                    trust: high
                    ---

                    # Profile
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertEqual(result.warnings, [], "\n".join(result.warnings))

    def test_access_entry_with_path_traversal_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.jsonl",
                '{"file":"../identity/profile.md","date":"2026-03-16","task":"test","helpfulness":0.7,"note":"used"}',
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "file must be a repo-relative path inside the memory repo" in error
                    for error in result.errors
                )
            )

    def test_access_entry_with_missing_live_target_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.jsonl",
                '{"file":"skills/missing.md","date":"2026-03-16","task":"test","helpfulness":0.7,"note":"used"}',
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "file references missing target 'skills/missing.md'" in error
                    for error in result.errors
                )
            )

    def test_access_archive_missing_target_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "skills" / "ACCESS.archive.jsonl",
                '{"file":"skills/missing.md","date":"2026-03-16","task":"test","helpfulness":0.7,"note":"used"}',
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(
                any(
                    "file references missing target 'skills/missing.md'" in warning
                    for warning in result.warnings
                )
            )

    def test_chat_leaf_missing_reflection_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "chats" / "2026" / "03" / "16" / "chat-001" / "SUMMARY.md",
                "# Chat Summary\n\nSession notes.\n",
            )

            result = validator.validate_repo(root)
            self.assertEqual(result.errors, [], "\n".join(result.errors))
            self.assertTrue(
                any("missing session reflection note" in warning for warning in result.warnings)
            )

    def test_chat_leaf_summary_without_heading_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_minimal_repo(root)
            write(
                root / "chats" / "2026" / "03" / "16" / "chat-001" / "SUMMARY.md",
                "# Chat Log\n\nSession notes.\n",
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "chat leaf summaries must begin with '# Chat Summary'" in error
                    for error in result.errors
                )
            )

    def test_setup_copy_uses_quick_reference_routing_language(self) -> None:
        for path in (
            REPO_ROOT / "setup" / "setup.sh",
            REPO_ROOT / "setup" / "setup.html",
            REPO_ROOT / "HUMANS" / "docs" / "QUICKSTART.md",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn(PROMPT_START_LINE, text)
            self.assertIn(PROMPT_ROUTE_LINE, text)
            self.assertIn(LIVE_CONFIG_LINE, text)

        self.assertNotIn(
            "start with README.md and follow its routing rules",
            (REPO_ROOT / "setup" / "setup.sh").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "start with README.md and follow its routing rules",
            (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "follow the bootstrap sequence",
            (REPO_ROOT / "setup" / "setup.sh").read_text(encoding="utf-8"),
        )

    def test_adapter_files_point_to_quick_reference(self) -> None:
        for path in (
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "CLAUDE.md",
            REPO_ROOT / ".cursorrules",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertIn("meta/quick-reference.md", text)
            self.assertIn(ADAPTER_ROUTING_LINE, text)
            self.assertNotIn("follow the bootstrap sequence and rules in README.md", text)

    def test_root_setup_entrypoints_exist_and_target_canonical_impl(self) -> None:
        wrapper = (REPO_ROOT / "setup.sh").read_text(encoding="utf-8")
        wrapper_html = (REPO_ROOT / "setup.html").read_text(encoding="utf-8")

        self.assertIn("setup/setup.sh", wrapper)
        self.assertIn("setup/setup.html", wrapper_html)

    def test_browser_setup_copy_no_longer_claims_remote_parity(self) -> None:
        quickstart = (REPO_ROOT / "HUMANS" / "docs" / "QUICKSTART.md").read_text(encoding="utf-8")
        setup_html = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        self.assertIn("Git remote setup stays manual.", quickstart)
        self.assertIn("git remote setup stays manual", setup_html)
        self.assertNotIn("Either path walks you through three choices", quickstart)
        self.assertNotIn("follow the bootstrap sequence", quickstart)

    def test_onboarding_export_template_uses_canonical_import_command(self) -> None:
        text = (REPO_ROOT / "HUMANS" / "tooling" / "onboard-export-template.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("bash HUMANS/tooling/scripts/onboard-export.sh <file>", text)
        self.assertNotIn("bash scripts/onboard-export.sh <file>", text)

    def test_session_start_skill_defaults_to_quick_reference_and_uses_checklists_on_demand(
        self,
    ) -> None:
        text = (REPO_ROOT / "skills" / "session-start.md").read_text(encoding="utf-8")

        self.assertIn(
            "For normal returning sessions, follow the compact returning manifest in `meta/quick-reference.md`.",
            text,
        )
        self.assertIn(
            "Load `meta/session-checklists.md` only when you want more detail",
            text,
        )
        self.assertNotIn(
            "For normal returning sessions, the compact checklist in `meta/session-checklists.md` is sufficient",
            text,
        )

    def test_session_wrapup_skill_uses_on_demand_session_checklists_language(
        self,
    ) -> None:
        text = (REPO_ROOT / "skills" / "session-wrapup.md").read_text(encoding="utf-8")

        self.assertIn(
            "Load `meta/session-checklists.md` only when you want",
            text,
        )
        self.assertIn("session-end runbook", text)
        self.assertNotIn(
            "For normal sessions, the compact checklist in `meta/session-checklists.md` is sufficient",
            text,
        )

    def test_quickstart_describes_template_backed_first_run_and_conditional_import_commit(
        self,
    ) -> None:
        text = (REPO_ROOT / "HUMANS" / "docs" / "QUICKSTART.md").read_text(encoding="utf-8")

        self.assertIn(
            "rm -rf .git && git init --initial-branch=core",
            text,
        )
        self.assertIn(
            "rm -rf .git && git init && git symbolic-ref HEAD refs/heads/core",
            text,
        )
        self.assertIn(
            "fresh system (blank-slate or template-backed onboarding, with no recorded chat history yet)",
            text,
        )
        self.assertIn(
            "auto-commits the imported files when git author identity is configured",
            text,
        )
        self.assertIn(
            "stages them and prints the manual commit command",
            text,
        )

    def test_compact_manifest_excludes_readme_and_session_checklists(self) -> None:
        quick_reference = (REPO_ROOT / "meta" / "quick-reference.md").read_text(encoding="utf-8")
        compact_row = validator.extract_manifest_row(quick_reference, "Compact returning")

        assert compact_row is not None
        self.assertNotIn("README.md", compact_row)
        self.assertNotIn("session-checklists", compact_row)
        self.assertIn("identity/SUMMARY.md", compact_row)
        self.assertIn("chats/SUMMARY.md", compact_row)
        self.assertIn("plans/SUMMARY.md", compact_row)
        self.assertIn("task-relevant `knowledge/SUMMARY.md`", compact_row)

    def test_context_budget_copy_uses_canonical_ranges(self) -> None:
        required_phrases = (
            "First-run onboarding bootstrap",
            "~15,000–20,000",
            "Returning compact session",
            "~3,000–7,000",
            "Full bootstrap / periodic review",
            "~18,000–25,000",
        )
        for path in (
            REPO_ROOT / "README.md",
            REPO_ROOT / "HUMANS" / "docs" / "QUICKSTART.md",
            REPO_ROOT / "meta" / "quick-reference.md",
        ):
            text = path.read_text(encoding="utf-8")
            for phrase in required_phrases:
                self.assertIn(phrase, text)

    def test_seed_compact_context_budget_fits_published_upper_bound(self) -> None:
        compact_paths = [
            REPO_ROOT / "meta" / "quick-reference.md",
            REPO_ROOT / "identity" / "SUMMARY.md",
            REPO_ROOT / "plans" / "SUMMARY.md",
            REPO_ROOT / "scratchpad" / "USER.md",
            REPO_ROOT / "scratchpad" / "CURRENT.md",
        ]
        chats_summary = REPO_ROOT / "chats" / "SUMMARY.md"
        chats_text = chats_summary.read_text(encoding="utf-8")
        if "*No conversations yet.*" not in chats_text:
            compact_paths.append(chats_summary)

        approx_tokens = round(
            sum(len(path.read_text(encoding="utf-8")) for path in compact_paths) / 4.0
        )
        self.assertLessEqual(approx_tokens, 7000)


if __name__ == "__main__":
    unittest.main()
