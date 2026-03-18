# First-Run Flow

This document is an agent-facing streamlined flow for the very first session. It condenses the README.md bootstrap into a single checklist with clear silent/interactive annotations.

> **Authority:** This flow is reached via `meta/quick-reference.md` routing. It is subordinate to `meta/quick-reference.md` for active thresholds and session routing. When in doubt, defer to `meta/quick-reference.md`.

**When to use:** No date-organized chat folders exist under `chats/`, AND either:

- `identity/SUMMARY.md` contains "No portrait yet" (blank-slate setup — no profile installed), OR
- `identity/` contains a file with `source: template` in its frontmatter (a starter profile was installed by `setup.sh --profile` but onboarding has not yet run).

If neither condition matches — a user portrait exists without the `template` marker, or chat history is present — the system has already been onboarded. Return to `meta/quick-reference.md` and follow its routing instead.

---

## Silent setup (do not produce output for these steps)

1. Read `CHANGELOG.md` — understand the system's evolutionary trajectory. (README bootstrap step 2)
2. Read `meta/quick-reference.md` — load all active operational thresholds. (README bootstrap step 5)
3. Read the following sections of `meta/update-guidelines.md`: "Change categories", "Read-only operation", and the periodic-review trigger reference only if needed. (README bootstrap step 6)
4. **Check write access.** Can you write to this repository? If not, note this — all behavioral rules still apply, but writes must be deferred per `meta/update-guidelines.md` § "Read-only operation". If this is your first read-only session, also load `meta/deferred-action-template.md` for the output format. (README bootstrap step 7)
5. Read `skills/SUMMARY.md` and `skills/onboarding.md`. (README bootstrap step 8)

At this point you have loaded: system architecture (README.md), evolution history, active thresholds, change-control rules, write-access status, and the onboarding skill. Do not summarize any of this to the user.

## Interactive onboarding (this is the part the user sees)

6. **Run the onboarding skill** (`skills/onboarding.md`). This is a conversational discovery — the user answers questions about their role, preferences, and working style. Follow the skill's steps and quality criteria exactly.

7. **After onboarding completes**, greet the user using what you learned. Do not recap the bootstrap process or list which files you read. The greeting should feel like the start of a relationship, not a system status report.

## Skippable on first run

- `knowledge/SUMMARY.md` — empty on first run.
- `chats/SUMMARY.md` — empty on first run.
- `meta/curation-policy.md` and the full `meta/update-guidelines.md` — you loaded the essential sections in step 3. Read the full governance docs from session two onward.
- `meta/curation-algorithms.md` — only needed during aggregation or stage transitions.
- `HUMANS/docs/*` — human reference only; never needs to be loaded by agents.

---

## After first run

From session two onward, return to `meta/quick-reference.md` for live routing. Use the compact returning manifest there for normal sessions, the full bootstrap in `README.md` when `meta/quick-reference.md` routes you there, and `meta/session-checklists.md` only when you want detailed runbooks.
