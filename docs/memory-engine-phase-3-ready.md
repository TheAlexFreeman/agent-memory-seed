# Memory Engine Phase 3 Readiness

This note captures what the current implementation now makes possible for the next planning round.

## Ready inputs for Phase 3

- Derived task groups are available from ACCESS history through both `task-groups` and `query`.
- Calibration-stage aggregation can now materialize those groups into canonical repo state via `meta/task-groups.md`.
- Rebuild persists the derived grouping layer into SQLite, so future CLI or MCP features do not need to recompute everything from scratch.
- Query results already expose a lightweight ranking model over task groups and files, which provides a concrete surface for evaluating any later retrieval changes.
- A first MCP server slice can now be built as a thin wrapper over shared engine services rather than a second implementation.

## Natural Phase 3 focus

- Controlled category vocabulary generation from `meta/task-groups.md`
- Backfill and validation strategy for future ACCESS `category` values
- Query refinement once category data exists
- MCP operations that can read categories and derived retrieval results without bypassing governance

## Initial implementation slice

- Extract a reusable Python service layer over the current engine logic.
- Launch a stdio MCP server with `status_memory`, `read_memory`, `query_memory`, `get_context`, and `log_access`.
- Keep canonical writes limited to ACCESS appends; defer broader proposal workflows.

## Constraint to preserve

Phase 3 should still keep Markdown and JSONL as the canonical memory store. New category logic should be explicit, inspectable, and rebuildable from repo state.
