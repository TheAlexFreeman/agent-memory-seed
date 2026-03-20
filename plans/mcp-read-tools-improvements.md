---
created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: add since and path_filter params to memory_git_log"
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: implementation-plan
---

# Implementation Plan: MCP Tier 0 Read Tool Improvements

## Goals

Close three gaps in the Tier 0 read tool suite (`read_tools.py`) identified during a full-stack MCP tooling review. All three are additive, non-breaking enhancements to existing tools or new read-only tools that involve no write risk. They directly reduce session-start overhead and surface trust decay earlier.

---

## Problem statement

The current Tier 0 tool set (`memory_read_file`, `memory_list_folder`, `memory_search`, `memory_git_log`, `memory_diff`, `memory_audit_trust`, `memory_validate`, `memory_get_maturity_signals`) leaves three friction points unaddressed:

**Gap 1 — `memory_git_log` is coarse-grained:** The tool accepts only `n` (count of commits, max 50). There is no way to filter by date range or by path. When 50+ commits have landed between sessions, or when an agent wants to see "what changed to identity/ this week?", it must either over-fetch and scan manually, or read each file independently for change detection.

**Gap 2 — Session health check requires 6–10 round trips:** `skills/session-start.md` instructs the agent to manually: read `meta/quick-reference.md` for the aggregation trigger threshold, count non-empty lines in each ACCESS.jsonl file (6 files), compare individually to the threshold, check whether `meta/review-queue.md` has real entries or only a placeholder, and check the `last_periodic_review` date against today. That is 8–10 sequential tool calls just to answer "is any maintenance due this session?" There is no single tool that collapses this check.

**Gap 3 — Trust decay has a blind spot from 50–75% of threshold:** `memory_audit_trust` reports two tiers: `overdue` (past threshold) and `upcoming` (within 30 days of threshold). A low-trust file that is 95 days old (past 75% of its 120-day clock but more than 30 days from the boundary) is invisible. It only surfaces in the tool output 2–4 weeks before it becomes a forced retirement decision, leaving no time for proactive review.

---

## Phases

### Phase 1 — `memory_git_log` filter params

**1.1 Add `since` param**
Add an optional `since: str | None = None` parameter accepting an ISO date string (e.g. `"2026-03-15"`). When set, passes `--after={since}` to `git log`. Combine with existing `n` limit (whichever truncates first). Emit a `truncated: true` flag in the result when the limit was hit before the date boundary.

**1.2 Add `path` param**
Add an optional `path: str | None = None` parameter accepting a repo-relative path or glob (e.g. `"identity/"`, `"plans/react-stack-research.md"`). When set, passes `-- {path}` to `git log` to restrict output to commits that touched that subtree. Combine with `since` freely.

**1.3 Update docstring and `capabilities.toml`**
Update the `memory_git_log` docstring to describe both new params, their defaults (None = no filter), and the `truncated` output field. Update `[operations.memory_git_log]` in `HUMANS/tooling/agent-memory-capabilities.toml` if an operations table exists for it.

---

### Phase 2 — `memory_session_health_check`

**2.1 Implement the tool in `read_tools.py`**

New Tier 0 tool. Signature:
```python
async def memory_session_health_check() -> str
```

Reads the following without requiring agent orchestration:
- `meta/quick-reference.md` → extract `aggregation_trigger` value and `last_periodic_review` date
- All hot `*/ACCESS.jsonl` paths (plans, knowledge, knowledge/_unverified, skills, identity, chats) → count non-empty lines per file without scanning archive segments
- `meta/review-queue.md` → count real pending items (lines that are not headings, blank, or matching the placeholder pattern)

Returns structured JSON:
```json
{
  "aggregation_due": [
    {"folder": "plans/", "entries": 100, "threshold": 15, "overdue": true}
  ],
  "aggregation_threshold": 15,
  "review_queue_pending": 0,
  "periodic_review_due": false,
  "days_since_review": 0,
  "last_periodic_review": "2026-03-19",
  "checked_at": "2026-03-19"
}
```

`aggregation_due` is a list of folders where hot-log `entries >= threshold`. `periodic_review_due` is true when `days_since_review` exceeds a configurable window (default: 30 days, readable from `quick-reference.md`).

**2.2 Register in `server.py` and `read_support` list**
Add `memory_session_health_check` to the `read_support` list in `HUMANS/tooling/agent-memory-capabilities.toml` and ensure `register()` in `read_tools.py` returns it.

**2.3 Update `skills/session-start.md`**
Replace the manual 8-step health-probe procedure with a single `memory_session_health_check` call. Retain the manual fallback instructions for environments where MCP is unavailable.

---

### Phase 3 — `memory_audit_trust` warn_pct param

**3.1 Add `warn_pct` param to `memory_audit_trust`**
Add `warn_pct: float = 0.75` parameter. When set, files whose age exceeds `warn_pct * threshold` (but not yet in the `upcoming` window, i.e., not within 30 days of the boundary) are added to a new `approaching` bucket in the output. Default of 75% means: flag low-trust files older than 90 days, flag medium-trust files older than 135 days, but only when they are not already in `upcoming`.

**3.2 Add `approaching` bucket to output JSON**
Extend the return JSON to include an `approaching` list alongside `overdue`, `upcoming_low`, and `upcoming_medium`. Each entry has the same schema as `overdue` entries.

**3.3 Update docstring and test**
Update the `memory_audit_trust` docstring. Add a test case for a file at 80% of threshold that correctly appears in `approaching` but not `upcoming`.

---

### Phase 4 — Tests, documentation, and contract update

**4.1 Tests for `memory_git_log` filter params**
Unit tests: log filtered by `since` returns only commits after the date; log filtered by `path` returns only commits touching that path; both filters combined; neither set behaves identically to current behavior.

**4.2 Tests for `memory_session_health_check`**
Unit tests: folder above threshold appears in `aggregation_due`; periodic review overdue when last_periodic_review > 30 days ago; review queue count correctly ignores placeholder lines.

**4.3 Tests for `memory_audit_trust` approaching bucket**
Add to existing test file: file at 80% of threshold → in `approaching`; file at 90% of threshold → in `upcoming`, not `approaching`.

**4.4 Update `agent-memory-capabilities.toml`**
Add `memory_session_health_check` to `read_support` list. Ensure `warn_pct` and filter params are documented in the relevant operations tables.

---

## Progress tracking

- [ ] 1.1 Add `since` param to `memory_git_log`
- [ ] 1.2 Add `path` param to `memory_git_log`
- [ ] 1.3 Update docstring and TOML for `memory_git_log`
- [ ] 2.1 Implement `memory_session_health_check` in `read_tools.py`
- [ ] 2.2 Register in server and capabilities contract
- [ ] 2.3 Update `skills/session-start.md` to use the new tool
- [ ] 3.1 Add `warn_pct` param to `memory_audit_trust`
- [ ] 3.2 Add `approaching` bucket to audit output
- [ ] 3.3 Update docstring and test for approaching bucket
- [ ] 4.1 Tests for `memory_git_log` filter params
- [ ] 4.2 Tests for `memory_session_health_check`
- [ ] 4.3 Tests for `memory_audit_trust` approaching bucket
- [ ] 4.4 Update `agent-memory-capabilities.toml`

**Progress:** 0/13 items complete

---

## Design constraints

- All changes are additive: no existing params removed, no return schema fields removed.
- `memory_session_health_check` is read-only (`readOnlyHint=True`): it must never stage or commit.
- `memory_session_health_check` must operate on hot ACCESS logs only; archive segments are historical state and should not inflate routine session-start maintenance checks.
- `warn_pct` must satisfy `0 < warn_pct < 1`; raise `ValidationError` on out-of-range values.
- `since` must be validated as a valid ISO date string before being passed to git; raise `ValidationError` on bad format.
- `memory_session_health_check` must not require a separate `meta/quick-reference.md` read from the agent — it reads that file internally.
