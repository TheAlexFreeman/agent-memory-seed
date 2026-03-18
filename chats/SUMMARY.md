# Chats Summary

This folder is the episodic memory — a chronological archive of conversations between the user and agent. It is organized hierarchically by date, with summaries at each level providing progressively compressed views of the interaction history.

## Overall history

**Three chat records logged (2026-03-18).** All from the first day; chat-001 spanned three context windows, chat-002 handled maintenance, and chat-003 focused on automation design.

### chat-001 — Extended first session (3 context windows)

**Part 1 — Onboarding.** Identity profile confirmed (source upgraded from template to user-stated, trust: high). Django 6.0 knowledge base built (9 files). React 19 + Chakra UI 3 research added (4 files). Knowledge-building goal established: Celery expertise over time.

**Part 2 — Philosophy research.** Extensive `knowledge/_unverified/philosophy/` folder built: self-organizing dynamical systems, LLMs vs human minds, narrative cognition, cognitive linguistics (Lakoff, Fauconnier, Sweetser). History-of-philosophy research plan launched. Alex noted personal connection to Eve Sweetser (Berkeley, ~10 years ago).

**Part 3 — Engineering stack planning and MCP design.** Four research plans created: `django-stack-research.md`, `react-stack-research.md` (TanStack Router replacing React Router), `devops-docker-research.md`, `agent-memory-mcp.md`. Upstream core branch (76 files) integrated. Commit conventions and SUMMARY anchor scheme designed. Two commits made.

### chat-002 — System review and maintenance

Delivered system review findings: updated CHANGELOG, chats/SUMMARY, chat-001 SUMMARY, fixed `memory_move` source restriction gap in MCP plan, created this chat-002 record.

### chat-003 — Automation planning and wrap-up

Drafted four setup-ready Codex automations for this repo: `Memory Health`, `Aggregation Watcher`, `Unverified Triage`, and `Periodic Review`. Revised them to self-gate and archive clean runs, then recorded a provisional backlog of future candidates in scratchpad notes.

See `2026/03/18/chat-001/`, `2026/03/18/chat-002/`, and `2026/03/18/chat-003/` for full session records.

## Structure

```
chats/
├── SUMMARY.md          ← This file. Top-level history overview.
├── ACCESS.jsonl        ← Tracks which past chats are retrieved and why.
└── YYYY/
    ├── SUMMARY.md      ← Yearly summary: major themes, projects, evolution.
    └── MM/
        ├── SUMMARY.md  ← Monthly summary: key conversations and outcomes.
        └── DD/
            ├── SUMMARY.md  ← Daily summary: what happened today.
            └── chat-NNN/
                ├── SUMMARY.md    ← Individual chat summary.
                ├── transcript.md ← Full conversation record (read-only archive).
                └── artifacts/    ← Files created or uploaded during the chat.
```

## Compression principles

- **Chat-level summaries:** What was discussed, what was decided, what was produced. Include enough detail that an agent could pick up the thread if the user says "remember when we talked about X?"
- **Daily summaries:** Brief roll-up of the day's conversations. Only notable if multiple chats occurred or something significant happened.
- **Monthly summaries:** Thematic overview. What projects were active, what shifted, what was learned. Individual chats mentioned only if pivotal.
- **Yearly summaries:** Broad narrative arc. How the user's needs, interests, and working patterns evolved over the year.

## When to retrieve past chats

- When the user explicitly references a past conversation.
- When the current task closely resembles a past task (check ACCESS.jsonl patterns).
- When the user's request involves a topic that appears in the chat summaries.
- **Do not** load full transcripts unless the summary is insufficient. Start with summaries and drill down only as needed.

## Usage patterns

_No access data yet._ After aggregation, this section will contain:
- **High-value files** — files with 5+ retrievals and mean helpfulness ≥ 0.7
- **Low-value files** — files with 3+ retrievals and mean helpfulness ≤ 0.3
- **Co-retrieval clusters** — file sets accessed together across 3+ sessions
- **Retrieval trends** — frequency and helpfulness changes since last aggregation
