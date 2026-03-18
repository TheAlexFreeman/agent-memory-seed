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

Seven files covering Django 6.0, Celery, Redis caching, production-stack operations, and the React/DRF boundary. The cluster was revised with current official Django, DRF, and Celery docs on 2026-03-18. Pending Alex's review for promotion.

Key files:
- `django-6.0-whats-new.md` — Django 6.0 release-line overview with 6.0.1/6.0.3 patch-line notes and stack-relevant upgrade concerns
- `django-tasks-framework.md` — Corrected `django.tasks` model: built-in dev/test backends only, transaction caveats, and Celery decision boundary
- `django-orm-postgres.md` — Advanced ORM patterns, Postgres features, `Lexeme`, indexing guidance, and production-oriented DB notes
- `django-caching-redis.md` — Native Redis cache backend, replication/topology, versioning, invalidation, and operational separation from Celery
- `celery-advanced-patterns.md` — Idempotency, ack strategy, retries, queue isolation, result-storage discipline, and Celery-vs-Django-tasks boundary
- `django-react-drf.md` — React-facing API design with DRF: auth mode choices, CSRF/CORS, pagination, filtering, throttling, and error contracts
- `django-production-stack.md` — Cross-cutting operational guidance for Django + Postgres + Redis + Celery + Docker

### `_unverified/react/` — React + Chakra frontend research (ingested 2026-03-18, trust: low)

Four files covering React 19 and Chakra UI 3. Sourced from official React and Chakra docs/blog pages, with a focus on modern React frontends and design-system-driven styling.

Key files:
- `react-19-overview.md` — Stable release status, Actions/forms APIs, `use`, metadata/assets support, upgrade hazards, TS changes, and React 19.2 additions
- `chakra-ui-3-overview.md` — Chakra 3 architecture, migration surface, state-machine components, performance changes, and ecosystem shifts from v2
- `chakra-ui-3-styling-system.md` — `createSystem`, tokens, semantic tokens, recipes, slot recipes, virtual colors, cascade layers, and CLI typegen
- `chakra-ui-3-react-frontend-patterns.md` — Practical synthesis for building consistent, accessible, responsive, and mode-aware React frontends with Chakra 3

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
