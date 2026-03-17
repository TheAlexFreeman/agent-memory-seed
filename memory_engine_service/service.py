from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, cast

import memory_engine_core.engine as memory_engine

READABLE_TEXT_EXTENSIONS = {
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".html",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
RETRIEVAL_ROOTS = {"identity", "knowledge", "skills", "chats"}
LOW_CONFIDENCE_SOURCES = {"agent-inferred", "external-research", "skill-discovery"}


class FileLock:
    def __init__(self, lock_path: Path, timeout_seconds: float = 5.0) -> None:
        self.lock_path = lock_path
        self.timeout_seconds = timeout_seconds
        self._fd: int | None = None

    def __enter__(self) -> FileLock:
        deadline = time.monotonic() + self.timeout_seconds
        while True:
            try:
                self._fd = os.open(
                    str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out acquiring lock for {self.lock_path}")
                time.sleep(0.05)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.lock_path.unlink()
        except FileNotFoundError:
            pass


class MemoryEngineService:
    def __init__(self, repo_root: Path, db_path: Path | None = None) -> None:
        self.engine = memory_engine
        self.repo_root = cast(Path, self.engine.detect_repo_root(repo_root))
        self.db_path = cast(Path, self.engine.resolve_db_path(self.repo_root, db_path))

    def load_inventory(self) -> Any:
        return self.engine.load_inventory(self.repo_root)

    def load_quick_reference(self) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.engine.parse_quick_reference(
                self.repo_root / "meta" / "quick-reference.md"
            ),
        )

    def status(self) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.engine.format_status(
                self.repo_root,
                self.db_path,
                self.load_inventory(),
                self.load_quick_reference(),
            ),
        )

    def query(
        self,
        query: str,
        task_group: str | None = None,
        limit: int = 10,
        group_limit: int = 5,
    ) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.engine.format_query_report(
                self.repo_root,
                self.load_inventory(),
                query,
                task_group,
                limit,
                group_limit,
            ),
        )

    def _resolve_repo_file(self, relative_path: str) -> Path:
        candidate = (self.repo_root / relative_path).resolve()
        try:
            candidate.relative_to(self.repo_root)
        except ValueError as exc:
            raise ValueError(f"Path escapes repo root: {relative_path}") from exc
        if not candidate.exists() or not candidate.is_file():
            raise FileNotFoundError(relative_path)
        if candidate.suffix.lower() not in READABLE_TEXT_EXTENSIONS:
            raise ValueError(f"Unsupported file type for MCP read: {relative_path}")
        return candidate

    def _build_read_metadata(self, file_path: Path) -> dict[str, object]:
        relative_path = file_path.relative_to(self.repo_root).as_posix()
        top_level = relative_path.split("/", 1)[0]
        file_type = (
            cast(str, self.engine.determine_file_type(file_path))
            if file_path.suffix.lower() == ".md"
            else "text"
        )
        frontmatter = (
            cast(dict[str, str], self.engine.parse_frontmatter(file_path))
            if file_path.suffix.lower() == ".md"
            else {}
        )
        is_quarantined = relative_path.startswith("knowledge/_unverified/")
        requires_access_log = (
            top_level in RETRIEVAL_ROOTS
            and file_type == "content"
            and top_level != "meta"
            and file_path.name != "SUMMARY.md"
        )
        trust = frontmatter.get("trust")
        source = frontmatter.get("source")
        provenance_pause_required = bool(
            is_quarantined
            or trust in {"low", "medium"}
            or source in LOW_CONFIDENCE_SOURCES
        )
        return {
            "path": relative_path,
            "folder": top_level,
            "file_type": file_type,
            "frontmatter": frontmatter,
            "is_quarantined": is_quarantined,
            "requires_access_log": requires_access_log,
            "provenance_pause_required": provenance_pause_required,
        }

    def read_memory(self, relative_path: str) -> dict[str, object]:
        file_path = self._resolve_repo_file(relative_path)
        metadata = self._build_read_metadata(file_path)
        return {
            **metadata,
            "content": file_path.read_text(encoding="utf-8"),
            "size_bytes": file_path.stat().st_size,
        }

    def get_context(
        self,
        topic: str,
        limit: int = 3,
        group_limit: int = 3,
        excerpt_chars: int = 1200,
    ) -> dict[str, object]:
        query_report = self.query(topic, limit=limit, group_limit=group_limit)
        context_items: list[dict[str, object]] = []
        for result in cast(list[dict[str, object]], query_report["results"]):
            read_result = self.read_memory(cast(str, result["file"]))
            context_items.append(
                {
                    "path": result["file"],
                    "score": result["score"],
                    "task_groups": result["task_groups"],
                    "provenance_pause_required": read_result[
                        "provenance_pause_required"
                    ],
                    "excerpt": cast(str, read_result["content"])[:excerpt_chars],
                    "frontmatter": read_result["frontmatter"],
                }
            )
        return {
            "topic": topic,
            "matched_task_groups": query_report["matched_task_groups"],
            "context": context_items,
        }

    def _find_access_log(self, file_path: Path) -> Path:
        relative_path = file_path.relative_to(self.repo_root).as_posix()
        top_level = relative_path.split("/", 1)[0]
        if top_level not in RETRIEVAL_ROOTS:
            raise ValueError(f"ACCESS logging is not supported for {relative_path}")
        if file_path.name == "SUMMARY.md":
            raise ValueError("Do not log SUMMARY.md retrievals")
        if (
            file_path.suffix.lower() == ".md"
            and cast(str, self.engine.determine_file_type(file_path)) != "content"
        ):
            raise ValueError(f"ACCESS logging is not supported for {relative_path}")
        for parent in [file_path.parent, *file_path.parents]:
            if parent == self.repo_root.parent:
                break
            access_file = parent / "ACCESS.jsonl"
            if access_file.exists():
                return access_file
            if parent == self.repo_root:
                break
        raise ValueError(f"Could not locate ACCESS.jsonl for {relative_path}")

    def log_access(
        self,
        relative_path: str,
        task: str,
        helpfulness: float,
        note: str,
        session_id: str | None = None,
        access_date: str | None = None,
    ) -> dict[str, object]:
        if not 0.0 <= helpfulness <= 1.0:
            raise ValueError("helpfulness must be between 0.0 and 1.0")
        file_path = self._resolve_repo_file(relative_path)
        access_log_path = self._find_access_log(file_path)
        entry = {
            "file": file_path.relative_to(self.repo_root).as_posix(),
            "date": access_date or time.strftime("%Y-%m-%d"),
            "task": task,
            "helpfulness": helpfulness,
            "note": note,
        }
        if session_id is not None:
            entry["session_id"] = session_id

        lock_path = access_log_path.with_suffix(access_log_path.suffix + ".lock")
        with FileLock(lock_path):
            with access_log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")

        aggregation_report, _markdown = cast(
            tuple[dict[str, object], str | None],
            self.engine.format_aggregation_report(
                self.repo_root,
                self.load_quick_reference(),
                self.load_inventory(),
                False,
            ),
        )
        return {
            "entry": entry,
            "access_log": access_log_path.relative_to(self.repo_root).as_posix(),
            "aggregation": {
                "stage": aggregation_report["stage"],
                "pending_entries": aggregation_report["pending_entries"],
                "aggregation_trigger": aggregation_report["aggregation_trigger"],
                "would_write_task_groups": aggregation_report[
                    "would_write_task_groups"
                ],
            },
        }
