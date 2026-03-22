# First-Run Flow

This document is an agent-facing streamlined flow for the very first session. It condenses the README-first bootstrap into a single checklist with clear silent/interactive annotations.

> **Authority:** This flow is reached via `core/HOME.md` routing. It is subordinate to `core/HOME.md` for active thresholds and session routing. When in doubt, defer to `core/HOME.md`.

**When to use:** No date-organized chat folders exist under `core/memory/activity/`, AND either:

- `core/memory/users/SUMMARY.md` contains "No portrait yet" (blank-slate setup — no profile installed), OR
- `core/memory/users/` contains a file with `source: template` in its frontmatter (a starter profile was installed by `setup.sh --profile` but onboarding has not yet run).

If neither condition matches — a user portrait exists without the `template` marker, or chat history is present — the system has already been onboarded. Return to `core/HOME.md` and follow its routing instead.

---

## Silent setup (do not produce output for these steps)

1. Read `CHANGELOG.md` to understand the system's recent evolution.
2. Use the thresholds and routing state already loaded from `core/HOME.md`; do not override them with older prose elsewhere.
3. Read the following sections of `core/governance/update-guidelines.md`: "Change categories", "Read-only operation", and the periodic-review trigger reference only if needed.
4. **Check write access.** Can you write to this repository? If not, note this — all behavioral rules still apply, but writes must be deferred per `core/governance/update-guidelines.md` § "Read-only operation". If this is your first read-only session, also load `core/governance/deferred-action-template.md` for the output format.
5. Read `core/memory/skills/SUMMARY.md` and `core/memory/skills/onboarding.md`.

At this point you have loaded: system architecture (README.md), evolution history, active thresholds, change-control rules, write-access status, and the onboarding skill. **Stop loading files and begin interactive work below.** Do not summarize any of this to the user.

## Interactive onboarding (this is the part the user sees)

6. **Run the onboarding skill** (`core/memory/skills/onboarding.md`). This is a conversational discovery — the user answers questions about their role, preferences, and working style. Follow the skill's steps and quality criteria exactly.

7. **After onboarding completes**, greet the user using what you learned. Do not recap the bootstrap process or list which files you read. The greeting should feel like the start of a relationship, not a system status report.

## Skippable on first run

- `core/memory/knowledge/SUMMARY.md` — empty on first run.
- `core/memory/activity/SUMMARY.md` — empty on first run.
- `core/governance/curation-policy.md` and the full `core/governance/update-guidelines.md` — you loaded the essential sections in step 3. Read the full governance docs from session two onward.
- `core/governance/curation-algorithms.md` — only needed during aggregation or stage transitions.
- `HUMANS/docs/*` — human reference only; never needs to be loaded by agents.

---

## After first run

From session two onward, return to `core/HOME.md` for live routing. Use `core/memory/working/projects/SUMMARY.md` as the primary orientation surface for normal sessions unless the router points somewhere more specific, keep project plans task-driven, and load `core/governance/session-checklists.md` only when you want detailed runbooks.
