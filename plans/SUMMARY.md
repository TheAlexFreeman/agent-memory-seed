# Plans — Summary

This folder holds multi-session research and implementation plans. Plans track intended work and next actions; knowledge files track findings and skills track reusable procedures.

## Active plans

Read this section first during compact returning sessions when active plans exist.

Priority order for active work:

1. `codex-desktop-bootstrap-support.md`
2. `codex-desktop-governed-memory-writes.md`
3. `codex-desktop-automation-continuity.md`
4. `codex-desktop-github-network-ergonomics.md`
5. `django-stack-research.md`
6. `react-stack-research.md`
7. `devops-docker-research.md`
8. `philosophy-history-survey.md`
9. `lesswrong-rationalist-community-research.md`
10. `ai-paradigm-genealogy-research.md`

---

<!-- BEGIN: codex-desktop-bootstrap-support -->
### `codex-desktop-bootstrap-support.md` · status: active · trust: medium

Implementation plan for memory-aware repo startup in Codex desktop. Focus: repo-declared startup manifests, first-run vs. returning-session detection, compact preload ordering, and startup UI for branch/worktree/bootstrap state.

**Progress:** 3/11 tasks complete
**Next action:** Phase 2 — translate the manifest-backed prototype into app-side detection, dedup, and preload telemetry behavior
<!-- END: codex-desktop-bootstrap-support -->

---

<!-- BEGIN: codex-desktop-governed-memory-writes -->
### `codex-desktop-governed-memory-writes.md` · status: active · trust: medium

Implementation plan for first-class governed memory operations in Codex desktop. Focus: semantic write tools, invariant ownership, governance enforcement, and MCP/app integration for structured memory writes.

**Progress:** 0/11 tasks complete
**Next action:** Phase 1 — define the semantic memory operation set and invariant ownership model
<!-- END: codex-desktop-governed-memory-writes -->

---

<!-- BEGIN: codex-desktop-automation-continuity -->
### `codex-desktop-automation-continuity.md` · status: active · trust: medium

Implementation plan for recurring-run continuity in Codex desktop. Focus: automation-local memory, plan pinning, branch/base-branch carry-forward, blocker persistence, and structured run writeback.

**Progress:** 0/11 tasks complete
**Next action:** Phase 1 — define the automation run-state model and memory handoff contract
<!-- END: codex-desktop-automation-continuity -->

---

<!-- BEGIN: codex-desktop-github-network-ergonomics -->
### `codex-desktop-github-network-ergonomics.md` · status: active · trust: medium

Implementation plan for earlier GitHub, network, and runtime blocker detection in Codex desktop. Focus: preflight checks, task-aware readiness, blocker reporting, and recovery ergonomics.

**Progress:** 0/11 tasks complete
**Next action:** Phase 1 — define preflight checks for GitHub auth, network reachability, and local tooling availability
<!-- END: codex-desktop-github-network-ergonomics -->

<!-- BEGIN: philosophy-history-survey -->
### `philosophy-history-survey.md` · status: active · trust: medium

Broad survey of the history of philosophy — the overarching story of how ideas developed, what mattered in different times and places, how schools influenced one another. 26 output files planned across 7 phases + 4 synthesis files. Output goes to `knowledge/_unverified/philosophy/history/`.

**Progress:** 0/26 files written (0/4 synthesis files)
**Next action:** Begin Phase 1 — write `knowledge/_unverified/philosophy/history/ancient/pre-socratics.md`
<!-- END: philosophy-history-survey -->

---

<!-- BEGIN: lesswrong-rationalist-community-research -->
### `lesswrong-rationalist-community-research.md` · status: active · trust: medium

Narrative research plan for understanding LessWrong and the Rationalist community: Yudkowsky and the Sequences, heuristics-and-biases roots, Overcoming Bias, Scott Alexander, Gwern, and institutions such as MIRI and CFAR. Output goes to `knowledge/_unverified/rationalist-community/`.

**Progress:** 0/11 files written
**Next action:** Begin Phase 1 — write `knowledge/_unverified/rationalist-community/origins/eliezer-yudkowsky-intellectual-biography.md`
<!-- END: lesswrong-rationalist-community-research -->

---

<!-- BEGIN: ai-paradigm-genealogy-research -->
### `ai-paradigm-genealogy-research.md` · status: active · trust: medium

Narrative research plan for understanding how the current AI paradigm formed: perceptrons, symbolic detours, backpropagation, deep learning, transformers, scaling, and frontier LLM systems. Output goes to `knowledge/_unverified/ai-history/`.

**Progress:** 0/11 files written
**Next action:** Begin Phase 1 — write `knowledge/_unverified/ai-history/origins/cybernetics-perceptrons-and-the-first-connectionist-wave.md`
<!-- END: ai-paradigm-genealogy-research -->

---

<!-- BEGIN: django-stack-research -->
### `django-stack-research.md` · status: active · trust: medium

Gaps and depth research for Alex's Django + Celery + Postgres + Redis + Docker stack. 10 files planned across 7 phases. Priority order: Celery Canvas in depth → Celery worker/beat ops → drf-spectacular → Django test data/factories → Django async → Django security → Django migrations advanced → gunicorn/uvicorn deployment → database connection pooling → django-storages. Output goes to `knowledge/_unverified/django/`.

**Progress:** 2/10 files written
**Next action:** Begin Phase 2 — write `knowledge/_unverified/django/drf-spectacular.md`
<!-- END: django-stack-research -->

---

<!-- BEGIN: react-stack-research -->
### `react-stack-research.md` · status: active · trust: medium

Gaps and depth research for Alex's React + Chakra UI 3 frontend (backed by Django/DRF). 9 files planned across 8 phases. Priority order: TanStack Query (DRF integration) → react-hook-form + zod → TanStack Router → TypeScript patterns → testing (Vitest/RTL/MSW) → auth state management → performance → Vite build tooling → error boundaries + Suspense. Output goes to `knowledge/_unverified/react/`.

**Progress:** 0/9 files written
**Next action:** Begin Phase 1 — write `knowledge/_unverified/react/tanstack-query.md`
<!-- END: react-stack-research -->

---

<!-- BEGIN: devops-docker-research -->
### `devops-docker-research.md` · status: active · trust: medium

Docker, Vite, and DevOps tooling for the full Django + React + Celery + Redis + Postgres stack. 10 files planned across 9 phases. Priority order: Docker Compose local dev → multi-worker Celery containers → nginx reverse proxy → production Docker config → GitHub Actions CI/CD → zero-downtime deploys → secrets/environment management → Celery + Prometheus monitoring → database ops → dev workflow tooling (Makefile, pre-commit, debugpy). Output goes to `knowledge/_unverified/devops/`.

**Progress:** 0/10 files written
**Next action:** Begin Phase 1 — write `knowledge/_unverified/devops/docker-compose-local-dev.md`
<!-- END: devops-docker-research -->

---

## Completed plans

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
