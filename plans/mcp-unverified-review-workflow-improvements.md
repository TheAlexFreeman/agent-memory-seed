---
created: '2026-03-20'
last_verified: '2026-03-20'
next_action: 'Implement Phase 7: memory_mark_reviewed tracking tool.'
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: active
title: MCP Unverified Review Workflow Improvements
trust: medium
type: implementation-plan
---


## Goals

Eliminate the 7 operational friction points identified during the 2026-03-20 unverified mathematics promotion session, in which 35 files were promoted from `knowledge/_unverified/mathematics/` to `knowledge/mathematics/`. The session required 35 sequential `promote_knowledge` calls, 35 individual `read_file` calls with Python extraction workarounds, and a manual SUMMARY.md repair at the end despite 35 promotion warnings. Total friction made a routine curation task unnecessarily tedious.

This plan is explicitly higher-priority than:
- **mcp-curation-and-analytics-tools.md** — partially overlaps (batch promotion), treat Phase 4 of that plan as superseded by Phase 5 here if not yet implemented.
- **mcp-read-tools-improvements.md** — status: complete; does NOT address inline content return.
- **mcp-write-and-crosscutting-improvements.md** — status: complete; does NOT address SUMMARY.md auto-update.

---

## Problem Statement

**Gap 1 — `memory_read_file` returns a temp file path instead of inline content.**
During the 35-file review every single read required a Python extraction script of the form `python -c "import json; ..."` to retrieve the actual content. For files under ~20 KB this is pure overhead; the content should be returned directly in the JSON response. Cost: ~1 extra tool call per file reviewed.

**Gap 2 — `memory_promote_knowledge` does not update SUMMARY.md.**
All 35 promotion calls emitted the warning: `Section '<!-- section: mathematics -->' not found in knowledge/SUMMARY.md`. The section had to be hand-crafted and committed afterward. Cost: 1 manual repair commit per promotion session + 35 noise warnings.

**Gap 3 — `memory_list_folder` has no content preview option.**
To assess 35 files, 35 individual `read_file` calls were required. A `preview_chars` parameter returning the first N characters + parsed frontmatter per entry would collapse an entire review session into a single list call. Cost: N-1 extra tool calls per review session (N = file count).

**Gap 4 — No purpose-built `memory_review_unverified` digest tool.**
There is no tool designed for the review→decide→promote workflow. An agent must manually enumerate, read, assess, and decide for each file. A digest tool that surfaces filename, dates, source, trust, and a content extract in one response would make the step trivial. Complements Gap 3 but easier to add independently.

**Gap 5 — No subtree promotion shorthand.**
Promoting a folder of 35 files required 35 sequential `promote_knowledge` calls. Even `promote_knowledge_batch` (which was not discovered — see Gap 6) accepts a flat list, not a folder path. A `promote_knowledge_subtree` tool would handle entire topic trees atomically. Cost: N-1 extra tool calls per bulk promotion.

**Gap 6 — `promote_knowledge_batch` is not discoverable.**
The batch promotion tool exists but was never surfaced during the workflow. The single-file tool's description contains no "see also" reference, and `meta/quick-reference.md` does not mention the batch variant. Result: 35 sequential calls instead of 1. Cost: N-1 extra tool calls per session this happens.

**Gap 7 — No review-session tracking primitive.**
Multi-session review workflows (read on day 1, promote on day 2) have no lightweight record-keeping. There is no `memory_mark_reviewed` tool to log a verdict without committing a promotion. Agents must either promote immediately or lose review state between sessions.

---

## Phases

### Phase 1 — `memory_read_file` inline content return

*Addresses Gap 1. Highest leverage: required by all downstream review workflows.*

**1.1 Modify `memory_read_file` in `engram_mcp/agent_memory_mcp/tools/read_tools.py`**

When the file content is ≤ 20 000 bytes after reading, return it directly in the JSON response body under a `content` key rather than writing to a temp file. For files above the threshold, keep the current temp-file behavior and document the threshold in the response metadata.

New response shape (small files):
```json
{
  "path": "knowledge/mathematics/logic-foundations/godels-first-incompleteness.md",
  "size_bytes": 3241,
  "inline": true,
  "content": "---\ncreated: 2026-03-20\n..."
}
```

Large-file response (unchanged behavior, add `inline: false`):
```json
{
  "path": "...",
  "size_bytes": 87400,
  "inline": false,
  "temp_file": "/tmp/mcp_content_abc123.json"
}
```

**1.2 Update docstring** to document the `inline` field and the 20 000-byte threshold.

**1.3 Add unit test** in `engram_mcp/tests/` asserting that a small fixture file returns `inline: true` with `content` populated and no `temp_file` key.

Checklist:
- ☑ Identify the read-file handler in `engram_mcp/agent_memory_mcp/tools/read_tools.py`
- ☑ Add size check and conditional inline-vs-tempfile branch
- ☑ Update response serialization to include `inline` bool
- ☑ Update docstring / tool description
- ☑ Write unit test
- ☑ Manual smoke-test: call `memory_read_file` on a small file and confirm content is returned inline

---

### Phase 2 — SUMMARY.md auto-update on `memory_promote_knowledge`

*Addresses Gap 2. Eliminates post-promotion manual repair.*

**2.1 Add optional `summary_entry` parameter to `memory_promote_knowledge`**

```python
async def memory_promote_knowledge(
    source_path: str,
    trust_level: str = "medium",
    reason: str = "",
    summary_entry: str | None = None,   # NEW
) -> str
```

When `summary_entry` is provided:
1. Resolve the target folder's SUMMARY.md (e.g. `knowledge/mathematics/SUMMARY.md`).
2. Search for the `<!-- section: mathematics -->` marker. If found, insert `summary_entry` on the next line after the marker. If not found, append a stub section at the end of SUMMARY.md with the marker and `summary_entry`.
3. Stage and commit the SUMMARY.md change in the same commit as the file move, or as a follow-up commit with the message `[curation] Auto-update SUMMARY.md after promotion of {filename}`.

**2.2 Suppress the warning when `summary_entry` is not provided.**
The current warning `Section '<!-- section: X -->' not found in knowledge/SUMMARY.md` fires unconditionally. It should only fire if the caller has not opted into auto-update AND the section is absent. When auto-update is active, the warning is noise.

**2.3 Update docstring** to document `summary_entry`, the marker search/insert logic, and the two-commit behavior.

**2.4 Add test** asserting that promoting a file with `summary_entry="- [foo.md](foo.md) — Test entry"` results in the entry appearing in the target SUMMARY.md under the correct section marker.

Checklist:
- ☑ Add `summary_entry: str | None = None` param to `memory_promote_knowledge`
- ☑ Implement marker-search + insert / stub-create logic
- ☑ Adjust warning condition to only fire when auto-update is inactive and section absent
- ☑ Write test
- ☑ Smoke-test: promote a single file with a `summary_entry` and verify SUMMARY.md diff

---

### Phase 3 — `memory_list_folder` content preview option

*Addresses Gap 3. Collapses N `read_file` calls into 1 `list_folder` call.*

**3.1 Add `preview_chars` parameter to `memory_list_folder`**

```python
async def memory_list_folder(
    folder_path: str,
    recursive: bool = False,
    preview_chars: int = 0,     # NEW
) -> str
```

When `preview_chars > 0`, each file entry in the response includes:
- `frontmatter`: dict of parsed YAML frontmatter keys (created, trust, source, type, etc.)
- `preview`: first `preview_chars` characters of the file body (after frontmatter block)

Response entry shape with preview:
```json
{
  "name": "godels-first-incompleteness.md",
  "path": "knowledge/mathematics/logic-foundations/godels-first-incompleteness.md",
  "size_bytes": 3241,
  "frontmatter": {"created": "2026-03-20", "trust": "high", "source": "agent-generated"},
  "preview": "Gödel's first incompleteness theorem states that any consistent formal system..."
}
```

**3.2 Performance note:** Preview reads are done lazily (skip binary files; truncate at `preview_chars` without loading whole file into memory).

**3.3 Update docstring** to document `preview_chars` and the `frontmatter`/`preview` fields.

**3.4 Add test** asserting that `list_folder` with `preview_chars=100` returns entries with non-empty `preview` for markdown files and no `preview` key when `preview_chars=0`.

Checklist:
- ☑ Add `preview_chars: int = 0` param
- ☑ Implement frontmatter parse (reuse existing YAML parser if available)
- ☑ Implement body-preview truncation
- ☑ Update docstring
- ☑ Write test
- ☑ Smoke-test: `list_folder("knowledge/_unverified", preview_chars=200)` and confirm previews appear

---

### Phase 4 — `memory_review_unverified` digest tool

*Addresses Gap 4. Purpose-built review→decide→promote workflow entry point.*

**4.1 Implement new Tier 1 tool `memory_review_unverified`**

```python
async def memory_review_unverified(
    folder_path: str = "knowledge/_unverified",
    max_extract_words: int = 150,
    include_expired: bool = True,
) -> str
```

Returns a structured digest for every file under `folder_path`. Each entry contains:
- `path`: repo-relative path
- `created`: from frontmatter
- `source`: from frontmatter
- `trust`: from frontmatter
- `days_old`: days since `created`
- `expired`: bool (days_old > threshold per trust level per curation-policy)
- `extract`: first `max_extract_words` words of body content

The response groups files by subfolder and includes a header summary: total file count, count expired, count by trust level.

**4.2 Curation policy integration:** Read expiry thresholds from `meta/curation-policy.md` at call time (or from a hardcoded constant with a comment pointing to the policy). Do not hardcode 120 days without a named constant `TRUST_LOW_EXPIRY_DAYS = 120`.

**4.3 Add test** asserting correct grouping, expiry calculation, and word-count truncation of extract.

Checklist:
- ☑ Register new tool in tool manifest / `__init__.py`
- ☑ Implement folder walk + frontmatter parse + extract generation
- ☑ Implement expiry calculation using policy constants
- ☑ Implement grouped response with summary header
- ☑ Write test
- ☑ Smoke-test on `knowledge/_unverified` (should now be empty for mathematics; test with another unverified folder)

---

### Phase 5 — `memory_promote_knowledge_subtree`

*Addresses Gap 5. Handles entire topic trees atomically.*

**5.1 Implement new Tier 1 tool `memory_promote_knowledge_subtree`**

```python
async def memory_promote_knowledge_subtree(
    source_folder: str,
    dest_folder: str,
    trust_level: str = "medium",
    reason: str = "",
    dry_run: bool = False,
) -> str
```

Behavior:
1. Walk `source_folder` recursively, collecting all `.md` files.
2. Run a pre-flight check: verify each file has required frontmatter fields (`created`, `source`, `trust`). Abort the entire operation (no partial moves) if any file fails.
3. If `dry_run=True`, return the list of files that would be moved without making changes.
4. Move all files from `source_folder/**` to `dest_folder/**` (preserving sub-path structure), update each file's `trust` frontmatter to `trust_level`, and commit as a single atomic git commit with the message `[curation] Promote subtree {source_folder} → {dest_folder} ({n} files, trust: {trust_level})`.
5. Auto-update `dest_folder/SUMMARY.md` with stub entries for all promoted files (reuse Phase 2 logic).

**5.2 Add test** asserting dry-run returns file list without committing, and that a real run produces a single commit containing all file moves.

Checklist:
- ☑ Register new tool
- ☑ Implement recursive walk + pre-flight check
- ☑ Implement atomic move + frontmatter patch
- ☑ Implement single-commit for all moves
- ☑ Wire in Phase 2 SUMMARY.md auto-update logic
- ☑ Implement `dry_run` mode
- ☑ Write test
- ☑ Smoke-test: dry-run on a folder with 3+ files and verify no git changes

---

### Phase 6 — `promote_knowledge_batch` discoverability

*Addresses Gap 6. Zero-code improvement; pure documentation.*

**6.1 Add "see also" to `memory_promote_knowledge` docstring**

Append to the single-file tool's description:
> See also: `memory_promote_knowledge_batch` to promote multiple files in one call, and `memory_promote_knowledge_subtree` (Phase 5 of mcp-unverified-review-workflow-improvements plan) to promote an entire folder tree.

**6.2 Update `meta/quick-reference.md`**

Under the "Curation operations" section, add a row for `memory_promote_knowledge_batch` and `memory_promote_knowledge_subtree` with a one-line description and example call each.

**6.3 Update `plans/SUMMARY.md`** entry for this plan once Phase 5 is complete to note that both batch tools are now documented.

Checklist:
- ☑ Edit `memory_promote_knowledge` docstring to add "see also" block
- ☑ Edit `meta/quick-reference.md` curation section
- ☑ Commit as `[docs] Improve discoverability of batch promotion tools`
- ☑ Verify the "see also" text appears in the MCP tool description surface (test via tool introspection)

---

### Phase 7 — `memory_mark_reviewed` tracking tool

*Addresses Gap 7. Enables multi-session review workflows.*

**7.1 Implement new Tier 1 tool `memory_mark_reviewed`**

```python
async def memory_mark_reviewed(
    path: str,
    verdict: str,           # "approve" | "reject" | "defer"
    reviewer_notes: str = "",
    session_id: str = "",
) -> str
```

Appends a JSON record to `knowledge/_unverified/REVIEW_LOG.jsonl`:
```json
{
  "path": "knowledge/_unverified/mathematics/logic-foundations/foo.md",
  "verdict": "approve",
  "reviewer_notes": "Gödel statement is accurate; sources consistent with SEP.",
  "session_id": "chats/2026/03/20/chat-003",
  "timestamp": "2026-03-20T14:32:00Z",
  "reviewed_by": "agent"
}
```

Verdicts:
- `"approve"` — file is ready to promote; the caller should follow up with `promote_knowledge` or `promote_knowledge_batch`.
- `"reject"` — file should be deleted or archived; the caller should follow up with `memory_archive_knowledge`.
- `"defer"` — needs more time; record the note for the next session.

**7.2 Implement `memory_list_pending_reviews`** (companion read tool):

```python
async def memory_list_pending_reviews(
    folder_path: str = "knowledge/_unverified",
) -> str
```

Reads `REVIEW_LOG.jsonl`, groups by verdict, and returns:
- Files with `"approve"` not yet promoted (still exist in `_unverified`)
- Files with `"defer"` (still exist in `_unverified`)
- Files with `"reject"` not yet archived/deleted

**7.3 Add `REVIEW_LOG.jsonl` to `.gitignore`** of the _unverified folder, or include it in commits — decide and document the policy in `meta/curation-policy.md`.

**7.4 Add tests** for append behavior, idempotent re-marking (last verdict wins), and list-pending grouping.

Checklist:
- ☐ Register `memory_mark_reviewed` tool
- ☐ Implement JSONL append with timestamp injection
- ☐ Register `memory_list_pending_reviews` companion tool
- ☐ Implement JSONL read + grouping logic + existence check
- ☐ Decide and document REVIEW_LOG.jsonl commit policy
- ☐ Write tests
- ☐ Smoke-test: mark 3 files with different verdicts, call list_pending, verify groupings

---

## Implementation Order and Dependencies

```
Phase 1 (read_file inline)          ← no dependencies; start here
Phase 6 (discoverability)           ← no dependencies; can parallelize with Phase 1
Phase 2 (SUMMARY auto-update)       ← no dependencies; can parallelize
Phase 3 (list_folder preview)       ← depends on Phase 1 patterns (same read logic)
Phase 4 (review_unverified digest)  ← depends on Phase 3 (reuses preview logic)
Phase 5 (promote subtree)           ← depends on Phase 2 (reuses SUMMARY auto-update)
Phase 7 (mark_reviewed)             ← depends on Phase 4 (review workflow context)
```

Recommended batches:
- **Batch A:** Phases 1, 2, 6 in parallel (independent, high-value)
- **Batch B:** Phases 3, 4 (preview + digest; Phase 4 reuses Phase 3 logic)
- **Batch C:** Phases 5, 7 (bulk-move + tracking; Phase 5 reuses Phase 2)

---

## Test Plan Summary

| Phase | Test type | Key assertion |
|-------|-----------|---------------|
| 1 | Unit | Small file returns `inline: true` with `content` key |
| 2 | Unit | Promotion with `summary_entry` inserts under correct `<!-- section -->` |
| 3 | Unit | `preview_chars=100` returns truncated body + parsed frontmatter per entry |
| 4 | Unit | Digest groups by subfolder, expiry calc correct, extract word-count respected |
| 5 | Unit | Dry-run = no commits; real run = single atomic commit |
| 6 | Manual | Tool introspection confirms "see also" text visible in description |
| 7 | Unit | JSONL append, last-verdict-wins re-mark, list-pending grouping |