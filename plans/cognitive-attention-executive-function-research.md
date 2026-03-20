created: 2026-03-20
last_verified: 2026-03-20
next_action: "Human review of knowledge/cognitive-science/attention/ files recommended"
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Attention, Executive Function, and Cognitive Control

## Goals

The memory science knowledge base surfaced a significant gap: Baddeley's central executive — the component that directs attention across working memory subsystems — is the most important component for explaining fluid intelligence, but it is also the most poorly understood. The context-window-as-working-memory analogy identified that the system's effective intelligence depends on context curation quality, which is precisely what the central executive governs. This plan ground that claim empirically: what is attention, what are its limits, how does executive control manage multiple cognitive tasks, and what does dual-process theory tell us about fast vs. slow reasoning? All of these have direct mappings to LLM behavior and to this system's design.

Primary connections to existing files:
- `cognitive-science/memory/working-memory-baddeley-model.md` — the central executive is the motivation for this entire plan
- `cognitive-science/cognitive-science-synthesis.md` — Section 2 (context window as working memory) opens the question this plan answers
- `philosophy/phenomenology/husserl-time-consciousness.md` — attention has Husserlian dimensions (what is attended is the "now-point")
- `knowledge/ai/frontier-synthesis.md` — reasoning models and the distinction between fast/slow inference connects to System 1/2

---

## Problem statement

The memory synthesis identified that the agent's effective intelligence scales with context-window management quality — but it did not explain what "good context management" means cognitively, or why it is hard. Attention research provides that explanation: human and artificial cognitive systems have a limited-capacity attentional bottleneck; directing attention is an executive function that can succeed or fail; and there are two qualitatively different modes of information processing (fast/automatic vs. slow/deliberate) that interact in ways that produce systematic errors. Without this foundation, recommendations to "improve context curation" remain vague. With it, they become targeted.

---

## Scope decisions

**In scope:**
- Attention as selection: early vs. late selection models; Broadbent's filter theory; Treisman's attenuation; Deutsch-Norman late selection
- Attentional bottleneck and limited capacity: Kahneman's resource model; multiple resource theory; attentional blink
- Feature integration theory (Treisman): how attention binds features into objects; conjunctive vs. disjunctive search; the binding problem
- Visual attention and the saliency map: Itti & Koch model; top-down vs. bottom-up attention guidance
- Dual-process theory (Kahneman System 1/2): automatic vs. controlled processing; cognitive ease; conditions under which each mode dominates
- Cognitive biases as failures of executive control: availability heuristic, anchoring, representativeness, base-rate neglect
- Executive function: inhibitory control, cognitive flexibility, working memory updating — the "unity and diversity" debate (Miyake et al.)
- Sustained attention and vigilance: the vigilance decrement; what determines how long effortful attention can be maintained
- Cognitive load theory (Sweller): intrinsic, extraneous, and germane load; implications for instruction design and knowledge organization

**Out of scope:**
- Full neuroscience of attention (parietal cortex, FEF, LIP) — biological detail beyond what's needed for design implications
- Clinical attention disorders (ADHD) in depth
- Meditation and attention training — interesting but peripheral

---

## Phases

### Phase 1 — Attentional selection and bottleneck models

**1.1 Early, Late, and Attenuation Models of Attention**
- Broadbent's filter theory: attention selects on physical features before full semantic processing; the cocktail party effect as challenge
- Treisman's attenuation model: unattended channel is not blocked but attenuated; semantic content still processed but below threshold
- Deutsch-Norman late selection: all stimuli processed fully; selection occurs only at the response stage
- The Cherry dichotic listening paradigm and what subjects can/cannot report from unattended channels
- Implications for agent context loading: are tools, system prompts, or loaded files "early-selected" (blocked) or "late-selected" (processed but attenuated)?

**1.2 The Attentional Bottleneck and Limited Capacity**
- Kahneman's resource model: attention as a general, undifferentiated, limited-capacity resource allocated to tasks
- Multiple resource theory (Wickens): separate resource pools for visual vs. auditory, spatial vs. verbal processing
- The attentional blink: targets in rapid serial visual presentation are missed if <200ms after a prior target — the bottleneck has a recovery time
- Psychological refractory period: performing two simultaneous tasks produces interference because the bottleneck processes one at a time
- Applications to LLMs: what is the "bottleneck" in transformer attention? How does multi-head attention partially circumvent human-like bottlenecks?

**1.3 Feature Integration and the Binding Problem**
- Pre-attentive vs. attentive processing: some feature conjunctions (color, shape) pop out without focused attention; others require serial search
- Feature Integration Theory (Treisman, 1980): features are registered in parallel feature maps; attention acts as a "glue" that binds features at a location into a unified object representation
- The binding problem: how do distributed neural representations of color, shape, motion, identity get integrated into a coherent object percept?
- Illusory conjunctions: under conditions of diverted attention, features of nearby objects can be incorrectly bound — demonstrating attention's role in correct binding
- Agent analog: when loading many knowledge files into context, the binding of concepts from different files may produce "illusory conjunctions" — incorrect associations between content from different sources

### Phase 2 — Dual-process theory and cognitive control

**2.1 System 1 and System 2: Dual-Process Theory (Kahneman)**
- Two qualitatively distinct modes of processing: System 1 (fast, automatic, associative, effortless, parallel, does not require working memory) and System 2 (slow, deliberate, rule-based, effortful, serial, working memory-dependent)
- The evolutionary logic: System 1 handles routine scenarios efficiently; System 2 handles novel, complex, or conflicting situations
- Heuristics as System 1 outputs: availability (frequency estimated by ease of retrieval), representativeness (probability assessed by resemblance to prototype), anchoring (estimates anchored to initial values) — all produce predictable, systematic errors
- When System 1 output is wrong: dual-process failures occur when System 1 gives a confident but incorrect answer and System 2 fails to override it (due to cognitive load, time pressure, ego depletion)
- The CRT (Cognitive Reflection Test) as a measure of System 2 willingness to override System 1 outputs
- LLM relevance: transformer models may be characterized as a very powerful System 1 (fast, associative, parallel, next-token prediction) with limited System 2 capacity — chain-of-thought prompting as System 2 induction

**2.2 Executive Functions: Inhibition, Updating, Shifting**
- Miyake et al. (2000) "Unity and Diversity" framework: three separable but correlated executive functions — inhibition (suppressing prepotent responses), updating (monitoring and refreshing working memory contents), and shifting (switching between mental tasks)
- Inhibitory control: suppressing dominant responses; the stop-signal task and go/no-go task; failures produce impulsive responses to environmental triggers
- Working memory updating: monitoring the current goal-relevant set; replacing outdated content with new; failures produce perseveration (continuing with an irrelevant strategy)
- Cognitive flexibility / set shifting: switching between task sets; failures produce perseveration or over-switching; Wisconsin Card Sorting Test
- The interaction of executive functions with dual-process theory: System 2 processes require inhibition of System 1 defaults (inhibition), maintenance of goal states (updating), and switching between reasoning frameworks (shifting)
- Agent implications: the session's system prompt and routing instructions govern all three executive functions — inhibiting irrelevant responses, maintaining the right goals, and switching between domains

**2.3 Cognitive Load Theory (Sweller)**
- Three types of cognitive load: intrinsic (inherent complexity of the material — cannot be reduced without changing the content), extraneous (unnecessary complexity from poor presentation — can and should be reduced), germane (load that contributes to learning/schema formation — should be supported)
- Worked-example effect: studying worked examples produces better learning than solving equivalent problems — because problems impose high extraneous load (search for solution method) that competes with schema construction
- Redundancy effect: presenting the same information in multiple formats (text + diagram) can increase extraneous load when the formats are redundant — contrary to intuition
- Split-attention effect: when related information is physically separated, attention must split between them, increasing extraneous load
- Implications for knowledge file design: well-structured files with clear sections reduce extraneous load; comprehensive SUMMARY files with internal organization reduce split-attention effects; files that anticipate agent needs with "agent implications" sections reduce intrinsic load

### Phase 3 — Sustained attention and vigilance

**3.1 The Vigilance Decrement**
- The finding: sustained attention performance deteriorates over time — errors of omission (missed targets) increase, reaction time slows within minutes to hours of a monotonous monitoring task
- Mackworth's (1948) clock test: radar operators missing signals after 30 minutes of monitoring — the original practical motivation
- Rate of signal presentation: the paradox that very-low-probability targets are hardest to detect, even though they are easiest — because the infrequency fails to maintain arousal
- Resource depletion vs. expectancy accounts: does vigilance decrement reflect fatigue/resource depletion, or does it reflect updated probability estimates (rare targets become expected to be rare)?
- Implications for agent operation: long sessions with monotonous operations (repeated file reviews, extended curation) may be subject to a vigilance decrement analog — the model's "attention" to the task degrading over the session

**3.2 Mind-Wandering and Task-Unrelated Thought**
- Killingsworth and Gilbert (2010): humans spend ~47% of waking hours not attending to what they are currently doing; mind-wandering tracks negatively with happiness
- The default mode network (DMN): brain regions that are more active during mind-wandering, self-referential thought, and future simulation than during externally directed attention
- Relation to creativity: mind-wandering produces incubation effects — novel associations, creative insights that occur when attention temporarily decouples from the problem
- Relation to working memory capacity: individuals with higher WM capacity can better regulate mind-wandering — they have better executive control to return to task
- Agent analog: in long sessions, the model generating task-unrelated associations (topic drift, unsolicited elaboration) may be an analog of mind-wandering — a kind of default-mode drift when the external task fails to sustain full attentional engagement

---

## Expected output

11 knowledge files in `knowledge/cognitive-science/attention/`:

| File | Content |
|---|---|
| `early-late-selection-models.md` | Broadbent, Treisman attenuation, Deutsch-Norman, cocktail party effect |
| `attentional-bottleneck-limited-capacity.md` | Kahneman resource model, multiple resources, attentional blink, psychological refractory period |
| `feature-integration-binding-problem.md` | Treisman FIT, pre-attentive/attentive, illusory conjunctions, object binding |
| `dual-process-system1-system2.md` | Kahneman System 1/2, heuristics, CRT, LLM dual-process implications |
| `availability-representativeness-anchoring.md` | Three main heuristics; when they fail; dual-process account |
| `executive-functions-miyake-unity-diversity.md` | Inhibition, updating, shifting; unity-and-diversity findings; agent implications |
| `cognitive-load-theory-sweller.md` | Intrinsic/extraneous/germane; worked examples; split attention; implications for file design |
| `vigilance-decrement.md` | Mackworth clock; resource vs. expectancy; agent session-length implications |
| `mind-wandering-default-mode.md` | DMN, default mode, creativity, WM capacity and regulation |
| `transformer-attention-vs-human-attention.md` | Comparison: self-attention mechanism vs. cognitive bottleneck; how transformers differ from human attentional limits; multi-head attention as partial parallel-selection |
| `attention-synthesis-agent-implications.md` | Capstone: full synthesis of attentional science for agent design; System 1/2 in LLMs; executive function as session management; cognitive load as context organization |

---

## Connection graph

This plan extends:
- `cognitive-science/memory/working-memory-baddeley-model.md` → the central executive resolved
- `cognitive-science/cognitive-science-synthesis.md` → Section 2 deepened

This plan connects forward to:
- `cognitive-science/metacognition-epistemic-self-monitoring-research.md` (planned) — attention and metacognition interact (monitoring one's own attention is a metacognitive skill)
- `knowledge/philosophy/philosophy-synthesis.md` — Husserlian phenomenology of attention complements cognitive science account
- `knowledge/ai/frontier-synthesis.md` — reasoning models as System 2 induction
