# Plans — Summary

This folder holds structured research plans and investigation roadmaps. Plans are agent-generated, retrievable memory documents that describe what we intend to investigate and how. They are distinct from knowledge files, which record what we have found, and skills, which record reusable procedures.

## Active plans

Read this section first during compact returning sessions when active plans exist.

Priority order for active work:

1. `codex-desktop-bootstrap-support.md`
2. `codex-desktop-governed-memory-writes.md`
3. `codex-desktop-automation-continuity.md`
4. `codex-desktop-github-network-ergonomics.md`
5. `agent-memory-mcp.md`
6. `django-stack-research.md`
7. `react-stack-research.md`
8. `devops-docker-research.md`
9. `philosophy-history-survey.md`

---

<!-- BEGIN: codex-desktop-bootstrap-support -->
### `codex-desktop-bootstrap-support.md` · status: active · trust: medium

Implementation plan for memory-aware repo startup in Codex desktop. Focus: repo-declared startup manifests, first-run vs. returning-session detection, compact preload ordering, and startup UI for branch/worktree/bootstrap state.

**Progress:** 0/11 tasks complete
**Next action:** Phase 1 — define the compact startup manifest contract and repo-declared bootstrap surface
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

---

<!-- BEGIN: agent-memory-mcp -->
### `agent-memory-mcp.md` · status: active · trust: medium

Implementation plan for an enhanced agent-memory MCP with read/write and read/write/commit tooling. Two-tier architecture: Tier 1 semantic tools (auto-commit, own all invariants per operation) + Tier 2 low-level tools (staged writes + explicit `memory_commit`). Version tokens for optimistic locking. 17 tools total across 4 build phases. Stack: FastMCP (Python), subprocess git, python-frontmatter.

**Progress:** 0/17 tools built (Phase 0: 0/3)
**Next action:** Phase 0 — implement git integration layer and version token model
<!-- END: agent-memory-mcp -->

---

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

## Completed plans

_None yet._

---

## What belongs here

- Multi-session research projects with a defined scope, phase structure, and output targets
- Investigation roadmaps where the agent needs to track progress across sessions
- Any plan where execution state (what's done, what's next) needs to persist

## What doesn't belong here

- One-off task notes → use `scratchpad/CURRENT.md`
- Completed plans that no longer matter → archive within this folder or delete
- Governance and system meta → use `meta/`

## Frontmatter conventions

Plans use the standard content frontmatter (`source`, `origin_session`, `created`, optional `last_verified`, `trust`) with `source: agent-generated` for agent-authored plans, plus these plan-specific fields:

```yaml
type: research-plan        # distinguishes plans from knowledge content
status: active             # active | paused | complete
next_action: "..."         # one-line description of where to pick up
```

For plans, `last_verified` means the plan state was reviewed or advanced in-session; it is a freshness marker, not a claim that every statement in the file has been fact-checked. Trust decay rules from `meta/quick-reference.md` still apply normally: `trust: medium` plans are flagged for review after 180 days without a `last_verified` update.

## ACCESS logging

`plans/ACCESS.jsonl` tracks retrievals of specific plan files the same way other memory folders do. Log reads of `plans/*.md` when a plan materially informed the session. Do not log reads of this `SUMMARY.md`.

## Change control

- Routine progress updates are automatic: `status`, `next_action`, progress text, `last_verified`, and `SUMMARY.md` coverage refreshes.
- Creating a new plan, archiving or retiring a plan, or materially changing a plan's scope should be surfaced to the user under the normal proposed-change flow.
