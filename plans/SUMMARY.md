# Plans — Summary

This folder holds multi-session research and implementation plans. Plans track intended work and next actions; knowledge files track findings and skills track reusable procedures.

## Active plans

Read this section first during compact returning sessions when active plans exist.

Priority order for active work:

1. `django-stack-research.md`
2. `react-stack-research.md`
3. `devops-docker-research.md`
4. `lesswrong-rationalist-community-research.md`

<!-- BEGIN: lesswrong-rationalist-community-research -->
### `lesswrong-rationalist-community-research.md` · status: active · trust: medium

Narrative research plan for understanding LessWrong and the Rationalist community: Yudkowsky and the Sequences, heuristics-and-biases roots, Overcoming Bias, Scott Alexander, Gwern, and institutions such as MIRI and CFAR. Output goes to `knowledge/_unverified/rationalist-community/`.

**Progress:** 0/11 files written
**Next action:** Begin Phase 1 — write `knowledge/_unverified/rationalist-community/origins/eliezer-yudkowsky-intellectual-biography.md`
<!-- END: lesswrong-rationalist-community-research -->

---

<!-- BEGIN: django-stack-research -->
### `django-stack-research.md` · status: active · trust: medium
**Progress:** 5/10 items complete
**Next action:** `django-security.md`
<!-- END: django-stack-research -->

---

<!-- BEGIN: react-stack-research -->
### `react-stack-research.md` · status: active · trust: medium

Gaps and depth research for Alex's React + Chakra UI 3 frontend (backed by Django/DRF). 9 files planned across 8 phases. Priority order: TanStack Query (DRF integration) → react-hook-form + zod → TanStack Router → TypeScript patterns → testing (Vitest/RTL/MSW) → auth state management → performance → Vite build tooling → error boundaries + Suspense. Output goes to `knowledge/_unverified/react/`.

**Progress:** 3/9 files written
**Next action:** Begin Phase 3 — write `knowledge/_unverified/react/typescript-react-patterns.md`
<!-- END: react-stack-research -->

---

<!-- BEGIN: devops-docker-research -->
### `devops-docker-research.md` · status: active · trust: medium

Docker, Vite, and DevOps tooling for the full Django + React + Celery + Redis + Postgres stack. 10 files planned across 9 phases. Priority order: Docker Compose local dev → multi-worker Celery containers → nginx reverse proxy → production Docker config → GitHub Actions CI/CD → zero-downtime deploys → secrets/environment management → Celery + Prometheus monitoring → database ops → dev workflow tooling (Makefile, pre-commit, debugpy). Output goes to `knowledge/_unverified/devops/`.

**Progress:** 2/10 files written
**Next action:** Begin Phase 2 — write `knowledge/_unverified/devops/nginx-django-react.md`
<!-- END: devops-docker-research -->

---

## Completed plans

<!-- BEGIN: philosophy-history-survey -->
### `philosophy-history-survey.md` · status: complete · trust: medium

Broad narrative survey of the history of philosophy: 26 period/tradition files across 7 phases (ancient through contemporary + non-Western) plus 4 cross-cutting synthesis files (mind-body, language/meaning, the self, science/metaphysics/religion). All output in `knowledge/_unverified/philosophy/history/`.

**Progress:** 30/30 files written (26 period + 4 synthesis)
**Completed:** 2026-03-19
<!-- END: philosophy-history-survey -->

---

<!-- BEGIN: codex-desktop-github-network-ergonomics -->
### `codex-desktop-github-network-ergonomics.md` · status: complete · trust: medium

Task-readiness support for Codex desktop is now prototyped through a repo-declared manifest plus executable resolver covering GitHub publish checks, runtime and package-manager readiness, blocker carry-forward, and structured UI feedback.

**Progress:** 11/11 items complete
**Completed:** 2026-03-18
<!-- END: codex-desktop-github-network-ergonomics -->

---

<!-- BEGIN: codex-desktop-automation-continuity -->
### `codex-desktop-automation-continuity.md` · status: complete · trust: medium

Implementation plan for recurring-run continuity in Codex desktop completed: automation-local memory, plan pinning, branch/base-branch carry-forward, blocker persistence, structured run writeback, validation matrix, and rollout metrics.

**Progress:** 11/11 items complete
**Completed:** 2026-03-18
<!-- END: codex-desktop-automation-continuity -->

---

<!-- BEGIN: codex-desktop-bootstrap-support -->
### `codex-desktop-bootstrap-support.md` · status: complete · trust: medium

Concrete Codex desktop bootstrap roadmap completed: repo-declared startup manifest, mode detection, budget-aware preload ordering, startup panel UX contract, validation matrix, and staged rollout strategy.

**Progress:** 11/11 items complete
**Completed:** 2026-03-18
<!-- END: codex-desktop-bootstrap-support -->

---

<!-- BEGIN: ai-paradigm-genealogy-research -->
### `ai-paradigm-genealogy-research.md` · status: complete · trust: medium

Narrative genealogy of how the current AI paradigm formed: from perceptrons through symbolic AI, backpropagation, ConvNets/LSTMs, statistical NLP, the deep learning turn, transformers, BERT/GPT/scaling laws, RLHF, and frontier LLM systems. All 11 files written in `knowledge/_unverified/ai-history/`.

**Progress:** 11/11 files written
**Completed:** 2026-03-18
<!-- END: ai-paradigm-genealogy-research -->

---

<!-- BEGIN: codex-desktop-governed-memory-writes -->
### `codex-desktop-governed-memory-writes.md` · status: complete · trust: medium

Governed memory writes now have a repo-declared capability contract, discovery flow, UI feedback surface, and runtime invariant coverage for plan, knowledge, protected-path, and version-token cases.

**Progress:** 11/11 items complete
**Completed:** 2026-03-18
<!-- END: codex-desktop-governed-memory-writes -->

---

<!-- BEGIN: agent-memory-mcp -->
### `agent-memory-mcp.md` · status: complete · trust: medium

Enhanced agent-memory MCP now runs through the shipped `memory_mcp.py` entrypoint, exposes the read/write tool surface from `tools/agent_memory_mcp/`, and supports an optional runtime delete-permission helper for `memory_delete`.

**Progress:** 17/17 milestones complete
**Completed:** 2026-03-18
<!-- END: agent-memory-mcp -->

---

## Usage notes

- Keep active multi-session plans here. Use `scratchpad/CURRENT.md` for one-offs and `meta/` for governance.
- Required extra frontmatter: `type`, `status`, and `next_action`. `last_verified` means the plan was reviewed or advanced in-session.
- Log reads of `plans/*.md` in `plans/ACCESS.jsonl` when they materially inform a session. Do not log reads of this `SUMMARY.md`.
- Routine progress updates are automatic. New plans, retirements, and major scope changes should still be surfaced to the user.
