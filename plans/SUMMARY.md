# Plans — Summary

This folder holds multi-session research and implementation plans. Plans track intended work and next actions; knowledge files track findings and skills track reusable procedures.

## Active plans

Read this section first during compact returning sessions when active plans exist.

**Priority after MCP completion:** `django-stack-research` → `react-stack-research` → `devops-docker-research` → `philosophy-history-survey`

<!-- BEGIN: philosophy-history-survey -->
### `philosophy-history-survey.md` · status: active · trust: medium

Broad survey of the history of philosophy — the overarching story of how ideas developed, what mattered in different times and places, how schools influenced one another. 26 output files planned across 7 phases + 4 synthesis files. Output goes to `knowledge/_unverified/philosophy/history/`.

**Progress:** 0/26 files written (0/4 synthesis files)
**Next action:** Begin Phase 1 — write `knowledge/_unverified/philosophy/history/ancient/pre-socratics.md`
<!-- END: philosophy-history-survey -->

---

<!-- BEGIN: django-stack-research -->
### `django-stack-research.md` · status: active · trust: medium

Gaps and depth research for Alex's Django + Celery + Postgres + Redis + Docker stack. 10 files planned across 7 phases. Priority order: Celery Canvas in depth → Celery worker/beat ops → drf-spectacular → Django test data/factories → Django async → Django security → Django migrations advanced → gunicorn/uvicorn deployment → database connection pooling → django-storages. Output goes to `knowledge/_unverified/django/`.

**Progress:** 1/10 files written
**Next action:** Continue Phase 1 — write `knowledge/_unverified/django/celery-worker-beat-ops.md`
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
