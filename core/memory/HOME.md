# Home

This is your Home File. It is your primary orientation surface for the Engram memory store. Use this file as a map of the memory architecture and a place for anything that must be top-of-mind for both user and agent across sessions.

---

## Relevant Context

Load these files in this order: `core/memory/users/SUMMARY.md` → `core/memory/activity/SUMMARY.md` _(skip if empty or still placeholder)_ → `core/memory/working/scratchpad/USER.md` _(skip if only placeholder)_ → `core/memory/working/scratchpad/CURRENT.md` _(skip if only placeholder)_ → task-relevant `core/memory/working/projects/SUMMARY.md` plus task-relevant `core/memory/knowledge/SUMMARY.md` and/or `core/memory/skills/SUMMARY.md` only when the active project, recent history, or current task makes them relevant

### Compact returning notes

**Access-tracked namespaces:** `core/memory/users/`, `core/memory/knowledge/`, `core/memory/skills/`, `core/memory/working/projects/`, `core/memory/activity/`.

- Run metadata-first maintenance probes before loading extra governance files.
- Load `core/governance/review-queue.md` only when it has real entries or the user asks.
- Count non-empty lines in `ACCESS.jsonl` files for access-tracked namespaces before loading governance docs.
- Treat `core/memory/working/projects/SUMMARY.md`, `core/memory/knowledge/SUMMARY.md`, and `core/memory/skills/SUMMARY.md` as task-driven drill-down context, not unconditional startup reads.
- In worktree mode, use `host_repo_root` from `agent-bootstrap.toml` for host-code git operations; use the worktree path for memory files.


---

## Top of mind

TODO: Protocol design
 - activity logging for automations and user interactions
 - user/automation tracking for per-session best-guess
 - activity log consolidation/archival, eventual summarization into narrative
 - which aspects of the system most engage the user, and why?
