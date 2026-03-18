---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 1 — define the automation run-state model and memory handoff contract"
---

# Implementation Plan: Codex Desktop Automation Continuity

## Goals

Improve how Codex desktop handles recurring and background-style runs in memory-backed repos so each run starts with the correct prior state, branch context, blockers, and next action. The target outcome is first-class automation continuity rather than treating each automation run as an isolated thread with ad hoc memory notes.

---

## Problem statement

Recurring runs need continuity across time, but today too much of that state is implicit:

- prior automation memory has to be discovered manually
- the app does not surface branch/base branch expectations at the start of the run
- previous blockers like missing network access or PR failure are easy to rediscover instead of inherit
- active plan continuation depends on repo inspection instead of explicit carry-forward state

That adds avoidable work and increases the chance of resuming the wrong thread or repeating already completed steps.

---

## Desired capabilities

1. **Run-state preload**
   - last run timestamp
   - last chosen branch/base branch
   - active plan or next action
   - unresolved blockers

2. **Automation memory as first-class context**
   - dedicated place in the UI for automation notes
   - automatic surfacing before execution starts
   - clear distinction between durable repo memory and automation-local run memory

3. **Plan continuity**
   - surface active plans relevant to the automation
   - show progress and next action without requiring repo-wide rediscovery
   - support explicit pinning of a plan as the automation's current thread

4. **Outcome persistence**
   - structured writeback of what happened
   - blocked / completed / waiting-on-user states
   - branch and PR outcome recording

---

## Research and design phases

### Phase 1 — Automation state model · ☐ 0/3 complete

1. ☐ Define the automation continuity schema
   - run metadata
   - active branch/base branch
   - active plan pointer
   - blockers and deferred actions

2. ☐ Define separation of concerns
   - what belongs in automation-local memory
   - what belongs in repo memory
   - what belongs in thread UI only

3. ☐ Define startup preload order for recurring runs
   - automation memory first
   - then repo startup manifest
   - then current task-specific plan/context

### Phase 2 — Continuity UX · ☐ 0/3 complete

4. ☐ Design the run header panel
   - last run summary
   - active branch / base branch
   - next action
   - unresolved blockers

5. ☐ Add plan pinning and resume affordances
   - "resume previous plan"
   - "switch plan"
   - "no active plan"

6. ☐ Add blocker carry-forward controls
   - network unavailable
   - auth unavailable
   - validation tool missing
   - waiting on user review or PR merge

### Phase 3 — Execution and writeback · ☐ 0/3 complete

7. ☐ Define automatic writeback at run end
   - concise run summary
   - blockers encountered
   - artifacts produced
   - branch / commit / PR state

8. ☐ Define interruption and retry semantics
   - partial run persistence
   - rerun on same branch
   - superseding old blockers

9. ☐ Add continuity-aware scheduling hooks
   - skip redundant work if prior blocker still applies
   - reopen the same branch if appropriate
   - warn when the repo state diverged since last run

### Phase 4 — Validation and productization · ☐ 0/2 complete

10. ☐ Test recurring-run scenarios
   - daily research continuation
   - PR-follow-up automation
   - blocked network/auth run
   - branch drift between runs

11. ☐ Define rollout metrics
   - repeated rediscovery reduced
   - blocker recurrence rate
   - correct plan continuation rate

---

## Open questions

- Should automation memory remain a Markdown file, or should Codex also persist structured automation state outside the repo?
- How should Codex reconcile automation-local memory with repo-local plan progress when they disagree?
- Should branch/base branch continuity be mandatory for automations that touch git?
- How visible should prior blockers be in the main conversation UI?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: recurring-run continuity, branch context, and blocker carry-forward |

---

## Notes

- This plan is tightly coupled with `codex-desktop-bootstrap-support.md` because automations need a specialized startup path.
- It also depends on stronger Git awareness so branch/base state is available before the run starts.
