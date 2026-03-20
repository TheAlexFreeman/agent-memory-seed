# Plans — Summary

Compact returning-session view of multi-session work. Read this file for live priorities, immediate next actions, and drill-down paths only.

Plans are categorized as **build** (code/infrastructure changes with a defined done-state) or **research** (knowledge-base work with an open or survey scope). Each category maintains its own priority stack. Within a session, pick the highest-priority item from whichever category fits the task at hand.

## Active plans

### Build plans

- *(No active build plans. See recent completions below for the latest shipped build work.)*

### Research plans

### `software-testing-validation-research.md` · status: active · trust: medium · **TOP PRIORITY**

Detail: plans/software-testing-validation-research.md
Scope: Testing epistemology (oracle problem, Dijkstra impossibility), unit testing (FIRST, test doubles, TDD/BDD), black-box and white-box design techniques, mutation testing, property-based testing, integration/system/acceptance testing, performance and load testing, software QA process and metrics, formal verification (Hoare logic, model checking, abstract interpretation), ML evaluation methodology, and behavioral testing/red-teaming for AI systems.
Progress: 0/14 — not yet started.
Next: Begin Phase 1 — Testing foundations and unit testing. Output goes to `knowledge/software-engineering/testing/`.


### `cognitive-attention-executive-function-research.md` · status: **complete** · trust: medium

11/11 ✓ COMPLETE. Attention selection models, attentional bottleneck/blink, FIT, dual-process, executive functions (Miyake), CLT, vigilance, mind-wandering, transformer comparison, synthesis. 11 knowledge files in `knowledge/cognitive-science/attention/`.


### `cognitive-metacognition-calibration-research.md` · status: **complete** · trust: medium

10/10 ✓ COMPLETE. Nelson-Narens monitoring/control, FOK/JOL/TOT, calibration/overconfidence/hard-easy, Dunning-Kruger, illusion of knowing, source monitoring, metacognitive control of learning, conflict monitoring, calibrated uncertainty communication, synthesis. 10 knowledge files in `knowledge/cognitive-science/metacognition/`.


### `cognitive-concepts-categorization-research.md` · status: **complete** · trust: medium

12/12 ✓ COMPLETE. Classical theory failures, prototype theory, exemplar theory/GCM, theory-theory, Gärdenfors conceptual spaces, embodied/grounded cognition, structural alignment/analogy, conceptual change, ACT* knowledge compilation, basic level categories, conceptual hygiene, synthesis. 12 knowledge files in `knowledge/cognitive-science/concepts/`.


### `information-theory-stat-learning-research.md` · status: complete · trust: medium · **COMPLETE**

Detail: plans/information-theory-stat-learning-research.md
Scope: Shannon information theory, rate-distortion, MDL, PAC learning, VC dimension, modern generalization theory — mathematical substrate for the compression-intelligence thesis.
Progress: 12/12 ✓ COMPLETE
Next: Human review of knowledge/_unverified/mathematics/information-theory/ files recommended.


### `cultural-evolution-epistemics-research.md` · status: complete · trust: medium · **COMPLETE**

Detail: plans/cultural-evolution-epistemics-research.md
Scope: Memetic propagation, cultural evolution, epistemic norms — natural companion to memetic-security and cognitive-neuroscience research.
Progress: 12/12 ✓ COMPLETE
Next: Human review of knowledge/_unverified/social-science/cultural-evolution/ files recommended.


### `ai-frontier-research.md` · status: active · trust: medium

Detail: plans/ai-frontier-research.md
Scope: Frontier AI survey — reasoning, alignment, interpretability, multi-agent, retrieval/memory, architectures.
Progress: All 7 phases + Phase 2 infrastructure extension + Phase 3 retrieval extension complete (25/25 base + 9 extension items). Phase 3 extension: ColPali, late chunking, agentic RAG patterns, HyDE, reranking (5 files added to `retrieval-memory/`).
Next: No active items. Archive when reviewed, or add further extension phases.


### Research queue

Ordered by priority. Rationale: Tier 1 plans directly inform Engram's design (cognitive-neuroscience grounds curation/retrieval, cultural-evolution extends memetic-security insights). Tier 2 builds core intellectual infrastructure. Tier 3 is important but less immediately actionable.

**Tier 1 — System-Relevant**
- *(All original Tier 1 plans complete.)*

**Tier 2 — Core Intellectual Infrastructure** ← **CURRENT PRIORITY**
- `formal-logic-foundations-research.md` — 11/11 ✓ COMPLETE. Underpins reasoning capability analysis; connects to interpretability, incompleteness results, and AI limits.
- `phenomenology-embodied-cognition-research.md` — 12/12 ✓ COMPLETE. Husserl → Heidegger → Merleau-Ponty → 4E cognition → grounding/synthesis; grounds the embodiment critique and LLM limitations analysis.

**Tier 3 — Rich but Lower Urgency** ← **CURRENT PRIORITY**
- `personal-identity-memory-research.md` — 12/12 ✓ COMPLETE. Locke → Hume → four-dimensionalism → Parfit → Ricoeur → MacIntyre → Schechtman → AI identity synthesis/failure modes/design recommendations.
- `ethics-metaethics-research.md` — 13/13 ✓ COMPLETE. Classical frameworks (utilitarianism, Kantian deontology, virtue ethics, contractualism), Parfit's *Reasons and Persons* (self-defeating theories, consequentialism, population ethics, collective action), metaethics (moral realism, anti-realism/expressivism, moral epistemology), applied AI ethics (moral status/welfare, responsibility attribution, algorithmic fairness).
- `game-theory-mechanism-design-research.md` — 12/12 ✓ COMPLETE. Normal-form games/Nash, Prisoner's Dilemma/coordination, extensive-form/backward induction, evolutionary game theory, evolution of cooperation (Axelrod), mechanism design/revelation principle, VCG mechanisms, matching markets (Gale-Shapley/Roth), Arrow's impossibility theorem, voting rules/Gibbard-Satterthwaite, costly signaling (Spence), cheap talk (Crawford-Sobel).

## Recent completions

- [cognitive-concepts-categorization-research.md](cognitive-concepts-categorization-research.md) — completed 2026-03-20; 12/12 items across 3 phases (classical/prototype/exemplar/theory-theory, conceptual spaces/embodied cognition/analogy, conceptual change/compilation/hygiene/synthesis); 12 knowledge files in `knowledge/cognitive-science/concepts/`; pending human review.
- [cognitive-metacognition-calibration-research.md](cognitive-metacognition-calibration-research.md) — completed 2026-03-20; 10/10 items across 3 phases (monitoring/control framework, calibration failure modes, learning control/communication/synthesis); 10 knowledge files in `knowledge/cognitive-science/metacognition/`; pending human review.
- [cognitive-attention-executive-function-research.md](cognitive-attention-executive-function-research.md) — completed 2026-03-20; 11/11 items across 3 phases (selection/capacity models, dual-process/executive function, sustained attention/synthesis); 11 knowledge files in `knowledge/cognitive-science/attention/`; pending human review.
- [game-theory-mechanism-design-research.md](game-theory-mechanism-design-research.md) — completed 2026-03-20; 12/12 items across 5 phases (normal-form games/Nash, Prisoner's Dilemma/coordination, extensive-form/backward induction, evolutionary game theory, evolution of cooperation/Axelrod, mechanism design/revelation principle, VCG mechanisms, matching markets/Gale-Shapley/Roth, Arrow's impossibility theorem, voting rules/Gibbard-Satterthwaite, costly signaling/Spence, cheap talk/Crawford-Sobel); 12 knowledge files in `_unverified/mathematics/game-theory/`; pending human review.
- [mcp-read-tools-improvements.md](mcp-read-tools-improvements.md) — completed 2026-03-20; 13/13 items across 4 phases (git-log filters, session health check, trust-audit warning band, read-surface contract/test updates); `memory_git_log` now supports `since` and `path_filter`, `memory_session_health_check` collapses session-start maintenance checks, and `memory_audit_trust` now surfaces an `approaching` bucket via `warn_pct`.
- [mcp-write-and-crosscutting-improvements.md](mcp-write-and-crosscutting-improvements.md) — completed 2026-03-20; 15/15 items across 3 phases (bulk frontmatter updates, capability discovery, richer search context); raw batch frontmatter updates, repo capability discovery, and contextual search rendering all landed with focused contract coverage.
- [mcp-curation-and-analytics-tools.md](mcp-curation-and-analytics-tools.md) — completed 2026-03-20; 22/22 items across 5 phases (batch promotion, cross-reference validation, summary generation, access analytics, branch divergence); the governed read/write surface now covers the full curation loop from promotion through validation and review reporting.
- [access-log-tooling-improvements.md](access-log-tooling-improvements.md) — completed 2026-03-20; 13/13 items across 3 phases (ACCESS routing cleanup, session identity propagation, batch logging support); ACCESS writes now support richer session-aware maintenance flows.
- [ethics-metaethics-research.md](ethics-metaethics-research.md) — completed 2026-03-20; 13/13 items across 4 phases (classical frameworks, Parfit's Reasons and Persons, metaethics, applied AI ethics); 13 knowledge files in `_unverified/philosophy/ethics/`; pending human review.
- [personal-identity-memory-research.md](personal-identity-memory-research.md) — completed 2026-03-20; 12/12 items across 4 phases (early modern debate, Parfit's reductionism, narrative identity, AI identity synthesis); 12 knowledge files in `_unverified/philosophy/personal-identity/`; pending human review.
- [phenomenology-embodied-cognition-research.md](phenomenology-embodied-cognition-research.md) — completed 2026-03-20; 12/12 items across 5 phases (Husserlian foundations, Heidegger, Merleau-Ponty, 4E cognition, application/synthesis); 12 knowledge files in `_unverified/philosophy/phenomenology/`; pending human review.
- [formal-logic-foundations-research.md](formal-logic-foundations-research.md) — completed 2026-03-20; 11/11 items across 4 phases (classical logic, incompleteness/undecidability, type theory, set theory/alternatives); 11 knowledge files in `_unverified/mathematics/logic-foundations/`; pending human review.
- [information-theory-stat-learning-research.md](information-theory-stat-learning-research.md) — completed 2026-03-20; 12/12 items across 4 phases (Shannon info theory, rate-distortion, statistical learning theory, synthesis); 12 knowledge files in `_unverified/mathematics/information-theory/`; pending human review.
- [cultural-evolution-epistemics-research.md](cultural-evolution-epistemics-research.md) — completed 2026-03-20; 12/12 items across 4 phases (foundations/memes, dual inheritance/transmission biases, cumulative culture/norms, epistemic communities/LLMs); 12 knowledge files in `_unverified/social-science/cultural-evolution/`; pending human review.
- [cognitive-neuroscience-memory-research.md](cognitive-neuroscience-memory-research.md) — completed 2026-03-20; 11/11 items across 4 phases (memory taxonomy, hippocampal consolidation, reconsolidation, forgetting/false memory); 11 knowledge files in `_unverified/cognitive-science/memory/`; pending human review.
- [memetic-security-research.md](memetic-security-research.md) — completed 2026-03-20; 18/18 items across 5 phases (threat taxonomy, mitigation audit, comparative analysis, design implications, irreducible core); 8 knowledge files in `_unverified/system-notes/` and `_unverified/ai-frontier/`; pending human review.
- [ai-paradigm-genealogy-research.md](ai-paradigm-genealogy-research.md) — completed 2026-03-18; genealogy of AI paradigm formation (11 files, perceptrons through transformers); pending promotion review.
- [worktree-integration.md](worktree-integration.md) — completed 2026-03-20; worktree deployment flow now has a deployed-worktree validator profile, validator-backed init-worktree E2E coverage, and dedicated CI enforcement.
- [mcp-semantic-tools-improvements.md](mcp-semantic-tools-improvements.md) — completed 2026-03-20; Tier 1 semantic tool gaps closed across scratchpad targeting, review-queue lifecycle, skill updates, composite session recording, and ACCESS aggregation compaction.
- [mcp-reorganization.md](mcp-reorganization.md) — completed 2026-03-20; Phase 5 validator/CI/layout verification finished and downstream MCP tooling plans unblocked.
- [compact-bootstrap-efficiency.md](compact-bootstrap-efficiency.md) — completed 2026-03-20; startup contract enforced and measured under budget.
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

