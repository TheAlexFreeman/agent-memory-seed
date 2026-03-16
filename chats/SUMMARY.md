# Chats Summary

This folder is the episodic memory — a chronological archive of conversations between the user and agent. It is organized hierarchically by date, with summaries at each level providing progressively compressed views of the interaction history.

## Overall history

*No conversations yet.* This section will develop into a high-level narrative of the user's journey with the agent: major projects undertaken, how interests evolved, pivotal decisions, and recurring themes.

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

*No access data yet.* This section will be populated after the ACCESS.jsonl file accumulates enough entries to reveal retrieval patterns.
