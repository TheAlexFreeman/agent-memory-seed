---
created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: research Darwinian foundations of cultural evolution — Dawkins, meme concept, replication/variation/selection applied to ideas"
origin_session: chats/2026/03/19
source: agent-generated
status: active
trust: medium
type: research-plan
---

# Research Plan: Cultural Evolution and the Epistemics of Ideas

## Goals

Two completed research plans cover related territory without providing the underlying mechanistic framework: the rationalist community survey (how a specific epistemic community formed and spread) and the AI paradigm genealogy (how AI technical ideas developed and won). Missing is the *science* of how ideas propagate, get selected, mutate, and survive or die — the mechanics of what might be called "intellectual culture." Cultural evolution provides exactly this: a Darwinian framework applied to cultural units (memes, practices, institutions) that operate by replication, variation, and selection. This bears on how AI capabilities diffuse through the technical community, whether the rationalist community's ideas are epistemically sound or merely well-propagated, and how scientific paradigms form and stabilize.

Primary connections to existing files:
- `rationalist-community/` — describes a cultural phenomenon; cultural evolution explains the mechanism
- `ai-history/` — describes how AI ideas spread; cultural evolution explains the spread
- `philosophy/synthesis-intelligence-as-dynamical-regime.md` — both biological and cultural evolution are instances of the self-organizing dynamics frame
- `ai-frontier/epistemology/compression-and-intelligence.md` — culture as accumulated compressed worldly structure

---

## Problem statement

The rationalist community research describes what LessWrong believes and why; it doesn't explain *how* those beliefs spread so effectively in certain communities and failed to spread in others. The AI genealogy describes the lineage of technical ideas but not the selection pressures that determined which ideas survived (compute availability, institutional backing, benchmark design are all selection pressures on ideas). Cultural evolution provides a principled framework for asking: what are the fitness criteria for ideas in intellectual communities? How do they propagate? What makes some memeplexes (clusters of mutually reinforcing ideas) more stable than others? This enriches the existing research with explanatory depth.

---

## Scope decisions

**In scope:**
- Foundational memetics: Dawkins' meme concept, Blackmore's development, the replicator/interactor distinction
- Dual inheritance theory: Boyd, Richerson, Henrich — culture as a second inheritance system with its own evolutionary dynamics
- Cultural transmission mechanisms: imitation, teaching, prestige-biased learning, content-biased learning
- Cumulative culture and collective intelligence: Henrich's WEIRD problem, collective brain hypothesis
- Epistemic injustice and structural barriers to idea propagation (Fricker)
- Application: AI paradigm evolution, rationalist community dynamics, how LLMs affect cultural evolution

**Out of scope:**
- Gene-culture coevolution in detail (lactase persistence, etc.) — biological specifics not needed
- Evolutionary psychology beyond what's needed for cultural transmission
- Full sociology of knowledge (Mannheim, Merton) — handled tangentially

---

## Phases

### Phase 1 — Foundations of cultural evolution

**1.1 Dawkins and the Meme Concept**
- Dawkins' original proposal (*The Selfish Gene*, 1976, ch. 11): memes as cultural replicators — units of cultural transmission that undergo variation and selection
- The replicator requirements: fidelity, fecundity, longevity — memes vary in these properties
- Examples: tunes, ideas, catch-phrases, clothing fashions, architectural styles
- Critiques: what is the unit of cultural replication? Memes are poorly defined; no clear boundary; high fidelity is not obvious for ideas
- Dennett's extension: memes as brain parasites that use human minds as hosts; religion, nationalism as memetically fit ideas regardless of their truth or utility to hosts
- Useful vs. dangerously over-extended: the meme concept as a productive metaphor vs. a pernicious one

**1.2 Blackmore: The Meme Machine**
- Blackmore's development: imitation as the defining capacity; humans as the only animals capable of true imitation
- The imitation machine: we copy both the content of ideas and the behavior of successful imitators (prestige bias in transmission)
- The evolution of language, religion, and the self as memetic phenomena
- The "temes" extension: technology as a third replicator (beyond genes and memes) — relevant to AI
- Critique: Susan Blackmore's extreme position (the self is a memetic construction; free will is an illusion) is contested; worth knowing as a position even if not fully endorsed

**1.3 The Replicator/Interactor Distinction (Hull)**
- David Hull's application of evolutionary biology to science: the replicator (what is copied — the idea/theory) vs. the interactor (what interacts with the environment — the scientist/community)
- This gives conceptual precision missing from Dawkins: we can ask what the units of cultural replication are (theories? research programs? practices?) without assuming they must be brain-state atoms
- Application to AI research: the "transformer architecture" is a replicator; various labs are interactors; the selection environment is benchmark performance, publications, and compute availability

### Phase 2 — Dual inheritance theory and cultural transmission mechanisms

**2.1 Boyd, Richerson, and Dual Inheritance Theory**
- The central claim: humans have two inheritance systems — biological (genes) and cultural (socially learned information); both evolve, and they interact
- Cultural evolution is Darwinian: variation (new ideas), differential transmission (some ideas spread more), heritability (transmitted to others) — all the ingredients for evolution
- Cultural evolution is not genetic evolution: much faster (no generational time); Lamarckian in some respects (acquired traits can be transmitted); directed by cognitive biases
- Why culture accelerates: accumulated cultural adaptations can exceed what any individual could reinvent; this is why humans dominate ecosystems despite being individually weak

**2.2 Transmission Biases and Content Biases**
- Conformity bias: copy the majority — adaptive when social information is more reliable than individual information but leads to cultural inertia and herd behavior
- Prestige bias: copy successful/high-status individuals — adaptive shortcut; does not require understanding why they are successful, only observing success
- Content biases: some ideas are intrinsically easier to transmit (memorable stories, counterintuitive but not too counterintuitive, emotionally engaging, actionable)
- The cognitive attractors hypothesis (Sperber): some ideas are more "catchy" because they fit cognitive biases — religious beliefs about agents, morally relevant narratives, memorable but surprising claims
- Applied to rationalist community: prestige bias (Yudkowsky's status as autodidact genius) + content bias (counterintuitive but actionable Bayesian ideas) explain rapid spread within a specific prestilled community

**2.3 Prestige, Dominance, and Trickle-Down Dynamics**
- Henrich & Gil-White: prestige-based deference is a human universal; we pay attention to and copy those who are successful
- Prestige markers: track record, confidence, fluency, beauty, wealth — proxies for underlying competence
- The prestige cascade: new ideas enter through high-prestige practitioners; validation from multiple high-prestige sources triggers broader adoption
- Applied to LLM adoption: OpenAI's prestige (research reputation + product success) drove early adoption; once adoption reached threshold, conformity bias took over; alternative approaches (SSMs, MoE-first architectures) faced uphill cultural battle

### Phase 3 — Cumulative culture and collective intelligence

**3.1 Henrich: The Secret of Our Success**
- Humans' evolutionary advantage is not individual intelligence but collective intelligence — the "cultural brain" that accumulates adaptations across generations
- The dark implication: individual rationality is often less important than cultural inheritance; what you know is mostly what your culture gives you
- The WEIRD problem (Western, Educated, Industrialized, Rich, Democratic): most psychological studies use WEIRD populations; results don't generalize; most humans have radically different cognitive profiles shaped by different cultural evolution
- Application to AI: LLMs trained on WEIRD internet text inherit WEIRD cognitive profiles; the "universal" AI is not universal

**3.2 Cumulative Culture and the Ratchet**
- Tomasello's cultural ratchet: human artifacts and practices improve over time because each generation starts where the previous left off; chimpanzees can individually innovate but cannot ratchet
- The conditions for ratcheting: faithful transmission (imitation, teaching), continuous variation (creativity), cumulative selection (retaining improvements)
- Why AI could be a cultural ratchet accelerator: LLMs can transmit and build on accumulated cultural knowledge much faster than human intergenerational transmission; the danger is that the ratchet may not reliably move in the direction of human values

**3.3 The Evolution of Norms and Punishment**
- Norms as cultural units: rules about behavior that are enforced by social sanction, not genes
- Third-party punishment: humans punish norm violators even at personal cost — not explainable by individual fitness alone
- Cultural group selection: groups with pro-social norms outcompete groups without them; norms that support intra-group cooperation spread
- Implications for AI safety: AI safety norms in the technical community are cultural units subject to these dynamics; competition (individual lab vs. safety norms) and coordination (safety coalitions) are culturally mediated

### Phase 4 — Epistemic communities and idea fitness

**4.1 What Makes Ideas Epistemically Fit vs. Propagation-Fit**
- The fitness-in-culture vs. truth correlation: an idea can be maximally fit for propagation and false; a true idea can be unfit for propagation
- Epistemically virtuous communities: communities with norms that align propagation fitness with truth (transparency, falsifiability, independent replication, disagreement tolerance)
- Epistemically vicious communities: communities whose transmission biases select for unfalsifiable, self-flattering ideas
- Is the rationalist community epistemically virtuous? Assessment through the cultural evolution lens: prestige-bias dominance around Yudkowsky; content-biased toward counterintuitive ideas that feel clever; norms that privilege individual reasoning over disciplinary consensus — mixed results

**4.2 Fricker: Epistemic Injustice**
- Testimonial injustice: deflating the credibility of a knower due to identity prejudice (the speaker is a woman, Black, young, etc.)
- Hermeneutical injustice: a gap in collective interpretive resources that puts some people at a systematic disadvantage — no concept to describe their experience because their experience is not represented in the concept-formation process
- Epistemic virtues as social: knowledge is produced in communities; community structure determines whose knowledge counts
- Application to AI: current LLMs train on text produced by people with unequal access to writing and platforms; the concepts encoded are those of the represented groups; hermeneutical injustice is baked into the training distribution

**4.3 How LLMs Affect Cultural Evolution**
- LLMs as a new transmission mechanism: can transmit ideas with high fidelity, high volume, and low cost — unlike human teachers, who introduce noise and variation that enables cultural evolution
- The cultural monoculture risk: if everyone uses the same LLMs for information, conformity bias is amplified massively; diversity of transmitted ideas decreases; cultural evolution stalls
- The counter-risk: LLMs synthesize across cultural traditions at scale, producing novel combinations previously inaccessible (cross-cultural meme mixing); this could accelerate cultural evolution
- The selection pressure shift: before LLMs, ideas spread because humans found them compelling; with LLMs, ideas that are represented in training data spread, independent of current human evaluation — a shift in who (what) applies selection pressure

---

## Output format

Files go in `knowledge/_unverified/social-science/cultural-evolution/` with standard frontmatter.

---

## Progress tracking

### Phase 1 — Foundations of cultural evolution
- [ ] 1.1 Dawkins and the meme concept
- [ ] 1.2 Blackmore: the meme machine
- [ ] 1.3 Hull: replicator/interactor distinction

### Phase 2 — Dual inheritance and transmission
- [ ] 2.1 Boyd, Richerson, and dual inheritance theory
- [ ] 2.2 Transmission biases and content biases
- [ ] 2.3 Prestige, dominance, and trickle-down dynamics

### Phase 3 — Cumulative culture
- [ ] 3.1 Henrich: the secret of our success
- [ ] 3.2 Cumulative culture and the ratchet
- [ ] 3.3 Evolution of norms and punishment

### Phase 4 — Epistemic communities
- [ ] 4.1 Fitness vs. truth: epistemically fit vs. propagation-fit ideas
- [ ] 4.2 Fricker: epistemic injustice
- [ ] 4.3 How LLMs affect cultural evolution

**Progress:** 0/12 items complete

---

## Priority order

1. **Phase 2.2** (transmission biases) — content and prestige biases; directly illuminates rationalist community spread and LLM adoption dynamics
2. **Phase 3.1** (Henrich: Secret of Our Success) — the collective intelligence/cultural ratchet argument; most important single result
3. **Phase 4.3** (LLMs and cultural evolution) — the synthesis most relevant to current concerns
4. **Phase 1.1** (Dawkins/memes) — foundational; readable; controversial enough to be worth engaging
5. **Phase 4.1** (idea fitness vs. truth) — the epistemological core question
