created: 2026-03-20
last_verified: 2026-03-20
next_action: "Complete — all 13 items done. Human review of knowledge/cognitive-science/relevance-realization/ files recommended."
origin_session: chats/2026/03/20
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Relevance Realization, Insight, and the Cognitive Roots of Intelligence, Rationality, and Wisdom

## Goals

Build a deep knowledge base on relevance realization (RR) — the cognitive process by which minds identify what matters — and on its explanatory reach across the major questions of cognitive science and philosophy of mind. The concept is primarily developed by John Vervaeke, whose lecture series *Awakening from the Meaning Crisis* and 2012 paper with Lillicrap and Lepage present RR as the foundational capacity that unifies attention, insight, intelligence, rationality, and wisdom under a single theoretical framework. This plan investigates that claim systematically, tracing RR's historical antecedents, articulating the core theory, examining insight as its paradigm demonstration, and then extending it to the three cognitive ideals the user identified: intelligence, rationality, and wisdom.

Primary connections to existing files:
- `knowledge/cognitive-science/attention/` — attention is a major mechanism of relevance selection; the spotlight model, salience maps, and FIT are all partial RR theories
- `knowledge/cognitive-science/metacognition/` — metacognitive monitoring tracks how well one's relevance assignments are performing; calibration and the Dunning-Kruger effect bear directly on RR failures
- `knowledge/cognitive-science/concepts/` — concept formation is a form of relevance organization; prototype theory and the basic-level effect are both about which distinctions matter
- `knowledge/philosophy/phenomenology/` — Heidegger's forestructure of understanding, thrownness, and "being-in-the-world" are phenomenological precursors to RR; affordances and salience are Heideggerian before they are Vervaekan
- `knowledge/philosophy/synthesis-intelligence-as-dynamical-regime.md` — the dynamical-systems framing of intelligence is the natural partner for RR as a self-organizing capacity
- `knowledge/philosophy/free-energy-autopoiesis-cybernetics.md` — active inference under the free-energy principle provides a computational vocabulary for relevance detection via prediction error minimization
- `knowledge/philosophy/ethics/` — practical wisdom (phronesis) is the ethical tradition's name for morally situated relevance realization

---

## Problem statement

Much of the existing knowledge base circles a central question without answering it directly: how do cognitive systems — biological or artificial — identify, in real time and without exhaustive search, what matters to them? Attention research explains *which* stimuli are selected but not *why those criteria are the right ones for the task*. Metacognition explains how performance is monitored, but monitoring presupposes an already-fixed relevance frame. Concepts organize information, but concept formation already presupposes that some distinctions are worth drawing. Each field offers partial answers; none provides a unifying account.

Vervaeke's relevance realization theory is the most systematic attempt to fill this gap in the cognitive science/philosophy literature. It proposes that RR is not a separate module but a *self-organizing, opponent-processing dynamic* that runs across all levels of cognition — and that failures of RR explain insight blocks, cognitive biases, irrationality, and the loss of meaning. Understanding RR would complete the cognitive-science arc of this knowledge base and provide a unifying frame that cross-links attention, concepts, metacognition, phenomenology, wisdom, and rationality.

---

## Scope decisions

**In scope:**
- The frame problem in classical AI and its philosophical readings (Minsky, McCarthy, Dreyfus)
- Gestalt psychology as the empirical prehistory of RR: productive vs. reproductive thinking, fixedness, restructuring
- Vervaeke's core theory: opponent processing, self-organization, the relevance landscape
- The four kinds of knowing: procedural, declarative, perspectival, participatory — and how RR operates differently in each
- The aptitudes of intelligence (Vervaeke & Lillicrap 2012): flexibility, integration, appropriate framing
- Insight: phenomenology, incubation, the Aha effect, representational change theory (Ohlsson), neural correlates (Bowden & Jung-Beeman)
- RR and intelligence: why g may reflect RR capacity, the connection to working memory and fluid cognition
- RR and theoretical rationality: confirmation bias, evidence weighting, why relevance frames distort belief updating
- Ecological rationality (Gigerenzen) vs. heuristics-and-biases (Kahneman): RR as the third position that resolves the debate
- Practical rationality and phronesis: Aristotle's account of situational perception, the morally salient features of situations
- Wisdom: philosophical traditions (Aristotle, Confucius, Stoics), empirical research (Sternberg's balance theory, Ardelt's three-component model), and Vervaeke's synthesis
- Participatory knowing and transformative experience (L.A. Paul): how wisdom changes what is relevant
- The meaning crisis: civilizational-scale RR failure, the role of "psychotechnologies" in supporting RR

**Out of scope:**
- Vervaeke's full theological/mystical argument about the meaning crisis in depth (interesting but peripheral to the cognitive science focus)
- Detailed philosophy of religion / Gnostic history traversed in the *Awakening* series — cultural history, not RR theory
- Meditation and mindfulness in clinical/empirical detail — covered better under a dedicated contemplative-practice plan
- Full social epistemology and collective RR — one file only; not a main focus

---

## Phases

### Phase 1 — Historical Antecedents: Gestalt Psychology and the Frame Problem

**1.1 Gestalt Psychology and Productive Thinking**
- The Gestalt distinction between reproductive thinking (applying known algorithms) and productive thinking (genuine insight requiring problem restructuring)
- Wertheimer's *Productive Thinking* (1945): the parallelogram area problem; why rote instruction produces blind application, not understanding
- Köhler's ape experiments: Sultan, the banana, and the sticks — insight as sudden solution after apparent impasse
- Duncker's candle problem and functional fixedness: prior relevance assignment (the box-as-container) blocks novel relevance (the box-as-shelf) — the paradigm case of RR failure under constraint
- The concept of "Umstrukturierung" (restructuring): insight as a reorganization of the problem field so that previously invisible relations become salient
- Productive thinking as a precursor to RR: Gestalt psychology did not theorize the underlying mechanism, but correctly identified that insight requires more than incremental search; Vervaeke later provides the mechanism

**1.2 The Frame Problem: Minsky, Dreyfus, and the Limits of Formalized Relevance**
- McCarthy and Hayes (1969): the frame problem as the challenge of tracking what stays constant when an action occurs — an apparently narrow problem in situation calculus
- Minsky's frames: schema-based representations intended to encode "typical" structure; how context selects which frame to activate — a first attempt to mechanize relevance
- Why frame selection leads to an infinite regress: choosing the right frame requires already knowing what is relevant; frames for selecting frames introduce the same problem recursively
- Dreyfus's critique (*What Computers Can't Do*, 1972; *What Computers Still Can't Do*, 1992): the frame problem as a symptom of disembodied AI's fundamental inability to be "in" a context; formalization requires that everything relevant be explicitly represented, but relevance is precisely what cannot be exhaustively enumerated
- The "relevance problem" as Vervaeke's restatement: not a technical glitch in AI design but a fundamental puzzle about how any system — biological or artificial — avoids combinatorial explosion when computing what to attend to
- The combinatorial explosion: in a world of $n$ features, the number of potentially relevant feature-combinations is $2^n$; no finite search through this space can track relevance in real time; brains must be doing something qualitatively different

**1.3 Attention and Salience Before Vervaeke: Convergent Partial Theories**
- The spotlight/zoom-lens models: attention as a spatial selection device — captures what is relevant *where* but not *what* makes a location relevant in the first place
- Salience maps (Itti & Koch): bottom-up feature-contrast computes a relevance-priority map; partially explains where gaze goes but not how task context modulates the map
- Feature Integration Theory (Treisman): attention binds features into objects — a relevance operation over the feature space; presupposes that feature category membership is already given
- Schema theory (Bartlett, Piaget): prior knowledge actively shapes what is perceived and remembered; schemas are relevance templates, but schema selection is itself a relevance problem
- The shared limitation: every partial theory of attention, salience, or schema takes some level of relevance as already solved and builds a selection mechanism on top; none accounts for the circular bootstrapping by which agents develop relevance sensitivity in the first place

### Phase 2 — Vervaeke's Theory of Relevance Realization

**2.1 Opponent Processing and the Self-Organizing Dynamics of RR**
- The opponent-processing architecture: RR is not a single module but the emergent product of two antagonistic systems running in parallel
- Divergent processing: broad, exploratory, associative — reduces relevance constraints to increase the probability of encountering a solution outside the current frame; analog of spreading activation, mind-wandering, creative ideation
- Convergent processing: narrow, exploitative, goal-directed — tightens relevance constraints to efficiently pursue a current frame; analog of focused attention, deliberate reasoning
- Neither pole is intrinsically correct: over-convergence produces rigidity and functional fixedness; over-divergence produces noise and perseveration on irrelevant cues
- Optimal RR as dynamic balance: the agent repeatedly oscillates between broadening and narrowing, with each cycle calibrating the relevance landscape more accurately
- Self-organization without external designer: the balance point is not specified in advance; it emerges from the interaction between the agent's current commitments, the task environment, and the history of successful vs. unsuccessful relevance assignments
- Connection to self-organized criticality: the brain operates near a critical point between order (over-convergent) and chaos (over-divergent) states; RR is a consequence of maintaining this criticality

**2.2 The Four Kinds of Knowing and RR's Role in Each**
- Procedural knowing: knowing-how; embodied skill that is not explicitly represented; example: riding a bike, speaking a language fluently
  - RR in procedural knowing: the body learns which muscle tensions, joint angles, and balancing corrections are relevant to maintaining a skill — entirely implicit; disruption of procedural RR appears as "choking under pressure" (explicit attention interfering with automatic regulation)
- Declarative knowing: knowing-that; propositional, explicitly representable, transferable through testimony; the dominant mode of academic knowledge
  - RR in declarative knowing: what propositions are relevant to believe given current evidence; the space of potential beliefs is infinite; RR must select which are worth computing
- Perspectival knowing: knowing from a situated standpoint; the first-person "what it is like to be in this situation" — Nagel's famous formulation; connects to phenomenological tradition
  - RR in perspectival knowing: perception is always perspectival; what is foregrounded and backgrounded in a perceptual situation depends on the agent's goals, history, and embodied orientation; Heidegger's "ready-to-hand" (equipment in use, transparent to awareness) vs. "present-at-hand" (equipment broken, dragged into explicit attention)
- Participatory knowing: knowing-by-being-transformed; the agent's identity is partially constituted by the knowing relationship itself; contrast with "spectator epistemology" in which the knower remains unchanged
  - RR in participatory knowing: wisdom requires not just tracking what is relevant but *being the kind of agent for whom the right things are relevant*; transformative experience (L.A. Paul) — some experiences cannot be evaluated in advance because they change what one finds relevant; character formation as the cultivation of participatory RR

**2.3 The Aptitudes of Intelligence: RR as the Common Factor**
- Vervaeke and Lillicrap (2012) argue that the three "aptitudes" of intelligence — which they distinguish from measurable intelligence-as-g — are all expressions of RR:
  - Flexibility: the ability to transfer relevance assignments across domains, reformulating problems by importing relevance structure from analogous solved problems; damaged in over-convergent states (set effects, Einstellung)
  - Integration: the ability to bind relevance across modalities, time scales, and knowledge domains into a coherent situational model; damaged when relevant connections across systems are not made (the "islands of competence" failure mode)
  - Appropriate framing: selecting the right level of abstraction at which to represent a problem; neither too fine-grained (missing the forest for the trees) nor too coarse (missing critical distinctions); the most distinctively RR-related aptitude
- Why g alone is insufficient: the dysrationalia finding (Stanovich) — high-g individuals systematically fail certain reasoning tasks because relevance frames override logical structure; IQ tests measure within a fixed relevance frame, not the ability to select the right frame
- RR as the *missing variable* in intelligence research: it predicts performance precisely in domains where g fails — novel problems, cross-domain transfer, situations requiring context-sensitive judgment rather than within-context computation

### Phase 3 — Insight as the Paradigm Case of Relevance Realization

**3.1 The Psychology of Insight: Impasse, Incubation, and Phenomenology**
- The four-stage model (Wallas 1926): preparation (explicit effortful work, establishing the current relevance frame) → incubation (withdrawal from explicit work) → illumination (the Aha moment) → verification (checking the solution)
- Problem types that require insight: the nine-dot problem, Duncker's radiation problem, the mutilated checkerboard — all share the feature that the initial, natural framing makes the solution invisible, so progress requires frame abandonment rather than frame exploitation
- Impasse as the diagnostic sign: insight problems produce a confident wrong representation, a feeling of being stuck, low "feeling of warmth" as one approaches the solution — the opposite of analytical problems where warmth monotonically increases
- The Aha phenomenology: subjective suddenness and surprise; high felt conviction; frequently accompanied by pleasurable affect; the impression of the solution "coming from outside" deliberate effort
- Metcalfe and Wiebe (1987): the warmth curve as the empirical signature of insight — flat until the moment of solution, then discontinuous jump; contrasts with the continuous warmth increase in analytical problem-solving

**3.2 Neural Correlates of Insight: Gamma Burst, Remote Associations, and the Default Mode Network**
- Bowden and Jung-Beeman (2003): EEG studies showing a high-gamma burst (~40 Hz) in the right anterior temporal lobe approximately 0.3 seconds before subjects report an Aha moment; the temporal lobe as the site of coarse semantic coding that connects distantly related concepts (versus left hemisphere fine-grained coding)
- The compound remote associates task (CRA): three words that share a common associate (e.g., PINE / CRAB / SAUCE → APPLE); solved by either analytic search or sudden insight; neural signatures differ
- Semantic distance and insight: insight solutions typically involve bridging semantically distant concepts; the right temporal lobe's "coarse coding" (broad, weak activation across distant associates) enables the relevant remote connection to surface
- The default mode network (DMN) and incubation: during rest and mind-wandering, the DMN maintains spreading activation across stored knowledge; incubation works not by "resting" the problem but by allowing DMN-mediated spreading activation to find distant connections that focused attention (which suppresses DMN) cannot reach
- Predictive processing account of insight: insight = a *precision-weighted prediction error* from an unexpected direction; the brain suddenly re-weights relevance in light of a pattern it was not explicitly searching for; analogous to Bayesian structure learning where a new latent variable suddenly explains many seemingly unrelated observations

**3.3 Representational Change Theory and RR as the Transformative Mechanism**
- Ohlsson's (1992) representational change theory: insight requires a change in the mental representation of the problem, not just more search within the current representation; three mechanisms: constraint relaxation (loosen an implicit constraint, e.g., "lines must stay within a square"), re-encoding (redescribe a feature of the problem, e.g., "the box as a candleholder"), and elaboration (recall related information previously not active)
- Einstellung effect (set effect): prior solution experience creates a strong attentional/relevance bias toward solutions that worked before; this bias actively suppresses noticing better solutions; a direct RR failure — the agent's convergent system locks on an obsolete relevance frame
- Analogy and insight: Gick and Holyoak (1983) — subjects who read the "fortress" story before the "radiation problem" solve the latter by analogy; analogy works by importing a relevance structure (how the parts of one problem relate) onto a new domain; flexible RR transfer
- Vervaeke's synthesis: insight is not a special cognitive faculty; it is what happens when the opponent-processing system oscillates away from an over-converged (fixed) frame and back to a broader relevance landscape, allowing a previously suppressed relevance assignment to surface and dominate; the Aha is the phenomenological signature of a relevance landscape discontinuously reorganizing
- RR as predictive of insight therapy: mindfulness- and flow-based interventions that loosen rigid relevance frames improve insight problem-solving performance — evidence that RR is the operative variable

### Phase 4 — Intelligence, Rationality, Wisdom, and Synthesis

**4.1 RR and Rationality: Theoretical, Practical, and Ecological**
- Theoretical rationality and relevance: belief revision requires identifying which evidence is relevant to which beliefs; confirmation bias = the tendency to treat evidence that confirms current beliefs as more relevant than disconfirming evidence; motivated reasoning = selectively attending to evidence relevant to a preferred conclusion
- Stanovich's rationality quotient and dysrationalia: high-g individuals are no less prone to attribute substitution (answering an easy question instead of the hard one) if the substituted question is *framed* as relevant; cognitive sophistication does not automatically correct relevance errors
- The Kahneman-Gigerenzen debate: Kahneman treats heuristic errors as rationality failures; Gigerenzen treats the same heuristics as ecologically rational within their home environments; the debate is unresolvable within both camps because both take the relevance frame as fixed
- RR as the resolution: a heuristic is "rational" or "irrational" depending on whether the agent's relevance frame correctly picks out the features of the environment that the heuristic exploits; the prior question — does the agent have the right relevance frame for this environment? — is a RR question neither Kahneman nor Gigerenzen asks
- Practical rationality and phronesis: Aristotle's *phronesis* (practical wisdom) is the capacity to correctly perceive the morally germane features of a particular situation — the "what matters here" judgment — and then deliberate and act from that perception; without RR, even a perfect deliberative algorithm produces wrong outputs because it operates on the wrong inputs (the wrong features of the situation)
- The skilled perceiver: Aristotle claims the morally educated person perceives situations differently from the uneducated; moral education is not primarily rule-learning but relevance-recalibration — training the agent to notice what matters

**4.2 Wisdom as Optimized RR: Philosophical Traditions and Empirical Research**
- Aristotelian wisdom: the distinction between sophia (theoretical wisdom — knowledge of universal truths) and phronesis (practical wisdom — situated relevance perception + deliberation + action); phronesis is the harder and rarer capacity; its hallmark is context-sensitivity that no set of rules can replicate
- Confucian wisdom: the junzi (exemplary person) is defined by the ability to respond fittingly to each situation — a cultivated sensitivity to what each relationship and context calls for; rituals (*li*) as shared relevance-scaffolding structures that train appropriate responsiveness
- Stoic wisdom: the sage perceives correctly what is and is not "up to us" (eph' hēmin); wisdom is precisely the ability to correctly assign relevance to matters of virtue vs. matters of circumstance; impressions (phantasiai) must be assessed before assenting — an internal RR check on salience
- Sternberg's Balance Theory: wisdom = applying intelligence and creativity to balance intrapersonal, interpersonal, and extrapersonal interests over the long run to achieve a common good; the "balancing" judgment is a RR operation across incommensurable stakeholder perspectives
- Ardelt's three-component model: wisdom = cognitive (understanding of life, tolerance of ambiguity) + reflective (ability to see multiple perspectives, not locked into one frame) + affective (compassion, equanimity) — the reflective and affective components are direct expressions of calibrated RR
- Vervaeke's synthesis: wisdom is not accumulated information or rule mastery; it is the *optimization of RR across the full depth of the agent's existence* — adjusting not just what-to-attend-to in a task, but what-matters in one's life as a whole; this requires participatory knowing (being the right kind of agent) not just declarative knowing (having the right rules)
- Transformative experience (L.A. Paul): some experiences — having a child, losing a faith, encountering a radically different culture — cannot be evaluated from the outside because they change the evaluator's relevance landscape; wisdom includes making well-founded choices at these junctures despite the epistemic impasse; this is possible only through participatory knowing, not spectator reasoning

**4.3 The Meaning Crisis and Threats to RR at Civilizational Scale**
- Vervaeke's diagnosis: the contemporary "meaning crisis" (widespread loss of the sense that life is meaningful, connected to rising mental health crises, nihilism, disconnection) is a civilizational-scale failure of RR
- Historical RR-supporting structures: Axial Age developments (Socratic dialogue, Buddhist meditation, Confucian ritual, Hebrew prophetic tradition) each provided "psychotechnologies" — systematic practices for calibrating relevance; later integrations (Neoplatonism, Christianity) synthesized these into broadly shared relevance-scaffolding frameworks
- The modern collapse: the Scientific Revolution + the Reformation + Cartesian dualism together dismantled the shared relevance frameworks without providing adequate replacements; the "disenchantment" of the world (Weber) = the world no longer presents itself as structured by relevance; everything is flattened into bare resources and preference
- Second-order consequences: without shared psychotechnologies for RR calibration, individuals are left with private, ad hoc relevance systems; these are brittle, prone to addiction (narrow relevance to hedonic cues), cult membership (outsourcing RR to an authority), and nihilism (collapse of RR altogether)
- What can be recovered: Vervaeke argues that certain contemplative and philosophical practices — mindfulness, philosophical dialogue (as therapeutic practice, not academic debate), flow-inducing skill cultivation — function as RR-calibration tools even outside their original religious frameworks; the open question is whether secular institutions can transmit these effectively

**4.4 Relevance Realization: Synthesis and Implications for AI**
- Unifying thread: attention selects what to process (RR at the scene-perception level); concepts organize what distinctions matter (RR at the ontological level); metacognition monitors whether current relevance assignments are serving goals (RR at the monitoring level); insight reorganizes relevance landscapes when they fail; rationality succeeds or fails depending on whether the right relevance frame is operative; wisdom is long-run global optimization of RR; meaning is the phenomenological signature of RR working well
- What RR is not: it is not a unified cognitive module (it is an emergent property of opponent processing); it is not computable by exhaustive search (combinatorial explosion); it is not fully articulable (the agent cannot always say why something matters — participatory knowing)
- AI systems and RR: LLMs partially instantiate RR through attention mechanisms and in-context learning; soft attention computes a weighted relevance sum across all tokens — a fast, continuous approximation to discrete relevance selection; however, transformer attention is frame-relative (relevance is computed within the current prompt context), not frame-transforming (the model cannot abandon its training-time relevance priors); insights, in the RR sense, require frame transformation, not just frame exploitation
- Failure modes for AI RR: prompt injection exploits the model's inability to assess which input channel is relevant (all tokens receive equal syntactic standing regardless of semantic trustworthiness); hallucination is a relevance error — generating plausible-within-the-frame content rather than detecting that evidence for the claim is actually absent; over-refusal is over-convergent RR (treating safety-relevant features as always dominating regardless of context)
- Design implications for agent memory systems: context loading = relevance assignment at session start; the quality of a session depends on how accurately the agent identifies which memories, plans, and knowledge files are relevant to the current task; this is a RR problem that current systems solve by keyword proximity and recency, which is a narrowly computational proxy for genuine relevance; the gap between proxy-relevance and genuine RR is precisely what motivates the curation and recall design of this repository

---

## Output location

`knowledge/cognitive-science/relevance-realization/`

Items: 13 total across 4 phases. Progress tracked in `plans/SUMMARY.md`.
