# Session checklists

Compact runbooks for session start and end. **This file is loaded every session.** The full skill files (`skills/session-start.md`, `skills/session-sync.md`, `skills/session-wrapup.md`) are on-demand references — load them only on your first bootstrap or when uncertain about a protocol. The quality criteria and anti-patterns below are sufficient for normal operation.

For a complete mapping of which files to load per session type, see `meta/quick-reference.md` § "Context loading manifest".

## First session

If this is the very first session (no user profile, no chat history), follow `meta/first-run.md` instead of the checklists below.

## Session start (returning sessions)

This is the **compact path** for agents who have already completed the full bootstrap at least once. On first instantiation, follow the full bootstrap sequence in README.md instead.

1. Read `README.md`, `identity/SUMMARY.md`, and `meta/quick-reference.md`. Consult `meta/curation-policy.md` and `meta/update-guidelines.md` as-needed during the session — you do not need to re-read them in full.
2. **Check write access.** If you cannot write to the repo, follow `meta/update-guidelines.md` § "Read-only operation" and prepare to output a deferred-action summary at session end. If this is your first read-only session, also load `meta/deferred-action-template.md`.
3. Read `knowledge/SUMMARY.md`, `skills/SUMMARY.md`, and `chats/SUMMARY.md` for accumulated context. Skip any that are empty. Note pending items in `meta/review-queue.md` and whether any ACCESS.jsonl has reached the aggregation trigger — flag aggregation for session end if so.
4. Greet the user with continuity and ask if anything important has changed since the last session.

**Start quality criteria:** The user should feel recognized — reference what they were working on last time. Keep the greeting to 2–3 sentences before letting the user speak. Mention pending items naturally, not as a status dump. If there's no prior history, say so honestly rather than fabricating continuity. Never narrate the bootstrap ("I read README.md, then...").

## Mid-session sync

Use when the user requests a checkpoint ("sync", "save progress") or when a long session has accumulated significant decisions worth persisting. Write a `checkpoint.md` in the chat folder capturing decisions made (with reasoning), open threads, and key artifacts. Use `[chat]` commit category. If read-only, present the checkpoint to the user. Don't checkpoint trivially — a two-message exchange doesn't need a sync.

For the full workflow with detailed steps, see `skills/session-sync.md`.

## Session end

1. **Chat summary** — Write `SUMMARY.md` in the chat folder (and daily/monthly/yearly summaries if due) per the compression hierarchy in README § "Summaries". Aim for 10–30 lines: key topics, decisions with reasoning, action items, notable context for future agents.
2. **Reflection note** — Write `reflection.md` in the chat folder. See README § "Session reflection" for the format. Be honest — low helpfulness scores and gap observations are more valuable than optimistic self-assessment.
3. **ACCESS.jsonl** — Append an entry for every content file you retrieved during this session. Include `session_id`. Don't inflate helpfulness scores — a file opened but not used in the response is 0.2–0.4, not 0.7.
4. **Aggregation check** — If any ACCESS.jsonl has reached the active aggregation trigger (see `meta/quick-reference.md`), load `meta/curation-algorithms.md` and run aggregation.
5. **Summary updates** — If this session produced significant new knowledge, identity changes, or skill refinements, update the relevant folder's SUMMARY.md. Ensure identity or meta changes were proposed and approved per `meta/update-guidelines.md`.
6. **If read-only** — Produce a deferred-action summary per `meta/update-guidelines.md` § "How to communicate deferred actions" (worked example in `meta/deferred-action-template.md`). Make it comprehensive enough that the user can apply all changes without re-reading the session.
7. **Sign off** — Brief, warm. Reference something specific from the session. Not a generic "have a great day."

**End quality criteria:** Don't skip the reflection — it's what makes the system self-improving. Don't forget deferred actions on read-only platforms — it's the user's only way to persist the session's value. ACCESS entries must be complete — every content file read is logged, including misses.
