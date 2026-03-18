---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 2 — implement startup mode detection and deterministic preload ordering"
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

### Phase 1 — Startup manifest contract · ☑ 3/3 complete

1. ☑ Define a repo-level manifest format
   - decision: use a repo-owned root file, `agent-bootstrap.toml`; Codex may cache derived state app-side, but the repo file is the preload authority
   - support named modes: `first_run`, `returning`, `automation`, `periodic_review`
   - each step records `path`, `role`, `required`, `skip_if`, and `cost` so preload order is explicit and context-aware

2. ☑ Define fallback behavior when the manifest is missing or incomplete
   - safe defaults for generic repos: `AGENTS.md` if present, otherwise `README.md`, then task-driven retrieval
   - memory-repo heuristic: if `meta/quick-reference.md` plus `identity/`, `plans/`, `knowledge/`, and `chats/` exist, treat that file as the router and infer compact-returning preload behavior
   - conflict rule: the manifest controls preload order, but Codex surfaces disagreements with repo docs as a startup warning instead of silently guessing

3. ☑ Define compatibility with existing memory repos
   - zero-break migration: repos without `agent-bootstrap.toml` continue to rely on Markdown routing until they opt in
   - adapter-file rule: `AGENTS.md`, `.cursorrules`, and `CLAUDE.md` are treated as platform shims that may point to the router or add platform-specific constraints, but they should not become competing startup authorities

### Phase 1 decisions (2026-03-18)

#### 1. Bootstrap surface

The bootstrap contract should be repo-declared and layered:

- **Router**: one canonical Markdown file that chooses the session route (`meta/quick-reference.md` in this repo shape)
- **Manifest**: one machine-readable file that tells Codex what to preload for each mode
- **Adapter shims**: platform-specific files like `AGENTS.md`, `.cursorrules`, and `CLAUDE.md` that point agents toward the router/manifest without redefining the startup graph

This keeps repo authority centralized while still letting different agent platforms expose their own instruction surfaces.

#### 2. Manifest shape

Use a root `agent-bootstrap.toml` with named modes and ordered steps. Minimal draft:

```toml
version = 1
router = "meta/quick-reference.md"
default_mode = "returning"

adapter_files = ["AGENTS.md", "CLAUDE.md", ".cursorrules"]

[[modes.returning.steps]]
path = "meta/quick-reference.md"
role = "router"
required = true
cost = "light"

[[modes.returning.steps]]
path = "identity/SUMMARY.md"
role = "identity-summary"
required = true
cost = "light"

[[modes.returning.steps]]
path = "chats/SUMMARY.md"
role = "chat-summary"
required = false
skip_if = "placeholder_or_empty"
cost = "light"

[[modes.returning.steps]]
path = "plans/SUMMARY.md"
role = "plan-summary"
required = false
skip_if = "no_active_plans"
cost = "light"

[[modes.returning.steps]]
path = "scratchpad/USER.md"
role = "scratchpad-user"
required = false
skip_if = "placeholder_or_empty"
cost = "light"

[[modes.returning.steps]]
path = "scratchpad/CURRENT.md"
role = "scratchpad-current"
required = false
skip_if = "placeholder_or_empty"
cost = "light"
```

Deliberately keep the first version small. The manifest should declare preload order and skip rules, not become a second policy engine.

#### 3. Fallback model

When no manifest exists, Codex should fall back in this order:

1. Read `AGENTS.md` if present and follow any startup pointer it contains.
2. Otherwise read `README.md`.
3. If the repo matches the memory-repo shape (`meta/quick-reference.md`, folder summaries, `ACCESS.jsonl` files), infer the compact returning flow instead of doing an indiscriminate bootstrap.
4. If the shape is unknown, stay generic: load the lightest authority file available, then shift to task-driven retrieval.

When the manifest is present but incomplete, Codex should trust the declared steps first, then fill missing pieces with the same heuristics and label those additions as inferred.

#### 4. Compatibility and precedence

- The manifest is opt-in. Existing repos remain functional without it.
- Codex should offer migration help by previewing an inferred manifest, but must not write one automatically.
- Platform adapters remain valid, but the manifest is the only preload contract Codex treats as authoritative.
- If Markdown instructions disagree with the manifest, Codex should preserve audibility by warning and showing both sources rather than silently picking one.

This preserves consistency and keeps preload behavior reviewable in git.

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

- Should preloaded files automatically count as retrievals for memory systems that track access?
- How much startup state should be visible to the user vs. kept agent-facing only?
- Should task-classified on-demand context (for example `knowledge/SUMMARY.md`) remain heuristic, or should manifests be allowed to declare conditional task expansions too?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: memory-aware repo startup and bootstrap loading |
| 2026-03-18 | Completed Phase 1 contract definition: chose a repo-owned `agent-bootstrap.toml`, defined fallback and conflict rules, and formalized adapter-file precedence |

---

## Notes

- This plan pairs closely with `codex-desktop-automation-continuity.md` because automations need a specialized startup mode.
- The most important constraint is preserving repo authority: the app should amplify the repo's bootstrap contract, not silently replace it.
