from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate_memory_repo.py"
ROUTED_PROMPT_LINE = (
    "start with README.md and follow its routing rules"
)
ROUTED_SESSION_LINE = (
    "Use meta/first-run.md for blank-slate onboarding, meta/session-checklists.md for returning sessions, and the full bootstrap only when README.md routes you there."
)
LIVE_CONFIG_LINE = (
    "meta/quick-reference.md is the live runtime config; do not use hardcoded thresholds."
)

SPEC = importlib.util.spec_from_file_location("validate_memory_repo", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


VALID_QUICK_REFERENCE = textwrap.dedent(
    """\
    # Quick Reference

    This is the single authoritative source for active operational parameters.

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
    """
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_minimal_repo(root: Path) -> None:
    write(
        root / "README.md",
        "# README\nRead `meta/quick-reference.md` for active thresholds.\n",
    )
    write(
        root / "QUICKSTART.md",
        "# Quickstart\nOptional check: `python scripts/validate_memory_repo.py`\n",
    )
    write(root / "meta" / "quick-reference.md", VALID_QUICK_REFERENCE)
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
        "# Session checklists\nBootstrap uses `meta/quick-reference.md`.\n",
    )

    for dirname in ("identity", "knowledge", "skills", "chats"):
        write(root / dirname / "SUMMARY.md", f"# {dirname} summary\n")
        write(root / dirname / "ACCESS.jsonl", "")


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
                    last_verified: 2026-03-16
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
        # source: template is set by setup.sh when installing starter profiles;
        # the validator must accept it so fresh template-installed repos pass CI.
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
                    trust: high
                    ---

                    # Example
                    """
                ),
            )

            result = validator.validate_repo(root)
            self.assertTrue(
                any(
                    "missing required frontmatter keys" in error
                    for error in result.errors
                )
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
            self.assertTrue(
                any("legacy origin_session" in warning for warning in result.warnings)
            )

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
            self.assertTrue(
                any("origin_session must be" in error for error in result.errors)
            )

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
                any(
                    "forbidden runtime guidance pattern" in error
                    for error in result.errors
                )
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
                any(
                    "quarantine file must have trust: low" in error
                    for error in result.errors
                )
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
                    last_verified: 2026-03-16
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
                    last_verified: 2026-03-16
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

    def test_setup_copy_uses_readme_routing_language(self) -> None:
        for path in (REPO_ROOT / "setup.sh", REPO_ROOT / "setup.html", REPO_ROOT / "QUICKSTART.md"):
            text = path.read_text(encoding="utf-8")
            self.assertIn(ROUTED_PROMPT_LINE, text)
            self.assertIn(ROUTED_SESSION_LINE, text)
            self.assertIn(LIVE_CONFIG_LINE, text)

        self.assertNotIn(
            "At the start of this session:",
            (REPO_ROOT / "setup.sh").read_text(encoding="utf-8"),
        )
        self.assertNotIn(
            "At the start of this session:",
            (REPO_ROOT / "setup.html").read_text(encoding="utf-8"),
        )

    def test_browser_setup_copy_no_longer_claims_remote_parity(self) -> None:
        quickstart = (REPO_ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
        setup_html = (REPO_ROOT / "setup.html").read_text(encoding="utf-8")

        self.assertIn("Git remote setup stays manual.", quickstart)
        self.assertIn("git remote setup stays manual", setup_html)
        self.assertNotIn("Either path walks you through three choices", quickstart)

    def test_context_budget_copy_uses_canonical_ranges(self) -> None:
        required_phrases = (
            "First-run onboarding bootstrap",
            "~15,000–20,000",
            "Returning compact session",
            "~2,000–5,000",
            "Full bootstrap / periodic review",
            "~18,000–25,000",
        )
        for path in (
            REPO_ROOT / "README.md",
            REPO_ROOT / "QUICKSTART.md",
            REPO_ROOT / "meta" / "quick-reference.md",
        ):
            text = path.read_text(encoding="utf-8")
            for phrase in required_phrases:
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
