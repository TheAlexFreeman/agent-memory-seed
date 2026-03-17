# Session checklists

Compact runbooks for session start and end. See README.md for full bootstrap and reflection protocols. These checklists are implemented as executable skills in `skills/session-start.md`, `skills/session-sync.md`, and `skills/session-wrapup.md`.

## First session

If this is the very first session (no user profile, no chat history), follow `meta/first-run.md` instead of the checklists below. It condenses the bootstrap into a streamlined silent setup + interactive onboarding flow.

## Session start (returning sessions)

This is the **compact path** for agents who have already completed the full bootstrap at least once. On first instantiation, follow the full bootstrap sequence in README.md instead.

1. Read `README.md`, `identity/SUMMARY.md`, and `meta/quick-reference.md`. Consult `meta/curation-policy.md` and `meta/update-guidelines.md` as-needed during the session — you do not need to re-read them in full.
2. **Check write access.** If you cannot write to the repo, follow `meta/update-guidelines.md` § "Read-only operation" and prepare to output a deferred-action summary at session end.
3. Read `knowledge/SUMMARY.md`, `skills/SUMMARY.md`, and `chats/SUMMARY.md` for accumulated context. Skip any that are empty.
4. Greet the user and ask if anything important has changed since the last session.

For the full executable workflow, see `skills/session-start.md`.

## Mid-session sync

Use `skills/session-sync.md` when the user requests a checkpoint or when a long session has accumulated significant decisions worth persisting before session end.

## Session end

1. **Chat summary** — Write or update the summary for this chat (and daily/monthly/yearly summaries if due) per the compression hierarchy in README § "Summaries".
2. **Reflection note** — Write `reflection.md` in this session's chat folder. See README § "Session reflection" for the canonical format.
3. **ACCESS.jsonl** — Append an entry for every content file you retrieved from identity/, knowledge/, skills/, or chats/ during this session. See README § "Memory curation" for the canonical format. Include `session_id` whenever the chat folder is known.
4. **If read-only** — Produce a deferred-action summary listing all ACCESS entries, review-queue items, and summary updates the user should apply (see `meta/update-guidelines.md` § "How to communicate deferred actions").

For the full executable workflow, see `skills/session-wrapup.md`.
