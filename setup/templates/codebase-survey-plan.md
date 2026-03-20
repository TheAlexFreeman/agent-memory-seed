---
created: {{TODAY}}
last_verified: {{TODAY}}
next_action: "Phase 0, item 1: identify the application entry points and boot sequence"
origin_session: setup/init-worktree.sh
source: template
status: active
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: {{PROJECT_NAME}} Codebase Survey

## Goals

Build a compact, maintainable knowledge base for {{PROJECT_NAME}} so future sessions can answer architecture, data-model, operational, and historical questions without re-reading the entire host repository.

## Scope

- map the major entry points, modules, data model, and operational commands
- capture one durable knowledge file per survey track under `knowledge/codebase/`
- attach `related` frontmatter over time so freshness checks can follow host-repo source changes

## Phases

### Phase 0 - Entry-point mapping

1. ☐ Identify the application entry points, boot sequence, and top-level package boundaries.
2. ☐ Replace the placeholder content in `knowledge/codebase/architecture.md` with the initial system map.

### Phase 1 - Module and subsystem survey

1. ☐ Trace the major modules, services, or feature areas and record their responsibilities.
2. ☐ Expand `knowledge/codebase/architecture.md` with module boundaries and cross-references.

### Phase 2 - Data model and API contracts

1. ☐ Document the core entities, persistence layers, and internal or external API boundaries.
2. ☐ Replace the placeholder content in `knowledge/codebase/data-model.md`.

### Phase 3 - Operations and delivery

1. ☐ Capture how to run, test, deploy, debug, and observe the host project.
2. ☐ Replace the placeholder content in `knowledge/codebase/operations.md`.

### Phase 4 - Design rationale and history

1. ☐ Record ADRs, important conventions, and historically relevant implementation decisions.
2. ☐ Replace the placeholder content in `knowledge/codebase/decisions.md`.

### Phase 5 - Freshness and maintenance loop

1. ☐ Add `related` frontmatter to each codebase knowledge file so freshness checks can resolve source files.
2. ☐ Update `knowledge/codebase/SUMMARY.md` with survey coverage and a re-verification cadence.

## Progress tracking

- [ ] 0.1 Identify entry points and boot sequence
- [ ] 0.2 Seed architecture note from the entry-point map
- [ ] 1.1 Survey major modules and subsystem boundaries
- [ ] 1.2 Expand architecture note with module cross-references
- [ ] 2.1 Capture entities, persistence, and API boundaries
- [ ] 2.2 Write the data-model note
- [ ] 3.1 Capture local run, test, deploy, and debug flows
- [ ] 3.2 Write the operations note
- [ ] 4.1 Capture ADRs and design rationale
- [ ] 4.2 Write the decisions note
- [ ] 5.1 Add `related` frontmatter for freshness checks
- [ ] 5.2 Update the codebase summary with maintenance guidance

**Progress:** 0/12 items complete

## Notes for the first pass

- Prefer compact, verified notes over exhaustive prose.
- When uncertain, keep the file at `trust: low` and record the uncertainty explicitly.
- Link back to concrete source paths in `related` once the corresponding note is grounded.