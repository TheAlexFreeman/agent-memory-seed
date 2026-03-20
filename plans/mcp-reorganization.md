---
created: 2026-03-19
last_verified: '2026-03-19'
next_action: Resolve the top-level `mcp` namespace collision before renaming `tools/`.
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: implementation-plan
---

# Implementation Plan: MCP Module Reorganization

## Problem statement

The MCP runtime has outgrown its current placement. The package lives at
`tools/agent_memory_mcp/` — a directory name that communicates nothing about its
role — while its entrypoint lives at `HUMANS/tooling/scripts/memory_mcp.py`,
alongside human-facing setup scripts it has no logical relationship to. Tests for
the package also live in `HUMANS/tooling/tests/`, burying agent-runtime test
coverage inside a human-tooling namespace.

More critically, the `semantic_tools.py` file has grown to 1,917 lines with no
internal module boundaries. All 16 semantic tools, the session state singleton,
and shared helpers are defined in a single file. This makes the file hard to
navigate, hard to test in isolation, and hard to extend without risking regression
across unrelated tools.

The system also lacks a formal layer boundary between the *memory format* (the
file schema, governance rules, and git operations — things that work without Python)
and the *MCP runtime* (the governed write layer that requires Python and `mcp`).
This boundary exists conceptually but is not reflected in the directory structure,
the dependency graph, or the repository's contract-version surface. The
systems-architecture research also clarifies that this runtime boundary is the natural
single-writer actor for governed mutations, so the reorganization should make that
ownership explicit rather than leave it implicit.

## Goals

1. Rename `tools/` → `mcp/` so the directory name matches what it contains.
2. Move the MCP entrypoint into `mcp/` so all MCP runtime code lives in one place.
3. Move MCP-specific tests into `mcp/tests/` and keep only non-MCP tests in
   `HUMANS/tooling/tests/`.
4. Add a `[project.scripts]` CLI entrypoint so the server runs as `memory-mcp`
   after `pip install -e .[server]` — no path arithmetic required.
5. Split `semantic_tools.py` into four focused submodules grouped by domain.
6. Make the format/validation layer importable without the `mcp` dependency, with centralized schema-version and contract constants that adapters can expose consistently.
7. Update every hardcoded path reference: config files, setup scripts, adapter
   files, capability manifests, and the worktree integration plan.
8. Keep the test suite green throughout. Treat a failing test at any point as a
   blocker, not a known issue.

## Non-goals

- Changing any tool behavior, signature, or return type.
- Changing the MCP tool names exposed to agents.
- Changing the memory file format or frontmatter schema.
- Publishing to PyPI (defer to production-readiness roadmap).
- Implementing the worktree init script (separate plan).

## Resulting directory structure

```
mcp/                                  ← renamed from tools/
  __init__.py
  agent_memory_mcp/
    __init__.py
    errors.py
    frontmatter_utils.py
    git_repo.py
    models.py
    path_policy.py
    server.py
    server_main.py                    ← new: CLI entrypoint function
    tools/
      __init__.py
      read_tools.py
      write_tools.py
      semantic/                       ← new: replaces monolithic semantic_tools.py
        __init__.py                   ← re-exports all tools for server.py compat
        _session.py                   ← session state + reset tool
        plan_tools.py                 ← mark_plan_item_complete, create_plan,
        |                                update_plan_next_action, list_plans
        knowledge_tools.py            ← add_knowledge_file, promote, demote,
        |                                archive
        identity_tools.py             ← update_identity_trait
        session_tools.py              ← record_chat_summary, record_reflection,
                                         append_scratchpad, log_access,
                                         flag_for_review, revert_commit,
                                         diff, audit_trust
  tests/                              ← moved from HUMANS/tooling/tests/
    __init__.py
    test_memory_mcp.py
    test_agent_memory_mcp_write_tools.py

HUMANS/
  tooling/
    scripts/
      validate_memory_repo.py         ← stays (human-facing validator)
      resolve_bootstrap_manifest.py  ← stays (human-facing resolver)
      resolve_memory_capabilities.py ← stays (human-facing resolver)
      resolve_task_readiness.py      ← stays
      onboard-export.sh              ← stays
    tests/                            ← only non-MCP tests remain
      __init__.py
      test_validate_memory_repo.py   ← stays
      test_bootstrap_resolver.py     ← stays
      test_memory_capabilities.py    ← stays
      test_task_readiness.py         ← stays
      test_onboard_export.py         ← stays
      test_setup_flows.py            ← stays (references entrypoint path → update)
    agent-memory-capabilities.toml   ← update mcp_entrypoint path
    mcp-config-example.json          ← update args path
```

---

## Phase 0: Rename `tools/` → `mcp/` and update package metadata

Goal: establish the new directory name and make Python packaging aware of it.
The server does not yet run from the new path at the end of this phase — that
comes in Phase 1. This phase is purely structural and must not break any existing
imports until Phase 1 provides the compat shim.

Blocking finding (2026-03-19): the repo already depends on the third-party
`mcp` package (`mcp>=1.0` in `pyproject.toml`), and the active virtual
environment resolves `import mcp` to site-packages. Creating a top-level local
package named `mcp/` would shadow that dependency on `sys.path`, breaking
imports like `from mcp.server.fastmcp import FastMCP`. Resolve this namespace
collision before executing the rename as written.

### Items

1. ☐ Rename the directory

   `tools/` → `mcp/` (file copy + delete since the sandbox restricts `rename()`).
   The subdirectory `tools/agent_memory_mcp/` becomes `mcp/agent_memory_mcp/`.
   The top-level `tools/__init__.py` becomes `mcp/__init__.py`.

2. ☐ Update `pyproject.toml` package discovery and add CLI entrypoint

   ```toml
   [tool.setuptools.packages.find]
   where = ["."]
   include = ["mcp*"]          # was "tools*"

   [project.scripts]
   memory-mcp = "mcp.agent_memory_mcp.server_main:main"

   [tool.pytest.ini_options]
   testpaths = [
       "HUMANS/tooling/tests",
       "mcp/tests",             # add new location
   ]
   ```

3. ☐ Write `mcp/agent_memory_mcp/server_main.py`

   A minimal module containing the `main()` function that `[project.scripts]`
   will call:

   ```python
   from __future__ import annotations
   from .server import mcp

   def main() -> None:
       mcp.run()

   if __name__ == "__main__":
       main()
   ```

4. ☐ Add a compat shim at `tools/__init__.py` (temporary)

   After moving `tools/` to `mcp/`, any code that still imports from
   `tools.agent_memory_mcp.*` would immediately break. To keep the test suite
   green throughout the transition, create a shim:

   ```
   tools/
     __init__.py   ← "import mcp.agent_memory_mcp as agent_memory_mcp; ..."
     agent_memory_mcp/
       __init__.py ← re-export everything from mcp.agent_memory_mcp
   ```

   This shim is temporary and removed in Phase 3 once all direct `tools.*`
   imports are updated. Do not add new imports to the shim.

5. ☐ Verify: install package, confirm `memory-mcp` command is present

   ```bash
   pip install -e ".[server]" --break-system-packages
   memory-mcp --help   # or: python -m mcp.agent_memory_mcp.server_main
   ```

6. ☐ Run full test suite — must be green before proceeding to Phase 1.

---

## Phase 1: Relocate entrypoint and MCP-specific tests

Goal: move `HUMANS/tooling/scripts/memory_mcp.py` into `mcp/` and move the two
MCP-specific test files into `mcp/tests/`. After this phase, nothing MCP-runtime
lives under `HUMANS/`.

### Items

7. ☐ Move entrypoint: `HUMANS/tooling/scripts/memory_mcp.py` → `mcp/memory_mcp.py`

   Update the file to use the new import path:

   ```python
   # Old: _server = importlib.import_module("tools.agent_memory_mcp.server")
   # New: direct import — no sys.path manipulation needed once installed
   from mcp.agent_memory_mcp import server as _server
   ```

   The file is kept for backward compatibility with existing `.codex/config.toml`
   and `mcp-config-example.json` references. It is not removed — it is only
   relocated. A deprecation comment is added noting that `memory-mcp` (the CLI
   entrypoint) is now the preferred invocation.

8. ☐ Move MCP test files

   - `HUMANS/tooling/tests/test_memory_mcp.py` → `mcp/tests/test_memory_mcp.py`
   - `HUMANS/tooling/tests/test_agent_memory_mcp_write_tools.py`
     → `mcp/tests/test_agent_memory_mcp_write_tools.py`
   - Create `mcp/tests/__init__.py`

   Update `SCRIPT_PATH` in `mcp/tests/test_memory_mcp.py`:

   ```python
   # Old: SCRIPT_PATH = REPO_ROOT / "HUMANS" / "tooling" / "scripts" / "memory_mcp.py"
   # New: SCRIPT_PATH = REPO_ROOT / "mcp" / "memory_mcp.py"
   ```

   Update `tools.agent_memory_mcp.*` imports in `mcp/tests/test_agent_memory_mcp_write_tools.py`
   to `mcp.agent_memory_mcp.*`.

9. ☐ Update `test_setup_flows.py` entrypoint path assertion

   The setup flow test asserts that `setup.sh` generates a config containing the
   `memory_mcp.py` path. Update the expected path from
   `HUMANS/tooling/scripts/memory_mcp.py` to `mcp/memory_mcp.py`:

   ```python
   # test_setup_flows.py line ~168
   str(root / "mcp" / "memory_mcp.py").replace("\\", "\\\\")
   ```

10. ☐ Update `resolve_memory_capabilities.py` import

    ```python
    # Old: from tools.agent_memory_mcp.server import create_mcp
    # New: from mcp.agent_memory_mcp.server import create_mcp
    ```

11. ☐ Run full test suite — must be green before proceeding to Phase 2.

---

## Phase 2: Update all hardcoded path references

Goal: every config file, setup script, adapter file, and documentation reference
that embeds the old `HUMANS/tooling/scripts/memory_mcp.py` path is updated to
`mcp/memory_mcp.py`. This is the user-visible change — existing `.codex/config.toml`
files generated by `setup.sh` will need to be regenerated by each user after
upgrading.

### Items

12. ☐ Update `setup/setup.sh`

    ```bash
    # Old:
    local memory_script="${repo_root_native%[\\/]}${sep}HUMANS${sep}tooling${sep}scripts${sep}memory_mcp.py"
    # New:
    local memory_script="${repo_root_native%[\\/]}${sep}mcp${sep}memory_mcp.py"
    ```

13. ☐ Update `setup/setup.html`

    ```javascript
    // Old:
    var memoryScript = trimmedRepo + sep + 'HUMANS' + sep + 'tooling' + sep + 'scripts' + sep + 'memory_mcp.py'
    // New:
    var memoryScript = trimmedRepo + sep + 'mcp' + sep + 'memory_mcp.py'
    ```

14. ☐ Update `HUMANS/tooling/mcp-config-example.json`

    ```json
    // Old: "args": ["~/code/personal/agent-memory-seed/HUMANS/tooling/scripts/memory_mcp.py"]
    // New: "args": ["~/code/personal/agent-memory-seed/mcp/memory_mcp.py"]
    ```

15. ☐ Update `HUMANS/tooling/agent-memory-capabilities.toml`

    ```toml
    # Old: mcp_entrypoint = "HUMANS/tooling/scripts/memory_mcp.py"
    # New: mcp_entrypoint = "mcp/memory_mcp.py"
    ```

16. ☐ Update `.codex/config.toml`

    The committed config contains user-specific absolute paths. Update the
    `args` path to point at `mcp/memory_mcp.py` and add a comment that this file
    is regenerated by `setup.sh` and should not be edited by hand. (The committed
    version with absolute paths is a known issue tracked separately — see
    P3-C of the remediation plan.)

17. ☐ Update `HUMANS/docs/INTEGRATIONS.md`

    The Python library import example:
    ```python
    # Old: from tools.agent_memory_mcp.server import create_mcp
    # New: from mcp.agent_memory_mcp.server import create_mcp
    ```

18. ☐ Update `worktree-integration.md` plan references

    Phase 1, item 6 of the worktree plan references
    `<worktree-path>/HUMANS/tooling/scripts/memory_mcp.py` as the MCP entrypoint.
    Update to `<worktree-path>/mcp/memory_mcp.py` and note that the preferred
    invocation is `memory-mcp` (the CLI script) when installed.

19. ☐ Update `setup/initial-commit-paths.txt`

    Remove: `tools/__init__.py`, `tools/agent_memory_mcp/*` entries
    Add: `mcp/__init__.py`, `mcp/memory_mcp.py`, `mcp/agent_memory_mcp/*`,
    `mcp/tests/__init__.py`, `mcp/tests/test_memory_mcp.py`,
    `mcp/tests/test_agent_memory_mcp_write_tools.py`

20. ☐ Update CI workflow (``.github/workflows/ci.yml``)

    Update the `ruff` lint paths and any explicit file paths from
    `tools/agent_memory_mcp/` to `mcp/agent_memory_mcp/`.

21. ☐ Remove the `tools/` compat shim (from Phase 0, item 4)

    Once all imports are updated, delete:
    - `tools/__init__.py`
    - `tools/agent_memory_mcp/` (the shim directory)

    Verify nothing imports from `tools.*` any longer:
    ```bash
    grep -r "from tools\." --include="*.py" .
    grep -r "import tools\." --include="*.py" .
    ```

22. ☐ Run full test suite — must be green before proceeding to Phase 3.

---

## Phase 3: Split `semantic_tools.py` into domain submodules

Goal: replace the 1,917-line monolith with four focused modules plus a session
state module, all re-exported through a compatibility `__init__.py` so `server.py`
requires no changes.

The split follows domain boundaries that are already implicit in the tool names:

| New module | Tools it contains | Lines (approx) |
|---|---|---|
| `_session.py` | `_session_state` dict, `memory_reset_session_state` | ~80 |
| `plan_tools.py` | `memory_create_plan`, `memory_mark_plan_item_complete`, `memory_update_plan_next_action`, `memory_list_plans` | ~600 |
| `knowledge_tools.py` | `memory_add_knowledge_file`, `memory_promote_knowledge`, `memory_demote_knowledge`, `memory_archive_knowledge` | ~600 |
| `identity_tools.py` | `memory_update_identity_trait` | ~150 |
| `session_tools.py` | `memory_record_chat_summary`, `memory_record_reflection`, `memory_append_scratchpad`, `memory_log_access`, `memory_flag_for_review`, `memory_revert_commit`, `memory_diff`, `memory_audit_trust` | ~500 |

Note: `_session.py` is a private implementation module (underscore prefix). It is
imported by `identity_tools.py` (which increments `identity_updates`) and
`session_tools.py` (which reads and resets the counter). No other module touches
session state directly.

### Items

23. ☐ Create `mcp/agent_memory_mcp/tools/semantic/` directory and stub files

    Create `__init__.py`, `_session.py`, `plan_tools.py`, `knowledge_tools.py`,
    `identity_tools.py`, `session_tools.py` — initially empty except for imports.

24. ☐ Move session state to `_session.py`

    Extract `_session_state`, `_IDENTITY_CHURN_LIMIT`, and the
    `memory_reset_session_state` tool registration from `semantic_tools.py` into
    `_session.py`. Expose:

    ```python
    # _session.py
    _session_state: dict[str, int] = {"identity_updates": 0}
    _IDENTITY_CHURN_LIMIT: int = 5

    def get_identity_updates() -> int: ...
    def increment_identity_updates() -> int: ...
    def reset_session_state() -> None: ...

    def register_tools(mcp: FastMCP, ...) -> dict[str, Callable]: ...
    ```

    Using accessor functions (rather than direct dict mutation) makes the session
    state testable in isolation and eliminates the module-level global mutation
    that was flagged in the P1-A remediation item.

25. ☐ Move plan tools to `plan_tools.py`

    Move `memory_create_plan`, `memory_mark_plan_item_complete`,
    `memory_update_plan_next_action`, `memory_list_plans` and all their
    private helpers. Each submodule exposes a `register_tools(mcp, get_repo,
    get_root) -> dict[str, Callable]` function that returns the tool name →
    callable mapping.

26. ☐ Move knowledge tools to `knowledge_tools.py`

    Move `memory_add_knowledge_file`, `memory_promote_knowledge`,
    `memory_demote_knowledge`, `memory_archive_knowledge` and their helpers.

27. ☐ Move identity tools to `identity_tools.py`

    Move `memory_update_identity_trait`. This module imports `_session.py`'s
    `increment_identity_updates()` and `get_identity_updates()` instead of
    mutating `_session_state` directly.

28. ☐ Move session/governance tools to `session_tools.py`

    Move `memory_record_chat_summary`, `memory_record_reflection`,
    `memory_append_scratchpad`, `memory_log_access`, `memory_flag_for_review`,
    `memory_revert_commit`, `memory_diff`, `memory_audit_trust` and their
    helpers. The `memory_reset_session_state` tool is registered from
    `_session.py` but its MCP registration can be handled here or in
    `__init__.py` — keep it in `_session.py` for co-location with the state.

29. ☐ Write `semantic/__init__.py` as a compatibility re-export

    `server.py` currently does:
    ```python
    from .tools import semantic_tools
    # ... semantic_tools.register_tools(mcp, ...)
    ```

    The `semantic/__init__.py` re-exports a unified `register_tools` that
    delegates to all five submodules in the correct order, returning the merged
    tool dict. `server.py` changes only its import line:
    ```python
    # Old: from .tools import semantic_tools
    # New: from .tools import semantic   # semantic is now the package
    ```

30. ☐ Delete `semantic_tools.py`

    Only after all tests pass with the new submodule structure. Keep the file
    until then as a reference.

31. ☐ Run full test suite — must be green. Address any regressions before
    marking Phase 3 complete.

---

## Phase 4: Formalize the format/validation layer boundary

Goal: make it structurally true that the memory format and validation logic
can be imported without the `mcp` dependency. This is the "works without MCP"
guarantee formalized as a dependency constraint.

### Items

32. ☐ Identify the zero-MCP-dependency modules

    The following modules in `mcp/agent_memory_mcp/` have no `mcp` imports today
    and constitute the format/validation layer:
    - `errors.py` — exception types
    - `frontmatter_utils.py` — YAML frontmatter read/write
    - `git_repo.py` — git subprocess operations
    - `models.py` — data models (`MemoryWriteResult`, etc.)
    - `path_policy.py` — path validation rules

    Verify this claim with:
    ```bash
    python -c "import mcp.agent_memory_mcp.frontmatter_utils"
    # run with mcp not installed — should succeed
    ```

33. ☐ Add a `core` extras group to `pyproject.toml`

    ```toml
    [project.optional-dependencies]
    core = [
        "python-frontmatter>=1.1",
        "gitpython>=3.0",      # only if git_repo.py ever adopts it; keep as subprocess for now
    ]
    server = [
        "mcp>=1.0",
        "agent-memory-mcp[core]",  # server depends on core
    ]
    ```

    For now, `core` may be empty (git_repo.py uses subprocesses, not gitpython;
    frontmatter_utils.py requires python-frontmatter). The key outcome is that
    the distinction is declared and enforced, not that the dependency list changes.

34. ☐ Guard `mcp` imports in `server.py` behind `TYPE_CHECKING` where possible

    Any `from mcp.server.fastmcp import FastMCP` that appears at module level in
    non-server files is a layering violation. Audit all files in
    `mcp/agent_memory_mcp/` for top-level `mcp` imports — they should exist
    only in `server.py` and `server_main.py`.

35. ☐ Update `validate_memory_repo.py` to import from `mcp.agent_memory_mcp.core`
    submodules if needed

    The validator currently does not import from `tools.*` (confirmed in Phase 0
    reconnaissance). If it needs frontmatter utilities in the future, it should
    import from the core modules directly, not from the server.

36. ☐ Document the layer boundary in `HUMANS/docs/DESIGN.md`

    Add a section describing the two layers:
    - **Format layer** (`mcp/agent_memory_mcp/{errors,frontmatter_utils,git_repo,
      models,path_policy}.py`): no `mcp` dependency, usable independently,
      importable by the validator and setup scripts.
    - **Runtime layer** (`mcp/agent_memory_mcp/server.py`, `tools/`): requires
      `mcp[cli]>=1.0`, exposes the governed write surface to agents.

37. ☐ Run full test suite — must be green.

---

## Phase 5: Validation, CI update, and initial-commit manifest

Goal: ensure CI enforces the new structure, the initial-commit manifest is
accurate, and the validator understands the new layout.

### Items

38. ☐ Update `.github/workflows/ci.yml`

    - Change ruff lint paths from `tools/agent_memory_mcp/` to `mcp/agent_memory_mcp/`
    - Change pytest paths to include both `HUMANS/tooling/tests` and `mcp/tests`
    - Add a `pip install -e ".[dev]"` step before tests so the `memory-mcp`
      entrypoint is available

39. ☐ Update `validate_memory_repo.py` to check the new structure

    Add checks:
    - `mcp/` directory exists (if repo has MCP runtime)
    - `mcp/memory_mcp.py` exists
    - `tools/` directory does NOT exist (catches incomplete migrations)
    - `HUMANS/tooling/scripts/memory_mcp.py` does NOT exist (catches stale shims)
    - `agent-memory-capabilities.toml` `mcp_entrypoint` matches `mcp/memory_mcp.py`

40. ☐ Update `setup/initial-commit-paths.txt`

    Remove all `tools/` entries (they should have been removed in Phase 2,
    item 19 — this is the verification pass). Confirm all `mcp/` entries are
    present. Run `test_initial_commit_manifest_matches_tracked_repo_paths` to
    verify.

41. ☐ Final test run: all tests green, ruff clean, validator passes

    ```bash
    ruff check mcp/ HUMANS/tooling/scripts/ HUMANS/tooling/tests/
    python HUMANS/tooling/scripts/validate_memory_repo.py
    python -m pytest HUMANS/tooling/tests/ mcp/tests/ -v
    ```

---

## Commit strategy

Each phase should be committed as a single atomic commit once its test run is
green. Suggested commit messages:

- Phase 0: `[refactor] Rename tools/ to mcp/, add server_main entrypoint, compat shim`
- Phase 1: `[refactor] Relocate MCP entrypoint and tests into mcp/`
- Phase 2: `[refactor] Update all hardcoded memory_mcp.py path references`
- Phase 3: `[refactor] Split semantic_tools.py into domain submodules`
- Phase 4: `[refactor] Formalize format/runtime layer boundary`
- Phase 5: `[refactor] Update CI, validator, and initial-commit manifest for new layout`

All commits go on the current branch (`live-test--maiden`). No new branches needed.

---

## Risk register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Existing user `.codex/config.toml` breaks after upgrade | High | Document migration in CHANGELOG; `setup.sh --update` flag (future) |
| Compat shim (Phase 0) not removed, creating confusion | Medium | Phase 2 item 21 explicitly removes it; validator check in Phase 5 |
| `semantic/__init__.py` re-export misses a tool | Medium | Test suite covers all 16 tools; Phase 3 item 31 is a gating test run |
| Session state still leaks (P1-A) after split | Low | Phase 3 item 24 uses accessor functions; covered by existing write tool tests |
| `setup/initial-commit-paths.txt` goes stale | Low | Phase 5 item 40 runs the manifest test as explicit verification |

---

## Cross-plan dependencies

- **`worktree-integration.md`** — Phase 1, item 6 and Phase 0, item 1 of that plan
  reference `HUMANS/tooling/scripts/memory_mcp.py`. This reorganization must
  complete (or at least reach Phase 2) before the worktree init script is
  implemented. See item 18 above for the required update to that plan.

- **`production-readiness-roadmap.md`** — Phase 1 of that roadmap calls for moving
  governance-critical behavior into executable code. The layer boundary established
  in Phase 4 of this plan (format layer vs. runtime layer) is a prerequisite for
  the clean extraction described in that roadmap's Phase 0.

- **MCP improvements plans** (`mcp-read-tools-improvements.md`,
  `mcp-semantic-tools-improvements.md`, `mcp-write-and-crosscutting-improvements.md`,
  `access-log-tooling-improvements.md`) — all four add new tools or expand existing
  ones. New tools should be added to the appropriate semantic submodule, not to a
  new monolith. This reorganization should complete before those plans advance to
  avoid adding to `semantic_tools.py` during the split.

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-19 | Plan created following design discussion on MCP module growth and placement |
| 2026-03-19 | Verified a blocking namespace collision: renaming `tools/` to top-level `mcp/` would shadow the installed `mcp` dependency in the active venv, so Phase 0 needs a package-name revision before implementation can continue |