# Automation Backlog — 2026-03-18

Working note for future Codex automation setup. These are candidates beyond the four current drafts (`Memory Health`, `Aggregation Watcher`, `Unverified Triage`, `Periodic Review`).

## Candidate automations

- `Session Wrap-Up Nudger`
  Detect sessions that appear to have ended without a `chat-NNN/` record, reflection, or ACCESS flush, and open a small inbox item recommending wrap-up before the context fades.

- `Promotion Queue Builder`
  Scan `_unverified` knowledge plus recent review signals and propose a batched promotion review list by topic, so low-trust research does not accumulate faster than it can be validated.

- `Protected Change Audit`
  Watch for edits to `meta/`, `skills/`, `README.md`, or other protected surfaces that lack the expected proposal/changelog trail, and surface those for review.

- `Research Lane`
  Periodically choose the highest-leverage next artifact from active plans and draft a suggested focused work session, especially for the Django/Celery, React, DevOps, and MCP tracks.

- `Plan Freshness Check`
  Look for active plans whose `next_action` or `last_verified` fields are aging without movement, and surface whether they should be advanced, paused, or narrowed.

- `Git Hygiene Check`
  Detect a dirty worktree, unpushed commits, or memory updates that were recorded locally but not pushed, and nudge for cleanup before state diverges.

## Current read

The strongest future additions are probably `Session Wrap-Up Nudger` and `Promotion Queue Builder`. Both reinforce existing maintenance rules without adding much conceptual surface area.
