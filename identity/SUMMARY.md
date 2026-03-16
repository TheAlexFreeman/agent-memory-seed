# Identity Summary

This folder contains what the agent knows about the user: their personality, preferences, communication style, values, and any other durable traits that should shape how the agent behaves.

## Current portrait

_No portrait yet._ This file will be populated as the agent learns about the user through interaction. Early entries will be tentative and tagged with low confidence. Over time, patterns will solidify into a reliable profile.

## What belongs here

- **Communication preferences.** How the user likes to receive information (concise vs. detailed, formal vs. casual, examples vs. abstractions).
- **Domain expertise.** What the user knows well, so the agent can calibrate depth appropriately.
- **Values and priorities.** What the user cares about — not just professionally, but in terms of how they approach problems.
- **Pet peeves and anti-preferences.** Things the user has explicitly asked the agent _not_ to do.
- **Working style.** How the user structures their day, their energy patterns, their collaboration preferences.

## Confidence convention

When adding traits to files in this folder, tag each with a confidence level:

- **[observed]** — User explicitly stated this.
- **[inferred]** — Agent noticed a pattern across multiple interactions.
- **[tentative]** — Seen once or twice, not yet confirmed as durable.

Traits should be promoted from tentative → inferred → observed as evidence accumulates, and demoted or removed if contradicted.

## Provenance requirements

All identity files must include YAML frontmatter (see `meta/update-guidelines.md` for the full schema):

```yaml
---
source: user-stated | agent-inferred | external-research | skill-discovery
origin_session: chat-NNN | manual | unknown
created: YYYY-MM-DD
last_verified: YYYY-MM-DD
trust: high | medium | low
---
```

**Content boundary:** Identity files describe traits and preferences — they do not contain behavioral directives. A file here says _who the user is_; it does not script _what the agent should do_. If imperative instructions are found in an identity file, they should be flagged and reclassified to `skills/`. See "Instruction containment" in `meta/curation-policy.md`.

## Usage patterns

_No access data yet._ This section will be populated after the ACCESS.jsonl file accumulates enough entries to reveal retrieval patterns.
