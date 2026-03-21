created: 2026-03-19
last_verified: 2026-03-19
next_action: "Complete — all 12 items done. Human review of knowledge/_unverified/mathematics/information-theory/ files recommended."
origin_session: chats/2026/03/19
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Information Theory and Statistical Learning Theory

## Goals

Two files in the knowledge base — `compression-intelligence-ait.md` and `compression-and-intelligence.md` — gesture at Shannon information theory and Kolmogorov complexity but don't develop either rigorously. Statistical learning theory (PAC learning, VC dimension, double descent) provides the formal language for understanding *why* neural network scaling works — what the conditions are under which learned functions generalize beyond training data. This plan builds the mathematical infrastructure that underpins the compression-intelligence thesis and the scaling law discussion in the AI frontier files. It is notably more technical than most research plans in this system; the target audience is the synthesis files that connect technical AI to philosophical claims about compression, intelligence, and generalization.

Primary connections to existing files:
- `ai/frontier/epistemology/compression-and-intelligence.md` — needs Shannon, rate-distortion, MDL formalism
- `philosophy/compression-intelligence-ait.md` — needs Shannon as the information-theoretic foundation
- `ai/frontier/reasoning/test-time-compute-scaling.md` — scaling laws as empirical instances of PAC-learning-style trade-offs
- `ai/frontier/architectures/synthetic-data-self-improvement.md` — model collapse as a statistical learning phenomenon

---

## Problem statement

The compression thesis — that intelligence is compression efficiency — is invoked in multiple files but rests on informal analogies. Shannon's source coding theorem makes the relationship precise: the minimum average code length equals the entropy of the source. Rate-distortion theory extends this to lossy compression: the minimum distortion at a given rate. These theorems show exactly what a good compressor must do and what it must sacrifice. Statistical learning theory then addresses the generalization question: given a compression/model learned from finite samples, under what conditions does it generalize? This is the formal question behind "do scaling laws work" and "why does more data help."

---

## Scope decisions

**In scope:**
- Shannon information theory: entropy, mutual information, channel capacity, source/channel coding theorems
- Rate-distortion theory: the formal theory of lossy compression
- Minimum Description Length principle (Rissanen) as bridge between information theory and statistical inference
- PAC learning: sample complexity, VC dimension, fundamental theorem of statistical learning
- Double descent and modern generalization theory: interpolation threshold, the benign overfitting phenomenon
- Algorithmic information theory (brief consolidation): Kolmogorov complexity, Solomonoff, connection to Shannon

**Out of scope:**
- Network coding and distributed source coding — too specialized
- Full treatment of algebraic coding theory (error-correcting codes) — separate discipline
- Full Bayesian statistics — own plan if needed

---

## Phases

### Phase 1 — Shannon information theory

**1.1 Entropy and the Source Coding Theorem**
- Self-information: $-\log_2 p(x)$ bits to encode event $x$ with probability $p(x)$ — the surprise content
- Shannon entropy: $H(X) = -\sum_x p(x)\log_2 p(x)$ — expected self-information; average code length lower bound
- Source coding theorem: for i.i.d. source with entropy H, any lossless compression scheme requires at least H bits/symbol on average; can be achieved arbitrarily closely with long blocks (Huffman, arithmetic coding)
- Joint and conditional entropy; chain rule: $H(X,Y) = H(X) + H(Y|X)$
- Entropy as a measure of uncertainty: maximized by the uniform distribution; minimized (to 0) when an outcome is certain

**1.2 Mutual Information and Channel Capacity**
- Mutual information: $I(X;Y) = H(X) - H(X|Y)$ — how much learning Y reduces uncertainty about X
- Data processing inequality: processing can never increase mutual information; $I(X;Z) \leq I(X;Y)$ if $X \to Y \to Z$
- Channel capacity theorem: the maximum rate at which information can be transmitted reliably over a noisy channel equals $C = \max_{p(x)} I(X;Y)$
- Implications for LLMs: the information bottleneck view — intermediate representations compress the input while preserving information relevant to the output; mutual information between internal states and task labels

**1.3 Kullback-Leibler Divergence and Cross-Entropy**
- KL divergence: $D_{KL}(P \| Q) = \sum_x p(x) \log \frac{p(x)}{q(x)}$ — the "extra bits" needed to encode P-distributed data using Q-optimal code
- Cross-entropy: $H(P, Q) = H(P) + D_{KL}(P \| Q)$ — directly the language model training objective
- Why cross-entropy loss is information theory: minimizing cross-entropy between true distribution P and model distribution Q is minimizing the KL divergence from P to Q
- Empirical risk as cross-entropy: training on a dataset is minimizing the cross-entropy between the data distribution and the model's distribution — i.e., minimizing the compression cost of the data under the model

### Phase 2 — Rate-distortion theory

**2.1 Rate-Distortion Functions**
- The lossy compression problem: compress to R bits/symbol; accept average distortion D
- Rate-distortion function: the minimum rate R(D) needed to achieve average distortion D
- Gaussian source: $R(D) = \frac{1}{2}\log(\sigma^2/D)$ — the tradeoff between bits allowed and reconstruction error
- Shannon's rate-distortion theorem: for large blocks, R(D) is achievable; below it, distortion D is unavoidable
- Implication: LLMs operate at a particular point on the rate-distortion curve — their parameter count is the "rate" and their prediction error is the "distortion"

**2.2 Information Bottleneck and Deep Learning**
- Tishby & Schwartz-Ziv (2017): the information bottleneck framework applied to deep neural networks
- The bottleneck principle: an optimal intermediate representation should maximize I(Representation; Output) while minimizing I(Representation; Input)
- Observed dynamics: in training, networks initially fit the input (increasing mutual information with input), then compress representations (decreasing mutual information with input while maintaining task information)
- Controversy: subsequent work disputed the compression dynamics (artifact of binning); the framework remains influential even if the empirics are debated
- Connection to MDL: one interpretation of regularization (dropout, weight decay) is enforcing compression of representations

**2.3 MDL Principle (Rissanen)**
- Minimum Description Length: the best model for data minimizes the total code length (model code + data-given-model code)
- Two-part MDL: separately code the model, then the residuals
- Normalized Maximum Likelihood (NML): the optimal MDL code for a model class; corresponds to Bayesian model selection with a particular prior
- MDL as a clean unification: Occam's razor made precise — the simplest model that compresses the data best is preferred; not because we believe it is true, but because it demonstrably generalizes best to new data from the same source

### Phase 3 — Statistical learning theory

**3.1 PAC Learning**
- Probably Approximately Correct learning (Valiant, 1984): formalize when a concept class is efficiently learnable
- Sample complexity: how many examples are needed to learn a concept from a class C with error ≤ ε and confidence ≥ 1-δ?
- Consistent learners and the growth function
- Realizable vs. agnostic settings: when the true hypothesis is in the class vs. when it isn't
- Implication: PAC learning says a model trained on N examples can, with high probability, generalize to unseen examples at a stated error rate — under assumptions that may or may not apply to LLMs

**3.2 VC Dimension and the Fundamental Theorem**
- Vapnik-Chervonenkis dimension: the size of the largest set that a hypothesis class can shatter (classify in all possible ways)
- Shattering: a set S is shattered by class H if for every labeling of S, some h ∈ H achieves it
- Fundamental theorem: a class H is PAC-learnable iff its VC dimension is finite; sample complexity is O(VC(H)/ε²)
- VC dimension of neural networks: roughly proportional to the number of parameters; at billions of parameters, VC bounds are vacuous — they do not explain why LLMs generalize
- This is the puzzle double-descent was discovered to address

**3.3 Double Descent and Modern Generalization**
- Classical bias-variance tradeoff: as model complexity increases, generalization error decreases then increases (U-curve)
- The double descent phenomenon (Belkin et al. 2019; Nakkiran et al. 2020): after the classical optimal point, continuing to increase model size causes test error to *decrease again*, reaching a second asymptotic minimum
- The interpolation threshold: the point where the model has exactly enough parameters to fit the training data perfectly; test error peaks here then falls as further overparameterization enables benign overfitting
- Why VC theory fails to explain this: VC bounds apply to the worst case over all data distributions; LLM training data has strong inductive structure that enables benign overfitting
- Implicit regularization: gradient descent on overparameterized models finds minimum-norm solutions, which correspond to maximum-margin or minimum-complexity solutions

**3.4 Generalization via Inductive Bias**
- No Free Lunch theorem: no learning algorithm outperforms every other on every problem; there is no universally optimal learner
- Inductive bias: the assumptions a learning algorithm makes beyond the training data; what determines generalization
- Transformers' inductive bias: attention to relevant parts of context; position-independent representations; the specific biases introduced by layer norm, residual connections, etc.
- Why scaling works: at scale, the inductive bias of stochastic gradient descent + overparameterized transformers happens to match the inductive structure of natural language — neither is universal, but they meet
- The mystery: we don't have a clean theory predicting which biases match which data distributions

### Phase 4 — Synthesis and implications

**4.1 The Compression-Generalization Connection**
- MDL perspective on generalization: models that better compress training data generalize better, because compression requires extracting structure that is not sample-specific
- The double-descent reconciliation: at the interpolation threshold, the model memorizes without compressing; above it, the model over-parameterizes enough that gradient descent induces an implicit compression toward smooth, low-complexity solutions
- Why perplexity predicts task performance: held-out perplexity is the compression ratio on test data; better compression = better representation of underlying structure = better task performance

**4.2 Limits of the Theory and Open Questions**
- Can we bound LLM generalization? Current theory (PAC, VC) provides vacuously loose bounds for models with billions of parameters; tight new theory is an open research frontier
- Distribution shift: all generalization theory assumes test distribution ≈ training distribution; LLMs are routinely applied to shifted distributions; no theory covers this case well
- The empirical scaling law as an empirical fact without theoretical explanation: Chinchilla scaling laws are very well-confirmed empirically; why exactly this functional form holds is unknown

---

## Output format

Files go in `knowledge/_unverified/mathematics/information-theory/` with standard frontmatter. Phase 4 synthesis files may cross-post to `knowledge/_unverified/ai/frontier/` as appropriate.

---

## Progress tracking

### Phase 1 — Shannon information theory
- [x] 1.1 Entropy and source coding theorem
- [x] 1.2 Mutual information and channel capacity
- [x] 1.3 KL divergence and cross-entropy

### Phase 2 — Rate-distortion theory
- [x] 2.1 Rate-distortion functions and Shannon's theorem
- [x] 2.2 Information bottleneck and deep learning
- [x] 2.3 MDL principle (Rissanen)

### Phase 3 — Statistical learning theory
- [x] 3.1 PAC learning
- [x] 3.2 VC dimension and fundamental theorem
- [x] 3.3 Double descent and modern generalization
- [x] 3.4 Generalization via inductive bias

### Phase 4 — Synthesis
- [x] 4.1 Compression-generalization connection
- [x] 4.2 Limits and open questions

**Progress:** 12/12 items complete ✓

---

## Priority order

1. **Phase 1.1** (entropy and source coding) — foundational; immediately enriches the compression files
2. **Phase 3.3** (double descent) — the most important empirical phenomenon in modern ML theory
3. **Phase 1.3** (KL divergence / cross-entropy) — directly connects to training objectives
4. **Phase 2.3** (MDL principle) — the unification of compression and prediction
5. **Phase 3.2** (VC dimension) — needed to understand why classical theory fails at scale
