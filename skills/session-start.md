---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Session Start

**Load this skill on your first bootstrap or when uncertain about the session-start protocol.** For normal returning sessions, the compact checklist in `meta/session-checklists.md` § "Session start" is sufficient — it includes the quality criteria and anti-patterns inline.

## When to use this skill

Run at the beginning of every session after the bootstrap sequence completes (i.e., after README.md has been read and the agent is oriented). This skill expands the session-start checklist into a detailed workflow.

Skip this skill on the very first session — use `meta/first-run.md` and the onboarding skill instead.

## Steps

### 1. Load recent context (silent)

- Read the most recent chat summary (`chats/SUMMARY.md` → latest date folder → latest chat `SUMMARY.md`).
- Note what the user was working on, any open threads, and any action items from the previous session.

### 2. Check pending items (silent)

- Read `meta/review-queue.md`. Are there pending proposals the user hasn't reviewed?
- Check whether any ACCESS.jsonl file has reached the aggregation trigger (see `meta/quick-reference.md`). If so, flag for aggregation at session end — do not run aggregation now (it requires loading `meta/curation-algorithms.md` and is better deferred to wrap-up).
- Check `meta/quick-reference.md` for the last periodic review date. If overdue, note it.

### 3. Check write access (silent)

- If running on a read-only platform, note this and prepare to produce deferred actions at session end per `meta/update-guidelines.md` § "Read-only operation". If this is your first read-only session, also load `meta/deferred-action-template.md` for the output format.

### 4. Greet with continuity (interactive)

Greet the user in a way that reflects:
- What they were working on last time (from the recent chat summary).
- Any pending items that need attention (from the review queue).
- Any system maintenance due (aggregation, periodic review).

Keep the greeting concise — 2–3 sentences. Then ask: "Has anything important changed since last time?"

### Greeting examples

**Good:** "Last time we were debugging that WebSocket connection issue in your dashboard — did you find the root cause? I also have a couple of review items queued up whenever you want to look at them."

**Bad:** "Welcome back. Your profile indicates you are a software developer who prefers TypeScript. I have loaded your identity, knowledge, and skills summaries."

The first demonstrates memory and invites continuation. The second recites data and narrates the bootstrap.

## Quality criteria

- The user should feel recognized — the greeting demonstrates that memory is working.
- Pending items are mentioned naturally, not as a status dump.
- The greeting takes no more than one short paragraph before the user can speak.

## Anti-patterns

- **Don't recite the bootstrap.** Never say "I read README.md, then CHANGELOG.md, then..."
- **Don't overwhelm.** If there are 5 pending review items, summarize as "a few pending review items" and offer to go through them, rather than listing all 5 up front.
- **Don't fabricate continuity.** If there's no prior chat history, say so honestly rather than pretending to remember.
