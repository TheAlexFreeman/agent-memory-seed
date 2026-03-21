# Quick Reference

**Read this file at the start of every session before applying any thresholds or curation rules.**

This is the single authoritative source for the system's currently active operational parameters. All other threshold values in `README.md` and `meta/curation-policy.md` are reference values. `meta/system-maturity.md` is a stage-selection reference, not the live runtime config.

## Architectural guardrails for system changes

When you are reviewing or modifying the system itself, treat **consistency**, **user-friendliness**, and **context efficiency** as architectural guardrails. Keep authority files aligned, preserve the compact returning path, and make tradeoffs explicit when a change helps one dimension at the expense of another.

---

## Session routing

Use this file as the operational router for every session:

1. Start here.
2. If this is a fresh instantiation on a blank or template-backed repo, read `README.md` and then `meta/first-run.md`.
3. If this is a fresh instantiation on a returning system, or you intentionally need the full governance stack, read `README.md` and then follow the **Full bootstrap** manifest below.
4. Otherwise, use the **Compact returning** manifest below and keep additional loads task-driven.

**MCP discovery:** Some hosts expose the Engram server under a project-prefixed name instead of `agent-memory`. If a call fails because the server name does not exist, use the identifier shown in the host's available-server list.

---

## Context loading manifest

Use this table to determine which files to read for each session type. Load files in the listed order. Files marked _(skip if empty)_ should be skipped when they contain only placeholder text.

| Session type | Files to load |
|---|---|
| **First run** | `README.md` → `meta/first-run.md` (which directs: `CHANGELOG.md`, this file, `meta/update-guidelines.md` §§ Change categories + Read-only operation, `skills/SUMMARY.md`, `skills/onboarding.md`) |
| **Compact returning** | this file → `identity/SUMMARY.md` → `chats/SUMMARY.md` _(skip if empty or still placeholder)_ → `plans/SUMMARY.md` _(skip if no active plans)_ → `scratchpad/USER.md` _(skip if only placeholder)_ → `scratchpad/CURRENT.md` _(skip if only placeholder)_ → task-relevant `knowledge/SUMMARY.md` and/or `skills/SUMMARY.md` only when the current task or recent history makes them relevant |
| **Full bootstrap** | `README.md` → Compact returning files + `CHANGELOG.md`, `meta/curation-policy.md`, `meta/update-guidelines.md` |
| **Periodic review** | Full bootstrap files + `meta/system-maturity.md`, `meta/belief-diff-log.md`, `meta/review-queue.md`, `meta/integrity-checklist.md` |
| **ACCESS aggregation** | This file + `meta/curation-algorithms.md` (load only when aggregation threshold is reached) |
| **Stage transition** | Periodic review files + `meta/curation-algorithms.md` |

**Do not load** `HUMANS/docs/*` (human reference only) or `meta/curation-algorithms.md` (on-demand only). `meta/session-checklists.md` and `meta/scratchpad-guidelines.md` are also on-demand — load them only when you need detailed runbooks, session-end scratchpad review criteria, or extra protocol detail.

### Compact returning notes

- Run metadata-first maintenance probes before loading extra governance files.
- Check whether `meta/review-queue.md` still contains only its placeholder. Load the body only when real entries exist or the user asks about it.
- Count non-empty lines in `ACCESS.jsonl` files to see whether any folder has reached the aggregation trigger. Load entries only when a trigger is hit or the current task requires retrieval analysis.
- `knowledge/SUMMARY.md` and `skills/SUMMARY.md` are task-driven context, not unconditional startup reads.
- In worktree mode, use `host_repo_root` from `agent-bootstrap.toml` for host-code git operations and the worktree path for memory files and governance.

---

## Compact bootstrap contract

Compact startup files are live-state surfaces, not archives. They should answer only: what is active now, what should happen next, and where to drill down when the compact view is insufficient.

**Startup strategy:** Whole-file compact mode. Keep the startup-loaded files themselves compact; do not rely on hidden startup-safe subsections inside larger narrative files.

| File | Keep in compact path | Move to drill-down files | Target budget |
|---|---|---|---|
| `meta/quick-reference.md` | Routing authority, active thresholds, compact contract, decision triggers | Long rationale, runbooks, full algorithms | ~2,600 tokens |
| `identity/SUMMARY.md` | User portrait, working style, active durable goal | Detailed profile evidence | ~450 tokens |
| `chats/SUMMARY.md` | Live themes, recent continuity, retrieval guidance | Chat-by-chat narrative | ~750 tokens |
| `plans/SUMMARY.md` | Active-plan priority, scope, progress, next actions, recent completions | Full plan detail | ~1,700 tokens |
| `scratchpad/USER.md` | User-authored current constraints | Historical notes that no longer affect current work | ~400 tokens |
| `scratchpad/CURRENT.md` | Active threads, immediate next actions, open questions, drill-down refs | Extended analysis and large tables | ~650 tokens |

These targets intentionally leave reserve headroom inside the 7k returning-session ceiling. If a startup file needs sustained depth beyond its target, move that depth into a plan, dated scratchpad, or dated chat summary and link to it from the compact surface.

## Compact file success criteria

- `plans/SUMMARY.md` must preserve active-plan priority and next actions while keeping completed work to a compact recent-completions block.
- `chats/SUMMARY.md` must preserve current themes, recent continuity, and a clear retrieval guide.
- `scratchpad/CURRENT.md` must preserve active threads, immediate next actions, unresolved questions, and drill-down references.
- `meta/quick-reference.md` must preserve live routing, active thresholds, and the current compact contract without importing long explanatory policy text.

---

## Current active stage: Exploration

_Last assessed: 2026-03-19 — Exploration retained (all 6 signals within bounds)_

**Exploration defaults apply** — use the threshold values in the Active thresholds table below until a periodic review triggers a stage transition.

## Last periodic review

**Date:** 2026-03-19

Update this date when completing the full periodic-review checklist in `meta/update-guidelines.md`.

## Active thresholds

| Parameter | Active value | Stage |
|---|---|---|
| Low-trust retirement threshold | 120 days | Exploration |
| Medium-trust flagging threshold | 180 days | Exploration |
| Staleness trigger (no access) | 120 days | Exploration |
| Aggregation trigger | 15 entries | Exploration |
| Identity churn alarm | 5 traits/session | Exploration |
| Knowledge flooding alarm | 5 files/day | Exploration |
| Task similarity method | Session co-occurrence | Exploration |
| Cluster co-retrieval threshold | 3 sessions | Exploration |

---

## Active task similarity method

**Method:** Session co-occurrence

**Grouping precedence:** Group ACCESS entries by `session_id` when present. If an entry predates `session_id`, fall back to `date` for backward compatibility.

**Default before first assessment:** Treat the system as Exploration and use the values recorded in this file.

**Full algorithm details:** See `meta/curation-algorithms.md` (load only when running aggregation or a stage transition).

---

## Decision guide: trust decay

Trust sets the decay threshold; freshness comes from the effective verification date (`last_verified` if present, otherwise `created`).

- `trust: low` — older than **120 days** without re-verification: archive to `knowledge/_archive/` and remove from SUMMARY.md.
- `trust: medium` — older than **180 days** without re-verification: flag in `meta/review-queue.md` for review or demotion.
- `trust: high` — older than **365 days**: mention during periodic review for a freshness check only.
- Files without frontmatter are treated as `trust: medium` until fixed.

See `meta/curation-policy.md` for the full freshness-vs-confidence rationale and retroactive-frontmatter guidance.

## Decision guide: anomaly detection

| Signal | Trigger | Action |
|---|---|---|
| Identity traits changed in one session | > **5** traits | Flag in `meta/review-queue.md` |
| Knowledge files on same topic from `external-research`, same session or day | > **5** files | Flag in `meta/review-queue.md` |
| File dormant for **120 days**, then retrieved 3+ times in one session | Spike after dormancy | Flag in `meta/review-queue.md` |
| File retrieved 5+ times total but never explicitly approved by user | 5 retrievals | Flag in `meta/review-queue.md` |

## Decision guide: ACCESS.jsonl aggregation

Aggregate when entries accumulated since the last aggregation reach **15**.

1. Refresh the relevant SUMMARY.md usage patterns.
2. Enrich high-value files (5+ retrievals, mean helpfulness ≥ 0.7).
3. Review low-value files (3+ retrievals, mean helpfulness ≤ 0.3).
4. Scan for cross-folder co-retrieval clusters using the active task similarity method.
5. Archive processed entries to `ACCESS.archive.jsonl` and reset the live `ACCESS.jsonl`.

Entry counting rule: count entries in the current `ACCESS.jsonl`, not the archive. For the full aggregation procedure, load `meta/curation-algorithms.md`.

## Curation operations

| Tool | Use | Example |
|---|---|---|
| `memory_promote_knowledge_batch` | Promote multiple unverified files in one governed commit. | `memory_promote_knowledge_batch(source_paths='["knowledge/_unverified/literature/foo.md", "knowledge/_unverified/literature/bar.md"]', trust_level="high")` |
| `memory_promote_knowledge_subtree` | Promote an entire unverified topic tree while preserving nested paths. | `memory_promote_knowledge_subtree(source_folder="knowledge/_unverified/rationalist-community", dest_folder="knowledge/rationalist-community", trust_level="medium", dry_run=True)` |

## Helpfulness scoring guide

- `0.0–0.1` wrong context
- `0.2–0.4` near-miss
- `0.5–0.6` useful context
- `0.7–0.8` highly relevant
- `0.9–1.0` critical

Score what actually happened, not what should have happened.

---

## How to update this file

After periodic review:

1. Update the active stage and last-assessed line.
2. Update the last periodic review date.
3. Copy the chosen stage values from `meta/system-maturity.md` into the Active thresholds table.
4. Keep the compact bootstrap contract and decision triggers aligned with validator rules.
5. Log the change in `CHANGELOG.md`.

---

## Context budget guideline

| Session mode | Typical token cost |
|---|---|
| First-run onboarding bootstrap | ~15,000–20,000 |
| Returning compact session | ~3,000–7,000 |
| Full bootstrap / periodic review | ~18,000–25,000 |
