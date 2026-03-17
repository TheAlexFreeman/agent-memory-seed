# Session checklists

Compact runbooks for session start and end. For normal returning sessions, this file is the authoritative runtime guide. Read README.md, CHANGELOG.md, and the full governance docs only on first run, during periodic review, or when a task touches the memory system itself or protected changes. These checklists are implemented as executable skills in `skills/session-start.md`, `skills/session-sync.md`, and `skills/session-wrapup.md`.

## First session

If this is the very first session (no user profile, no chat history), follow `meta/first-run.md` instead of the checklists below. It condenses the bootstrap into a streamlined silent setup plus interactive onboarding flow.

## Session start

1. **Check for first run.** If there is no confirmed portrait and no chat history, stop and follow `meta/first-run.md`.
2. **Load live runtime state.** Read `meta/quick-reference.md`.
3. **Load only the relevant summaries.** Read `identity/SUMMARY.md`, the most recent relevant chat summary, and any `knowledge/` or `skills/` summaries needed to continue the user's current work. Do not load unrelated files yet.
4. **Check pending items.** Read `meta/review-queue.md` if pending proposals, aggregation work, or periodic review might matter for this session.
5. **Check write access.** If you cannot write to the repo, follow `meta/update-guidelines.md` § "Read-only operation" and prepare to output a deferred-action summary at session end.
6. **Escalate to the heavy docs only when needed.** Read README.md, CHANGELOG.md, `meta/curation-policy.md`, and `meta/update-guidelines.md` only if the task touches memory/governance/protected writes, the summaries are insufficient, or periodic review is due.
7. Greet the user and ask if anything important has changed since the last session.

For the full executable workflow, see `skills/session-start.md`.

## Mid-session sync

Use `skills/session-sync.md` when the user requests a checkpoint or when a long session has accumulated significant decisions worth persisting before session end.

## Session end

1. **Chat summary** — Write or update the summary for this chat (and daily/monthly/yearly summaries if due) per the compression hierarchy in README § "Summaries".
2. **Reflection note** — Write `reflection.md` in this session's chat folder (README § "Session reflection").
3. **ACCESS.jsonl** — Append an entry for every content file you retrieved from identity/, knowledge/, skills/, or chats/ during this session (README § "Memory curation"). Include `session_id` whenever the chat folder is known.
4. **If read-only** — Produce a deferred-action summary listing all ACCESS entries, review-queue items, and summary updates the user should apply (see `meta/update-guidelines.md` § "How to communicate deferred actions").

For the full executable workflow, see `skills/session-wrapup.md`.
