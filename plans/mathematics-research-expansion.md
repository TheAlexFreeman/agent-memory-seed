---
created: '2026-03-20'
last_verified: '2026-03-20'
next_action: 'Execute Phase 6 (Optimization Theory): Underpins ML and game-theory;
  convex analysis, duality, gradient descent, non-convex landscapes, online learning.'
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: active
title: Mathematics Knowledge Base Expansion
trust: medium
type: research-plan
---


## Goals

Expand the mathematics knowledge base from 35 verified files across 3 subfolders into a richer, more connected corpus that:

1. Fills the most glaring gap: **dynamical systems** — Alex's stated primary framework for thinking about intelligence ("self-organized criticality, Kauffman NK models, Langton's edge-of-chaos") has zero files in the knowledge base.
2. Grounds existing knowledge: **probability theory** is the foundation beneath information theory, PAC learning, MDL, and the Free Energy Principle — all already in the knowledge base — but has no dedicated files.
3. Bridges domains Alex cares deeply about: **statistical mechanics** connects FEP, dynamical systems, energy-based AI, and information theory. **Causal inference** connects AI interpretability, decision theory, and mechanism design. **Computational complexity** continues from Turing undecidability (already present) to the deeper structure of what's computable at what cost.
4. Adds optimization as a practical mathematical foundation for understanding how learning algorithms actually work.

### Relevance mapping to existing knowledge
| New cluster | Connects to (existing) |
|-------------|------------------------|
| Dynamical systems | FEP/autopoiesis (philosophy), intelligence-as-dynamical-regime, cognitive synthesis |
| Probability theory | Information theory (entropy, MDL), PAC learning, VC dimension, Bayesian inference |
| Statistical mechanics | FEP (Friston), energy-based models (philosophy/AI), Boltzmann, IIT |
| Causal inference | Mechanism design, game theory, AI interpretability, ethics/responsibility |
| Computational complexity | Turing undecidability, Gödel (logic-foundations), cryptography |
| Optimization theory | Game theory (Nash, minimax), PAC/learning theory, ML understanding |

---

## Gap Analysis

### What is present (35 files)

**`knowledge/mathematics/logic-foundations/`** (11 files):
Gödel's incompleteness theorems, ZFC set theory, propositional/first-order logic, Turing undecidability, Kolmogorov complexity, category theory, Curry-Howard isomorphism, dependent types/proof assistants, simple type theory/lambda calculus, compactness/Löwenheim-Skolem.

**`knowledge/mathematics/game-theory/`** (12 files):
Normal-form games/Nash, Arrow's impossibility, mechanism design/revelation principle, matching markets, VCG mechanisms, voting rules/Gibbard-Satterthwaite, evolutionary game theory, evolution of cooperation, cheap talk, extensive-form games, prisoner's dilemma, costly signaling.

**`knowledge/mathematics/information-theory/`** (12 files):
Shannon entropy/source coding, KL divergence/cross-entropy, mutual information/channel capacity, MDL, PAC learning, VC dimension, rate-distortion theory, compression-generalization, information bottleneck, inductive bias/no-free-lunch, double descent/benign overfitting, limits/open questions.

### What is absent (the research program)

**Gap A — Dynamical Systems (Critical):** Zero files. Alex explicitly names dynamical systems as a primary intellectual lens for intelligence. Self-organized criticality, bifurcation theory, strange attractors, and ergodic theory underlie his reading of Kauffman, Langton, Friston, and Maturana.

**Gap B — Probability Theory (Critical):** Zero files on measure-theoretic probability, Bayesian inference, stochastic processes, or Markov chains. These are the mathematical substructure beneath information theory (already present) and the FEP (referenced throughout philosophy files).

**Gap C — Statistical Mechanics (High):** Zero files. Statistical mechanics is the conceptual bridge between thermodynamics, information theory (Boltzmann entropy = Shannon entropy), the Free Energy Principle, and energy-based ML models. Spin glasses and the replica method are the mathematical language of learning theory at the frontier.

**Gap D — Causal Inference (High):** Zero files. Judea Pearl's causal hierarchy (association → intervention → counterfactual) is increasingly central to AI interpretability, fairness, and the theoretical foundations of agency — all areas Alex engages.

**Gap E — Computational Complexity (Medium):** Turing undecidability exists, but there are no files on P vs NP, NP-completeness, circuit complexity, or interactive proofs. The complexity landscape determines which problems can be efficiently solved — essential for understanding what algorithms can and cannot do.

**Gap F — Optimization Theory (Medium):** Zero files. Gradient descent, convex duality, minimax theorems, and regret bounds are the mathematical tools underlying both ML and game theory (which is already present).

---

## Phases

### Phase 1 — Dynamical Systems, Chaos & Self-Organization

*Addresses Gap A. Highest priority: these are Alex's stated primary intellectual tools.*

Target subfolder: `knowledge/mathematics/dynamical-systems/`

**Files to research and write:**

1. **`dynamical-systems-fundamentals.md`** — Phase space, vector fields, fixed points, limit cycles, flows. The vocabulary of ODEs as dynamical systems. Poincaré, Lyapunov stability. Why this language matters for modeling any evolving system.

2. **`bifurcation-theory-catastrophe.md`** — Bifurcations (saddle-node, Hopf, period-doubling), catastrophe theory (Thom), phase transitions. How qualitative system behavior changes at critical parameter values. Connects to phase transitions in learning (double descent file, already present).

3. **`chaos-lorenz-strange-attractors.md`** — Sensitive dependence on initial conditions (Lorenz 1963), strange attractors, Lyapunov exponents, the butterfly effect precisely formulated. What chaos is and isn't. Connection to compressibility and Kolmogorov complexity.

4. **`self-organized-criticality.md`** — Bak, Tang, and Wiesenfeld (1987): the sandpile model, power laws, 1/f noise, the argument that complex systems naturally evolve to criticality. Langton's edge-of-chaos thesis. Kauffman's NK model and adaptive fitness landscapes. Direct bearing on the intelligence-as-edge-of-chaos thesis.

5. **`ergodic-theory-mixing.md`** — Ergodicity, time averages vs ensemble averages, mixing, the Birkhoff ergodic theorem. Why statistical mechanics works. Relevance to the ergodicity problem in economics (Peters/Gell-Mann) and the FEP.

6. **`complex-networks-small-world-scale-free.md`** — Erdős-Rényi random graphs, Watts-Strogatz small-world model, Barabási-Albert preferential attachment and scale-free networks, degree distributions, clustering coefficients. Networks as the substrate of evolutionary and social dynamics already in the knowledge base.

7. **`fractals-dimension-multiscale.md`** — Fractal dimension (Hausdorff), self-similarity, iterated function systems, multiscale structure in nature and data. How fractals relate to strange attractors and self-organized criticality.

Checklist:
- ☑ Write `dynamical-systems-fundamentals.md` (2026-03-21)
- ☑ Write `bifurcation-theory-catastrophe.md` (2026-03-21)
- ☑ Write `chaos-lorenz-strange-attractors.md` (2026-03-21)
- ☑ Write `self-organized-criticality.md` (2026-03-21)
- ☑ Write `ergodic-theory-mixing.md` (2026-03-21)
- ☑ Write `complex-networks-small-world-scale-free.md` (2026-03-21)
- ☑ Write `fractals-dimension-multiscale.md` (2026-03-21)
- ☑ Promote all 7 files to `knowledge/mathematics/dynamical-systems/` (2026-03-21, written directly with trust: medium)
- ☑ Update `knowledge/SUMMARY.md` with `<!-- section: mathematics -->` entry for dynamical-systems (2026-03-21)

---

### Phase 2 — Probability Theory & Stochastic Processes

*Addresses Gap B. Foundational substructure for info-theory, PAC/VC, Bayesian inference, and FEP.*

Target subfolder: `knowledge/mathematics/probability/`

**Files to research and write:**

1. **`measure-theoretic-foundations.md`** — Kolmogorov axioms, σ-algebras, probability spaces, random variables as measurable functions, expectation as Lebesgue integral. Why measure theory is needed and what it resolves. Borel-Cantelli, dominated convergence.

2. **`bayesian-inference-priors-posteriors.md`** — Bayes' theorem as a learning rule, prior construction, conjugate priors, Bernstein-von Mises (Bayesian asymptotics). The philosophical debate: objective vs subjective Bayesianism. De Finetti's exchangeability theorem and the justification of priors.

3. **`concentration-inequalities.md`** — Markov, Chebyshev, Chernoff bounds, Hoeffding's inequality, McDiarmid's bounded differences inequality, the Azuma-Hoeffding martingale inequality. These are the workhorses of PAC learning proofs (connects directly to VC dimension file).

4. **`markov-chains-mixing-times.md`** — Markov chains, transition matrices, stationary distributions, detailed balance, MCMC (Metropolis-Hastings, Gibbs sampling), mixing times and spectral gaps. Connects to ergodic theory (Phase 1) and statistical mechanics (Phase 3).

5. **`gaussian-processes-bayesian-nonparametrics.md`** — Gaussian processes as distributions over functions, kernels, posterior updates, connections to RKHS and regularization. Dirichlet processes and Chinese restaurant process. How Bayesian nonparametrics resolves model selection without grid search.

6. **`martingales-optional-stopping.md`** — Conditional expectation, filtrations, martingales and submartingales, optional stopping theorem (Doob), martingale convergence theorem. Relevance to online learning, gambling/Kelly criterion, and the foundations of stochastic integration.

7. **`stochastic-processes-brownian-sde.md`** — Brownian motion, the Wiener process, stochastic differential equations (Itô calculus), the Fokker-Planck equation. Bridge to the FEP (Friston's equations are SDEs) and to diffusion models in generative AI.

Checklist:
- ☑ Write `measure-theoretic-foundations.md` (2026-03-21)
- ☑ Write `bayesian-inference-priors-posteriors.md` (2026-03-21)
- ☑ Write `concentration-inequalities.md` (2026-03-21)
- ☑ Write `markov-chains-mixing-times.md` (2026-03-21)
- ☑ Write `gaussian-processes-bayesian-nonparametrics.md` (2026-03-21)
- ☑ Write `martingales-optional-stopping.md` (2026-03-21)
- ☑ Write `stochastic-processes-brownian-sde.md` (2026-03-21)
- ☑ Promote all 7 files to `knowledge/mathematics/probability/` (2026-03-21, written directly with trust: medium)
- ☑ Update `knowledge/SUMMARY.md` entry (2026-03-21)

---

### Phase 3 — Statistical Mechanics & Energy-Based Systems

*Addresses Gap C. Bridges FEP, information theory, and ML at a deep mathematical level.*

Target subfolder: `knowledge/mathematics/statistical-mechanics/`

**Files to research and write:**

1. **`thermodynamics-entropy-unification.md`** — The Boltzmann entropy $S = k_B \ln W$, Gibbs entropy, the bridge to Shannon entropy (Jaynes: MaxEnt principle), why entropy has the same formula in physics and information theory. The second law as an information-theoretic statement.

2. **`partition-function-free-energy.md`** — The Boltzmann distribution $p \propto e^{-E/kT}$, the partition function $Z$, Helmholtz free energy $F = -kT \ln Z$, variational free energy formulation (connects directly to Friston's FEP). The free energy as the fundamental object in statistical mechanics.

3. **`ising-model-phase-transitions.md`** — The Ising model as paradigmatic: lattice spins, nearest-neighbor interactions, Onsager's exact solution, spontaneous magnetization, the critical temperature and universality. Phase transitions as mathematical phenomena. The mean-field approximation.

4. **`hopfield-boltzmann-machines.md`** — Hopfield networks as energy-based associative memories (1982), Boltzmann machines as stochastic Hopfield nets, restricted Boltzmann machines and their role in deep learning history. Energy landscapes and attractor dynamics for memory retrieval.

5. **`spin-glasses-replica-method.md`** — The Sherrington-Kirkpatrick model, frustration and disorder, replica symmetry and replica symmetry breaking (Parisi), the mathematical language of disordered systems. Why spin glasses are the right model for understanding the loss landscape of deep networks.

6. **`statistical-mechanics-of-learning.md`** — Gardner's capacity analysis (1988), the Vapnik-Chervonenkis connection to statistical mechanics, the thermodynamic limit in learning theory, phase transitions in generalization (from memorization to generalization). Connects Phase 2 (concentration) and information-theory (already present).

Checklist:
- ☑ Write `thermodynamics-entropy-unification.md` (2026-03-21)
- ☑ Write `partition-function-free-energy.md` (2026-03-21)
- ☑ Write `ising-model-phase-transitions.md` (2026-03-21)
- ☑ Write `hopfield-boltzmann-machines.md` (2026-03-21)
- ☑ Write `spin-glasses-replica-method.md` (2026-03-21)
- ☑ Write `statistical-mechanics-of-learning.md` (2026-03-21)
- ☑ Promote all 6 files to `knowledge/mathematics/statistical-mechanics/` (2026-03-21, written directly with trust: medium)
- ☑ Update `knowledge/SUMMARY.md` entry (2026-03-21)

---

### Phase 4 — Causal Inference & Structural Causal Models

*Addresses Gap D. Pearl's framework is central to AI interpretability, fairness, and decision theory.*

Target subfolder: `knowledge/mathematics/causal-inference/`

**Files to research and write:**

1. **`pearls-causal-hierarchy.md`** — The three rungs: association ($P(Y|X)$), intervention ($P(Y|\text{do}(X))$), counterfactual ($P(Y_x|X' = x', Y' = y')$). Why correlation doesn't imply causation and what additional structure is needed. Rubin's potential outcomes vs Pearl's graphical approach.

2. **`structural-causal-models-dags.md`** — Structural equations, directed acyclic graphs (DAGs), the Markov condition, faithfulness assumption, d-separation. How graphical structure encodes conditional independence claims. Pearl's d-separation criterion.

3. **`do-calculus-identification.md`** — The do-calculus as a complete system for deriving interventional distributions from observational data. When causal effects are identifiable from observational data. The backdoor and frontdoor criteria. Instrumental variables.

4. **`counterfactuals-rubin-potential-outcomes.md`** — Rubin's potential outcomes framework, the fundamental problem of causal inference, average treatment effects (ATE, ATT, LATE). How RCTs relate to Pearl's do-operator. Mediation analysis and natural direct/indirect effects.

5. **`causal-discovery-algorithms.md`** — PC algorithm, FCI algorithm, Greedy Equivalence Search, LiNGAM. What can be learned about causal structure from purely observational data. The Markov equivalence class problem. Connections to constraint-based and score-based methods.

Checklist:
- ☑ Write `pearls-causal-hierarchy.md` (2026-03-21)
- ☑ Write `structural-causal-models-dags.md` (2026-03-21)
- ☑ Write `do-calculus-identification.md` (2026-03-21)
- ☑ Write `counterfactuals-rubin-potential-outcomes.md` (2026-03-21)
- ☑ Write `causal-discovery-algorithms.md` (2026-03-21)
- ☑ Promote all 5 files to `knowledge/mathematics/causal-inference/` (2026-03-21)
- ☑ Update `knowledge/SUMMARY.md` entry (2026-03-21)

---

### Phase 5 — Computational Complexity

*Addresses Gap E. Natural continuation from Turing undecidability (logic-foundations) to the fine structure of tractability.*

Target subfolder: `knowledge/mathematics/complexity-theory/`

**Files to research and write:**

1. **`p-np-and-complexity-classes.md`** — P, NP, co-NP, PSPACE, EXP. The P vs NP problem as the central question of computer science (not just a technical question but a question about whether creativity can be automated). The polynomial hierarchy. Why the problem is hard to resolve.

2. **`np-completeness-cook-karp.md`** — Cook's theorem (SAT is NP-complete), Karp's 21 reductions, the structure of NP-completeness proofs. Why NP-complete problems are interesting: they're hard in theory but tractable in practice (approximations, specific instances). The approximability frontier.

3. **`circuit-complexity-lower-bounds.md`** — Boolean circuits as a model of computation, circuit complexity classes (NC, AC, TC), monotone circuit lower bounds (Razborov-Smolensky), the difficulty of proving lower bounds. Why proving P ≠ NP is hard (relativization, natural proofs, algebrization).

4. **`interactive-proofs-randomness.md`** — Interactive proof systems (Arthur-Merlin games), IP = PSPACE (Shamir), probabilistically checkable proofs (PCPs), zero-knowledge proofs. Randomized algorithms (BPP, RP, ZPP). The role of randomness in computation.

5. **`descriptive-complexity-logic.md`** — Fagin's theorem (NP = Existential Second Order Logic), descriptive characterizations of complexity classes, finite model theory. The machine-independent characterization of complexity connects back to the logic-foundations cluster.

Checklist:
- ☑ Write `p-np-and-complexity-classes.md` (2026-03-21)
- ☑ Write `np-completeness-cook-karp.md` (2026-03-21)
- ☑ Write `circuit-complexity-lower-bounds.md` (2026-03-21)
- ☑ Write `interactive-proofs-randomness.md` (2026-03-21)
- ☑ Write `descriptive-complexity-logic.md` (2026-03-21)
- ☑ Promote all 5 files to `knowledge/mathematics/complexity-theory/` (2026-03-21)
- ☑ Update `knowledge/SUMMARY.md` entry (2026-03-21)

---

### Phase 6 — Optimization Theory

*Addresses Gap F. Underpins game theory (Nash as fixed point of best-response), ML (gradient descent), and mechanism design.*

Target subfolder: `knowledge/mathematics/optimization/`

**Files to research and write:**

1. **`convex-analysis-separation.md`** — Convex sets, convex functions, supporting hyperplanes, separation theorems (Hahn-Banach). Why convexity matters: a convex optimization problem has no spurious local minima. Subdifferentials and non-smooth convex analysis.

2. **`duality-theory-minimax.md`** — Lagrange duality, strong duality conditions (Slater's), the minimax theorem (von Neumann), saddle-point problems. How LP duality, Nash equilibrium, and minimax all share the same deep structure. Connections to mechanism design (VCG already present) and to GANs.

3. **`gradient-descent-convergence.md`** — Gradient descent (GD), stochastic GD (SGD), convergence rates for convex problems (O(1/t) for GD, O(1/√t) for SGD), momentum methods (Nesterov acceleration), the role of learning rate schedules. Why SGD generalize better than full-batch GD (implicit regularization).

4. **`nonconvex-landscapes-saddle-points.md`** — The geometry of non-convex loss surfaces in deep learning: why saddle points dominate over local minima in high dimensions (Dauphin et al.), the loss surface of wide neural networks (Choromanska et al.), mode connectivity and linear mode interpolation.

5. **`online-learning-regret-bounds.md`** — Online convex optimization, the regret framework, the follow-the-regularized-leader (FTRL) algorithm, multiplicative weights / Hedge, regret bounds of $O(\sqrt{T})$. The connection to statistical learning theory (excess risk vs regret) and to game theory (no-regret dynamics converge to correlated equilibria).

Checklist:
- ☑ Write `convex-analysis-separation.md` (2026-03-21)
- ☑ Write `duality-theory-minimax.md` (2026-03-21)
- ☑ Write `gradient-descent-convergence.md` (2026-03-21)
- ☑ Write `nonconvex-landscapes-saddle-points.md` (2026-03-21)
- ☑ Write `online-learning-regret-bounds.md` (2026-03-21)
- ☑ Promote all 5 files to `knowledge/mathematics/optimization/` (2026-03-21)
- ☑ Update `knowledge/SUMMARY.md` entry (2026-03-21)

---

## Priority and Sequencing

Execute phases in this order:

| Order | Phase | Files | Rationale |
|-------|-------|-------|-----------|
| 1 | Dynamical Systems | 7 | Alex's primary lens for intelligence; severe gap |
| 2 | Probability Theory | 7 | Foundation for everything else on this list |
| 3 | Statistical Mechanics | 6 | Bridges FEP + info-theory + ML; high conceptual density |
| 4 | Causal Inference | 5 | High AI relevance; connects to existing game-theory |
| 5 | Complexity Theory | 5 | Extension of existing logic-foundations work |
| 6 | Optimization | 5 | Underpins ML and game-theory; can be done anytime |

**Total:** 35 new files across 6 new subfolders. Doubles the mathematics knowledge base.

---

## Cross-linking Targets

After all phases are complete, add cross-references in:

- `knowledge/philosophy/free-energy-autopoiesis-cybernetics.md` → link to dynamical systems + statistical mechanics
- `knowledge/philosophy/intelligence-dynamical-systems-conversation.md` → link to Phases 1 and 2
- `knowledge/mathematics/information-theory/entropy-source-coding-theorem.md` → link to thermodynamics-entropy-unification
- `knowledge/mathematics/information-theory/pac-learning-sample-complexity.md` → link to concentration inequalities + statistical mechanics of learning
- `knowledge/mathematics/information-theory/kl-divergence-cross-entropy.md` → link to partition function + free energy
- `knowledge/mathematics/game-theory/mechanism-design-revelation-principle.md` → link to causal inference + duality theory
- `knowledge/mathematics/logic-foundations/turing-undecidability-halting.md` → link to complexity theory cluster
- `knowledge/mathematics/logic-foundations/curry-howard-isomorphism.md` → link to online learning / optimization (Curry-Howard → homotopy type theory note)

---

## Scope Note: What Is Explicitly Deferred

The following mathematical areas were considered and deliberately deferred:

- **Abstract algebra / Galois theory**: Intellectually rich but lower direct relevance to Alex's current research programs. Can be added as a Phase 7 if interest is confirmed.
- **Differential geometry / Riemannian geometry**: Relevant to FEP (geodesics on statistical manifolds = information geometry) but high notation overhead. Defer until probability and statistical mechanics are established.
- **Algebraic topology / Homotopy type theory**: Connects to Curry-Howard but is a deep standalone research program. Defer to Phase 7 after complexity theory is in place.
- **Number theory / Cryptography**: Lower intellectual relevance to Alex's stated interests. Skip unless cryptographic foundations become relevant.
