# Knowledge Summary

This folder contains structured information the user has accumulated or that the agent has synthesized on the user's behalf. It is organized by topic, with each topic getting its own subfolder or file as appropriate.

## Current topics

<!-- section: philosophy -->
### `_unverified/philosophy/` — Intelligence, dynamical systems, consciousness, narrative cognition, cognitive linguistics (ingested 2026-03-18, trust: low)

Ten files on the philosophy and science of self-organizing intelligence, seeded from a philosophical conversation Alex shared and extended through follow-up research. The synthesis file is the entry point. Output files for the history of philosophy survey will land in `_unverified/philosophy/history/` — see `plans/philosophy-history-survey.md` for the research plan.

Key files:
- `synthesis-intelligence-as-dynamical-regime.md` — **Start here.** Unified thesis: intelligence as edge-of-chaos dynamical regime; convergence table across traditions; open questions.
- `self-organized-criticality.md` — SOC, edge of chaos (Langton), Kauffman NK model, neural criticality
- `compression-intelligence-ait.md` — Kolmogorov complexity, Solomonoff induction, Bateson, AIXI
- `free-energy-autopoiesis-cybernetics.md` — Friston FEP, Maturana/Varela, Wiener/Ashby
- `emergence-consciousness-iit.md` — Strong emergence, downward causation, IIT, GWT, Chalmers
- `llm-vs-human-mind-comparative-analysis.md` — Three root divergences framework, comparative strengths/weaknesses, memory system implications
- `narrative-cognition.md` — Narrative as constitutive cognitive structure: Bruner's two modes, Ricoeur's idem/ipse, Lakoff/Johnson image schemas, Jungian archetypes, DMN as narrative engine, LLM implications
- `cognitive-linguistics-metaphor-blending.md` — Lakoff & Johnson's CMT, Fauconnier & Turner's blending theory, Sweetser's polysemy and viewpoint work. Synthesis with dynamical systems framework and LLM implications.
- `blending-compression-coupling-construal.md` — Focused synthesis: blending-as-compression, structural coupling and metaphor, subjective construal and narrative viewpoint. Narrative as cognitive triangulation.

<!-- section: django -->
### `_unverified/django/` — Django 6.0 + stack knowledge (ingested 2026-03-18, trust: low)

Ten files covering Django 6.0, DRF API design/testing, pytest performance testing, structlog/Sentry observability, Celery, Redis caching, and production-stack operations. The cluster was revised with current official Django, DRF, Celery, pytest-django, structlog, and Sentry docs on 2026-03-18, and the Celery depth track now includes a dedicated Canvas/workflow note. Pending Alex's review for promotion.

Key files:
- `django-6.0-whats-new.md` — Django 6.0 release-line overview with 6.0.1/6.0.3 patch-line notes and stack-relevant upgrade concerns
- `django-tasks-framework.md` — Corrected `django.tasks` model: built-in dev/test backends only, transaction caveats, and Celery decision boundary
- `django-orm-postgres.md` — Advanced ORM patterns, Postgres features, `Lexeme`, indexing guidance, and production-oriented DB notes
- `django-caching-redis.md` — Native Redis cache backend, replication/topology, versioning, invalidation, and operational separation from Celery
- `celery-advanced-patterns.md` — Idempotency, ack strategy, retries, queue isolation, result-storage discipline, and Celery-vs-Django-tasks boundary
- `django-react-drf.md` — React-facing API design with DRF: auth mode choices, CSRF/CORS, pagination, filtering, throttling, and error contracts
- `django-production-stack.md` — Cross-cutting operational guidance for Django + Postgres + Redis + Celery + Docker
- `celery-canvas-in-depth.md` — Chain/group/chord semantics, immutable signatures, chord backend implications, and workflow composition patterns
- `drf-testing-pytest-django-perf-rec.md` — DRF contract/testing patterns plus `pytest-django` and `django-perf-rec` guidance for API teams
- `django-observability-structlog-sentry.md` — Structured logging and monitoring patterns for Django/Celery stacks using structlog and Sentry

<!-- section: react -->
### `_unverified/react/` — React + Chakra frontend research (ingested 2026-03-18, trust: low)

Four files covering React 19 and Chakra UI 3. Sourced from official React and Chakra docs/blog pages, with a focus on modern React frontends and design-system-driven styling.

Key files:
- `react-19-overview.md` — Stable release status, Actions/forms APIs, `use`, metadata/assets support, upgrade hazards, TS changes, and React 19.2 additions
- `chakra-ui-3-overview.md` — Chakra 3 architecture, migration surface, state-machine components, performance changes, and ecosystem shifts from v2
- `chakra-ui-3-styling-system.md` — `createSystem`, tokens, semantic tokens, recipes, slot recipes, virtual colors, cascade layers, and CLI typegen
- `chakra-ui-3-react-frontend-patterns.md` — Practical synthesis for building consistent, accessible, responsive, and mode-aware React frontends with Chakra 3

<!-- section: ai-tools -->
### `ai-tools/` — AI tools landscape and ecosystem positioning (promoted 2026-03-19, trust: medium)

Two files covering the current AI tools landscape and where agent-memory-seed fits within it.

Key files:
- `ai-tools-landscape-2026.md` — Survey of AI coding environments, CLI agents, autonomous agents, orchestration frameworks, research tools, infrastructure, and local inference as of early 2026; frontier model comparison table and 7 key ecosystem trends
- `agent-memory-in-ai-ecosystem.md` — How agent-memory-seed is positioned relative to vector RAG, Claude.ai Projects, LangGraph checkpointing, and LLM-native memory systems; why the git-backed governed-memory approach is distinctive; how it connects to current trends (agentic loops, vibe coding debt, multi-agent coordination)

<!-- section: systems-architecture -->
### `systems-architecture/` — Git-backed systems architecture research (promoted 2026-03-19, trust: medium)

Thirteen files covering the storage, concurrency, and data-modeling primitives underlying agent-memory-seed. Reviewed and promoted from `_unverified/` on 2026-03-19. See `systems-architecture/SUMMARY.md` for the full index.

Key files:
- `git-object-model.md` — Git's blob/tree/commit/tag object graph, the index as staging boundary, `index.lock`, refs, reflog, and packfiles, tied back to the current MCP server write path
- `git-worktrees-and-hooks.md` — Linked worktree topology, shared versus per-worktree refs, orphan branch mechanics, hook execution model, and how those map onto the worktree integration roadmap
- `git-plumbing-and-automation.md` — Plumbing versus porcelain, explicit commit publication primitives, `update-ref`, `cat-file`, `notes`, `bundle`, sparse checkout, and resilient automation patterns
- `filesystem-atomicity-and-locking.md` — `rename()` atomicity, `O_CREAT|O_EXCL` lock acquisition, advisory locking limits, unlink failure modes, and the visibility/durability distinction
- `filesystems-for-developers.md` — Journaling and copy-on-write filesystems, FUSE and network-share caveats, inotify watcher limitations, and environment-tier guidance for stateful tooling
- `write-ahead-logging-and-wal-design.md` — WAL invariants, SQLite and PostgreSQL WAL behavior, Git staging as a mini-WAL, and staged-transaction requirements for multi-file MCP writes
- `append-only-logs-and-compaction.md` — Log-structured storage, LSM/Kafka compaction ideas, event sourcing, archive segmentation, and ACCESS summary materialization
- `concurrency-models-for-local-state.md` — Optimistic versus pessimistic control, version tokens as compare-and-swap, MVCC for derived SQLite state, and actor-model single-writer design
- `crdts-and-collaborative-text.md` — CRDT guarantees and limits, Automerge/Yjs/OT comparison, and why governed Markdown files should prefer serialized writes over text convergence
- `provenance-and-trust-models.md` — PROV-O, SLSA-style process trust, Biba integrity framing, and stronger provenance fields for governed memory artifacts
- `temporal-data-modeling.md` — Transaction time versus valid time, verification-history trade-offs, event-time precision, and freshness modeling beyond date thresholds
- `schema-evolution-strategies.md` — Protobuf/Avro compatibility lessons, expand-contract migrations, and explicit versioning boundaries for frontmatter, ACCESS, and MCP contracts
- `content-addressable-storage-and-integrity.md` — CAS fundamentals, Git as a Merkle DAG, commit-SHA provenance, and integrity design grounded in Git's existing object model

<!-- section: tooling -->
### `tooling/` — Codex and MCP runtime notes (ingested 2026-03-18, trust: medium)

One file capturing a local debugging session for the repo's `agent_memory` MCP server under Codex Desktop.

Key files:
- `codex-mcp-timeouts-git-stdin.md` — Investigation showing that apparent Codex MCP config failures were actually stdio transport interference from git subprocess stdin inheritance, plus the patch and verification path

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
