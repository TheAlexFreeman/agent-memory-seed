created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: research normal-form games, Nash equilibrium definition, existence proof"
origin_session: chats/2026/03/19
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: research-plan

# Research Plan: Game Theory and Mechanism Design

## Goals

The multi-agent AI files cover coordination challenges operationally — context sharing, trust hierarchies, tool conflicts — without the mathematical game-theoretic foundation that explains *why* coordination is hard and *how* to design systems that produce desired coordination outcomes. Game theory is that foundation. Mechanism design extends it to the design question: given that agents pursue self-interest, how do you design the rules of interaction so that self-interested behavior produces socially desirable outcomes? This is precisely the central question of AI alignment read at the system level, and it connects directly to everything from RLHF reward design to AI safety arguments about competitive AI development races.

Primary connections to existing files:
- `ai-frontier/multi-agent/multi-agent-coordination.md` — game-theoretic foundations of coordination failure
- `ai-frontier/alignment/frontier-alignment-research.md` — mechanism design perspective on alignment
- `rationalist-community/` — prisoner's dilemma reasoning, cooperation, defection pervade EA discourse
- `ai-frontier/epistemology/compression-and-intelligence.md` — evolutionary game theory connects to the intelligence-as-adaptation frame

---

## Problem statement

When multiple AI agents interact, or when AI systems interact with humans, the outcome depends not just on what each party wants but on the structure of the interaction. Prisoner's dilemmas produce suboptimal outcomes even for fully rational agents. Coordination games have multiple equilibria — which one is selected determines whether cooperation emerges. Arrow's impossibility theorem shows that no voting rule can aggregate individual preferences into social choices satisfying all reasonable fairness criteria. Without understanding these results, discussions of multi-agent AI coordination remain at the level of engineering intuition rather than principled design. Mechanism design shows that better-designed rules can change equilibrium outcomes — this is the game theory of alignment.

---

## Scope decisions

**In scope:**
- Classical game theory: normal-form games, Nash equilibria, extensive-form games
- Key games: prisoner's dilemma, coordination games, stag hunt, public goods games
- Evolutionary game theory: evolutionarily stable strategies, replicator dynamics
- Mechanism design: revelation principle, Vickrey-Clarke-Groves, matching markets
- Social choice theory: Arrow's impossibility, Condorcet paradox, voting rules
- Signaling theory: costly and cheap talk, sender-receiver games, information transmission
- Application to AI: multi-agent coordination, alignment as mechanism design, AI safety race dynamics

**Out of scope:**
- Full treatment of cooperative game theory (Shapley values, core, bargaining — important but separate)
- Auction theory in full depth (overlaps with mechanism design but can stand alone)
- Behavioral game theory (Kahneman/experimental deviations) — covered in rationality research if done

---

## Phases

### Phase 1 — Foundations of strategic interaction

**1.1 Normal-Form Games and Nash Equilibrium**
- Representing strategic situations: players, strategies, payoffs; the payoff matrix
- Dominant strategies and dominance reasoning: what's optimal regardless of what others do
- Nash equilibrium: a strategy profile where no player can improve by unilateral deviation
- Existence: Nash's theorem — every finite game has at least one Nash equilibrium (possibly in mixed strategies)
- Limitations of Nash: multiplicity, refinements needed (trembling-hand perfect, subgame perfect), absence of dynamics

**1.2 Key Games: Prisoner's Dilemma and Coordination**
- Prisoner's dilemma: individually rational defection produces collectively irrational outcomes
- Why cooperation is rational in repeated games: folk theorem — in infinitely repeated games, cooperation can be sustained by threat of punishment
- Coordination games: Battle of Sexes, Stag Hunt — multiple Nash equilibria; the selection problem
- Schelling points (focal points): equilibria selected by salience in the absence of communication
- Application to AI: why competitive AI labs defect on safety norms (prisoner's dilemma structure) and how binding agreements or credible commitments could change equilibrium

**1.3 Extensive-Form Games and Backward Induction**
- Games in tree form: decision nodes, information sets, strategies as complete contingent plans
- Backward induction: solving from terminal nodes backwards to determine subgame-perfect equilibrium
- The centipede game: backward induction produces an implausible prediction; experiment shows cooperation
- Incomplete information: Bayes-Nash equilibrium; players have private information modeled as types
- Application to multi-agent AI: tool-use sequences as extensive-form games; anticipating subagent defection

### Phase 2 — Evolutionary and emergence perspectives

**2.1 Evolutionary Game Theory**
- Replicator dynamics: strategies that perform better than average increase in frequency
- Evolutionarily Stable Strategies (ESS): strategies resistant to invasion by mutants
- The Hawk-Dove game: finding stable mixes of aggressive and deferential strategies
- Connection to machine learning: gradient descent as replicator dynamics; neural architecture search as strategy evolution
- Multi-population replicator dynamics: predator-prey-style dynamics between interacting populations (e.g., red-teaming and model)

**2.2 Evolution of Cooperation**
- Axelrod's tournament: tit-for-tat wins in round-robin iterated prisoner's dilemma competition
- Properties of winning strategies: nice, provocable, forgiving, clear
- Kin selection and group selection as evolutionary mechanisms for cooperation beyond reciprocity
- The evolution of norms and punishment: third-party punishment as an evolved mechanism for maintaining cooperation
- Application: what "nice, provocable, forgiving, clear" means for AI agent behavior design

### Phase 3 — Mechanism design

**3.1 The Design Problem and Revelation Principle**
- The mechanism design question: what rules of interaction produce desired outcomes when agents are self-interested and strategically sophisticated?
- Revelation principle: every outcome achievable by any mechanism is achievable by a direct truthful mechanism — simplifies design space
- Incentive compatibility: mechanisms where truth-telling is optimal (dominant-strategy or Bayes-Nash IC)
- Implementation: when can a social choice function be implemented by a mechanism?

**3.2 Vickrey-Clarke-Groves Mechanisms**
- The problem: agents have private valuations; how to allocate resources to maximize social welfare without agents misreporting?
- Vickrey auction (second-price sealed bid): truth-telling is a dominant strategy; the seller extracts surplus via the externality payment
- Clarke and Groves extension: VCG mechanisms for general allocation problems
- Limitations: not budget-balanced; collusion; computational complexity at scale
- Application to LLM training: RLHF as an approximation to a preference-revelation mechanism; crowdworkers as agents with private moral valuations

**3.3 Matching Markets**
- Gale-Shapley algorithm: stable matching in two-sided markets (hospitals-residents, college admissions)
- Stability: no blocking pair would prefer to match with each other
- The school choice problem: mechanism design for public goods allocation
- Roth's contributions: recognizing that market design matters; fixing failures in medical residency matching
- Application to AI: aligning multiple stakeholders with conflicting preferences is a matching market problem; no stable match may exist (Arrow-style impossibility)

### Phase 4 — Social choice and aggregation impossibilities

**4.1 Arrow's Impossibility Theorem**
- The problem: how to aggregate individual preference orderings into a social preference ordering
- Arrow's conditions: unrestricted domain, Pareto efficiency, independence of irrelevant alternatives, non-dictatorship
- The theorem: no aggregation function satisfies all four conditions simultaneously
- Implications for AI alignment: any attempt to define a single objective from multiple stakeholder preferences will violate at least one of these conditions
- Escaping Arrow: relaxing conditions (cardinal utilities allow different conclusions; restricted domains work)

**4.2 Social Choice in Practice: Voting Rules**
- Plurality, Borda count, Condorcet methods, approval voting, ranked-choice — comparison
- Condorcet paradox: majority preferences can be cyclical (A beats B, B beats C, C beats A)
- Strategic voting and Gibbard-Satterthwaite theorem: any non-dictatorial voting rule is manipulable
- Practical response: approval voting and score voting as more strategy-resistant
- Application to RLHF: human raters are a voting mechanism over AI outputs; Gibbard-Satterthwaite implies the mechanism is manipulable

### Phase 5 — Signaling and information transmission

**5.1 Signaling Theory: Spence and Costly Signals**
- Spence's signaling model: education as a costly signal of ability (productivity is private information)
- Separating vs. pooling equilibria: when signals successfully transmit information vs. when they don't
- The signal must be costly to fake: only then does it credibly transmit information
- Application to AI: capability demonstrations as costly signals; why performance on held-out benchmarks is a credible signal (hard to fake) vs. reported numbers (cheap talk)

**5.2 Cheap Talk and Crawford-Sobel**
- Crawford-Sobel: sender has private information and potentially misaligned interests; what can the receiver infer?
- Babbling equilibria: when interests diverge enough, no information is transmitted
- Partial information transmission: coarse partitions when interests are somewhat aligned
- Application: AI system prompts as cheap talk — what can be credibly communicated? Instruction following as a cheap talk game where the model's interests and the user's interests may diverge

---

## Output format

Files go in `knowledge/_unverified/mathematics/game-theory/` with standard frontmatter. Phase 5 may go in `knowledge/_unverified/ai-frontier/multi-agent/` given direct application.

---

## Progress tracking

### Phase 1 — Foundations
- [ ] 1.1 Normal-form games and Nash equilibrium
- [ ] 1.2 Prisoner's dilemma and coordination games
- [ ] 1.3 Extensive-form games and backward induction

### Phase 2 — Evolutionary perspectives
- [ ] 2.1 Evolutionary game theory and replicator dynamics
- [ ] 2.2 Evolution of cooperation (Axelrod, tit-for-tat)

### Phase 3 — Mechanism design
- [ ] 3.1 The design problem and revelation principle
- [ ] 3.2 VCG mechanisms
- [ ] 3.3 Matching markets (Gale-Shapley, Roth)

### Phase 4 — Social choice
- [ ] 4.1 Arrow's impossibility theorem
- [ ] 4.2 Voting rules and Gibbard-Satterthwaite

### Phase 5 — Signaling
- [ ] 5.1 Costly signaling (Spence)
- [ ] 5.2 Cheap talk (Crawford-Sobel)

**Progress:** 0/12 items complete

---

## Priority order

1. **Phase 1.2** (prisoner's dilemma + coordination games) — the game-theoretic heart of AI multi-agent and safety race problems
2. **Phase 4.1** (Arrow's impossibility) — single most important result for preference aggregation/alignment
3. **Phase 3.1** (mechanism design foundations) — the design perspective on alignment
4. **Phase 2.2** (evolution of cooperation) — Axelrod's tournament results and their behavioral implications
5. **Phase 5.2** (cheap talk) — directly applicable to AI instruction-following dynamics
