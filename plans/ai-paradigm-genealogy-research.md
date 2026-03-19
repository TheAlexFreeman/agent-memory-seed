---
source: agent-generated
type: research-plan
origin_session: chats/2026/03/18/chat-005
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Begin Phase 2 — write knowledge/_unverified/ai-history/origins/backpropagation-and-the-pdp-revival.md"
---

# Research Plan: Genealogy of the Current AI Paradigm

## Goals

Alex wants a narrative account of how the current AI paradigm formed: from early connectionism and perceptrons, through the backpropagation revival, through deep learning's scaling era, through transformers and into frontier LLM practice. The point is not to memorize model names. It is to understand how each major insight answered a concrete bottleneck left behind by the previous generation.

This plan therefore treats AI history as a sequence of technical problems and partial solutions: how to represent structure, how to train multi-layer systems, how to encode locality and memory, how to exploit more data and compute, how to handle long-range sequence dependencies, how to pretrain general-purpose models, and how to turn raw language models into useful aligned systems.

Across all files, keep four through-lines in view:

1. **Representation learning** — the shift from hand-engineered rules and features toward learned distributed representations.
2. **Optimization and training** — perceptron learning, backpropagation, better activations, regularization, large-scale stochastic optimization, and post-training.
3. **Scale and infrastructure** — datasets, GPUs/TPUs, software stacks, benchmarks, and the economics of training.
4. **Sequence modeling and interfaces** — recurrence, attention, pretraining, instruction following, tool use, multimodality, and reasoning-time computation.

---

## Output file structure: `knowledge/_unverified/ai-history/`

Use subfolders to preserve the chronology:

- `origins/` — perceptrons, symbolic detours, and the backprop revival
- `deep-learning/` — architectural and infrastructure advances that made depth practical
- `language-models/` — embeddings, seq2seq, attention, transformers, and scaling
- `frontier/` — post-training, tool use, multimodality, and recent reasoning-era systems
- `synthesis/` — the integrated story of how the current paradigm formed

Maintain a `SUMMARY.md` as files are written.

---

## Research phases and priority order

### Phase 1 — First-wave connectionism and its eclipse (highest priority) · ☑ 2/2 complete

Start with the prehistory of the modern neural paradigm: the first wave of optimism, the first hard limits, and the first major conceptual split.

1. ☑ `origins/cybernetics-perceptrons-and-the-first-connectionist-wave.md`
   - McCulloch and Pitts, Hebbian intuitions, Rosenblatt's perceptron, and early hopes for learning machines
   - What single-layer perceptrons could actually do, and why that already mattered
   - The importance of hardware imaginaries, neuroscience analogies, and early pattern-recognition ambitions

2. ☑ `origins/symbolic-ai-expert-systems-and-the-neural-winter.md`
   - Minsky and Papert's critique of perceptrons, the limits of linear separability, and why this mattered historically
   - The shift toward symbolic AI, search, expert systems, and hand-built knowledge representations
   - Why neural approaches receded without disappearing, and what problems symbolic systems solved better in that era

---

### Phase 2 — Learning internal representations again (highest priority) · ☐ 0/3 complete

This is the core conceptual hinge. The modern paradigm depends on the rediscovery that multi-layer systems can learn useful hidden representations if they can be trained effectively.

3. ☐ `origins/backpropagation-and-the-pdp-revival.md`
   - Rumelhart, Hinton, and Williams; parallel distributed processing; error propagation through hidden layers
   - Why backprop was more than an optimization trick: it made feature learning inside the model tractable
   - What remained hard even after backprop: vanishing gradients, data scarcity, compute limits, and brittle optimization

4. ☐ `deep-learning/convnets-rnns-and-lstm-inductive-biases.md`
   - Convolution as a solution to spatial locality and parameter sharing
   - Recurrent networks as a solution to sequential structure, and LSTM/GRU as partial fixes for long-term dependency problems
   - The larger lesson: architecture mattered because unconstrained learning was still too hard

5. ☐ `language-models/statistical-nlp-word-embeddings-and-seq2seq.md`
   - The statistical NLP era: n-grams, language modeling, distributed semantics, and the move away from symbolic pipelines
   - Word embeddings and what they changed about representation in language
   - Encoder-decoder and seq2seq models as the immediate prehistory of attention and modern language generation

---

### Phase 3 — Deep learning becomes dominant (high priority) · ☐ 0/2 complete

The field's center of gravity shifts when neural methods stop being interesting alternatives and start winning benchmarks decisively.

6. ☐ `deep-learning/gpus-imagenet-and-the-deep-learning-turn.md`
   - AlexNet, ReLUs, dropout, GPU training, large labeled datasets, and why 2012 was a true inflection point
   - How ImageNet changed institutional belief about scale, depth, and compute
   - The feedback loop among benchmarks, hardware, industrial labs, and research prestige

7. ☐ `language-models/attention-and-the-transformer-breakthrough.md`
   - Bahdanau-style attention as the immediate conceptual precursor
   - Why self-attention beat recurrence for long-range dependencies, parallelization, and scaling
   - Transformers as an architectural simplification that unexpectedly opened the path to foundation models

---

### Phase 4 — Foundation models and the LLM turn (high priority) · ☐ 0/2 complete

The transformer becomes a general-purpose substrate once pretraining and scale start to dominate task-specific design.

8. ☐ `language-models/bert-gpt-and-the-scaling-laws-era.md`
   - BERT and GPT as two different uses of transformer pretraining
   - In-context learning, few-shot behavior, scaling laws, Chinchilla-style compute optimality, and the growing centrality of unsupervised pretraining
   - Why the field increasingly treated "just scale it" as a serious research strategy

9. ☐ `frontier/instruction-tuning-rlhf-and-the-chat-model-turn.md`
   - Instruction tuning and InstructGPT as the bridge from raw pretrained models to usable assistants
   - RLHF / RLAIF, safety fine-tuning, preference modeling, and why post-training became its own layer of the stack
   - The shift from benchmark model to product-facing conversational model

---

### Phase 5 — Frontier LLM systems (high priority, fast-moving) · ☐ 0/2 complete

This phase covers the current frontier as a system, not just a base model: multimodal inputs, retrieval, tools, routing, and reasoning-time strategies.

10. ☐ `frontier/multimodality-tool-use-and-reasoning-time-compute.md`
   - Multimodal models, retrieval augmentation, tool use, code execution, and agent-style scaffolding
   - Mixture-of-experts, efficiency techniques, open-weight vs. closed-weight ecosystems, and deployment tradeoffs
   - Chain-of-thought, deliberate inference, and recent reinforcement-learning-heavy reasoning systems

11. ☐ `synthesis/how-the-current-ai-paradigm-formed.md`
   - Reconstruct the full story from perceptrons to frontier LLMs as a chain of bottlenecks and unlocks
   - Make explicit what each transition added: hidden-layer learning, architecture-specific inductive bias, scale, attention, pretraining, post-training, tool use
   - Track the themes that persist across the whole genealogy: representation, optimization, data/compute co-evolution, and the return of old questions inside new neural systems

---

## Research approach and practical notes

- Each file: ~2500-4000 words. Write for causal understanding, not encyclopedic completeness.
- For every file, answer the same five questions: what bottleneck existed, what insight addressed it, what enabling conditions made it practical, what new bottlenecks remained, and what later work built on it.
- Use primary sources aggressively: Rosenblatt (1958), Minsky and Papert (1969), Rumelhart/Hinton/Williams (1986), Hochreiter/Schmidhuber (1997), LeCun's convnet work, AlexNet (2012), word2vec (2013), seq2seq (2014), Bahdanau attention (2014), Transformer (2017), BERT (2018), GPT-3 (2020), Chinchilla (2022), and InstructGPT (2022) should form the core spine.
- Avoid Whig history. Include winters, dead ends, and rival paradigms such as symbolic AI and statistical machine learning where they genuinely shaped the path.
- Be explicit about infrastructure. Many "algorithmic" breakthroughs only mattered because of compute, datasets, libraries, and industrial-scale training pipelines.
- Frontier sections should be re-checked against current technical reports when written, because this part of the story is moving quickly.
- Mark all produced knowledge files `trust: low` until Alex reviews them.

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created for a narrative genealogy of the current AI paradigm |
| 2026-03-18 | Phase 1 complete — wrote SUMMARY.md, cybernetics-perceptrons-and-the-first-connectionist-wave.md, symbolic-ai-expert-systems-and-the-neural-winter.md |

Last updated: 2026-03-18
