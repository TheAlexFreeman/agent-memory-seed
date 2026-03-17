# Memory Engine Phase 2 Prelude

This document describes the current implemented Phase 2 slice beyond the initial Phase 1 foundation.

## Goal

The current Phase 2 slice makes ACCESS task history operational while keeping the core storage model unchanged:

- normalize free-text `task` strings into derived token sets
- merge near-duplicate task descriptions into stable preview groups
- persist those groups in SQLite as disposable derived state
- emit machine-generated `meta/task-groups.md` during Calibration-stage aggregation
- rank files through a read-only query surface that uses the derived groups

## Current command

```bash
python scripts/memory_engine.py task-groups
python scripts/memory_engine.py aggregate --dry-run
python scripts/memory_engine.py query "react performance debug"
```

Use `--json` for machine-readable output. `task-groups` and `query` also support `--limit N`.

## What the command does

`task-groups` reads ACCESS history directly from the repo and reports:

- total ACCESS entries analyzed
- how many derived task groups were found
- a representative label for each group
- normalized tokens for the group
- representative original task strings
- common files associated with that task group

The command is intentionally conservative. It is a preview surface for operators and future automation.

`aggregate` is the first command that can update canonical state. It reads the live stage and aggregation trigger from `meta/quick-reference.md`, checks the current unarchived ACCESS backlog, and writes `meta/task-groups.md` only when task-group writes are allowed for the active stage and the trigger has been met. `--dry-run` previews the same decision without creating or modifying files.

`query` is read-only. It matches free-text queries to derived task groups, then ranks files using task-group similarity, retrieval frequency, helpfulness, and recency.

## Rebuild side effects

`python scripts/memory_engine.py rebuild` now also stores derived task-group state in SQLite:

- `task_groups` holds normalized group summaries
- `access_entries.normalized_task` stores the normalized token string
- `access_entries.task_group_name` stores the derived group label

As with the rest of `.memory.db`, this state is disposable and fully rebuildable from source files.

## Canonical write path

When `aggregate` writes `meta/task-groups.md`, it is following an already-defined governance exemption in `meta/update-guidelines.md`: the file is machine-generated state, not a governance document. The repo remains canonical because the write is explicit, inspectable, and grounded in ACCESS history rather than opaque model state.

## Deliberately deferred

This slice still does **not**:

- expose an MCP server
- archive processed ACCESS entries
- update folder summaries automatically
- assign controlled categories to ACCESS entries

Those remain the next steps once the derived grouping and query surfaces have proven useful enough to justify a Phase 3 category layer.
