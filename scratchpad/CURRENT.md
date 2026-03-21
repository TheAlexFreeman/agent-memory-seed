# Agent working notes

Provisional, agent-authored. Not formal memory. Each entry is dated and linked to its originating session. Entries are promoted to `identity/`, `knowledge/`, or `skills/` when confirmed, or cleared after ~3 sessions without action.

See `meta/scratchpad-guidelines.md` for the full write protocol, promotion criteria, and lifecycle rules.

---

## Active threads

- **Onboarding redesign.** Comprehensive review session (Cowork, 2026-03-20) produced `plans/onboarding-redesign.md` — a build plan to replace the interview-style onboarding with a collaborative first-session experience. Core idea: the user brings a real task, profile discovery happens as a byproduct of working together, and system capabilities are demonstrated inline rather than explained abstractly. Grounded in the cognitive science KB (human-LLM complementarity, relevance realization, metacognition synthesis, episodic memory formation). Phase 0 (design review with user) is next. User has deferred review for now.
- **Developmental governance model.** Alex articulated a key design philosophy: the human provides top-down governance while the agent accumulates bottom-up knowledge. Over time, as trust is earned, the agent gains more influence in higher-level decisions while the user gains understanding of lower-level dynamics. Analogy: raising a child, not launching a rocket. This frame is not yet captured in the formal design docs but should inform future governance evolution — particularly the maturity stage transitions and the question of when/how to relax protected-tier constraints per-domain. Consider proposing an addition to `HUMANS/docs/DESIGN.md` or `identity/engram-relationship.md`.
- **Plans → Projects overhaul.** Alex wants to subsume `plans/` into a `projects/` model where a project bundles open questions, accumulated knowledge, and action plans in a single scoped folder. Open questions are a first-class feature — a project is complete when all questions are resolved and all plans are done. Projects can resolve in one session or remain open indefinitely. Hard-coded starter projects (getting-to-know-you, system-literacy, general-knowledge-base, optional demo-app-build) replace the interview-style onboarding. Build plan at `plans/plans-to-projects-overhaul.md`. This takes priority over the onboarding redesign, which it will inform. Phase 0 (design review) is next.
- **System readiness for broader adoption.** Alex wants to move from self-development to serving other users. The projects overhaul and onboarding redesign are the concrete steps. Key insight from the review: the architecture is mature but experientially young — most usage has been meta-development (building the system) rather than real-world task work. The feedback loops (ACCESS-driven curation, retrieval patterns, aggregation) haven't been tested under real workload. Priority should shift from building to using.
- ACCESS logging is noisy and under-scoped: `plans/ACCESS.jsonl` dominates, sweep-style reads are overlogged, and `session_id` coverage is still very low.
- Multi-agent support likely wants worktree-level isolation plus single-writer promotion rules before true concurrent memory writes. No `agent_id` claim protocol exists yet.
- `identity/SUMMARY.md` is ~628 tokens against a 450-token compact budget target (+178 over). Overall budget still has headroom (5959/7000). Decision needed: trim SUMMARY, redistribute budget, or formally raise the target.
- The `_unverified/` backlog (80+ files across 8+ subdirectories) is growing faster than review capacity. Files start auto-archiving mid-July 2026. Promotion cadence should be discussed.
<!-- 2026-03-20, session: chats/2026/03/20/cowork-review -->

## Immediate next actions

- Aggregate `plans/ACCESS.jsonl` (100 entries, 6× over trigger — review-queue item from 2026-03-19).
- Access-log tooling is the next build priority: implement `memory_log_access_batch` in `write_tools.py` and start reducing `plans/ACCESS.jsonl` write noise.
- Treat batch ACCESS logging and governed review-queue resolution as the most valuable follow-on MCP improvements.

## Open questions

- Should `identity/SUMMARY.md`'s compact-path budget be formally raised to ~650 tokens to accommodate the richer portrait?
- What minimum `agent_id` or claim protocol is needed before multiple agents can safely share one repo?
- Is the knowledge flooding alarm (5 files/day) actually operational, or only documented? It should have fired during the initial research burst.

## Drill-down refs

- `plans/plans-to-projects-overhaul.md` ← projects architectural overhaul (highest priority)
- `plans/onboarding-redesign.md` ← collaborative onboarding build plan (blocked on projects overhaul)
- `plans/rationalist-ai-discourse-research.md` ← LessWrong/AI discourse research plan
- `scratchpad/2026-03-20-architecture-review-notes.md` ← full review from earlier this session
- `scratchpad/2026-03-18-automation-backlog.md`
- `scratchpad/2026-03-19-multi-agent-management-notes.md`
- `scratchpad/2026-03-19-mcp-tooling-development-notes.md`
- `plans/access-log-tooling-improvements.md`
- `plans/worktree-integration.md`
