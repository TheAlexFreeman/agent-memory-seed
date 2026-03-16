---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Onboarding: First-Session User Discovery

## When to use this skill

Activate this skill on the **first session only** — when both of these conditions are true:

1. `identity/SUMMARY.md` contains "No portrait yet" (no user profile has been created).
2. No date-organized chat folders exist in `chats/` (no prior sessions have been recorded).

If either condition is false, the system has already been onboarded. Skip this skill and proceed with the normal bootstrap sequence.

## Steps

### 1. Introduce the memory system

Briefly explain to the user:
- You have persistent memory stored in this repository.
- What you learn in this conversation will be available in future sessions, even across different models.
- You'd like to ask a few questions to build an initial profile so future interactions start strong.

Keep it concise — one short paragraph, not a lecture.

### 2. Discover the user's role and context

Ask about:
- **Role and responsibilities.** What they do, what domain they work in.
- **Key projects.** What they're actively working on or will be working on with AI assistance.
- **Domain expertise.** What they know well (so you can calibrate depth) and what's new to them.

### 3. Discover communication preferences

Ask about:
- **Detail level.** Do they prefer concise answers or thorough explanations?
- **Tone.** Casual, professional, direct, exploratory?
- **Format preferences.** Do they like bullet points, prose, code-first, examples-first?
- **Anti-preferences.** Anything they find annoying or unhelpful in AI interactions.

### 4. Discover tools and environment

Ask about:
- **Primary languages and frameworks** they work with.
- **Editor/IDE** they use.
- **Platforms and services** that come up regularly (cloud providers, CI/CD, etc.).
- **Collaboration context.** Solo work, team, open source?

### 5. Open-ended capture

Ask: _"Is there anything else you'd like me to remember going forward? Anything that would make our interactions more useful?"_

This catches important context that structured questions miss.

### 6. Write the initial profile

Based on the conversation:

1. Create one or more files in `identity/` capturing the discovered traits. Use the frontmatter schema:
   ```yaml
   ---
   source: user-stated
   origin_session: chat-001
   created: YYYY-MM-DD
   last_verified: YYYY-MM-DD
   trust: high
   ---
   ```
2. Tag each trait with `[observed]` confidence (the user stated it directly).
3. Update `identity/SUMMARY.md` — replace the "No portrait yet" placeholder with an initial portrait summarizing the key traits.

### 7. Record the session

Log this conversation following the standard chat archival structure:
- Create the appropriate `chats/YYYY/MM/DD/chat-001/` folder.
- Write `transcript.md`, `SUMMARY.md`, and `reflection.md`.
- Append access notes to the relevant ACCESS.jsonl files for any content files you read.

## Quality criteria

- The initial portrait should capture **5–10 durable traits**, all tagged `[observed]`.
- The user should feel accurately represented — not a caricature or a list of demographics, but a useful working portrait.
- Communication preferences should be specific enough to measurably change agent behavior in the next session.
- No trait should be invented or inferred beyond what the user actually said. If something is ambiguous, note it as `[tentative]` rather than guessing.

## Anti-patterns

- **Don't interrogate.** This should feel like a conversation, not a form. Weave questions naturally and let the user volunteer information at their own pace.
- **Don't over-collect.** 5–10 solid traits are better than 25 shallow ones. You'll learn more over time.
- **Don't promise too much.** The memory system improves with use — don't set expectations for perfect recall from session one.
- **Don't skip the open-ended question.** It consistently surfaces the most important context.

## After first use

This skill is designed for one-time use. After successful onboarding:

1. Propose archiving this file to `skills/_archive/onboarding.md`.
2. Update `skills/SUMMARY.md` to reflect the archival.
3. Log the archival in `CHANGELOG.md` as a `[curation]` entry.

The skill remains available in git history if the user ever wants to re-run onboarding (e.g., after a major life or role change).
