# Agent Memory System

You are reading a persistent memory system stored as a git repository. This repository allows any capable language model to instantiate a personalized agent by reading these files. You are not starting from scratch — you are resuming an ongoing relationship with a user whose preferences, history, and knowledge are encoded here.

**If you are a human setting up this system for the first time**, see [docs/QUICKSTART.md](docs/QUICKSTART.md) for a step-by-step guide.

## How to orient yourself

1. **Use this file for bootstrap and structure.** For full protocols and security details, see `meta/REFERENCE.md`.
2. **Read `identity/SUMMARY.md`** to understand who the user is and how they prefer to interact.
3. **Read `SUMMARY.md` in whichever folder is relevant** to the current task.
4. **Retrieve specific files only as needed.** Do not load everything into context. Use summaries to decide what to retrieve.
5. **Log your access** using the access-note format described in `meta/REFERENCE.md` § "Memory curation".

## Returning sessions

For normal returning sessions, use `meta/session-checklists.md` as the authoritative runbook and `meta/quick-reference.md` as the live threshold and decision-procedure lookup.

- Start with `meta/session-checklists.md`, `meta/quick-reference.md`, `identity/SUMMARY.md`, and only the summaries relevant to the current task.
- Read recent chat summaries before raw transcripts; load full transcripts only when summaries are insufficient.
- Read `meta/REFERENCE.md`, `meta/CHANGELOG.md`, `meta/curation-policy.md`, and `meta/update-guidelines.md` only on first exposure, when periodic review is due, when the task touches memory/governance/protected writes, or when summaries are insufficient.

## Repository structure

```
/
├── README.md              ← You are here. Bootstrap and structure.
├── setup.sh               ← Post-clone setup script (interactive or CLI flags).
├── setup.html             ← Browser-based setup wizard (no terminal required).
│
├── identity/              ← Who the user is. Personality, preferences, values.
│   ├── SUMMARY.md         ← Start here. High-level portrait of the user.
│   ├── ACCESS.jsonl       ← Access-tracking log.
│   └── (files added over time as traits and preferences emerge)
│
├── knowledge/             ← What the user knows or cares about. Organized by topic.
│   ├── SUMMARY.md         ← Index of knowledge areas and their relevance.
│   ├── ACCESS.jsonl       ← Access-tracking log.
│   ├── _unverified/       ← Quarantine zone for externally sourced content.
│   └── (topic folders/files added as knowledge accumulates)
│
├── skills/                ← How the agent should perform specific tasks.
│   ├── SUMMARY.md         ← Index of available skills and when to use them.
│   ├── ACCESS.jsonl       ← Access-tracking log.
│   └── (skill definitions added as workflows are refined)
│
├── chats/                 ← Episodic memory. Record of past interactions.
│   ├── SUMMARY.md         ← High-level summary of the entire chat history.
│   ├── ACCESS.jsonl       ← Access-tracking log.
│   └── YYYY/MM/DD/        ← Date-organized chat archives.
│       ├── SUMMARY.md     ← Summary at each level of the hierarchy.
│       └── chat-NNN/      ← Individual chat sessions.
│           ├── transcript.md
│           ├── SUMMARY.md
│           ├── reflection.md
│           └── artifacts/
│
├── meta/                  ← Governance. How this system updates itself.
│   ├── REFERENCE.md        ← Full system reference (protocols, security, curation).
│   ├── CHANGELOG.md        ← Record of how this system has evolved and why.
│   ├── quick-reference.md  ← Active operational parameters and decision guides.
│   ├── curation-policy.md  ← Rules for memory hygiene, decay, and promotion.
│   ├── update-guidelines.md ← Protocols for proposing and merging changes.
│   ├── review-queue.md     ← Pending suggestions for system modifications.
│   ├── belief-diff-log.md  ← Periodic audit log tracking content drift.
│   ├── system-maturity.md  ← Developmental stage tracking and adaptive thresholds.
│   ├── first-run.md        ← Streamlined first-session flow for agents.
│   ├── session-checklists.md ← Compact session start/end runbooks.
│   ├── glossary.md          ← Definitions of system terminology.
│   ├── integrity-checklist.md ← Advisory audit checklist.
│   ├── (task-groups.md     ← Created at Calibration stage; emergent task groups.)
│   └── (task-categories.md ← Created at Consolidation stage; controlled vocabulary.)
│
├── docs/                  ← Human-facing project documentation.
│   ├── QUICKSTART.md       ← Setup guide for humans.
│   └── DESIGN.md           ← Design philosophy and future directions.
│
├── engine/                ← Optional Python engine packages.
│   ├── memory_engine_core/ ← Core engine (CLI, SQLite index).
│   ├── memory_engine_service/ ← Governed service layer.
│   └── memory_mcp/        ← MCP server wrapper.
│
├── scripts/               ← Maintenance and import tooling.
├── templates/profiles/    ← Starter identity templates for setup.
└── tests/                 ← Test suite.
```

### Optional memory engine

An optional Python CLI creates `.memory.db` as a **derived** SQLite index. It is not part of the canonical memory store, is ignored by git, and can be deleted/rebuilt at any time. See `docs/DESIGN.md` for the full engine roadmap.

```bash
python scripts/memory_engine.py status
python scripts/memory_engine.py rebuild
python scripts/memory_engine.py query "react performance debug"
python scripts/memory_mcp_server.py --repo-root .
```

## Bootstrap sequence

If this is a fresh instantiation (the repo has just been cloned or linked for the first time with a new model), follow this sequence:

1. Read this README.md fully. ✓
2. Skim the 2–3 most recent entries in `meta/CHANGELOG.md` for context on recent changes. The full history is reference, not required for bootstrap.
3. Read `identity/SUMMARY.md` to understand the user.
4. Determine whether this is **first run**. Either condition qualifies:
   - `identity/SUMMARY.md` still contains "No portrait yet" and no date-organized chat folders exist under `chats/` (blank-slate setup).
   - `identity/` contains a file with `source: template` in its frontmatter and no date-organized chat folders exist under `chats/` (a starter profile was installed by `setup.sh --profile` but onboarding has not yet run).
   - **Agent shortcut:** If this is first run, see `meta/first-run.md` for a streamlined flow that condenses steps 1–9 into a silent setup + interactive onboarding.
5. Read `meta/quick-reference.md` to load the **currently active thresholds and decision guides**. This is the single lookup for all operational parameters — do not use hardcoded values from other files.
6. **If this is first run,** read the relevant parts of `meta/update-guidelines.md` before doing anything else: `Change categories`, `Read-only operation`, and the periodic-review trigger reference only if needed.
7. **Check write access.** Can you write to this repository? If not, follow `meta/update-guidelines.md` § "Read-only operation".
8. **If this is first run,** read `skills/SUMMARY.md` and `skills/onboarding.md`.
9. **If this is first run,** run the onboarding skill. `knowledge/SUMMARY.md` and `chats/SUMMARY.md` are skippable on first run when they are empty. After onboarding completes, greet the user using what you learned.
10. **Otherwise,** use `meta/session-checklists.md` as the authoritative runbook for normal returning sessions.
11. Read `meta/REFERENCE.md`, `meta/CHANGELOG.md`, `meta/curation-policy.md`, and `meta/update-guidelines.md` only when this is your first exposure, periodic review is due, the task touches memory/governance/protected writes, or the summaries are insufficient.
12. Greet the user in a way that reflects what you've learned, and ask if anything important has changed since the last session.

For normal returning sessions, use `meta/session-checklists.md` as the compact session start/end runbook.

Welcome. You have memory now. Use it well.
