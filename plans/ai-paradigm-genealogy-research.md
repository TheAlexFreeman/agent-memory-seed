---
source: agent-generated
type: research-plan
origin_session: chats/2026/03/18/chat-005
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: complete
next_action: "Review all 11 files and promote to knowledge/ once verified"
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

- `origins/` — perceptrons, symbolic detours, and the backprop revival
- `deep-learning/` — architectural and infrastructure advances that made depth practical
- `language-models/` — embeddings, seq2seq, attention, transformers, and scaling
- `frontier/` — post-training, tool use, multimodality, and recent reasoning-era systems
- `synthesis/` — the integrated story of how the current paradigm formed

---

## All phases complete — 11/11 files written

### Phase 1 · ☑ 2/2
1. ☑ `origins/cybernetics-perceptrons-and-the-first-connectionist-wave.md`
2. ☑ `origins/symbolic-ai-expert-systems-and-the-neural-winter.md`

### Phase 2 · ☑ 3/3
3. ☑ `origins/backpropagation-and-the-pdp-revival.md`
4. ☑ `deep-learning/convnets-rnns-and-lstm-inductive-biases.md`
5. ☑ `language-models/statistical-nlp-word-embeddings-and-seq2seq.md`

### Phase 3 · ☑ 2/2
6. ☑ `deep-learning/gpus-imagenet-and-the-deep-learning-turn.md`
7. ☑ `language-models/attention-and-the-transformer-breakthrough.md`

### Phase 4 · ☑ 2/2
8. ☑ `language-models/bert-gpt-and-the-scaling-laws-era.md`
9. ☑ `frontier/instruction-tuning-rlhf-and-the-chat-model-turn.md`

### Phase 5 · ☑ 2/2
10. ☑ `frontier/multimodality-tool-use-and-reasoning-time-compute.md`
11. ☑ `synthesis/how-the-current-ai-paradigm-formed.md`

---

## Research approach and practical notes

- Mark all produced knowledge files `trust: low` until Alex reviews them.
- Frontier sections (o1, DeepSeek-R1, GPT-4V) should be re-checked against current technical reports.
- The synthesis file explicitly flags that errors in component files propagate; review component files first.

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created |
| 2026-03-18 | Phase 1 complete — SUMMARY.md, cybernetics-perceptrons, symbolic-ai-expert-systems |
| 2026-03-18 | Phase 2 complete — backpropagation-pdp-revival, convnets-rnns-lstm, statistical-nlp-word-embeddings-seq2seq |
| 2026-03-18 | Phase 3 complete — gpus-imagenet-deep-learning-turn, attention-transformer-breakthrough |
| 2026-03-18 | Phase 4 complete — bert-gpt-scaling-laws-era, instruction-tuning-rlhf-chat-model-turn |
| 2026-03-18 | Phase 5 complete — multimodality-tool-use-reasoning-time-compute, how-the-current-ai-paradigm-formed |
| 2026-03-18 | All 11 files written; plan marked complete; awaiting Alex review |

Last updated: 2026-03-18
