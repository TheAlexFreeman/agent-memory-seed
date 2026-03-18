---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 1 — define the compact startup manifest contract and repo-declared bootstrap surface"
---

# Implementation Plan: Codex Desktop Bootstrap Support

## Goals

Improve Codex desktop's ability to enter a memory-backed repository in the right state automatically instead of depending on manual bootstrap discipline every session. The target outcome is a repo-declared startup manifest that lets Codex load the compact returning-session context, detect first-run vs. returning-session flows, and surface the right files before work begins.

This plan is about app support, not changes to this repo's memory contents. The deliverable is a concrete product and implementation roadmap for Codex desktop.

---

## Problem statement

Today, memory-system effectiveness depends on the agent correctly discovering and following bootstrap instructions in repo files such as `README.md`, `meta/quick-reference.md`, and folder summaries. That works, but it is fragile:

- the app does not know which files are canonical startup context
- detached worktrees and branch drift are invisible until the agent checks manually
- compact returning-session startup and full bootstrap are repo conventions, not first-class app concepts
- the agent has to spend context budget rediscovering structure the app could have loaded directly

The app should understand a repo's preferred startup route and preload the right context.

---

## Desired capabilities

1. **Repo-declared startup manifest**
   - file or metadata block declaring canonical startup files
   - different manifests for first run, returning session, periodic review, and automation runs
   - explicit precedence over ad hoc agent heuristics

2. **Bootstrap mode detection**
   - detect first run vs. returning session
   - detect automation run vs. interactive thread
   - detect detached HEAD vs. branch-bound worktree before work starts

3. **Context-budget-aware loading**
   - load compact startup set by default
   - allow the repo to declare "read only on first exposure" files
   - show the agent what was preloaded so retrieval remains auditable

4. **UI surfacing**
   - startup panel showing which repo files were loaded and why
   - one-click open for canonical startup files
   - explicit handoff from preload state into active task execution

---

## Research and design phases

### Phase 1 — Startup manifest contract · ☐ 0/3 complete

1. ☐ Define a repo-level manifest format
   - candidate locations: root file, frontmatter block, or app-side config
   - support named modes: `first_run`, `returning`, `automation`, `periodic_review`
   - support ordered file lists, optional files, and "heavy docs" annotations

2. ☐ Define fallback behavior when the manifest is missing or incomplete
   - safe defaults for generic repos
   - memory-repo-specific detection heuristics for known structures
   - conflict handling when the manifest disagrees with repo docs

3. ☐ Define compatibility with existing memory repos
   - zero-break migration path for repos that currently encode bootstrap only in Markdown
   - how to treat platform adapter files like `AGENTS.md`, `.cursorrules`, and `CLAUDE.md`

### Phase 2 — Startup runtime and detection logic · ☐ 0/3 complete

4. ☐ Implement startup mode detection
   - first-run vs. returning-session checks
   - branch/worktree state checks
   - automation run detection from thread metadata

5. ☐ Implement deterministic preload ordering
   - preserve repo-declared order
   - deduplicate equivalent files
   - mark skipped files and the reason they were skipped

6. ☐ Add compact-context budgeting rules
   - max file count / token budget hints
   - explicit "load summaries before transcripts" behavior
   - preserve an access trail for preloaded files

### Phase 3 — Desktop UX · ☐ 0/3 complete

7. ☐ Design the startup panel
   - files loaded
   - mode selected
   - repo-declared next step

8. ☐ Add branch/worktree warnings to startup
   - detached HEAD
   - worktree not aligned with requested branch
   - branch already checked out in another worktree

9. ☐ Add manual override controls
   - "load full bootstrap"
   - "load compact startup only"
   - "skip repo manifest for this thread"

### Phase 4 — Validation and rollout · ☐ 0/2 complete

10. ☐ Define test matrix
   - fresh clone
   - mature memory repo
   - detached automation worktree
   - malformed manifest

11. ☐ Draft rollout strategy
   - behind feature flag first
   - support repo opt-in before default-on
   - telemetry on preload usefulness and skipped-file rates

---

## Open questions

- Should the startup manifest live in the repo or in Codex app metadata, or both?
- Should preloaded files automatically count as retrievals for memory systems that track access?
- How much startup state should be visible to the user vs. kept agent-facing only?
- Should Codex support multiple named manifests per repo, or one manifest plus conditions?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: memory-aware repo startup and bootstrap loading |

---

## Notes

- This plan pairs closely with `codex-desktop-automation-continuity.md` because automations need a specialized startup mode.
- The most important constraint is preserving repo authority: the app should amplify the repo's bootstrap contract, not silently replace it.
