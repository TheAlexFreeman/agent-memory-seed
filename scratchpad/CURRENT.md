# Agent working notes

Provisional, agent-authored. Not formal memory. Each entry is dated and linked to its originating session. Entries are promoted to `identity/`, `knowledge/`, or `skills/` when confirmed, or cleared after ~3 sessions without action.

See `meta/scratchpad-guidelines.md` for the full write protocol, promotion criteria, and lifecycle rules.

---

## Active threads

- ACCESS logging is noisy and under-scoped: `plans/ACCESS.jsonl` dominates, sweep-style reads are overlogged, and `session_id` coverage is still very low.
- Multi-agent support likely wants worktree-level isolation plus single-writer promotion rules before true concurrent memory writes. No `agent_id` claim protocol exists yet.
- `identity/SUMMARY.md` is ~628 tokens against a 450-token compact budget target (+178 over). Overall budget still has headroom (5959/7000). Decision needed: trim SUMMARY, redistribute budget, or formally raise the target.
- The `_unverified/` backlog (80+ files across 8+ subdirectories) is growing faster than review capacity. Files start auto-archiving mid-July 2026. Promotion cadence should be discussed.
<!-- 2026-03-20, session: chats/2026/03/20/cowork-enrichment -->

## Immediate next actions

- Aggregate `plans/ACCESS.jsonl` (100 entries, 6× over trigger — review-queue item from 2026-03-19).
- Worktree integration Phase 5, item 21 is next: add validator-side worktree mode detection and host/memory topology checks.
- Treat batch ACCESS logging and governed review-queue resolution as the most valuable follow-on MCP improvements.

## Open questions

- Should `identity/SUMMARY.md`'s compact-path budget be formally raised to ~650 tokens to accommodate the richer portrait?
- What minimum `agent_id` or claim protocol is needed before multiple agents can safely share one repo?
- Is the knowledge flooding alarm (5 files/day) actually operational, or only documented? It should have fired during the initial research burst.

## Drill-down refs

- `scratchpad/2026-03-20-architecture-review-notes.md` ← full review from this session
- `scratchpad/2026-03-18-automation-backlog.md`
- `scratchpad/2026-03-19-multi-agent-management-notes.md`
- `scratchpad/2026-03-19-mcp-tooling-development-notes.md`
- `plans/access-log-tooling-improvements.md`
- `plans/worktree-integration.md`
