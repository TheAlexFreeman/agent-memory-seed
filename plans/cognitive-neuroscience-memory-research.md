created: 2026-03-19
last_verified: 2026-03-19
next_action: "Phase 1, item 1: research Tulving's episodic/semantic distinction — the founding papers and subsequent debate"
origin_session: chats/2026/03/19
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: active
trust: medium
type: research-plan

# Research Plan: Cognitive Neuroscience of Memory

## Goals

This repository's curation design — temporal decay, archiving, consolidation seasons, episodic vs. semantic vs. procedural distinctions — is based on folk intuitions about memory. There is a rich empirical science here. The goal of this plan is to ground those design intuitions in what is actually known about biological memory systems. Where the biological design supports the repo's choices, confidence increases. Where it diverges, there may be design improvements. Several findings are particularly interesting: memory reconsolidation (memories are rewritten when recalled, not simply retrieved read-only), the role of sleep in consolidation (offline replay enables transfer from hippocampus to cortex), and Ebbinghaus's forgetting curves (the form of temporal decay is well-characterized empirically).

Primary connections to existing files:
- `ai-frontier/retrieval-memory/persistent-memory-architectures.md` — episodic/semantic/procedural applied to AI
- `meta/curation-policy.md` — temporal decay thresholds and consolidation design
- `philosophy/free-energy-autopoiesis-cybernetics.md` — free energy principle's predictive processing is a memory theory
- `plans/personal-identity-memory-research.md` — philosophical identity questions are grounded in memory continuity claims

---

## Problem statement

The repo's curation policy makes decisions that implicitly assume facts about memory: that temporal distance decreases relevance (the decay claim), that rarely-accessed information can be archived without loss (the retrieval-frequency claim), that distinct types of memory warrant different treatment (the taxonomy claim). These assumptions may be right, but they are made without consulting the empirical literature. For instance: reconsolidation research shows that *each retrieval* of a memory modifies it — not just its salience but its content. This suggests that agent memories that are frequently accessed and revised may be the most accurate, while infrequently accessed memories may be frozen and stale, flipping the naive intuition.

---

## Scope decisions

**In scope:**
- Memory systems taxonomy: episodic, semantic, procedural, working memory — with biological substrates
- Hippocampal memory formation and consolidation: encoding, storage, retrieval at the systems level
- Memory consolidation during sleep: slow-wave sleep replay, REM, hippocampal-cortical transfer
- Reconsolidation: the discovery that retrieval opens a window of reconsolidation — memories can be updated
- Forgetting: Ebbinghaus forgetting curves, the spacing effect, retrieval-induced forgetting, motivated forgetting
- Working memory: Baddeley's model, capacity limits (Miller's 7±2), the central executive, phonological loop
- False memory and memory distortion: Loftus on eyewitness testimony; the constructive nature of memory

**Out of scope:**
- Full neuroscience of learning (synaptic plasticity, LTP mechanisms) — too deep into cellular biology
- Memory disorders in clinical depth (Korsakoff, Alzheimer's) — interesting but peripheral
- Computational models of memory in detail (Hopfield networks, etc.) — covered elsewhere

---

## Phases

### Phase 1 — Memory systems taxonomy

**1.1 Tulving's Episodic/Semantic Distinction**
- Tulving's original 1972 proposal: episodic memory (temporally located personal events) vs. semantic memory (general knowledge without temporal tags)
- Dissociation evidence: H.M. (Henry Molaison) — profound episodic deficit with relative sparing of semantic memory (and implicit/procedural memory); semantic dementia — loss of semantic knowledge with intact episodic recall
- The encoding specificity principle: memory retrieval is best when retrieval conditions match encoding conditions
- Autonoesis: episodic memory involves "mental time travel" — re-experiencing the event from the inside; not just knowing that it happened but remembering what it was like
- Implications for agent memory: the session summary (semantic distillate: "what was learned") vs. the raw conversation record (episodic: "what happened") — both are needed for different retrieval tasks

**1.2 Procedural Memory, Priming, and Conditioning**
- Procedural memory: motor skills, cognitive skills — implicit, unavailable to conscious report
- Double dissociation from episodic/semantic: amnesics with no new episodic learning can still acquire new motor skills
- Priming: prior exposure increases processing speed/accuracy for related items without conscious recollection
- Habit learning: basal ganglia system vs. hippocampal system — win-stay/lose-shift vs. cognitive mapping
- Agent implication: the agent's "skills" files (session-start, session-wrapup) function as procedural memory — behavioral routines that are invoked without representing their full rationale

**1.3 Working Memory: Baddeley's Model**
- The multicomponent model: phonological loop, visuospatial sketchpad, episodic buffer, central executive
- Capacity constraints: Miller's 7±2 chunks for short-term storage; interference rather than pure capacity limits
- The central executive: attentional control, task switching, inhibition — the "control room" of working memory
- Working memory and intelligence: strong correlation between working memory capacity and fluid intelligence
- Agent implication: the context window is the agent's working memory; its constraints are analogous to capacity limits; the episodic buffer (integration across subsystems) maps onto context integration across tool outputs

### Phase 2 — Hippocampal memory and consolidation

**2.1 The Hippocampus and Memory Formation**
- Patient H.M.: bilateral hippocampal removal caused anterograde amnesia — could not form new declarative memories, but remote memories pre-surgery were intact
- Hippocampus as rapid learner: encodes new episodes quickly, in one trial ("one-shot learning")
- Pattern separation and pattern completion: hippocampal computation that enables both discriminating similar events (CA3/CA1 axis) and retrieving complete memories from partial cues (CA3 recurrent connections)
- Spatial navigation and cognitive maps: O'Keefe and Moser — place cells and grid cells; the hippocampus as a map of space that generalizes to conceptual space (the "memory palace" technique exploits this)

**2.2 Standard Model of Consolidation**
- Consolidation hypothesis: initially, memories depend on the hippocampus; over time, this dependence decreases as memories are consolidated in cortex
- Systems consolidation: slow transfer from hippocampus to neocortex over days, weeks, months
- Temporal gradient of retrograde amnesia: distant memories are more robust to hippocampal damage than recent memories — evidence for gradual consolidation
- Why this design? The hippocampus is a fast learner; neocortex is a slow learner that stores statistics. Consolidation transfers from fast storage to slow-but-robust storage.
- Agent implication: raw session records (hippocampal fast storage) should be transferred to SUMMARY files (semantic/cortical slow storage) over time; recent records are high-resolution but fragile; old summaries are compressed but durable

**2.3 Sleep and Memory Consolidation**
- Sleep is not merely rest: it is an active phase of memory consolidation
- Slow-wave sleep (SWS): hippocampus replays recent experiences (sharp-wave ripples) in coordination with slow oscillations in cortex; this replay drives consolidation
- REM sleep: associated with emotional memory consolidation and integration with prior knowledge; the "sleep on it" effect for creative insight
- The targeted memory reactivation paradigm: playing environmental cues during SWS selectively boosts consolidation of specific memories — memory consolidation is targeted, not uniform
- Agent implication: "downtime" for agent memory — periods without active queries — could function as consolidation if used for offline reorganization (review queue processing, link-building, SUMMARY updates)

### Phase 3 — Reconsolidation

**3.1 Discovery and Mechanism of Reconsolidation**
- Nader, Schafe, LeDoux (2000): the canonical experiment — fear memory, when reactivated, becomes labile and can be blocked by protein synthesis inhibitors; without reactivation, the same inhibitor has no effect
- Reconsolidation window: a period of hours after memory reactivation during which the memory can be modified or even erased
- The adaptive function: reconsolidation allows memories to be updated with new information rather than being permanently fixed at encoding
- Why this is radical: the prior model was "consolidate once, store forever." Reconsolidation shows every retrieval is potentially a re-encoding.
- Clinical applications: PTSD treatment via reactivation + interference with reconsolidation; beta-blockers during traumatic memory reactivation

**3.2 Implications for Agent Memory Design**
- Memory-as-reconstructive not memory-as-playback: agent memories should not be treated as immutable records
- The access-modifies-the-memory paradox: an agent that reads a memory to use it may inadvertently update it (via the in-context learning / RAG process); subsequent storage of updated context overwrites the original
- Accuracy decreases with time? Not simply — frequently accessed memories may be more accurate (because they are updated with new information) OR less accurate (because they accumulate errors through successive reconsolidation)
- The ACCESS.jsonl files as reconsolidation markers: each access event is an implicit reconsolidation trigger; high-access files may be most accurate, or most distorted

### Phase 4 — Forgetting and false memory

**4.1 Ebbinghaus Forgetting Curves and the Spacing Effect**
- Ebbinghaus (1885): the first systematic study of forgetting — retention drops exponentially with time
- The forgetting curve: approximately $R = e^{-t/S}$ where R is retention, t is time, S is stability of the memory
- The spacing effect: distributed practice produces better long-term retention than massed practice; re-studying an item after a delay produces more durable learning than re-studying immediately
- Why spacing works: the retrieval practice effect (retrieval itself strengthens the trace); the variability effect (studying in different contexts produces more robust representations)
- Agent implication: exponential decay curves in curation policy are biologically vindicated; but the spacing effect suggests that periodic retrieval (even without new information) could strengthen traces — a case for rehearsal passes

**4.2 False Memory and the Constructive Nature of Memory**
- Bartlett (1932): memory is not reproductive but constructive — subjects reproduced stories in culturally normalized ways, not verbatim
- Loftus's misinformation effect: post-event misleading questions incorporate false details into recalled memories
- The DRM paradigm: presenting lists of associated words causes false recall of the critical lure (e.g., presenting "bed, rest, tired, dream..." leads to false recall of "sleep")
- Schema-driven distortion: memory is filled in by expectations and scripts; gaps are completed using general knowledge, not specific traces
- Agent implication: agent summaries are LLM-generated and thus subject to the same constructive errors — hallucinations inserted into "remembered" sessions; schemas overwriting specific episode details

**4.3 Motivated Forgetting and Retrieval-Induced Forgetting**
- Retrieval-induced forgetting (RIF): practicing retrieval of some items from a category *suppresses* retrieval of related but unpracticed items
- Motivated forgetting: evidence (contested) that unwanted memories can be actively suppressed; the frontal-hippocampal inhibition account
- Why forgetting is functional: forgetting reduces interference; removes outdated information; enables efficient access to what is currently relevant
- Agent implication: the curation policy's archiving mechanism is adaptive forgetting — reducing interference from stale information; RIF suggests that emphasizing some memories may suppress related ones (an unintended side effect of selective summarization)

---

## Output format

Files go in `knowledge/_unverified/cognitive-science/memory/` with standard frontmatter.

---

## Progress tracking

### Phase 1 — Memory taxonomy
- [ ] 1.1 Tulving's episodic/semantic distinction
- [ ] 1.2 Procedural memory, priming, conditioning
- [ ] 1.3 Working memory (Baddeley)

### Phase 2 — Hippocampus and consolidation
- [ ] 2.1 Hippocampus and memory formation
- [ ] 2.2 Standard model of consolidation
- [ ] 2.3 Sleep and consolidation

### Phase 3 — Reconsolidation
- [ ] 3.1 Discovery and mechanism
- [ ] 3.2 Agent memory design implications

### Phase 4 — Forgetting and false memory
- [ ] 4.1 Ebbinghaus curves and the spacing effect
- [ ] 4.2 False memory and constructive nature
- [ ] 4.3 Motivated forgetting and RIF

**Progress:** 0/11 items complete

---

## Priority order

1. **Phase 3.1** (reconsolidation) — the most surprising and design-relevant finding
2. **Phase 2.3** (sleep consolidation) — the biological basis for "downtime" as consolidation
3. **Phase 1.1** (episodic/semantic distinction) — foundational taxonomy; extends persistent-memory-architectures.md
4. **Phase 4.1** (Ebbinghaus/spacing effect) — directly validates or challenges the curation decay policy
5. **Phase 4.2** (false memory) — the constructive nature of memory undermines naive accuracy assumptions
