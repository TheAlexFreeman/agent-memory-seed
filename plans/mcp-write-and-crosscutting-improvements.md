---
created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: implement memory_update_frontmatter_bulk in write_tools.py"
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: MCP Tier 2 Write Tool and Cross-Cutting Improvements

## Goals

Close three gaps identified during a full-stack MCP tooling review that span Tier 2 write tools and cross-cutting concerns: a frontmatter bulk-update tool to replace error-prone mass backfills, a native capability discovery tool, and context-line support in `memory_search` to reduce follow-up reads.

---

## Problem statement

**Gap 9 — No bulk frontmatter update:** The current `memory_update_frontmatter` handles one file at a time. During a mass backfill operation in the prior session, 35+ individual calls were needed to add `origin_session: unknown` to files missing the field. Each call produces its own `[system]` commit, polluting git history with dozens of one-line commits. A `[{path, updates}]` batch form that stages all changes and produces a single commit is the natural solution. The systems-architecture research sharpens this further: the tool should behave like a staged transaction, with fail-before-publish validation and explicit rollback of any partial staged state.

**Gap 10 — Capability discovery is not tool-native:** The capabilities contract (`HUMANS/tooling/agent-memory-capabilities.toml`) declares a `[capability_discovery]` section specifying `well_known_paths`, `requires_kind`, and `supported_versions`. But there is no MCP tool that implements this discovery protocol. Capability discovery currently requires: call `memory_list_folder("HUMANS/tooling", include_humans=True)` → call `memory_read_file("HUMANS/tooling/agent-memory-capabilities.toml")` → parse TOML manually in the agent's context. A dedicated `memory_get_capabilities` tool would make this self-consistent and available to any runtime without TOML parsing logic.

**Gap 11 — `memory_search` context lines are missing:** Current output format is:
```
**knowledge/_unverified/django/celery-advanced-patterns.md**
  45: start a task chain using .si() or .s() and pass explicit arguments
```
When the matching line is part of a multi-line construct (a code block, a list item spanning several lines, or a paragraph), the single-line view is not enough to understand the match without a follow-up `memory_read_file`. A `context_lines` parameter (like `grep -B {n} -A {n}`) would expose surrounding lines and eliminate a common read-after-search pattern.

---

## Phases

### Phase 1 — `memory_update_frontmatter_bulk`

**1.1 Implement the batch tool in `write_tools.py`**
New Tier 2 tool (staged, no auto-commit). Signature:
```python
async def memory_update_frontmatter_bulk(
    updates: list[dict],
    create_missing_keys: bool = True,
) -> str
```

`updates` is a list of objects:
```json
[
  {
    "path": "knowledge/_unverified/rationalist-community/origins/foo.md",
    "fields": {"origin_session": "unknown", "source": "agent-generated"}
  }
]
```

For each entry:
1. Validate path is an allowed Tier 2 target (reuse `validate_raw_write_target`)
2. Read file and parse frontmatter
3. Apply `fields` dict: if `create_missing_keys=True` add missing keys; otherwise only update existing keys
4. Write file with updated frontmatter and stage with `repo.add(path)`

Returns `MemoryWriteResult` with `files_changed` listing all staged paths, `new_state.updated_count`, `new_state.skipped_count` (files where no field values changed), and `new_state.transaction_state = "staged"`. One call to `memory_commit` is required after to finalize.

**1.2 Enforce batch size limit**
Reject batches of more than 100 files with `ValidationError`. This is a soft safeguard against model-generated runaway batches.

**1.3 Handle partial validation failure**
If any path in the batch fails validation (protected directory, file not found, version conflict), fail the entire batch before staging anything. If a filesystem write or `repo.add()` fails after staging has begun, explicitly unstage and clean up any partial transaction state before returning an error. Return a clear error listing which paths failed and why.

**1.4 Add `memory_update_frontmatter_bulk` to capabilities TOML**
Add to `raw_fallback` list (it is a Tier 2 raw tool). Document `max_batch_size: 100` in an informational comment.

---

### Phase 2 — `memory_get_capabilities`

**2.1 Implement the tool in `read_tools.py`**
New Tier 0 tool. Signature:
```python
async def memory_get_capabilities() -> str
```

Reads `HUMANS/tooling/agent-memory-capabilities.toml` (using the well-known path declared in `[capability_discovery]`). Parses and returns structured JSON:
```json
{
  "version": 1,
  "kind": "agent-memory-capabilities",
  "contract_versions": {
    "frontmatter": 1,
    "access": 1,
    "mcp": 1,
    "capabilities": 1
  },
  "read_support": [...],
  "raw_fallback": [...],
  "semantic_extensions": [...],
  "declared_gaps": [...],
  "desktop_operations": {...},
  "integration_boundary": {...},
  "operations": {...}
}
```

If the TOML cannot be parsed, returns `{"error": "...", "raw": "..."}` rather than raising (capability discovery should degrade gracefully so callers can fall back to manual inspection).

**2.2 Return a compact `summary` field**
The full TOML is large. Add a `summary` field:
```json
{
  "summary": {
    "total_tools": 24,
    "read_tools": 10,
    "semantic_tools": 14,
    "declared_gaps": 0,
    "contract_versions": {
      "frontmatter": 1,
      "access": 1,
      "mcp": 1,
      "capabilities": 1
    }
  }
}
```

**2.3 Register in `read_support` and capabilities contract**
Add `memory_get_capabilities` to the `read_support` list in `HUMANS/tooling/agent-memory-capabilities.toml`. This is intentionally self-referential (the tool is listed in the very manifest it reads); document this in the docstring.

---

### Phase 3 — `memory_search` context lines

**3.1 Add `context_lines` param**
Add `context_lines: int = 0` parameter to `memory_search`. When non-zero, includes up to `context_lines` lines before and after each match in the output. Mirrors `grep -B {n} -A {n}` behavior.

Implementation path:
- For the git grep code path: pass `-B {context_lines} -A {context_lines}` to git grep. Parse the extra output lines (marked with `-` prefix in git grep output) and attach them to the matching line group.
- For the Python fallback: capture the surrounding lines from the file's `splitlines()` array using slice arithmetic.

**3.2 Enforce reasonable ceiling**
Cap `context_lines` at 10. Values above 10 raise `ValidationError`. Document the cap in the docstring.

**3.3 Output format**
Surrounding context lines are prefixed with `  {line_no}| ` (note: matching lines keep the existing `  {line_no}: ` format). This visual distinction makes it easy to see which lines matched vs. which are context.

**3.4 Update max_results accounting**
Context lines should not count toward `max_results`. Only matching lines count. Document this explicitly.

---

### Phase 4 — Tests and documentation

**4.1 Tests for `memory_update_frontmatter_bulk`**
- Single-file batch: field added, version_token checked, staged correctly
- Multi-file batch: all files staged; single `memory_commit` finalizes
- `create_missing_keys=False`: existing key updated, missing key skipped
- Batch with invalid path: fails before staging anything, error lists failing path
- Mid-batch staging failure: tool rolls back partial staged state and leaves no dirty transaction residue
- Batch > 100 files: rejected with ValidationError
- Batch touching protected directory: rejected

**4.2 Tests for `memory_get_capabilities`**
- Returns parseable JSON with all expected top-level keys
- `summary.total_tools` matches actual tool count
- Graceful error when TOML is malformed

**4.3 Tests for `memory_search` context_lines**
- `context_lines=0` (default): output identical to current behavior
- `context_lines=2`: surrounding lines included, correctly prefixed
- `context_lines=11`: raises ValidationError
- Context lines do not count toward `max_results`

**4.4 Update capabilities TOML test suite**
Extend `test_memory_capabilities.py` to assert `memory_get_capabilities` is in `read_support` and `memory_update_frontmatter_bulk` is in `raw_fallback`.

---

## Progress tracking

- [ ] 1.1 Implement `memory_update_frontmatter_bulk` in `write_tools.py`
- [ ] 1.2 Enforce 100-file batch size limit
- [ ] 1.3 Handle partial validation failure (fail-before-stage)
- [ ] 1.4 Update capabilities TOML for bulk frontmatter tool
- [ ] 2.1 Implement `memory_get_capabilities` in `read_tools.py`
- [ ] 2.2 Add `summary` field to capabilities output
- [ ] 2.3 Register in `read_support` and capabilities contract
- [ ] 3.1 Add `context_lines` param to `memory_search`
- [ ] 3.2 Enforce context_lines ceiling of 10
- [ ] 3.3 Output format with context line prefix `{line_no}|`
- [ ] 3.4 Update max_results accounting to exclude context lines
- [ ] 4.1 Tests for `memory_update_frontmatter_bulk`
- [ ] 4.2 Tests for `memory_get_capabilities`
- [ ] 4.3 Tests for `memory_search` context_lines
- [ ] 4.4 Update capabilities TOML test suite

**Progress:** 0/15 items complete

---

## Design constraints

- `memory_update_frontmatter_bulk` is a Tier 2 tool: it stages but does NOT auto-commit. The caller must call `memory_commit` explicitly. This is intentional — bulk changes benefit from a manual review step before committing.
- `memory_get_capabilities` must not modify any files. If the TOML cannot be found, return a structured error, not an exception.
- `memory_update_frontmatter_bulk` must behave like a staged transaction: validate first, publish later, and leave no partial staged residue on failure.
- `context_lines` cap of 10 is non-configurable via params (only via source changes). The ceiling prevents accidentally dumping full files through search.
- `memory_update_frontmatter_bulk` respects the same protected-directory restrictions as other Tier 2 tools: `identity/`, `meta/`, `chats/`, `skills/` are blocked. For governed writes to those dirs, callers must use the appropriate Tier 1 semantic tools.
- All three tools must be added to `server.py`'s `register()` call chain before they are callable.
