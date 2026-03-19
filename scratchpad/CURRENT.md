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

<!-- 2026-03-18, session: chats/2026/03/18/chat-003 -->
Pattern (needs more data): The memory repo now has a plausible second-tier automation backlog beyond the first four maintenance drafts. Candidate ideas are tracked in `scratchpad/2026-03-18-automation-backlog.md` until repeated need or user approval justifies promotion into a formal plan or skill proposal.
