# Deferred Action Template

**Load this file only when operating in read-only mode for the first time.** It provides a worked example of the deferred-action summary format described in `meta/update-guidelines.md` § "How to communicate deferred actions". After your first read-only session, you know the format — no need to reload this file.

---

## Worked example

A session where the agent retrieved three knowledge files and noticed a boundary violation:

```
## Deferred actions (write access required)

### ACCESS.jsonl entries
[knowledge/ACCESS.jsonl]
{"file": "knowledge/react-performance-patterns.md", "date": "2026-03-17", "task": "optimize dashboard rendering", "helpfulness": 0.8, "note": "directly applicable memoization patterns", "session_id": "chats/2026/03/17/chat-002"}
{"file": "knowledge/browser-api-reference.md", "date": "2026-03-17", "task": "optimize dashboard rendering", "helpfulness": 0.4, "note": "opened but only tangentially relevant", "session_id": "chats/2026/03/17/chat-002"}

[identity/ACCESS.jsonl]
{"file": "identity/communication-preferences.md", "date": "2026-03-17", "task": "calibrate response style", "helpfulness": 0.9, "note": "shaped concise code-first response format", "session_id": "chats/2026/03/17/chat-002"}

[plans/ACCESS.jsonl]
{"file": "plans/performance-investigation.md", "date": "2026-03-17", "task": "resume multi-session performance investigation", "helpfulness": 0.8, "note": "provided the active checklist and next step for the session", "session_id": "chats/2026/03/17/chat-002"}

### Review-queue entries
[meta/review-queue.md]
- type: boundary-violation, file: knowledge/react-performance-patterns.md, pattern: "always use React.memo for list items" — imperative instruction detected; candidate for reclassification to skills/

### Other
- SUMMARY.md for knowledge/ needs "Usage patterns" updated: react-performance-patterns.md is high-value (6 retrievals, mean helpfulness 0.82)
- plans/SUMMARY.md needs progress refreshed: performance-investigation.md advanced to Phase 2
- Chat summary and reflection note for chats/2026/03/17/chat-002/ need to be written
```

## Key principles

- Group ACCESS entries by target file (the ACCESS.jsonl they should be appended to).
- Include all required fields: `file`, `date`, `task`, `helpfulness`, `note`. Include `session_id` whenever the chat folder path is known.
- List review-queue entries with their type, the file they concern, and a brief description of the pattern or finding.
- Under "Other," note any summary updates, reflection notes, or other write actions that don't fit the structured sections.
- Present the summary at the very end of the session so all deferred actions are captured.
