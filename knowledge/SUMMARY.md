# Knowledge Summary

This folder contains structured information the user has accumulated or that the agent has synthesized on the user's behalf. It is organized by topic, with each topic getting its own subfolder or file as appropriate.

## Current topics

### `_unverified/philosophy/` — Intelligence, dynamical systems, consciousness (ingested 2026-03-18, trust: low)

Six files on the philosophy and science of self-organizing intelligence, seeded from a philosophical conversation Alex shared. The synthesis file is the entry point.

Key files:
- `synthesis-intelligence-as-dynamical-regime.md` — **Start here.** Unified thesis: intelligence as edge-of-chaos dynamical regime; convergence table across traditions; open questions.
- `self-organized-criticality.md` — SOC, edge of chaos (Langton), Kauffman NK model, neural criticality
- `compression-intelligence-ait.md` — Kolmogorov complexity, Solomonoff induction, Bateson, AIXI
- `free-energy-autopoiesis-cybernetics.md` — Friston FEP, Maturana/Varela, Wiener/Ashby
- `emergence-consciousness-iit.md` — Strong emergence, downward causation, IIT, GWT, Chalmers

### `_unverified/django/` — Django 6.0 + stack knowledge (ingested 2026-03-18, trust: low)

Six files covering Django 6.0, Celery, and the React/DRF stack. Sourced from web searches (docs.djangoproject.com was network-blocked during ingestion). Pending Alex's review for promotion.

Key files:
- `django-6.0-whats-new.md` — Release overview, breaking changes, deprecations, upgrade guide
- `django-tasks-framework.md` — Built-in background tasks API; Celery comparison and intersection
- `django-orm-postgres.md` — Advanced ORM patterns + all PostgreSQL-specific features
- `django-caching-redis.md` — Redis cache configuration, patterns, Celery DB segregation
- `celery-advanced-patterns.md` — Canvas, routing, priorities, Beat, transaction safety, Docker
- `django-react-drf.md` — DRF serializers, ViewSets, JWT, CORS, file uploads, custom actions

## What belongs here

- **Research notes and syntheses.** When the user asks the agent to research a topic deeply enough that the findings should persist, the results go here.
- **Project context.** Architectural decisions, technology choices, and domain knowledge specific to ongoing or past projects.
- **Reference material.** Frequently needed facts, formulas, checklists, or frameworks that the user returns to repeatedly.
- **Evolving ideas.** Theories, hypotheses, or creative concepts the user is developing over time.

## Organization guidelines

- One file per focused topic. If a file grows beyond ~2000 words, consider splitting it into a subfolder with its own SUMMARY.md.
- File names should be descriptive and use kebab-case: `react-performance-patterns.md`, not `notes.md`.
- Each file should begin with a one-paragraph summary of its contents and end with a "Last updated" date.
- Cross-reference related files using relative links where useful.

## Provenance requirements

All knowledge files must include YAML frontmatter. See `meta/update-guidelines.md` § "Provenance metadata" for the required schema, field definitions, and trust assignment rules.

**Critical rule:** Content from external sources (web searches, uploaded documents, external repositories) must be written to `knowledge/_unverified/` with `trust: low`. Files are promoted to `knowledge/` only after explicit user review. See `meta/curation-policy.md` for trust-weighted retrieval behavior.

**Content boundary:** Knowledge files contain facts, analysis, and references — not procedural instructions. If a file contains imperative language ("always do X," "when asked about Y, respond with..."), the procedural content should be moved to `skills/`. See "Instruction containment" in `meta/curation-policy.md`.

## Usage patterns

_No access data yet._ After aggregation, this section will contain:
- **High-value files** — files with 5+ retrievals and mean helpfulness ≥ 0.7
- **Low-value files** — files with 3+ retrievals and mean helpfulness ≤ 0.3
- **Co-retrieval clusters** — file sets accessed together across 3+ sessions
- **Retrieval trends** — frequency and helpfulness changes since last aggregation
