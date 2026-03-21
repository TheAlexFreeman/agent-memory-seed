---
source: agent-generated
origin_session: manual
created: 2026-03-21
type: build-plan
category: build
status: complete
next_action: All planned phases complete.
last_verified: 2026-03-21
trust: medium
---

# MCP Knowledge Base Reorganization Tools

## Scope

Add MCP tools to make compositional reorganization of the knowledge base easier. Friction identified during the 2026-03-21 ai-frontier → ai/frontier move: discovering references required grep; updating references was manual search-replace; validating links post-move was ad hoc. This plan introduces reference discovery, link validation, and governed reorganization with reference updates.

## Problem statement

**No reference discovery.** When moving or renaming a path, agents must grep for the old identifier across the repo. Markdown links, frontmatter `related:` and `domain:`, and include paths are not surfaced by a dedicated tool. Fuzzy variants (e.g. `ai_frontier` vs `ai-frontier`) are easy to miss.

**No link validation.** After reorganization, broken links are discovered when someone follows them. There is no pre- or post-move validation that internal references resolve.

**Reorganization is manual and error-prone.** Moving a subtree requires: (1) move files, (2) find all references, (3) update each reference with correct relative/absolute paths, (4) update SUMMARY sections, (5) update frontmatter. Steps 2–4 are brittle and easy to omit.

**No impact preview.** Agents cannot ask "what would be affected if I moved X to Y?" before committing to a reorganization.

---

## Phases

### Phase 1 — Reference discovery (`memory_find_references`)

*Goal: one tool to find every reference to a path or identifier.*

**1.1 Define reference extraction contract**

Document the reference types to extract:
- **Markdown links:** `[text](path)` and `[text](path "title")` — extract path, resolve relative to containing file
- **Frontmatter:** `related:`, `domain:`, `tags:` (when value is a path), any `*_path` or `*_file` keys
- **Markdown references:** `<!-- section: id -->`, `[[wikilink]]` if ever adopted
- **Explicit path patterns:** `knowledge/ai-frontier/`, `ai-frontier/alignment/`, `../../ai-frontier/`

Support optional `include_body: bool` to also scan body text for path-like strings (e.g. "see ai-frontier/epistemology/"), with caveat that body scans are noisier.

**1.2 Implement reference extractor**

Create internal module (e.g. `engram_mcp/agent_memory_mcp/tools/reference_extractor.py`) that:
- Walks governed content paths (identity/, knowledge/, plans/, skills/, meta/ where appropriate)
- Parses frontmatter and markdown per file
- Returns structured list: `{ from_path, ref_type, ref_value, line_range?, snippet? }`
- Ignores binary files, `__pycache__`, `.git`, etc.

**1.3 Implement `memory_find_references`**

Tool signature:
```
memory_find_references(path: str, include_body: bool = False) -> str
```

- `path`: The path or path fragment to search for (e.g. `knowledge/ai/frontier`, `ai-frontier`, `ai-frontier/alignment`)
- Returns JSON: `{ query: str, matches: [{ from_path, ref_type, ref_value, snippet? }], total: int }`
- Path matching: exact substring, or normalized (slashes, trailing-slash-insensitive) per config

**1.4 Add tests**

- Reference to path in markdown link → found
- Reference in frontmatter `related:` → found
- Reference in frontmatter `domain:` → found
- Path in body text with `include_body=True` → found
- No false positives from similar strings (e.g. "see ai-frontier in the abstract" when searching for a different path)
- Scope limited to governed paths; `HUMANS/docs/` excluded if desired

**Checklist:**
- [x] 1.1 Document reference extraction contract (types, paths, edge cases)
- [x] 1.2 Implement reference extractor module
- [x] 1.3 Implement and register `memory_find_references`
- [x] 1.4 Add unit and integration tests

---

### Phase 2 — Link validation (`memory_validate_links`)

*Goal: detect broken internal references before or after reorganization.*

**2.1 Define validation scope**

- **In-scope paths:** identity/, knowledge/, plans/, skills/, meta/ (configurable)
- **Link types:** markdown `[text](path)`, frontmatter path values
- **Resolution rules:** Relative links resolved from containing file; repo-root-relative paths (e.g. `knowledge/ai/`) resolved from repo root; anchor-only `#section` validated against headings in same file

**2.2 Implement link validator**

- For each in-scope file, extract all link targets
- Resolve each target to a filesystem path (or same-file anchor)
- Check existence; collect `{ from_path, target, resolved_path, status: "ok"|"broken"|"ambiguous" }`
- Optional: validate that target file has expected structure (e.g. frontmatter present)

**2.3 Implement `memory_validate_links`**

Tool signature:
```
memory_validate_links(path: str = "") -> str
```

- `path`: Optional. If provided, validate only files under this path; otherwise validate all in-scope content
- Returns JSON: `{ scope: str, ok_count: int, broken: [{ from_path, target, reason }], ambiguous?: [...] }`
- Keep output compact; truncate broken list if large, with `truncated: true` and `total_broken: N`

**2.4 Add tests**

- Valid internal link → ok
- Link to moved/deleted file → broken
- Malformed relative path → broken or ambiguous
- Cross-folder relative path correctness

**Checklist:**
- [x] 2.1 Document validation scope and resolution rules
- [x] 2.2 Implement link validator module
- [x] 2.3 Implement and register `memory_validate_links`
- [x] 2.4 Add tests

---

### Phase 3 — Reorganization preview (`memory_reorganize_preview`)

*Goal: show impact of a move before executing.*

**3.1 Define preview contract**

Output schema:
```json
{
  "source": "knowledge/ai-frontier",
  "dest": "knowledge/ai/frontier",
  "files_to_move": ["path1", "path2", ...],
  "files_with_references": [
    { "path": "...", "refs": [{ "type": "markdown_link", "old": "...", "new": "..." }] }
  ],
  "summary_updates": ["knowledge/SUMMARY.md", "knowledge/ai/SUMMARY.md?"],
  "warnings": ["..."]
}
```

**3.2 Implement preview logic**

- Given `source` and `dest`, enumerate files that would move (single file or subtree)
- Call reference extractor for `source` path; for each match, compute the new reference value after move
- Determine which SUMMARY files need section updates (reuse promotion-tool logic)
- Emit warnings: e.g. section id changes, path length, conflicts with existing dest

**3.3 Implement `memory_reorganize_preview`**

Tool signature:
```
memory_reorganize_preview(source: str, dest: str) -> str
```

- Read-only; no filesystem writes
- Validates `source` exists, `dest` parent exists
- Returns structured preview JSON

**3.4 Add tests**

- Subtree move preview includes all descendants
- Reference updates correctly computed for relative and absolute paths
- Warnings when dest already has conflicting content

**Checklist:**
- [x] 3.1 Define preview output schema
- [x] 3.2 Implement preview logic (reuse reference extractor)
- [x] 3.3 Implement and register `memory_reorganize_preview`
- [x] 3.4 Add tests

---

### Phase 4 — Governed reorganization (`memory_reorganize_path`)

*Goal: move a path and update all references in one governed operation.*

**4.1 Define governance**

- **Change class:** proposed (user awareness before write)
- **Preview required:** yes; tool must support `dry_run: bool`
- **Protected paths:** no moves into or out of protected meta/ surfaces without higher approval
- **Commit model:** single atomic commit: file moves + reference edits + SUMMARY updates

**4.2 Implement reorganization executor**

- Perform moves (file or directory) with `Path.rename` or shutil equivalent
- For each file with references (from preview), apply edits:
  - Markdown: update link targets in body
  - Frontmatter: update path-valued fields
  - Preserve formatting and escape sequences
- Update SUMMARY files (section links, paths in lists)
- Single commit with message: `[reorganize] source -> dest (N files, M reference updates)`

**4.3 Implement `memory_reorganize_path`**

Tool signature:
```
memory_reorganize_path(source: str, dest: str, dry_run: bool = True) -> str
```

- `dry_run=True`: return same structure as `memory_reorganize_preview` plus `would_commit: true`
- `dry_run=False`: execute move and reference updates; return `{ result, commit_sha, files_changed, refs_updated }`
- Reuse preview logic for planning; add execution step

**4.4 Edge cases and safeguards**

- Abort if `dest` already exists and would overwrite
- Abort if reference update would produce invalid markdown or frontmatter
- Preserve line endings and leading/trailing newlines
- Handle circular references (none expected; document assumption)

**4.5 Add tests**

- Dry run produces correct plan
- Execute produces correct move and reference updates
- SUMMARY updates applied correctly
- Rollback or no-op on validation failure

**Checklist:**
- [x] 4.1 Document governance (change class, preview, protection)
- [x] 4.2 Implement reorganization executor
- [x] 4.3 Implement and register `memory_reorganize_path`
- [x] 4.4 Handle edge cases and add safeguards
- [x] 4.5 Add tests (dry run, execute, failure modes)

---

### Phase 5 — Structure suggestions (optional, `memory_suggest_structure`)

*Goal: suggest compositional improvements based on current layout and conventions.*

**5.1 Define suggestion heuristics**

- **Orphan topics:** Folder with few files and no incoming links from SUMMARY → consider merging
- **Deep nesting:** Path like `a/b/c/d/e` → consider flattening or intermediate summaries
- **Naming inconsistency:** `ai-frontier` vs `ai/frontier` style → suggest alignment with sibling folders
- **Cross-reference clusters:** Files that heavily reference each other → consider co-location
- **SUMMARY drift:** Files on disk not listed in SUMMARY → suggest summary update

**5.2 Implement suggestion engine**

- Configurable heuristics; each produces `{ suggestion, rationale, confidence?, affected_paths }`
- Do not auto-apply; suggestions are advisory only

**5.3 Implement `memory_suggest_structure`**

Tool signature:
```
memory_suggest_structure(folder_path: str = "", heuristics: list[str] = []) -> str
```

- `folder_path`: Optional. If provided, limit analysis to subtree
- `heuristics`: Optional. If provided, run only named heuristics; otherwise run all
- Returns: `{ suggestions: [...], scope: str }`

**5.4 Add tests**

- Orphan detection produces expected suggestions
- Naming inconsistency detected when patterns exist
- No suggestions when structure is already consistent

**Checklist:**
- [x] 5.1 Define and document suggestion heuristics
- [x] 5.2 Implement suggestion engine (best-effort; may be iterative)
- [x] 5.3 Implement and register `memory_suggest_structure`
- [x] 5.4 Add tests

---

## Success criteria

- **Phase 1:** `memory_find_references("ai-frontier")` returns all files referencing that path across links and frontmatter.
- **Phase 2:** `memory_validate_links()` reports broken links; zero false positives for valid internal refs.
- **Phase 3:** `memory_reorganize_preview(source, dest)` accurately lists files to move and references to update.
- **Phase 4:** `memory_reorganize_path(source, dest, dry_run=False)` performs the move and reference updates in one committed operation; `memory_validate_links()` passes after.
- **Phase 5 (optional):** `memory_suggest_structure()` returns at least one actionable suggestion for a known structural inconsistency.

---

## Implementation notes

- **Shared code:** Phases 1–4 share the reference extractor; Phase 3 and 4 share preview logic. Implement extractor first, then validation, then preview, then execution.
- **Path policy:** Reuse `path_policy.py` and governance from existing write tools. Reorganization touches multiple governed paths; ensure change-class checks apply.
- **Capabilities manifest:** Register new tools in `agent-memory-capabilities.toml` with correct change_class and preview availability.
- **memory_route_intent:** Extend routing to recognize intents like "move X to Y", "reorganize ai-frontier", "find references to path" → recommend appropriate tool.

---

## References

- `plans/mcp-agent-discoverability-guidance.md` — tool description patterns, routing
- `plans/mcp-agent-friendliness-improvements.md` — preview contract, governed write patterns
- `plans/mcp-unverified-review-workflow-improvements.md` — subtree promotion, summary updates
- `engram_mcp/agent_memory_mcp/tools/read_tools.py` — existing read tools, path handling
- `engram_mcp/agent_memory_mcp/core/path_policy.py` — path validation, governance
- `HUMANS/tooling/agent-memory-capabilities.toml` — capability manifest, tool registration
