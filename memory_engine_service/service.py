from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Callable, NotRequired, TypeVar, cast

from typing_extensions import TypedDict

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

ResultT = TypeVar("ResultT")


class StatusInventory(TypedDict):
    indexed_files: int
    access_entries: int
    sessions: int


class StatusDatabaseSnapshot(TypedDict, total=False):
    indexed_files: int
    access_entries: int
    task_groups: int


class StatusResult(TypedDict):
    repo_root: str
    db_path: str
    db_exists: bool
    stage: object
    last_periodic_review: object
    thresholds: object
    inventory: StatusInventory
    database: NotRequired[StatusDatabaseSnapshot]


class QueryMatchedTaskGroup(TypedDict):
    group_name: object
    score: float
    entry_count: object


class QueryResultItem(TypedDict):
    file: str
    folder: object
    file_type: object
    score: float
    hit_count: int
    avg_helpfulness: float
    last_seen_date: object
    task_groups: list[str]


class QueryResult(TypedDict):
    repo_root: str
    query: str
    normalized_query_tokens: list[str]
    task_group_filter: str | None
    matched_task_groups: list[QueryMatchedTaskGroup]
    results: list[QueryResultItem]


class ReadMemoryResult(TypedDict):
    path: str
    folder: str
    file_type: str
    frontmatter: dict[str, str]
    is_quarantined: bool
    requires_access_log: bool
    provenance_pause_required: bool
    content: str
    size_bytes: int


class ContextItem(TypedDict):
    path: str
    score: float
    task_groups: list[str]
    provenance_pause_required: bool
    excerpt: str
    frontmatter: dict[str, str]


class ContextResult(TypedDict):
    topic: str
    matched_task_groups: list[QueryMatchedTaskGroup]
    context: list[ContextItem]


class AccessLogEntry(TypedDict):
    file: str
    date: str
    task: str
    helpfulness: float
    note: str
    session_id: NotRequired[str]


class AggregationState(TypedDict):
    stage: object
    pending_entries: object
    aggregation_trigger: object
    would_write_task_groups: object


class LogAccessResult(TypedDict):
    entry: AccessLogEntry
    access_log: str
    aggregation: AggregationState


class MemoryEngineServiceError(Exception):
    code = "service_error"


class InvalidRepositoryError(MemoryEngineServiceError):
    code = "invalid_repository"


class InventoryLoadError(MemoryEngineServiceError):
    code = "inventory_load_failed"


class InvalidMemoryRequestError(MemoryEngineServiceError):
    code = "invalid_request"


class MemoryNotFoundError(MemoryEngineServiceError):
    code = "memory_not_found"


class UnsupportedMemoryTargetError(MemoryEngineServiceError):
    code = "unsupported_target"


class MemoryWriteConflictError(MemoryEngineServiceError):
    code = "write_conflict"


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
        self.repo_root = self._resolve_repo_root(repo_root)
        self.db_path = cast(Path, self.engine.resolve_db_path(self.repo_root, db_path))

    def _wrap_engine_system_exit(
        self,
        callback: Callable[[], ResultT],
        error_type: type[MemoryEngineServiceError],
    ) -> ResultT:
        try:
            return callback()
        except SystemExit as exc:
            message = str(exc) or error_type.code.replace("_", " ")
            raise error_type(message) from exc

    def _resolve_repo_root(self, repo_root: Path) -> Path:
        return cast(
            Path,
            self._wrap_engine_system_exit(
                lambda: self.engine.detect_repo_root(repo_root),
                InvalidRepositoryError,
            ),
        )

    def _validate_non_negative(self, name: str, value: int) -> None:
        if value < 0:
            raise InvalidMemoryRequestError(f"{name} must be non-negative")

    def load_inventory(self) -> memory_engine.Inventory:
        return self._wrap_engine_system_exit(
            lambda: self.engine.load_inventory(self.repo_root),
            InventoryLoadError,
        )

    def load_quick_reference(self) -> dict[str, object]:
        try:
            return cast(
                dict[str, object],
                self.engine.parse_quick_reference(
                    self.repo_root / "meta" / "quick-reference.md"
                ),
            )
        except OSError as exc:
            raise InvalidRepositoryError(
                f"Unable to read quick reference: {exc}"
            ) from exc

    def status(self) -> StatusResult:
        return cast(
            StatusResult,
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
    ) -> QueryResult:
        self._validate_non_negative("limit", limit)
        self._validate_non_negative("group_limit", group_limit)
        return cast(
            QueryResult,
            self._wrap_engine_system_exit(
                lambda: self.engine.format_query_report(
                    self.repo_root,
                    self.load_inventory(),
                    query,
                    task_group,
                    limit,
                    group_limit,
                ),
                InvalidMemoryRequestError,
            ),
        )

    def _resolve_repo_file(self, relative_path: str) -> Path:
        candidate = (self.repo_root / relative_path).resolve()
        try:
            candidate.relative_to(self.repo_root)
        except ValueError as exc:
            raise InvalidMemoryRequestError(
                f"Path escapes repo root: {relative_path}"
            ) from exc
        if not candidate.exists() or not candidate.is_file():
            raise MemoryNotFoundError(relative_path)
        if candidate.suffix.lower() not in READABLE_TEXT_EXTENSIONS:
            raise UnsupportedMemoryTargetError(
                f"Unsupported file type for MCP read: {relative_path}"
            )
        return candidate

    def _build_read_metadata(self, file_path: Path) -> ReadMemoryResult:
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
            "content": "",
            "size_bytes": 0,
        }

    def read_memory(self, relative_path: str) -> ReadMemoryResult:
        file_path = self._resolve_repo_file(relative_path)
        metadata = self._build_read_metadata(file_path)
        try:
            metadata["content"] = file_path.read_text(encoding="utf-8")
            metadata["size_bytes"] = file_path.stat().st_size
            return metadata
        except OSError as exc:
            raise MemoryEngineServiceError(
                f"Unable to read memory file {relative_path}: {exc}"
            ) from exc

    def get_context(
        self,
        topic: str,
        limit: int = 3,
        group_limit: int = 3,
        excerpt_chars: int = 1200,
    ) -> ContextResult:
        self._validate_non_negative("limit", limit)
        self._validate_non_negative("group_limit", group_limit)
        self._validate_non_negative("excerpt_chars", excerpt_chars)
        query_report = self.query(topic, limit=limit, group_limit=group_limit)
        context_items: list[ContextItem] = []
        for result in query_report["results"]:
            read_result = self.read_memory(result["file"])
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
            raise UnsupportedMemoryTargetError(
                f"ACCESS logging is not supported for {relative_path}"
            )
        if file_path.name == "SUMMARY.md":
            raise UnsupportedMemoryTargetError("Do not log SUMMARY.md retrievals")
        if (
            file_path.suffix.lower() == ".md"
            and cast(str, self.engine.determine_file_type(file_path)) != "content"
        ):
            raise UnsupportedMemoryTargetError(
                f"ACCESS logging is not supported for {relative_path}"
            )
        for parent in [file_path.parent, *file_path.parents]:
            if parent == self.repo_root.parent:
                break
            access_file = parent / "ACCESS.jsonl"
            if access_file.exists():
                return access_file
            if parent == self.repo_root:
                break
        raise UnsupportedMemoryTargetError(
            f"Could not locate ACCESS.jsonl for {relative_path}"
        )

    def log_access(
        self,
        relative_path: str,
        task: str,
        helpfulness: float,
        note: str,
        session_id: str | None = None,
        access_date: str | None = None,
    ) -> LogAccessResult:
        if not 0.0 <= helpfulness <= 1.0:
            raise InvalidMemoryRequestError("helpfulness must be between 0.0 and 1.0")
        file_path = self._resolve_repo_file(relative_path)
        access_log_path = self._find_access_log(file_path)
        entry: AccessLogEntry = {
            "file": file_path.relative_to(self.repo_root).as_posix(),
            "date": access_date or time.strftime("%Y-%m-%d"),
            "task": task,
            "helpfulness": helpfulness,
            "note": note,
        }
        if session_id is not None:
            entry["session_id"] = session_id

        lock_path = access_log_path.with_suffix(access_log_path.suffix + ".lock")
        try:
            with FileLock(lock_path):
                with access_log_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(entry, sort_keys=True) + "\n")
        except TimeoutError as exc:
            raise MemoryWriteConflictError(
                f"Timed out writing ACCESS log for {relative_path}"
            ) from exc
        except OSError as exc:
            raise MemoryEngineServiceError(
                f"Unable to append ACCESS log for {relative_path}: {exc}"
            ) from exc

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
