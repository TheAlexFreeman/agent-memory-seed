# Plans — Summary

This folder holds multi-session research and implementation plans. Plans track intended work and next actions; knowledge files track findings and skills track reusable procedures.

## Active plans

Read this section first during compact returning sessions when active plans exist.

Priority order for active work:

1. `lesswrong-rationalist-community-research.md`

<!-- BEGIN: lesswrong-rationalist-community-research -->
### `lesswrong-rationalist-community-research.md` · status: active · trust: medium
**Progress:** 0/11 items complete
**Next action:** Begin Phase 1/2 — write knowledge/_unverified/rationalist-community/origins/the-sequences-core-arguments.md
<!-- END: lesswrong-rationalist-community-research -->

---

## Completed plans

<!-- BEGIN: devops-docker-research -->
### `devops-docker-research.md` · status: complete · trust: medium

Docker, Vite, and DevOps tooling for the full Django + React + Celery + Redis + Postgres stack. 10 files across 9 phases: Docker Compose local dev, multi-worker Celery, nginx reverse proxy, production Docker config, GitHub Actions CI/CD, zero-downtime deploys, secrets/environment management, Celery + Prometheus monitoring, database ops, dev workflow tooling (Makefile, pre-commit, debugpy). All output in `knowledge/_unverified/devops/`.

**Progress:** 10/10 files written
**Completed:** 2026-03-19
<!-- END: devops-docker-research -->

---

<!-- BEGIN: react-stack-research -->
### `react-stack-research.md` · status: complete · trust: medium

Gaps and depth research for Alex's React + Chakra UI 3 frontend (backed by Django/DRF). 9 files across 8 phases: TanStack Query, react-hook-form + zod, TanStack Router, TypeScript patterns, Vitest/RTL/MSW testing, auth state (httpOnly cookies/CSRF/protected routes), performance (memo discipline/React 19 Compiler/TanStack Virtual), Vite build tooling, and error boundaries + Suspense. All output in `knowledge/_unverified/react/`.

**Progress:** 9/9 files written
**Completed:** 2026-03-19
<!-- END: react-stack-research -->

---

<!-- BEGIN: django-stack-research -->
### `django-stack-research.md` · status: complete · trust: medium

Django stack depth research covering Celery Canvas, worker ops, DRF/spectacular, test data factories, async Django, security (allauth, Argon2, HSTS, CSP, rate limiting), advanced migrations (zero-downtime, squashing, large tables), gunicorn/uvicorn/Docker builds, database pooling (pgBouncer, pg_stat_statements), and file storage (S3, signed URLs, direct upload). All 10 files written in `knowledge/_unverified/django/`.

**Progress:** 10/10 files written
**Completed:** 2026-03-19
<!-- END: django-stack-research -->

---

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
