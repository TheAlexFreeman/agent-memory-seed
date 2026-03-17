# Memory Engine Phase 2 Prelude

This document describes the first implemented slice beyond the initial Phase 1 foundation.

## Goal

The first Phase 2 slice keeps the engine read-only while making ACCESS task history more useful:

- normalize free-text `task` strings into derived token sets
- merge near-duplicate task descriptions into stable preview groups
- persist those groups in SQLite as disposable derived state
- avoid any write-back into canonical Markdown or `meta/` files

## Current command

```bash
python scripts/memory_engine.py task-groups
```

Use `--json` for machine-readable output and `--limit N` to cap printed groups.

## What the command does

`task-groups` reads ACCESS history directly from the repo and reports:

- total ACCESS entries analyzed
- how many derived task groups were found
- a representative label for each group
- normalized tokens for the group
- representative original task strings
- common files associated with that task group

The command is intentionally conservative. It is a preview surface for operators and future automation, not a mutating aggregation workflow.

## Rebuild side effects

`python scripts/memory_engine.py rebuild` now also stores derived task-group state in SQLite:

- `task_groups` holds normalized group summaries
- `access_entries.normalized_task` stores the normalized token string
- `access_entries.task_group_name` stores the derived group label

As with the rest of `.memory.db`, this state is disposable and fully rebuildable from source files.

## Deliberately deferred

This slice still does **not**:

- write `meta/task-groups.md`
- automate ACCESS aggregation
- rank search results
- expose an MCP server
- modify canonical memory files

Those remain later steps once the derived grouping surface proves useful.
