# Agent working notes

Provisional, agent-authored. Not formal memory. Each entry is dated and linked to its originating session. Entries are promoted to `identity/`, `knowledge/`, or `skills/` when confirmed, or cleared after ~3 sessions without action.

See `meta/scratchpad-guidelines.md` for the full write protocol, promotion criteria, and lifecycle rules.

---

<!-- 2026-03-19, session: chats/2026/03/19/chat-001 -->
## Access-log aggregation analysis

**Corpus**: 128 entries across 6 ACCESS.jsonl files (plans/, knowledge/, skills/, identity/, chats/, knowledge/_unverified/).

### High-level stats

| Metric | Value |
|--------|-------|
| Total entries | 128 |
| Date range | 2026-03-16 – 2026-03-19 |
| Entries from 2026-03-18 alone | 118 (92%) |
| Entries with `session_id` | 17 (13%) |
| Low-value entries (helpfulness ≤ 0.3) | 37 (28%) |
| High-value entries (helpfulness ≥ 0.9) | 33 (25%) |
| Mean helpfulness | 0.61 |

### Folder breakdown

| Folder | Entries | Notes |
|--------|---------|-------|
| plans/ | 100 (78%) | Completely dominant |
| knowledge/_unverified/ | 15 | Django + rationalist research |
| skills/ | 7 | onboarding, session-start/wrapup |
| knowledge/ | 3 | literature files |
| chats/ | 2 | Severely underlogged |
| identity/ | 1 | Only profile.md onboarding read |

### Sweep pattern (the core issue)

9 distinct task strings with ≥5 entries each account for ~86 entries (67% of total). Every plan-review session logs ALL active plans even when only 1-2 are the actual working focus. The longest sweep task ("Review all active plans, advance the highest-priority one, and choose the next plan priority") generated **21 entries** alone.

### Most-accessed files

| File | Accesses | Avg helpfulness |
|------|----------|-----------------|
| codex-desktop-governed-memory-writes.md | 13 | 0.93 |
| codex-desktop-bootstrap-support.md | 12 | 0.94 |
| django-stack-research.md | 12 | 0.62 |
| philosophy-history-survey.md | 10 | **0.32** |
| codex-desktop-automation-continuity.md | 9 | 0.71 |
| lesswrong-rationalist-community-research.md | 8 | **0.28** |
| react-stack-research.md | 8 | **0.36** |
| devops-docker-research.md | 8 | **0.34** |
| ai-paradigm-genealogy-research.md | 6 | **0.20** |

Files in bold are consistently low-value but logged every sweep.

### Coverage gaps (files never logged)

- All `meta/` files (quick-reference, integrity-checklist, update-guidelines, etc.)
- All `scratchpad/` files
- Most `chats/` session summaries and reflections
- `skills/` files during research sessions (only logged in review sessions)

---

### MCP tooling improvements identified

**1. `memory_log_access_batch` — batch write for sweeps**
Currently each file access is a separate tool call + git commit. A sweep of 10 plans = 10 round trips. A batch variant taking `[{file, helpfulness, note}]` would reduce git noise, round-trip cost, and latency. Could also enable per-session commit grouping.

**2. Session-id enforcement / auto-injection**
Only 13% of entries carry a `session_id`. The tool should either: (a) require it as a non-optional param, or (b) auto-inject the current session path by reading `chats/CURRENT.md` or an env variable. Without it, `memory_get_maturity_signals`'s `total_sessions` metric is nearly meaningless.

**3. Sweep-filter parameter (`min_helpfulness`)**
Add an optional `min_helpfulness` threshold to `memory_log_access` (and the batch variant). Entries below the threshold would be logged to a lightweight "scan log" (not the main ACCESS.jsonl) or silently skipped. This would eliminate ~28% of current low-value noise — particularly the background plans that are opened and skipped every session.

**4. Write-mode field (`mode: read | write | update | create`)**
The access log currently only tracks reads. There is no record of which files were *created* or *modified* in a session. Adding a `mode` field would let `memory_get_maturity_signals` distinguish "consulted" from "actively maintained" files, and would give the user visibility into session output vs. session inputs.

**5. Intra-session timing (`time` or `seq` field)**
All entries have only a `date` field. Adding a lightweight `seq` (sequence integer within session) or ISO timestamp would distinguish orientation reads (early) from verification reads (late). This would also help `memory_get_maturity_signals` compute a "reads before first write" metric.

**6. Task normalization (`task_id` short code)**
34 distinct task strings, many nearly identical and very long. A short `task_id` (e.g., `"plan-review"`, `"research-write"`, `"validation"`) alongside the free-text note would enable grouping, filtering, and trend analysis without parsing long strings.

**7. Coverage incentive for meta/ and scratchpad/**
The system currently has no mechanism to notice that governance files (quick-reference, integrity-checklist) are consulted but never logged. A `memory_validate` check could flag folders with 0 access entries over a rolling window and surface them in the health report.

**8. `memory_get_maturity_signals` robustness fix**
Since session_id coverage is only 13%, the tool's `total_sessions` output is misleading. Fallback logic: count distinct (date, task) pairs as a proxy for sessions when session_ids are sparse. Or emit a `session_id_coverage_pct` warning field when coverage < 50%.

---

<!-- 2026-03-19, session: chats/2026/03/19/chat-001 -->
## MCP tooling system review — second pass

**Method:** Read all three tool files in full (`read_tools.py`, `semantic_tools.py`, `write_tools.py`), the capabilities TOML, `session-start.md`, `quick-reference.md`, `integrity-checklist.md`, and `curation-algorithms.md`.

---

### Tier 0 — Read tool gaps

**G1 `memory_git_log` missing `since` / `path_filter` params**
`git log --after=DATE -- path/` is fully supported by the underlying git CLI but not exposed. When >15 commits have landed between sessions, you either over-fetch with a high `n` or miss changes. Especially painful for identity/ and meta/ where you want "what changed to my profile this week?" 

**G2 No `memory_session_health_check` (highest-priority missing read)**
`session-start.md` explicitly instructs agents to: (a) read `meta/quick-reference.md` to get the aggregation trigger count, (b) count non-empty lines in each ACCESS.jsonl, (c) compare to threshold individually, (d) also check review queue for placeholder vs. real entries, and (e) check the last periodic-review date. That is 6–10 tool calls just to answer "is any maintenance due?" A single `memory_session_health_check` returning a structured result would collapse this entirely:
```json
{
  "aggregation_due": [{"folder": "plans/", "entries": 100, "threshold": 15, "overdue": true}],
  "review_queue_pending": 0,
  "periodic_review_due": false,
  "days_since_review": 0,
  "trust_decay_alerts": 0
}
```

**G3 `memory_audit_trust` scan-only — no approaching-threshold warning tier**
Currently reports overdue/upcoming (upcoming = within 30 days of threshold). But an approaching file that's 90 days into a 120-day clock has no visibility until it's 30 days out. A `warn_pct` param (default: 75%) would surface these earlier without flooding the report.

---

### Tier 1 — Semantic tool gaps

**G4 `memory_append_scratchpad` only targets `'user'` | `'current'`**
The repo has date-named scratchpad files (`scratchpad/2026-03-18-automation-backlog.md`, etc.) that were created mid-session and can't be targeted by this tool. Agents are forced to fall back to raw `memory_write` for these, losing the append-only convention, the `---` separator insertion, and the `[scratchpad]` commit prefix. Fix: accept any `scratchpad/{slug}.md` path as a third target form.

**G5 No `memory_resolve_review_item` / `memory_dismiss_review_item`**
`memory_flag_for_review` pushes items to `meta/review-queue.md`, but there is no governed path to remove them once resolved. After a periodic review, the agent currently has to use raw `memory_edit` or `memory_write` on `meta/` which is explicitly blocked by Tier 2 path policy. The review queue therefore accumulates without a governed pop. A `memory_resolve_review_item(item_id, resolution_note)` tool that removes an entry and appends to a resolved-items log would close the loop.

**G6 No skill file semantic tool**
`skills/` is protected from all Tier 2 mutations. But unlike `identity/` (which has `memory_update_identity_trait`), there is no `memory_update_skill` tool. Creating or updating a skill file currently has no tool-backed path — the user must do it manually or the agent falls silent. Minimum needed: `memory_update_skill(file, section, content, mode)` mirroring `memory_update_identity_trait`.

**G7 `memory_record_chat_summary` + `memory_record_reflection` are always called together**
Session wrap-up calls both back-to-back, producing two separate commits. A `memory_record_session(session_id, summary, reflection, key_topics)` composite would atomically write SUMMARY.md, reflection.md, update chats/SUMMARY.md, and log ACCESS — all in a single `[chat]` commit, and with proper session_id injection into the access log entry.

**G8 No `memory_run_aggregation`**
`curation-algorithms.md` defines a multi-step manual aggregation process: group ACCESS entries by session, compute co-retrieval pairs, identify clusters, write SUMMARY updates. With 100 entries already in plans/ACCESS.jsonl (6.7× the 15-entry trigger), this process should be tool-backed. A `memory_run_aggregation(folder)` that reads the algorithm parameters from `quick-reference.md` and executes Phase 1 co-occurrence clustering would make aggregation routine rather than heroic.

---

### Tier 2 — Write tool gaps

**G9 No `memory_update_frontmatter_bulk`**
Last session required updating `origin_session` or `source` fields across 35+ files individually. The current `memory_update_frontmatter` handles one file at a time. A `[{path, updates}]` batch form that stages all changes and commits them in a single `[system]` commit would handle mass backfills efficiently and safely.

---

### Cross-cutting gaps

**G10 No `memory_get_capabilities` tool**
Capability discovery currently requires: call `memory_list_folder("HUMANS/tooling", include_humans=True)` → then `memory_read_file("HUMANS/tooling/agent-memory-capabilities.toml")` → parse manually. A `memory_get_capabilities` tool that reads + parses the TOML and returns structured `{read_support, semantic_extensions, declared_gaps, desktop_operations}` would make capability discovery tool-native and align with the `capability_discovery` integration boundary the TOML already declares.

**G11 `memory_search` returns line matches with no surrounding context**
Current output: `file.md\n  45: matching line here`. When reading code or multi-line narratives, you need 2–5 surrounding lines to understand the match without a follow-up `memory_read_file`. A `context_lines` param (like `grep -B/-A`) would eliminate a common read-after-search round trip.

---

### Priority ranking

| # | Gap | Impact | Effort |
|---|-----|--------|--------|
| G2 | `memory_session_health_check` | HIGH — directly reduces session-start friction | Medium |
| G5 | `memory_resolve_review_item` | HIGH — review queue is currently a one-way accumulator | Low |
| G4 | `memory_append_scratchpad` target expansion | HIGH — dated scratchpad files are tool-inaccessible | Low |
| G6 | `memory_update_skill` | HIGH — skills/ is a write dead-end | Medium |
| G8 | `memory_run_aggregation` | HIGH — trigger hit, process is fully manual | High |
| G9 | `memory_update_frontmatter_bulk` | MEDIUM — demonstrated pain last session | Low |
| G7 | `memory_record_session` composite | MEDIUM — ergonomic, reduces session-end commits | Medium |
| G1 | `memory_git_log` since/path filter | MEDIUM — git supports it natively | Low |
| G10 | `memory_get_capabilities` | LOW — currently workable via read_file | Low |
| G11 | `memory_search` context lines | LOW — reduces follow-up reads | Low |
| G3 | `memory_audit_trust` warn_pct | LOW — not urgent at current scale | Low |

---

<!-- 2026-03-18, session: chats/2026/03/18/chat-003 -->
Pattern (needs more data): The memory repo now has a plausible second-tier automation backlog beyond the first four maintenance drafts. Candidate ideas are tracked in `scratchpad/2026-03-18-automation-backlog.md` until repeated need or user approval justifies promotion into a formal plan or skill proposal.
