from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RESOLVER_PATH = (
    REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "resolve_bootstrap_manifest.py"
)
SPEC = importlib.util.spec_from_file_location("resolve_bootstrap_manifest", RESOLVER_PATH)
assert SPEC is not None
resolver = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = resolver
SPEC.loader.exec_module(resolver)

BOOTSTRAP_MANIFEST = (REPO_ROOT / "agent-bootstrap.toml").read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_repo(
    root: Path,
    *,
    first_run: bool = False,
    active_plans: bool = True,
    placeholder_scratchpad: bool = True,
) -> None:
    write(root / "agent-bootstrap.toml", BOOTSTRAP_MANIFEST)

    for path in (
        "meta/quick-reference.md",
        "README.md",
        "meta/first-run.md",
        "CHANGELOG.md",
        "meta/curation-policy.md",
        "meta/update-guidelines.md",
        "meta/system-maturity.md",
        "meta/belief-diff-log.md",
        "meta/review-queue.md",
        "meta/integrity-checklist.md",
        "identity/SUMMARY.md",
        "chats/SUMMARY.md",
        "plans/SUMMARY.md",
    ):
        write(root / path, f"# {Path(path).stem}\n")

    profile_source = "template" if first_run else "user-stated"
    write(
        root / "identity" / "profile.md",
        textwrap.dedent(
            f"""\
            ---
            source: {profile_source}
            origin_session: manual
            created: 2026-03-18
            trust: high
            ---

            # Profile
            """
        ),
    )

    if not first_run:
        write(root / "chats" / "2026" / "03" / "18" / "chat-001" / "SUMMARY.md", "# Chat\n")

    plans_summary = (
        "### `example.md` · status: active · trust: medium\n"
        if active_plans
        else "# Plans\n\n_No active plans._\n"
    )
    write(root / "plans" / "SUMMARY.md", plans_summary)

    if placeholder_scratchpad:
        write(
            root / "scratchpad" / "USER.md",
            "# User notes\n\n_Nothing here yet. Add any context you'd like the agent to pick up at session start._\n",
        )
        write(
            root / "scratchpad" / "CURRENT.md",
            "# Agent working notes\n\n_No current notes._\n",
        )
    else:
        write(root / "scratchpad" / "USER.md", "# User notes\n\nImportant note.\n")
        write(root / "scratchpad" / "CURRENT.md", "# Agent working notes\n\nWorking note.\n")


class BootstrapResolverTests(unittest.TestCase):
    def test_automation_mode_beats_other_detection_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, first_run=True)

            manifest = resolver.read_manifest(root)
            mode, source = resolver.detect_mode(
                root,
                manifest,
                automation=True,
                periodic_review=True,
                fresh_instantiation=True,
                full_bootstrap=True,
            )

            self.assertEqual(mode, "automation")
            self.assertEqual(source, "automation_flag")

    def test_first_run_detection_uses_template_identity_and_no_chat_history(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, first_run=True)

            manifest = resolver.read_manifest(root)
            mode, source = resolver.detect_mode(root, manifest)

            self.assertEqual(mode, "first_run")
            self.assertEqual(source, "first_run_heuristic")

    def test_returning_trace_skips_placeholders_and_no_active_plans(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, active_plans=False, placeholder_scratchpad=True)

            resolution = resolver.resolve_startup(root, requested_mode="returning")
            trace_by_path = {step.path: step for step in resolution.trace}

            self.assertEqual(trace_by_path["meta/quick-reference.md"].status, "loaded")
            self.assertEqual(trace_by_path["plans/SUMMARY.md"].status, "skipped")
            self.assertEqual(trace_by_path["plans/SUMMARY.md"].reason, "no_active_plans")
            self.assertEqual(trace_by_path["scratchpad/USER.md"].status, "skipped")
            self.assertEqual(
                trace_by_path["scratchpad/USER.md"].reason, "placeholder_or_empty"
            )
            self.assertEqual(trace_by_path["scratchpad/CURRENT.md"].status, "skipped")
            self.assertEqual(
                trace_by_path["scratchpad/CURRENT.md"].reason, "placeholder_or_empty"
            )

    def test_duplicate_paths_are_deduplicated_after_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, placeholder_scratchpad=False)
            write(
                root / "agent-bootstrap.toml",
                BOOTSTRAP_MANIFEST.replace(
                    '[[modes.returning.steps]]\npath = "identity/SUMMARY.md"',
                    '[[modes.returning.steps]]\npath = "./identity/SUMMARY.md"\nrole = "identity-summary-alias"\nrequired = false\ncost = "light"\n\n[[modes.returning.steps]]\npath = "identity/SUMMARY.md"',
                    1,
                ),
            )

            resolution = resolver.resolve_startup(root, requested_mode="returning")
            identity_steps = [step for step in resolution.trace if step.path == "identity/SUMMARY.md"]

            self.assertEqual(len(identity_steps), 2)
            self.assertEqual(identity_steps[0].status, "loaded")
            self.assertEqual(identity_steps[1].status, "skipped")
            self.assertEqual(identity_steps[1].reason, "duplicate_path")

    def test_warning_generation_respects_git_state(self) -> None:
        warnings = resolver.resolve_warnings(
            resolver.GitState(
                current_branch="feature/runtime",
                detached_head=True,
                worktree_branch_drift=True,
                branch_checked_out_elsewhere=True,
            ),
            {
                "warn_on_detached_head": True,
                "warn_on_worktree_branch_drift": True,
                "warn_on_branch_checked_out_elsewhere": True,
            },
            expected_branch="main",
        )

        self.assertEqual(
            [warning.code for warning in warnings],
            [
                "detached_head",
                "worktree_branch_drift",
                "branch_checked_out_elsewhere",
            ],
        )

    def test_budget_pressure_skips_optional_step_and_updates_budget_state(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, placeholder_scratchpad=False)
            write(
                root / "agent-bootstrap.toml",
                BOOTSTRAP_MANIFEST.replace(
                    '[modes.returning]\ntoken_budget = 7000',
                    '[modes.returning]\ntoken_budget = 1500',
                    1,
                ).replace(
                    '[[modes.returning.steps]]\npath = "chats/SUMMARY.md"\nrole = "chat-summary"\nrequired = false\nskip_if = "placeholder_or_empty"\ncost = "light"',
                    '[[modes.returning.steps]]\npath = "docs/heavy-context.md"\nrole = "heavy-context"\nrequired = false\ncost = "medium"\n\n[[modes.returning.steps]]\npath = "chats/SUMMARY.md"\nrole = "chat-summary"\nrequired = false\nskip_if = "placeholder_or_empty"\ncost = "light"',
                    1,
                ),
            )
            write(root / "docs" / "heavy-context.md", "# Heavy context\n")

            resolution = resolver.resolve_startup(root, requested_mode="returning")
            trace_by_role = {step.role: step for step in resolution.trace}

            self.assertEqual(trace_by_role["heavy-context"].status, "skipped")
            self.assertEqual(trace_by_role["heavy-context"].reason, "budget_pressure")
            self.assertEqual(trace_by_role["heavy-context"].budget_after, 500)
            self.assertTrue(resolution.budget.pressure)
            self.assertEqual(resolution.budget.limit, 1500)
            self.assertEqual(resolution.budget.reserve, 500)
            self.assertEqual(resolution.budget.estimated_used, 1000)
            self.assertEqual(resolution.budget.estimated_remaining, 500)
            self.assertIn("budget_pressure", [warning.code for warning in resolution.warnings])

    def test_prefer_summaries_skips_transcript_under_budget_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_repo(root, placeholder_scratchpad=True)
            write(root / "docs" / "topic" / "transcript.md", "# Transcript\n")
            write(root / "docs" / "topic" / "SUMMARY.md", "# Summary\n")
            write(
                root / "agent-bootstrap.toml",
                BOOTSTRAP_MANIFEST.replace(
                    '[modes.returning]\ntoken_budget = 7000',
                    '[modes.returning]\ntoken_budget = 2500',
                    1,
                ).replace(
                    '[[modes.returning.steps]]\npath = "plans/SUMMARY.md"\nrole = "plan-summary"\nrequired = false\nskip_if = "no_active_plans"\ncost = "light"',
                    '[[modes.returning.steps]]\npath = "docs/topic/transcript.md"\nrole = "topic-transcript"\nrequired = false\ncost = "light"\n\n[[modes.returning.steps]]\npath = "docs/topic/SUMMARY.md"\nrole = "topic-summary"\nrequired = false\ncost = "light"\n\n[[modes.returning.steps]]\npath = "plans/SUMMARY.md"\nrole = "plan-summary"\nrequired = false\nskip_if = "no_active_plans"\ncost = "light"',
                    1,
                ),
            )

            resolution = resolver.resolve_startup(root, requested_mode="returning")
            trace_by_role = {step.role: step for step in resolution.trace}

            self.assertEqual(trace_by_role["topic-transcript"].status, "skipped")
            self.assertEqual(trace_by_role["topic-transcript"].reason, "budget_pressure")
            self.assertEqual(trace_by_role["topic-transcript"].estimated_tokens, 7000)
            self.assertEqual(trace_by_role["topic-summary"].status, "loaded")
            self.assertEqual(trace_by_role["topic-summary"].estimated_tokens, 500)
            self.assertEqual(resolution.preload_access_mode, "startup_trace_only")


if __name__ == "__main__":
    unittest.main()
