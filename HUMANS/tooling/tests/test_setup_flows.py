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
    ):
        shutil.copy2(REPO_ROOT / filename, root / filename)

    for dirname in ("setup", "meta", "identity", "chats", "knowledge", "skills", "scratchpad"):
        shutil.copytree(
            REPO_ROOT / dirname,
            root / dirname,
            ignore=shutil.ignore_patterns("__pycache__"),
        )


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


if __name__ == "__main__":
    unittest.main()
