---
created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: research propositional and predicate logic — syntax, semantics, proof systems, completeness"
origin_session: chats/2026/03/19
source: agent-generated
status: active
trust: medium
type: research-plan
---

# Research Plan: Formal Logic and Foundations of Mathematics

## Goals

Two threads in the existing knowledge base invoke logical foundations without developing them: the AI reasoning files (what LLMs can and can't prove/infer) and the compression-intelligence files (what formal systems can express). Gödel's incompleteness theorems are the deepest results in mathematical foundations and bear directly on questions about the limits of AI reasoning: no sufficiently powerful formal system can prove all truths. The Curry-Howard isomorphism (proofs as programs) connects mathematical logic to type theory and programming. Type theory connects to dependent types and proof assistants — relevant to the code-verification ambitions in AI systems. This plan provides the mathematical substory underlying all discussions of reasoning, knowledge, and limitation.

Primary connections to existing files:
- `ai-frontier/reasoning/reasoning-models.md` — benchmarks test formal reasoning; incompleteness sets limits
- `ai-frontier/epistemology/knowledge-and-knowing.md` — formal vs. informal knowledge; what proof adds
- `ai-frontier/epistemology/compression-and-intelligence.md` — Kolmogorov complexity is a logical concept; undecidability is its cousin
- `rationalist-community/origins/heuristics-biases-bayes-and-bounded-rationality.md` — Bayesian reasoning as an extension of probability logic

---

## Problem statement

The AI reasoning benchmarks (MATH, AMC, theorem proving) measure something real, but without understanding what formal proof is, it is hard to characterize what these benchmarks measure or where the limits lie. Gödel showed that any consistent system powerful enough to express arithmetic contains true statements it cannot prove — this is not a conjecture but a theorem. Understanding why, and what it implies, is essential to a rigorous picture of AI reasoning capabilities and limits. Similarly, the Halting Problem sets computational limits that apply equally to any AI system that reasons algorithmically.

---

## Scope decisions

**In scope:**
- Propositional and first-order predicate logic: syntax, semantics, proof systems, completeness
- Gödel's incompleteness theorems (both) and their proof sketches
- The Halting Problem and reductions
- Type theory: simple types, polymorphism, dependent types, propositions-as-types
- The Curry-Howard isomorphism: the direct correspondence between proofs and programs
- Set-theoretic foundations: ZFC, axiom of choice, continuum hypothesis
- Foundations alternatives: category theory as foundations (Lawvere, Grothendieck)

**Out of scope:**
- Full proof theory (sequent calculus, cut elimination) — too narrow
- Mathematical logic applications in model theory — too technical for this purpose
- Formal verification tools (Lean, Coq, Agda) — engineering, not foundations

---

## Phases

### Phase 1 — Classical logic

**1.1 Propositional and First-Order Logic**
- Propositional logic: syntax (connectives), truth tables as semantics, proof systems (Hilbert-style, natural deduction, sequent calculus)
- Completeness theorem (propositional): every tautology is provable
- First-order (predicate) logic: quantifiers, terms, predicates, interpretations
- Gödel's completeness theorem (1929): every valid first-order formula is provable — distinct from incompleteness
- Soundness and completeness as the central desiderata: what proof systems aspire to

**1.2 Compactness, Löwenheim-Skolem, and Semantic Limits**
- Compactness theorem: if every finite subset of a theory has a model, the whole theory has a model
- Löwenheim-Skolem: any first-order theory with an infinite model has a model of every infinite cardinality
- Why this matters: first-order logic cannot characterize the natural numbers up to isomorphism — any consistent first-order theory of arithmetic has non-standard models
- Implication: LLMs performing first-order reasoning cannot be doing what formal logic does — they are operating in the semantic space, but that space is much larger than intended models suggest

### Phase 2 — Incompleteness and undecidability

**2.1 Gödel's First Incompleteness Theorem**
- The setup: arithmetic (Peano) is a formal system; we want to know what it can prove
- Key construction: Gödel numbering — encoding syntactic objects as numbers so that syntax becomes arithmetic
- Diagonal argument: construct a sentence G that says "G is not provable in this system"
- The theorem: if the system is consistent, G is true but not provable; if the system is complete, it is inconsistent
- What it does NOT say: it does not say mathematics is unknowable, only that no single consistent formal system captures all arithmetic truth

**2.2 Gödel's Second Incompleteness Theorem and Consequences**
- No consistent, sufficiently powerful formal system can prove its own consistency
- The Hilbert program (formalize all of mathematics and prove it consistent internally) is impossible
- Gentzen's consistency proof: consistency of Peano arithmetic provable in a stronger system — transfinite induction up to ε₀
- The hierarchy of strength: systems ordered by what they can prove about other systems

**2.3 Turing and Undecidability**
- Turing machines as the formal model of computation
- The Halting Problem: no algorithm can determine, for arbitrary input, whether an arbitrary program halts
- Proof: diagonalization; identical structure to Gödel's argument
- Rice's theorem: all non-trivial semantic properties of programs are undecidable
- Implication for AI: verifying that an AI system is aligned (a semantic property of its behavior) is undecidable in general — there can be no algorithm that always correctly determines alignment

**2.4 The Relationship to Kolmogorov Complexity**
- Chaitin's incompleteness: for any sufficient proof system, most strings cannot be proven to be random (incompressible) within that system
- Formal undecidability of "this is the most compressed representation": connects incompleteness directly to the compression-intelligence thread
- Gregory Chaitin's omega (probability that a random program halts): maximally unknowable; encodes all mathematical truth

### Phase 3 — Type theory and foundations

**3.1 Simple Type Theory and Lambda Calculus**
- Church's simple type theory: terms have types; well-typed terms cannot produce type errors
- Lambda calculus: the formal calculus of function application and abstraction
- Church-Rosser theorem: reduction is confluent — order of reduction doesn't matter for the final value
- The relationship to programming languages: Haskell/ML type systems are Church's type theory, implemented

**3.2 The Curry-Howard Isomorphism**
- Propositions as types: a proposition P corresponds to the type of its proofs
- Proofs as programs: a proof of P is a term of type P
- The full correspondence: introduction/elimination rules ↔ construction/use of values; intuitionistic logic ↔ typed lambda calculus
- Implications: a program that type-checks is a proof; testing is proof-checking; formal verification is theorem proving
- Why this matters for AI code generation: generating type-correct code is proof generation; LLMs that generate type-safe code are (implicitly) generating valid proofs

**3.3 Dependent Types and Proof Assistants**
- Dependent types: types that depend on values (the type of vectors of length n, where n is a value)
- The Martin-Löf type theory and Calculus of Constructions
- Proof assistants: Lean 4, Coq, Agda — mechanically verified proofs
- AlphaProof (DeepMind, 2024): AI-generated formal proofs in Lean — the current frontier of AI mathematical reasoning
- What formal verification adds that LLM reasoning lacks: a machine-checkable certificate of correctness

### Phase 4 — Set theory and foundations alternatives

**4.1 ZFC Set Theory**
- Zermelo-Fraenkel axioms with Choice: the standard foundation for mathematics
- The role of the axiom of choice: equivalent to Zorn's lemma, well-ordering theorem; used throughout mathematics without explicit invocation
- Independent statements: the continuum hypothesis (CH) is independent of ZFC — neither provable nor disprovable
- What independence means: there are mathematical questions with no mathematical answer (within ZFC)

**4.2 Category Theory as Alternative Foundation**
- Categories, functors, natural transformations
- Lawvere's categorical foundation: toposes as universes of sets
- Why categorists prefer it: abstracts structure without commitment to set-membership as fundamental
- The "Yoneda lemma as the most important theorem in mathematics" claim and why
- Connection to type theory: the HoTT program (Homotopy Type Theory) as an alternative foundation combining topology, type theory, and category theory

---

## Output format

Files go in `knowledge/_unverified/mathematics/logic-foundations/` with standard frontmatter.

---

## Progress tracking

### Phase 1 — Classical logic
- [ ] 1.1 Propositional and first-order logic
- [ ] 1.2 Compactness, Löwenheim-Skolem, and semantic limits

### Phase 2 — Incompleteness and undecidability
- [ ] 2.1 Gödel's first incompleteness theorem
- [ ] 2.2 Second incompleteness and consequences
- [ ] 2.3 Turing and undecidability
- [ ] 2.4 Relationship to Kolmogorov complexity

### Phase 3 — Type theory
- [ ] 3.1 Simple type theory and lambda calculus
- [ ] 3.2 The Curry-Howard isomorphism
- [ ] 3.3 Dependent types and proof assistants

### Phase 4 — Set theory and alternatives
- [ ] 4.1 ZFC set theory
- [ ] 4.2 Category theory as alternative foundation

**Progress:** 0/11 items complete

---

## Priority order

1. **Phase 2.1** (Gödel's first incompleteness) — the single most important result; accessible and profound
2. **Phase 2.3** (Turing and undecidability) — extends to AI alignment undecidability directly
3. **Phase 3.2** (Curry-Howard) — connects logic to programming; most practically relevant
4. **Phase 2.4** (Kolmogorov complexity connection) — closes the loop with compression-intelligence files
5. **Phase 1.1** (classical logic) — foundational prerequisite; can be done in parallel with reading for Phase 2
