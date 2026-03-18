# Core Concepts

This document explains the system at the "why it is built this way" level.

- If you want to start using it, read [QUICKSTART.md](QUICKSTART.md).
- If you want deeper theory and future directions, read [DESIGN.md](DESIGN.md).
- If you want terminology help, read [GLOSSARY.md](GLOSSARY.md).

## In plain language

This repository is a durable memory layer for AI agents.

Instead of relying on a model to remember past conversations on its own, the important context lives in normal files that both humans and agents can inspect. That makes memory portable across tools, reviewable over time, and easier to correct when it drifts.

If you are nontechnical, a good mental model is: this is a shared notebook plus filing system plus change log for your AI.

If you are technical, a good mental model is: this is a git-backed, model-agnostic memory architecture with explicit routing, retrieval feedback, trust metadata, and human-governed updates.

## What problem this system is solving

Most AI systems are stateless or platform-bound:

- A model may forget important context between sessions.
- A memory feature may only work inside one product.
- It may be hard to see what the system "knows" or how that knowledge changed.
- Bad information can quietly accumulate because memory is opaque.

This system addresses those problems by making memory:

- Portable: the memory is in ordinary files, not hidden inside a vendor-specific feature.
- Inspectable: you can read, edit, diff, and audit what is stored.
- Governed: the system has explicit rules for what may change and how.
- Adaptive: retrieval and maintenance data feed back into how the memory is organized.

## Fundamental design decisions

### 1. Memory is stored in a git repository

This is the most important architectural decision.

Why:

- Files are durable and easy to back up.
- Git gives history, diffs, reversibility, and accountability.
- Any capable model can work with the same memory if it can read the repo.
- Humans are not locked into a single platform or vendor.

Tradeoff:

- This is less automatic than a hidden built-in memory feature.
- Users or agents sometimes need to maintain summaries, logs, and structure explicitly.

The system accepts that tradeoff because transparency and portability are more important than invisible convenience.

### 2. Routing is separate from reference material

The live operational router is [meta/quick-reference.md](../../meta/quick-reference.md).

That file tells an agent what to load for the current kind of session. It is intentionally compact because most sessions do not need the full governance stack.

Other files have different roles:

- [README.md](../../README.md): architecture and protocol reference.
- `meta/`: governance and operational rules for agents.
- `HUMANS/docs/`: explanation for people, not startup context for agents.

This separation is deliberate. It prevents the common failure mode where every important rule is repeated everywhere and drifts out of sync.

### 3. Context should be loaded progressively, not all at once

The system is designed around context efficiency.

Agents should not read the whole repo every session. They should start with summaries and routing files, then load additional detail only when the task justifies it.

Why:

- Context windows are limited.
- Most tasks do not need all historical detail.
- Smaller, cleaner context usually improves speed and response quality.

That is why the system uses:

- Summary files at many levels.
- A compact returning path for normal sessions.
- On-demand runbooks for detailed procedures.
- Metadata-first checks before loading heavier governance material.

### 4. Memory is curated, not merely accumulated

This system is not a dumping ground for every past interaction.

It treats memory as something that should become more useful over time. Files are summarized, retrieved selectively, logged in `ACCESS.jsonl`, reviewed for usefulness, and sometimes archived or promoted.

Why:

- More data is not the same as better memory.
- Uncurated memory becomes noisy, expensive, and misleading.
- Retrieval patterns reveal what the system actually uses, not just what exists.

The underlying philosophy is that memory quality matters more than memory volume.

### 5. Knowledge and instructions are kept separate

Not every file is allowed to tell an agent what to do.

The system distinguishes between:

- Informational memory: identity, knowledge, chats.
- Procedural authority: `skills/`, `meta/`, and core governance references.

This matters for safety. A knowledge file might contain useful facts, but it should not be able to smuggle in behavioral instructions that quietly change how the agent operates.

That separation is one of the main defenses against memory injection and slow behavioral drift.

### 6. Trust and provenance are explicit

Files can carry frontmatter describing where information came from, when it was created, whether it has been verified, and how much the system should trust it.

Why:

- Not all memory is equally reliable.
- A useful system must distinguish user-confirmed truth from inferred patterns and external research.
- Maintenance decisions depend on knowing how old and how verified content is.

This is why external material goes to `knowledge/_unverified/` first instead of becoming trusted memory automatically.

### 7. Humans stay in control of system-level changes

The system is adaptive, but it is not meant to rewrite its own rules without oversight.

Changes to high-leverage surfaces such as `meta/`, `skills/`, `README.md`, and other architectural references are deliberately governed. Significant system changes are logged in `CHANGELOG.md`.

Why:

- The most dangerous errors are often changes to the rules, not the facts.
- Users need to understand why the system behaves differently over time.
- Reviewability matters more than maximum automation when the system is modifying itself.

### 8. The architecture is designed to survive model changes

The repo is the continuity layer, not the model.

The user should be able to switch from one AI platform or model to another without losing the system's working memory, operating rules, and historical context.

This is why the repo uses plain files, platform adapters, human-readable documentation, and a model-agnostic startup contract.

## Architectural principles

These are the principles that should shape future changes to the system.

### Consistency

Operational router, README, setup flows, validators, tests, and human docs should not tell different stories. If the contract changes, dependent surfaces should be updated together.

Consistency matters because users and agents both rely on the same system. A "mostly right" rule set is still a broken architecture if different files imply different behavior.

### User-friendliness

The system should remain understandable and workable for normal people, not just for maintainers who already know it well.

That means:

- setup should be straightforward,
- docs should explain the why as well as the how,
- the file structure should stay legible,
- maintenance should prefer practical workflows over clever but fragile ones.

In this project, usability is not cosmetic polish. It is an architectural requirement.

### Context efficiency

The system should preserve a compact normal operating mode.

That means:

- summaries before deep reads,
- on-demand references before unconditional loading,
- small live routing files instead of giant startup prompts,
- careful attention to what each additional file costs in real sessions.

The goal is not minimalism for its own sake. The goal is to make the right context available at the right time without turning every session into a full bootstrap.

### Transparency and reversibility

A good memory system should make it easy to answer:

- What changed?
- Why did it change?
- Who approved it?
- Can we undo it?

Git history, changelog entries, explicit docs, and file-based storage make those questions answerable.

### Safety through containment

The system assumes memory can become dangerous if it is allowed to act like unreviewed instruction.

That is why it uses:

- trust levels,
- quarantine for external material,
- instruction containment,
- protected change surfaces,
- periodic review and decay rules.

The design does not aim to remove all risk. It aims to make risk visible, bounded, and recoverable.

## Guiding philosophy

At a high level, this system follows a few broad beliefs.

### Continuity is more valuable than novelty

A good long-term agent should feel like it remembers the user, their work, and prior decisions. That continuity usually matters more than squeezing out one extra clever response in a single isolated session.

### Explicit structure beats hidden magic

Many AI systems promise convenience by hiding how memory works. This project makes the opposite bet: memory should be inspectable, understandable, and governable even if that means a bit more structure.

### The system should improve through use

Usage data should help the memory become better organized over time. The architecture is meant to learn from retrieval patterns, not stay static forever.

### Human judgment remains central

The system supports human judgment; it does not replace it. User approval, correction, and review are core parts of keeping the memory trustworthy.

### Simple mechanisms should do most of the work

The repo prefers plain files, summaries, logs, and clear rules over hidden automation or exotic infrastructure. The idea is to make the system robust enough that it can survive tool churn, model churn, and future redesigns.

## What this means in practice

If you use this system as intended, you should expect:

- a heavier first-session setup than an ordinary chat,
- much lighter returning sessions once summaries and routing are in place,
- explicit approval for high-impact system changes,
- better long-term continuity across sessions and platforms,
- a memory that can be inspected and repaired instead of guessed at.

## When to read which document

- Read [QUICKSTART.md](QUICKSTART.md) if you want to set up or start using the system.
- Read this file if you want the core mental model and architectural rationale.
- Read [DESIGN.md](DESIGN.md) if you want deeper product philosophy, use cases, and future directions.
- Read [GLOSSARY.md](GLOSSARY.md) if a term is unfamiliar.
- Read [README.md](../../README.md) if you need the full architecture and agent protocol reference.
