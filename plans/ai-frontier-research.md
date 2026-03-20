---
created: 2026-03-19
last_verified: 2026-03-20
next_action: "All 7 phases + Phases 2 and 3 extensions complete (25/25 + 9 total). Phase 3 extension (5 files): ColPali, late chunking, agentic RAG patterns, HyDE, reranking. No further active items. Archive or extend as needed."
origin_session: chats/2026/03/19/chat-002
source: agent-generated
status: active
trust: medium
type: research-plan
category: research
---

# Research Plan: Frontier AI Topics

## Goals

Build a knowledge base on the most intellectually interesting and practically relevant topics in contemporary AI — going beyond survey-level familiarity into the mechanisms, tradeoffs, and open questions. Complements the existing AI paradigm genealogy (`knowledge/_unverified/ai-history/`) which covers historical formation; this plan focuses on the active frontier.

Topics are selected for their combination of:
- Conceptual depth (not just "what it does" but "why it works and where it breaks")
- Practical relevance to agent design, tool use, and memory systems
- Connection to Alex's philosophical interests (dynamical systems, compression, cognition)
- Unsettled questions worth tracking

---

## Problem statement

The AI tools landscape file (`ai-tools-landscape-2026.md`) covers the product surface. The AI history files cover how the current paradigm formed. What's missing is a layer in between: the **technical concepts and ideas** that explain the current frontier — why reasoning models work, how alignment actually functions, what makes retrieval difficult at scale, what multi-agent coordination looks like in practice, and where the next architectural transitions might come from.

Without this layer, discussions about AI remain at the level of product comparisons rather than principled analysis.

---

## Scope decisions

**In scope:**
- Reasoning-time compute and reasoning models
- Alignment, RLHF, and post-training methods
- Retrieval, memory, and long-context architecture
- Multi-agent systems and coordination
- Interpretability and mechanistic understanding
- Emerging architectures and training paradigms
- AI epistemology — what LLMs know, believe, and confabulate

**Out of scope (covered elsewhere or too deep for now):**
- Historical AI paradigm formation → see `ai-history/` plan
- MCP protocol specifics → see `mcp/` files
- Django/React/DevOps tooling → see those plans

---

## Phases

### Phase 1 — Reasoning and test-time compute

The shift from "bigger pretraining" to "longer thinking at inference time" is the most significant recent architectural move, and the mechanism is still poorly understood publicly.

**1.1 Reasoning models: o1, o3, DeepSeek R1**
- How chain-of-thought (CoT) emerged as a capability at scale (Wei et al. 2022)
- Internal scratch-pad reasoning vs. hidden chain-of-thought
- Process reward models (PRMs) vs. outcome reward models (ORMs) — the key distinction
- MCTS / beam search at test time vs. learned reasoning
- DeepSeek R1: open weights, distillation from reasoning traces, GRPO training — the replication story
- Extended thinking (Claude 3.7): how it differs architecturally from o1-style reasoning
- When reasoning helps: structured planning, math, multi-step deduction — and when it doesn't (pattern recognition, factual recall)
- The computational cost profile: reasoning tokens × depth × batch size

**1.2 Scaling laws for test-time compute**
- Snell et al. (2024) "Scaling LLM Test-Time Compute Optimally" — the core paper
- The inference-time scaling curve: does it replicate the pretraining scaling curve? Where does it saturate?
- Trade-off: large model + short chain vs. small model + long chain
- Best-of-N sampling, majority voting, and ranking approaches as baselines
- Connection to the dynamical systems frame: reasoning as extended trajectory in activation space

**1.3 Benchmarking reasoning: what the benchmarks actually measure**
- MATH, AMC/AIME, HumanEval, SWE-bench, GPQA, ARC-AGI
- Contamination and benchmark saturation — how quickly benchmarks are "solved"
- ARC-AGI as the hard outlier: why novel generalization remains rare
- The frontier/benchmark gap: what gets measured vs. what matters in deployment

---

### Phase 2 — Alignment and post-training

**2.1 RLHF, RLAIF, and the reward model problem**
- From supervised fine-tuning (SFT) → reward modeling → PPO pipeline (InstructGPT)
- The Goodhart's law problem: reward models as imperfect proxies — what the model optimizes vs. what we want
- Constitutional AI (Anthropic): AI-generated feedback, the RLAIF variant
- Reward model collapse / hacking: what it looks like in practice and mitigations
- Direct Preference Optimization (DPO): why it's simpler than PPO and what it trades away
- Group Relative Policy Optimization (GRPO): the DeepSeek insight — no reference model needed

**2.2 Instruction following and the instruction hierarchy**
- How models learn to follow system prompts, user turns, and tool results differently
- The "instruction hierarchy" (OpenAI 2024): trust levels for different prompt positions
- Prompt injection as an attack surface: how it exploits instruction hierarchy confusion
- Refusals, over-refusals, and the alignment tax: what capabilities alignment costs
- System prompt confidentiality and information leakage

**2.3 Frontier alignment research**
- Constitutional AI and Claude's approach to values
- Scalable oversight: using AI to supervise AI at capabilities above human competence
- Debate as an alignment approach (Irving et al.)
- Superalignment (OpenAI, now dormant): the theory and its practical challenges
- Interpretability as a prerequisite for alignment (Anthropic's view)
- What "alignment" means at different capability levels — a conceptual map

---

### Phase 3 — Retrieval, memory, and long-context

**3.1 RAG architecture and when it works**
- Dense retrieval: bi-encoder (FAISS, pgvector) vs. cross-encoder (reranker) vs. sparse (BM25)
- Chunking strategy: fixed-size vs. sentence vs. semantic; overlap; parent-document retrieval
- The embedding quality problem: what makes a good retrieval embedding, what makes a bad one
- Hypothetical Document Embeddings (HyDE): query expansion for retrieval
- Re-ranking: why two-stage retrieval (retrieve many, rerank few) dramatically outperforms single-stage
- RAG vs. long-context: when to retrieve vs. when to just put it all in context
- The "lost in the middle" problem: performance degradation for context in the middle of a long window
- Agentic RAG: query decomposition, multi-step retrieval, iterative refinement

**3.2 Long-context architecture**
- Flash Attention: IO-aware algorithm that made long-context practical
- RoPE positional encoding and extrapolation (YaRN, LongRoPE)
- Context window vs. effective context window: the distinction that matters
- Sparse attention patterns: Longformer, BigBird, Mamba-style SSMs as alternatives
- The memory-compute tradeoff: KV cache size, quantization, batching constraints
- What 1M+ token context (Gemini 2.0) actually enables vs. what it doesn't

**3.3 Persistent memory architectures**
- Knowledge graph memory (MemGPT / OpenAI Memory server style)
- Episodic vs. semantic vs. procedural memory — cognitive science frame applied to AI systems
- Vector store as external memory: strengths (scale, similarity) and weaknesses (no structure, no update)
- The write problem: how do you update a memory store? Vector deletion/replacement, CRUD operations on graph memory, git-backed structured memory (this repo)
- Memory extraction from conversations: entity recognition, summarization, contradiction detection
- Forgetting as a feature: why temporal decay and archiving are necessary (curation policy frame)

---

### Phase 4 — Multi-agent systems

**4.1 Agent architecture patterns**
- ReAct (Reasoning + Acting): the interleaved thought/action loop
- Plan-and-execute: upfront plan followed by execution — when it beats ReAct
- Reflection and self-critique agents (Reflexion): generating feedback on own outputs
- Orchestrator/subagent patterns: routing, specialization, result aggregation
- "Building Effective Agents" (Anthropic 2024): the canonical taxonomy of patterns (augmented LLM, prompt chaining, routing, parallelization, orchestrator-subagents, evaluator-optimizer, autonomous agents)
- Swarm architectures: decentralized multi-agent without a fixed orchestrator

**4.2 Multi-agent coordination challenges**
- Context sharing: what do agents know about each other's state?
- Tool conflict and resource locking: two agents modifying the same file
- Trust hierarchies between agents: which agent can tell which agent what to do?
- Prompt injection in multi-agent contexts: an attacker controls a tool response seen by an orchestrator
- Evaluating multi-agent systems: harder than single-agent evals — partial credit, correct-outcome-wrong-path
- The communication overhead problem: agents spending most tokens coordinating rather than doing

**4.3 Human-in-the-loop design**
- When to interrupt and ask vs. when to proceed autonomously
- Approval gate design: what information does a human need to make a good approval decision?
- Reversibility scoring: categorizing actions by recoverability before execution
- Elicitation (MCP primitive): the formal spec mechanism for server-initiated user queries
- Building trust incrementally: agent track record, confidence signals, action logs

---

### Phase 5 — Interpretability and mechanistic understanding

**5.1 Mechanistic interpretability**
- The superposition hypothesis: features as linear combinations of neurons, not individual neurons
- Sparse Autoencoders (SAEs): decomposing superposition to find monosemantic features
- Anthropic's scaling monosemanticity work (2024): features from 1M to 34M parameters
- Circuit analysis: tracing information flow for specific capabilities (indirect object identification, induction heads)
- Dictionary learning as the current leading method: how it works, what it finds
- What's been found: memory features, emotional valence, reasoning tokens

**5.2 What LLMs represent and confabulate**
- World models vs. lookup tables: the debate
- Factual recall vs. reasoning: different failure modes
- Hallucination taxonomy: fabrication, mis-attribution, temporal confusion, confident-wrong-answer
- Calibration: do model confidence scores correlate with accuracy? How to measure
- The "I don't know" problem: why models default to generating plausible-sounding content over admitting uncertainty
- Probing classifiers: how to test whether a model "knows" X vs. just outputs text that looks like X

**5.3 Emergence and phase transitions**
- The emergence debate: sharp capability jumps vs. artifacts of measurement (Schaeffer et al. 2023)
- What actually appears to emerge: in-context learning, chain-of-thought, arithmetic at scale
- Grokking: the delayed generalization phenomenon — training long past memorization to true generalization
- The "bitter lesson" (Sutton): why scale + simple objectives keeps outperforming engineering knowledge
- What a "capability" is: prompt-specific, task-general, or architecture-dependent?

---

### Phase 6 — Emerging architectures and training paradigms

**6.1 State space models (Mamba, S4)**
- The recurrence vs. attention trade-off: O(n) vs. O(n²) in sequence length
- How SSMs achieve parallel training (convolution perspective) while maintaining recurrent inference
- Selective state spaces (Mamba): context-dependent recurrence vs. fixed dynamics
- Hybrid architectures: Mamba-Transformer interleaving (Jamba, Zamba)
- Where SSMs beat Transformers: very long sequences, limited memory; where they lose: retrieval-heavy tasks

**6.2 Mixture of experts (MoE)**
- Sparse MoE: routing inputs to k-of-N experts, only k are active per token
- Training challenges: expert collapse, load balancing, expert routing instability
- DeepSeek MoE architecture: fine-grained experts + shared experts + auxiliary-loss-free balancing
- Inference implications: larger model, fewer FLOPs-per-token — the economic case
- Expert specialization: do experts develop semantic specialities? What the research shows

**6.3 Synthetic data and self-improvement**
- Why synthetic data is now mainstream: post-Chinchilla, real data is the bottleneck
- Distillation at scale: smaller models learning from reasoning traces of larger models (DeepSeek R1 approach)
- Self-play and self-improvement: AlphaGo → AlphaCode → OpenAI o1 reasoning
- Data quality over quantity: filtering synthetic data, constitutional filters
- The collapse problem (Shumailov et al. 2024): models trained on model-generated data degrade — mechanisms and mitigations
- Speculation: can AI systems generate genuinely novel training signal, or are they limited to recombination?

---

### Phase 7 — AI epistemology (connection to philosophical interests)

This phase connects directly to the philosophical framework from `knowledge/_unverified/philosophy/` — the dynamical systems, compression, and narrative cognition threads.

**7.1 What it means for a model to "know" something**
- Knowledge as dispositional: not a stored fact but a pattern of behavior
- The Chinese Room argument and its modern reformulation (does GPT-4 understand Chinese?)
- Stochastic parrots vs. world models: Bender et al. vs. the empirical case for internal structure
- Distributional semantics: meaning as co-occurrence patterns, and what that can and can't encode
- Ground truth and grounding: why language-only training may have fundamental limits (embodiment argument)

**7.2 LLMs as dynamical systems**
- Building on `synthesis-intelligence-as-dynamical-regime.md`: LLMs as fixed-weight dynamical systems
- Activation trajectories during inference: early layers as feature extraction, middle layers as processing, late layers as output formation
- In-context learning as transient dynamics: the context as an initial condition that shapes the trajectory
- Reasoning as extended trajectory: why chain-of-thought literally gives the activations longer to integrate
- Attractors in transformer residual stream: can we identify stable attractor states?

**7.3 Compression, intelligence, and what LLMs compress**
- Building on `compression-intelligence-ait.md`: LLMs as learned compression functions
- What the loss is actually minimizing: next-token prediction as MDL compression of the training corpus
- The relationship between compression quality and task performance (the core empirical claim)
- What cannot be compressed: truly novel patterns, embodied knowledge, counterfactuals not in training
- Hypothetical: if you could perfectly decompress an LLM, what would you see?

---

## Output format

Each research item produces one knowledge file in `knowledge/_unverified/ai-frontier/` with:
- Frontmatter: `source: external-research`, `trust: low`, `created`, `origin_session`, `topic`
- Summary lede: one paragraph situating the topic in the four through-lines from the AI history plan
- Technical depth: mechanisms, not just descriptions
- Open questions section: what is genuinely unsettled
- Key sources: papers, posts, or talks cited (not retrieved — listed for follow-up)

Group files by phase subfolder:
```
knowledge/_unverified/ai-frontier/
  reasoning/
  alignment/
  retrieval-memory/
  multi-agent/
  interpretability/
  architectures/
  epistemology/
```

---

## Progress tracking

### Phase 1 — Reasoning and test-time compute
- [x] 1.1 Reasoning models (o1/o3/R1/extended thinking)
- [x] 1.2 Scaling laws for test-time compute
- [x] 1.3 Benchmarking reasoning

### Phase 2 — Alignment and post-training
- [x] 2.1 RLHF, RLAIF, reward model problem
- [x] 2.2 Instruction following and hierarchies
- [x] 2.3 Frontier alignment research

### Phase 3 — Retrieval, memory, and long-context
- [x] 3.1 RAG architecture
- [x] 3.2 Long-context architecture
- [x] 3.3 Persistent memory architectures

### Phase 4 — Multi-agent systems
- [x] 4.1 Agent architecture patterns
- [x] 4.2 Multi-agent coordination challenges
- [x] 4.3 Human-in-the-loop design

### Phase 5 — Interpretability
- [x] 5.1 Mechanistic interpretability
- [x] 5.2 What LLMs represent and confabulate
- [x] 5.3 Emergence and phase transitions

### Phase 6 — Emerging architectures
- [x] 6.1 State space models (Mamba)
- [x] 6.2 Mixture of experts
- [x] 6.3 Synthetic data and self-improvement

### Phase 7 — AI epistemology
- [x] 7.1 What it means for a model to "know" something
- [x] 7.2 LLMs as dynamical systems (connecting to philosophy files)
- [x] 7.3 Compression, intelligence, and what LLMs compress (connecting to AIT file)

**Progress:** 21/21 items complete

### Phase 2 extension — Infrastructure and governance (2026-03-20)
- [x] Agentic frameworks (LangGraph, CrewAI, AutoGen, OpenAI SDK, LlamaIndex)
- [x] Foundation model governance (EU AI Act, NIST, compute governance, Conditioner problem)
- [x] Inference-time compute infrastructure (vLLM/PagedAttention, speculative decoding, quantization)
- [x] AI hardware and efficiency trends (H100/B200/TPUs/custom silicon, MoE, power constraints)

**Extension progress:** 4/4 items complete

### Phase 3 extension — RAG depth and retrieval advanced techniques (2026-03-20)
- [x] ColPali — visual document retrieval with vision-language models, bypassing OCR (`retrieval-memory/colpali-visual-document-retrieval.md`)
- [x] Late chunking and contextual embeddings — JinaAI technique; full-document encoding then boundary pooling (`retrieval-memory/late-chunking-contextual-embeddings.md`)
- [x] Agentic RAG patterns — query decomposition, FLARE, CRAG, SELF-RAG, RAGAS evaluation (`retrieval-memory/agentic-rag-patterns.md`)
- [x] HyDE query expansion — hypothetical document embeddings, query-document asymmetry (`retrieval-memory/hyde-query-expansion.md`)
- [x] Reranking and two-stage retrieval — cross-encoder rerankers, cascade architecture, position bias (`retrieval-memory/reranking-two-stage-retrieval.md`)

**Extension progress:** 5/5 items complete

---

## Priority order

When time is limited, prioritize in this order:

1. **Phase 2.1** (RLHF/reward models) — most directly relevant to understanding AI behavior and alignment failure modes
2. **Phase 1.1** (Reasoning models) — most topical; the current dominant conversation
3. **Phase 5.1** (Mechanistic interpretability) — most likely to change what we know in the next 12 months
4. **Phase 3.1** (RAG) — most directly applicable to the agent memory system in this repo
5. **Phase 7.2** (LLMs as dynamical systems) — deepens the philosophical synthesis already started

---

## Design constraints

- Each file covers one topic at enough depth to resolve the "why" behind observed behaviors, not just catalog the "what."
- All files source: external-research, trust: low until Alex reviews.
- Phase 7 files should explicitly cross-reference the philosophy files from `knowledge/_unverified/philosophy/` to build coherent cross-domain synthesis.
- Files in Phase 3 (retrieval/memory) should note implications for this repo's design decisions where relevant.
