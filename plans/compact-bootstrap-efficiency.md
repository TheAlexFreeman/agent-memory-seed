---
created: 2026-03-19
last_verified: 2026-03-20
next_action: "Complete"
origin_session: unknown
source: agent-generated
status: complete
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: Compact Bootstrap and Context-Efficiency Optimization

## Goals

Restore the compact returning-session bootstrap to a genuinely compact operating mode, with enforcement strong enough to keep it from drifting again. The immediate target is to bring the compact startup payload back under the published ceiling while preserving enough live context for reliable session continuity. The broader goal is to reduce recurring context waste across summaries, scratchpads, routing docs, and validator logic.

---

## Problem statement

The compact bootstrap path currently violates its own contract. A focused health check measured the startup payload at roughly 11.6k tokens against a published 7k-token ceiling. The overrun is driven by four files that have gradually become hybrid documents rather than compact operational summaries:

1. `plans/SUMMARY.md` now mixes active execution state, rich completed-plan narratives, and archival detail.
2. `meta/quick-reference.md` carries both runtime-routing authority and long-form explanatory policy text.
3. `scratchpad/CURRENT.md` has accumulated deep analysis that belongs in dated scratchpads or plan files, not the startup handoff path.
4. `chats/SUMMARY.md` is functioning as a narrative history instead of a retrieval map.

The validator catches only the aggregate failure at the end. It does not localize which file drifted, what shape constraints were violated, or whether a summary is reproducing drill-down prose that should live elsewhere. As a result, the system can look valid until the budget is already badly blown.

There is also a second-order efficiency problem: even when summaries are large, the startup contract still loads full files rather than a bounded startup-safe section. That means the repo pays repeated context cost for explanatory prose whose only real purpose is later drill-down.

---

## Design principles

- Compact startup files should answer only: live state, next actions, and drill-down triggers.
- Summary files should carry state, not archives.
- Explanatory rationale should move to deeper files that are loaded on demand.
- Validation should fail or warn early at the file level, not only at the aggregate bootstrap level.
- The compact path should have headroom below the published ceiling so one or two normal edits do not immediately re-break it.

---

## Phases

### Phase 1 - Define the compact-path contract and budgets

**1.1 Define the compact bootstrap contract**
Write down the canonical purpose of each startup-loaded file: `meta/quick-reference.md`, `identity/SUMMARY.md`, `plans/SUMMARY.md`, `scratchpad/USER.md`, `scratchpad/CURRENT.md`, and conditional `chats/SUMMARY.md`. For each file, specify what content is allowed in the compact path and what must be moved behind a follow-up read.

**1.2 Set per-file token targets**
Translate the aggregate 7k-token ceiling into concrete per-file budgets with headroom. Example categories: routing authority, user identity, active plans, current handoff, and optional chat continuity. Keep a reserve budget so one file can temporarily grow without immediately failing the global test.

**1.3 Define compact-file success criteria**
For each file, define what a successful compact form must preserve. Examples: `plans/SUMMARY.md` must preserve active-plan priority and next actions; `quick-reference.md` must preserve live routing and active thresholds; `chats/SUMMARY.md` must preserve retrieval guidance and current themes.

**1.4 Decide the startup-safe section strategy**
Choose whether the system should use fully compact whole files or a two-tier format with an explicit startup-safe section at the top of richer files. If section-bound loading is adopted, define the marker convention and how tools or agents should interpret it.

---

### Phase 2 - Migrate the compact-path files

**2.1 Refactor `plans/SUMMARY.md` to active-state format**
Restructure the file so active plans are short metadata-first entries and completed plans collapse to a one-line recent-completions block or a similarly compact form. Preserve references to the underlying plan files as drill-down targets.

**2.2 Refactor `meta/quick-reference.md` to runtime authority only**
Reduce the startup-loaded quick reference to the live routing contract, current stage, active thresholds, and minimal decision triggers. Move extended rationale and runbook prose into on-demand docs such as `meta/curation-policy.md`, `meta/update-guidelines.md`, and `meta/session-checklists.md`.

**2.3 Refactor `chats/SUMMARY.md` to thematic continuity and retrieval guidance**
Replace detailed chat-by-chat narration with a compact map of persistent themes, recent continuity points, and rules for when to load dated summaries or deeper chat artifacts.

**2.4 Refactor `scratchpad/CURRENT.md` to handoff-only format**
Keep only active threads, immediate next actions, unresolved questions, and drill-down references. Move durable analysis into dated scratchpads or plan files.

**2.5 Normalize `scratchpad/USER.md` and `identity/SUMMARY.md` if needed**
Verify that `scratchpad/USER.md` remains lightweight and that `identity/SUMMARY.md` stays compact and high-signal. Only make changes if they improve startup clarity without deleting useful live context.

---

### Phase 3 - Add validator enforcement and diagnostics

**3.1 Keep the aggregate compact-budget test, but add headroom-aware messaging**
Retain the existing whole-bootstrap ceiling check, but improve the failure output so it reports the total measured payload, the configured limit, and the largest contributing files.

**3.2 Add per-file compact-budget checks**
Introduce validator warnings or failures for individual compact-path files that exceed their assigned target budgets. This should localize drift before the aggregate ceiling is broken.

**3.3 Add structural rules for compact summaries**
Teach the validator to check file-specific shape constraints. Examples: `plans/SUMMARY.md` must have an active-plans section and a compact completed-plan block; `scratchpad/CURRENT.md` must have active-thread and next-action style sections; `chats/SUMMARY.md` must have retrieval guidance.

**3.4 Add archive-vs-summary drift checks**
Warn when startup-loaded summaries reproduce long explanatory prose that belongs in drill-down files. Practical heuristics may include long completed-plan descriptions, multiple large tables in `scratchpad/CURRENT.md`, or chat-by-chat narrative expansion in `chats/SUMMARY.md`.

**3.5 Add drill-down reference checks**
Require compact summaries to point to the underlying detailed files instead of duplicating their content. This keeps summaries actionable while preserving the ability to fetch depth on demand.

---

### Phase 4 - Broader context-efficiency improvements

**4.1 Add a compact-budget inspection helper**
Create or extend tooling so developers can quickly see the measured size contribution of each compact-path file without having to rerun the full test suite and manually inspect file sizes.

**4.2 Add section-bound loading support if adopted in Phase 1**
Phase 1 explicitly chose whole-file compact startup surfaces instead of section-bound loading. No loader or manifest change is required as long as startup-loaded files remain compact entire documents.

**4.3 Review bootstrap manifest and retrieval heuristics for avoidable startup reads**
Verify that conditional loads remain conditional in practice. Examples: skip `chats/SUMMARY.md` when placeholder-only, skip `plans/SUMMARY.md` when there are no active plans, and keep `knowledge/SUMMARY.md` and `skills/SUMMARY.md` fully task-driven.

**4.4 Add context-efficiency guidance to documentation**
Document the principle that summaries are state-carrying startup files and that history, rationale, and rich explanation belong in drill-down files. This should live in the most relevant governance and contributor docs.

---

### Phase 5 - Rollout, testing, and stabilization

**5.1 Update tests for the new compact formats**
Revise validator tests and any summary-shape tests so they assert the new compact contracts rather than the current narrative-heavy forms.

**5.2 Re-measure the compact payload after migration**
After the file migrations land, rerun the compact-budget test and record the new file-by-file size breakdown. Keep enough margin that normal edits do not immediately re-break the ceiling.

**5.3 Run repo-wide validation and targeted regression checks**
Confirm that summary refactors do not break other validator expectations, routing copy, or plan consistency assumptions.

**5.4 Record the optimization in changelog and summary surfaces**
Update `CHANGELOG.md` and the relevant summary files so future maintainers understand why the compact format exists and why validator enforcement is intentionally strict.

---

## Progress tracking

- [x] 1.1 Define the compact bootstrap contract
- [x] 1.2 Set per-file token targets
- [x] 1.3 Define compact-file success criteria
- [x] 1.4 Decide the startup-safe section strategy
- [x] 2.1 Refactor `plans/SUMMARY.md` to active-state format
- [x] 2.2 Refactor `meta/quick-reference.md` to runtime authority only
- [x] 2.3 Refactor `chats/SUMMARY.md` to thematic continuity + retrieval guidance
- [x] 2.4 Refactor `scratchpad/CURRENT.md` to handoff-only format
- [x] 2.5 Normalize `scratchpad/USER.md` and `identity/SUMMARY.md` if needed
- [x] 3.1 Improve aggregate compact-budget diagnostics
- [x] 3.2 Add per-file compact-budget checks
- [x] 3.3 Add structural rules for compact summaries
- [x] 3.4 Add archive-vs-summary drift checks
- [x] 3.5 Add drill-down reference checks
- [x] 4.1 Add a compact-budget inspection helper
- [x] 4.2 Add section-bound loading support if adopted
- [x] 4.3 Review bootstrap manifest and retrieval heuristics
- [x] 4.4 Add context-efficiency guidance to documentation
- [x] 5.1 Update tests for the new compact formats
- [x] 5.2 Re-measure the compact payload after migration
- [x] 5.3 Run repo-wide validation and targeted regressions
- [x] 5.4 Record the optimization in changelog and summary surfaces

**Progress:** 22/22 items complete

**Latest measurement:** `inspect_compact_budget.py --json` reported `5705 / 7000` tokens with `1295` tokens of remaining headroom after the compact-path migration.

---

## Design constraints

- The compact bootstrap must remain operationally sufficient for returning sessions; the goal is not minimal text at any cost.
- `identity/SUMMARY.md` should stay compact, but it should not be over-compressed into losing user-specific working-style signals.
- Completed work should remain discoverable through drill-down files even if startup summaries collapse it aggressively.
- Validator enforcement should prefer localized, actionable failures over one coarse global failure.
- If section-bound loading is introduced, the marker convention must be simple enough that both humans and tools can follow it reliably.
- The compact path should target enough headroom that ordinary maintenance edits do not immediately put the repo back into a failing state.
- Documentation changes must keep the routing authority and the validator rules aligned; compactness is useful only if the operational contract remains coherent.