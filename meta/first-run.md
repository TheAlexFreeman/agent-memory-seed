# First-Run Flow

This document is an agent-facing streamlined flow for the very first session. It condenses bootstrap steps 1–9 from README.md into a single checklist with clear silent/interactive annotations.

**When to use:** No date-organized chat folders exist under `chats/`, AND either:

- `identity/SUMMARY.md` contains "No portrait yet" (blank-slate setup — no profile installed), OR
- `identity/` contains a file with `source: template` in its frontmatter (a starter profile was installed by `setup.sh --profile` but onboarding has not yet run).

If neither condition matches — a user portrait exists without the `template` marker, or chat history is present — the system has already been onboarded. Use `meta/session-checklists.md` for normal returning sessions and consult `meta/REFERENCE.md` when you need the full architecture or governance reference.

---

## Silent setup (do not produce output for these steps)

1. Skim the 2–3 most recent entries in `meta/CHANGELOG.md` for context on recent changes. The full history is reference, not required for first-run.
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

From session two onward, use `meta/session-checklists.md` for the normal returning-session runbook. Read `meta/REFERENCE.md`, `meta/CHANGELOG.md`, and the full governance docs only when a task touches the memory system itself, protected changes, or periodic review.
