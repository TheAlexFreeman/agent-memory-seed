---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 1 — define preflight checks for GitHub auth, network reachability, and local tooling availability"
---

# Implementation Plan: Codex Desktop GitHub and Network Ergonomics

## Goals

Improve Codex desktop's handling of GitHub operations, network availability, and local tool readiness so the app can detect environment blockers before late-stage actions like push, PR creation, package install, or validation. The target outcome is earlier detection, better recovery paths, and less wasted work at the end of a task.

---

## Problem statement

Network and GitHub failures often appear only at the end of a task:

- `gh` may be installed but unusable because config or auth is inaccessible
- direct git push may fail due network restrictions
- required local tooling like Python or Node may be absent
- the app often discovers these issues after work is already complete

That is especially painful for automations and memory-system maintenance where validation and PR creation are expected closing steps.

---

## Desired capabilities

1. **Preflight environment checks**
   - GitHub CLI availability and config access
   - Git remote reachability
   - outbound network status
   - required local runtime/tool availability

2. **Task-aware readiness detection**
   - if the task likely needs GitHub, check GitHub early
   - if the task likely needs Python, check Python early
   - if the task likely needs package installs, check network and package managers early

3. **Clear blocker reporting**
   - what failed
   - when it was checked
   - whether the blocker is auth, config, runtime, or connectivity
   - what fallback paths remain possible

4. **Recovery ergonomics**
   - retry after login/network restoration
   - partial completion states
   - clearer guidance for "work completed locally, publish later"

---

## Research and design phases

### Phase 1 — Preflight model · ☐ 0/3 complete

1. ☐ Define the environment check suite
   - GitHub auth/config
   - git remote reachability
   - network access
   - language runtime availability
   - package manager availability

2. ☐ Define task-to-check mapping
   - PR task → GitHub + push reachability
   - validation task → required runtime
   - dependency-install task → network + package manager

3. ☐ Define caching and freshness rules
   - how long a check result remains trusted
   - when the app should recheck automatically
   - when the agent can request a refresh

### Phase 2 — UX and error handling · ☐ 0/3 complete

4. ☐ Design the preflight status panel
   - pass/fail state
   - exact blocker
   - checked-at timestamp
   - retry action

5. ☐ Add progressive disclosure for blockers
   - lightweight when all green
   - detailed only when blocked
   - avoid overwhelming casual tasks with irrelevant diagnostics

6. ☐ Standardize fallback messaging
   - "local work complete, publish blocked"
   - "validation skipped because runtime missing"
   - "GitHub CLI unavailable, direct git still possible"

### Phase 3 — Integration with task execution · ☐ 0/3 complete

7. ☐ Trigger task-aware preflight early
   - before substantial work starts
   - again before final publish/PR actions
   - surface changes since the first check

8. ☐ Integrate with automation runs
   - carry forward prior blockers
   - skip doomed publish attempts when the blocker is unchanged
   - notify when the environment became healthy again

9. ☐ Add tool-specific adapters
   - `gh`
   - git HTTPS/SSH remotes
   - Python / Node / package managers
   - repo validator / test runner prerequisites

### Phase 4 — Hardening and rollout · ☐ 0/2 complete

10. ☐ Build environment simulation tests
   - no network
   - no runtime
   - locked `gh` config
   - reachable remote but unauthenticated push

11. ☐ Define success metrics
   - reduced late-stage publish failures
   - reduced "tool missing" discovery after edits
   - faster user understanding of what remains blocked

---

## Open questions

- How aggressive should the app be about running preflight checks automatically?
- Should GitHub/network health be global app state or workspace-specific state?
- How should Codex distinguish transient failures from policy restrictions in sandboxes?
- Should the app offer task templates that declare required tooling explicitly?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: late discovery of GitHub, network, and runtime blockers |

---

## Notes

- This plan complements `codex-desktop-automation-continuity.md` because blocked publish steps need to carry forward cleanly between runs.
- The core principle is earlier failure detection with precise blocker classification, not just more diagnostics.
