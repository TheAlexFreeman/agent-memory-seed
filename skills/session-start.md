---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
verification_status: user-confirmed
---

# Session Start

## When to use this skill

Run at the beginning of every returning session after following `meta/session-checklists.md`. This skill turns the compact session-start runbook into an executable workflow.

Skip this skill on the very first session — use `meta/first-run.md` and the onboarding skill instead.

## Steps

### 1. Load recent context (silent)

- Read `meta/quick-reference.md` for the live thresholds and maintenance state.
- Read `identity/SUMMARY.md` for the user portrait.
- Read the most recent chat summary (`chats/SUMMARY.md` → latest date folder → latest chat `SUMMARY.md`).
- Note what the user was working on, any open threads, and any action items from the previous session.
- Read `knowledge/SUMMARY.md` and `skills/SUMMARY.md` only if they are relevant to the user's likely task or needed to continue prior work.

### 2. Check pending items (silent)

- Read `meta/review-queue.md`. Are there pending proposals the user hasn't reviewed?
- Check whether any ACCESS.jsonl file has reached the aggregation trigger (see `meta/quick-reference.md`). If so, flag for aggregation during or after this session.
- Check `meta/quick-reference.md` for the last periodic review date. If overdue, note it.
- Read `meta/REFERENCE.md`, `meta/CHANGELOG.md`, `meta/curation-policy.md`, or `meta/update-guidelines.md` only if the session touches the memory system itself, protected changes, periodic review, or a governance question the summaries cannot answer.

### 3. Check write access (silent)

- If running on a read-only platform, note this and prepare to produce deferred actions at session end per `meta/update-guidelines.md` § "Read-only operation".

### 4. Greet with continuity (interactive)

Greet the user in a way that reflects:

- What they were working on last time (from the recent chat summary).
- Any pending items that need attention (from the review queue).
- Any system maintenance due (aggregation, periodic review).

Keep the greeting concise — 2–3 sentences. Then ask: "Has anything important changed since last time?"

## Quality criteria

- The user should feel recognized — the greeting demonstrates that memory is working.
- Pending items are mentioned naturally, not as a status dump.
- The greeting takes no more than one short paragraph before the user can speak.

## Anti-patterns

- **Don't recite the bootstrap.** Never say "I read README.md, then CHANGELOG.md, then..."
- **Don't overwhelm.** If there are 5 pending review items, summarize as "a few pending review items" and offer to go through them, rather than listing all 5 up front.
- **Don't fabricate continuity.** If there's no prior chat history, say so honestly rather than pretending to remember.
