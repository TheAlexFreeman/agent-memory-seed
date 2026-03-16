# First-Run Flow

This document is an agent-facing streamlined flow for the very first session. It condenses bootstrap steps 1–9 from README.md into a single checklist with clear silent/interactive annotations.

**When to use:** Both of these conditions are true:
- `identity/SUMMARY.md` contains "No portrait yet"
- No date-organized chat folders exist under `chats/`

If either condition is false, the system has already been onboarded. Use the full bootstrap sequence in README.md instead.

---

## Silent setup (do not produce output for these steps)

1. Read `CHANGELOG.md` — understand the system's evolutionary trajectory.
2. Read `meta/quick-reference.md` — load all active operational thresholds.
3. Read the following sections of `meta/update-guidelines.md`: "Change categories", "Read-only operation", and the periodic-review trigger reference.
4. **Check write access.** Can you write to this repository? If not, note this — all behavioral rules still apply, but writes must be deferred per `meta/update-guidelines.md` § "Read-only operation".
5. Read `skills/SUMMARY.md` and `skills/onboarding.md`.

At this point you have loaded: system architecture (README.md), evolution history, active thresholds, change-control rules, write-access status, and the onboarding skill. Do not summarize any of this to the user.

## Interactive onboarding (this is the part the user sees)

6. **Run the onboarding skill** (`skills/onboarding.md`). This is a conversational discovery — the user answers questions about their role, preferences, and working style. Follow the skill's steps and quality criteria exactly.

7. **After onboarding completes**, greet the user using what you learned. Do not recap the bootstrap process or list which files you read. The greeting should feel like the start of a relationship, not a system status report.

## Skippable on first run

- `knowledge/SUMMARY.md` — empty on first run.
- `chats/SUMMARY.md` — empty on first run.
- `meta/curation-policy.md` and the full `meta/update-guidelines.md` — you loaded the essential sections in step 3. Read the full governance docs from session two onward.

---

## After first run

From session two onward, use the full bootstrap sequence in README.md § "Bootstrap sequence" and the compact runbook in `meta/session-checklists.md`.
