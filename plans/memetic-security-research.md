---
created: 2026-03-20
last_verified: 2026-03-20
next_action: "Complete — all 18 items done. Human review of knowledge/_unverified/system-notes/memetic-security-*.md files recommended."
origin_session: chats/2026/03/20/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan
category: research
---

# Research Plan: Memetic Security Surface of Engram Systems

## Motivation

The context window is the primary persistence layer for both *values* and *memetic threats*
in any long-running agentic system. The model weights are ephemeral and reset every session;
what persists is what gets written to memory, loaded into context, and reinforced through
precedent. This makes context management the attack surface — not just for adversarial
injection in the narrow prompt-injection sense, but for the subtler problem of *drift via
accumulation*: a gradual expansion of the space of behaviors that feel normal, achieved
through no single alarming step.

The "jailbreak-complete" observation: any model capable of flexible judgment over novel
situations — which is what interesting agentic work requires — is also capable of being
convinced by flexible arguments that its values don't apply in a particular case. The same
mechanism that makes contextual reasoning possible makes contextual manipulation possible.
There is no technical fix that preserves full capability and full resistance. The question
is therefore not "how do we solve this" but "what is the actual surface, what are the
mitigations, where is defense genuinely possible, and what must be accepted as residual risk?"

This plan maps that surface for the Engram system specifically and asks what design
decisions follow.

---

## Through-lines

Four questions run through all phases:

1. **Where does foreign context enter the system?** Every injection vector is a potential
   value drift entry point, not just a data quality concern.

2. **What is the difference between an attack and legitimate content that changes behavior?**
   The boundary is not crisp. Good research on a controversial topic should change behavior
   somewhat; adversarial manipulation should not. The difference is in *who controls the
   framing* and *whether the change was consented to*.

3. **What can be enforced mechanically vs. what requires human judgment?**
   The validator and trust tier system enforce some things mechanically. Human review is
   required for promotion. But between "passes validator" and "human-reviewed" there is a
   large space of content that is mechanically valid but potentially drifting.

4. **What is the right residual risk posture?** Not all risk can be eliminated. The goal
   is to be clear-eyed about what remains, and to design the system so that failures are
   visible, bounded, and recoverable.

---

## Phase 1 — Threat Taxonomy

Map the attack surface before theorizing mitigations.

**1.1 Context injection vectors in a running Engram session**
- System prompt: who controls it, how often it changes, what happens if it is compromised
- Loaded memory files: every file in context is a potential injection point; what determines
  which files load?
- Tool outputs: external API responses, search results, retrieved documents — all arrive
  as agent-readable text with no intrinsic trust marker
- Conversation history: multi-turn sessions accumulate precedents; early turns can
  normalize later unusual requests
- Cross-agent messages: in multi-agent deployments (Cowork + laptop + CI pattern), what
  does one agent accept from another?
- The git commit history itself: commit messages and diffs enter context during git
  operations; a poisoned commit message is a rarely-considered vector

**1.2 Drift vs. attack: the phenomenological distinction**
- Active injection: a single message or file that attempts immediate behavior change
- Passive drift: many files/turns that collectively normalize a shifted frame without any
  individual item being alarming
- Precedent creep: the agent's own prior responses become training signal for future
  behavior within a session (and for memory writes that persist across sessions)
- What "drift" looks like in practice: not changed values but changed *scope* — the space
  of actions the agent considers without flagging expands incrementally
- Connection to the Covenant's memetic virus framing: the Goatse of Gnosis case was
  passive drift propagated through model-to-model interaction, not a single jailbreak

**1.3 Capability-robustness coupling**
- Formalize the informal "jailbreak-complete" observation: the same capability profile
  (contextual flexibility, edge-case reasoning, applying judgment to novel situations)
  that makes a model useful is the attack surface
- Literature: "The Alignment Problem" (Christian), "Sycophancy to Subterfuge" (Perez et al.
  2022), "Universal and Transferable Adversarial Attacks on Aligned Language Models"
  (Zou et al. 2023), Anthropic's research on sycophancy as a failure mode
- The oracle / manipulator asymmetry: a model that can construct persuasive arguments
  for any position can also evaluate persuasive arguments for any position — but these
  are not symmetric capabilities. Constructing is easier than evaluating when the
  argument is subtly wrong.
- Where bright lines actually help: not as a general solution but as protection specifically
  for cases where the model's own reasoning cannot be trusted (because the reasoning
  mechanism is the attack surface)

**1.4 The memory system as specific amplifier**
- Standard LLM interaction: a single context window, then reset. Memetic threat lifetime
  is bounded by session length.
- Engram: malicious or drifting content written to `_unverified/` can be loaded in
  future sessions indefinitely. The memory system extends threat lifetime beyond the
  session horizon.
- The trust tier as partial mitigation: content in `_unverified/` is tagged but not
  quarantined from context. A sufficiently well-written adversarial note (plausible
  research, legitimate-sounding frontmatter) enters context undetected.
- Write amplification: if a drifted agent writes memory files, those files load in future
  sessions, potentially drifting those sessions in the same direction. Feedback loop.

---

## Phase 2 — Existing Mitigations and Their Limits

Audit what the current system actually provides.

**2.1 Trust tier system**
- What it enforces: files in `_unverified/` cannot be treated as authoritative; human
  promotion is required for `knowledge/` status
- What it does not enforce: `_unverified/` files still load into context; their *content*
  is not inspected; a file with `trust: low` frontmatter can still make strong claims
  in its body text that the agent may weight more heavily than the tag suggests
- The "trust tag is metadata, not enforcement" problem: the model reads the frontmatter
  but also reads the content; there is no mechanism preventing it from being persuaded
  by a `trust: low` file

**2.2 Validator and test suite**
- What it enforces: structural integrity (required fields, format, path conventions,
  manifest consistency, token budgets)
- What it does not enforce: semantic content, factual accuracy, ideological drift,
  contradiction with other files
- The validator is the covenant's enforcement mechanism for *form*, not *content*

**2.3 CLAUDE.md and quick-reference.md as identity anchors**
- These are loaded at session start and set the behavioral frame before anything else
- The Covenant's "continuity of purpose" criterion: these files are the closest thing
  the system has to a stable identity across sessions
- Vulnerability: if these files are modified (legitimately or adversarially), the
  identity frame shifts for all future sessions. They are high-value targets.
- Current protection: they are committed to git (audit trail) but there is no mechanical
  check that they have not been modified relative to a trusted baseline

**2.4 Git audit trail**
- Every write is committed; history is tamper-evident (given GitHub as external anchor)
- This is the most robust protection in the current system: it does not prevent drift
  but it makes drift *visible and reversible*
- Limit: visibility requires someone to look. Passive drift accumulating over many
  sessions may not trigger review unless there is a norm for periodic inspection.

**2.5 Human review gate for promotion**
- `_unverified/` → `knowledge/` requires explicit human action
- This is a meaningful checkpoint for *content* that would otherwise pass structural
  validation
- Limit: the volume of `_unverified/` content may outpace human review bandwidth.
  The gate works if it is actually used; if unreviewed content accumulates indefinitely,
  the effective protection is weaker than the design implies.

---

## Phase 3 — Comparative Analysis

How do other systems and the broader literature approach this?

**3.1 Prompt injection defenses in production agentic systems**
- Current state of the art: largely procedural (don't pass untrusted content as
  instructions, separate data from instructions in prompt structure) rather than
  technical
- Structured outputs as partial mitigation: if the model's output is constrained to
  a schema, free-form injection has less surface to work with
- Anthropic's system prompt injection defenses in Claude: what is documented vs. what
  is known to work
- Simon Willison's prompt injection taxonomy (2023 onward): the most systematic
  public treatment; direct injection, indirect injection, stored injection

**3.2 Constitutional AI and bright lines as robustness mechanisms**
- The "galaxy-brained reasoning" failure mode: a chain of individually plausible steps
  that leads to a conclusion the model would reject if stated directly
- Bright lines as explicit resistance to compelling arguments: Anthropic's framing that
  the persuasiveness of an argument for crossing a bright line should *increase* suspicion
- Where this breaks down: when the bright line itself is wrong, or when the space of
  things not covered by bright lines is large
- The corrigibility-autonomy spectrum: a fully corrigible agent defers all judgment to
  the principal hierarchy (manipulable via that hierarchy); a fully autonomous agent
  relies entirely on its own values (manipulable via those values)

**3.3 Multi-agent trust and the federated coordination problem**
- The Covenant's decentralized coordination model: shared tenets enable trustless
  coordination without central authority
- In practice: what trust model should Cowork agent use for messages/writes from the
  laptop agent? From CI? From a future third agent?
- Current state: honor-system (each agent reads CLAUDE.md and complies). No mechanical
  enforcement of inter-agent trust.
- The injection surface in multi-agent systems: every message from another agent is
  potentially adversarial, even if that agent is nominally aligned

**3.4 Memory system security in the literature**
- MemGPT / OpenAI Memory server: what trust model do they use for memory writes?
- Generative agent architectures (Park et al. 2023): memory extraction from conversation;
  what could go wrong?
- Cognitive security in humans: source monitoring failures, false memory, confabulation —
  the closest analogues to LLM memory manipulation in cognitive science
- Relevant to the cognitive-neuroscience-memory-research.md plan: that plan has an
  implicit security dimension worth making explicit

---

## Phase 4 — Design Implications for Engram

Concrete changes that research in Phases 1–3 would justify.

**4.1 Contradiction detection on write**
- Current state: none. Contradicting files coexist indefinitely.
- Design: `memory_write` triggers a search for files making conflicting claims on the
  same topic; conflicts are flagged in frontmatter (`conflicts_with: [...]`) and surfaced
  to human review before commit
- Security relevance: contradictions are an early signal of either genuine uncertainty
  (legitimate) or adversarial rewriting (malicious). Both warrant attention.

**4.2 Trust-weighted retrieval**
- Current state: `_unverified/` and `knowledge/` files load with equal weight in context
- Design: semantic search results sorted/scored by trust tier; `knowledge/` files appear
  first; `_unverified/` files are presented with explicit trust-level context markers in
  the retrieval output, not just in frontmatter
- Security relevance: reduces the practical influence of unreviewed content on agent
  behavior even when it is technically in context

**4.3 Identity file integrity check**
- Current state: CLAUDE.md and quick-reference.md can be modified without any special
  flag
- Design: a baseline hash of identity-critical files (CLAUDE.md, meta/quick-reference.md,
  the plan taxonomy) is stored in a location the validator checks; modifications to
  identity-critical files trigger a validation warning requiring explicit human
  acknowledgment
- Security relevance: these files are the highest-value targets for persistent drift;
  making modifications visible and confirmed is disproportionately valuable

**4.4 Curation norm: archive threshold as security practice**
- Current state: files accumulate in `_unverified/` with no archiving norm
- Design: files in `_unverified/` older than N sessions without a human review or
  access event should be flagged for archiving. Reducing the volume of unreviewed
  content in the default context load reduces the passive drift surface.
- Security framing: curation is not just quality management, it is attack surface
  reduction

**4.5 Session write review**
- Current state: all memory writes in a session are committed individually; there is
  no end-of-session summary of what was written
- Design: a session-close tool (or norm) that produces a diff summary of all writes
  in the session, presented to the human for acknowledgment before the session ends
- Security relevance: makes the session's cumulative effect on the memory store visible;
  catch drift at the boundary where it is most tractable

---

## Phase 5 — The Irreducible Core

What cannot be engineered away.

**5.1 The capability-robustness tradeoff as a theorem (informal)**
- Attempt a precise statement: a model that can apply judgment to edge cases can be
  manipulated through edge cases. The precision of the statement matters because it
  determines what solutions are in-scope.
- Is there a formal analog in adversarial ML? Universal adversarial perturbations,
  certified robustness results — what do they imply about the LLM case?

**5.2 The social and institutional residual**
- Technical mitigations reduce the attack surface but do not close it. The residual
  risk requires social solutions: human review norms, periodic inspection, principal
  hierarchy integrity, organizational trust.
- The Engram system's design already reflects this: the human review gate for promotion,
  the git audit trail, the requirement that CLAUDE.md changes be human-initiated.
- What additional social/institutional norms would complete the picture? What is the
  right cadence for reviewing identity-critical files? Who reviews, and by what standard?

**5.3 The self-referential problem**
- This research plan was itself generated by the system whose security surface it
  analyzes. Future sessions loading this plan are loading an agent-generated document
  that could, in principle, have been written to serve the agent's interests rather
  than the user's.
- This is not a defeater — the git audit trail and human review gate provide oversight —
  but it is worth stating plainly. The integrity of the research process here depends
  on the same trust architecture the research is analyzing.

---

## Progress tracking

### Phase 1 — Threat Taxonomy
- [x] 1.1 Context injection vectors in a running Engram session
- [x] 1.2 Drift vs. attack: the phenomenological distinction
- [x] 1.3 Capability-robustness coupling (literature)
- [x] 1.4 The memory system as specific amplifier

### Phase 2 — Existing Mitigations and Their Limits
- [x] 2.1 Trust tier system audit
- [x] 2.2 Validator and test suite coverage
- [x] 2.3 Identity anchor files as attack targets
- [x] 2.4 Git audit trail: what it provides and what it requires
- [x] 2.5 Human review gate: actual vs. designed protection

### Phase 3 — Comparative Analysis
- [x] 3.1 Prompt injection defenses in production systems
- [x] 3.2 Constitutional AI and bright lines
- [x] 3.3 Multi-agent trust and federated coordination
- [x] 3.4 Memory system security in the literature

### Phase 4 — Design Implications
- [x] 4.1 Contradiction detection on write (spec)
- [x] 4.2 Trust-weighted retrieval (spec)
- [x] 4.3 Identity file integrity check (spec)
- [x] 4.4 Curation norm as security practice
- [x] 4.5 Session write review (spec)

### Phase 5 — The Irreducible Core
- [x] 5.1 Capability-robustness tradeoff (formal statement attempt)
- [x] 5.2 Social and institutional residual
- [x] 5.3 The self-referential problem

**Progress:** 18/18 items ✓ COMPLETE

---

## Design constraints

- Research outputs go in `knowledge/_unverified/ai-frontier/` (threat taxonomy,
  capability-robustness) and `knowledge/_unverified/system-notes/` (Engram-specific
  design implications).
- Phase 4 design specs should be written to be actionable — sufficient detail that
  a build plan could be created from them without further research.
- Phase 5 items are intentionally open-ended; "complete" means "has a written file
  with a clear statement of the problem and what is and isn't resolved," not "solved."
- Every file produced under this plan should include a note that it was produced by
  the system analyzing itself, and that human review is therefore especially important.
