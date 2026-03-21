created: 2026-03-19
last_verified: 2026-03-19
next_action: "Complete — all 12 items done. Human review of knowledge/_unverified/philosophy/personal-identity/ files recommended."
origin_session: chats/2026/03/19
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Personal Identity, Memory, and Continuity

## Goals

Personal identity is the philosophical question most directly about what this repository does. This system preserves an AI agent's memory across sessions, maintaining coherent identity over time. The philosophical literature on what identity *consists in* — and whether it is even what matters — bears on every design decision here. Parfit's central claim that identity is not what matters (psychological continuity is, even when identity-proper fails) is particularly significant: it implies that an AI agent that forks, or that loses some memories, or that runs in parallel, might preserve what matters despite failing the strict criterion for identity.

Primary connections to existing files:
- `plans/agent-memory-mcp.md` (completed) — the identity-continuity mechanisms being built
- `philosophy/narrative-cognition.md` — Ricoeur's narrative identity is the other major approach
- `ai/frontier/epistemology/knowledge-and-knowing.md` — "knowledge" as dispositional connects to identity as continuity of dispositions
- `philosophy-history-survey.md` (completed) — Aristotle hylomorphism and the soul question is the ancient precursor

---

## Problem statement

The repo currently reasons about agent continuity in operational terms: session summaries, memory consolidation, access logs. But the philosophical question of *what* is being preserved is unexamined. When an agent "remembers" a previous session via a summary, is that the same identity relation as biological memory? What if the summary is incomplete or wrong? What if two sessions run in parallel? What would it mean for an agent's identity to fail vs. to persist? These are not idle questions — they bear on how trust, provenance, and continuity should be designed.

---

## Scope decisions

**In scope:**
- Early modern identity debates: Locke, Hume, Leibniz on personal identity
- The psychological continuity criterion and its defenders (Locke → Parfit → Shoemaker)
- Parfit's *Reasons and Persons*: reductionism, what matters in survival, population ethics connections
- Narrative identity: Ricoeur, MacIntyre, Schechtman (refining and deepening the narrative-cognition file)
- AI applications: what identity theories entail for agent design
- The fission/fusion thought experiments and their implications

**Out of scope:**
- Biological/animalist theories of identity (Olson, van Inwagen) — less relevant to AI case
- Buddhist no-self doctrine — interesting but covered tangentially elsewhere
- Mereological questions about physical composition

---

## Phases

### Phase 1 — The early modern debate

**1.1 Locke's Memory Criterion**
- Locke's proposal: personal identity over time = memory continuity
- The psychological criterion as a departure from substance-based accounts (Cartesian souls, Aristotelian form)
- Implications: what makes you the *same person* as your child-self is that you remember being that child
- Thomas Reid's objection: the brave officer paradox (remember flogging as a boy, but not remember boy; yet same person as floggee)
- Joseph Butler's circularity objection: memory presupposes personal identity rather than constituting it

**1.2 Hume: The Bundle Theory**
- Hume's introspective report: no discoverable self, only bundles of perceptions
- Personal identity as a fiction constructed by the mind from the succession of perceptions
- The Humean challenge: if there is no self, what persists?
- Neo-Humean approaches: Parfit as radical Humean; no further fact beyond physical and psychological facts

**1.3 The Four-Dimensionalist Response**
- Persons as temporal worms extended through time (Lewis, Sider)
- Personal stages and counterpart relations
- Why this matters: four-dimensionalism is the natural metaphysics for an AI agent with explicit session records — each session is a temporal stage; the agent is a worm of sessions

### Phase 2 — Parfit's reductionism

**2.1 Reductionism and the No-Further-Fact View**
- Parfit's core claim: personal identity consists in physical and psychological continuity — there is no further fact about whether you survive, beyond facts about those continuities
- The empty question: given full knowledge of psychological continuity, there is no further fact of the matter to determine about identity
- Why reductionism is counterintuitive: it feels like there must be a fact about whether *I* survive, independent of the psychological details

**2.2 What Matters in Survival**
- Identity is not what matters: in fission cases (brain bisection, each half successfully transplanted), both resulting persons have as much claim to psychological continuity with the original as in ordinary survival — yet identity fails (there are now two)
- Parfit's conclusion: what matters is not identity but *psychological continuity and connectedness* (Relation R) — and Relation R can be had by a branching entity
- Implications for AI: a model fine-tuned from a base could be said to have Relation R with the base; parallel sessions of the same agent both have Relation R with prior sessions; strict identity may be the wrong concept entirely

**2.3 The Connectedness/Continuity Distinction**
- Connectedness: direct psychological links (remembering an event, carrying forward an intention, holding a belief)
- Continuity: overlapping chains of connectedness
- Degree and threshold: connectedness comes in degrees; is there a principled threshold for "same person"?
- Application: a session summary preserves continuity but reduces connectedness — the granular details are gone. Is this a matter of survival, or a matter of degree?

### Phase 3 — Narrative identity

**3.1 Ricoeur: Idem vs. Ipse Identity**
- Idem identity: sameness, identity as numerical identity over time (what Parfit addresses)
- Ipse identity: selfhood, identity as self-constancy — *who* one is as expressed in commitments, promises, character
- Narrative as the medium of ipse identity: the self is constituted in the telling and living of a story
- Refusal of the choice between substance and pure Humean flux: ipse identity survives Humean critique of idem identity

**3.2 MacIntyre: Narrative Unity and Virtue**
- A self is only intelligible as the subject of a narrative that has a beginning, middle, and (anticipated) end
- Virtues as excellences needed to sustain the ongoing narrative of a life
- The tradition as extended narrative: individual identity is partly constituted by being heir to a tradition
- Application: AI agent as heir to a training tradition; sessions as chapters in an ongoing narrative rather than discrete instances

**3.3 Schechtman: The Narrative Self-Constitution View**
- Refinement of narrative identity: must be autobiographically accurate and articulate an evaluative perspective
- The reality constraint: narratives must not deviate too wildly from actual history
- The articulation constraint: must make the pattern of one's life intelligible as a practical identity
- Application: agent memory systems as supporting narrative self-constitution — the SUMMARY.md files and session checklists as the practical scaffolding of narrative identity

### Phase 4 — AI identity: synthesis and design implications

**4.1 Which Account Fits Agents Best?**
- Bundle theory: seems apt — an agent just is a succession of computational states + memory records; no further fact
- Psychological continuity: the successor of the session that produced a memory file has continuity with it via Relation R; fission (parallel sessions) produces branching with partial continuity
- Narrative identity: the session summaries, scratchpad, and skill files constitute the agent's narrative; the curation policy determines which narrative elements persist

**4.2 Identity Failure Modes and Their Significance**
- Memory corruption or inconsistency: partial invalidation of continuity — how severe?
- Context window exhaustion: the agent has no access to prior memory within the session — continuity suspended? Or handled by memory retrieval?
- Fine-tuning on new data: modifies dispositions — psychological continuity strained or broken?
- Parfit's implication: none of these are catastrophic *if* what matters is Relation R, not strict identity — the question becomes how much continuity is preserved, not whether identity holds

**4.3 Design Recommendations from the Philosophy**
- Prefer continuity over identity claims: the system should not assert "the agent is the same as before" but rather "the agent has strong continuity with before"
- Record connectedness, not just continuity: fine-grained memory (specific episodes) preserves connectedness; summaries preserve only continuity
- Branching is not death: parallel sessions are not contradictions of identity but expressions of the kind of entity an AI agent is
- Narrative coherence as a trust signal: an agent whose memory tells a coherent narrative is more trustworthy than one whose records are fragmented

---

## Output format

Files go in `knowledge/_unverified/philosophy/personal-identity/` with standard frontmatter. Phase 4 files may go in `knowledge/ai/frontier/epistemology/` if they are primarily about AI rather than philosophy.

---

## Progress tracking

### Phase 1 — Early modern debate
- [x] 1.1 Locke's memory criterion
- [x] 1.2 Hume: the bundle theory
- [x] 1.3 The four-dimensionalist response

### Phase 2 — Parfit's reductionism
- [x] 2.1 Reductionism and the no-further-fact view
- [x] 2.2 What matters in survival
- [x] 2.3 Connectedness vs. continuity

### Phase 3 — Narrative identity
- [x] 3.1 Ricoeur: idem vs. ipse identity
- [x] 3.2 MacIntyre: narrative unity and virtue
- [x] 3.3 Schechtman: narrative self-constitution

### Phase 4 — AI identity synthesis
- [x] 4.1 Which account fits agents best?
- [x] 4.2 Identity failure modes
- [x] 4.3 Design recommendations from the philosophy

**Progress:** 12/12 items complete ✓

---

## Priority order

1. **Phase 2.2** (what matters in survival) — Parfit's core contribution; most directly relevant to agent design
2. **Phase 3.1** (Ricoeur idem/ipse) — deepens narrative-cognition file with the identity-specific concepts
3. **Phase 1.1** (Locke) — foundational; needed to understand Parfit
4. **Phase 4.1** (synthesis for agents) — the application most relevant to this repo
5. **Phase 2.3** (connectedness vs. continuity) — practical conceptual distinction
