# Quick Reference

**Read this file at the start of every session before applying any thresholds or curation rules.**

This is the single authoritative source for the system's currently active operational parameters. It is updated during each periodic review after a maturity assessment. All other threshold values in `curation-policy.md` and `README.md` are reference values shown for illustration — the values below are what actually governs the live system. `meta/system-maturity.md` is a reference used to assess maturity and choose the next parameter set; it is not the live runtime config.

## Architectural guardrails for system changes

When you are reviewing or modifying the system itself, treat **consistency**, **user-friendliness**, and **context efficiency** as architectural guardrails. Keep authority files aligned, preserve the compact returning path, and make tradeoffs explicit when a change helps one dimension at the expense of another.

---

## Session routing

Use this file as the operational router for every session:

1. Start here.
2. If this is a fresh instantiation on a blank or template-backed repo, read `README.md` and then `meta/first-run.md`.
3. If this is a fresh instantiation on a returning system, or you intentionally need the full governance stack, read `README.md` and then follow the **Full bootstrap** manifest below.
4. Otherwise, use the **Compact returning** manifest below and keep additional loads task-driven.

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

**Do not load** `HUMANS/docs/*` (human reference only) or `meta/curation-algorithms.md` (on-demand only — see above). `meta/session-checklists.md` and `meta/scratchpad-guidelines.md` are also on-demand — load them only when you need detailed runbooks, session-end scratchpad review criteria, or extra protocol detail.

### Compact returning notes

- Run metadata-first maintenance probes before loading extra governance files:
  - Check whether `meta/review-queue.md` still contains only its placeholder. Load the body only when real entries exist or the user asks about it.
  - Count non-empty lines in `ACCESS.jsonl` files to see whether any folder has reached the aggregation trigger. Load entries only when a trigger is hit or the current task requires retrieval analysis.
- `knowledge/SUMMARY.md` and `skills/SUMMARY.md` are task-driven context, not unconditional startup reads.

---

## Current active stage: Exploration

_Last assessed: 2026-03-19 — Exploration retained (all 6 signals within bounds)_

**Exploration defaults apply** — use the threshold values in the Active thresholds table below until a periodic review triggers a stage transition.

## Last periodic review

**Date:** 2026-03-19

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

**Full algorithm details:** See `meta/curation-algorithms.md` (load only when running aggregation or a stage transition).

---

## Decision guide: trust decay

Trust level sets the **decay threshold** (how long before action is taken). The **effective verification date** determines actual staleness. These are independent — a high-trust file can still be stale, and a low-trust file can be fresh. See `meta/curation-policy.md` § "Freshness vs. confidence" for the full rationale.

### `trust: low` file

1. Has the effective verification date (`last_verified` if set, otherwise `created`) gone unupdated for more than **120 days**? → Archive to `knowledge/_archive/`, remove from SUMMARY.md, log as `[curation]` commit.
2. Otherwise → retain.

### `trust: medium` file

1. Has the effective verification date (`last_verified` if set, otherwise `created`) gone unupdated for more than **180 days**? → Flag in `meta/review-queue.md` for re-verification or demotion.
2. If demoted to `low` → the 120-day low-trust retirement clock starts from the demotion date.
3. Otherwise → retain.

### `trust: high` file

1. Is the effective verification date (`last_verified` if set, otherwise `created`) older than **365 days**? → Mention in periodic review for a freshness check (informational — no automatic action).
2. Otherwise → no action needed.

**Effective verification date:** Use `last_verified` when present; otherwise use `created`.

**Definition of "unverified":** Files with no `last_verified` yet are still unverified. Their decay clock starts at `created`. Any user interaction that confirms the content (explicit approval, correction, or re-confirmation) sets or updates `last_verified` and resets the clock.

**Files without frontmatter:** Treated as `trust: medium`. When adding frontmatter retroactively: if the backfill is mechanical (adding metadata without verifying content), omit `last_verified` — the decay clock runs from `created`. If the original creation date is unknown, use the backfill date as `created`. Only set `last_verified` to the backfill date if the reviewer actually reads and verifies the content during backfill. See `meta/update-guidelines.md` § "Retroactive application" for the full policy.

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
4. Scans for cross-folder co-retrieval clusters using the active task similarity method (currently: **session co-occurrence**). For the full algorithm, load `meta/curation-algorithms.md`.
5. Archives **all processed entries** to `ACCESS.archive.jsonl` and resets `ACCESS.jsonl` to empty. The archive is the historical record used for staleness detection across aggregation cycles.

**Entry counting rule:** Always count entries in the current `ACCESS.jsonl` file (not the archive). After each aggregation, `ACCESS.jsonl` is reset to empty, so all entries in it are by definition accumulated since the last aggregation. The archive is append-only and used only for historical staleness detection.

**For the full aggregation procedure,** see `meta/curation-algorithms.md` § "Aggregation runbook."

---

## Helpfulness scoring guide

`helpfulness` is the agent's judgment of whether a retrieval was useful to producing the session's responses, on a 0.0–1.0 scale:

| Range   | Meaning                                                                          | Example                                                |
| ------- | -------------------------------------------------------------------------------- | ------------------------------------------------------ |
| 0.0–0.1 | **Wrong context.** Irrelevant or retrieved in error.                             | Retrieved "React patterns" for a React Native query    |
| 0.2–0.4 | **Near-miss.** Right neighborhood but not incorporated.                          | Opened a related file but used a different one instead |
| 0.5–0.6 | **Useful context.** Directly relevant, informed the response but wasn't central. | Provided background that shaped framing                |
| 0.7–0.8 | **Highly relevant.** Shaped a key decision or was directly used.                 | File content was quoted or directly applied            |
| 0.9–1.0 | **Critical.** Response would be significantly worse without this file.           | Core reference that the answer depended on             |

Score what actually happened, not what should have happened. A high-quality file that wasn't needed for this particular task is a 0.2, not a 0.7.

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

| Session mode                     | Typical token cost | When                                                                                                      |
| -------------------------------- | ------------------ | --------------------------------------------------------------------------------------------------------- |
| First-run onboarding bootstrap   | ~15,000–20,000     | Fresh model instantiation on a blank or template-backed repo                                              |
| Returning compact session        | ~3,000–7,000       | Normal day-to-day use via the compact returning manifest in this file                                     |
| Full bootstrap / periodic review | ~18,000–25,000     | Fresh model on a returning system, or sessions that reopen the full governance stack and review artifacts |

For models with context windows under 32k, prefer the compact returning manifest in this file after the first session. As a guideline, bootstrap files should consume no more than ~15% of the model's effective context window.
