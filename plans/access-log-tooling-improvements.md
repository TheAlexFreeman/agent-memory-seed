---
created: 2026-03-19
last_verified: 2026-03-20
next_action: "Plan complete; optional follow-up is human review of ACCESS analytics outputs"
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: complete
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: Access-Log Tooling Improvements

## Goals

Improve the quality, efficiency, and analytical utility of the memory system's access-logging layer. The current `memory_log_access` tool works, but an audit of 128 real ACCESS.jsonl entries exposed structural gaps that reduce the value of every downstream consumer: `memory_get_maturity_signals`, session health checks, and human review. The systems-architecture research also makes clear that ACCESS is an append-only event log, so this plan now treats aggregation as compaction plus materialized-summary refresh rather than as ad hoc cleanup.

---

## Problem statement

Analysis of the full ACCESS.jsonl corpus (128 entries, 6 folders, 2026-03-16 to 2026-03-19) revealed four systemic problems:

1. **Sweep inflation** — every plan-review session logs all active plans, even ones skipped. One task string produced 21 entries in a single session; 67% of all entries came from 9 "sweep" tasks. This pollutes helpfulness averages and bloats git history.

2. **Broken session identity** — only 13% of entries carry a `session_id`. The `total_sessions` field in `memory_get_maturity_signals` is therefore nearly meaningless.

3. **Read-only blind spot** — no entries record which files were *written* in a session. The log only tracks inputs, not outputs.

4. **Coverage gaps** — `meta/`, `scratchpad/`, and most `chats/` files are entirely unlogged despite active use. No existing check surfaces this.

5. **No archive segmentation or materialized-view discipline** — the repo documents `ACCESS.archive.jsonl` conceptually but does not yet define how hot logs rotate into immutable archive segments or how aggregation updates folder summaries as rebuildable derived state.

---

## Phases

### Phase 1 — Batch write and session wiring (foundation)

**1.1 `memory_log_access_batch`** *(semantic/session_tools.py)*
Implement a new MCP tool that accepts a list of access entries and writes them all in a single git commit. Schema: `[{file, helpfulness, note, mode?, task_id?}]`. Reduces a 10-plan sweep from 10 round trips to 1. Register it on the semantic session-tool surface exposed through the server bootstrap.

**1.2 Session-id auto-injection**
Update `memory_log_access` and the batch variant to accept an optional `session_id` param. If absent, attempt to read from a configurable env var (`MEMORY_SESSION_ID`) or a sentinel file (`chats/CURRENT_SESSION`). Document the injection contract in `HUMANS/tooling/agent-memory-capabilities.toml`.

**1.3 Update capabilities contract**
Add `memory_log_access_batch` to `semantic_extensions` and add its `[operations.memory_log_access_batch]` table. Add `session_id` to the `memory_log_access` operation's param list.

---

### Phase 2 — Schema enrichment

**2.1 `mode` field**
Add an optional `mode` field to each access entry with values: `read`, `write`, `update`, `create`. Document in the field spec. Update `memory_get_maturity_signals` to report `write_sessions` (sessions with at least one non-read entry) alongside `total_sessions`.

**2.2 `task_id` short code**
Add an optional `task_id` field (lowercase slug, e.g., `"plan-review"`, `"research-write"`, `"validation"`, `"health-check"`). Define the canonical set in `HUMANS/tooling/agent-memory-capabilities.toml`. Update `memory_get_maturity_signals` to group `access_density` by `task_id` bucket.

**2.3 `min_helpfulness` sweep filter**
Add an optional `min_helpfulness` param to `memory_log_access` and the batch variant. Entries below threshold are written to a sidecar `ACCESS_SCANS.jsonl` (same folder) rather than the main `ACCESS.jsonl`. This keeps the primary log high-signal while preserving the scans as append-only audit data rather than silently dropping them.

**2.4 Archive segmentation and hot-log reset**
Define the post-aggregation storage model explicitly:
- current reads land only in the hot `ACCESS.jsonl`
- aggregation rotates processed entries into immutable dated segments such as `ACCESS.archive.2026-03.jsonl`
- `SUMMARY.md` usage patterns are treated as materialized views derived from those raw events

Update `memory_get_maturity_signals` and any future aggregation tooling to operate on the hot segment by default, not the entire historical archive.

---

### Phase 3 — Validate coverage

**3.1 `memory_validate` coverage check**
Extend the validator to detect folders with 0 ACCESS.jsonl entries over a configurable rolling window (default: 30 days). Emit a new warning class `CoverageGap` listing the folder and days-since-last-entry. Initially scope to: `meta/`, `skills/`, `identity/`, `chats/`.

**3.2 `memory_get_maturity_signals` robustness**
Emit a `session_id_coverage_pct` field. When coverage < 50%, also compute `proxy_sessions` as the count of distinct `(date, task_id or task)` pairs and emit it alongside `total_sessions` with a `proxy_session_note` warning string.

---

### Phase 4 — Tests and documentation

**4.1 Test `memory_log_access_batch`**
Add unit tests in `HUMANS/tooling/tests/` covering: correct JSONL append, single-commit behavior, optional fields (mode, task_id, session_id), and min_helpfulness routing to sidecar file.

**4.2 Test coverage check**
Add tests for the new `CoverageGap` validator warning: folder with no entries triggers warning, folder with recent entry does not.

**4.3 Update capabilities TOML tests**
Extend `test_memory_capabilities.py` to assert that `memory_log_access_batch` is present in `semantic_extensions` and has a valid operations table.

**4.4 Update `HUMANS/docs/CORE.md`**
Document the `mode`, `task_id`, `session_id` fields and the `ACCESS_SCANS.jsonl` sidecar convention.


## Progress tracking

- [x] 1.1 Implement `memory_log_access_batch` tool
- [x] 1.2 Session-id auto-injection (env var + sentinel file)
- [x] 1.3 Update capabilities contract
- [x] 2.1 Add `mode` field + maturity signal update
- [x] 2.2 Add `task_id` short code + maturity signal grouping
- [x] 2.3 Add `min_helpfulness` sweep filter + sidecar file
- [x] 2.4 Define archive segmentation + materialized-summary refresh behavior
- [x] 3.1 Extend `memory_validate` with coverage check
- [x] 3.2 `memory_get_maturity_signals` fallback + coverage field
- [x] 4.1 Tests for batch tool
- [x] 4.2 Tests for coverage validator
- [x] 4.3 Update capabilities TOML tests
- [x] 4.4 Document new fields in CORE.md

**Progress:** 13/13 items complete

---

## Design constraints

- All new fields are optional; existing ACCESS.jsonl entries remain valid.
- The `ACCESS_SCANS.jsonl` sidecar must not be included in maturity signal calculations.
- `ACCESS.jsonl` is the hot append-only log; archive segments are immutable and are processed separately from the session-start hot-path health check.
- `memory_log_access_batch` must use a single `auto_commit` (not one commit per entry).
- `min_helpfulness` default is `None` (no filtering) to avoid breaking existing call sites.
- `task_id` values are a controlled vocabulary defined in the TOML; free strings are rejected.

