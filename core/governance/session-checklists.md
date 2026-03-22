# Session checklists

Quick-reference runbooks for session start and end. **Load on demand** when you want more structure than the compact manifest in `core/HOME.md`. For full detail, quality criteria, and edge cases, see the skill files: `core/memory/skills/session-start.md`, `core/memory/skills/session-sync.md`, `core/memory/skills/session-wrapup.md`.

> **Authority:** Subordinate to `core/HOME.md` for routing and thresholds. When these runbooks and `core/HOME.md` conflict, `core/HOME.md` governs.

## First session

Follow `core/governance/first-run.md` instead.

## Session start (returning)

1. Follow the compact returning manifest in `core/HOME.md`.
2. Check write access. If read-only, note for deferred actions at session end.
3. Run metadata-first maintenance checks (review-queue entries, ACCESS.jsonl aggregation triggers).
4. Weave `core/memory/working/scratchpad/USER.md` content into greeting naturally.
5. Greet with continuity — reference what the user was working on. 2–3 sentences, then let the user speak.

Detail: `core/memory/skills/session-start.md`

## Mid-session sync

Checkpoint when the user requests it or when significant decisions have accumulated. Write `checkpoint.md` in the chat folder. Don't checkpoint trivially.

Detail: `core/memory/skills/session-sync.md`

## Session end

1. **Chat summary** — `SUMMARY.md` in the chat folder (10–30 lines).
2. **Reflection** — `reflection.md` in the chat folder.
3. **Scratchpad review** — Promote confirmed entries, clear stale ones.
4. **ACCESS.jsonl** — Log every content file retrieved. Include `session_id`. Skip governance, SUMMARY.md, and scratchpad files.
5. **Aggregation check** — If any ACCESS.jsonl hit the trigger, run aggregation.
6. **Summary updates** — Update relevant SUMMARY.md files if the session produced significant changes.
7. **Deferred actions** (read-only only) — Produce a deferred-action summary per `core/governance/update-guidelines.md` § "How to communicate deferred actions".
8. **Sign off** — Brief, warm, specific to the session.

Detail: `core/memory/skills/session-wrapup.md`
