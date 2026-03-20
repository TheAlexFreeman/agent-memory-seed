# Plans — Summary

Compact returning-session view of multi-session work. Read this file for active plan priority, short scope, next actions, and recent completions. Open individual plan files only when the compact block is insufficient.

## Active plans

Read this section first during compact returning sessions when active plans exist.

Priority order for active work:



### `mcp-reorganization.md` · status: active · trust: medium · **TOP PRIORITY**

Detail: plans/mcp-reorganization.md
Scope: Move the MCP implementation out of `tools/` into the `engram_mcp/` runtime package, then split the monolith and update path contracts under the Engram naming direction.
Progress: 18/41 complete
Next: Phase 2, item 21 — remove the `tools/` compat shim, then run the full suite once the remaining historical `tools/` path references are reconciled.
Blocks: `access-log-tooling-improvements.md`, `mcp-semantic-tools-improvements.md`, `mcp-read-tools-improvements.md`, `mcp-write-and-crosscutting-improvements.md`, and `worktree-integration.md` item 6 after the reorganization reaches its path-update phase.





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





### `phenomenology-embodied-cognition-research.md` · status: active · trust: medium

Detail: plans/phenomenology-embodied-cognition-research.md
Scope: Deep survey of phenomenology (Husserl, Heidegger, Merleau-Ponty) and 4E embodied cognition (Varela/Thompson/Rosch, Clark & Chalmers) with synthesis into the existing dynamical-systems and grounding-problem threads.
Progress: 0/12 complete
Next: Phase 1, item 1 — Husserl's intentionality, epoché, and transcendental reduction.
Blocks: nothing.


### `personal-identity-memory-research.md` · status: active · trust: medium

Detail: plans/personal-identity-memory-research.md
Scope: Philosophy of personal identity — Locke, Hume, Parfit's reductionism and what-matters-in-survival, narrative identity (Ricoeur, Schechtman) — applied to the design of this repo.
Progress: 0/12 complete
Next: Phase 1, item 1 — Locke's memory criterion and the early modern identity debate.
Blocks: nothing.


### `ethics-metaethics-research.md` · status: active · trust: medium

Detail: plans/ethics-metaethics-research.md
Scope: Systematic normative ethics (utilitarianism, Kant, virtue, contractualism), Parfit's Reasons and Persons in depth, metaethics (realism vs. expressivism), and applied AI ethics (moral status, responsibility, fairness).
Progress: 0/13 complete
Next: Phase 1, item 1 — classical utilitarianism from Bentham to Singer.
Blocks: nothing.


### `formal-logic-foundations-research.md` · status: active · trust: medium

Detail: plans/formal-logic-foundations-research.md
Scope: Classical logic, Gödel's incompleteness theorems, Turing undecidability, type theory and the Curry-Howard isomorphism, ZFC and category theory as alternative foundations.
Progress: 0/11 complete
Next: Phase 1, item 1 — propositional and first-order logic, completeness.
Blocks: nothing.


### `game-theory-mechanism-design-research.md` · status: active · trust: medium

Detail: plans/game-theory-mechanism-design-research.md
Scope: Game theory foundations (Nash equilibrium, prisoner's dilemma, coordination), evolutionary game theory, mechanism design (VCG, Gale-Shapley), social choice (Arrow's impossibility), signaling theory.
Progress: 0/12 complete
Next: Phase 1, item 1 — normal-form games and Nash equilibrium.
Blocks: nothing.


### `information-theory-stat-learning-research.md` · status: active · trust: medium

Detail: plans/information-theory-stat-learning-research.md
Scope: Shannon information theory (entropy, channel capacity, KL divergence), rate-distortion theory, MDL principle, PAC learning, VC dimension, double descent, and generalization via inductive bias.
Progress: 0/12 complete
Next: Phase 1, item 1 — Shannon entropy and the source coding theorem.
Blocks: nothing.


### `cognitive-neuroscience-memory-research.md` · status: active · trust: medium

Detail: plans/cognitive-neuroscience-memory-research.md
Scope: Memory systems taxonomy (episodic/semantic/procedural/working), hippocampal consolidation, sleep replay, reconsolidation, Ebbinghaus forgetting curves, false memory — with implications for this repo's curation design.
Progress: 0/11 complete
Next: Phase 1, item 1 — Tulving's episodic/semantic distinction, biological substrates.
Blocks: nothing.


### `cultural-evolution-epistemics-research.md` · status: active · trust: medium

Detail: plans/cultural-evolution-epistemics-research.md
Scope: Memetics (Dawkins, Blackmore), dual inheritance theory (Boyd/Richerson/Henrich), cultural transmission biases, cumulative culture and collective intelligence, epistemic injustice (Fricker), and how LLMs affect cultural evolution.
Progress: 0/12 complete
Next: Phase 1, item 1 — Dawkins' meme concept and the conditions for cultural replication.
Blocks: nothing.


---

## Recent completions

- [ai-frontier-research.md](ai-frontier-research.md) — completed 2026-03-19; 21 knowledge files covering reasoning models, alignment, retrieval/memory, multi-agent coordination, interpretability, emerging architectures, and AI epistemology.
- [compact-bootstrap-efficiency.md](compact-bootstrap-efficiency.md) — completed 2026-03-20; compact startup contract enforced, drill-down references required, helper added, measured at 5705/7000 tokens with 1295 headroom.
- [systems-architecture-research.md](systems-architecture-research.md) — completed 2026-03-19; storage, concurrency, and data-model primitives for the memory system.
- [lesswrong-rationalist-community-research.md](lesswrong-rationalist-community-research.md) — completed 2026-03-19; LessWrong and rationalist-community narrative survey.
- [devops-docker-research.md](devops-docker-research.md) — completed 2026-03-19; Docker and DevOps stack research for the Django/React/Celery system.
- [react-stack-research.md](react-stack-research.md) — completed 2026-03-19; React 19 + Chakra UI + TanStack depth research.
- [django-stack-research.md](django-stack-research.md) — completed 2026-03-19; advanced Django, DRF, async, security, and operations research.
- [philosophy-history-survey.md](philosophy-history-survey.md) — completed 2026-03-19; broad history-of-philosophy survey and synthesis.
- [codex-desktop-github-network-ergonomics.md](codex-desktop-github-network-ergonomics.md) — completed 2026-03-18; task-readiness manifest and resolver prototype.
- [codex-desktop-automation-continuity.md](codex-desktop-automation-continuity.md) — completed 2026-03-18; recurring-run continuity support.
- [codex-desktop-bootstrap-support.md](codex-desktop-bootstrap-support.md) — completed 2026-03-18; repo-declared startup manifest and resolver direction.
- [ai-paradigm-genealogy-research.md](ai-paradigm-genealogy-research.md) — completed 2026-03-18; genealogy of the modern AI paradigm.
- [codex-desktop-governed-memory-writes.md](codex-desktop-governed-memory-writes.md) — completed 2026-03-18; governed-write capability contract prototype.
- [agent-memory-mcp.md](agent-memory-mcp.md) — completed 2026-03-18; shipped MCP entrypoint and write surface.

---

## Usage notes

- Keep active multi-session plans here. Use `scratchpad/CURRENT.md` for one-offs and `meta/` for governance.
- Required extra frontmatter: `type`, `status`, and `next_action`. `last_verified` means the plan was reviewed or advanced in-session.
- Log reads of `plans/*.md` in `plans/ACCESS.jsonl` when they materially inform a session. Do not log reads of this `SUMMARY.md`.
- Routine progress updates are automatic. New plans, retirements, and major scope changes should still be surfaced to the user.
- Keep active blocks compact. Extended rationale belongs in the plan file itself, not here.

