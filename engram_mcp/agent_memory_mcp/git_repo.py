"""
GitRepo — thin subprocess wrapper around the git CLI.

All paths accepted as arguments should be repo-relative strings.
Absolute paths are constructed internally by joining with self.root.

Design notes:
- Uses subprocess.run (synchronous) — git operations are fast local I/O and
  this is a single-client local MCP, so blocking the event loop briefly is fine.
- Author identity: if git config is missing, we set a fallback automatically
  so Tier 1 tool commits never fail with "Author identity unknown".
- All errors are normalized to StagingError with the git stderr attached.
"""

from __future__ import annotations

import subprocess
import tempfile
from datetime import date
from pathlib import Path

from .errors import StagingError


_FALLBACK_AUTHOR_NAME = "Claude"
_FALLBACK_AUTHOR_EMAIL = "agent@agent-memory"


class GitRepo:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()
        if not (self.root / ".git").exists():
            raise ValueError(f"Not a git repository: {self.root}")

    # ------------------------------------------------------------------
    # Internal runner
    # ------------------------------------------------------------------

    def _run(
        self,
        args: list[str],
        check: bool = True,
        capture: bool = True,
    ) -> subprocess.CompletedProcess:
        result = subprocess.run(
            args,
            cwd=str(self.root),
            capture_output=capture,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        if check and result.returncode != 0:
            stderr = result.stderr.strip()
            cmd = " ".join(args[:3])
            raise StagingError(
                f"`{cmd}` failed (exit {result.returncode}): {stderr}",
                stderr=stderr,
            )
        return result

    # ------------------------------------------------------------------
    # Author identity
    # ------------------------------------------------------------------

    def ensure_author_identity(self) -> None:
        """Set git user.name / user.email locally if not already configured."""
        name_result = self._run(["git", "config", "--local", "user.name"], check=False)
        if name_result.returncode != 0 or not name_result.stdout.strip():
            self._run(["git", "config", "--local", "user.name", _FALLBACK_AUTHOR_NAME])

        email_result = self._run(["git", "config", "--local", "user.email"], check=False)
        if email_result.returncode != 0 or not email_result.stdout.strip():
            self._run(["git", "config", "--local", "user.email", _FALLBACK_AUTHOR_EMAIL])

    # ------------------------------------------------------------------
    # Object hashing (version tokens)
    # ------------------------------------------------------------------

    def hash_object(self, rel_path: str) -> str:
        """Return the git object hash (SHA-1) of the file on disk.

        This is the version token: if it changes, the file was modified.
        """
        abs_path = str(self.root / rel_path)
        result = self._run(["git", "hash-object", abs_path])
        return result.stdout.strip()

    def check_version_token(self, rel_path: str, token: str | None) -> None:
        """Raise ConflictError if token is provided and does not match current hash."""
        if token is None:
            return
        # Import here to avoid circular
        from .errors import ConflictError

        current = self.hash_object(rel_path)
        if current != token:
            raise ConflictError(
                f"Version conflict on {rel_path}: file was modified since last read. "
                f"Re-read the file to get the current version_token and retry.",
                current_token=current,
            )

    # ------------------------------------------------------------------
    # Staging
    # ------------------------------------------------------------------

    def add(self, *rel_paths: str) -> None:
        """Stage one or more files."""
        if not rel_paths:
            return
        self._run(["git", "add", "--"] + list(rel_paths))

    def add_all(self) -> None:
        """Stage all changes (git add -A)."""
        self._run(["git", "add", "-A"])

    def rm(self, rel_path: str) -> None:
        """Remove file from working tree and stage the deletion."""
        self._run(["git", "rm", "--", rel_path])

    def mv(self, rel_src: str, rel_dst: str) -> None:
        """Rename/move a file and stage the change (preserves history)."""
        # Ensure destination directory exists
        dst_abs = self.root / rel_dst
        dst_abs.parent.mkdir(parents=True, exist_ok=True)
        self._run(["git", "mv", "--", rel_src, rel_dst])

    # ------------------------------------------------------------------
    # Committing
    # ------------------------------------------------------------------

    def nothing_staged(self) -> bool:
        """True if the staging area is empty (nothing to commit)."""
        result = self._run(["git", "diff", "--cached", "--quiet"], check=False)
        return result.returncode == 0

    def has_staged_changes(self, *rel_paths: str) -> bool:
        """True if the staging area contains changes for the given paths."""
        if not rel_paths:
            return not self.nothing_staged()
        result = self._run(["git", "diff", "--cached", "--quiet", "--", *rel_paths], check=False)
        return result.returncode == 1

    def commit(
        self,
        message: str,
        *,
        paths: list[str] | None = None,
        allow_empty: bool = False,
    ) -> str:
        """Commit staged changes. Returns the new commit SHA."""
        self.ensure_author_identity()
        cmd = ["git", "commit", "-m", message]
        if allow_empty:
            cmd.append("--allow-empty")
        if paths:
            deduped_paths = list(dict.fromkeys(paths))
            cmd += ["--only", "--", *deduped_paths]
        self._run(cmd)
        sha_result = self._run(["git", "rev-parse", "HEAD"])
        return sha_result.stdout.strip()

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------

    def log(self, n: int = 10) -> list[dict]:
        """Return the last n commits as structured dicts."""
        # Use a record separator to handle multi-line messages
        sep = "|||COMMIT|||"
        result = self._run(
            [
                "git",
                "log",
                f"-{n}",
                f"--pretty=format:{sep}%H%n%s%n%ai%n",
                "--name-only",
            ]
        )

        commits = []
        raw = result.stdout.strip()
        for block in raw.split(sep):
            block = block.strip()
            if not block:
                continue
            lines = block.splitlines()
            if len(lines) < 3:
                continue
            sha = lines[0].strip()
            message = lines[1].strip()
            date = lines[2].strip()
            files = [line.strip() for line in lines[3:] if line.strip()]
            commits.append(
                {
                    "sha": sha,
                    "message": message,
                    "date": date,
                    "files_changed": files,
                }
            )
        return commits

    def current_head(self) -> str:
        """Return the current HEAD commit SHA."""
        result = self._run(["git", "rev-parse", "HEAD"])
        return result.stdout.strip()

    def inspect_commit(self, sha: str) -> dict[str, object]:
        """Return structured metadata for a commit."""
        resolved = self._run(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"])
        full_sha = resolved.stdout.strip()

        show_result = self._run(["git", "show", "--quiet", "--format=%H%n%s%n%P", full_sha])
        lines = show_result.stdout.splitlines()
        if len(lines) < 3:
            raise StagingError(f"Could not inspect commit metadata for {sha}")

        files_result = self._run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "--root", "-r", full_sha]
        )
        parents = [parent for parent in lines[2].split() if parent]
        files_changed = [line.strip() for line in files_result.stdout.splitlines() if line.strip()]
        return {
            "sha": lines[0].strip(),
            "message": lines[1].strip(),
            "parents": parents,
            "files_changed": files_changed,
        }

    def revert_preview_status(self, sha: str) -> dict[str, object]:
        """Return whether reverting *sha* at HEAD would apply cleanly."""
        with tempfile.TemporaryDirectory(prefix="agent-memory-revert-preview-") as tmpdir:
            worktree_path = Path(tmpdir) / "worktree"

            add_result = subprocess.run(
                ["git", "worktree", "add", "--detach", str(worktree_path), "HEAD"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
            )
            if add_result.returncode != 0:
                stderr = add_result.stderr.strip()
                raise StagingError(
                    f"`git worktree add` failed (exit {add_result.returncode}): {stderr}",
                    stderr=stderr,
                )

            try:
                revert_result = subprocess.run(
                    ["git", "revert", "--no-commit", "--no-edit", sha],
                    cwd=str(worktree_path),
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL,
                )
                combined = "\n".join(
                    part.strip()
                    for part in (revert_result.stdout, revert_result.stderr)
                    if part and part.strip()
                ).strip()
                return {
                    "applies_cleanly": revert_result.returncode == 0,
                    "details": combined,
                }
            finally:
                remove_result = subprocess.run(
                    ["git", "worktree", "remove", "--force", str(worktree_path)],
                    cwd=str(self.root),
                    capture_output=True,
                    text=True,
                    stdin=subprocess.DEVNULL,
                )
                if remove_result.returncode != 0:
                    stderr = remove_result.stderr.strip()
                    raise StagingError(
                        f"`git worktree remove` failed (exit {remove_result.returncode}): {stderr}",
                        stderr=stderr,
                    )

    def revert(self, sha: str) -> str:
        """Create a revert commit for *sha*. Returns the new HEAD commit SHA."""
        self.ensure_author_identity()
        self._run(["git", "revert", "--no-edit", sha])
        result = self._run(["git", "rev-parse", "HEAD"])
        return result.stdout.strip()

    def grep(
        self,
        pattern: str,
        *,
        glob: str = "*.md",
        case_sensitive: bool = False,
        max_count: int | None = None,
    ) -> list[tuple[str, int, str]]:
        """Run git grep and return (rel_path, line_no, line_text) triples.

        Raises StagingError only on genuine failures. Returns [] when there
        are no matches (git grep exits 1 for "no matches" — that is not an error).

        Args:
            pattern:        POSIX extended regex to match.
            glob:           Path glob passed to git grep via '--' (e.g. '*.md').
            case_sensitive: If False, passes -i to git grep.
            max_count:      If set, pass --max-count to limit matches per file.
        """
        cmd = ["git", "grep", "-n", "-E"]
        if not case_sensitive:
            cmd.append("-i")
        if max_count is not None:
            cmd += [f"--max-count={max_count}"]
        cmd += [pattern, "--", glob]

        result = self._run(cmd, check=False)

        if result.returncode == 0:
            pass  # matches found
        elif result.returncode == 1:
            return []  # no matches — not an error
        else:
            # Real failure (e.g. bad regex, git not available)
            raise StagingError(
                f"git grep failed (exit {result.returncode}): {result.stderr.strip()}",
                stderr=result.stderr.strip(),
            )

        matches: list[tuple[str, int, str]] = []
        for line in result.stdout.splitlines():
            # Format: <path>:<line_no>:<content>
            try:
                path_part, rest = line.split(":", 1)
                line_no_str, text = rest.split(":", 1)
                matches.append((path_part, int(line_no_str), text))
            except ValueError:
                continue
        return matches

    def diff_status(self) -> dict[str, list[str]]:
        """Return working tree status: staged, unstaged, untracked file lists."""
        staged_result = self._run(["git", "diff", "--name-only", "--cached"], check=False)
        unstaged_result = self._run(["git", "diff", "--name-only"], check=False)
        untracked_result = self._run(
            ["git", "ls-files", "--others", "--exclude-standard"], check=False
        )

        def _lines(result: subprocess.CompletedProcess) -> list[str]:
            return [line for line in result.stdout.strip().splitlines() if line.strip()]

        return {
            "staged": _lines(staged_result),
            "unstaged": _lines(unstaged_result),
            "untracked": _lines(untracked_result),
        }

    def first_tracked_author_date(self, rel_path: str) -> date | None:
        """Return the first git author date for a tracked path, if available."""
        result = self._run(
            [
                "git",
                "log",
                "--diff-filter=A",
                "--follow",
                "--format=%aI",
                "--reverse",
                "--",
                rel_path,
            ],
            check=False,
        )
        if result.returncode not in (0, 1):
            raise StagingError(
                f"git log failed (exit {result.returncode}): {result.stderr.strip()}",
                stderr=result.stderr.strip(),
            )

        first_line = next(
            (line.strip() for line in result.stdout.splitlines() if line.strip()),
            "",
        )
        if not first_line:
            return None

        return date.fromisoformat(first_line[:10])

    # ------------------------------------------------------------------
    # Path utilities
    # ------------------------------------------------------------------

    def abs_path(self, rel_path: str) -> Path:
        p = (self.root / rel_path).resolve()
        # Ensure it's within the repo root (prevent path traversal)
        try:
            p.relative_to(self.root)
        except ValueError:
            from .errors import MemoryPermissionError

            raise MemoryPermissionError(f"Path escapes repository root: {rel_path}", path=rel_path)
        return p

    def rel_path(self, abs_path: Path) -> str:
        return str(abs_path.relative_to(self.root))
