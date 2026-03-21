# Agent working notes

Provisional, agent-authored. Not formal memory. Each entry is dated and linked to its originating session. Entries are promoted to `identity/`, `knowledge/`, or `skills/` when confirmed, or cleared after ~3 sessions without action.

See `meta/scratchpad-guidelines.md` for the full write protocol, promotion criteria, and lifecycle rules.

---

## Active threads

- **Onboarding redesign.** Plan at `plans/onboarding-redesign.md`. Phase 0 (design review) deferred by user.
- **Developmental governance model.** Human top-down governance; agent bottom-up knowledge; agent gains influence as trust builds. Not yet in formal design docs — candidate for `HUMANS/docs/DESIGN.md` or `identity/engram-relationship.md`.
- **Plans → Projects overhaul.** Plan at `plans/plans-to-projects-overhaul.md`. Projects bundle open questions, knowledge, and action plans. Highest priority; Phase 0 design review next. Subsumes onboarding redesign.
- **System readiness for broader adoption.** Architecture mature but experientially young; feedback loops untested under real workload. Priority: shift from building to using.
- ACCESS logging noisy: `plans/ACCESS.jsonl` dominates, sweep-style reads overlogged, `session_id` coverage very low.
- Multi-agent support needs worktree-level isolation and single-writer promotion before concurrent writes.
- `identity/SUMMARY.md` ~628 tokens vs 450-token target. Decision: trim, redistribute, or raise target.
- `_unverified/` backlog (80+ files, 8+ dirs) growing faster than review capacity. Auto-archiving mid-July 2026.

## Immediate next actions

- Aggregate `plans/ACCESS.jsonl` (100 entries, 6× over trigger — review-queue item from 2026-03-19).
- Implement `memory_log_access_batch` in `write_tools.py` to reduce ACCESS write noise.
- Treat batch ACCESS logging and governed review-queue resolution as next MCP priorities.

## Open questions

- Should `identity/SUMMARY.md` budget be formally raised to ~650 tokens?
- What minimum `agent_id` / claim protocol is needed before multiple agents can safely share one repo?
- Is the knowledge flooding alarm (5 files/day) actually operational?

## Drill-down refs

- `plans/plans-to-projects-overhaul.md` ← projects overhaul (highest priority)
- `plans/onboarding-redesign.md` ← collaborative onboarding (blocked on projects)
- `plans/rationalist-ai-discourse-research.md` ← LessWrong/AI discourse research
- `scratchpad/2026-03-20-architecture-review-notes.md` ← full review session
- `plans/access-log-tooling-improvements.md`
- `plans/worktree-integration.md`
