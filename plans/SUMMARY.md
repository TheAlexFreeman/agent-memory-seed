# Plans — Summary

Compact returning-session view of multi-session work. Read this file for live priorities, immediate next actions, and drill-down paths only.

Plans are categorized as **build** (code/infrastructure changes with a defined done-state) or **research** (knowledge-base work with an open or survey scope). Each category maintains its own priority stack. Within a session, pick the highest-priority item from whichever category fits the task at hand.

## Active plans

### Build plans

### `access-log-tooling-improvements.md` · status: active · trust: medium · **TOP PRIORITY**

Detail: plans/access-log-tooling-improvements.md
Scope: Fix ACCESS logging noise, session identity, and missing coverage by adding batch writes and schema improvements.
Progress: 0/12 complete
Next: Phase 1, item 1 — implement `memory_log_access_batch` in `write_tools.py`
Blocks: none; structural prerequisites are complete.


### `mcp-read-tools-improvements.md` · status: active · trust: medium

Detail: plans/mcp-read-tools-improvements.md
Scope: Collapse manual session-start reads and improve git-log and trust-audit visibility.
Progress: 0/13 complete
Next: Phase 1, item 1 — add `since` and `path_filter` params to `memory_git_log` in `read_tools.py`
Blocks: none; structural prerequisites are complete.


### `mcp-write-and-crosscutting-improvements.md` · status: active · trust: medium

Detail: plans/mcp-write-and-crosscutting-improvements.md
Scope: Add frontmatter batch updates, native capability lookup, and richer search results.
Progress: 0/15 complete
Next: Phase 1, item 1 — implement `memory_update_frontmatter_bulk` in `write_tools.py`
Blocks: none; structural prerequisites are complete.

### Research plans

### `cognitive-neuroscience-memory-research.md` · status: not-started · trust: medium · **TOP PRIORITY**

Detail: plans/cognitive-neuroscience-memory-research.md
Scope: Empirical memory science — encoding, consolidation, retrieval, episodic/semantic distinction, reconsolidation, false memory formation.
Progress: 0/11
Next: Phase 1, item 1.1 — Tulving's episodic/semantic distinction
Blocks: none. Now highest-priority research after memetic-security completion; directly grounds trust-weighted retrieval and curation specs from memetic-security Phase 4.


### `ai-frontier-research.md` · status: active · trust: medium

Detail: plans/ai-frontier-research.md
Scope: Frontier AI survey — reasoning, alignment, interpretability, multi-agent, retrieval/memory, architectures.
Progress: Phase 1 + Phase 2 extension complete (4/4)
Next: Phase 3 extension (RAG details, ColPali) or agentic-framework follow-ons.


### Research queue

Ordered by priority. Rationale: Tier 1 plans directly inform Engram's design (cognitive-neuroscience grounds curation/retrieval, cultural-evolution extends memetic-security insights). Tier 2 builds core intellectual infrastructure. Tier 3 is important but less immediately actionable.

**Tier 1 — System-Relevant**
- `cognitive-neuroscience-memory-research.md` — 0/11; next: Tulving episodic/semantic. Grounds curation design (trust decay, retrieval weighting, consolidation) in empirical memory science. Priority increased: memetic-security design specs (Phase 4) reference trust-weighted retrieval and consolidation models that this plan would empirically ground.
- `cultural-evolution-epistemics-research.md` — 0/12; next: meme concept. Natural companion to the now-complete memetic-security research; explains propagation mechanisms for memetic threats.

**Tier 2 — Core Intellectual Infrastructure**
- `information-theory-stat-learning-research.md` — 0/12; next: Shannon entropy. Mathematical substrate for the compression-intelligence thesis; connects to AIT, MDL, and model evaluation.
- `formal-logic-foundations-research.md` — 0/11; next: propositional/first-order logic. Underpins reasoning capability analysis; connects to interpretability, incompleteness results, and AI limits.
- `phenomenology-embodied-cognition-research.md` — 0/12; next: Husserl intentionality. Grounds the embodiment critique; connects to dynamical-systems framework and LLM limitations analysis.

**Tier 3 — Rich but Lower Urgency**
- `personal-identity-memory-research.md` — 0/12; next: Locke's memory criterion. Philosophical foundations for agent persistence and continuity of identity across sessions.
- `ethics-metaethics-research.md` — 0/13; next: classical utilitarianism. Normative frameworks and moral realism; relevant to alignment theory but less directly system-relevant.
- `game-theory-mechanism-design-research.md` — 0/12; next: Nash equilibrium. Mathematical foundations for multi-agent coordination and mechanism design.

## Recent completions

- [memetic-security-research.md](memetic-security-research.md) — completed 2026-03-20; 18/18 items across 5 phases (threat taxonomy, mitigation audit, comparative analysis, design implications, irreducible core); 8 knowledge files in `_unverified/system-notes/` and `_unverified/ai-frontier/`; pending human review.
- [ai-paradigm-genealogy-research.md](ai-paradigm-genealogy-research.md) — completed 2026-03-18; genealogy of AI paradigm formation (11 files, perceptrons through transformers); pending promotion review.
- [worktree-integration.md](worktree-integration.md) — completed 2026-03-20; worktree deployment flow now has a deployed-worktree validator profile, validator-backed init-worktree E2E coverage, and dedicated CI enforcement.
- [mcp-semantic-tools-improvements.md](mcp-semantic-tools-improvements.md) — completed 2026-03-20; Tier 1 semantic tool gaps closed across scratchpad targeting, review-queue lifecycle, skill updates, composite session recording, and ACCESS aggregation compaction.
- [mcp-reorganization.md](mcp-reorganization.md) — completed 2026-03-20; Phase 5 validator/CI/layout verification finished and downstream MCP tooling plans unblocked.
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

