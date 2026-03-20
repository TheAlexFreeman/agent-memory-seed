---
created: 2026-03-19
last_verified: 2026-03-20
next_action: "Phase 3, item 13 — write CI/CD exemption guidance in HUMANS/docs/INTEGRATIONS.md"
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: implementation-plan
category: build
---

# Roadmap: Orphan-Branch Worktree Integration

Enable `agent-memory-seed` to drop into an existing project as a git orphan branch
checked out as a worktree, so a codebase-specific memory store can live alongside the
project without polluting its history, CI, or tooling.

## Problem statement

The repo is currently designed as a standalone project: `setup.sh` assumes it _is_ the
repo root, `CLAUDE.md`/`AGENTS.md` adapter files live in its root, the MCP server path
is hardcoded relative to the memory repo, and the bootstrap resolver knows of no "host"
codebase. Dropping this into an existing project requires too many manual steps that
aren't obvious, aren't tested, and will silently break if the host changes shape.

The goal is a single command — `memory-init` or `bash setup/init-worktree.sh` — that a
developer runs once from an existing project root, after which the memory store is live,
the MCP server is configured, and agents can start working immediately. The
systems-architecture research adds one important design constraint: the first-cut
worktree topology should assume a single governed writer per memory worktree, with
provenance anchored to host-repo commits rather than CRDT-style concurrent editing of
protected Markdown files.

## Scope

- Add a worktree-specific init script and setup flow.
- Extend the MCP server to understand the host/memory topology.
- Add a `memory_git_log` host-repo mode so agents can detect knowledge staleness.
- Provide CI/CD, gitignore, and tooling hygiene templates.
- Add a codebase-survey skeleton so agents have a ready-made starting point.
- Extend the validator and test suite to cover the worktree configuration.

## What is explicitly out of scope

- Multi-agent concurrent write support.
- Automatic migration of existing standalone memory repos to worktree mode.
- GUI/browser setup for worktree init (keep it shell-first for now).

---

## Phase 0: Worktree init script

Goal: one command turns any git repo into a host with a live memory worktree.

### Items

1. ☑ Write `setup/init-worktree.sh`

   The script should, in order:
   - Verify it is run from a git repo root (fail loudly otherwise).
   - Accept `--worktree-path` (default `.agent-memory`), `--branch-name` (default
     `agent-memory`), `--profile`, and `--platform` flags matching `setup.sh`.
   - Create the orphan branch (`git checkout --orphan <branch-name>`).
   - Seed it from the template: copy the minimal file set (see item 2 below), make the
     initial commit on the orphan branch, then return to the original branch.
   - Add the worktree: `git worktree add <worktree-path> <branch-name>`.
   - Run the personalization flow (profile template → identity/profile.md, with a new
     `codebase_root` trait pointing at the host repo root).
   - Write the MCP config (see Phase 1) and print a "next steps" summary.

2. ☑ Define the minimal worktree seed file set

   The orphan branch should contain only what is needed for the memory store — not the
   tooling, not the setup scripts, not the CI/CD that belongs to the standalone seed:

   **Include:**
   - `identity/`, `knowledge/`, `plans/`, `skills/`, `scratchpad/`, `chats/` (with
     their `SUMMARY.md` and `ACCESS.jsonl` stubs)
   - `meta/` (all governance docs)
   - `engram_mcp/agent_memory_mcp/` (the MCP server package)
   - `engram_mcp/memory_mcp.py` (the path-based entrypoint; prefer `engram-mcp` when installed)
   - `agent-bootstrap.toml`
   - `pyproject.toml` (server extras only)
   - `.gitattributes`

   **Exclude from the orphan branch:**
   - `setup/` (standalone init tooling; not needed in the memory branch)
   - `HUMANS/docs/`, `HUMANS/tooling/tests/`, `HUMANS/tooling/scripts/validate_*`
     (human-facing docs and validation tooling live in the seed repo, not in every
     deployed memory branch)
   - `.github/` (host project owns CI)
   - `setup.html`, `setup.sh` (not relevant in worktree mode)
   - `CHANGELOG.md` (memory branch has its own git log)

   Capture this as `setup/init-worktree-paths.txt` alongside the existing
   `setup/initial-commit-paths.txt`.

3. ☑ Add `--dry-run` flag to `init-worktree.sh`

   Print every git command that would be run without executing any of them. Lets users
   inspect what will happen before committing.

4. ☑ Write tests for `init-worktree.sh` in `test_setup_flows.py`

   Cover: orphan branch exists and has no shared history with main; worktree is
   checked out at the expected path; identity/profile.md contains codebase_root; MCP
   config path points at the worktree; `--dry-run` prints commands and exits cleanly.

---

## Phase 1: MCP config and adapter file placement

Goal: the MCP server and agent adapter files (CLAUDE.md, AGENTS.md, .cursorrules)
work correctly when the memory store is a worktree inside a larger project.

### Items

5. ☑ Extend `setup/init-worktree.sh` to write adapter files to the host root

   In standalone mode, `CLAUDE.md`/`AGENTS.md`/`.cursorrules` live in the memory repo
   root — they _are_ the project root. In worktree mode, agents run from the host
   project root and need those files there. The init script should write trimmed
   adapter files to the host root that:
   - Reference the worktree path for MCP config.
   - Include the quick-reference routing language so agents know where the memory
     store is.
   - Note that the memory branch is at `<branch-name>` and the worktree is at
     `<worktree-path>`.

   The host-root adapter files should be distinct from the adapter files living
   inside the worktree (which remain for when agents access the memory branch
   directly).

6. ☑ Extend `setup/init-worktree.sh` to write platform-specific MCP config

   For each supported platform (Codex, Claude Cowork, generic):
   - Write the MCP server config pointing at `<worktree-path>/engram_mcp/memory_mcp.py`
     and `repo_root = <worktree-path>`. When the package is installed inside the
     worktree, prefer the `engram-mcp` CLI.
   - On Codex platform: write `.codex/config.toml` in the host root, not in the
     worktree.
   - For other platforms: write an `mcp-config-example.json` referencing the worktree
     path, with a clear comment that the user must paste this into their client config.

7. ☑ Add `host_repo_root` field to `agent-bootstrap.toml`

   A new optional field that tells the bootstrap resolver where the host codebase
   lives. When set, the bootstrap can surface the host repo's git status (branch,
   recent commits) alongside the memory store status at session start. In standalone
   mode this field is absent and behaviour is unchanged.

8. ☑ Update `meta/quick-reference.md` routing rules for worktree topology

   Add a routing rule: if the agent detects it is operating from a host project root
   (not the memory repo root directly), the MCP server path and memory store path
   differ from the project root. The agent should use `host_repo_root` from
   `agent-bootstrap.toml` for codebase git operations and the worktree path for all
   memory operations.

---

## Phase 2: Host-repo git access for freshness detection

Goal: agents can read the host codebase's git log from within the memory session,
enabling knowledge staleness detection as source files change.

### Items

9. ☑ Add `host_repo_root` parameter to `memory_git_log`

   The existing tool reads git log from the memory repo root. Add an optional
   `use_host_repo: bool = False` parameter that, when set, reads from
   `host_repo_root` in `agent-bootstrap.toml` instead. Path validation must ensure
   the resolved path is a git repo and is not a child of the memory worktree (to
   prevent path traversal).

   This is the prerequisite for all staleness detection work. Without it, agents
   have no way to know when source files have changed since a knowledge file's
   `last_verified` date.

10. ☑ Add `memory_check_knowledge_freshness` tool to `read_tools.py`

    Given a list of knowledge file paths, returns a list of freshness reports:
    - `status`: `fresh` / `stale` / `unknown` (unknown if `last_verified` is absent
      or `host_repo_root` is not configured)
    - `knowledge_file`: the memory file path
    - `source_files`: list of files referenced in the knowledge file's frontmatter
      `related` field or inferred from the file's content directory structure
    - `last_verified`: date from frontmatter
    - `verified_against_commit`: optional commit SHA recorded in frontmatter when the
      knowledge file was last reviewed against the host repo
    - `current_head`: current host-repo commit SHA used for the freshness comparison
    - `host_changes_since`: number of commits to matched source files since
      `last_verified`
    - `suggested_action`: `promote` / `reverify` / `downgrade_trust` / `none`

    This makes the trust decay policy machine-enforceable rather than advisory and gives
    freshness checks a stronger provenance anchor than date-only comparisons.

11. ☑ Update `memory_audit_trust` to use freshness data when `host_repo_root` is set

    The existing audit tool checks `last_verified` dates against fixed thresholds.
    Extend it so that when host repo access is available, stale thresholds are
    supplemented by actual change activity and, when present, `verified_against_commit`.
    A knowledge file with a 6-month-old `last_verified` but zero host-repo changes to
    its source files is less urgent than one with a 2-week-old `last_verified` but 40
    intervening commits.

12. ☑ Add test coverage for items 9–11

    Use a temporary git repo with a known commit history as the simulated host repo.
    Cover: fresh file (no source changes), stale file (source changed after
    `last_verified`), missing `host_repo_root` returns `unknown`, path traversal
    attempt is rejected.

---

## Phase 3: CI/CD and tooling hygiene templates

Goal: the memory branch and worktree do not cause noise in the host project's CI,
search tools, formatters, or linters.

### Items

13. ☐ Write a CI/CD exemption guide in `HUMANS/docs/INTEGRATIONS.md`

    Add a "Worktree Mode" section covering:
    - How to add `branches-ignore: [agent-memory]` (or the configured branch name)
      to GitHub Actions workflows.
    - How to handle branch protection rules (memory branch should be exempt from
      required reviews and status checks).
    - How to prevent the memory branch from appearing in PR comparisons or release
      notes.
    - GitLab CI / Bitbucket Pipelines equivalents.

14. ☐ Write a tooling-bleed prevention guide in `HUMANS/docs/INTEGRATIONS.md`

    Cover how to exclude the worktree path from:
    - ESLint / Prettier (`.eslintignore`, `.prettierignore`)
    - Black / Ruff (`pyproject.toml` `exclude` lists)
    - TypeScript (`tsconfig.json` `exclude`)
    - IDE search indexes (VS Code `search.exclude`, JetBrains scope exclusions)
    - `grep`/`ripgrep` (`.ignore` or `.rgignore` file at the worktree root)

    Include ready-to-paste config snippets for each.

15. ☐ Add a `.ignore` file to the worktree seed (item 2)

    A `.ignore` file (used by ripgrep, fd, and many editors) at the worktree root
    prevents most search tools from indexing memory content during codebase search
    without requiring per-tool configuration.

16. ☐ Add a `.editorconfig` stub to the worktree seed

    Prevents editors from applying the host project's indentation/line-ending rules
    to memory Markdown files.

---

## Phase 4: Codebase knowledge starter templates

Goal: an agent starting a new codebase memory store has a ready-made structure and
plan to follow rather than having to design one from scratch.

### Items

17. ☐ Add `setup/templates/codebase-survey-plan.md`

    A template plan file that agents can instantiate with the host project's name.
    Pre-populated phases:
    - Phase 0: Entry-point mapping (main urls, top-level components, app entrypoint)
    - Phase 1: Module-by-module structural survey
    - Phase 2: Data model and API contract documentation
    - Phase 3: Operational knowledge (how to run, test, deploy)
    - Phase 4: Design rationale capture (ADRs, historical decisions)
    - Phase 5: Ongoing staleness review cycle

    Each phase item produces one knowledge file. The plan tracks completion and
    surfaces `next_action` for the next session.

18. ☐ Add `setup/templates/knowledge/codebase/` starter structure

    A minimal skeleton:
    - `codebase/SUMMARY.md` (describes the project at the architecture level)
    - `codebase/architecture.md` (stub: entry points, module map, key dependencies)
    - `codebase/data-model.md` (stub: core entities and their relationships)
    - `codebase/operations.md` (stub: how to run, test, deploy)
    - `codebase/decisions.md` (stub: key design decisions and rationale)

    All stubs have `trust: low, source: template` frontmatter as placeholders.
    The init script copies this skeleton into the worktree during setup.

19. ☐ Add `skills/codebase-survey.md`

    A skill file (procedural, protected tier) describing the session workflow for
    systematic codebase exploration:
    - How to read the active survey plan and find the next uncompleted item.
    - How to explore a module (read entry points first, then follow imports).
    - When to write a knowledge file vs. a scratchpad note.
    - How to cross-reference knowledge files with `related` frontmatter.
    - When to promote `trust: low` codebase knowledge to `trust: medium`.
    - How to surface a source-file change (via `memory_check_knowledge_freshness`)
      as a review-queue item.

20. ☐ Update `identity/profile.md` template to capture codebase context

    Add a `codebase` section to the `software-developer` and `project-manager`
    profile templates with fields:
    - `project_name`
    - `tech_stack` (list)
    - `repo_url`
    - `host_repo_root` (absolute path, set by init script)
    - `memory_worktree_path` (absolute path, set by init script)

---

## Phase 5: Validator and test suite extensions

Goal: `validate_memory_repo.py` and the test suite understand and enforce the
worktree configuration, preventing silent misconfiguration.

### Items

21. ☐ Add worktree mode detection to `validate_memory_repo.py`

    If `agent-bootstrap.toml` contains `host_repo_root`, the validator should:
    - Verify that `host_repo_root` exists and is a git repo.
    - Verify that `host_repo_root` is not a child of the memory repo root.
    - Verify that the memory repo root is a git worktree (not a standard checkout).
    - Check that the memory branch has no shared history with the host repo's
      default branch.

22. ☐ Verify adapter files are not duplicated into the worktree

    In worktree mode the host-root adapter files (`CLAUDE.md`, `AGENTS.md`,
    `.cursorrules`) should differ from the worktree-internal adapter files.
    The validator should warn if the worktree root contains adapter files that
    duplicate the host root's content without modification.

23. ☐ Add validator tests for items 21–22

    Cover: valid worktree config passes; missing `host_repo_root` in worktree mode
    fails; `host_repo_root` pointing inside the worktree fails; shared history
    detected as a warning; duplicate adapter content produces a warning.

24. ☐ Add CI job for `init-worktree.sh` end-to-end test

    In `.github/workflows/ci.yml`, add a job that:
    - Creates a minimal host git repo in a temp dir.
    - Runs `init-worktree.sh --non-interactive --profile software-developer`.
    - Asserts the orphan branch has no shared history with the host default branch.
    - Asserts the worktree exists at the expected path.
    - Asserts the MCP config references the worktree path.
    - Asserts `validate_memory_repo.py` passes against the new worktree.

---

## Dependencies and sequencing

Phases should be worked in order: Phase 0 is the entry point users will actually
touch, Phases 1–2 make it correct, Phases 3–4 make it frictionless, Phase 5 keeps
it honest.

Phase 2 (host git access) depends on Phase 1 (`host_repo_root` in
`agent-bootstrap.toml`). Everything else in Phases 3–5 can proceed in parallel
once Phase 0 is complete.

The MCP tool improvements in Phase 2 are additive — they do not break the existing
standalone-mode contract. `use_host_repo=False` is the default; existing users see
no change.

---

## Non-goals for this roadmap

- Making the worktree approach retroactively compatible with existing standalone
  memory repos (migration is a separate future plan).
- Supporting multiple simultaneous worktrees for the same memory branch.
- Windows native path support beyond what `setup.sh` currently handles (deferred
  until the host-detection logic is proven on Linux/Mac first).
- Any GUI-based init flow.

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-19 | Plan created following design discussion on orphan-branch worktree integration strategy |
| 2026-03-20 | Completed Phase 0 by adding `setup/init-worktree.sh`, the minimal `setup/init-worktree-paths.txt` seed manifest, `--dry-run` support, host-root Codex/generic MCP config output, and setup-flow coverage for orphan-branch creation and dry-run behavior. Then completed Phase 1 items 5-8 by writing host-root adapter files, preferring `engram-mcp` over the path-based script when available, formalizing optional `host_repo_root` support in the bootstrap resolver and validator, and updating `meta/quick-reference.md` for host-root worktree routing. Also completed Phase 2 item 9 by teaching `memory_git_log` to read from the configured host repo with path-safety checks. Next planned item: Phase 2 item 10 (`memory_check_knowledge_freshness`). |
| 2026-03-20 | Completed Phase 2 items 10-12 by adding `memory_check_knowledge_freshness`, reusing the host-repo bootstrap contract to resolve related source files and compare them against host git history, and folding the same freshness signal into `memory_audit_trust` so stale host-backed notes are escalated by change activity while unchanged notes stay lower priority. Added targeted MCP coverage for stale, fresh, unknown-host, and export behavior; targeted tests passed (`98 passed`). Next planned item: Phase 3 item 13 (`HUMANS/docs/INTEGRATIONS.md` worktree guidance). |
