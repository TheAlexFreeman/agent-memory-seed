# Knowledge Summary

This folder contains structured information the user has accumulated or that the agent has synthesized on the user's behalf. It is organized by topic, with each topic getting its own subfolder or file as appropriate.

## Current topics

<!-- section: philosophy -->
### `philosophy/` — Intelligence, dynamical systems, consciousness, narrative cognition, history of ideas (promoted 2026-03-20, trust: medium)

Forty-six files on the philosophy and science of self-organizing intelligence, plus a broad survey of the history of philosophy. Seeded from Alex's conversation and extended through `plans/philosophy-history-survey.md`. See `philosophy/SUMMARY.md` and `philosophy/history/SUMMARY.md` for the full index.

Key entry points:
- `synthesis-intelligence-as-dynamical-regime.md` — **Start here.** Unified thesis, convergence table, open questions
- `history/` — Ancient through contemporary, Western and non-Western traditions, synthesis files
- `narrative-cognition.md`, `cognitive-linguistics-metaphor-blending.md` — Cognition, metaphor, narrative
- `llm-vs-human-mind-comparative-analysis.md` — LLM implications

<!-- section: software-engineering -->
### `software-engineering/` — Django, React, DevOps stack (promoted 2026-03-20, trust: medium)

Forty-one files covering Alex's primary development stack: Django 6.0 + DRF + Celery, React 19 + Chakra UI 3, and Docker-based DevOps. Sanity-checked and promoted from `_unverified/` on 2026-03-20.

Subfolders:
- `django/` — 19 files: Django 6.0, ORM, DRF, Celery, migrations, observability, production stack
- `react/` — 13 files: React 19, Chakra 3, TanStack, Vite, testing
- `devops/` — 9 files: Docker Compose, production config, CI/CD, Celery workers, monitoring

Key entry points:
- `django/django-production-stack.md` — Service boundaries, startup order, Redis topology
- `react/react-19-overview.md` — Actions, forms, upgrade path
- `devops/docker-production-config.md` — Production Docker patterns

<!-- section: ai-history -->
### `ai-history/` — AI paradigm genealogy (promoted 2026-03-19, trust: medium)

Eleven files tracing the causal history of the current AI paradigm from 1943 to 2025 across five subfolders: `origins/`, `deep-learning/`, `language-models/`, `frontier/`, and `synthesis/`. See `ai-history/SUMMARY.md` for the full index.

Key files:
- `origins/cybernetics-perceptrons-and-the-first-connectionist-wave.md` — McCulloch-Pitts, Rosenblatt, the first learning optimism, and the limit of linear separability (1943–1969)
- `origins/backpropagation-and-the-pdp-revival.md` — The credit assignment unlock: Rumelhart/Hinton/Williams backprop, PDP program, vanishing gradients
- `deep-learning/gpus-imagenet-and-the-deep-learning-turn.md` — ImageNet, CUDA, AlexNet, dropout, ReLU — the data/compute unlock (2012)
- `language-models/attention-and-the-transformer-breakthrough.md` — Self-attention, multi-head attention, positional encoding, BERT, GPT (2017–2018)
- `language-models/bert-gpt-and-the-scaling-laws-era.md` — GPT-3, in-context learning, Kaplan scaling laws, Chinchilla compute-optimal training
- `frontier/instruction-tuning-rlhf-and-the-chat-model-turn.md` — InstructGPT, RLHF/PPO, Constitutional AI, DPO, ChatGPT launch (2022)
- `frontier/multimodality-tool-use-and-reasoning-time-compute.md` — Vision-language, RAG, tool use/agents, MoE, open weights, o1 inference-time compute (2022–2026)
- `synthesis/how-the-current-ai-paradigm-formed.md` — Full causal synthesis: nine bottleneck-unlock transitions, four through-lines end-to-end, open assumptions

<!-- section: ai-tools -->
### `ai-tools/` — AI tools landscape and ecosystem positioning (promoted 2026-03-20, trust: medium)

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
### `tooling/` — MCP protocol knowledge and runtime notes (promoted 2026-03-20, trust: medium)

Five files plus a four-file MCP subfolder covering the Model Context Protocol specification, server design patterns, ecosystem landscape, 2026 roadmap, and a local debugging case study.

Key entry points:
- `mcp/SUMMARY.md` — Index for the MCP knowledge base (4 files promoted from `_unverified/` on 2026-03-20)
- `mcp/mcp-protocol-overview.md` — Architecture and spec overview: Host/Client/Server model, transports, primitives, lifecycle
- `mcp/mcp-server-design-patterns.md` — Practical build guide: FastMCP, tool design, security, testing
- `mcp/mcp-ecosystem-survey.md` — 108 clients, feature matrix, reference servers, SDKs, frameworks (March 2026)
- `mcp/mcp-2026-roadmap-update.md` — 2026 roadmap: transport scalability, Tasks, enterprise, governance
- `codex-mcp-timeouts-git-stdin.md` — Debugging stdio transport stdin inheritance in this repo's MCP server

<!-- section: mathematics -->
### `mathematics/` — Logic, game theory, information theory, dynamical systems, probability, statistical mechanics, causal inference, and complexity theory (promoted 2026-03-20/21, trust: high/medium)

Sixty-five files across eight subfolders. The original 35 files (logic-foundations, game-theory, information-theory) were reviewed and promoted from `_unverified/` on 2026-03-20 with trust: high. Seven dynamical-systems files were added on 2026-03-21 with trust: medium. Seven probability files were added on 2026-03-21 with trust: medium. Six statistical-mechanics files were added on 2026-03-21 with trust: medium. Five causal-inference files were added on 2026-03-21 with trust: medium. Five complexity-theory files were added on 2026-03-21 with trust: medium.

Subfolders:
- `logic-foundations/` — 11 files: Gödel incompleteness (1st and 2nd), ZFC set theory, propositional and FOL, Turing undecidability, Kolmogorov complexity, category theory, Curry-Howard isomorphism, dependent types and proof assistants, simple type theory and lambda calculus, compactness and Löwenheim-Skolem
- `game-theory/` — 12 files: Normal-form games and Nash equilibrium, extensive-form and backward induction, Prisoner's dilemma and coordination games, evolutionary game theory, evolution of cooperation, Arrow's impossibility theorem, Gibbard-Satterthwaite theorem, mechanism design and revelation principle, VCG mechanisms, Gale-Shapley matching markets, Spence costly signaling, Crawford-Sobel cheap talk
- `information-theory/` — 12 files: Shannon entropy and source coding theorem, KL divergence and cross-entropy, mutual information and channel capacity, rate-distortion theory, MDL principle, PAC learning and sample complexity, VC dimension and fundamental theorem, compression-generalization connection, information bottleneck and deep learning, inductive bias and no-free-lunch, double descent and benign overfitting, limits and open questions
- `dynamical-systems/` — 7 files: Phase space, flows, fixed points and stability (dynamical-systems-fundamentals); bifurcation theory and catastrophe theory; chaos, Lorenz system, strange attractors, Lyapunov exponents; self-organized criticality, Bak sandpile, Langton edge-of-chaos, Kauffman NK models, neural criticality; ergodic theory, Birkhoff theorem, mixing hierarchy, ergodicity breaking; complex networks, small-world, scale-free, preferential attachment; fractals, dimension, multiscale structure, multifractal analysis
- `probability/` — 7 files: Measure-theoretic foundations (Kolmogorov axioms, σ-algebras, convergence theorems, CLT, Borel-Cantelli); Bayesian inference, priors, posteriors, and Bernstein-von Mises; concentration inequalities (Hoeffding, McDiarmid, Azuma-Hoeffding, matrix Bernstein, Rademacher complexity); Markov chains, mixing times, MCMC, spectral gap; Gaussian processes, RKHS, Bayesian nonparametrics (Dirichlet process, CRP, IBP); martingales, optional stopping theorem, Kelly criterion, sequential analysis; stochastic processes, Brownian motion, Itô calculus, SDEs, Fokker-Planck
- `statistical-mechanics/` — 6 files: Thermodynamic entropy, Boltzmann-Gibbs-Shannon unification, Jaynes MaxEnt, Landauer's principle; partition function, Helmholtz free energy, variational free energy, Legendre transforms; Ising model, phase transitions, mean-field, Landau theory, universality, renormalisation group; Hopfield networks, Boltzmann machines, RBMs, contrastive divergence, modern Hopfield-transformer connection; spin glasses, SK model, replica method, RSB, ultrametricity, applications to random CSPs; statistical mechanics of learning, Gardner capacity, teacher-student framework, double descent, neural scaling laws

Key entry points:
- `logic-foundations/godels-first-incompleteness.md` — Hilbert program, Gödel numbering, diagonal lemma, proof sketch
- `game-theory/normal-form-games-nash-equilibrium.md` — Strategic form games, Nash's existence theorem, mixed strategies
- `game-theory/mechanism-design-revelation-principle.md` — Reverse game theory, incentive compatibility, revelation principle
- `information-theory/entropy-source-coding-theorem.md` — Shannon entropy, source coding theorem, Huffman codes
- `information-theory/vc-dimension-fundamental-theorem.md` — Shattering, VC dimension, Sauer-Shelah, fundamental theorem of PAC learning
- `dynamical-systems/self-organized-criticality.md` — **Start here for dynamical systems.** SOC, edge-of-chaos, Kauffman NK, neural criticality hypothesis — directly grounds the intelligence-as-dynamical-regime thesis
- `dynamical-systems/dynamical-systems-fundamentals.md` — Phase space, flows, fixed points, attractors, Lyapunov stability
- `probability/measure-theoretic-foundations.md` — **Start here for probability.** Kolmogorov axioms, measure-theoretic conditional expectation, convergence theorems, CLT
- `probability/stochastic-processes-brownian-sde.md` — Brownian motion, Itô calculus, SDEs, Fokker-Planck — bridge to FEP and diffusion models
- `statistical-mechanics/thermodynamics-entropy-unification.md` — **Start here for stat mech.** Boltzmann-Gibbs-Shannon unification, Jaynes MaxEnt, Landauer's principle
- `statistical-mechanics/partition-function-free-energy.md` — Partition function, Helmholtz free energy, variational principles — template for variational inference and FEP
- `statistical-mechanics/statistical-mechanics-of-learning.md` — Gardner capacity, phase transitions in generalisation, double descent, neural scaling laws

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
