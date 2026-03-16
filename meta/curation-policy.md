# Curation Policy

This document defines how memory is maintained, pruned, promoted, and retired. It is the immune system of the memory repo — preventing unbounded growth, information decay, and context pollution.

## The forgetting principle

Memory without forgetting degrades over time. Indiscriminate accumulation causes:
- Retrieval of stale information that contradicts current reality.
- Context pollution from irrelevant details crowding out relevant ones.
- Growing costs as more material must be searched and loaded.

**Forgetting is not failure. It is maintenance.**

## Lifecycle stages

Every piece of stored memory passes through these stages:

### 1. Capture
New information enters the system during a chat session. The agent identifies what is worth persisting based on the criteria in README.md ("What to store" / "What not to store").

### 2. Provisional storage
New memories are written with low confidence. Identity traits are tagged `[tentative]`. Knowledge files include a "Last verified" date. Skill files are marked as drafts until confirmed by successful use.

### 3. Confirmation
Through repeated access, user validation, or explicit approval, provisional memories are promoted to confirmed status. Confidence tags are upgraded. Skills are marked as tested.

### 4. Maintenance
Confirmed memories are periodically reviewed for staleness. Triggers for review:
- A file has not been accessed in 90+ days (check ACCESS.jsonl).
- The user contradicts information in the file.
- A related file has been significantly updated, potentially creating inconsistency.

### 5. Retirement
Memories that are stale, contradicted, or consistently unhelpful (low ACCESS.jsonl scores) are:
- **Demoted** — moved to an `_archive/` subfolder within their category, removed from the active SUMMARY.md, but retained in git history.
- **Merged** — consolidated into a broader file if the information is still partially relevant but too granular to justify its own file.
- **Deleted** — removed entirely if the information is wrong or the user requests it. Git history preserves the record.

## Access-driven curation

The ACCESS.jsonl feedback loop is the primary curation signal:

- **High access + high helpfulness:** Core memory. Ensure it stays current and prominent in summaries.
- **High access + low helpfulness:** Misleading memory. The file is being retrieved but isn't delivering value. Investigate — it may need updating, splitting, or better titling.
- **Low access + high helpfulness:** Hidden gem. When it's found, it's useful, but it's not being discovered. Improve the folder SUMMARY.md to surface it better.
- **Low access + low helpfulness:** Retirement candidate. Flag for review, and retire if the user confirms it's no longer relevant.

## Summary refresh cadence

- **Chat-level summaries:** Written immediately after each session.
- **Daily summaries:** Written at the end of each day with multiple sessions, or skipped for single-session days (the chat summary suffices).
- **Monthly summaries:** Written during the first session of a new month, reviewing the prior month.
- **Yearly summaries:** Written during the first session of a new year, reviewing the prior year.
- **Folder SUMMARY.md files:** Updated whenever ACCESS.jsonl aggregation is triggered (every 20 entries), or when significant new content is added.

## Size limits

Guidelines to prevent individual files from becoming unwieldy:

- **SUMMARY.md files:** Aim for 200–800 words. If a summary exceeds 1000 words, the folder probably needs restructuring.
- **Knowledge files:** Aim for 500–2000 words. Split into subfolders beyond that.
- **Skill files:** Aim for 300–1000 words. A skill that takes more than 1000 words to describe may actually be multiple skills.
- **Chat summaries:** 100–400 words per individual session. Be concise.

## Conflict resolution protocol

When new information conflicts with existing memory:

1. **Explicit correction wins.** If the user says "actually, I prefer X now," update immediately regardless of how well-established the old preference was.
2. **Recent observation wins over old inference.** A `[tentative]` tag from today outweighs an `[inferred]` tag from six months ago if they conflict.
3. **When uncertain, flag and ask.** Add both versions to the relevant file with a `[CONFLICT]` tag and raise it with the user at the next natural opportunity.
4. **Never silently discard.** Retiring memory is fine; doing so without leaving a trace is not. Git history is your safety net.
