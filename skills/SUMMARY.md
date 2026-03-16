# Skills Summary

This folder contains procedural knowledge — instructions for how the agent should perform specific types of tasks. Unlike knowledge (which is *what*), skills are *how*.

## Current skills

*No skills yet.* Skills will be created when the user and agent discover recurring workflows that benefit from codified procedures.

## What belongs here

- **Recurring workflows.** If the user asks for the same type of output more than twice, the pattern should be captured as a skill.
- **Quality standards.** Specific criteria the user applies when evaluating certain kinds of work (e.g., "when writing commit messages, always include the ticket number and use imperative mood").
- **Tool-specific procedures.** How to interact with particular tools, APIs, or platforms the user works with regularly.
- **Templates.** Reusable structures for common outputs (emails, reports, code patterns).

## Skill file format

Each skill file should include:

1. **When to use this skill.** Trigger conditions — what kind of user request activates this procedure.
2. **Steps.** The actual procedure, written as clear instructions the agent should follow.
3. **Quality criteria.** How to evaluate whether the output meets the user's standards.
4. **Examples.** At least one concrete example of good output, ideally drawn from an actual past interaction.
5. **Anti-patterns.** Common mistakes to avoid, especially ones the user has previously corrected.

## Skill discovery

Skills often emerge from corrections. When the user says "no, do it like this instead," that correction is a candidate for a new skill or a refinement of an existing one. The agent should:

1. Note the correction in the current session.
2. Check if a related skill already exists.
3. If yes, propose updating it. If no, propose creating one.
4. Include the triggering interaction as the example.

## Usage patterns

*No access data yet.* This section will be populated after the ACCESS.jsonl file accumulates enough entries to reveal retrieval patterns.
