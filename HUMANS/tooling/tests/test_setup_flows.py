from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def find_bash() -> str | None:
    candidates = [
        Path(r"C:\Program Files\Git\bin\bash.exe"),
        Path(r"C:\Program Files\Git\usr\bin\bash.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    bash = shutil.which("bash")
    if bash and "system32\\bash.exe" not in bash.lower():
        return bash
    return None


def isolated_env(temp_home: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = str(temp_home)
    env["USERPROFILE"] = str(temp_home)
    env["XDG_CONFIG_HOME"] = str(temp_home)
    return env


def build_setup_repo(root: Path) -> None:
    for filename in (
        "README.md",
        "CHANGELOG.md",
        "setup.sh",
        "setup.html",
        "AGENTS.md",
        "CLAUDE.md",
        ".cursorrules",
        ".gitignore",
    ):
        shutil.copy2(REPO_ROOT / filename, root / filename)

    for dirname in (
        ".github",
        "HUMANS",
        "setup",
        "meta",
        "identity",
        "chats",
        "knowledge",
        "skills",
        "scratchpad",
    ):
        shutil.copytree(
            REPO_ROOT / dirname,
            root / dirname,
            ignore=shutil.ignore_patterns("__pycache__"),
        )


def read_initial_commit_manifest(root: Path) -> list[str]:
    manifest = root / "setup" / "initial-commit-paths.txt"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    return [line for line in lines if line and not line.startswith("#")]


class SetupFlowTests(unittest.TestCase):
    def run_setup(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        bash = find_bash()
        if bash is None:
            self.skipTest("bash is not available in this environment")

        env = isolated_env(root / ".home")
        return subprocess.run(
            [bash, str(root / "setup.sh"), *args],
            cwd=root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_setup_sh_personalization_flags_write_browser_parity_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_setup_repo(root)

            self.run_setup(
                root,
                "--non-interactive",
                "--profile",
                "software-developer",
                "--platform",
                "generic",
                "--user-name",
                "Alex",
                "--user-context",
                "Writing code and debugging",
            )

            summary = (root / "identity" / "SUMMARY.md").read_text(encoding="utf-8")
            profile = (root / "identity" / "profile.md").read_text(encoding="utf-8")

            self.assertIn("**User:** Alex", summary)
            self.assertIn("**Uses AI for:** Writing code and debugging", summary)
            self.assertIn("Template-based profile — pending onboarding confirmation.", summary)
            self.assertNotIn("last_verified:", profile)
            self.assertIn("created:", profile)

    def test_shell_and_browser_setup_sources_keep_profile_summary_copy_aligned(self) -> None:
        shell_text = (REPO_ROOT / "setup" / "setup.sh").read_text(encoding="utf-8")
        browser_text = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        required_phrases = (
            "Template-based profile",
            "pending onboarding confirmation.",
            "A starter profile has been installed from a template. During the first",
            "session, the onboarding skill will walk through the template traits and",
            "confirm, adjust, or remove them.",
            "See [profile.md](profile.md) for the current profile.",
            "**User:**",
            "**Uses AI for:**",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, shell_text)
            self.assertIn(phrase, browser_text)

    def test_browser_setup_uses_local_date_components_for_created_frontmatter(self) -> None:
        browser_text = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        self.assertNotIn("toISOString().slice(0, 10)", browser_text)
        self.assertIn("getFullYear()", browser_text)
        self.assertIn("getMonth() + 1", browser_text)
        self.assertIn("getDate()", browser_text)

    def test_initial_commit_manifest_matches_tracked_repo_paths(self) -> None:
        manifest_paths = set(read_initial_commit_manifest(REPO_ROOT))
        tracked_paths = set(
            subprocess.run(
                ["git", "ls-files"],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.splitlines()
        )

        expected_seed_paths = tracked_paths | {"setup/initial-commit-paths.txt"}

        self.assertTrue(
            expected_seed_paths.issubset(manifest_paths),
            "initial commit manifest is missing tracked seed paths",
        )

        for relative_path in manifest_paths:
            self.assertTrue(
                (REPO_ROOT / relative_path).exists(),
                f"manifest path does not exist: {relative_path}",
            )

    def test_setup_initial_commit_excludes_unrelated_local_files_and_generated_prompts(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_setup_repo(root)
            bash = find_bash()
            if bash is None:
                self.skipTest("bash is not available in this environment")

            env = isolated_env(root / ".home")
            subprocess.run(
                ["git", "init"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            (root / "notes.txt").write_text("leave me out\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "notes.txt"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    bash,
                    str(root / "setup.sh"),
                    "--non-interactive",
                    "--profile",
                    "software-developer",
                    "--platform",
                    "generic",
                ],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            head_files = set(
                subprocess.run(
                    ["git", "show", "--name-only", "--pretty=", "HEAD"],
                    cwd=root,
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.splitlines()
            )

            self.assertIn("setup/initial-commit-paths.txt", head_files)
            self.assertIn("README.md", head_files)
            self.assertNotIn("notes.txt", head_files)
            self.assertNotIn("system-prompt.txt", head_files)

    def test_setup_missing_git_identity_stages_only_allowlisted_paths_and_prints_safe_command(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_setup_repo(root)
            bash = find_bash()
            if bash is None:
                self.skipTest("bash is not available in this environment")

            env = isolated_env(root / ".home")
            subprocess.run(
                ["git", "init"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            (root / "notes.txt").write_text("leave me untracked\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "notes.txt"],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [
                    bash,
                    str(root / "setup.sh"),
                    "--non-interactive",
                    "--profile",
                    "software-developer",
                    "--platform",
                    "generic",
                ],
                cwd=root,
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn(
                "git add -- ",
                result.stdout,
            )
            self.assertIn(
                "git commit -m '[system] Initialize agent memory system' -m 'Created from agent-memory-seed template on",
                result.stdout,
            )
            self.assertNotIn("git add -A", result.stdout)

            staged_files = set(
                subprocess.run(
                    ["git", "diff", "--cached", "--name-only"],
                    cwd=root,
                    env=env,
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.splitlines()
            )

            self.assertIn("README.md", staged_files)
            self.assertIn("setup/initial-commit-paths.txt", staged_files)
            self.assertNotIn("notes.txt", staged_files)
            self.assertNotIn("system-prompt.txt", staged_files)


if __name__ == "__main__":
    unittest.main()
