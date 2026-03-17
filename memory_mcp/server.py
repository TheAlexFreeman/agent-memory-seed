from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable, TypeVar

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from memory_engine_service import MemoryEngineService, MemoryEngineServiceError

ResultT = TypeVar("ResultT")


class MemoryMCPApplication:
    def __init__(self, repo_root: Path, db_path: Path | None = None) -> None:
        self.service = MemoryEngineService(repo_root, db_path)

    def _run_tool(self, callback: Callable[[], ResultT]) -> ResultT:
        try:
            return callback()
        except MemoryEngineServiceError as exc:
            raise ToolError(f"{exc.code}: {exc}") from exc

    def status_memory(self) -> dict[str, object]:
        return self._run_tool(self.service.status)

    def read_memory(self, path: str) -> dict[str, object]:
        return self._run_tool(lambda: self.service.read_memory(path))

    def query_memory(
        self,
        query: str,
        task_group: str | None = None,
        limit: int = 10,
        group_limit: int = 5,
    ) -> dict[str, object]:
        return self._run_tool(
            lambda: self.service.query(query, task_group, limit, group_limit)
        )

    def get_context(
        self,
        topic: str,
        limit: int = 3,
        group_limit: int = 3,
        excerpt_chars: int = 1200,
    ) -> dict[str, object]:
        return self._run_tool(
            lambda: self.service.get_context(topic, limit, group_limit, excerpt_chars)
        )

    def log_access(
        self,
        path: str,
        task: str,
        helpfulness: float,
        note: str,
        session_id: str | None = None,
        access_date: str | None = None,
    ) -> dict[str, object]:
        return self._run_tool(
            lambda: self.service.log_access(
                path,
                task,
                helpfulness,
                note,
                session_id,
                access_date,
            )
        )

    def build_server(self) -> FastMCP[Any]:
        server: FastMCP[Any] = FastMCP(
            "agent-memory-seed",
            instructions=(
                "Thin MCP wrapper over the governed memory engine. "
                "Markdown and JSONL remain canonical; SQLite is derived state."
            ),
            dependencies=["mcp"],
        )
        server.tool(
            name="status_memory", description="Read engine status and live thresholds."
        )(self.status_memory)
        server.tool(
            name="read_memory",
            description="Read a repo file with provenance and trust metadata.",
        )(self.read_memory)
        server.tool(
            name="query_memory",
            description="Rank files using derived task-group matches.",
        )(self.query_memory)
        server.tool(
            name="get_context",
            description="Build a bounded context package for a topic.",
        )(self.get_context)
        server.tool(
            name="log_access",
            description="Append an ACCESS entry and report aggregation readiness.",
        )(self.log_access)
        return server


def build_server(repo_root: Path, db_path: Path | None = None) -> FastMCP[Any]:
    return MemoryMCPApplication(repo_root, db_path).build_server()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Phase 3 MCP server for agent-memory-seed"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Path to the memory repo root",
    )
    parser.add_argument(
        "--db-path", type=Path, default=None, help="Path to the derived SQLite database"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_server(args.repo_root, args.db_path).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
