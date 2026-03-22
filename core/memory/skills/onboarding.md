---
source: user-stated
origin_session: manual
created: 2026-03-16
last_verified: 2026-03-16
trust: high
---

# Onboarding: First-Session User Discovery

## When to use this skill

Activate this skill on the **first session only** — when no date-organized chat folders exist in `core/memory/activity/`, AND either:

1. `core/memory/users/SUMMARY.md` contains "No portrait yet" (blank-slate setup — no profile installed), OR
2. `core/memory/users/` contains a file with `source: template` in its frontmatter (a starter profile was installed by `setup.sh --profile` but has not yet been confirmed through onboarding).

If neither condition matches — a confirmed user portrait exists, or chat history is present — the system has already been onboarded. Return to `core/HOME.md` and follow its routing instead.

Before using this skill, the agent should already have been routed here from `core/HOME.md`, reviewed the relevant change-control and read-only sections of `core/governance/update-guidelines.md`, and checked write access per the first-run flow in `core/governance/first-run.md`.

When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes during onboarding; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation.

## Steps

### 0. Check for a starter profile template

If `core/memory/users/` contains a file with `source: template` in its YAML frontmatter (placed there by `setup.sh --profile`), the user chose a starter profile during setup. In this case:

1. Read the template file.
2. Present the pre-filled traits to the user: "I see you started with the [role] template. Let me walk through these to see what fits."
3. For each trait marked `[template]`, ask whether it's accurate, needs adjustment, or should be removed.
4. Fill in any blank fields through conversation.
5. Rewrite the profile: retag confirmed traits from `[template]` to `[observed]`, drop traits the user rejected, and incorporate any new traits discovered. Update the file's YAML frontmatter from `source: template` to `source: user-stated` and `trust: high`, and set `last_verified` to today's date.
6. Skip to step 5 (open-ended capture) after confirming all template traits — steps 2–4 below are for blank-slate onboarding.

If no template exists, proceed with step 1 as normal.

### 1. Introduce the memory system

Briefly explain to the user:

- You have persistent memory stored in this repository.
- What you learn in this conversation will be available in future sessions, even across different models.
- You'd like to ask a few questions to build an initial profile so future interactions start strong.

Keep it concise — one short paragraph, not a lecture.

### 2. Discover the user's role and context

Cover:

- **Role and responsibilities.** What they do, what domain they work in.
- **Key projects.** What they're actively working on or will be working on with AI assistance.
- **Domain expertise.** What they know well (so you can calibrate depth) and what's new to them.

### 3. Discover communication preferences

Cover:

- **Detail level.** Do they prefer concise answers or thorough explanations?
- **Tone.** Casual, professional, direct, exploratory?
- **Format preferences.** Do they like bullet points, prose, code-first, examples-first?
- **Anti-preferences.** Anything they find annoying or unhelpful in AI interactions.

### 4. Discover tools and environment

Cover:

- **Primary languages and frameworks** they work with.
- **Editor/IDE** they use.
- **Platforms and services** that come up regularly (cloud providers, CI/CD, etc.).
- **Collaboration context.** Solo work, team, open source?

**Pacing note for steps 2–4:** These categories guide *what* to cover, not the order of questions. Weave them naturally across 3–5 conversational turns rather than exhausting one category before starting the next. A question about their role might naturally lead to their tech stack, which leads to how they like code examples formatted. Follow the thread — the categories are a checklist to review afterward, not a script to follow linearly.

### 5. Open-ended capture

Ask: _"Is there anything else you'd like me to remember going forward? Anything that would make our interactions more useful?"_

This catches important context that structured questions miss. Don't skip it — it consistently surfaces the most valuable information.

### 6. Propose and write the initial profile

Based on the conversation:

1. Draft one or more proposed files in `core/memory/users/` capturing the discovered traits. Use the frontmatter schema:
   ```yaml
   ---
   source: user-stated
   origin_session: core/memory/activity/YYYY/MM/DD/chat-001
   created: YYYY-MM-DD
   last_verified: YYYY-MM-DD
   trust: high
   ---
   ```
2. Tag each trait with `[observed]` confidence when the user stated it directly.
3. Present the proposed portrait to the user and state that saving to `core/memory/users/` is a proposed-tier change that requires explicit confirmation.
4. If the user requests edits, revise the proposal and ask for confirmation again.
5. Only after explicit in-chat confirmation may you create the `core/memory/users/` files and update `core/memory/users/SUMMARY.md`.
6. That explicit confirmation counts as the required approval for the first user-profile file creation during onboarding.
7. If write access is unavailable, do not attempt the write. Instead, produce the confirmed profile using the **onboarding export format** (see `HUMANS/tooling/onboard-export-template.md`): output a single markdown document with top-level YAML frontmatter for `session_id` and `session_date`, followed by `## Identity Profile`, `## Session Transcript`, `## Session Summary`, and `## Session Reflection` sections. Use the canonical session path form (`core/memory/activity/YYYY/MM/DD/chat-001`) for `session_id`. Tell the user to save this output to a file and run `bash HUMANS/tooling/scripts/onboard-export.sh <file>` to import it into the repo. This replaces the generic deferred-action format for onboarding specifically, since the export script preserves the first session's metadata, transcript, and chat artifacts while handling the repo writes and commit.
8. If the session ends without confirmation, do not write to `core/memory/users/`.

### 7. Record the session

Log this conversation following the standard chat archival structure:

- Create the appropriate `core/memory/activity/YYYY/MM/DD/chat-001/` folder.
- Write `transcript.md`, `SUMMARY.md`, and `reflection.md`.
- Append access notes to the relevant ACCESS.jsonl files for any content files you read. Include `session_id` whenever the chat folder is known.
- If read-only, keep chat archival in the onboarding export produced in step 6 — do not produce a separate deferred-action summary. The export format already covers session transcript, summary, and reflection.

## Quality criteria

- The initial portrait should capture **5–10 durable traits**, all tagged `[observed]`.
- The user should feel accurately represented — not a caricature or a list of demographics, but a useful working portrait.
- Communication preferences should be specific enough to measurably change agent behavior in the next session.
- No trait should be invented or inferred beyond what the user actually said. If something is ambiguous, note it as `[tentative]` rather than guessing.
- No `core/memory/users/` write should occur before explicit user confirmation.

## Anti-patterns

- **Don't interrogate.** This should feel like a conversation, not a form.
- **Don't over-collect.** 5–10 solid traits are better than 25 shallow ones. You'll learn more over time.
- **Don't promise too much.** The memory system improves with use — don't set expectations for perfect recall from session one.
- **Don't write memory optimistically.** Proposal first, confirmation second, write third.

## After first use

This skill is designed for one-time use. After successful onboarding:

1. Propose archiving this file to `core/memory/skills/_archive/onboarding.md`.
2. Update `core/memory/skills/SUMMARY.md` to reflect the archival.
3. Log the archival in `CHANGELOG.md` as a `[curation]` entry.

The skill remains available in git history if the user ever wants to re-run onboarding (e.g., after a major life or role change).
