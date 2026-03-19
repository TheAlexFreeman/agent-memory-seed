# AI Paradigm Genealogy — Summary

Narrative history of how the current AI paradigm formed, written for causal understanding rather than encyclopedic completeness. Each file answers: what bottleneck existed, what insight addressed it, what enabling conditions made it practical, what remained hard, and what later work built on it.

Four through-lines tracked across all files:
1. **Representation learning** — from hand-engineered features to learned distributed representations
2. **Optimization and training** — perceptron learning → backprop → better activations/regularization → large-scale stochastic optimization → post-training
3. **Scale and infrastructure** — datasets, GPUs/TPUs, software stacks, benchmarks, economics of training
4. **Sequence modeling and interfaces** — recurrence → attention → pretraining → instruction following → tool use → reasoning-time compute

Trust level: **low** on all files until Alex reviews. This is inherently interpretive history; primary sources are cited but commentary is agent-synthesized.

## Files

### origins/
| File | Period | Core story |
|---|---|---|
| `cybernetics-perceptrons-and-the-first-connectionist-wave.md` | 1943–1969 | McCulloch-Pitts, Rosenblatt, the first learning optimism, and the limit of linear separability |
| `symbolic-ai-expert-systems-and-the-neural-winter.md` | 1956–1986 | The symbolic turn, expert systems, why neural approaches receded, and what symbolic AI solved and failed to solve |

### deep-learning/
*(files planned — not yet written)*

### language-models/
*(files planned — not yet written)*

### frontier/
*(files planned — not yet written)*

### synthesis/
*(files planned — not yet written)*

## Source spine

Rosenblatt (1958), Minsky and Papert (1969), Rumelhart/Hinton/Williams (1986), Hochreiter/Schmidhuber (1997), LeCun convnets, AlexNet (2012), word2vec (2013), seq2seq (2014), Bahdanau attention (2014), Vaswani et al. Transformer (2017), BERT (2018), GPT-3 (2020), Chinchilla (2022), InstructGPT (2022).
