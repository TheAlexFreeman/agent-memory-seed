# Memory Engine Phase 1

This document defines the initial implementation boundary for the optional memory engine.

## Goal

Phase 1 establishes a safe persistence boundary for future retrieval and MCP work:

- The git repo remains the canonical memory store.
- SQLite is derived state only.
- The initial CLI is read-heavy and conservative.
- Governance rules still come from the existing Markdown files in `meta/`.

## Current commands

```bash
python scripts/memory_engine.py status
python scripts/memory_engine.py rebuild --dry-run
python scripts/memory_engine.py rebuild
```

## Canonical vs derived state

Canonical state:

- Markdown files in `identity/`, `knowledge/`, `skills/`, `chats/`, and `meta/`
- ACCESS logs in `ACCESS.jsonl`
- Git history

Derived state:

- `.memory.db`

The SQLite database is intentionally disposable. Deleting it must never lose memory. Rebuilding the database must be enough to restore the engine state from source files.

## Phase 1 schema

The current CLI creates the following tables:

- `files` — indexed Markdown files with folder, file type, provenance metadata, and timestamps
- `access_entries` — ACCESS.jsonl entries joined back to indexed files
- `aggregation_checkpoints` — reserved for later aggregation milestones
- `clusters` — reserved for later co-retrieval analysis
- `anomalies` — reserved for later review and integrity findings
- `system_state` — a snapshot of the current stage and active thresholds from `meta/quick-reference.md`

The schema is intentionally ahead of current behavior so later phases can add search and aggregation without redefining the persistence boundary.

## Status command contract

`status` must be authoritative about runtime configuration. It reads `meta/quick-reference.md` directly and reports:

- current active stage
- last periodic review date
- active thresholds
- basic repo inventory counts
- whether `.memory.db` exists
- indexed counts when a database is present

## Rebuild command contract

`rebuild` must:

- detect the repo root
- scan the canonical Markdown and ACCESS files
- populate the Phase 1 SQLite schema
- leave canonical files unchanged

`rebuild --dry-run` must not create or modify `.memory.db`.

## Deliberately deferred

Phase 1 does **not** implement:

- semantic or lexical search
- aggregation writes
- trust-weighted ranking
- MCP server integration
- direct modification of memory files

These are later phases. Phase 1 exists to make those additions easier and safer.