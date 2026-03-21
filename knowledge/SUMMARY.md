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
### `mathematics/` — Logic, game theory, information theory, dynamical systems, probability, statistical mechanics, causal inference, complexity theory, and optimization (promoted 2026-03-20/21, trust: high/medium)

Seventy files across nine subfolders. The original 35 files (logic-foundations, game-theory, information-theory) were reviewed and promoted from `_unverified/` on 2026-03-20 with trust: high. Seven dynamical-systems files were added on 2026-03-21 with trust: medium. Seven probability files were added on 2026-03-21 with trust: medium. Six statistical-mechanics files were added on 2026-03-21 with trust: medium. Five causal-inference files were added on 2026-03-21 with trust: medium. Five complexity-theory files were added on 2026-03-21 with trust: medium. Five optimization files were added on 2026-03-21 with trust: medium.

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

<!-- section: ai-frontier -->
### AI frontier (ai/frontier/)
- **[agentic-frameworks.md](knowledge/ai/frontier/agentic-frameworks.md)** — Agentic Frameworks
- **[frontier-alignment-research.md](knowledge/ai/frontier/alignment/frontier-alignment-research.md)** — Frontier Alignment Research
- **[instruction-following.md](knowledge/ai/frontier/alignment/instruction-following.md)** — Instruction Following
- **[rlhf-reward-models.md](knowledge/ai/frontier/alignment/rlhf-reward-models.md)** — Rlhf Reward Models
- **[mixture-of-experts.md](knowledge/ai/frontier/architectures/mixture-of-experts.md)** — Mixture Of Experts
- **[state-space-models.md](knowledge/ai/frontier/architectures/state-space-models.md)** — State Space Models
- **[synthetic-data-self-improvement.md](knowledge/ai/frontier/architectures/synthetic-data-self-improvement.md)** — Synthetic Data Self Improvement
- **[compression-and-intelligence.md](knowledge/ai/frontier/epistemology/compression-and-intelligence.md)** — Compression And Intelligence
- **[knowledge-and-knowing.md](knowledge/ai/frontier/epistemology/knowledge-and-knowing.md)** — Knowledge And Knowing
- **[llms-as-dynamical-systems.md](knowledge/ai/frontier/epistemology/llms-as-dynamical-systems.md)** — Llms As Dynamical Systems
- **[foundation-model-governance.md](knowledge/ai/frontier/foundation-model-governance.md)** — Foundation Model Governance
- **[hardware-efficiency.md](knowledge/ai/frontier/hardware-efficiency.md)** — AI Hardware and Efficiency Trends
- **[inference-time-compute.md](knowledge/ai/frontier/inference-time-compute.md)** — Inference-Time Compute Infrastructure
- **[emergence-phase-transitions.md](knowledge/ai/frontier/interpretability/emergence-phase-transitions.md)** — Emergence Phase Transitions
- **[llm-representation-confabulation.md](knowledge/ai/frontier/interpretability/llm-representation-confabulation.md)** — Llm Representation Confabulation
- **[mechanistic-interpretability.md](knowledge/ai/frontier/interpretability/mechanistic-interpretability.md)** — Mechanistic Interpretability
- **[memetic-security-capability-robustness.md](knowledge/ai/frontier/memetic-security-capability-robustness.md)** — Memetic Security Capability Robustness
- **[agent-architecture-patterns.md](knowledge/ai/frontier/multi-agent/agent-architecture-patterns.md)** — Agent Architecture Patterns
- **[human-in-the-loop.md](knowledge/ai/frontier/multi-agent/human-in-the-loop.md)** — Human In The Loop
- **[multi-agent-coordination.md](knowledge/ai/frontier/multi-agent/multi-agent-coordination.md)** — Multi Agent Coordination
- **[benchmarking-reasoning.md](knowledge/ai/frontier/reasoning/benchmarking-reasoning.md)** — Benchmarking Reasoning
- **[reasoning-models.md](knowledge/ai/frontier/reasoning/reasoning-models.md)** — Reasoning Models
- **[test-time-compute-scaling.md](knowledge/ai/frontier/reasoning/test-time-compute-scaling.md)** — Test Time Compute Scaling
- **[agentic-rag-patterns.md](knowledge/ai/frontier/retrieval-memory/agentic-rag-patterns.md)** — Agentic Rag Patterns
- **[colpali-visual-document-retrieval.md](knowledge/ai/frontier/retrieval-memory/colpali-visual-document-retrieval.md)** — Colpali Visual Document Retrieval
- **[hyde-query-expansion.md](knowledge/ai/frontier/retrieval-memory/hyde-query-expansion.md)** — Hyde Query Expansion
- **[late-chunking-contextual-embeddings.md](knowledge/ai/frontier/retrieval-memory/late-chunking-contextual-embeddings.md)** — Late Chunking Contextual Embeddings
- **[long-context-architecture.md](knowledge/ai/frontier/retrieval-memory/long-context-architecture.md)** — Long Context Architecture
- **[persistent-memory-architectures.md](knowledge/ai/frontier/retrieval-memory/persistent-memory-architectures.md)** — Persistent Memory Architectures
- **[rag-architecture.md](knowledge/ai/frontier/retrieval-memory/rag-architecture.md)** — Rag Architecture
- **[reranking-two-stage-retrieval.md](knowledge/ai/frontier/retrieval-memory/reranking-two-stage-retrieval.md)** — Reranking Two Stage Retrieval

<!-- section: social-science -->
### Social Science

#### `cultural-evolution/` — Memetics, dual inheritance, transmission, cultural group selection (promoted 2026-03-21, trust: medium)
- **[blackmore-meme-machine.md](knowledge/social-science/cultural-evolution/blackmore-meme-machine.md)** — Blackmore: memes as replicators, meme's-eye view, critique of memetics
- **[boyd-richerson-dual-inheritance.md](knowledge/social-science/cultural-evolution/boyd-richerson-dual-inheritance.md)** — Dual inheritance theory, transmission biases, gene-culture coevolution
- **[dawkins-meme-concept.md](knowledge/social-science/cultural-evolution/dawkins-meme-concept.md)** — Dawkins: meme as cultural replicator, vehicles, extended phenotype
- **[fricker-epistemic-injustice.md](knowledge/social-science/cultural-evolution/fricker-epistemic-injustice.md)** — Testimonial and hermeneutical injustice; credibility gaps as biased cultural transmission
- **[henrich-collective-brain.md](knowledge/social-science/cultural-evolution/henrich-collective-brain.md)** — Collective brain, cumulative culture, population size and cultural complexity
- **[hull-replicator-interactor.md](knowledge/social-science/cultural-evolution/hull-replicator-interactor.md)** — Replicator/interactor distinction, units of selection, generalised Darwinism
- **[idea-fitness-vs-truth.md](knowledge/social-science/cultural-evolution/idea-fitness-vs-truth.md)** — Why adaptive ideas outcompete true ideas; epistemic implications
- **[llms-cultural-evolution-mechanism.md](knowledge/social-science/cultural-evolution/llms-cultural-evolution-mechanism.md)** — LLMs as a new axis of cultural transmission; implications for idea fitness
- **[norms-punishment-cultural-group-selection.md](knowledge/social-science/cultural-evolution/norms-punishment-cultural-group-selection.md)** — Norm enforcement, altruistic punishment, cultural group selection
- **[prestige-cascades-llm-adoption.md](knowledge/social-science/cultural-evolution/prestige-cascades-llm-adoption.md)** — Prestige bias, cascades, LLM adoption as a case study
- **[tomasello-ratchet-shared-intentionality.md](knowledge/social-science/cultural-evolution/tomasello-ratchet-shared-intentionality.md)** — Ratchet effect, shared intentionality, cumulative cultural learning
- **[transmission-biases-cognitive-attractors.md](knowledge/social-science/cultural-evolution/transmission-biases-cognitive-attractors.md)** — Conformist, prestige, content, and skill biases; cognitive attractors (Sperber)

#### `sociology-of-knowledge/` — How knowledge is socially produced, contested, and stabilized (promoted 2026-03-21, trust: low — awaiting review)
- **[mannheim-sociology-of-knowledge.md](knowledge/social-science/sociology-of-knowledge/mannheim-sociology-of-knowledge.md)** — Mannheim: knowledge as socially situated; ideology vs utopia; the free-floating intellectual; relationism vs relativism
- **[merton-scientific-norms.md](knowledge/social-science/sociology-of-knowledge/merton-scientific-norms.md)** — CUDOS norms (Communalism, Universalism, Disinterestedness, Organized Skepticism); Matthew Effect; normative vs descriptive debate
- **[kuhn-paradigms-scientific-revolutions.md](knowledge/social-science/sociology-of-knowledge/kuhn-paradigms-scientific-revolutions.md)** — Normal science, paradigms, anomalies, crisis, scientific revolution, incommensurability; applies directly to AI paradigm genealogy
- **[latour-actor-network-theory.md](knowledge/social-science/sociology-of-knowledge/latour-actor-network-theory.md)** — ANT: translation, enrollment, black-boxing, inscription, immutable mobiles; symmetry between human and nonhuman actors
- **[social-construction-of-scientific-knowledge.md](knowledge/social-science/sociology-of-knowledge/social-construction-of-scientific-knowledge.md)** — Edinburgh strong programme (Bloor), experimenter's regress (Collins), science wars (Sokal), synthesis position

#### `collective-action/` — Collective action theory and institutional economics (promoted 2026-03-21, trust: low — awaiting review)
- **[olson-logic-of-collective-action.md](knowledge/social-science/collective-action/olson-logic-of-collective-action.md)** — Free-rider problem, public goods, large vs small groups, selective incentives; the foundational collective action pessimism
- **[ostrom-governing-the-commons.md](knowledge/social-science/collective-action/ostrom-governing-the-commons.md)** — Eight design principles for commons governance; polycentric governance; empirical challenge to Hardin and Olson
- **[north-institutions-institutional-change.md](knowledge/social-science/collective-action/north-institutions-institutional-change.md)** — Institutions as rules of the game; formal vs informal; transaction costs; path dependence; adaptive efficiency
- **[acemoglu-robinson-inclusive-institutions.md](knowledge/social-science/collective-action/acemoglu-robinson-inclusive-institutions.md)** — Inclusive vs extractive institutions; critical junctures; creative destruction; political economy of institutional persistence
- **[collective-action-synthesis-ai-governance.md](knowledge/social-science/collective-action/collective-action-synthesis-ai-governance.md)** — Synthesis: Olson-Ostrom-North-A&R applied to AI capability race, safety coordination, and governance design

#### `social-psychology/` — Conformity, obedience, group dynamics, bystander effect (promoted 2026-03-21, trust: low — awaiting review)
- **[asch-conformity-experiments.md](knowledge/social-science/social-psychology/asch-conformity-experiments.md)** — Asch line-length experiments; normative vs informational conformity; unanimity effect; maps to conformist bias in cultural transmission
- **[milgram-obedience-experiments.md](knowledge/social-science/social-psychology/milgram-obedience-experiments.md)** — Obedience to authority (65% max shock); agentic state; situational variations; maps to prestige/authority bias
- **[zimbardo-stanford-prison-situation.md](knowledge/social-science/social-psychology/zimbardo-stanford-prison-situation.md)** — SPE, Lucifer Effect, role internalization, deindividuation; Le Texier critique; maps to role-based cultural transmission
- **[group-polarization-groupthink.md](knowledge/social-science/social-psychology/group-polarization-groupthink.md)** — Group polarization (Moscovici, Sunstein), groupthink (Janis 8 symptoms); echo chambers; applied to AI communities
- **[bystander-effect-diffusion-responsibility.md](knowledge/social-science/social-psychology/bystander-effect-diffusion-responsibility.md)** — Latané-Darley; diffusion of responsibility; pluralistic ignorance; collective inaction parallel to Olson
- **[social-psychology-transmission-biases-synthesis.md](knowledge/social-science/social-psychology/social-psychology-transmission-biases-synthesis.md)** — Full mapping: Asch→conformist bias, Milgram→authority bias, Zimbardo→role transmission, polarization→echo chambers

#### `behavioral-economics/` — Heuristics, biases, prospect theory, nudge theory, bounded rationality (promoted 2026-03-21, trust: low — awaiting review)
- **[kahneman-tversky-heuristics-biases.md](knowledge/social-science/behavioral-economics/kahneman-tversky-heuristics-biases.md)** — Availability, representativeness, anchoring heuristics; dual-process framework; System 1/2; Gigerenzen debate
- **[prospect-theory-loss-aversion.md](knowledge/social-science/behavioral-economics/prospect-theory-loss-aversion.md)** — Reference dependence, S-shaped value function, loss aversion (λ≈2.25), probability weighting; endowment effect; status quo bias
- **[thaler-sunstein-nudge-theory.md](knowledge/social-science/behavioral-economics/thaler-sunstein-nudge-theory.md)** — Choice architecture: defaults, salience, social proof, framing; libertarian paternalism; mental accounting; debiasing via environment design
- **[bounded-rationality-simon.md](knowledge/social-science/behavioral-economics/bounded-rationality-simon.md)** — Herbert Simon's satisficing; aspiration levels; procedural vs substantive rationality; attention as scarce resource; AI design implications
- **[behavioral-economics-rationality-synthesis.md](knowledge/social-science/behavioral-economics/behavioral-economics-rationality-synthesis.md)** — Rationality landscape (EUT, K&T, Gigerenzen, Simon); domain specificity of biases; what debiasing works; connections to rationalist community and cultural evolution

#### `network-diffusion/` — Weak ties, diffusion of innovations, cascades, wisdom of crowds (promoted 2026-03-21, trust: low — awaiting review)
- **[granovetter-weak-ties-strength.md](knowledge/social-science/network-diffusion/granovetter-weak-ties-strength.md)** — Weak ties as bridges between clusters; structural holes (Burt); homophily and polarization; intellectual weak ties for cross-domain insight
- **[rogers-diffusion-of-innovations.md](knowledge/social-science/network-diffusion/rogers-diffusion-of-innovations.md)** — Innovation attributes (relative advantage, trialability, observability); adopter S-curve; opinion leaders; critical mass; the chasm
- **[watts-information-cascades.md](knowledge/social-science/network-diffusion/watts-information-cascades.md)** — Threshold models; cascade window; why influencers matter less than network structure; viral misinformation dynamics
- **[surowiecki-wisdom-of-crowds.md](knowledge/social-science/network-diffusion/surowiecki-wisdom-of-crowds.md)** — Four conditions for crowd wisdom (diversity, independence, decentralization, aggregation); prediction markets; when crowds are stupid (herding)
- **[network-diffusion-synthesis.md](knowledge/social-science/network-diffusion/network-diffusion-synthesis.md)** — Unified framework: diffusion-wisdom tension; echo chambers/groupthink/filter bubbles; LLMs as high-degree diffusion nodes; AI governance implications

---
