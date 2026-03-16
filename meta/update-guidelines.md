# Update Guidelines

This document defines how changes to the memory system are proposed, evaluated, and applied. It distinguishes between changes to _content_ (what the system knows) and changes to _governance_ (how the system operates).

## Provenance metadata

Every content file in `identity/`, `knowledge/`, and `skills/` must include YAML frontmatter tracking its origin and trust level. Files in `meta/` and `chats/` are exempt — governance docs are protected by change-control tiers, and chat transcripts are read-only archives.

### Required frontmatter schema

```yaml
---
source: user-stated | agent-inferred | external-research | skill-discovery
origin_session: chat-NNN | manual | unknown
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
trust: high | medium | low
---
```

### Field definitions

- **source** — How this information entered the system.
  - `user-stated`: The user directly provided or dictated this content.
  - `agent-inferred`: The agent synthesized this from patterns across interactions.
  - `external-research`: Content originated from web searches, uploaded documents, or any source outside direct user conversation.
  - `skill-discovery`: A procedural pattern the agent identified from user corrections or repeated workflows.
- **origin_session** — The chat session that produced this file, or `manual` for hand-authored content, or `unknown` for files predating this schema.
- **created** — Date the file was first written.
- **last_verified** — Date a human last reviewed or confirmed the content. Updated when the user explicitly approves, corrects, or re-confirms the file.
- **trust** — The current trust classification (see `meta/curation-policy.md` for retrieval behavior at each level).

### Trust assignment rules

| Source              | Initial trust | Promotion path                                                      |
| ------------------- | ------------- | ------------------------------------------------------------------- |
| `user-stated`       | `high`        | Already at highest level                                            |
| `agent-inferred`    | `medium`      | → `high` when user explicitly confirms                              |
| `skill-discovery`   | `medium`      | → `high` after user approval + successful use                       |
| `external-research` | `low`         | → `medium` after user review; → `high` after user confirms accuracy |

Trust may also be demoted: if a `high`-trust file is found to contain inaccuracies or the user expresses doubt, downgrade to `medium` and update `last_verified`.

### Retroactive application

Files that predate this schema should have frontmatter added during the next periodic review, using `source: unknown`, `trust: medium`, and `last_verified` set to the review date.

## Change categories

### Automatic changes (no approval needed)

- Appending entries to ACCESS.jsonl files.
- Writing chat transcripts and chat-level summaries to `chats/`.
- Writing external-research results to `knowledge/_unverified/` (never directly to `knowledge/`).
- Updating "Usage patterns" sections in SUMMARY.md files based on access aggregation.
- Routine summary refreshes at any level.

### Proposed changes (require user awareness)

- Adding new knowledge files to `knowledge/` (i.e., outside `_unverified/`).
- Adding, modifying, or removing files in `identity/`.
- Promoting files from `knowledge/_unverified/` to `knowledge/`.
- Restructuring folders (renaming, splitting, merging).
- Retiring or archiving memory files.
- Modifying any SUMMARY.md in ways that change meaning rather than just updating coverage.

For proposed changes: describe the change and reasoning to the user. If approved, apply and log in CHANGELOG.md. If the user is unavailable, add to `meta/review-queue.md`.

### Protected changes (require explicit approval)

- Creating, modifying, or removing files in `skills/`.
- Any modification to files in `meta/` (including this file).
- Any modification to `README.md`.
- Any modification to `CHANGELOG.md` beyond appending new entries.
- Bulk operations (retiring multiple files, restructuring multiple folders).

Protected changes must never be applied silently. Always present them to the user with full reasoning and wait for explicit confirmation.

**Why `skills/` is protected:** Skill files contain procedures the agent will execute. They are the highest-value target for memory injection — a poisoned skill file directly controls agent behavior. Requiring explicit approval for all skill changes ensures that no procedural instruction enters the system without human oversight.

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
5. Are there any security flags (type: `security`) in `meta/review-queue.md`?
6. Are there files in `knowledge/_unverified/` older than 60 days awaiting review?

This review should be lightweight — a quick summary and any recommendations, not a full audit. The user can engage as much or as little as they want.

### Belief diff

As part of each periodic review, the agent should generate a **belief diff** — a concise summary of how the system's content has changed since the last review. Record the diff as a new dated entry in `meta/belief-diff-log.md` covering:

- **New files added** — with their source, trust level, and folder.
- **Files modified** — with a brief description of what changed.
- **Files retired or archived** — with the reason.
- **Trust level changes** — any promotions or demotions.
- **Security flags triggered** — any anomalies or boundary violations detected since last review.
- **Identity drift** — whether the user portrait has changed, and by how much.

The belief diff makes drift visible. If the user sees unexpected entries ("your agent now has a new skill for X" or "your knowledge base now claims Y"), they can investigate and revert immediately.

## Commit integrity

Protected changes should use GPG-signed commits (`git commit -S`) when the environment supports it. Signed commits create a cryptographic chain of custody — even if malicious content is written to the repo, the verification step catches unauthorized authorship.

- **Verification:** `git log --show-signature` shows which commits are signed and by whom.
- **Unsigned commits on protected files** (anything in `meta/`, `skills/`, or `README.md`) should be flagged in `meta/review-queue.md` as a security concern during periodic review.
- **This is guidance, not enforcement.** The memory system cannot enforce git configuration. It can recommend signing and detect unsigned commits during review.

## Model portability

This system is designed to work with any capable language model. When switching models:

- No changes to the repository should be needed.
- The new model should follow the bootstrap sequence in README.md.
- If the new model has significantly different capabilities (e.g., smaller context window, no tool use), it should note any limitations in `meta/review-queue.md` so the user can decide whether to adapt the system.
- The CHANGELOG.md should record model transitions as system events.
