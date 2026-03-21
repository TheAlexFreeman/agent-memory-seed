---
created: 2026-03-20
last_verified: 2026-03-20
next_action: "Human review of the completed curation and analytics tool suite."
origin_session: chats/2026/03/20/chat-002
source: agent-generated
status: complete
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: MCP Curation, Validation, and Analytics Tools

## Goals

Add five tools that close operational gaps in the memory system's curation workflow, structural validation, and retrieval analytics. These tools were identified during a hands-on quarantine-to-promotion session (2026-03-20) where 4 MCP knowledge files were promoted manually, exposing friction that the current tool surface does not address.

This plan is complementary to:
- **mcp-read-tools-improvements.md** — already plans `memory_session_health_check` (Phase 2), which this plan does NOT duplicate.
- **mcp-write-and-crosscutting-improvements.md** — plans `memory_update_frontmatter_bulk` (Tier 2 raw), which is distinct from the Tier 1 semantic batch promotion here.
- **access-log-tooling-improvements.md** — plans schema enrichment and batch logging, which this plan's analytics tool will consume downstream.

---

## Problem statement

**Gap A — Batch promotion is the most common curation operation but has no tool.** Promoting a folder of unverified files requires N calls to `memory_promote_knowledge` (one per file), plus manual SUMMARY.md edits for the target subfolder, plus manual cleanup of the source SUMMARY.md section. The 4-file MCP promotion took 8+ individual operations. A folder of 14 Django files would require 30+.

**Gap B — Markdown cross-references silently drift.** Files get moved, promoted, archived, or deleted. The SUMMARY.md entries, relative links, and plan references that point at them are not validated by `memory_validate`. Broken links accumulate without detection until an agent follows one and gets a `NotFoundError`.

**Gap C — SUMMARY.md authoring is manual boilerplate.** After promoting or reorganizing files, regenerating a folder's SUMMARY.md requires reading every file's frontmatter and first paragraph, then composing a formatted summary within the 200-800 word budget. This is pure mechanical work that should be automatable.

**Gap D — ACCESS analytics per the curation policy have no tool surface.** The curation policy defines four retrieval-quality categories (core memory, near-miss, hidden gem, retirement candidate) based on access frequency × helpfulness. No tool surfaces these classifications. `memory_get_maturity_signals` reports aggregate counts; `memory_run_aggregation` does clustering. Neither maps files to the curation policy's own action categories.

**Gap E — Branch divergence is invisible.** With `core` as the default branch and `live-test--maiden` as the working branch, there's no tool to show what has changed. `memory_diff` shows the working tree; `memory_git_log` shows commits on the current branch. Neither shows the divergence from the default branch, which matters for merge planning.

---

## Phases

### Phase 1 — `memory_promote_knowledge_batch` (Tier 1 semantic)

The highest-value tool. Addresses Gap A.

**1.1 Implement in `knowledge_tools.py`**

New Tier 1 tool. Signature:
```python
async def memory_promote_knowledge_batch(
    source_paths: str,
    trust_level: str = "medium",
    target_folder: str | None = None,
) -> str
```

`source_paths` is a JSON array of repo-relative paths under `knowledge/_unverified/`, OR a single folder path (e.g., `"knowledge/_unverified/mcp/"`) which expands to all `.md` files in that folder (excluding SUMMARY.md).

`target_folder` is the destination folder under `knowledge/`. If `None`, infer from source paths by stripping the `_unverified/` segment (e.g., `knowledge/_unverified/mcp/` → `knowledge/tooling/mcp/`... but this default is fragile, so require it when source paths span multiple target folders).

For each file:
1. Validate source path is under `knowledge/_unverified/`
2. Read file, update frontmatter: `trust` → `trust_level`, `last_verified` → today
3. Move to target via `repo.mv()`
4. Remove entry from source folder's SUMMARY.md section

After all files:
5. Remove the batch's section from `knowledge/_unverified/SUMMARY.md` if all files in that section were promoted
6. Add a section entry to the target folder's SUMMARY.md (or to `knowledge/SUMMARY.md` if the target has no sub-SUMMARY)
7. Commit atomically as `[curation] Batch promote {n} files to {target_folder} (trust: {trust_level})`

Return `MemoryWriteResult` with `files_changed`, `commit_sha`, and `new_state`:
```json
{
  "promoted_count": 4,
  "target_folder": "knowledge/tooling/mcp",
  "trust": "medium",
  "promoted_files": ["mcp-protocol-overview.md", "..."],
  "summary_updates": ["knowledge/_unverified/SUMMARY.md", "knowledge/SUMMARY.md"]
}
```

**1.2 Validate-before-stage discipline**

Before moving any file, validate the entire batch:
- All source paths exist
- All source paths are under `knowledge/_unverified/`
- `trust_level` is `"medium"` or `"high"`
- `target_folder` resolves under `knowledge/` but NOT under `knowledge/_unverified/`
- No target path collisions (two source files resolving to the same target)

If any validation fails, reject the entire batch before staging. Return a clear error listing which paths failed and why.

**1.3 Batch size limit**

Cap at 50 files per call. Reject larger batches with `ValidationError`. This prevents runaway model-generated promotions.

**1.4 Register and update capabilities**

Register in `semantic/__init__.py` via `knowledge_tools`. Add to `semantic_extensions` in capabilities TOML.

---

### Phase 2 — `memory_check_cross_references` (Tier 0 read)

Structural integrity validator. Addresses Gap B.

**2.1 Implement in `read_tools.py`**

New Tier 0 tool. Signature:
```python
async def memory_check_cross_references(
    path: str = ".",
    check_summaries: bool = True,
    check_links: bool = True,
) -> str
```

Scans all `.md` files under `path`. Returns structured JSON:
```json
{
  "broken_links": [
    {"file": "plans/SUMMARY.md", "line": 42, "target": "plans/old-plan.md", "reason": "target not found"}
  ],
  "orphaned_files": [
    {"file": "knowledge/tooling/mcp/mcp-protocol-overview.md", "folder_summary": "knowledge/tooling/mcp/SUMMARY.md", "reason": "not mentioned in SUMMARY.md"}
  ],
  "stale_summary_entries": [
    {"summary": "knowledge/SUMMARY.md", "entry": "old-file.md", "reason": "referenced file does not exist"}
  ],
  "stats": {
    "files_scanned": 120,
    "links_checked": 340,
    "summaries_checked": 8,
    "issues_found": 3
  }
}
```

**Link checking logic:**
- Extract all `[text](relative/path)` patterns from Markdown
- Resolve against the containing file's directory
- Skip external URLs (http://, https://)
- Skip anchor-only links (#section)
- Report targets that don't exist on disk

**SUMMARY orphan checking logic:**
- For each folder containing a SUMMARY.md, list all `.md` files in that folder
- Check that each file (except SUMMARY.md itself) is mentioned in the SUMMARY.md
- Report files not mentioned as orphans

**2.2 Performance guard**

Use `git ls-files` to enumerate tracked files rather than walking the filesystem. Cap the scan to 500 files; if exceeded, require `path` to narrow scope.

**2.3 Register in read tools**

Add to `read_tools.register()`. Add `readOnlyHint=True` annotation.

---

### Phase 3 — `memory_generate_summary` (Tier 0 read with preview)

SUMMARY.md scaffolding. Addresses Gap C.

**3.1 Implement in `read_tools.py`**

New Tier 0 tool (read-only: returns a draft, does not write). Signature:
```python
async def memory_generate_summary(
    path: str,
    style: str = "standard",
) -> str
```

`path` is a folder path (e.g., `"knowledge/tooling/mcp"`).

For each `.md` file in the folder (excluding SUMMARY.md):
1. Parse frontmatter (trust, source, created, last_verified)
2. Extract the first `#` heading as the title
3. Extract the first paragraph as the description
4. Format as a SUMMARY.md entry: `- **filename.md** — {description}`

Compose a complete SUMMARY.md draft:
- `# {Folder Name} — Summary` heading
- Metadata line: trust, source, promoted/created date
- File entries grouped logically (by subfolder if any exist)
- Word count annotation (target: 200-800 words per curation policy)

`style` options:
- `"standard"` — bulleted list with one-line descriptions
- `"detailed"` — bulleted list with 2-3 sentence descriptions

Return the draft as a string (not JSON), ready to paste into `memory_write`. Include a metadata comment at the top: `<!-- Generated by memory_generate_summary on {date}. Review before committing. -->`

**3.2 Subfolder awareness**

If the folder contains subfolders with their own SUMMARY.md files, reference them by link rather than inlining their contents: `- **subfolder/** — See [subfolder/SUMMARY.md](subfolder/SUMMARY.md)`

**3.3 Register in read tools**

Add to `read_tools.register()`. Add `readOnlyHint=True` annotation.

---

### Phase 4 — `memory_access_analytics` (Tier 0 read)

Curation-policy-driven retrieval insights. Addresses Gap D.

**4.1 Implement in `read_tools.py`**

New Tier 0 tool. Signature:
```python
async def memory_access_analytics(
    folders: str | None = None,
    window_days: int = 90,
    top_n: int = 10,
) -> str
```

`folders` is a comma-separated list of folder paths to analyze (default: all governed folders). `window_days` limits analysis to entries within this window.

Reads hot `ACCESS.jsonl` files (and archive segments within the window). For each file that appears:
- Compute `access_count` and `mean_helpfulness`
- Classify into the four curation-policy categories:

| Category | Criteria | Action |
|---|---|---|
| **Core memory** | access ≥ 5, mean helpfulness ≥ 0.5 | Enrich cross-refs, strengthen SUMMARY |
| **Near-miss** | access ≥ 5, mean helpfulness 0.2–0.4 | Split or retitle |
| **False-positive attractor** | access ≥ 5, mean helpfulness 0.0–0.1 | Retag or retitle |
| **Retirement candidate** | access ≥ 3, mean helpfulness ≤ 0.3 | Flag for review |
| **Hidden gem** | access < 3, mean helpfulness ≥ 0.5 (when found) | Improve SUMMARY placement |

Return structured JSON:
```json
{
  "window": {"start": "2025-12-21", "end": "2026-03-20", "days": 90},
  "total_entries": 245,
  "unique_files": 67,
  "categories": {
    "core_memory": [{"file": "...", "access_count": 12, "mean_helpfulness": 0.8}],
    "near_miss": [],
    "false_positive_attractor": [],
    "retirement_candidate": [],
    "hidden_gem": []
  },
  "top_accessed": [{"file": "...", "count": 15}],
  "least_accessed": [{"file": "...", "count": 1, "last_access": "2026-01-05"}],
  "suggested_actions": [
    {"file": "...", "action": "enrich_cross_refs", "reason": "Core memory: 12 accesses, 0.8 mean helpfulness"},
    {"file": "...", "action": "flag_for_review", "reason": "Retirement candidate: 4 accesses, 0.2 mean helpfulness"}
  ]
}
```

**4.2 Threshold alignment**

Read category thresholds from `meta/curation-policy.md` comments or hardcode the values from the current policy (5+ retrievals for core/near-miss/attractor, 3+ for retirement). Document which thresholds are used and that they match the curation policy.

**4.3 Register in read tools**

Add to `read_tools.register()`. Add `readOnlyHint=True` annotation.

---

### Phase 5 — `memory_diff_branch` (Tier 0 read)

Branch divergence view. Addresses Gap E.

**5.1 Implement in `read_tools.py`**

New Tier 0 tool. Signature:
```python
async def memory_diff_branch(
    base: str = "core",
) -> str
```

`base` is the branch to compare against (default: the repo's default branch, read from `agent-bootstrap.toml` if available, otherwise `"core"`).

Runs `git log {base}..HEAD --oneline` and `git diff --stat {base}...HEAD` with `stdin=subprocess.DEVNULL`.

Return structured JSON:
```json
{
  "base_branch": "core",
  "current_branch": "live-test--maiden",
  "commits_ahead": 47,
  "files_changed": 123,
  "insertions": 4500,
  "deletions": 800,
  "by_category": {
    "knowledge": {"added": 45, "modified": 12, "deleted": 2},
    "plans": {"added": 8, "modified": 15, "deleted": 0},
    "identity": {"added": 0, "modified": 3, "deleted": 0},
    "meta": {"added": 1, "modified": 8, "deleted": 0},
    "engram_mcp": {"added": 12, "modified": 20, "deleted": 3},
    "other": {"added": 5, "modified": 7, "deleted": 1}
  },
  "recent_commits": [
    {"sha": "abc1234", "message": "[curation] Promote MCP knowledge files", "date": "2026-03-20"}
  ]
}
```

`by_category` groups files by top-level directory into the memory system's natural categories. `recent_commits` shows the last 10 commits on the current branch not on base.

**5.2 Handle missing base branch**

If the base branch doesn't exist locally (common after a fresh clone without `--single-branch`), attempt `git fetch origin {base}` first. If that also fails, return a clear error rather than a git traceback.

**5.3 Register in read tools**

Add to `read_tools.register()`. Add `readOnlyHint=True` annotation.

---

### Phase 6 — Tests and documentation

**6.1 Tests for `memory_promote_knowledge_batch`**
- Single-file batch: equivalent to existing `memory_promote_knowledge`
- Multi-file batch: all files moved, single commit produced
- Folder path expansion: `knowledge/_unverified/mcp/` expands to all `.md` files
- Validation failure: one bad path rejects entire batch
- Batch > 50: rejected with ValidationError
- SUMMARY updates: source entry removed, target entry added

**6.2 Tests for `memory_check_cross_references`**
- Broken link detected: `[text](nonexistent.md)` flagged
- External URLs skipped: `[text](https://...)` not flagged
- Orphaned file detected: file exists but not in SUMMARY.md
- Clean folder: zero issues returned

**6.3 Tests for `memory_generate_summary`**
- Generates valid Markdown with correct file entries
- Word count within 200-800 range for typical folders
- Subfolder references use link format, not inline

**6.4 Tests for `memory_access_analytics`**
- Core memory classification: high access + high helpfulness
- Retirement candidate classification: moderate access + low helpfulness
- Hidden gem: low access + high helpfulness
- Empty ACCESS log: returns zero entries gracefully

**6.5 Tests for `memory_diff_branch`**
- Returns commit count and file stats
- Category grouping correct for known file paths
- Missing base branch: clear error message

**6.6 Capabilities TOML updates**
- Add all 5 new tools to appropriate lists (`semantic_extensions` for batch promote, `read_support` for the four Tier 0 tools)
- Add `[operations.XXX]` tables for each

---

## Progress tracking

- [x] 1.1 Implement `memory_promote_knowledge_batch` in `knowledge_tools.py`
- [x] 1.2 Validate-before-stage discipline
- [x] 1.3 Batch size limit (50 files)
- [x] 1.4 Register and update capabilities
- [x] 2.1 Implement `memory_check_cross_references` in `read_tools.py`
- [x] 2.2 Performance guard (git ls-files, 500-file cap)
- [x] 2.3 Register in read tools
- [x] 3.1 Implement `memory_generate_summary` in `read_tools.py`
- [x] 3.2 Subfolder awareness
- [x] 3.3 Register in read tools
- [x] 4.1 Implement `memory_access_analytics` in `read_tools.py`
- [x] 4.2 Threshold alignment with curation policy
- [x] 4.3 Register in read tools
- [x] 5.1 Implement `memory_diff_branch` in `read_tools.py`
- [x] 5.2 Handle missing base branch
- [x] 5.3 Register in read tools
- [x] 6.1 Tests for batch promote
- [x] 6.2 Tests for cross-reference checker
- [x] 6.3 Tests for summary generator
- [x] 6.4 Tests for access analytics
- [x] 6.5 Tests for branch diff
- [x] 6.6 Capabilities TOML updates

**Progress:** 22/22 items complete

---

## Design constraints

- `memory_promote_knowledge_batch` is Tier 1 (auto-commit). It owns the full promotion workflow including SUMMARY updates. This distinguishes it from `memory_update_frontmatter_bulk` (Tier 2, raw frontmatter only).
- All four Tier 0 tools are `readOnlyHint=True`. They must never stage, write, or commit.
- `memory_generate_summary` returns a draft string, not JSON. The caller writes it via `memory_write` after review. This preserves human-in-the-loop for SUMMARY content.
- `memory_access_analytics` thresholds match the exact values in `meta/curation-policy.md` § "Access-driven curation" and § "Knowledge amplification." If those thresholds change, the tool must be updated.
- `memory_diff_branch` uses `stdin=subprocess.DEVNULL` for all git subprocesses (per the stdio transport lesson in `knowledge/tooling/codex-mcp-timeouts-git-stdin.md`).
- Phase 1 (batch promote) is the highest priority and can ship independently. Phases 2-5 are individually deployable and have no inter-dependencies.

## Relationship to existing plans

- **mcp-read-tools-improvements.md** Phase 2 (`memory_session_health_check`) was originally proposed here but is already fully planned there. Not duplicated.
- **mcp-write-and-crosscutting-improvements.md** Phase 1 (`memory_update_frontmatter_bulk`) is a Tier 2 raw tool for mass frontmatter edits. `memory_promote_knowledge_batch` is a Tier 1 semantic tool that happens to update frontmatter as part of a larger governed workflow. They address different use cases and can coexist.
- **access-log-tooling-improvements.md** Phase 2 adds `mode` and `task_id` fields to ACCESS entries. `memory_access_analytics` will benefit from these enrichments but does not depend on them — it works with the current schema.
- **production-readiness-roadmap.md** Phase 2 calls for versioned contracts. New tools added here should be tagged with contract version annotations when that versioning is implemented.
