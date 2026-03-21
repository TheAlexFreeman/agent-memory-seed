---
source: agent-generated
origin_session: manual
created: 2026-03-20
trust: medium
type: research-plan
category: research
status: completed
next_action: "All 17 files written across 6 phases; SUMMARY.md updated"
---

# Research Plan: Rationalist AI Discourse — Canonical Ideas, Blind Spots, and Industry Influence

## Goals

The existing rationalist community research (`knowledge/_unverified/rationalist-community/`)
provides a broad intellectual and social history of the LessWrong world. This plan
goes deeper on a specific axis: **the community's discourse about AI systems** —
its canonical ideas, their applicability to the actual AI paradigm that emerged,
the developments the community failed to anticipate, and the concrete influence
that the Berkeley/MIRI nexus has had on the AI industry.

The central questions:

1. **Which canonical rationalist ideas about AI have proven most applicable to
   the current paradigm?** Examine the Sequences-era concepts (orthogonality
   thesis, instrumental convergence, mesa-optimization, Goodhart's law,
   corrigibility, deceptive alignment) against the reality of RLHF-trained
   large language models. Which ideas transferred cleanly? Which required
   significant reinterpretation? Which turned out to address problems that
   the actual paradigm doesn't have?

2. **What did the community fail to anticipate?** The rationalist AI discourse
   was shaped by assumptions about how advanced AI would arrive — recursive
   self-improvement, hard takeoff, agent-like optimization. The actual paradigm
   (statistical language models, scaling laws, RLHF, emergent capabilities)
   diverged sharply from these assumptions. Map the specific prediction failures:
   timeline miscalibration, the absence of FOOM, the centrality of language
   rather than search, the role of commercial incentive structures, the
   importance of deployment-time behavior rather than design-time alignment.

3. **How has the Berkeley/MIRI community influenced the AI industry?** Trace the
   concrete causal pathways: personnel who moved from MIRI/rationalist circles
   into labs (Anthropic, OpenAI, DeepMind); concepts that migrated from
   LessWrong into mainstream AI safety (RLHF itself, constitutional AI, red-
   teaming, evals); policy influence (the 2023 open letter, Senate testimony,
   executive orders, the Bletchley Declaration); and the broader Overton window
   shift on AI existential risk. Distinguish genuine intellectual influence from
   mere temporal coincidence.

### Connection to existing knowledge base

This plan builds directly on several existing knowledge areas:

- **Rationalist community survey** (`_unverified/rationalist-community/`) —
  provides the social and institutional context. This plan adds the AI-specific
  intellectual assessment that the survey intentionally deferred.
- **AI frontier research** (`_unverified/ai-frontier/`) — alignment files
  (`alignment/frontier-alignment-research.md`, `alignment/instruction-following.md`,
  `alignment/rlhf-reward-models.md`) cover the technical landscape. This plan
  asks how rationalist ideas relate to that landscape.
- **AI paradigm genealogy** (`knowledge/ai/history/`) — traces the causal
  history of the current paradigm. This plan asks which parts of that history
  the rationalist community correctly anticipated and which surprised them.
- **Memetic security research** (`_unverified/system-notes/memetic-security-*`) —
  the community's thinking about information hazards and memetic dynamics
  connects to the Engram system's own security model.
- **Ethics and metaethics** (`_unverified/philosophy/ethics/`) — the rationalist
  community's moral philosophy (utilitarian, consequentialist, longtermist) is
  load-bearing for their AI risk arguments.

---

## Problem statement

The existing rationalist community research treats AI risk as one of several
community aims and notes that the community's empirical basis is contested. But
it doesn't drill into which specific ideas held up, which didn't, and why. This
matters beyond historiography: the rationalist AI safety framework is the
intellectual foundation for much of the current AI governance landscape, and
understanding where it's strong and where it's weak is directly relevant to
evaluating contemporary safety proposals, Engram's own security model, and the
broader question of how communities of practice shape technological development.

---

## Scope decisions

**In scope:**
- Canonical rationalist AI concepts and their track record against the actual
  paradigm (Phases 1–2)
- Specific prediction failures and their root causes (Phase 3)
- Concrete industry influence: personnel, concepts, policy, Overton shift (Phase 4)
- The community's internal response to the LLM paradigm — how discourse has
  shifted post-GPT-3/ChatGPT (Phase 5)
- Synthesis: what the rationalist AI discourse got right, what it got wrong,
  and what it reveals about the limits of theoretical prediction for technological
  trajectories (Phase 6)

**Out of scope:**
- The broader EA movement's relationship to AI (covered tangentially but not
  the focus)
- Technical details of alignment research (covered in `_unverified/ai-frontier/
  alignment/`)
- The rationalist community's non-AI intellectual contributions (covered in the
  existing community survey)
- Individual biographical deep-dives beyond what's needed for intellectual
  influence tracing (Yudkowsky biography already exists)

---

## Output file structure: `knowledge/_unverified/rationalist-community/ai-discourse/`

New subfolder under the existing rationalist-community directory:

- `canonical-ideas/` — concept-by-concept assessment against the current paradigm
- `prediction-failures/` — what was missed and why
- `industry-influence/` — personnel, concepts, policy, Overton shift
- `post-llm-adaptation/` — how the discourse has shifted since GPT-3/ChatGPT
- `synthesis/` — integrated assessment

Maintain `rationalist-community/SUMMARY.md` updates as files are written.

---

## Research phases and priority order

### Phase 1 — Canonical ideas and their contact with contemporary AI (highest priority)

The rationalist AI safety framework rests on a set of core concepts, most
articulated before the current LLM paradigm existed. Assess each against
the reality that actually emerged.

1. `canonical-ideas/orthogonality-thesis-instrumental-convergence.md`
   - Bostrom's orthogonality thesis (intelligence and goals are independent)
     and instrumental convergence (sufficiently capable agents converge on
     self-preservation, resource acquisition, goal preservation regardless of
     terminal goals)
   - How these apply (or fail to apply) to LLMs: do language models have
     "goals" in the relevant sense? Is instrumental convergence observed in
     RLHF-trained systems? The mesa-optimization framing vs. the reality
     of gradient-descent-trained predictors
   - Where the concepts retain explanatory power (agentic scaffolding,
     tool-using systems) vs. where they misfire (base models as
     next-token predictors)

2. `canonical-ideas/goodharts-law-reward-hacking-alignment-tax.md`
   - Goodhart's law as applied to RLHF: reward model exploitation,
     sycophancy, length bias, and specification gaming
   - This is arguably the rationalist concept with the cleanest empirical
     vindication — trace the path from abstract formulation to concrete
     observation in deployed systems
   - The "alignment tax" concept: does alignment reduce capability? Evidence
     from constitutional AI, DPO, and instruction-tuning showing alignment
     can *improve* capability — a result the original framing didn't anticipate

3. `canonical-ideas/deceptive-alignment-mesa-optimization.md`
   - Hubinger et al.'s "Risks from Learned Optimization" (2019): mesa-
     optimizers, deceptive alignment, distributional shift as the trigger
     for deceptive behavior
   - How this maps (or doesn't) onto actual LLM behavior: are there
     mesa-optimizers in transformer weights? The gap between the theoretical
     framework and empirical interpretability findings
   - Steelman: where the concern retains force even if the specific mechanism
     is wrong (capability elicitation, sleeper agent experiments, in-context
     scheming)

4. `canonical-ideas/corrigibility-shutdown-problem-value-loading.md`
   - The corrigibility problem: can you build a system that accepts correction
     and shutdown without gaming the correction mechanism?
   - Soares et al. formalization; the utility-indifference approach; the
     stop-button problem
   - How this looks in practice: RLHF as a partial corrigibility mechanism;
     constitutional AI as value loading; the gap between theoretical
     corrigibility and practical instruction-following

5. `canonical-ideas/intelligence-explosion-foom-recursive-self-improvement.md`
   - The I.J. Good / Yudkowsky intelligence explosion hypothesis: once AI
     can improve its own intelligence, a positive feedback loop produces
     superintelligence rapidly ("FOOM")
   - Why this hasn't happened and what it reveals about the hypothesis:
     scaling laws show diminishing returns; architecture improvements are
     discontinuous and human-driven; "self-improvement" in practice means
     better prompting and scaffolding, not recursive redesign
   - The hard takeoff vs. slow takeoff debate (Yudkowsky vs. Christiano)
     and how the actual trajectory has unfolded
   - What remains valid: capability jumps across training runs are real;
     emergent capabilities surprise developers; the pace of improvement
     has exceeded many forecasts even without recursive self-improvement

### Phase 2 — Concepts that required reinterpretation

Some rationalist ideas survived contact with the LLM paradigm but required
significant translation. These are the most intellectually interesting cases.

6. `canonical-ideas/inner-alignment-as-behavioral-reliability.md`
   - The inner/outer alignment distinction (Hubinger): outer alignment
     = the training objective reflects human values; inner alignment =
     the learned model actually optimizes for the training objective
   - In the LLM context: the "inner alignment" concern translates less
     to mesa-optimization and more to behavioral reliability — does the
     model generalize instruction-following to novel situations, or does
     it develop context-dependent compliance?
   - Connection to Engram's own trust model: how confident should you be
     that an agent following governance instructions in training-like
     contexts will follow them in novel ones?

7. `canonical-ideas/value-alignment-as-ongoing-process.md`
   - The original framing: value alignment as a design-time problem —
     get the values right before deployment, because a misaligned
     superintelligence can't be corrected after the fact
   - The actual practice: alignment as an ongoing, iterative process —
     RLHF, red-teaming, constitutional AI, deployment monitoring,
     capability evals, and continuous refinement
   - Why the shift matters: the rationalist framing implied a single
     critical moment; the reality is a continuous feedback loop. This
     is closer to the child-rearing analogy than the rocket-launch
     analogy (connect to Alex's developmental governance frame)

### Phase 3 — What the community failed to anticipate

Map the specific gaps between rationalist predictions and the actual paradigm.

8. `prediction-failures/language-not-search.md`
   - The rationalist AI discourse was shaped by the assumption that
     advanced AI would be an optimization process — a search algorithm
     over a goal space. The actual paradigm is a statistical model of
     language trained by gradient descent
   - Why this matters: the threat models (treacherous turn, instrumental
     convergence, power-seeking) were designed for agent-like optimizers.
     Language models are not natively agents — they become agent-like
     only through scaffolding (tool use, agentic loops, memory systems)
   - The implications: the safety-relevant properties of LLMs are
     different from what the pre-LLM safety literature anticipated.
     Hallucination, sycophancy, and prompt injection are the actual
     failure modes — none of which feature prominently in the canonical
     rationalist threat taxonomy

9. `prediction-failures/commercial-deployment-dynamics.md`
   - The rationalist scenario assumed a small number of actors racing
     toward AGI with the AI's design as the primary variable. The actual
     landscape: massive commercial deployment of incrementally improving
     systems, with market dynamics, regulatory pressure, competitive
     incentive structures, and user behavior as first-order variables
   - The "deployment overhang" problem that the community didn't model:
     hundreds of millions of users interacting with capable but imperfect
     systems, generating real-world harm at scale through mundane
     failure modes (misinformation, manipulation, job displacement)
     rather than through misaligned superintelligence
   - How the community's focus on existential risk led to relative
     neglect of deployment-time safety

10. `prediction-failures/timeline-calibration-and-paradigm-surprise.md`
    - Track the community's AI timeline forecasts: early predictions
      (decades), the post-GPT shift (years), and the recurrent pattern
      of confident predictions followed by surprise
    - The specific paradigm surprise: the community expected progress
      through novel architectures or explicit reasoning systems; the
      actual breakthrough was scaling a relatively simple architecture
      (transformer) with more data and compute
    - What this reveals about the limits of inside-view forecasting:
      the community had detailed models of how AGI might work but
      missed the scaling hypothesis because it didn't fit their models
    - Contrast with Gwern's earlier recognition of the scaling trend

### Phase 4 — Industry influence: the Berkeley/MIRI nexus

Trace the concrete pathways through which rationalist ideas entered the
AI industry.

11. `industry-influence/personnel-and-intellectual-migration.md`
    - Key personnel movements: Dario and Daniela Amodei (OpenAI →
      Anthropic), Chris Olah (interpretability), Jan Leike (alignment
      research at OpenAI/DeepMind), Paul Christiano (alignment research
      at OpenAI, ARC), and others with rationalist community connections
    - The MIRI → lab pipeline: which researchers moved from MIRI or
      MIRI-adjacent positions into major labs, and what ideas they
      carried with them
    - The Berkeley geography: MIRI based in Berkeley, proximity to
      UC Berkeley AI research, the social network effects of physical
      co-location, the rationalist group houses and their role as
      intellectual incubators

12. `industry-influence/concept-migration-rlhf-constitutional-ai-evals.md`
    - Trace specific concepts from rationalist discourse to mainstream
      AI practice:
      - RLHF: Christiano et al. (2017) as a direct product of
        alignment-motivated research
      - Constitutional AI: Anthropic's approach as a descendant of
        value-loading ideas
      - Red-teaming and evals: the eval paradigm as a translation of
        "test your AI for deceptive/dangerous behavior" from the
        theoretical to the practical
      - Interpretability: mechanistic interpretability as a descendant
        of "we need to understand what the AI is doing"
    - Distinguish genuine intellectual lineage from post-hoc framing
      (not everything the labs do was rationalist-influenced, even if
      rationalists claim credit)

13. `industry-influence/policy-and-overton-shift.md`
    - The 2023 open letter ("Pause Giant AI Experiments") and the
      rationalist community's role in organizing it
    - Senate testimony and congressional engagement (Altman, Amodei,
      Marcus; background briefings by safety-focused researchers)
    - Executive orders and the Bletchley Declaration: how existential
      risk language entered policy documents
    - The Overton window shift: "AI could pose existential risk" went
      from fringe rationalist position (2010s) to mainstream concern
      (2023–2024). How much of this shift was caused by rationalist
      advocacy vs. by the visible capabilities of deployed systems?
    - The counter-narrative: critics (Timnit Gebru, Emily Bender,
      the Stochastic Parrots authors) arguing that the existential
      risk framing distracts from present-day harms. How this debate
      maps onto rationalist vs. non-rationalist AI safety approaches

### Phase 5 — Post-LLM adaptation: how the discourse has shifted

The rationalist AI discourse has not stood still since GPT-3 and ChatGPT
changed the landscape.

14. `post-llm-adaptation/doom-discourse-and-p-doom.md`
    - The "p(doom)" discourse: community members publicly stating
      probability estimates for AI-caused human extinction. The culture
      of quantified existential risk
    - Yudkowsky's increasingly pessimistic public statements (2022–2025);
      the "we're all going to die" framing and its reception inside and
      outside the community
    - The internal split: doomers vs. accelerationists vs. cautious
      optimists within the rationalist-adjacent world. How the community
      that prized calibrated uncertainty produced some of its most
      uncalibrated public claims

15. `post-llm-adaptation/from-agent-foundations-to-empirical-alignment.md`
    - The shift in alignment research: from MIRI's agent-foundations
      program (formal, theoretical, pre-paradigm) to empirical
      alignment (RLHF iteration, red-teaming, behavioral evals,
      interpretability on real models)
    - What this shift reveals: the problems that actually need solving
      are tractable with empirical methods, not the intractable formal
      problems MIRI focused on
    - The counterargument: empirical alignment solves current-generation
      problems but may not scale to more capable systems; MIRI's
      concerns may become relevant at a capability level we haven't
      reached yet
    - How the community has processed this shift: the "MIRI was right
      about the importance but wrong about the approach" framing

16. `post-llm-adaptation/rationalist-adjacent-labs-and-organizations.md`
    - Anthropic as the most rationalist-influenced major lab: its
      founding story, constitutional AI as applied alignment theory,
      its safety-first positioning and commercial strategy
    - ARC (Alignment Research Center), METR, and other organizations
      with rationalist roots doing empirical safety work
    - The effective altruism funding pipeline: Open Philanthropy's
      role in funding both rationalist orgs and mainstream safety
      research; the FTX collapse and its impact on the funding landscape

### Phase 6 — Synthesis

17. `synthesis/rationalist-ai-discourse-assessment.md`
    - Integrated assessment: what the rationalist AI discourse got right,
      what it got wrong, and what it reveals about the limits of
      theoretical prediction for technological trajectories
    - The strongest vindications: Goodhart's law, the importance of
      alignment as a problem, the policy Overton shift, the concept
      of evals and red-teaming
    - The clearest misses: the paradigm itself (language models, not
      agent-like optimizers), timeline calibration, the absence of
      FOOM, the centrality of deployment-time rather than design-time
      safety
    - The deeper lesson: the community's theoretical apparatus was
      designed for a different AI paradigm than the one that arrived.
      When the actual paradigm emerged, the community's most useful
      contributions came from translating its concerns into empirical
      practice (RLHF, constitutional AI, evals), not from applying
      its formal frameworks directly
    - Implications for this system: Engram's security model draws on
      several rationalist-adjacent ideas (defense in depth, trust
      tiers, memetic security). Which of those inherit the strengths
      of the rationalist framework, and which inherit its blind spots?
    - Connection to Alex's developmental governance frame: the
      rationalist community modeled AI development as a one-shot
      design problem (get it right before launch). The actual paradigm
      — and Engram's philosophy — treats it as an ongoing developmental
      process. What does this imply for safety research?

---

## Cross-references

- `_unverified/rationalist-community/` — the existing community survey
  (this plan extends it, doesn't replace it)
- `_unverified/ai-frontier/alignment/` — technical alignment landscape
- `knowledge/ai/history/` — the causal history of the current AI paradigm
- `_unverified/philosophy/ethics/` — utilitarian and longtermist moral
  philosophy underlying the community's AI risk arguments
- `_unverified/system-notes/memetic-security-*` — Engram's own security
  model and its rationalist-adjacent intellectual roots
- `cognitive-science/metacognition/calibration-overconfidence-hard-easy.md` —
  calibration science relevant to evaluating the community's forecast record
- `plans/onboarding-redesign.md` — the developmental governance frame
  articulated during the same session connects to Phase 6's synthesis
