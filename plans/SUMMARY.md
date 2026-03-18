# Plans — Summary

This folder holds structured research plans and investigation roadmaps. Plans are agent-generated, persistent documents that describe *what we intend to investigate and how*. They are distinct from knowledge files (which record what we've found) and skills (which record reusable procedures).

## What belongs here

- Multi-session research projects with a defined scope, phase structure, and output targets
- Investigation roadmaps where the agent needs to track progress across sessions
- Any plan where execution state (what's done, what's next) needs to persist

## What doesn't belong here

- One-off task notes → use `scratchpad/CURRENT.md`
- Completed plans → archive within this folder or delete
- Governance and system meta → use `meta/`

## Frontmatter conventions

Plans use standard frontmatter with two additional fields:

```yaml
type: research-plan        # distinguishes plans from knowledge content
status: active             # active | paused | complete
next_action: "..."         # one-line description of where to pick up
```

Trust decay rules from `meta/quick-reference.md` apply normally: `trust: medium` plans are flagged for review after 180 days without a `last_verified` update. Update `last_verified` and `next_action` at the end of any session that makes progress on a plan.

---

## Active plans

### `philosophy-history-survey.md` · status: active · trust: medium

Broad survey of the history of philosophy — the overarching story of how ideas developed, what mattered in different times and places, how schools influenced one another. 26 output files planned across 7 phases + 4 synthesis files. Output goes to `knowledge/_unverified/philosophy/history/`.

**Progress:** 0/26 files written (0/4 synthesis files)
**Next action:** Begin Phase 1 — write `knowledge/_unverified/philosophy/history/ancient/pre-socratics.md`

---

## Completed plans

_None yet._
