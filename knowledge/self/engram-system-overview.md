---
title: Engram System — Architecture and Design Overview
category: knowledge
tags: [engram, architecture, self-knowledge, mcp, memory-system]
source: agent-generated
trust: medium
origin_session: chats/2026/03/20/chat-001
created: 2026-03-20
last_verified: 2026-03-20
---

# Engram System — Architecture and Design Overview

This file is self-knowledge: a description of this system by the system itself, written for
use by future sessions of this agent. It should be treated as authoritative about intent and
design philosophy, and cross-checked against `README.md` and `meta/quick-reference.md` for
operational details. Human review is recommended before relying on it for architectural decisions.

---

## What Engram Is

Engram is a **git-backed persistent AI memory system** designed to give a language model agent
durable memory across sessions. The model itself is stateless and ephemeral — each session starts
from a clean context window. Engram provides continuity by maintaining a structured repository of
knowledge, plans, and session history that the agent loads at session start and updates during the
session.

The core design bet: *structured Markdown files under git version control are a better long-term
memory substrate than embeddings databases or opaque blob stores*, because they are:
- **Human-readable and editable** — the user can inspect, correct, or override any memory directly
- **Auditable** — git history is a tamper-evident record of everything the system has written
- **Version-controlled** — rollback to any prior state is always possible
- **Composable** — files can link to each other, be organized into taxonomies, and be queried both
  semantically and structurally

The tradeoff: Markdown + git is slower, more verbose, and requires more curation discipline than
a vector store. The bet is that for a long-running personal memory system, those costs are worth
paying for the transparency and recoverability guarantees.

---

## Repository Structure

```
agent-memory-seed/
├── CLAUDE.md                    # Session adapter — Claude Code entry point
├── AGENTS.md                    # Session adapter — general agent entry point
├── .cursorrules                 # Session adapter — Cursor IDE entry point
├── agent-bootstrap.toml         # Structured bootstrap configuration
├── README.md                    # Full architectural reference
│
├── meta/                        # Governance and operational parameters
│   ├── quick-reference.md       # IDENTITY-CRITICAL: routing authority, active thresholds
│   ├── curation-policy.md       # Trust decay and archiving policy
│   ├── update-guidelines.md     # How to change the system
│   ├── system-maturity.md       # Stage definitions and transition criteria
│   ├── curation-algorithms.md   # Full aggregation and cluster algorithms
│   ├── review-queue.md          # Flagged items awaiting human review
│   ├── belief-diff-log.md       # Tracking belief changes over time
│   └── integrity-checklist.md  # Periodic review checklist
│
├── identity/                    # Who the user is; persistent user profile
│   └── SUMMARY.md               # User portrait, working style, goals
│
├── chats/                       # Session history by date
│   └── YYYY/MM/DD/chat-NNN/     # Per-session summaries and reflections
│       ├── SUMMARY.md
│       └── reflection.md
│
├── plans/                       # Active multi-session work tracking
│   ├── SUMMARY.md               # IDENTITY-CRITICAL: priority stack, next actions
│   └── *.md                     # Individual build and research plans
│
├── scratchpad/                  # Ephemeral working notes
│   ├── CURRENT.md               # Active session threads and immediate next steps
│   └── USER.md                  # User-authored constraints and preferences
│
├── knowledge/                   # Promoted (human-reviewed) knowledge
│   ├── SUMMARY.md               # Knowledge index
│   ├── ai-history/              # AI paradigm history (promoted)
│   ├── literature/              # Literary knowledge (promoted)
│   ├── systems-architecture/    # Storage, git, concurrency primitives (promoted)
│   ├── tooling/                 # Operational tooling notes (promoted)
│   ├── self/                    # This folder — self-knowledge (promoted)
│   └── _unverified/             # Agent-written, awaiting human review
│       ├── ai-frontier/         # Frontier AI research
│       ├── ai-tools/            # AI tooling landscape
│       ├── devops/              # DevOps/Docker research
│       ├── django/              # Django stack research
│       ├── mcp/                 # MCP protocol and ecosystem
│       ├── philosophy/          # Philosophy (Lewis, history, governance)
│       ├── rationalist-community/
│       ├── react/               # React/frontend research
│       └── system-notes/        # Operational notes about this system
│
├── skills/                      # Reusable procedure files for the agent
│
├── engram_mcp/                  # Python MCP server (the runtime)
│   └── agent_memory_mcp/
│       ├── server.py            # FastMCP server definition
│       ├── server_main.py       # CLI entrypoint
│       ├── tools/
│       │   ├── read_tools.py    # ~2000 lines: read, search, git log tools
│       │   ├── semantic_tools.py # ~2000 lines: semantic search, plan tools (MONOLITH)
│       │   └── write_tools.py   # ~550 lines: write, update, archive tools
│       └── tests/               # 190 pytest tests
│
├── tools/                       # Legacy location; now a compat shim
│   └── agent_memory_mcp/
│       └── __init__.py          # Re-exports from engram_mcp (Phase 0 of reorganization)
│
└── HUMANS/                      # Human-facing documentation and tooling
    ├── docs/                    # MCP setup guides, integration docs
    └── tooling/
        ├── scripts/             # validate_memory_repo.py, inspect_compact_budget.py, etc.
        └── tests/               # test_validate_memory_repo.py (the 190-test suite)
```

---

## The MCP Server (engram_mcp)

The MCP server exposes the memory system to any MCP-capable agent (Claude Desktop, Claude Code,
Cursor, etc.). It is implemented in Python using FastMCP.

### Tool Categories

**Read tools** (`read_tools.py`):
- `memory_read_file` — read a specific file by path
- `memory_list_files` — list files by folder or pattern
- `memory_search` — keyword/semantic search across the repo
- `memory_git_log` — structured git history for a path or the whole repo

**Semantic tools** (`semantic_tools.py` — currently a monolith being split):
- Identity tools: `memory_get_identity`, `memory_update_identity`
- Knowledge tools: `memory_search_knowledge`, `memory_get_knowledge_file`
- Plan tools: `memory_get_plans`, `memory_update_plan`, `memory_archive_plan`
- Session tools: `memory_start_session`, `memory_end_session`, `memory_append_scratchpad`

**Write tools** (`write_tools.py`):
- `memory_write` — write a new file (with frontmatter validation)
- `memory_update` — update an existing file
- `memory_archive_knowledge` — move a file to `_archive/`
- `memory_flag_for_review` — add a file to the human review queue
- `memory_promote_knowledge` — move a file from `_unverified/` to `knowledge/`

### Key Design Constraints

- All writes are committed to git immediately (no uncommitted writes)
- The server resolves the repo root via `MEMORY_REPO_ROOT` or `AGENT_MEMORY_ROOT` env vars
- Push to remote is deliberately NOT implemented (see `environment-capability-asymmetry.md`)
- A GitHub token can be added to `.codex/config.toml` `[mcp_servers.agent_memory.env]` if
  push capability is wanted in a future version

---

## The Trust Tier System

Every knowledge file has a `trust` frontmatter field and lives in a path that encodes its
review status:

| Tier | Path | Meaning |
|---|---|---|
| Unverified | `knowledge/_unverified/` | Agent-written, not yet human-reviewed |
| Promoted | `knowledge/*/` (non-`_unverified`) | Human-reviewed, approved for full weight |
| Archived | `knowledge/_archive/` | Retired; preserved for reference but not loaded in normal context |

The trust field (`low` / `medium` / `high`) encodes confidence about the *content*, independent
of the review status. A promoted file can still be `trust: medium` if its content is uncertain.

The system also uses `source` frontmatter (`agent-generated`, `external-research`, `manual`,
`user-authored`) to distinguish provenance.

---

## Session Bootstrap Architecture

The bootstrap is designed for minimal context cost. Two entry points:

**Compact returning** (~3,000–7,000 tokens): the default for day-to-day sessions. Loads:
`meta/quick-reference.md` → `identity/SUMMARY.md` → `chats/SUMMARY.md` → `plans/SUMMARY.md`
→ `scratchpad/USER.md` → `scratchpad/CURRENT.md` (all skipped if empty or only placeholder text).

**Full bootstrap** (~18,000–25,000 tokens): for fresh instantiation on a returning system or
periodic governance reviews. Adds `README.md`, `CHANGELOG.md`, `meta/curation-policy.md`,
`meta/update-guidelines.md`.

The compact path has strict token budgets enforced by the test suite:
`meta/quick-reference.md` ≤ ~2,600 tokens, `plans/SUMMARY.md` ≤ ~1,700 tokens.

---

## Plan Taxonomy

Plans live in `plans/` and are categorized:

- **Build plans** (`category: build`): implementation plans with a defined done-state.
  Dependency-ordered; have blocking relationships. Current TOP PRIORITY: `mcp-reorganization.md`
  (22/41 complete as of 2026-03-20, at Phase 3).
- **Research plans** (`category: research`): open-ended knowledge-base work. Pursued
  opportunistically or on user request. Current TOP PRIORITY: `memetic-security-research.md`
  (0/18, just created 2026-03-20).

Build plans take precedence over research plans when unblocked work is available.

---

## Current Development State (as of 2026-03-20)

The system is in **Exploration** stage (see `meta/quick-reference.md`).

**mcp-reorganization** (the primary build plan) is moving the MCP runtime from the legacy
`tools/` path into the `engram_mcp/` package. Phase 0 (manifest repair, origin_session fixes,
compat shim) is complete. The laptop agent has advanced this to Phase 3, item 24 (22/41
complete). The `tools/agent_memory_mcp/__init__.py` is now a compat shim re-exporting from
`engram_mcp`.

**Two-agent coordination pattern**: this system is regularly worked on by two agents
concurrently — a Cowork (sandbox) agent and a laptop Claude Code agent. The Cowork agent
cannot push to remote (no GitHub credentials, FUSE mount). The laptop agent can push. The
mitigation: workspace-folder-first writes so Cowork changes are always visible locally, and
git as the audit trail / merge mechanism. Documented in
`knowledge/_unverified/system-notes/environment-capability-asymmetry.md`.

**Test suite**: 190 tests passing, 1 skipped. The suite is in `HUMANS/tooling/tests/`.
Running `python3 -m pytest` from repo root is the standard verification step before every commit.
