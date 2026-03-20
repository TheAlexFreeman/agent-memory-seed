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
        "agent-bootstrap.toml",
        "setup.sh",
        "setup.html",
        "AGENTS.md",
        "CLAUDE.md",
        ".cursorrules",
        ".gitattributes",
        ".gitignore",
    ):
        shutil.copy2(REPO_ROOT / filename, root / filename)

    for dirname in (
        ".codex",
        ".github",
        ".vscode",
        "HUMANS",
        "setup",
        "meta",
        "identity",
        "chats",
        "knowledge",
        "plans",
        "skills",
        "scratchpad",
        "tools",
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

    def test_setup_initializes_new_repo_on_core_branch(self) -> None:
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
            )

            head_result = subprocess.run(
                ["git", "symbolic-ref", "--short", "HEAD"],
                cwd=root,
                check=True,
                capture_output=True,
                text=True,
            )
            head_branch = head_result.stdout.strip()

            self.assertEqual("core", head_branch)

    def test_setup_rewrites_codex_config_for_current_clone(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            build_setup_repo(root)

            self.run_setup(
                root,
                "--non-interactive",
                "--profile",
                "software-developer",
                "--platform",
                "codex",
            )

            config_text = (root / ".codex" / "config.toml").read_text(encoding="utf-8")
            escaped_root = str(root).replace("\\", "\\\\")
            self.assertIn(escaped_root, config_text)
            self.assertIn(
                str(root / "engram_mcp" / "memory_mcp.py").replace("\\", "\\\\"),
                config_text,
            )
            self.assertNotIn(str(REPO_ROOT).replace("\\", "\\\\"), config_text)

    def test_shell_and_browser_setup_sources_keep_profile_summary_copy_aligned(
        self,
    ) -> None:
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

    def test_browser_setup_uses_local_date_components_for_created_frontmatter(
        self,
    ) -> None:
        browser_text = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        self.assertNotIn("toISOString().slice(0, 10)", browser_text)
        self.assertIn("getFullYear()", browser_text)
        self.assertIn("getMonth() + 1", browser_text)
        self.assertIn("getDate()", browser_text)

    def test_browser_setup_collects_codex_paths_and_generates_config(self) -> None:
        browser_text = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        self.assertIn('id="codex-repo-path"', browser_text)
        self.assertIn('id="codex-python-path"', browser_text)
        self.assertIn('id="codex-path-error"', browser_text)
        self.assertIn("function makeCodexConfig", browser_text)
        self.assertIn("function isAbsolutePath", browser_text)
        self.assertIn("function setCodexPathError", browser_text)
        self.assertIn("'.codex/config.toml'", browser_text)
        self.assertNotIn("C:\\\\path\\\\to\\\\your\\\\repo", browser_text)
        self.assertNotIn("C:\\\\path\\\\to\\\\python.exe", browser_text)

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

    def test_setup_initial_commit_excludes_unrelated_local_files_and_generated_prompts(
        self,
    ) -> None:
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
            self.assertIn("plans/SUMMARY.md", head_files)
            self.assertNotIn("notes.txt", head_files)
            self.assertNotIn("system-prompt.txt", head_files)

    def test_setup_missing_git_identity_stages_only_allowlisted_paths_and_prints_safe_command(
        self,
    ) -> None:
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
            self.assertIn("git status --short", result.stdout)
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
            self.assertIn("plans/SUMMARY.md", staged_files)
            self.assertNotIn("notes.txt", staged_files)
            self.assertNotIn("system-prompt.txt", staged_files)

    def test_generated_prompt_copy_mentions_semantic_default_and_deferred_file_blind_writes(
        self,
    ) -> None:
        shell_text = (REPO_ROOT / "setup" / "setup.sh").read_text(encoding="utf-8")
        browser_text = (REPO_ROOT / "setup" / "setup.html").read_text(encoding="utf-8")

        required_phrases = (
            "default repo-local runtime is semantic/governed MCP",
            "raw fallback is opt-in via `MEMORY_ENABLE_RAW_WRITE_TOOLS=1`",
            "do not claim that ACCESS logging or governed writes happened; defer them",
            "Identity changes are proposed changes",
            "Plans may guide only their own scoped work",
            "Append-only `CHANGELOG.md` updates are allowed without protected-file approval",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, shell_text)
            self.assertIn(phrase, browser_text)


if __name__ == "__main__":
    unittest.main()
