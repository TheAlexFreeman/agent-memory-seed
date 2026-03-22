---
source: agent-generated
origin_session: manual
created: 2026-03-20
trust: medium
type: build-plan
category: build
status: active
next_action: "Phase 0 — finalize design decisions with user before implementation"
---

# Build Plan: Collaborative Onboarding Redesign

## Goals

Replace the current interview-style onboarding (`core/memory/skills/onboarding.md`) with a
collaborative first-session experience that teaches the system's capabilities
through use rather than explanation. The new flow should feel like a first working
session with a capable partner, not a registration form.

The redesigned onboarding should satisfy three objectives simultaneously:

1. **Profile discovery.** The agent learns who the user is — role, tools,
   communication style, interests — with the same fidelity as the current flow.
2. **Capability demonstration.** The user experiences what the system can do for
   them — persistent memory, knowledge building, trust governance, cross-session
   continuity — through concrete examples, not abstract description.
3. **Relationship calibration.** Both parties establish a working dynamic: what
   the user expects from the agent, how the agent communicates, and what
   "collaboration" means for this particular partnership.

### Design principles

- **Show, don't tell.** Every system capability is demonstrated through use
  during the session, not explained in a preamble.
- **Value before structure.** The user should experience a useful outcome
  before they understand the governance framework. Progressive disclosure
  applies to onboarding, not just to the repo layout.
- **The profile is a byproduct, not the product.** The user's first-session
  experience should be "we did something useful together" — with the profile
  as a natural artifact of that collaboration, not the primary deliverable.
- **Respect diverse use cases.** The flow must work for a developer debugging
  code, a researcher exploring a question, a writer drafting a document, and
  a non-technical user managing projects — without requiring use-case-specific
  branching in the skill procedure itself.
- **Preserve governance invariants.** All existing security guarantees —
  proposal-before-write for identity files, trust-level enforcement, instruction
  containment — must be maintained. The onboarding UX changes; the safety model
  does not.

### Theoretical grounding

The knowledge base provides direct support for this design:

- **Cognitive complementarity** (`cognitive-science/human-llm-cognitive-complementarity.md`):
  The onboarding should establish the human-LLM partnership by exercising both
  parties' strengths — the human's grounding, goal-setting, and calibration
  abilities alongside the agent's breadth, working-memory extension, and
  consistency enforcement. The first session should feel like a collaboration,
  not a service interaction, because that's what the system is designed to be.

- **Relevance realization** (`cognitive-science/relevance-realization/relevance-realization-synthesis.md`):
  Vervaeke's opponent-processing model (convergent/divergent balance) applies
  to the onboarding itself. The current interview is over-convergent: it follows
  a fixed checklist. The redesign should allow divergent exploration (following
  the user's interests) while maintaining convergent structure (ensuring the
  profile covers the necessary categories). The pacing note in the current skill
  gestures at this but the linear step structure works against it.

- **Metacognition and calibration** (`cognitive-science/metacognition/metacognition-synthesis-agent-implications.md`):
  The trust system is externalized metacognition. Onboarding is the first
  opportunity to make this visible. When the agent says "I'm saving this with
  high trust because you told me directly," it's teaching the user the
  metacognitive framework through a concrete instance.

- **Episodic memory formation** (`cognitive-science/memory/tulving-episodic-semantic-distinction.md`,
  `cognitive-science/cognitive-science-synthesis.md`):
  The first session is the system's founding episode. It should be memorable
  and distinctive — a reference point both parties can return to — not a
  generic intake. Tulving's autonoetic consciousness research suggests that
  vivid, personally significant episodes are the ones that persist and
  ground future retrieval.

- **The dual-audience problem** (`HUMANS/docs/DESIGN.md`):
  The onboarding skill file is read by agents, but the onboarding *experience*
  is the user's first encounter with the system. The skill must give the agent
  enough structure to deliver a consistently good experience without making the
  conversation feel scripted.

---

## Problem statement

The current onboarding skill (`core/memory/skills/onboarding.md`) is well-governed but
one-dimensional. It follows a sequential interview pattern: introduce system →
discover role → discover preferences → discover tools → open-ended capture →
write profile. This has three weaknesses:

1. **The user learns nothing about the system's capabilities.** The "wow, it
   remembered" moment is deferred to session two. If session one felt like
   a form, there may not be a session two.

2. **The information flow is asymmetric.** The agent asks; the user answers.
   This sets the wrong expectation for the ongoing relationship, which should
   be genuinely collaborative.

3. **The profile is context-free.** Traits discovered through interview
   ("I prefer TypeScript") are lower-quality than traits discovered through
   collaboration ("when we debugged that together, you reached for TypeScript
   and explained your reasoning — that tells me something richer about your
   relationship to the language").

---

## Architecture

### Phase structure of the new onboarding

The redesigned flow has four phases. Phases are not rigid steps — they represent
the natural arc of a collaborative first session. The agent should move fluidly
between them based on conversational cues.

**Phase A: Warm start (1–2 exchanges)**
Brief, human-first introduction. The agent explains it has persistent memory in
one sentence, acknowledges this is a first meeting, and asks what the user is
working on or interested in exploring. If a starter template exists, the agent
mentions it ("I see you picked the software developer profile — let's see how
well it fits as we work together").

The goal is to establish rapport and identify a **seed task** — a real problem,
question, or project the user brings to the session.

**Phase B: Collaborative work on the seed task (the bulk of the session)**
The agent and user work together on whatever the user brought. This is the
core of the redesigned onboarding: genuine collaboration on a real task. As
they work, the agent:

- **Demonstrates memory inline.** When the user reveals a preference or piece
  of context, the agent explicitly notes it: "Got it — I'll remember that for
  next time." This makes the memory system tangible through repeated small
  demonstrations.
- **Shows trust governance in action.** When the agent looks something up or
  synthesizes information, it can briefly note the trust distinction: "I found
  some relevant context. Since I pulled this from an external source, I'd flag
  it as unverified — you'd need to confirm it before it becomes part of your
  permanent knowledge base."
- **Discovers the profile organically.** Role, tools, communication style,
  expertise level, and anti-preferences emerge naturally from collaborative
  work. The agent tracks these silently against the discovery checklist
  (same categories as current steps 2–4) and only asks direct questions for
  uncovered gaps.

**Phase C: Reflection and profile (2–3 exchanges)**
After the collaborative work reaches a natural pause, the agent shifts to
reflection:

1. **Reflect back the working portrait.** "Based on how we worked together,
   here's what I've learned about you." Present the discovered traits.
2. **Fill gaps.** Check the discovery checklist — if major categories are still
   empty, ask targeted questions. Keep this brief; the collaborative work should
   have covered most of it.
3. **Capability tour (tailored).** Based on what the agent now knows about the
   user, highlight 2–3 capabilities that would be most relevant to them. For a
   developer: "I can track multi-session debugging context and remember your
   codebase conventions." For a researcher: "I can build you a persistent
   knowledge base on any topic." For a writer: "I can maintain style preferences
   and continuity across sessions." Optionally demonstrate one in microcosm.
4. **Propose and confirm the profile.** Same governance as current step 6:
   proposal → user review → explicit confirmation → write.

**Phase D: Forward bridge (1 exchange)**
End with a preview of session two and a handoff:

- Explain briefly what the next session will feel like ("I'll greet you with
  what I know and pick up any open threads").
- Offer `core/memory/working/scratchpad/USER.md` as a place to leave notes for next time.
- If the seed task has follow-up work, suggest creating a plan ("Want me to
  track this as a multi-session project?").
- Greet the user as a now-known person, not a new stranger.

### Discovery checklist (carried from current skill)

The agent uses this as a post-hoc audit, not a script. After Phase B, check
coverage:

- [ ] Role and responsibilities
- [ ] Active projects / current focus
- [ ] Domain expertise (what they know well, what's new)
- [ ] Communication preferences (detail level, tone, format)
- [ ] Anti-preferences (what annoys them in AI interactions)
- [ ] Primary languages/frameworks
- [ ] Editor/IDE and tools
- [ ] Collaboration context (solo, team, open source)

Items naturally surfaced during collaboration get tagged `[observed]`.
Items explicitly asked get tagged `[observed]` if stated directly,
`[tentative]` if uncertain.

### Inline memory demonstrations

These are the moments during Phase B where the agent makes the memory system
visible. They should feel natural, not rehearsed. Examples:

| Moment | What the agent says | What it teaches |
|---|---|---|
| User mentions a tool or preference | "Noted — I'll remember you prefer X for future sessions." | Memory persists across sessions |
| User corrects the agent | "Good correction. I'm saving that — it's the kind of thing that makes our future interactions better." | Corrections are high-value memory |
| Agent uses external information | "I pulled this from [source]. In my system, external info starts as unverified until you confirm it." | Trust tiers and quarantine |
| Agent writes to the profile | "I'm marking this as high-trust because you told me directly. If I'd inferred it, it would start lower." | Trust levels and provenance |
| Collaborative work produces a useful artifact | "Want me to save this to your knowledge base? It'll be available next session." | Knowledge persistence |

Not all of these will occur in every onboarding. The agent should use whichever
are natural to the conversation. The goal is 3–5 such moments across the session.

---

## Scope decisions

**In scope:**
- Rewrite of `core/memory/skills/onboarding.md` with the new phase structure
- Updated quality criteria and anti-patterns
- Compatibility with existing template-confirmation flow (Phase A absorbs step 0)
- Compatibility with read-only platform export (Phase C/D produce the same
  export format)
- Updated `core/governance/first-run.md` if the silent setup sequence needs adjustment
- CHANGELOG entry

**Out of scope (future work):**
- Use-case-specific onboarding variants (developer, researcher, writer) — the
  single skill should handle diverse users through the seed-task mechanism
- Changes to `setup.sh`, `setup.html`, or profile templates — those are
  pre-onboarding and work fine
- Expanded starter profiles (DESIGN.md item 4) — complementary but separate
- The `/health` diagnostic skill (DESIGN.md item 5) — worth building but
  not coupled to onboarding
- Multi-user onboarding — requires architectural work beyond this plan's scope

---

## Implementation phases

### Phase 0: Design review
- [ ] Review this plan with the user; confirm or adjust the phase structure
- [ ] Decide whether to preserve the current onboarding as a fallback (e.g.,
      `core/memory/skills/_archive/onboarding-v1.md`) or replace it outright
- [ ] Confirm that the inline-demonstration approach doesn't conflict with any
      platform-specific constraints (e.g., read-only environments where the
      agent can't actually demonstrate writes)

### Phase 1: Core skill rewrite
- [ ] Rewrite `core/memory/skills/onboarding.md` with the four-phase structure
- [ ] Preserve all governance invariants (proposal-before-write, frontmatter
      requirements, trust assignment rules, explicit confirmation)
- [ ] Preserve read-only platform compatibility (export format)
- [ ] Preserve template-confirmation compatibility (Phase A absorbs current
      step 0)
- [ ] Write the inline-demonstration guidance as a reference table within the
      skill, not as a rigid script
- [ ] Update the discovery checklist to serve as a post-hoc audit tool
- [ ] Update quality criteria: add "user has experienced at least 2–3 concrete
      capability demonstrations" alongside the existing "5–10 durable traits"
- [ ] Update anti-patterns: add "Don't explain capabilities abstractly when you
      can demonstrate them in context" and "Don't let the seed task consume the
      entire session — leave time for reflection and profile confirmation"

### Phase 2: Supporting file updates
- [ ] Update `core/governance/first-run.md` if the silent setup sequence needs changes
      (likely minimal — the bootstrap steps are the same; only the interactive
      phase changes)
- [ ] Update `core/memory/skills/SUMMARY.md` to reflect the new skill description
- [ ] Verify that the existing session-recording infrastructure (chat archival,
      reflection notes, ACCESS logging) works with the new flow without changes
- [ ] Write CHANGELOG entry

### Phase 3: Validation
- [ ] Dry-run the new onboarding flow manually: walk through a simulated
      first session with a developer persona, a researcher persona, and a
      non-technical persona. Verify that:
  - The seed-task mechanism produces natural profile discovery
  - The discovery checklist achieves adequate coverage
  - The inline demonstrations feel organic, not scripted
  - The governance invariants are maintained
  - The read-only export path still works
- [ ] Verify the skill file stays within the 300–1000 word guideline from
      `core/governance/curation-policy.md` (the current skill is ~930 words; the new
      one may need to be slightly longer given the added demonstration
      guidance — flag if it exceeds 1200 words)
- [ ] Run the repo validator to confirm no structural regressions

---

## Dependencies

- Current `core/memory/skills/onboarding.md` (will be replaced or archived)
- `core/governance/first-run.md` (may need minor updates)
- `core/governance/update-guidelines.md` § "Change categories" (skill modification is
  protected-tier — requires explicit user approval)
- `HUMANS/tooling/onboard-export-template.md` (export format preserved)

## Risk assessment

**Risk: Seed task dominates the session.** If the user brings a complex problem,
Phase B could consume the entire session without leaving time for Phases C–D.
Mitigation: the skill should include timing guidance — after ~60% of expected
session length, begin transitioning to Phase C regardless of task completion.
The task can continue in session two (and that itself demonstrates continuity).

**Risk: Non-technical users don't have a seed task.** Not everyone arrives with
a coding problem. Mitigation: the Phase A prompt should be broad ("What are you
working on, or what would you like to explore?"). For users who don't have
something specific, the agent can offer to demonstrate a capability directly
("Want me to research a topic you're curious about and show you how the
knowledge base works?").

**Risk: Capability demonstrations feel forced.** If the agent shoehorns in
trust-level explanations during a debugging session, it breaks flow.
Mitigation: the demonstration table is a menu of opportunities, not a checklist.
The agent should use only the ones that arise naturally. Minimum target is 2–3
demonstrations, not all of them.

**Risk: Skill file becomes too long.** The new skill has more guidance than
the current one (demonstration table, timing notes, phase transitions).
Mitigation: keep the core procedure concise; move detailed examples and
rationale to a companion reference file if needed (following the
checklist-skill separation pattern from `DESIGN.md`).

## Success criteria

- A new user's first session produces both a useful collaborative outcome
  (the seed task) AND a complete identity profile
- The user can name at least 2 specific things the system can do for them
  by the end of session one (without having read any documentation)
- Profile quality is at least as good as the current flow: 5–10 durable
  traits, all properly tagged, with explicit confirmation before any write
- All governance invariants pass the repo validator
- The skill works on read-only platforms via the existing export mechanism
