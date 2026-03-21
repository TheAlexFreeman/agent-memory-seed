---
source: agent-generated
origin_session: manual
created: 2026-03-21
trust: medium
type: build-plan
category: build
status: completed
next_action: "Merged into plans/plans-to-projects-overhaul.md (2026-03-21)"
---

# Build Plan: Orient–Evaluate Protocol and Cognitive Complementarity Documentation

## Goals

Propagate the **orient → work → evaluate** pattern (the "cognitive sandwich")
across the memory system's protocols at every operational scale, and deepen
cognitive complementarity coverage in the system's design documentation so that
future agents and human readers understand *why* the system's protocols are
structured as collaborations between two different cognitive architectures.

This plan treats the session-project interaction protocol (Frame/Flag/Check)
already added to the plans-to-projects overhaul as the session-scale instance of
a more general pattern. The work here extends that pattern to three additional
scales — single-task, multi-session arc, and system-level — and updates the
design and governance docs to make complementarity a visible architectural
principle rather than an implicit one.

### Design principles

- **The orient–evaluate pattern is a habit, not an architecture.** It lives in
  behavioral contracts and conventions, not in new folder structures or MCP
  tools. The changes are primarily to documentation and protocol descriptions,
  not to code.
- **Complementarity routing is the system's executive function.** The cognitive
  complementarity analysis (`knowledge/cognitive-science/human-llm-cognitive-complementarity.md`)
  establishes that context curation is the framework's analog of executive
  control. This plan makes that principle explicit in the governance docs so it
  shapes how agents engage with the system, not just how files are organized.
- **Lightweight beats comprehensive.** Each scale's orient–evaluate bracket
  should cost at most a few sentences of context per instance. If a protocol
  can't justify its context budget, it shouldn't exist (per DESIGN.md §
  "Measure what you mandate").
- **The human leads the "before" beats; the agent leads tracking; the "after"
  beats are joint.** This mapping — goal-setting is human, sustained attention
  is agent, calibration is joint — flows directly from the complementarity
  analysis and should be consistent across all scales.

### Connection to other work

- **Plans-to-projects overhaul** (`plans/plans-to-projects-overhaul.md`): The
  session-project interaction protocol (Frame/Flag/Check), cognitive mode field,
  `resolves_by` routing, and collaborative question review are all instances of
  the orient–evaluate pattern at the session-project scale. This plan extends
  the pattern to the other three scales without duplicating that work.
- **Onboarding redesign** (`plans/onboarding-redesign.md`): The onboarding
  redesign's "show don't tell" principle applies here — the orient–evaluate
  pattern should be demonstrated in the first session, not explained abstractly.
- **Cognitive complementarity analysis**
  (`knowledge/cognitive-science/human-llm-cognitive-complementarity.md`): The
  theoretical foundation. This plan operationalizes §4 (implications for
  collaboration framework design) into concrete protocol changes.
- **Metacognition synthesis**
  (`knowledge/cognitive-science/metacognition/metacognition-synthesis-agent-implications.md`):
  The orient–evaluate pattern is externalized prospective and retrospective
  metacognition. The trust system is externalized monitoring. This plan connects
  both into a coherent story.

---

## Problem statement

The memory system already embodies cognitive complementarity in its
*architecture* — trust tiers are externalized metacognition, SUMMARY files are
chunking operations, the consolidation pipeline mirrors hippocampal replay. But
the system's *protocols* — session checklists, periodic review, knowledge
creation, context loading — don't explicitly leverage complementarity. They
describe *what* the agent should do, but not *how the human and agent should
divide cognitive labor* to do it well.

This creates three specific gaps:

1. **No orient–evaluate bracket around knowledge creation.** The agent writes
   knowledge files with no structured moment of stating what gap the file fills
   (orient) or evaluating whether it actually filled that gap (evaluate). The
   curation policy governs format but not epistemic quality. This is where the
   metacognition synthesis predicts fluency-induced overconfidence — the IOED
   (illusion of explanatory depth) operating at the file level.

2. **No purpose-driven context loading.** The session routing in
   `quick-reference.md` specifies *what* to load but not *why*. Context curation
   is the system's executive function (per the complementarity analysis), yet
   the loading manifest is followed mechanically rather than driven by the
   session's purpose. The human's knowledge of what matters today — the
   executive-control signal — isn't part of the loading decision.

3. **No system-level "is this actually working?" evaluation.** The periodic
   review checks system *health* (freshness, anomalies, thresholds) but not
   system *value* — whether the knowledge base is making the human more
   effective. This is a calibration judgment only the human can make, and the
   current periodic review doesn't solicit it.

4. **Complementarity is invisible in the design docs.** DESIGN.md covers the
   dual-audience problem (human vs. agent readers) but not the deeper
   complementarity between human and agent *cognition*. A reader can understand
   the system's architecture without ever encountering the idea that it's
   designed as a prosthetic cognitive architecture compensating for the specific
   failure modes of each partner. This limits both adoption (users don't
   understand why the system works the way it does) and development (contributors
   don't know which design decisions serve complementarity).

---

## Architecture

### The orient–evaluate pattern at four scales

The orient → work → evaluate structure applies at four operational scales. The
session-project scale is already specified in the plans-to-projects overhaul;
this plan addresses the other three plus the documentation layer.

#### Scale 1: Single task (minutes)

**When it fires:** Knowledge file creation, knowledge promotion, identity
updates, and any task where the agent produces a durable artifact that will be
read in future sessions. Does *not* fire for ephemeral outputs (chat responses,
quick lookups, routine ACCESS logging).

**Orient (before writing):**
The agent states in 1–2 sentences what gap this artifact fills and what its known
limitations are. This is a Flag beat in miniature — it pre-registers what "good"
looks like so the evaluate step has criteria to check against.

Example:
> "Writing a knowledge file on Django middleware ordering. This fills a gap in
> the django stack coverage — we have views and models but not middleware. I'm
> drawing on training data and your earlier conversation about request lifecycle;
> the production-specific ordering considerations are where I'm least confident."

**Evaluate (after writing):**
The agent checks the artifact against the stated orient criteria. For
agent-research artifacts, this can be brief and agent-internal. For
joint-evaluation artifacts, the evaluate beat explicitly invites human grounding:

> "The middleware file is written. It covers the standard ordering and the
> exception-handling edge case you mentioned. The section on async middleware
> interaction is where I'm most likely to have causal gaps — does this match your
> production experience?"

**Complementarity mapping:**
- Orient: agent states the gap (breadth of awareness); human refines if needed
  (goal-setting, priorities)
- Work: agent writes (consistency, retrieval, tireless computation)
- Evaluate: joint — agent checks structural completeness; human checks grounding

**Where this lives in the system:** Described as a behavioral convention in the
knowledge-creation section of `meta/session-checklists.md` (or its successor in
the projects model). Not a separate file — it's a refinement of existing
protocol, not a new one.

#### Scale 2: Session-project (covered by plans-to-projects overhaul)

Frame/Flag/Check beats, cognitive mode, `resolves_by` routing. See
`plans/plans-to-projects-overhaul.md` § "Session-project interaction protocol."
No additional work needed here beyond what that plan already specifies.

#### Scale 3: Multi-session arc (days to weeks)

**When it fires:** At the start of any session that continues an active project,
when the project has been worked on for 3+ sessions. Does *not* fire in the
first few sessions of a project (there isn't enough trajectory to assess).

**Orient (trajectory review):**
The agent briefly surfaces the project's epistemic trajectory — not just
"here's where we are" (the Frame beat already does that) but "here's how our
understanding has shifted since we started." This is the divergent/convergent
opponent-processing check from the Vervaeke relevance-realization corpus: are
we asking the right questions, or have we converged prematurely?

Example:
> "We've been working on the multi-agent architecture for four sessions. We
> started with a focus on write coordination, but the last two sessions revealed
> that the real constraint is identity isolation, not write locking. Two of our
> original five questions are now resolved; three remain but two of them have
> shifted significantly from how we first framed them."

**Evaluate (trajectory assessment):**
Periodically (every 3–5 sessions on an active project, or when the human
triggers it), the agent and human jointly assess whether the project's direction
is still right. This is specifically about *meta-level* questions: are we asking
the right questions? Has the original goal shifted? Are we converging or should
we reopen exploration?

Example:
> "Looking at the trajectory: we set out to design multi-agent write
> coordination. The work has evolved toward a broader agent-identity architecture
> that includes writes as one concern among several. Should we update the
> project's scope to reflect this, or is the write-coordination framing still
> the right container?"

**Complementarity mapping:**
- Orient: agent reconstructs the trajectory (breadth of recall across sessions,
  no vigilance decrement); human provides episodic salience ("this moment in
  session 3 was the real turning point")
- Evaluate: human leads (goal-setting, calibration — is this project still
  serving my actual needs?); agent contributes pattern detection (are the
  questions converging or diverging?)

**Where this lives in the system:** As a convention in the project SUMMARY.md
update protocol — when updating a project's current focus and cognitive mode at
session end, the agent should also assess whether a trajectory review is due. A
lightweight heuristic: if the project's cognitive mode has changed since last
session, or if 3+ sessions have elapsed since the last trajectory note, include
a trajectory observation in the session's Check beat.

#### Scale 4: System level (months)

**When it fires:** During periodic review (currently every 30 days per
`meta/update-guidelines.md`).

**Orient (system value framing):**
Before running the periodic review checklist, the agent articulates what "the
system is working well" would mean for this specific user. This is personalized
— for a developer, "working well" means reducing context-rebuild time and
catching knowledge gaps; for a researcher, it means surfacing cross-domain
connections and maintaining a reliable literature base.

**Evaluate (system value assessment):**
After the standard periodic review (freshness, anomalies, maturity signals),
a joint assessment of whether the system is earning its maintenance cost. This
is the question the current periodic review doesn't ask: "Is this knowledge base
actually making your work better, or is it just accumulating?"

Concrete evaluation dimensions:
- **Retrieval hit rate:** Are the files that get loaded actually helping?
  (Quantitative — ACCESS.jsonl already tracks this.)
- **Context rebuild savings:** Has session-start context improved? Does the
  agent arrive at useful work faster than it would without the memory system?
  (Qualitative — human assessment.)
- **Knowledge base ROI:** Is the time spent on knowledge curation paying off
  in better collaboration? (Qualitative — human assessment.)
- **Governance overhead:** Are the protocols helping or hindering? Is the
  agent spending too much context on system maintenance vs. user work?
  (Mixed — agent can estimate context budget usage; human assesses subjective
  experience.)

**Complementarity mapping:**
- Orient: joint — agent proposes personalized value criteria (breadth of
  awareness of the system's state); human confirms or adjusts (goal-setting —
  what does "working well" mean to me right now?)
- Evaluate: human leads (calibration — only the human can say whether the
  system is genuinely improving their work); agent contributes data (retrieval
  stats, context budget estimates, coverage metrics)

**Where this lives in the system:** As a new section in the periodic review
checklist (`meta/update-guidelines.md` § "Periodic review"), inserted after
the current step 7 (governance evaluation) and before step 8 (folder structure).

---

### Design documentation updates

#### DESIGN.md: New section on cognitive complementarity

Add a new section to `HUMANS/docs/DESIGN.md` Part I (Design Philosophy) after
the current "The dual-audience problem" section. Title: **"The cognitive
complementarity principle."**

This section should cover:

1. **The core thesis.** The memory system is not just a data store — it is a
   prosthetic cognitive architecture that compensates for the specific failure
   modes of both human and LLM cognition. This is the design principle that
   explains *why* the system's features are structured the way they are.

2. **The failure-mode complementarity table.** Condensed from the full analysis
   in `knowledge/cognitive-science/human-llm-cognitive-complementarity.md` —
   human failure modes the LLM compensates for, and vice versa. This gives
   readers an intuitive understanding of why the partnership works.

3. **Architectural features as complementarity implementations.** A mapping
   table connecting system features to the complementarity function they serve:
   - Trust tiers → externalized metacognition (compensating for LLM calibration
     deficit)
   - SUMMARY files → chunking operations (compensating for human working memory
     limits)
   - Session routing → attentional control (compensating for LLM's absent
     executive function)
   - Consolidation pipeline → episodic-to-semantic conversion (compensating for
     LLM's absent learning mechanism)
   - Decay thresholds → functional forgetting (compensating for LLM's inability
     to forget irrelevant information)

4. **The orient–evaluate pattern.** How the system uses temporal bracketing of
   cognitive work to externalize metacognition at every scale, and how each
   bracket is designed to route cognitive labor to the system (human or agent)
   best equipped to perform it.

5. **Design implications.** How this principle should guide future development
   decisions: when adding a new feature, ask "which cognitive system's failure
   mode does this compensate for?" and "does the protocol route the work to the
   right system?"

**Audience note:** DESIGN.md is a human-facing document (never loaded by agents).
It can be as expansive and well-explained as needed. The agent-facing
implications are captured in the governance docs (session-checklists,
update-guidelines, quick-reference) per the dual-audience separation.

#### CORE.md: Brief complementarity mention

Add a short paragraph to `HUMANS/docs/CORE.md` § "Fundamental design decisions"
(after the existing decisions) briefly introducing the complementarity principle
and pointing to DESIGN.md for the full treatment. Keep it to 3–4 sentences.

#### GLOSSARY.md: New terms

Add glossary entries for: cognitive complementarity, orient–evaluate pattern,
cognitive mode, `resolves_by` routing, Frame/Flag/Check protocol. Brief
definitions with cross-references to the relevant design and governance docs.

---

## Scope decisions

**In scope:**
- Orient–evaluate behavioral conventions at single-task, multi-session-arc, and
  system-level scales
- Updates to `meta/session-checklists.md`: knowledge-creation orient–evaluate
  convention
- Updates to `meta/update-guidelines.md`: system-value assessment in periodic
  review
- New section in `HUMANS/docs/DESIGN.md`: cognitive complementarity principle
- Brief addition to `HUMANS/docs/CORE.md`
- New glossary entries in `HUMANS/docs/GLOSSARY.md`
- Updates to `knowledge/cognitive-science/human-llm-cognitive-complementarity.md`:
  new §6 covering the orient–evaluate pattern as temporal externalization of
  metacognition (extending the existing open questions)
- CHANGELOG entry

**Out of scope (handled by plans-to-projects overhaul):**
- Session-project interaction protocol (Frame/Flag/Check)
- Cognitive mode field in project SUMMARY.md
- `resolves_by` routing in questions.md
- Collaborative question review protocol
- MCP tool changes for projects

**Out of scope (future work):**
- Purpose-driven context loading (the idea that loading decisions should be
  driven by session goals rather than following the manifest mechanically). This
  is architecturally significant — it would change how `quick-reference.md`
  routing works — and deserves its own design review. Noted here as a direction
  the orient–evaluate principle points toward.
- Quantitative context-budget monitoring (DESIGN.md item 6). The system-level
  evaluate step would benefit from actual token-cost data, but building that
  instrumentation is separate work.
- Relationship maturity tracking (noted in plans-to-projects overhaul as future
  work; informs how the orient–evaluate pattern's verbosity adapts over time).

---

## Implementation phases

### Phase 0: Design review
- [ ] Review this plan with the user; confirm or adjust:
  - The four-scale model (single-task, session-project, multi-session arc,
    system-level) — is this the right decomposition?
  - The activation thresholds for each scale — are they calibrated correctly?
    (Single-task: fires on durable artifacts only. Multi-session arc: fires
    after 3+ sessions. System-level: fires on periodic review.)
  - The complementarity mapping at each scale — does the human/agent/joint
    division feel right?
  - The scope boundary with the plans-to-projects overhaul — is the division
    clean?
- [ ] Decide: should the single-task orient–evaluate convention apply to all
  knowledge files, or only to files being promoted from `_unverified/` to the
  main knowledge base? (Plan recommends all durable artifacts, but this could
  be narrowed to reduce overhead.)
- [ ] Decide: should the system-level value assessment be a formal section in
  `meta/update-guidelines.md` or a lighter-weight convention described in
  `meta/session-checklists.md`? (Plan recommends update-guidelines for
  authority; session-checklists for discoverability.)
- [ ] Decide: how much of the complementarity analysis from the knowledge base
  should be surfaced in DESIGN.md? (Plan recommends a condensed version — the
  failure-mode tables and the architectural mapping — not the full 200-line
  analysis.)

### Phase 1: Governance protocol updates

These are the agent-facing changes — updates to the files agents actually read
during sessions.

- [ ] Update `meta/session-checklists.md` § "Session end":
  - Add a knowledge-creation orient–evaluate convention between the current
    chat-summary and reflection-note steps. Describe it as a behavioral
    expectation, not a rigid checklist item. Include the activation threshold
    (fires on durable artifacts: knowledge files, promotions, identity updates)
    and a brief worked example.
  - Add a note that when writing knowledge files mid-session (not just at
    session end), the same orient–evaluate discipline applies.
- [ ] Update `meta/update-guidelines.md` § "Periodic review":
  - Add a new step 7.5 (between current step 7 "Governance evaluation" and
    step 8 "Folder structure"): **System value assessment.**
  - Describe the four evaluation dimensions (retrieval hit rate, context rebuild
    savings, knowledge base ROI, governance overhead).
  - Specify that this is a joint assessment — the agent presents data, the human
    provides the calibration judgment.
  - Note that this step is qualitative and brief (not a formal ROI analysis) —
    the goal is to solicit the human's "is this working?" signal, which is
    the irreducible human calibration function applied at the system level.
- [ ] Update `meta/session-checklists.md` § "Session start":
  - Add a note that for returning sessions on active projects with 3+ sessions
    of history, the agent should include a brief trajectory observation in its
    greeting or Frame beat — not as a separate step, but as an enrichment of
    the existing "greet with continuity" instruction.
- [ ] Review changes for consistency with `meta/quick-reference.md` compact
  bootstrap contract — ensure no new always-load overhead is introduced.

### Phase 2: Human-facing documentation updates

These are the human-facing changes — DESIGN.md and companion docs that agents
never load.

- [ ] Write the new "Cognitive complementarity principle" section for
  `HUMANS/docs/DESIGN.md`, placed after "The dual-audience problem" in Part I:
  - The core thesis (prosthetic cognitive architecture)
  - Condensed failure-mode complementarity tables (from the knowledge base
    analysis, trimmed to the most illustrative examples)
  - Architectural-features-as-complementarity-implementations mapping table
  - The orient–evaluate pattern as temporal metacognition externalization
  - Design implications for future development
  - Cross-reference to `knowledge/cognitive-science/human-llm-cognitive-complementarity.md`
    for the full analysis
  - Target length: 800–1200 words (expansive is fine — this is human-only)
- [ ] Add a brief paragraph to `HUMANS/docs/CORE.md` § "Fundamental design
  decisions" introducing the complementarity principle (3–4 sentences, pointing
  to DESIGN.md for full treatment)
- [ ] Add glossary entries to `HUMANS/docs/GLOSSARY.md`:
  - Cognitive complementarity
  - Orient–evaluate pattern (cognitive sandwich)
  - Cognitive mode (exploration, evaluation, crystallization, execution,
    verification)
  - `resolves_by` routing
  - Frame/Flag/Check protocol
  - Prospective metacognition / retrospective metacognition
- [ ] Review all additions for tone consistency with existing DESIGN.md prose
  (technical but readable, concrete examples, no jargon without definition)

### Phase 3: Knowledge base extension

- [ ] Update `knowledge/cognitive-science/human-llm-cognitive-complementarity.md`:
  - Add a new §6: "The orient–evaluate pattern: temporal externalization of
    metacognition." This extends the analysis from spatial (trust tiers,
    SUMMARY files) to temporal (before/after brackets around cognitive work).
  - Connect to Nelson-Narens prospective vs. retrospective monitoring
    (from the metacognition subfolder)
  - Connect to the attention synthesis's executive-function-as-context-curation
    principle
  - Revise open question #2 ("Can externalized metacognition become
    self-improving?") to note that the orient–evaluate pattern provides a
    mechanism — the evaluate step generates calibration data that can improve
    future orient steps
  - Add an open question #6: "At which scales does the orient–evaluate pattern
    have the highest marginal value? Is single-task bracketing worth its
    overhead, or does the session-project scale capture most of the benefit?"
- [ ] Update `knowledge/cognitive-science/SUMMARY.md` to mention the new §6
  and the orient–evaluate pattern as a key concept.
- [ ] Ensure cross-references are consistent: the new DESIGN.md section points
  to the knowledge file; the knowledge file points to the governance docs where
  the pattern is operationalized; the governance docs point to the knowledge
  file for theoretical grounding.

### Phase 4: Verification

- [ ] Review all changed files for internal consistency:
  - Do the governance docs (session-checklists, update-guidelines) describe the
    same pattern the knowledge file analyzes?
  - Do the human-facing docs (DESIGN.md, CORE.md, GLOSSARY.md) accurately
    summarize what the governance docs specify?
  - Are cross-references bidirectional and accurate?
- [ ] Verify that no new always-load files were introduced — all changes are to
  existing files or to human-only docs that agents never load.
- [ ] Verify context budget impact: estimate the token cost of the additions to
  session-checklists and update-guidelines. The session-checklists addition
  should be ≤ 100 words; the update-guidelines addition should be ≤ 200 words.
  If either exceeds this, consider moving detail to an on-demand reference.
- [ ] Dry-run the orient–evaluate convention mentally:
  - Single-task: walk through a knowledge-file creation scenario. Does the
    orient–evaluate bracket add value or just noise?
  - Multi-session arc: walk through a 5-session research project. Does the
    trajectory review surface useful meta-level observations?
  - System-level: walk through a periodic review. Does the value assessment
    produce actionable information?
- [ ] CHANGELOG entry

---

## Dependencies

- **Plans-to-projects overhaul** (`plans/plans-to-projects-overhaul.md`): The
  session-project scale is handled there. This plan assumes that overhaul will
  land — if it doesn't, the session-project protocol described here would need
  to be incorporated into this plan instead. The two plans should be implemented
  in either order without conflict, since they touch different files.
- **Knowledge base files:** The complementarity analysis and metacognition
  synthesis must exist in their current form. Both are already written and at
  `trust: medium`.
- No MCP tool changes. No validator changes. No code changes.

## Risk assessment

**Risk: Orient–evaluate convention at single-task scale adds noise.** Every
knowledge file gets a 2-sentence preamble and a 2-sentence review. For routine
files this may feel rote. Mitigation: the convention fires only on durable
artifacts (knowledge files, promotions, identity updates), not on chat
responses or ephemeral outputs. For routine files in well-understood domains,
the orient step can be a single sentence. The convention is guidance, not
enforcement — agents should exercise judgment about when the full bracket adds
value vs. when a lighter touch suffices.

**Risk: System-level value assessment feels like a survey.** If the periodic
review asks "is this system working for you?" every 30 days, it could feel
repetitive and extract agreement without genuine reflection. Mitigation: the
assessment should be personalized and specific — not "is this working?" but
"last month we built 12 knowledge files in the Django area; have you noticed
better session starts on Django tasks?" Concrete, falsifiable questions invite
genuine calibration.

**Risk: DESIGN.md complementarity section is too theoretical.** Human readers
browsing the docs may not care about cognitive science — they want to understand
how to use the system. Mitigation: lead with the practical implications (the
failure-mode tables, the architectural mapping) and put the theoretical
grounding at the end. Use the same "show, don't tell" principle the onboarding
redesign follows.

**Risk: Multi-session trajectory review is hard to trigger reliably.** Unlike
periodic review (which has a clear 30-day trigger), "3+ sessions on an active
project" is a fuzzy threshold — agents may not track session counts per project.
Mitigation: tie the trigger to the project SUMMARY.md's `Last activity` field
and the cognitive mode field. If the cognitive mode has changed since the last
session, or if the project has been active for 3+ sessions without a trajectory
observation in the Check beat, the convention fires. The plans-to-projects
overhaul's MCP tools can support this tracking.

**Risk: Cross-reference web becomes too dense.** This plan introduces
bidirectional references between governance docs, human-facing docs, and
knowledge files. If every file points to every other file, the cross-reference
graph becomes noise. Mitigation: follow the existing "justify once, reference
everywhere" principle from DESIGN.md. The knowledge file is the theoretical
home; the governance docs are the operational home; the human-facing docs are
the explanatory home. Each references the others but doesn't duplicate their
content.

## Success criteria

- The orient–evaluate convention is described in session-checklists and
  update-guidelines in a way that a new agent can follow without loading
  additional reference material
- The periodic review includes a system-value assessment step that solicits
  the human's calibration judgment, not just system-health metrics
- DESIGN.md includes a coherent explanation of cognitive complementarity that
  a non-technical reader can follow, connecting the system's architectural
  features to the specific cognitive failure modes they compensate for
- The knowledge base analysis is extended to cover temporal metacognition
  externalization (the orient–evaluate pattern) as a complement to the existing
  spatial externalization analysis (trust tiers, SUMMARY files)
- All cross-references are bidirectional and accurate
- No new always-load context budget is consumed — all governance additions fit
  within the existing session-checklists and update-guidelines token budgets
- The conventions feel like natural good practice, not bureaucratic overhead —
  verified through mental dry-runs with diverse task types
