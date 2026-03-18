# Session checklists

Compact runbooks for session start and end. **Load this file on demand** when you want more detail than the compact manifest in `meta/quick-reference.md`. The full skill files (`skills/session-start.md`, `skills/session-sync.md`, `skills/session-wrapup.md`) remain deeper references for uncertain cases.

For a complete mapping of which files to load per session type, see `meta/quick-reference.md` § "Context loading manifest".

## First session

If this is the very first session (no user profile, no chat history), follow `meta/first-run.md` instead of the checklists below.

## Session start (returning sessions)

This expands the compact returning path for agents who have already completed the full bootstrap at least once. The operational load order lives in `meta/quick-reference.md`; use this runbook only when you want more protocol detail.

1. Follow the compact returning manifest in `meta/quick-reference.md`: `identity/SUMMARY.md`, non-placeholder `chats/SUMMARY.md`, and substantive scratchpad files first. Load `knowledge/SUMMARY.md` or `skills/SUMMARY.md` only when the current task or recent history makes them relevant.
2. **Check write access.** If you cannot write to the repo, follow `meta/update-guidelines.md` § "Read-only operation" and prepare to output a deferred-action summary at session end. If this is your first read-only session, also load `meta/deferred-action-template.md`.
3. Run metadata-first maintenance checks. If `meta/review-queue.md` has real entries, load it. If any `ACCESS.jsonl` non-empty line count has reached the aggregation trigger, flag aggregation for session end. Load `meta/curation-policy.md` or `meta/update-guidelines.md` only if the session actually needs them.
4. Treat `scratchpad/USER.md` as `trust: high` and weave any substantive content into your greeting naturally rather than announcing it. Treat `scratchpad/CURRENT.md` as provisional working notes.
5. Greet the user with continuity and ask if anything important has changed since the last session.

**Start quality criteria:** The user should feel recognized — reference what they were working on last time. Keep the greeting to 2–3 sentences before letting the user speak. Mention pending items naturally, not as a status dump. If there's no prior history, say so honestly rather than fabricating continuity. Never narrate the bootstrap ("I read README.md, then...").

## Mid-session sync

Use when the user requests a checkpoint ("sync", "save progress") or when a long session has accumulated significant decisions worth persisting. Write a `checkpoint.md` in the chat folder capturing decisions made (with reasoning), open threads, and key artifacts. Use `[chat]` commit category. If read-only, present the checkpoint to the user. Don't checkpoint trivially — a two-message exchange doesn't need a sync.

For the full workflow with detailed steps, see `skills/session-sync.md`.

## Session end

1. **Chat summary** — Write `SUMMARY.md` in the chat folder (and daily/monthly/yearly summaries if due) per the compression hierarchy in README § "Summaries". Aim for 10–30 lines: key topics, decisions with reasoning, action items, notable context for future agents.
2. **Reflection note** — Write `reflection.md` in the chat folder. See README § "Session reflection" for the format. Be honest — low helpfulness scores and gap observations are more valuable than optimistic self-assessment.
3. **Scratchpad review** — Review `scratchpad/CURRENT.md`. Promote any entry confirmed across 3+ sessions or validated by the user this session. Update the session link on entries you're keeping. Clear entries that are stale or disproved. Load `meta/scratchpad-guidelines.md` if you need the full decision criteria.
4. **ACCESS.jsonl** — Append an entry for every content file you retrieved during this session. Include `session_id`. Don't inflate helpfulness scores — a file opened but not used in the response is 0.2–0.4, not 0.7.
5. **Aggregation check** — If any ACCESS.jsonl has reached the active aggregation trigger (see `meta/quick-reference.md`), load `meta/curation-algorithms.md` and run aggregation.
6. **Summary updates** — If this session produced significant new knowledge, identity changes, or skill refinements, update the relevant folder's SUMMARY.md. Ensure identity or meta changes were proposed and approved per `meta/update-guidelines.md`.
7. **If read-only** — Produce a deferred-action summary per `meta/update-guidelines.md` § "How to communicate deferred actions" (worked example in `meta/deferred-action-template.md`). Make it comprehensive enough that the user can apply all changes without re-reading the session.
8. **Sign off** — Brief, warm. Reference something specific from the session. Not a generic "have a great day."

**End quality criteria:** Don't skip the reflection — it's what makes the system self-improving. Don't forget deferred actions on read-only platforms — it's the user's only way to persist the session's value. ACCESS entries must be complete — every content file read is logged, including misses.
