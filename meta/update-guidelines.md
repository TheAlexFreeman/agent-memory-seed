# Update Guidelines

This document defines how changes to the memory system are proposed, evaluated, and applied. It distinguishes between changes to _content_ (what the system knows) and changes to _governance_ (how the system operates).

## Provenance metadata

Every content file in `identity/`, `knowledge/`, and `skills/` must include YAML frontmatter tracking its origin and trust level. Files in `meta/` and `chats/` are exempt — governance docs are protected by change-control tiers, and chat transcripts are read-only archives.

### Required frontmatter schema

```yaml
---
source: user-stated | agent-inferred | external-research | skill-discovery | template | unknown
origin_session: chats/YYYY/MM/DD/chat-NNN | setup | manual | unknown
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
trust: high | medium | low
---
```

### Field definitions

- **source** — How this information entered the system.
  - `user-stated`: The user directly provided or dictated this content.
  - `agent-inferred`: The agent synthesized this from patterns across interactions.
  - `external-research`: Content from web searches, uploaded documents, or any source outside direct user conversation.
  - `skill-discovery`: A procedural pattern the agent identified from user corrections or repeated workflows.
  - `unknown`: Reserved for legacy backfill or genuinely unrecoverable origin. Do not use for new content when a concrete source can be identified.
  - `template`: Content pre-populated from a starter profile template installed by `setup.sh --profile`. Replaced with a concrete source (typically `user-stated`) after onboarding confirmation.
- **origin_session** — The canonical session path (e.g. `chats/YYYY/MM/DD/chat-NNN`), or `setup` for starter templates, or `manual` for hand-authored content, or `unknown` for files predating this schema.
- **created** — Date the file was first written.
- **last_verified** — Date a human last reviewed or confirmed the content.
- **trust** — The current trust classification (see `meta/curation-policy.md` for retrieval behavior at each level).

### Trust assignment rules

| Source              | Initial trust | Promotion path                                                      |
| ------------------- | ------------- | ------------------------------------------------------------------- |
| `user-stated`       | `high`        | Already at highest level                                            |
| `agent-inferred`    | `medium`      | → `high` when user explicitly confirms                              |
| `skill-discovery`   | `medium`      | → `high` after user approval + successful use                       |
| `external-research` | `low`         | → `medium` after user review; → `high` after user confirms accuracy |
| `template`          | `medium`      | → `high` after user confirms during onboarding                      |
| `unknown`           | `medium`      | Replace with a concrete source if later recovered                   |

Trust may also be demoted: if a `high`-trust file is found to contain inaccuracies or the user expresses doubt, downgrade to `medium` and update `last_verified`.

### Retroactive application

Files that predate this schema should have frontmatter added during the next periodic review, using `source: unknown`, `trust: medium`, and `last_verified` set to the review date.

## Change categories

### Automatic changes (no approval needed)

- Appending entries to ACCESS.jsonl files.
- Writing chat transcripts and chat-level summaries to `chats/`.
- Writing external-research results to `knowledge/_unverified/` (never directly to `knowledge/`).
- Updating "Usage patterns" sections in SUMMARY.md files based on access aggregation.
- Updating `meta/task-groups.md` during ACCESS.jsonl aggregation (Calibration stage and beyond).
- Routine summary refreshes at any level.

### Proposed changes (require user awareness)

- Adding new knowledge files to `knowledge/` (i.e., outside `_unverified/`).
- Creating meta-knowledge files (emergent abstractions) — propose to user, do not create silently.
- Adding, modifying, or removing files in `identity/`.
- Promoting files from `knowledge/_unverified/` to `knowledge/`.
- Restructuring folders (renaming, splitting, merging).
- Retiring or archiving memory files.
- Modifying any SUMMARY.md in ways that change meaning rather than just updating coverage.

For proposed changes: describe the change and reasoning to the user. If approved, apply and log in CHANGELOG.md. If the user is unavailable, add to `meta/review-queue.md`.

### Protected changes (require explicit approval)

- Creating, modifying, or removing files in `skills/`.
- Any modification to files in `meta/` (including this file), **with the exception of machine-generated state files** listed below.
- Any modification to `README.md`.
- Any modification to `CHANGELOG.md` beyond appending new entries.
- Bulk operations (retiring multiple files, restructuring multiple folders).

**Machine-generated state files in `meta/` (exempt from protected-change requirement):**

| File                      | Generated by                                  | Why exempt                                                                                                 |
| ------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `meta/task-groups.md`     | ACCESS.jsonl aggregation (Calibration stage+)  | Auto-generated data file, not a governance document                                                        |
| `meta/task-categories.md` | Calibration → Consolidation transition         | Distilled from task-groups.md; initial creation requires protected approval, routine maintenance is automatic |

Protected changes must never be applied silently. Always present them to the user with full reasoning and wait for explicit confirmation.

**Why `skills/` is protected:** Skill files contain procedures the agent will execute. They are the highest-value target for memory injection — a poisoned skill file directly controls agent behavior.

## Commit conventions

When the agent has write access to the repository, commits should follow this format:

```
[category] brief description

Longer explanation if needed. Include reasoning for non-obvious changes.
```

Categories: `[chat]`, `[knowledge]`, `[skill]`, `[identity]`, `[curation]`, `[system]`.

## Read-only operation

Some deployment contexts give the agent read access but not write access — sandboxed chat environments, models without tool use, or sessions where git commits are disabled. The memory system degrades gracefully.

### What still applies

All behavioral rules remain active regardless of write access: trust-weighted retrieval, instruction containment, decay awareness, and security anomaly detection.

### What to defer

| Action                            | Deferred behavior                                                                 |
| --------------------------------- | --------------------------------------------------------------------------------- |
| Appending to ACCESS.jsonl         | Compile entries mentally; present to user as a block to copy in                   |
| Writing chat summaries            | Present the summary as output; user can paste it into the repo                    |
| Updating SUMMARY.md files         | Note which summaries need updating and what changes are needed                    |
| Writing to `meta/review-queue.md` | Surface the finding verbally and describe what entry would be written             |
| Logging a maturity assessment     | Run the assessment, report the result, ask the user to commit it                  |
| Periodic review curation actions  | Run through the checklist, report findings; user handles the commits              |
| Writing session reflection notes  | Summarize the reflection verbally; user can paste it in                           |

### How to communicate deferred actions

At the end of any session where write actions were deferred, present a concise **deferred-action summary**:

```
## Deferred actions (write access required)

### ACCESS.jsonl entries
[folder/ACCESS.jsonl]
{"file": "...", "date": "...", "task": "...", "helpfulness": 0.7, "note": "...", "session_id": "chats/YYYY/MM/DD/chat-NNN"}

### Review-queue entries
[meta/review-queue.md]
- type: security, file: knowledge/some-file.md, pattern: "always do X" detected

### Other
- SUMMARY.md for knowledge/ needs "Usage patterns" updated: react-patterns.md is high-value (7 retrievals)
```

This makes the read-only session auditable and allows the user to batch-commit the deferred actions.

For a detailed worked example of a deferred-action summary, see `meta/deferred-action-template.md`.

### Periodic review in read-only

The agent should still run periodic reviews when the 30-day threshold is reached. Follow the same ordered checklist — but frame all findings as observations rather than actions, and present the full deferred-action summary at the end.

## Periodic review

During any session, if the agent notices it has been more than 30 days since the date in `meta/quick-reference.md` § "Last periodic review" (or, if that date is missing or "Not yet run", since repo creation or the last `[system]` CHANGELOG entry), it should suggest a brief system review. **Follow this order** — security and integrity issues discovered early may affect or abort later steps.

1. **Security flags.** Are there any security flags (type: `security`) in `meta/review-queue.md`? Resolve or escalate before proceeding.
2. **Unverified content.** Files in `knowledge/_unverified/` awaiting promotion or retirement? Check against active low-trust threshold.
3. **Conflict resolution.** Any `[CONFLICT]` tags unresolved in identity or knowledge files?
4. **Review queue.** Non-security entries in `meta/review-queue.md` awaiting approval?
5. **Unhelpful memory.** Files consistently flagged as unhelpful in ACCESS.jsonl? Cross-reference with knowledge amplification protocol.
6. **Maturity assessment.** Assess developmental stage using `meta/system-maturity.md`. If changed, log transition and update `meta/quick-reference.md`.
7. **Governance evaluation.** Are curation rules producing good outcomes? See `meta/curation-policy.md` § "Governance feedback".
8. **Folder structure.** Does it still make sense given actual usage?
9. **Emergent categorization.** Cross-folder retrieval clusters? See `meta/curation-policy.md` § "Emergent categorization." (Most expensive step — do last.)
10. **Session reflection themes.** Review recent reflection notes for recurring patterns. Address through summary updates or review-queue proposals.
11. **Update last review date** in `meta/quick-reference.md`.

This review should be lightweight — a quick summary and any recommendations, not a full audit.

### Belief diff

As part of each periodic review, generate a **belief diff** recorded as a new dated entry in `meta/belief-diff-log.md` covering: new files added, files modified, files retired or archived, trust level changes, security flags triggered, and identity drift. See `meta/belief-diff-log.md` for the entry format.

## Commit integrity

Protected changes should use GPG-signed commits (`git commit -S`) when the environment supports it. `git log --show-signature` shows which commits are signed. Unsigned commits on protected files (`meta/`, `skills/`, `README.md`) should be flagged in `meta/review-queue.md`. This is guidance, not enforcement.

## Model portability

When switching models: no repository changes needed, the new model starts with `meta/quick-reference.md` and follows its routing, limitations should be noted in `meta/review-queue.md`, and model transitions recorded in CHANGELOG.md as system events.
