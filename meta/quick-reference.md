# Quick Reference

**Read this file at the start of every session before applying any thresholds or curation rules.**

This is the single authoritative source for the system's currently active operational parameters. It is updated during each periodic review after a maturity assessment. All other threshold values in `curation-policy.md` and `README.md` are reference values shown for illustration — the values below are what actually governs the live system. `meta/system-maturity.md` is a reference used to assess maturity and choose the next parameter set; it is not the live runtime config.

---

## Current active stage: Exploration

_Last assessed: not yet assessed — Exploration defaults apply_

## Last periodic review

**Date:** _Not yet run_

The agent should update this date when completing a full periodic review (same checklist as in `meta/update-guidelines.md` § "Periodic review").

## Active thresholds

| Parameter                       | Active value          | Stage       |
| ------------------------------- | --------------------- | ----------- |
| Low-trust retirement threshold  | 120 days              | Exploration |
| Medium-trust flagging threshold | 180 days              | Exploration |
| Staleness trigger (no access)   | 120 days              | Exploration |
| Aggregation trigger             | 15 entries            | Exploration |
| Identity churn alarm            | 5 traits/session      | Exploration |
| Knowledge flooding alarm        | 5 files/day           | Exploration |
| Task similarity method          | Session co-occurrence | Exploration |
| Cluster co-retrieval threshold  | 3 sessions            | Exploration |

---

## Active task similarity method

**Method:** Session co-occurrence

**Grouping precedence:** Group ACCESS entries by `session_id` when present. If an entry predates `session_id`, fall back to `date` for backward compatibility.

**Default before first assessment:** Treat the system as Exploration and use the values recorded in this file.

---

## Decision guide: trust decay

### `trust: low` file

1. Has `last_verified` gone unupdated for more than **120 days**? → Archive to `knowledge/_archive/`, remove from SUMMARY.md, log as `[curation]` commit.
2. Otherwise → retain.

### `trust: medium` file

1. Has `last_verified` gone unupdated for more than **180 days**? → Flag in `meta/review-queue.md` for re-verification or demotion.
2. If demoted to `low` → the 120-day low-trust retirement clock starts from the demotion date.
3. Otherwise → retain.

### `trust: high` file

1. Is `last_verified` older than **365 days**? → Mention in periodic review for a freshness check (informational — no automatic action).
2. Otherwise → no action needed.

**Definition of "unverified":** `last_verified` has not been updated since the decay clock started. Any user interaction that confirms the content (explicit approval, correction, or re-confirmation) resets the clock.

---

## Decision guide: anomaly detection

| Signal                                                                            | Trigger              | Action                         |
| --------------------------------------------------------------------------------- | -------------------- | ------------------------------ |
| Identity traits changed in one session                                            | > **5** traits       | Flag in `meta/review-queue.md` |
| Knowledge files on same topic from `external-research`, same session or day       | > **5** files        | Flag in `meta/review-queue.md` |
| File with zero retrievals in last **120 days**, then 3+ retrievals in one session | Spike after dormancy | Flag in `meta/review-queue.md` |
| File retrieved 5+ times total but never explicitly approved by user               | 5 retrievals         | Flag in `meta/review-queue.md` |

---

## Decision guide: ACCESS.jsonl aggregation

Aggregate when entries accumulated since last aggregation reach **15**. Aggregation:

1. Updates SUMMARY.md files with refreshed usage patterns.
2. Identifies high-value files (5+ retrievals, mean helpfulness ≥ 0.7) → enrich per knowledge amplification protocol.
3. Identifies low-value files (3+ retrievals, mean helpfulness ≤ 0.3) → investigate for retirement.
4. Scans for cross-folder co-retrieval clusters using the active task similarity method (currently: **session co-occurrence** — groups entries by `session_id` when present, otherwise by legacy `date`, identifies file sets co-occurring in 3+ session-groups, and flags clusters of 3+ files from 2+ folders). See `meta/curation-policy.md` § "Task similarity definition" for the full algorithm.
5. Archives **all processed entries** to `ACCESS.archive.jsonl` and resets `ACCESS.jsonl` to empty. The archive is the historical record used for staleness detection across aggregation cycles.

**Entry counting rule:** Always count entries in the current `ACCESS.jsonl` file (not the archive). After each aggregation, `ACCESS.jsonl` is reset to empty, so all entries in it are by definition accumulated since the last aggregation. The archive is append-only and used only for historical staleness detection.

---

## How to update this file

After completing the maturity assessment during periodic review:

1. Update the **Current active stage** line above.
2. Update the **Last assessed** date.
3. Copy the parameter values from the matching stage table in `meta/system-maturity.md` into the Active thresholds table.
4. Update the concrete values in the decision guides to match.
5. Log the update as a `[system]` commit in `CHANGELOG.md`.

Stage parameter tables: see `meta/system-maturity.md` §§ "Stage 1: Exploration", "Stage 2: Calibration", "Stage 3: Consolidation".

---

## Context budget guideline

Use these rough planning numbers when deciding how much repo state to load:

| Session mode | Typical token cost | When |
| --- | --- | --- |
| First-run onboarding bootstrap | ~15,000–20,000 | Fresh model instantiation on a blank or template-backed repo |
| Returning compact session | ~2,000–5,000 | Normal day-to-day use via `meta/session-checklists.md` |
| Full bootstrap / periodic review | ~18,000–25,000 | Fresh model on a returning system, or sessions that reopen the full governance stack and review artifacts |

For models with context windows under 32k, prefer the compact returning-session checklist after the first session. As a guideline, bootstrap files should consume no more than ~15% of the model's effective context window.
