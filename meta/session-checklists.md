# Session checklists

Compact runbooks for session start and end. See README.md for full bootstrap and reflection protocols.

## Session start

1. Run the **bootstrap sequence** in README § "Bootstrap sequence", including the first-run branch that loads change-control rules and checks write access before onboarding writes are considered.
2. **Check write access.** If you cannot write to the repo, follow `meta/update-guidelines.md` § "Read-only operation" and prepare to output a deferred-action summary at session end.
3. Greet the user and ask if anything important has changed since the last session.

## Session end

1. **Chat summary** — Write or update the summary for this chat (and daily/monthly/yearly summaries if due) per the compression hierarchy in README § "Summaries".
2. **Reflection note** — Write `reflection.md` in this session's chat folder (README § "Session reflection").
3. **ACCESS.jsonl** — Append an entry for every content file you retrieved from identity/, knowledge/, skills/, or chats/ during this session (README § "Memory curation"). Include `session_id` whenever the chat folder is known.
4. **If read-only** — Produce a deferred-action summary listing all ACCESS entries, review-queue items, and summary updates the user should apply (see `meta/update-guidelines.md` § "How to communicate deferred actions").
