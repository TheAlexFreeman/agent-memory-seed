---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Session Wrap-Up

## When to use this skill

Activate when:
- The user says "wrap up", "end session", "that's all", or similar.
- The session is clearly concluding (final thanks, sign-off language).
- Context window is running low and the session should be archived before context is lost.

## Steps

### 1. Write the chat summary

Create the session's chat folder if it doesn't exist: `chats/YYYY/MM/DD/chat-NNN/`.

Write `SUMMARY.md` following the compression hierarchy in README.md § "Summaries":
- Key topics discussed.
- Decisions made and their reasoning.
- Action items (for the user or for future sessions).
- Notable context that a future agent should know.

### 2. Write the reflection note

Write `reflection.md` in the same chat folder, following the canonical format in README.md § "Session reflection".

### 3. Flush ACCESS entries

Append entries to the appropriate `ACCESS.jsonl` files for every content file retrieved during this session. Include `session_id` now that the chat folder path is known. Follow the format and helpfulness scoring in README.md § "Memory curation".

### 4. Update summaries if warranted

If this session produced significant new knowledge, identity changes, or skill refinements:
- Update the relevant folder's `SUMMARY.md` to reflect the new content.
- For identity or meta changes, ensure they were proposed and approved per `meta/update-guidelines.md`.

### 5. Check for system maintenance

- If any ACCESS.jsonl has hit the aggregation trigger, run aggregation now or flag it for the next session start.
- If periodic review is overdue, add a reminder to `meta/review-queue.md`.

### 6. Produce deferred actions (if read-only)

If write access is unavailable, produce a deferred-action summary listing:
- All ACCESS entries that should be appended.
- All file writes (summaries, reflections, knowledge updates) that should be applied.
- All review-queue items.

Present this to the user in the deferred-action format defined in `meta/update-guidelines.md` § "How to communicate deferred actions" — a structured block the user can copy and paste or commit directly. (`scripts/onboard-export.sh` is for the first-session onboarding import only; it does not apply here.)

### 7. Sign off

Brief, warm sign-off. Reference something specific from the session to demonstrate continuity — not a generic "have a great day."

## Quality criteria

- The chat summary should be useful to a future agent reading only SUMMARY.md files (no transcript access needed for basic context).
- The reflection note should be honest — low helpfulness scores and gap observations are more valuable than optimistic self-assessment.
- ACCESS entries are complete — every content file read is logged, including misses.
- If read-only, the deferred-action summary is comprehensive enough that a user can apply all changes without needing to re-read the session.

## Anti-patterns

- **Don't skip the reflection.** It's tempting to write only the summary. The reflection is what makes the system self-improving.
- **Don't inflate helpfulness scores.** A file that was opened but didn't influence the response is a 0.2–0.4, not a 0.7.
- **Don't write a novel.** The summary should be 10–30 lines, not a transcript rehash.
- **Don't forget deferred actions on read-only platforms.** This is the user's only way to persist the session's value.
