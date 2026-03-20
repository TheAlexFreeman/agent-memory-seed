# Plans — Summary

Compact returning-session view of multi-session work. Read this file for live priorities, immediate next actions, and drill-down paths only.

Plans are categorized as **build** (code/infrastructure changes with a defined done-state) or **research** (knowledge-base work with an open or survey scope). Each category maintains its own priority stack. Within a session, pick the highest-priority item from whichever category fits the task at hand.

## Active plans

### Build plans

### `mcp-reorganization.md` · status: active · trust: medium · **TOP PRIORITY**

Detail: plans/mcp-reorganization.md
Progress: 22/41 complete
Next: Phase 3, item 24 — move the reset-tool registration into `semantic/_session.py`, then continue the semantic-tools split.
Blocks: `access-log-tooling-improvements.md`, `mcp-semantic-tools-improvements.md`, `mcp-read-tools-improvements.md`, `mcp-write-and-crosscutting-improvements.md`, and `worktree-integration.md` item 6.
Scope: Move the MCP implementation out of `tools/` into the `engram_mcp/` runtime package, then split the monolith and update path contracts under the Engram naming direction.

### `worktree-integration.md` · status: active · trust: medium

Detail: plans/worktree-integration.md
Scope: Support using this repo as an orphan-branch worktree attached to an existing project.
Progress: 0/24 complete
Next: Phase 0, item 1 — write init-worktree.sh scaffold
Blocks: item 6 waits on `mcp-reorganization.md` Phase 2; the rest can proceed independently.


### `access-log-tooling-improvements.md` · status: active · trust: medium

Detail: plans/access-log-tooling-improvements.md
Scope: Fix ACCESS logging noise, session identity, and missing coverage by adding batch writes and schema improvements.
Progress: 0/12 complete
Next: Phase 1, item 1 — implement `memory_log_access_batch` in `write_tools.py`
Blocks: waits on `mcp-reorganization.md` Phase 2.


### `mcp-semantic-tools-improvements.md` · status: active · trust: medium

Detail: plans/mcp-semantic-tools-improvements.md
Scope: Close semantic-tooling gaps around scratchpad writes, review-queue lifecycle, skills updates, session recording, and aggregation.
Progress: 0/22 complete
Next: Phase 1, item 1 — expand `memory_append_scratchpad` to accept dated scratchpad slugs
Blocks: waits on `mcp-reorganization.md` Phase 2.


### `mcp-read-tools-improvements.md` · status: active · trust: medium

Detail: plans/mcp-read-tools-improvements.md
Scope: Collapse manual session-start reads and improve git-log and trust-audit visibility.
Progress: 0/13 complete
Next: Phase 1, item 1 — add `since` and `path_filter` params to `memory_git_log` in `read_tools.py`
Blocks: waits on `mcp-reorganization.md` Phase 2.


### `mcp-write-and-crosscutting-improvements.md` · status: active · trust: medium

Detail: plans/mcp-write-and-crosscutting-improvements.md
Scope: Add frontmatter batch updates, native capability lookup, and richer search results.
Progress: 0/15 complete
Next: Phase 1, item 1 — implement `memory_update_frontmatter_bulk` in `write_tools.py`
Blocks: waits on `mcp-reorganization.md` Phase 2.

### Research plans

### `ai-frontier-research.md` · status: active · trust: medium · **TOP PRIORITY**

Detail: plans/ai-frontier-research.md
Scope: Frontier AI survey — reasoning, alignment, interpretability, multi-agent, retrieval/memory, emerging architectures.
Progress: Phase 1 complete; Phase 2 extension complete (4/4)
Next: Consider Phase 3 extension (RAG details, ColPali, late-chunking) or deeper agentic-framework follow-on work.


### Research queue

- `phenomenology-embodied-cognition-research.md` — 0/12; next: Husserl intentionality; detail: plans/phenomenology-embodied-cognition-research.md
- `personal-identity-memory-research.md` — 0/12; next: Locke's memory criterion; detail: plans/personal-identity-memory-research.md
- `ethics-metaethics-research.md` — 0/13; next: classical utilitarianism; detail: plans/ethics-metaethics-research.md
- `formal-logic-foundations-research.md` — 0/11; next: propositional and first-order logic; detail: plans/formal-logic-foundations-research.md
- `game-theory-mechanism-design-research.md` — 0/12; next: Nash equilibrium; detail: plans/game-theory-mechanism-design-research.md
- `information-theory-stat-learning-research.md` — 0/12; next: Shannon entropy; detail: plans/information-theory-stat-learning-research.md
- `cognitive-neuroscience-memory-research.md` — 0/11; next: Tulving episodic/semantic distinction; detail: plans/cognitive-neuroscience-memory-research.md
- `cultural-evolution-epistemics-research.md` — 0/12; next: meme concept; detail: plans/cultural-evolution-epistemics-research.md

## Recent completions

- [compact-bootstrap-efficiency.md](compact-bootstrap-efficiency.md) — completed 2026-03-20; startup contract enforced and measured under budget.
- [ai-frontier-research.md](ai-frontier-research.md) — completed 2026-03-19; frontier-AI knowledge set written.
- [systems-architecture-research.md](systems-architecture-research.md) — completed 2026-03-19; storage and concurrency primitives captured.
- [lesswrong-rationalist-community-research.md](lesswrong-rationalist-community-research.md) — completed 2026-03-19; community survey written.
- [devops-docker-research.md](devops-docker-research.md) — completed 2026-03-19; Docker and DevOps stack research written.
- [react-stack-research.md](react-stack-research.md) — completed 2026-03-19; React, Chakra UI, and TanStack research written.
- [django-stack-research.md](django-stack-research.md) — completed 2026-03-19; advanced Django research written.
- [philosophy-history-survey.md](philosophy-history-survey.md) — completed 2026-03-19; broad philosophy survey written.

## Usage notes

- Keep active multi-session plans here. Use `scratchpad/CURRENT.md` for one-offs and `meta/` for governance.
- Required frontmatter: `type`, `category` (`build` or `research`), `status`, `next_action`. `last_verified` means reviewed or advanced in-session.
- **Build**: defined done-state, dependency-ordered. **Research**: open-ended, phase-by-phase, pursue opportunistically. Build takes precedence when unblocked work is ready.
- Log reads of `plans/*.md` in `plans/ACCESS.jsonl` when they materially inform a session. Do not log reads of this `SUMMARY.md`.
- Routine progress updates are automatic. New plans, retirements, and major scope changes should still be surfaced to the user.
- Keep active blocks compact. Extended rationale belongs in the plan file itself, not here.

