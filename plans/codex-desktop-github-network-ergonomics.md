---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: complete
next_action: null
---

# Implementation Plan: Codex Desktop GitHub and Network Ergonomics

## Goals

Improve Codex desktop's handling of GitHub operations, network availability, and local tool readiness so the app can detect environment blockers before late-stage actions like push, PR creation, package install, or validation. The target outcome is earlier detection, clearer recovery paths, and less wasted work at the end of a task.

This plan is about app-facing readiness support, not generic diagnostics. The deliverable is a repo-declared preflight contract plus an executable prototype that classifies common publish/install/validation blockers.

---

## Problem statement

Network and GitHub failures often appear only at the end of a task:

- `gh` may be installed but unusable because config or auth is inaccessible
- direct `git push` may fail due auth, policy, or network restrictions
- required local tooling like Python or Node may be absent
- package-manager network failures often appear only when install commands are attempted

That is especially painful for automations and memory-system maintenance where validation and publish steps are expected close-out behavior.

---

## Desired capabilities

1. **Preflight environment checks**
   - GitHub CLI availability and config access
   - git remote reachability
   - outbound network status
   - required local runtime/tool availability

2. **Task-aware readiness detection**
   - if the task likely needs GitHub, check GitHub early
   - if the task likely needs Python, check Python early
   - if the task likely needs package installs, check network and package managers early

3. **Clear blocker reporting**
   - what failed
   - when it was checked
   - whether the blocker is auth, config, runtime, repo state, policy, or connectivity
   - what fallback paths remain possible

4. **Recovery ergonomics**
   - retry after login/network restoration
   - partial completion states
   - clearer guidance for "work completed locally, publish later"

---

## Research and design phases

### Phase 1 — Preflight model · ☑ 3/3 complete

1. ☑ Define the environment check suite
   - repo-side prototype now declares `git_cli`, `git_remote`, `git_push_dry_run`, `gh_auth`, `remote_network`, `python_runtime`, `python_validation_stack`, `python_package_manager`, `python_package_network`, `node_runtime`, `node_validation_stack`, `node_package_manager`, and `node_package_network`

2. ☑ Define task-to-check mapping
   - `pull_request` and `publish_branch` profiles gate GitHub publish work
   - `python_validation` / `node_validation` gate local validation
   - `python_dependency_install` / `node_dependency_install` gate package-manager plus outbound package-network access

3. ☑ Define caching and freshness rules
   - manifest-backed cache policy now records `result_ttl_sec = 300`, `retry_failure_ttl_sec = 60`, `recheck_on_manual_retry = true`, `recheck_on_final_gate = true`, and `agent_refresh_allowed = true`

### Phase 1 decisions (2026-03-18)

#### 1. Readiness should be repo-declared and task-aware

The readiness contract should live in a repo-owned manifest, `HUMANS/tooling/agent-task-readiness.toml`, so Codex desktop can discover the expected preflight behavior without reconstructing it from prose. The contract now declares:

- task profiles with keyword-based inference and explicit final-gate checks
- cache and freshness rules for probe reuse
- automation blocker carry-forward behavior
- UI labels and per-profile fallback messages
- per-check retry actions, fallback paths, and failure-mode taxonomies

#### 2. Profile selection should stay narrow

The first prototype uses seven profiles:

- `workspace_general`
- `pull_request`
- `publish_branch`
- `python_validation`
- `python_dependency_install`
- `node_validation`
- `node_dependency_install`

This keeps the preflight surface understandable while still covering the main late-stage failure classes the plan targeted.

#### 3. Blockers need stable classifications, not raw stderr only

The prototype classifies failures into stable buckets: `missing`, `missing_remote`, `auth`, `config`, `connectivity`, `runtime`, `policy`, `repo_state`, and `unknown`. That lets the app surface better recovery guidance and track repeated blockers across runs.

### Phase 2 — UX and error handling · ☑ 3/3 complete

4. ☑ Design the preflight status panel
   - resolver now emits `ui_feedback` with panel title, status, status label, checked-at timestamp, blocker summary, check list, and a manifest action

5. ☑ Add progressive disclosure for blockers
   - the manifest now records `details_when_blocked_only = true` and `green_summary_only = true`, so healthy states stay compact and blocked states can expand into exact check results

6. ☑ Standardize fallback messaging
   - each profile now declares specific fallback copy such as "Local work complete, publish blocked" or "Validation skipped because the Python runtime or validation tools are missing"

### Phase 2 decisions (2026-03-18)

#### 4. UI feedback should be emitted by the resolver, not rebuilt later

`HUMANS/tooling/scripts/resolve_task_readiness.py` now returns a structured `ui_feedback` object that carries:

- a stable panel title and status label
- the selected profile and how it was chosen
- a checked-at timestamp
- blocker counts and a primary blocker summary
- a manifest action pointing back to the readiness contract
- summarized check rows suitable for direct rendering

#### 5. Recovery messaging should be profile-specific

The app does not need one global error string. Publish tasks, validation tasks, and dependency-install tasks fail for different reasons and have different viable fallback paths. The manifest now stores that distinction explicitly.

#### 6. Config failures deserve their own bucket

The ergonomics problem was not only "not logged in." Locked or unreadable `gh` config is materially different from missing auth, and the resolver now classifies those cases as `config` so the app can explain them precisely instead of folding them into generic login failures.

### Phase 3 — Integration with task execution · ☑ 3/3 complete

7. ☑ Trigger task-aware preflight early
   - resolver now infers the task profile from task text plus repo hints before heavy work starts and records `final_gate_checks` for publish/install rechecks

8. ☑ Integrate with automation runs
   - manifest now declares `carry_forward_blockers = true`, `skip_unchanged_publish_attempts = true`, and `notify_when_restored = true`; resolver compares current blockers with `previous_blockers`

9. ☑ Add tool-specific adapters
   - the prototype now adapts `git`, `gh`, remote host network probes, Python runtime/package-manager probes, and Node runtime/package-manager probes

### Phase 3 decisions (2026-03-18)

#### 7. Repo hints should supplement task text

The resolver does not rely on task text alone. It also inspects repo hints such as:

- whether `.github/workflows/ci.yml` references `pytest` or `ruff`
- whether the repo looks Python- or Node-backed
- the current branch and `origin` remote URL
- the remote host implied by the remote URL

That keeps profile inference useful even when the task phrasing is short or ambiguous.

#### 8. Carry-forward blockers should be compared structurally

Automation continuity works better when blockers are compared by `(check_id, classification)` instead of by raw message text. The resolver now marks unchanged blockers, surfaces resolved prior blockers, and exposes `skip_unchanged_publish_attempts_now` for publish profiles.

#### 9. Final-gate checks should be narrower than full startup probes

The manifest now separates `checks` from `final_gate_checks`. A publish task can run the full preflight early, then recheck only the publish-critical subset before the final push/PR step.

### Phase 4 — Hardening and rollout · ☑ 2/2 complete

10. ☑ Build environment simulation tests
   - `HUMANS/tooling/tests/test_task_readiness.py` now covers healthy PR readiness, missing `gh`, locked `gh` config, missing Python runtime, unauthenticated push, unchanged blocker carry-forward, and restored-blocker attention

11. ☑ Define success metrics
   - the prototype now makes the key rollout signals observable: blocker classification, carried-forward blocker reuse, restored blocker detection, and task/profile inference

### Phase 4 decisions (2026-03-18)

#### 10. The test matrix should model blocker classes directly

The readiness test suite uses injected command and network runners so the resolver can be hardened against the exact failure classes the plan called out:

- `gh` missing
- `gh` config unreadable
- push reachable but unauthenticated
- Python runtime absent
- repeated publish blockers across runs
- previously blocked environments becoming healthy again

This keeps the prototype deterministic and independent of the current machine state.

#### 11. Rollout value is about earlier failure detection

The useful success signals are:

- fewer publish attempts that rediscover unchanged blockers at the end
- clearer classification of auth vs. config vs. connectivity failures
- faster understanding of when local work can still continue despite a blocked publish/install step
- less wasted work in automation runs when prior blockers still apply

The manifest-plus-resolver prototype now makes those signals inspectable instead of implicit.

---

## Open questions

- How aggressively should the app run preflight checks automatically on lightweight tasks?
- Should GitHub/network health be global app state or workspace-specific state?
- Should future profiles include language- or ecosystem-specific package registries beyond PyPI and npm?
- How should Codex distinguish transient network failures from durable sandbox or policy restrictions?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: late discovery of GitHub, network, and runtime blockers |
| 2026-03-18 | Added `HUMANS/tooling/agent-task-readiness.toml` to define task-aware profiles, cache policy, automation blocker carry-forward, UI labels, and per-check fallback behavior |
| 2026-03-18 | Added `HUMANS/tooling/scripts/resolve_task_readiness.py` to validate the manifest, infer readiness profiles, run GitHub/network/runtime/package-manager probes, classify blockers, and emit structured UI feedback |
| 2026-03-18 | Added `HUMANS/tooling/tests/test_task_readiness.py` covering healthy publish readiness, missing `gh`, locked `gh` config, missing Python runtime, unauthenticated push, unchanged blockers, and restored blockers |
| 2026-03-18 | Extended `HUMANS/tooling/scripts/validate_memory_repo.py` and `HUMANS/tooling/tests/test_validate_memory_repo.py` so task-readiness manifests become part of the repo contract and the minimal seed fixture includes the current MCP guidance |
| 2026-03-18 | Updated `README.md`, `setup/initial-commit-paths.txt`, `CHANGELOG.md`, and `plans/SUMMARY.md` so the readiness contract is documented and preserved in the canonical seed commit; completed the GitHub/network ergonomics plan (11/11) |

---

## Notes

- This plan complements `codex-desktop-bootstrap-support.md` because startup routing and task readiness are adjacent desktop concerns.
- It also complements `codex-desktop-automation-continuity.md` because blocker carry-forward is only useful when the blocker types are stable and task-aware.
