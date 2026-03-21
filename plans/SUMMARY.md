# Plans — Summary

Compact returning-session view of multi-session work. Read this file for live priorities, immediate next actions, and drill-down paths only.

Plans are categorized as **build** (code/infrastructure changes with a defined done-state) or **research** (knowledge-base work with an open or survey scope). Each category maintains its own priority stack. Within a session, pick the highest-priority item from whichever category fits the task at hand.

## Active plans

### Build plans

- [mcp-knowledge-reorganization-tools.md](mcp-knowledge-reorganization-tools.md) — MCP tools for compositional KB reorganization: memory_find_references, memory_validate_links, memory_reorganize_preview, memory_reorganize_path, memory_suggest_structure; Phase 1 next (reference extractor + find_references).
- [mcp-agent-discoverability-guidance.md](mcp-agent-discoverability-guidance.md) — MCP agent discoverability and guidance: server name discovery doc, tool disambiguation (list_pending_reviews vs prepare_unverified_review, subtree vs batch), routing accuracy for promotion intents, warning clarity, paths-only enum; Phase 1 next.
- [checklist-app-architecture.md](checklist-app-architecture.md) — Django/React checklist tool for task management and progress tracking; Phase 1 next (Django scaffold + models).

### Research plans

- [social-science-expansion-research.md](social-science-expansion-research.md) — Expand social science KB beyond cultural evolution into 6 domains: sociology of knowledge/STS, collective action/institutions, social psychology, behavioral economics, network diffusion, social epistemology; 30 files across 6 phases; Phase 1 next.

## Recent completions

- [mcp-agent-friendliness-improvements.md](mcp-agent-friendliness-improvements.md) — completed 2026-03-21; 31/31 items across 7 phases (promotion parity, routing/policy-state helpers, preview contract support, workflow bundles, advisory tool profiles, MCP-native resources/prompts, provenance enrichment, structured extraction); the governed MCP surface now covers routing, previews, workflow bootstraps, host-side narrowing metadata, MCP-native navigation primitives, lineage-aware provenance reads, and section-based large-file inspection.
- [mcp-agent-discoverability-guidance.md](mcp-agent-discoverability-guidance.md) — completed 2026-03-21; 11/11 checklist items complete across re-baselining, discovery guidance, workflow hints, subtree-aware promotion prep, paths-only unverified enumeration, warning clarity, and periodic-review runtime reliability.
- [software-testing-validation-research.md](software-testing-validation-research.md) — completed 2026-03-20; 14/14 items across 5 phases (testing foundations/epistemology, unit testing/TDD/BDD, black-box and white-box design/mutation/property-based testing, integration/system/acceptance/performance testing, formal verification/AI-ML evaluation/behavioral testing/red-teaming); 14 knowledge files in `knowledge/software-engineering/testing/`; pending human review.
- [ai-frontier-research.md](ai-frontier-research.md) — completed (date unrecorded); 25/25 base + 9 extension items across 7 phases + Phase 2 infrastructure extension + Phase 3 retrieval extension (ColPali, late chunking, agentic RAG patterns, HyDE, reranking); knowledge files in `knowledge/ai/`; pending human review.
- [relevance-realization-research.md](relevance-realization-research.md) — completed 2026-03-20; 13/13 items across 4 phases (Gestalt/frame-problem antecedents, opponent-processing/four-kinds-of-knowing/aptitudes-of-intelligence, insight behavioral/neural/mechanism, rationality/wisdom/meaning-crisis/synthesis); 13 knowledge files in `knowledge/cognitive-science/relevance-realization/`; pending human review.
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
- [memetic-security-research.md](memetic-security-research.md) — completed 2026-03-20; 18/18 items across 5 phases (threat taxonomy, mitigation audit, comparative analysis, design implications, irreducible core); 8 knowledge files in `_unverified/system-notes/` and `knowledge/ai/frontier/`; pending human review.
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

---

<!-- BEGIN: mcp-agent-friendliness-improvements -->
### MCP Agent-Friendliness Improvements · status: complete · trust: medium
Detail: plans/mcp-agent-friendliness-improvements.md
Scope: Improve the repo-local MCP surface so agents can route intents correctly, preview governed writes consistently, follow common workflows in fewer calls, and reason about policy and provenance with less reconstruction overhead. Top-priority build plan as of 2026-03-20.
Progress: 31/31 checklist items complete; Phases 1-7 finished (promotion-path parity, routing/policy-state helpers, preview contract support, compact workflow bundles, advisory tool-profile reporting, MCP-native resources/prompts, and provenance-aware structured extraction).
Next: All planned phases complete.
<!-- END: mcp-agent-friendliness-improvements -->

---

<!-- BEGIN: mcp-unverified-review-workflow-improvements -->
### MCP Unverified Review Workflow Improvements · status: complete · trust: medium
Detail: plans/mcp-unverified-review-workflow-improvements.md
Scope: Address 7 friction points identified during the 2026-03-20 unverified mathematics promotion session (35 files). Ranked by estimated time-savings per session. Top priority as of 2026-03-20.
Progress: Phases 1-7 complete (42/42 checklist items); inline reads, summary-aware promotion, previews, review digests, subtree promotion, discoverability docs, and review-log tracking all landed.
Next: All planned phases complete.
<!-- END: mcp-unverified-review-workflow-improvements -->

---

<!-- BEGIN: mathematics-research-expansion -->
### Mathematics Knowledge Base Expansion · status: active · trust: medium
Detail: plans/mathematics-research-expansion.md
Scope: Expand the mathematics knowledge base from 35 files (logic-foundations, game-theory, information-theory) into 6 additional domains identified as high-relevance to Alex's core intellectual interests: dynamical systems, probability theory, statistical mechanics, causal inference, computational complexity, and optimization. Prioritized by connection to existing research programs and foundational leverage.
Progress: 0/0 complete
Next: Execute Phase 1 (Dynamical Systems & Chaos): highest priority — Alex's stated primary framework for intelligence has no files in the knowledge base.
<!-- END: mathematics-research-expansion -->

---

<!-- BEGIN: social-science-expansion-research -->
### Social Science Knowledge Base Expansion · status: active · trust: medium
Detail: plans/social-science-expansion-research.md
Scope: Expand social science beyond cultural evolution (12 files) into 6 domains: sociology of knowledge/STS (Mannheim, Merton, Kuhn, Latour), collective action/institutions (Olson, Ostrom, North, Acemoglu-Robinson), social psychology (Asch, Milgram, group dynamics), behavioral economics (Kahneman/Tversky, prospect theory, nudges), network diffusion (Granovetter, Rogers, wisdom of crowds), social epistemology (Goldman, extended mind).
Progress: 0/30 files across 6 phases.
Next: Execute Phase 1 (Sociology of Knowledge & STS) — Mannheim, Merton, Kuhn, Latour; how scientific knowledge is socially produced and contested.
<!-- END: social-science-expansion-research -->

---

<!-- BEGIN: mcp-agent-discoverability-guidance -->
### MCP Agent Discoverability and Guidance · status: complete · trust: medium
Detail: plans/mcp-agent-discoverability-guidance.md
Scope: Re-baseline plus finish-pass on MCP discoverability and promotion guidance. The plan delivered discovery notes, route workflow hints, subtree-aware promotion prep, full-path unverified enumeration, clearer subtree warnings, and the periodic-review reliability fix.
Progress: 11/11 checklist items complete.
Next: All planned phases complete.
<!-- END: mcp-agent-discoverability-guidance -->

---

<!-- BEGIN: mcp-knowledge-reorganization-tools -->
### MCP Knowledge Base Reorganization Tools · status: draft · trust: medium
Detail: plans/mcp-knowledge-reorganization-tools.md
Scope: Reference discovery (memory_find_references), link validation (memory_validate_links), reorganization preview and execution (memory_reorganize_preview, memory_reorganize_path), optional structure suggestions (memory_suggest_structure). Friction from 2026-03-21 ai-frontier → ai/frontier move.
Progress: 0/17 checklist items
Next: Phase 1 — Design reference extraction contract, implement extractor and memory_find_references.
<!-- END: mcp-knowledge-reorganization-tools -->
