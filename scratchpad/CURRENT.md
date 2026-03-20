# Agent working notes

Provisional, agent-authored. Not formal memory. Each entry is dated and linked to its originating session. Entries are promoted to `identity/`, `knowledge/`, or `skills/` when confirmed, or cleared after ~3 sessions without action.

See `meta/scratchpad-guidelines.md` for the full write protocol, promotion criteria, and lifecycle rules.

---

## Active threads

- ACCESS logging is noisy and under-scoped: `plans/ACCESS.jsonl` dominates, sweep-style reads are overlogged, and `session_id` coverage is still very low.
- Compact bootstrap enforcement is now a first-class engineering task: keep startup files as handoff/index surfaces rather than narrative archives.
- Multi-agent support likely wants worktree-level isolation plus single-writer promotion rules before true concurrent memory writes.

## Immediate next actions

- Finish the compact-bootstrap plan by aligning summary formats, validator checks, and tests.
- Keep access-log tooling improvements queued behind the `mcp-reorganization.md` dependency chain.
- Treat `memory_session_health_check`, batch ACCESS logging, and governed review-queue resolution as the most valuable follow-on MCP improvements.

## Open questions

- Is whole-file compact mode sufficient long term, or will startup-safe subsections be needed later?
- Should low-value ACCESS sweep entries be skipped, downgraded into a scan log, or retained with richer metadata?
- What minimum `agent_id` or claim protocol is needed before multiple agents can safely share one repo?

## Drill-down refs

- `scratchpad/2026-03-18-automation-backlog.md`
- `scratchpad/2026-03-19-multi-agent-management-notes.md`
- `plans/access-log-tooling-improvements.md`
- `plans/compact-bootstrap-efficiency.md`
