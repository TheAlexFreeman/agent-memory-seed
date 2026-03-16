# Update Guidelines

This document defines how changes to the memory system are proposed, evaluated, and applied. It distinguishes between changes to *content* (what the system knows) and changes to *governance* (how the system operates).

## Change categories

### Automatic changes (no approval needed)
- Appending entries to ACCESS.jsonl files.
- Writing chat transcripts and chat-level summaries to `chats/`.
- Adding new knowledge files to `knowledge/`.
- Updating "Usage patterns" sections in SUMMARY.md files based on access aggregation.
- Routine summary refreshes at any level.

### Proposed changes (require user awareness)
- Adding, modifying, or removing files in `identity/`.
- Creating or modifying files in `skills/`.
- Restructuring folders (renaming, splitting, merging).
- Retiring or archiving memory files.
- Modifying any SUMMARY.md in ways that change meaning rather than just updating coverage.

For proposed changes: describe the change and reasoning to the user. If approved, apply and log in CHANGELOG.md. If the user is unavailable, add to `meta/review-queue.md`.

### Protected changes (require explicit approval)
- Any modification to files in `meta/` (including this file).
- Any modification to `README.md`.
- Any modification to `CHANGELOG.md` beyond appending new entries.
- Bulk operations (retiring multiple files, restructuring multiple folders).

Protected changes must never be applied silently. Always present them to the user with full reasoning and wait for explicit confirmation.

## Commit conventions

When the agent has write access to the repository, commits should follow this format:

```
[category] brief description

Longer explanation if needed. Include reasoning for non-obvious changes.
```

Categories:
- `[chat]` — New chat transcript or summary.
- `[knowledge]` — Knowledge file added or updated.
- `[skill]` — Skill file added or updated.
- `[identity]` — User profile updated.
- `[curation]` — Access aggregation, summary refresh, retirement.
- `[system]` — Changes to meta files, README, or CHANGELOG.

## Periodic review

During any session, if the agent notices it has been more than 30 days since the last `[system]` entry in CHANGELOG.md, it should suggest a brief system review:

1. Are there any files consistently flagged as unhelpful in ACCESS.jsonl?
2. Are there any `[CONFLICT]` tags unresolved in identity or knowledge files?
3. Are there any entries in `meta/review-queue.md` awaiting approval?
4. Does the overall folder structure still make sense given how the system is actually being used?

This review should be lightweight — a quick summary and any recommendations, not a full audit. The user can engage as much or as little as they want.

## Model portability

This system is designed to work with any capable language model. When switching models:

- No changes to the repository should be needed.
- The new model should follow the bootstrap sequence in README.md.
- If the new model has significantly different capabilities (e.g., smaller context window, no tool use), it should note any limitations in `meta/review-queue.md` so the user can decide whether to adapt the system.
- The CHANGELOG.md should record model transitions as system events.
