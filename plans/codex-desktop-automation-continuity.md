---
created: 2026-03-18
last_verified: '2026-03-18'
next_action: Define separation of concerns
origin_session: manual
source: agent-generated
status: active
trust: medium
type: implementation-plan
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

### Phase 1 — Automation state model · ☐ 1/3 complete

1. ☑ Define the automation continuity schema
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

### Phase 1 decisions (2026-03-18)

#### 1. Automation continuity schema

The automation continuity record should be a structured app-owned state object, not a Markdown note that the agent has to reinterpret each run. Markdown may still hold the human-readable run summary, but the preload contract should read from a normalized continuity record with these fields:

- `automation_id` and `workspace_id` so state is scoped to one recurring automation in one repo/workspace
- `last_run` metadata: timestamp, trigger type, outcome (`completed`, `blocked`, `waiting_on_user`, `interrupted`), and run summary
- `git_context`: `branch`, `base_branch`, `head_sha`, `dirty_state`, and a `diverged_since_last_run` flag
- `plan_context`: pinned `plan_id`, last known `next_action`, progress snapshot, and whether the plan is still active
- `blockers`: typed entries with `kind` (`network`, `auth`, `tooling`, `repo_state`, `external_dependency`, `user_input`), status, first-seen / last-seen timestamps, and retry condition
- `deferred_actions`: ordered follow-ups the previous run intentionally left for the next run
- `artifacts`: branch names, commit SHAs, PR URLs, generated files, and links to any durable repo-memory writes made during the run

The key design choice is that the continuity record stores resolved state, not raw conversation text. That keeps preload deterministic and lets the UI render the same automation state without reparsing prior threads.

#### 2. Memory handoff contract

The startup handoff between automation-local state and repo memory should be explicit and one-directional:

- automation continuity owns run-local execution state, unresolved blockers, branch/base expectations, and the currently pinned plan pointer
- repo memory remains the authority for durable knowledge, governed plan progress, scratchpad notes, and chat summaries
- thread UI holds ephemeral reasoning and conversational detail, but should not be the only place where blocker or next-action state survives

On preload, Codex should read the continuity record first, then verify any referenced durable objects instead of trusting stale pointers blindly:

1. load automation continuity state
2. validate the pinned plan still exists and is active
3. verify branch/base branch assumptions against current repo state
4. open the repo router / startup manifest for the automation mode
5. expand only the plan or files needed for the carried-forward next action

If continuity state and repo memory disagree, the app should prefer durable repo truth for plan status and current git truth for branch state, while surfacing the mismatch as an automation warning instead of silently overwriting either side.

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
| 2026-03-18 | Completed Define the automation continuity schema (codex-desktop-automation-continuity 1/11) |

---

## Notes

- This plan is tightly coupled with `codex-desktop-bootstrap-support.md` because automations need a specialized startup path.
- It also depends on stronger Git awareness so branch/base state is available before the run starts.