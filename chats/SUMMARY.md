# Chats Summary

This folder is the episodic memory — a chronological archive of conversations between the user and agent. It is organized hierarchically by date, with summaries at each level providing progressively compressed views of the interaction history.

## Overall history

**One session logged (2026-03-18).** First-session onboarding with Alex Freeman.
Confirmed identity profile from the software developer template. Established
communication preferences (concise, code-first, criticism > validation) and a
knowledge-building goal around Celery + Redis + Docker in Django/Postgres stacks.
Philosophical curiosity (self-organizing dynamics, cognitive science) also noted
as a recurring interest.

See `2026/03/18/chat-001/` for the full session record.

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
