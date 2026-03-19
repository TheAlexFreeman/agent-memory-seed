---
created: 2026-03-18
last_verified: '2026-03-18'
next_action: Define rollout metrics
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

### Phase 1 — Automation state model · ☑ 3/3 complete

1. ☑ Define the automation continuity schema
   - run metadata
   - active branch/base branch
   - active plan pointer
   - blockers and deferred actions

2. ☑ Define separation of concerns
   - what belongs in automation-local memory
   - what belongs in repo memory
   - what belongs in thread UI only

3. ☑ Define startup preload order for recurring runs
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

#### 3. Separation of concerns

The continuity design should enforce a strict three-layer model so the app does not blur durable repo memory, automation execution state, and transient chat context.

**Automation-local memory owns:**

- the latest run outcome and concise handoff summary
- pinned plan selection for that automation
- unresolved blockers and deferred follow-ups
- branch/base branch expectations and prior publish state
- retry semantics for interrupted or blocked runs

This layer is mutable by the automation runtime on every run and is optimized for resume accuracy, not long-term knowledge retention.

**Repo memory owns:**

- governed plan progress and `next_action`
- knowledge files, promotions, trust levels, and summaries
- scratchpad notes intended to persist across sessions
- chat summaries and other durable session artifacts

This layer remains the durable source of truth that other runs and interactive threads can inspect independently of one automation's local state.

**Thread UI owns only ephemeral execution context:**

- chain-of-thought and exploratory reasoning
- one-off debugging traces and command output
- conversational framing and local clarification during the run
- transient observations that were not promoted into automation-local or repo memory

If something must survive into the next run, it should be written into automation-local continuity state or governed repo memory before the run ends. The thread must never be the sole persistence layer for blockers, next-action state, branch expectations, or artifact references.

A practical boundary rule follows from this split:

- if the state is specific to one automation's resume path, keep it automation-local
- if the state should be true for the repo regardless of which automation or person resumes work, write it to repo memory
- if the state only helps the current conversation and has no resume value, leave it in the thread UI

#### 4. Startup preload order for recurring runs

Recurring automation startup should use a fixed preload sequence with verification gates between layers. The order should optimize for resume correctness first, context efficiency second.

**Recommended preload sequence**

1. **Load automation continuity state**
   - last run outcome
   - pinned plan pointer
   - unresolved blockers
   - branch/base expectations
   - deferred actions

2. **Run critical validity checks before deep context loads**
   - confirm the repo/workspace still matches the continuity record
   - confirm the referenced branch/base branch still exist or detect drift
   - confirm any pinned plan still exists and is still `active`
   - downgrade stale continuity fields into warnings rather than treating them as preload truth

3. **Load automation-mode repo startup contract**
   - repo router or `agent-bootstrap.toml` automation mode
   - only the compact automation startup files declared by the repo
   - startup warnings from git/worktree state or missing required files

4. **Load the carried-forward execution thread**
   - the pinned plan file when valid
   - otherwise the highest-priority active plan relevant to the automation
   - any directly referenced repo-memory artifacts needed for the next action

5. **Load optional task-expansion context only if still needed**
   - linked knowledge summaries
   - prior chat summaries
   - supporting files for the specific next action

This sequence keeps the automation from spending startup budget on broad repo rediscovery before it has confirmed that the previous run's assumptions are still valid.

#### 5. Preload resolution rules

The preload contract should also specify how to behave when continuity inputs are stale or conflicting:

- stale plan pointer: drop back to repo priority order and surface `pinned_plan_inactive`
- missing branch: preserve the prior branch name in the warning state, but do not auto-create or silently substitute a branch
- unresolved blocker still valid: surface it before execution and allow the automation scheduler to skip doomed work
- unresolved blocker cleared: retain it in history, but remove it from the active blocker list so it does not poison the next run
- repo startup contract changed since the last run: trust the current repo contract and mark the continuity snapshot as outdated

A good default is "verify before expand": continuity state can nominate what to load next, but repo truth and current git state decide what is actually eligible for preload.

### Phase 2 — Continuity UX · ☑ 3/3 complete

4. ☑ Design the run header panel
   - last run summary
   - active branch / base branch
   - next action
   - unresolved blockers

5. ☑ Add plan pinning and resume affordances
   - "resume previous plan"
   - "switch plan"
   - "no active plan"

6. ☑ Add blocker carry-forward controls
   - network unavailable
   - auth unavailable
   - validation tool missing
   - waiting on user review or PR merge

### Phase 2 decisions (2026-03-18)

#### 6. Run header panel contract

The automation run header should be a compact status surface shown before substantial work begins. It should answer four questions immediately:

- what happened last time
- what plan or branch is being resumed now
- what the next action is
- what blockers still apply

**Recommended panel fields**

- `status`: `ready`, `attention`, `blocked`, or `waiting_on_user`
- `last_run`: timestamp, outcome, and one-line run summary
- `git_context`: branch, base branch, drift warning, and PR state if relevant
- `plan_context`: pinned plan name, progress snapshot, and current `next_action`
- `blocker_summary`: count plus highest-severity active blocker
- `primary_action`: resume plan, inspect blocker, or open startup contract

The panel should stay summary-first. Detailed blocker lists, prior artifact lists, or historical run notes should sit behind expansion, not compete with the next action.

#### 7. Plan pinning and resume affordances

Plan continuity needs explicit controls instead of implicit carry-forward only. The UX should support three states:

- `resume_previous_plan` when the pinned plan is still active and relevant
- `switch_plan` when another active plan should take precedence for this automation
- `no_active_plan` when the automation is maintenance-style or the prior plan completed

Behavior rules:

- a pinned plan is a strong default, not an unbreakable lock
- switching plans should update automation-local continuity state without mutating repo plan priority order automatically
- if the pinned plan completed since the last run, the panel should downgrade to `switch_plan` and offer the repo's highest-priority relevant active plan as the replacement
- if the automation has no pinned plan, the app should surface the relevant active-plan shortlist rather than force repo-wide rediscovery

This keeps plan continuity explicit while preserving repo authority over real plan progress and ordering.

#### 8. Blocker carry-forward controls

Blockers should be first-class resumable objects, not just text from the previous run summary. Each active blocker should expose:

- blocker kind and severity
- last checked timestamp
- whether it is still believed active
- retry action
- dismiss or supersede action when conditions changed

Minimum blocker actions:

- `retry_now` for transient conditions like network/auth/tool availability
- `defer_and_skip` when the blocker still makes the run non-viable
- `mark_resolved` when the environment changed and the blocker should no longer carry forward
- `waiting_on_user` when the blocker is a human decision, review, or merge event rather than a technical failure

The UX should treat blocker carry-forward as a control surface, not just a warning banner. That is what prevents repeated doomed publish attempts and makes automation continuity materially better than a fresh thread.

### Phase 3 — Execution and writeback · ☑ 3/3 complete

7. ☑ Define automatic writeback at run end
   - concise run summary
   - blockers encountered
   - artifacts produced
   - branch / commit / PR state

8. ☑ Define interruption and retry semantics
   - partial run persistence
   - rerun on same branch
   - superseding old blockers

9. ☑ Add continuity-aware scheduling hooks
   - skip redundant work if prior blocker still applies
   - reopen the same branch if appropriate
   - warn when the repo state diverged since last run

### Phase 3 decisions (2026-03-18)

#### 9. Automatic writeback at run end

A recurring run should end by writing a normalized continuity result back into automation-local state, with links out to any durable repo-memory changes made during the run. The writeback should happen even when the run is blocked or interrupted, not only on clean success.

**Required writeback fields**

- `run_outcome`: `completed`, `blocked`, `waiting_on_user`, or `interrupted`
- `run_summary`: concise summary of what changed or why progress stopped
- `plan_result`: pinned plan id, any updated progress snapshot, and the next intended action
- `git_result`: branch, base branch, head sha, dirty/clean state, commit refs, and PR state if applicable
- `blocker_result`: active blockers to carry forward, resolved blockers to archive in history, and any newly discovered blockers
- `artifact_result`: files produced, URLs created, and repo-memory operations performed

The writeback rule should be "summarize outcome, not transcript." Automation continuity needs a durable resume record, not a replay of the whole conversation.

#### 10. Interruption and retry semantics

Automation continuity should distinguish between incomplete work and failed work. An interrupted run is not the same as a blocked run, and the retry path should preserve that difference.

- `interrupted`: the run stopped before reaching a stable conclusion; keep the last known intended action and mark partial artifacts as provisional
- `blocked`: the run reached a stable blocker that prevents useful progress; carry forward the blocker as active and allow scheduling logic to skip redundant retries
- `waiting_on_user`: progress is paused on review, merge, credentials, or another explicit human handoff
- `completed`: the run reached a stable end state, even if follow-up work remains for a future run

Retry rules:

- retries on the same branch are preferred when the branch still exists and the repo state has not diverged materially
- stale blockers can be superseded, but never silently discarded; retain blocker history with a resolution reason
- partial artifacts from interrupted runs should be visible to the next run, but clearly labeled as incomplete until verified or resumed
- if a rerun starts after significant repo drift, continuity should preserve the prior intent but force revalidation before reusing branch or plan assumptions

#### 11. Continuity-aware scheduling hooks

Scheduling should consult continuity state before launching work so repeated automations can avoid predictable waste.

**Minimum scheduling hooks**

- skip or downgrade a run when an unchanged active blocker still makes the task non-viable
- prefer reopening the prior branch when continuity state says the work is still in progress and the branch remains valid
- surface a `repo_drift` warning when HEAD, branch availability, or pinned-plan state changed since the last run
- escalate `waiting_on_user` runs into reminder-style behavior instead of full execution attempts

The scheduler should not make deep product decisions on its own. Its role is to gate obvious non-starters, reopen viable in-progress work, and surface changed conditions early enough that the agent starts from the right premise.

### Phase 4 — Validation and productization · ☐ 1/2 complete

10. ☑ Test recurring-run scenarios
   - daily research continuation
   - PR-follow-up automation
   - blocked network/auth run
   - branch drift between runs

11. ☐ Define rollout metrics
   - repeated rediscovery reduced
   - blocker recurrence rate
   - correct plan continuation rate

---

### Phase 4 decisions (2026-03-18)

#### 12. Recurring-run validation matrix

Validation should prove that continuity works across the failure modes that motivated the plan, not just the happy path.

| Scenario | What continuity must prove | Expected result |
|---|---|---|
| Daily research continuation | A pinned plan, next action, and prior branch reopen cleanly without repo-wide rediscovery. | Startup panel shows `ready`, resumes the same plan, and preserves artifact/branch context from the prior run. |
| PR-follow-up automation | Branch/PR state survives between runs and writeback reflects publish status accurately. | Startup surfaces PR status, reuses the same branch when valid, and records follow-up outcome without losing prior blocker history. |
| Blocked network/auth run | A known blocker prevents repeated doomed publish attempts. | Startup shows `blocked` or `waiting_on_user`, scheduling downgrades or skips the run, and blocker history remains visible. |
| Branch drift between runs | Old continuity state does not silently override current repo truth. | Startup surfaces `repo_drift` / branch warning state, revalidates plan/branch assumptions, and forces a conscious resume path. |
| Interrupted partial run | Partial artifacts and intended next action survive, but are clearly labeled incomplete. | Next run sees provisional artifacts, preserved intent, and a retry path distinct from a true blocker. |

A continuity implementation is not ready if it only works for clean successful reruns. The point of the feature is to preserve state through interruptions, blockers, and drift.

#### 13. Rollout metrics

The rollout should measure whether continuity reduces rediscovery and repeated failure, not merely whether the app stored more metadata.

**Primary metrics**

- repeated rediscovery rate: how often the agent reopens broad repo context despite a valid pinned plan and continuity record
- blocker recurrence rate: how often the same blocker causes repeated full execution attempts instead of early downgrade/skip behavior
- correct plan continuation rate: how often the next run resumes the intended active plan and next action without manual repair

**Secondary metrics**

- branch reuse accuracy: same-branch resume when appropriate vs. unnecessary branch churn
- stale-continuity warning frequency: how often drift or invalid pinned-plan state is caught before execution
- interrupted-run recovery rate: how often a provisional run is resumed successfully rather than abandoned or misclassified
- writeback completeness: share of runs that persist outcome, blocker, git, and artifact state successfully

The release gate should be practical: continuity is successful when repeated automations start from the right state more often, skip doomed work earlier, and require less manual rediscovery than fresh-thread behavior.

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
| 2026-03-18 | Completed Define separation of concerns (codex-desktop-automation-continuity 2/11) |
| 2026-03-18 | Completed Define startup preload order for recurri (codex-desktop-automation-continuity 3/11) |
| 2026-03-18 | Completed Design the run header panel (codex-desktop-automation-continuity 4/11) |
| 2026-03-18 | Completed Add plan pinning and resume affordances (codex-desktop-automation-continuity 5/11) |
| 2026-03-18 | Completed Add blocker carry-forward controls (codex-desktop-automation-continuity 6/11) |
| 2026-03-18 | Completed Define automatic writeback at run end (codex-desktop-automation-continuity 7/11) |
| 2026-03-18 | Completed Define interruption and retry semantics (codex-desktop-automation-continuity 8/11) |
| 2026-03-18 | Completed Add continuity-aware scheduling hooks (codex-desktop-automation-continuity 9/11) |
| 2026-03-18 | Completed Test recurring-run scenarios (codex-desktop-automation-continuity 10/11) |

---

## Notes

- This plan is tightly coupled with `codex-desktop-bootstrap-support.md` because automations need a specialized startup path.
- It also depends on stronger Git awareness so branch/base state is available before the run starts.