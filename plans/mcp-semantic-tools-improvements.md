---
created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: expand memory_append_scratchpad to accept dated scratchpad slugs"
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: implementation-plan
---

# Implementation Plan: MCP Tier 1 Semantic Tool Improvements

## Goals

Close five gaps in the Tier 1 semantic tool suite (`semantic_tools.py`) identified during a full-stack MCP tooling review. These range from small ergonomic fixes (scratchpad target expansion) to major new tools (review queue lifecycle, skill file management, session record composite, aggregation runner). All belong in Tier 1 because they own system invariants and auto-commit.

---

## Problem statement

The Tier 1 semantic layer currently has five structural gaps:

**Gap 4 — `memory_append_scratchpad` cannot target dated files:** The tool only accepts `'user'` or `'current'` as targets, mapping to `scratchpad/USER.md` and `scratchpad/CURRENT.md`. The repo also contains dated session-scoped scratchpad files such as `scratchpad/2026-03-18-automation-backlog.md` that are created and used mid-session. Agents must fall back to raw `memory_write` for these, losing the append-only convention, the `---` separator insertion, and the `[scratchpad]` commit category hint.

**Gap 5 — Review queue is a one-way accumulator:** `memory_flag_for_review` writes entries to `meta/review-queue.md`, but there is no governed reverse path. After a periodic review, removing resolved items requires raw writes to `meta/` — which Tier 2 path policy explicitly blocks. The review queue accumulates without a tool-backed pop.

**Gap 6 — `skills/` is a write dead-end:** `skills/` is protected from all Tier 2 mutations. Unlike `identity/` which has `memory_update_identity_trait`, there is no Tier 1 equivalent for skill files. Creating or updating a skill file has no tool-backed path. Agents must ask the user to do it manually or use raw writes on an unprotected path and then `git mv`, which defeats the invariant system.

**Gap 7 — Session wrap-up produces two commits:** `memory_record_chat_summary` and `memory_record_reflection` are always called sequentially at session end, producing two `[chat]` commits with no causal link and no ACCESS log entry. A composite `memory_record_session` tool would atomically write both files, update `chats/SUMMARY.md`, and log one ACCESS entry — in a single commit.

**Gap 8 — Aggregation is fully manual despite being fully specified:** `meta/curation-algorithms.md` defines the Phase 1 co-occurrence clustering algorithm in detail. `plans/ACCESS.jsonl` is already at 100 entries (6.7× the 15-entry aggregation trigger), but running the algorithm requires manual multi-step orchestration across 6 ACCESS.jsonl files with no tool support. The systems-architecture research tightens the target behavior here: aggregation should not stop at a report. It should behave like log compaction plus materialized-summary refresh while keeping raw archive segments immutable.

---

## Phases

### Phase 1 — `memory_append_scratchpad` target expansion

**1.1 Accept dated slug targets**
Extend `memory_append_scratchpad` to accept a third target form: any string matching `scratchpad/{slug}.md` where slug is a valid kebab-case identifier (matching `_SLUG_RE`). The tool resolves it to `scratchpad/{slug}.md`, creates the file if it does not exist, and applies the same `---` separator + append logic as the named targets.

**1.2 Validation**
Reject targets that do not match `'user'`, `'current'`, or `r'^scratchpad/[a-z0-9][a-z0-9-]*\.md$'`. Raise `ValidationError` with a clear message showing the accepted forms.

**1.3 Update capabilities contract**
Update the `[operations.memory_append_scratchpad]` table in `HUMANS/tooling/agent-memory-capabilities.toml` to document the new target form.

---

### Phase 2 — `memory_resolve_review_item`

**2.1 Implement the tool in `semantic_tools.py`**
New Tier 1 tool. Signature:
```python
async def memory_resolve_review_item(
    item_id: str,
    resolution_note: str | None = None,
    version_token: str | None = None,
) -> str
```

`item_id` is the identifier of the review queue entry (slug or date-prefixed label). The tool:
1. Reads `meta/review-queue.md` and locates the matching entry
2. Removes the entry from the pending section
3. Appends a one-line entry to a `## Resolved` section at the bottom (date, item_id, resolution_note)
4. Auto-commits as `[governance] Resolve review item: {item_id}`

**2.2 `item_id` discovery**
`memory_flag_for_review` should emit an `item_id` in its result JSON so callers know how to reference the item later. Add `item_id` to its `new_state` output.

**2.3 Add `[operations.memory_resolve_review_item]` table to capabilities TOML**
Group: `governance`, tier: `semantic`, change_class: `proposed` (requires a human to have confirmed the item is resolved before the agent calls this), commit_model: `auto_commit`.

---

### Phase 3 — `memory_update_skill`

**3.1 Implement the tool in `semantic_tools.py`**
New Tier 1 tool mirroring `memory_update_identity_trait` but for `skills/`. Signature:
```python
async def memory_update_skill(
    file: str,
    section: str,
    content: str,
    mode: str = "upsert",
    version_token: str | None = None,
) -> str
```

`file` is the skill filename without path or `.md` extension (e.g. `"session-start"`, `"onboarding"`). `section` is a `##` heading name or a frontmatter key. `mode` is `'upsert'`, `'append'`, or `'replace'` — same semantics as `memory_update_identity_trait`.

Invariants maintained:
1. File must exist under `skills/` (no arbitrary creation — use `memory_write` for new skill files, which is allowed because `skills/` is in the protected write set for Tier 2 only for direct writes, but creation through a governed path is acceptable)
2. `last_verified` frontmatter updated to today
3. Auto-commits as `[skill] Update {section} in skills/{file}.md`

**3.2 Handle new skill file creation**
Add a `create_if_missing: bool = False` parameter. When true and the file does not exist, create it with skeleton frontmatter (`source`, `created`, `trust`, `origin_session` required as params). When false (default), raise `NotFoundError` if the file is missing.

**3.3 Session churn guard (optional)**
Consider whether skill updates need a session-level churn alarm analogous to `_IDENTITY_CHURN_LIMIT`. Skills are less identity-sensitive than profile fields, so default: no alarm. Document this decision.

**3.4 Update capabilities contract**
Add `memory_update_skill` to `semantic_extensions` and add `[operations.memory_update_skill]` table.

---

### Phase 4 — `memory_record_session` composite

**4.1 Implement the composite tool**
New Tier 1 tool. Signature:
```python
async def memory_record_session(
    session_id: str,
    summary: str,
    reflection: str | None = None,
    key_topics: str = "",
    access_entries: list[dict] | None = None,
) -> str
```

Atomically:
1. Writes `{session_id}/SUMMARY.md` with correct frontmatter (reusing `memory_record_chat_summary` internals)
2. If `reflection` is provided, writes `{session_id}/reflection.md`
3. Updates `chats/SUMMARY.md` top-level index
4. If `access_entries` is provided, appends entries to the appropriate ACCESS.jsonl files (injecting `session_id` automatically into each entry)
5. Commits a single `[chat] Record session {session_id}` commit covering all staged files

**4.2 Deprecate `memory_record_chat_summary` + `memory_record_reflection` in favor of composite**
Do not remove the individual tools immediately — they may be called in isolation — but update their docstrings to recommend `memory_record_session` for full session wrap-up. Mark them as `superseded_by: memory_record_session` in the capabilities TOML.

**4.3 Update `skills/session-wrapup.md`**
Replace the two-step `memory_record_chat_summary` → `memory_record_reflection` instruction with a single `memory_record_session` call.

---

### Phase 5 — `memory_run_aggregation`

**5.1 Implement Phase 1 co-occurrence clustering and compaction preview**
New Tier 0 tool (read-only computation; it does not write cluster results automatically). Signature:
```python
async def memory_run_aggregation(
    folders: list[str] | None = None,
    dry_run: bool = True,
) -> str
```

Reads all ACCESS.jsonl hot logs in the specified folders (default: all governed folders). Executes the Phase 1 algorithm from `meta/curation-algorithms.md`:
1. Group entries by `session_id` when present; fall back to `date` for legacy entries
2. Build a co-retrieval matrix across all session groups
3. Identify cluster candidates: 3+ files from 2+ folders where every pair co-occurs in 3+ session groups
4. Return a `clusters` list, `sessions_processed`, `entries_processed`, a `summary_updates` preview, and `archive_segments` that would be created if the run is applied

When `dry_run=False`, updates the affected folder `SUMMARY.md` usage sections, rotates processed entries into immutable archive segments such as `ACCESS.archive.2026-03.jsonl`, clears the hot `ACCESS.jsonl`, and commits as `[curation] Aggregate access log ({date})`. Protected by requiring user confirmation via the `change_class: proposed` governance path before any write.

**5.2 Add `memory_run_aggregation` to `read_support` (when dry_run=True) / `semantic_extensions` (when writing)**
The tool is read-only by default. Only the writing variant needs semantic extension registration. Model both behaviors in the capabilities TOML, noting the dual mode.

**5.3 Update `skills/session-start.md`**
When `memory_session_health_check` (from the Tier 0 plan) reports `aggregation_due`, include an instruction to call `memory_run_aggregation(dry_run=True)` and report the compaction preview to the user before deciding whether to apply the summary/archive updates.

**5.4 Handle the retroactive backfill case**
Document in the tool's docstring that the Exploration stage algorithm (Phase 1) does not require `task_id` or `category` fields. Flag entries missing `session_id` in the output summary so the user can see how much data is lost to the legacy fallback.

---

### Phase 6 — Tests, documentation, and contract updates

**6.1 Tests for `memory_append_scratchpad` expansion**
Test: dated slug target is accepted; file created if missing; separator behavior identical to named targets; invalid target format raises ValidationError.

**6.2 Tests for `memory_resolve_review_item`**
Test: item removed from pending section; appended to Resolved section; commit message correct; missing item_id raises NotFoundError.

**6.3 Tests for `memory_update_skill`**
Test: section upsert; mode=append; mode=replace; file not found raises NotFoundError; create_if_missing=True creates file with frontmatter.

**6.4 Tests for `memory_record_session`**
Test: both SUMMARY.md and reflection.md written; chats/SUMMARY.md updated; access entries have session_id injected; single commit produced.

**6.5 Tests for `memory_run_aggregation`**
Test: co-occurrence pairs correctly identified; cluster threshold enforcement (requires 3+ sessions); dry_run=True produces no file writes; dry_run=False updates folder summaries, rotates a dated archive segment, and clears only the processed hot log.

**6.6 Full capabilities TOML update**
Add all new tools to `semantic_extensions` and add their `[operations.XXX]` tables. Update the test that checks `semantic_extensions` length.

---

## Progress tracking

- [ ] 1.1 Expand `memory_append_scratchpad` to accept dated slug targets
- [ ] 1.2 Validation for new target form
- [ ] 1.3 Update capabilities TOML for scratchpad tool
- [ ] 2.1 Implement `memory_resolve_review_item`
- [ ] 2.2 Add `item_id` to `memory_flag_for_review` result
- [ ] 2.3 Add operations table for `memory_resolve_review_item`
- [ ] 3.1 Implement `memory_update_skill`
- [ ] 3.2 Handle `create_if_missing` param
- [ ] 3.3 Document skill churn guard decision
- [ ] 3.4 Update capabilities contract for skill tool
- [ ] 4.1 Implement `memory_record_session` composite
- [ ] 4.2 Update individual chat/reflection tool docstrings
- [ ] 4.3 Update `skills/session-wrapup.md`
- [ ] 5.1 Implement `memory_run_aggregation` with Phase 1 algorithm
- [ ] 5.2 Register tool in capabilities contract (both modes)
- [ ] 5.3 Update `skills/session-start.md` with aggregation instruction
- [ ] 5.4 Document retroactive backfill and session_id fallback behavior
- [ ] 6.1 Tests for `memory_append_scratchpad`
- [ ] 6.2 Tests for `memory_resolve_review_item`
- [ ] 6.3 Tests for `memory_update_skill`
- [ ] 6.4 Tests for `memory_record_session`
- [ ] 6.5 Tests for `memory_run_aggregation`
- [ ] 6.6 Full capabilities TOML update

**Progress:** 0/22 items complete

---

## Design constraints

- `memory_update_skill` churn guard: omitted for now; revisit when skill update frequency data is available.
- `memory_record_session` must fall back gracefully when only `summary` is provided (no reflection, no access entries); it should still produce a valid session record.
- `memory_run_aggregation` in `dry_run=True` mode must never write any file; enforce with `readOnlyHint=True` annotation in that mode.
- Aggregation must treat raw ACCESS events as immutable history: compaction means rotate and materialize, never rewrite old archive entries in place.
- `memory_resolve_review_item` operates on `meta/review-queue.md` which is a system-governed path; it must be a Tier 1 semantic tool and must not use Tier 2 primitives internally.
- All new tools must be registered in `server.py` and returned from their module's `register()` function.
- All new tools must have operations tables before the `test_semantic_operations_own_required_contract_fields` test is run.

---

## Notes

- 2026-03-19: Adjacent semantic groundwork landed outside this checklist: `memory_record_periodic_review` now provides a protected governance write path for approved periodic-review outputs. That does not directly complete checklist items here, but it validates the manifest, approval, and publication patterns needed for future protected semantic tools.
- 2026-03-19: The read-side additions from the same session (`memory_run_periodic_review`, provenance inspection, commit inspection) also reduce uncertainty around future `memory_resolve_review_item`, `memory_record_session`, and aggregation-oriented flows.
- 2026-03-19: Keep `next_action` unchanged. The remaining direct scope is still scratchpad targeting, review-queue lifecycle, skill updates, session recording, and aggregation execution.
