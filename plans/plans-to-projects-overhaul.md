---
source: agent-generated
origin_session: manual
created: 2026-03-20
trust: medium
type: build-plan
category: build
status: active
next_action: "Phase 1 — create projects/ directory structure and migrate existing plans"
---

# Build Plan: Plans → Projects Architectural Overhaul

## Goals

Replace the top-level `plans/` folder with a `projects/` folder that elevates
projects to a first-class organizational unit and a root-level part of the
system's orientation context. A project bundles **open questions**,
**accumulated project knowledge**, and **action plans** into a single scoped
workspace. This is the system's next major abstraction: plans become artifacts
within projects rather than top-level entities.

The overhaul also introduces **open questions as a first-class feature**. Each
project carries a set of open questions — natural-language uncertainties that
range from concrete ("which database?") to open-ended ("what does the user
actually want from this?"). A project is considered **complete** when it has no
remaining open questions and all active plans have been executed. Projects that
are perpetual by nature (e.g., "build your general knowledge base") simply never
exhaust their open questions.

### Design principles

- **Projects are the unit of sustained cognitive work.** A project is not just a
  task list — it's a scoped workspace where understanding accumulates, questions
  get resolved, and plans crystallize when readiness is sufficient. Because open
  projects will be one of the most important returning-session signals,
  `projects/` belongs in the root orientation surface rather than being treated
  as a secondary container.
- **Open questions drive the lifecycle.** Questions are the heartbeat of a
  project. They provide re-entry context ("here's what we don't know yet"),
  completion criteria (all resolved), and a record of epistemic trajectory
  (resolved questions with their answers are valuable knowledge).
- **Plans are internal to projects.** A plan is one artifact among several within
  a project — it represents the "act" phase after sufficient "understand" work.
  Some projects may never need a formal plan; others may spawn several.
- **Projects can resolve in one session or remain open indefinitely.** The model
  must be lightweight enough for a quick task ("fix this bug") and structured
  enough for an open-ended effort ("build your knowledge base over months").
- **No backwards compatibility required.** Alex is the sole user. The migration
  is a clean break, not a gradual transition.
- **Cognitive complementarity is a first-class design concern.** Projects are
  collaborative workspaces shared by two fundamentally different cognitive
  architectures. The project model should make explicit who leads which kind of
  cognitive work — not as rigid role assignment but as a shared orientation that
  helps both parties contribute where they're strongest. See
  `knowledge/cognitive-science/human-llm-cognitive-complementarity.md` for the
  full analysis; the short version is that the human brings grounding,
  calibration, goal-setting, and temporal continuity, while the agent brings
  breadth, tireless computation, structural analogy, and consistency enforcement.
  Good project design routes each subtask to the better-equipped system.

### Connection to other work

- **Onboarding redesign** (`plans/onboarding-redesign.md`): The project
  architecture directly informs the updated onboarding. Hard-coded starter
  projects ("Get to know your user", "Learn this memory system") replace the
  interview-style flow with collaborative work within a project context. The
  onboarding redesign should wait for the project model to land.
- **Orient–evaluate protocol** (formerly `plans/orient-evaluate-protocol-and-complementarity-docs.md`):
  Merged into this plan as of 2026-03-21. The orient → work → evaluate pattern
  ("cognitive sandwich") at single-task, multi-session-arc, and system-level
  scales is now part of this overhaul, along with the complementarity
  documentation updates for DESIGN.md, CORE.md, GLOSSARY.md, and the knowledge
  base extension. The session-project scale (Frame/Flag/Check) was already here.
- **Developmental governance** (scratchpad thread, 2026-03-20): Alex's top-down
  governance / bottom-up knowledge accumulation frame maps naturally onto
  projects — the human sets project scope and resolves high-level questions while
  the agent accumulates knowledge and proposes plans within those bounds.
- **Cognitive complementarity** (`knowledge/cognitive-science/human-llm-cognitive-complementarity.md`):
  The project lifecycle (questions → knowledge → plan → execution → resolution)
  maps onto a natural cognitive division of labor. Questions are primarily a
  human contribution surface (goal-setting, framing). Knowledge accumulation is
  primarily an agent contribution surface (breadth, retrieval). Plan
  crystallization — the transition from "still exploring" to "ready to act" — is
  a joint calibration act. The project model makes this division legible.

---

## Problem statement

The current `plans/` folder is flat and one-dimensional. A plan is a checklist
with frontmatter — it tracks what to do, but not what's unknown, what's been
learned, or how the work relates to a broader context. This creates several
gaps:

1. **No place for open questions.** When a research project surfaces uncertainties
   that aren't actionable yet, they have nowhere to live. They end up in the
   scratchpad, disconnected from the work that generated them.

2. **No project-scoped artifact flow.** Findings from a research plan get
  written directly to `knowledge/` or `_unverified/`, and outputs from build
  plans have no canonical project home. There's no way to see "everything we
  learned while working on X" versus "everything X produced."

3. **No natural completion criterion.** A plan is "done" when all checkboxes are
   checked, but that doesn't capture whether the *understanding* is complete.
   A plan can be fully executed while the motivating questions remain unresolved.

4. **No lightweight project container.** Quick tasks ("fix this, then verify")
   don't warrant a full plan file with phases, but they'd benefit from a project
   wrapper that tracks the question ("is this bug fixed?") and its resolution.

5. **Plans don't compose.** A complex effort like "prepare the system for new
   users" naturally involves multiple plans (onboarding redesign, project model,
   documentation updates) plus shared context. The flat `plans/` folder can't
   represent this relationship.

---

## Architecture

### Folder structure

```
projects/
  SUMMARY.md                    # compact navigator (replaces plans/SUMMARY.md)
  ACCESS.jsonl                  # retrieval logging (replaces plans/ACCESS.jsonl)
  OUT/                          # global outbox: vetted artifacts for system-wide use
    SUMMARY.md                  # structured index of available artifacts by project
    <project-slug>/             # artifacts filed by originating project
      <artifact>.md

  getting-to-know-you/          # hard-coded starter project
    SUMMARY.md                  # project status, description, completion state
    questions.md                # open and resolved questions
    IN/                         # local inbox: accumulated project knowledge
    plans/                      # action plans (optional, may be empty)

  system-literacy/              # hard-coded starter project
    SUMMARY.md
    questions.md
    IN/
    plans/

  general-knowledge-base/       # perpetual project
    SUMMARY.md
    questions.md
    IN/
    plans/

  rationalist-ai-discourse/     # migrated from plans/rationalist-ai-discourse-research.md
    SUMMARY.md
    questions.md
    IN/                         # research-plan findings live here first
    plans/
      research-plan.md          # the current plan, relocated

  <user-created-projects>/
    ...
```

### Project SUMMARY.md

Each project's `SUMMARY.md` is its status dashboard. **Routing fields live in
YAML frontmatter** so tools and automations can parse them without reading the
markdown body. The markdown body carries narrative context for humans and agents
that have loaded the project for active work.

```markdown
---
source: agent-generated
origin_session: <session>
created: YYYY-MM-DD
trust: medium
type: project
status: active | ongoing | completed | archived
cognitive_mode: exploration | evaluation | crystallization | execution | verification
open_questions: N
active_plans: N
last_activity: YYYY-MM-DD
current_focus: "<one-line summary of the most important open item>"
---

# Project: <title>

## Description
<1-3 sentences: what this project is about and why it exists>

## Cognitive mode
<1-2 sentences: what the current mode means for session routing — e.g., "agent
surveying the space; human evaluation needed before we proceed">

## Artifact flow
- IN/: <what kind of accumulated research material lives here>
- OUT contributions: <what this project has published to projects/OUT/>

## Notes
<optional: context that doesn't fit in frontmatter — design rationale,
cross-project connections, things to watch>
```

The frontmatter fields are the **routing contract** — the fields that
`memory_load_project`, the top-level navigator generator, and returning-session
bootstrap all depend on. Specifically:

- `status`, `cognitive_mode`, `open_questions`, `active_plans`, `last_activity`,
  and `current_focus` are the fields the navigator table is generated from.
- An agent reading only the frontmatter (via `memory_load_project` at `summary`
  depth) can make a routing decision without parsing markdown.
- The markdown body is loaded when the agent engages with the project for active
  work — it provides context the frontmatter can't capture.

The cognitive mode field captures what *kind* of work the project currently
needs, which tells a returning agent how to engage with it:

| Cognitive mode | What's happening | Default lead |
|---|---|---|
| **exploration** | Generating questions, surveying the space | Agent (breadth, retrieval) |
| **evaluation** | Assessing options, testing against reality | Human (grounding, causal reasoning) |
| **crystallization** | Enough knowledge to plan; designing approach | Joint (agent proposes, human calibrates) |
| **execution** | Plan exists, work is procedural | Agent (consistency, tireless computation) |
| **verification** | Work done, checking quality and completeness | Joint (agent checks consistency, human checks intent) |

These modes are not strictly sequential — a project can loop back from
evaluation to exploration when evaluation reveals gaps. The mode is a routing
hint, not a state machine. The agent updates it at session end based on the
work that occurred.

### Project status model

- **active**: Finite project with defined completion criteria. Has open questions
  or active plans. Expected to reach `completed`.
- **ongoing**: Perpetual project that accumulates work over time. Never expected
  to reach `completed` but can go dormant. Examples: "build your general
  knowledge base," "get to know your user."
- **completed**: All open questions resolved, all plans executed. Terminal state
  for finite projects. The project folder persists as a record.
- **archived**: Explicitly shelved by the user. Distinguished from `completed`
  because the work may be unfinished — the user chose to stop, not because the
  questions were answered.

### questions.md — the epistemic heartbeat

Each project's `questions.md` tracks open and resolved questions. Questions are
human-readable, but every question also carries a stable machine ID so MCP
tools can reference it reliably even if the wording changes:

```markdown
---
type: questions
next_question_id: 4
---

# Open Questions

## q-001: <question text>
**Asked:** YYYY-MM-DD | **Context:** <why this question matters>
**Resolves by:** <agent-research | human-decision | joint-evaluation | human-only>
**Agent contribution:** <what the agent can do to help — even for human-only questions>

<optional elaboration, constraints, candidate answers>

---

# Resolved Questions

## q-003: <question text>
**Asked:** YYYY-MM-DD | **Resolved:** YYYY-MM-DD
**Disposition:** <answered | superseded | refactored | no-longer-applicable>
**Answer:** <the resolution — concise, linking to knowledge files if detailed>

<optional: how we got here, what changed our understanding>
```

The frontmatter is deliberately light: `type` for validation and
`next_question_id` so MCP tools can allocate IDs without parsing the file body.
This avoids a class of race conditions in question ID allocation and is
future-forward in case we want to enrich the frontmatter later (e.g., question
count caches, category tags).

Design notes on questions:
- Questions use natural language. They can be precise ("which ORM should we
  use?") or exploratory ("what are the failure modes of this approach?").
- Every question gets a stable machine ID (`q-001`, `q-002`, ...). Tools refer
  to the ID; humans read and edit the text.
- Resolved questions stay visible with their answers. The resolution history is
  itself valuable knowledge — it records the project's epistemic trajectory.
- A question can be resolved by answering it, by deciding it's no longer
  relevant, or by refactoring it into more specific sub-questions.
- Questions can reference each other and link to knowledge files. A research
  finding might resolve one question and open two more.
- Questions can be tagged with priority or category if the project warrants it,
  but this is optional — most projects won't need it.
- Format consistency should be validator-enforced so `questions.md` remains a
  governed surface rather than drifting into ad hoc note-taking.

The `resolves_by` field turns `questions.md` into a **collaboration router**.
When the agent picks up a project at session start, it can immediately see which
open questions it can advance autonomously (agent-research), which are blocked
on human input (human-decision, human-only), and which need joint work
(joint-evaluation). This is the cognitive complementarity analysis
(`knowledge/cognitive-science/human-llm-cognitive-complementarity.md` §4.4–4.5)
made operational at the question level. The four resolution types:

| `resolves_by` | What it means | Example |
|---|---|---|
| `agent-research` | Agent can make progress autonomously through survey, retrieval, or analysis. Human reviews the result. | "What are the trade-offs of optimistic vs pessimistic locking?" |
| `human-decision` | Agent can inform the decision (survey options, clarify trade-offs) but the choice requires human judgment about goals, values, or priorities. | "Should we prioritize API stability or feature velocity?" |
| `joint-evaluation` | Requires both agent research and human grounding — the agent surveys the space, the human tests conclusions against embodied experience or domain expertise. | "Is our consolidation frequency right, or does the spacing effect suggest less frequent reviews?" |
| `human-only` | Introspective or experiential question the agent cannot meaningfully research. Agent can clarify implications but cannot answer. | "Does this feature actually matter to you?" |

### Collaborative question review

Open-ended projects can accumulate many unresolved questions, and periodic
review is necessary to prevent sprawl. However, assessing which questions are
still relevant is a **calibration and goal-setting task** — exactly where the
human's cognitive contribution is irreducible (see
`metacognition/metacognition-synthesis-agent-implications.md` §5: monitoring
failures under load). The agent cannot reliably judge what the human still cares
about.

Question review should therefore be a **joint calibration checkpoint**, not an
agent-only housekeeping task. The protocol:

1. **Agent surfaces candidates.** When a project has questions that have been
   open for 3+ sessions without activity, or when the question count exceeds
   ~10, the agent flags the stalest or lowest-activity questions: "We have 12
   open questions on this project. Before diving in, let me surface the three I
   think are most stale — are any of these still live for you?"

2. **Human adjudicates.** The human decides: still relevant (keep), no longer
   relevant (resolve as "superseded" or "no longer applicable"), or needs
   refactoring (split, merge, or rephrase).

3. **Agent records the resolution.** Resolved questions move to the Resolved
  section with their machine ID and disposition preserved. Questions that the
  human confirms as still relevant keep the same machine ID and get their
  `Asked` date refreshed to prevent repeated flagging.

This is the metacognitive monitoring pattern from the trust system (externalized
calibration compensating for the agent's inability to self-assess relevance)
applied at the question level.

### Artifact flow: local inbox, global outbox

The system uses a **local-inbox / global-outbox** model that separates
project-scoped accumulation from system-wide availability:

- **`projects/<slug>/IN/`** (local inbox) — accumulated project research and
  other inward-facing context. This is where findings from research plans live
  first. `IN/` is the project-scoped understanding surface: notes, partial
  syntheses, comparisons, and other materials that matter primarily in the
  context of the project. Each project's `IN/` is its own — loaded only when
  a session is actively working on that project.

- **`projects/OUT/`** (global outbox) — vetted artifacts available for
  system-wide use, organized by originating project. When a project produces
  something useful beyond its own scope — a knowledge file ready for promotion,
  a design document, a spec, a migration guide — it goes here. The global
  outbox is the single surface an agent can scan to find everything newly
  available across all projects, without loading any individual project's
  context.

The global outbox has a **`projects/OUT/SUMMARY.md`** that serves as a hybrid
index — a "recently added" section for automations to scan what's new, plus a
full structured index grouped by project for browsing and promotion tracking:

```markdown
# Projects Outbox

## Recently added
| Date | Project | Artifact | Status |
|---|---|---|---|
| 2026-03-19 | rationalist-ai-discourse | prediction-failures.md | pending |
| 2026-03-18 | rationalist-ai-discourse | canonical-ideas-synthesis.md | promoted |
| 2026-03-15 | getting-to-know-you | profile-v1.md | promoted |

## By project

### rationalist-ai-discourse
- `rationalist-ai-discourse/canonical-ideas-synthesis.md` — synthesized
  assessment of rationalist AI canonical ideas (2026-03-18, promoted to
  knowledge/rationalist-community/)
- `rationalist-ai-discourse/prediction-failures.md` — analysis of prediction
  track record (2026-03-19, pending promotion)

### getting-to-know-you
- `getting-to-know-you/profile-v1.md` — initial user profile snapshot
  (2026-03-15, promoted to identity/)
```

The "Recently added" table is what automations read — it answers "what's new
since I last looked?" without parsing the whole file. It has a fixed depth
(last ~15 entries) so it doesn't grow unbounded. The "By project" section is
the human browsing surface and the reference for promotion tracking. Both
sections are tool-generated — the MCP tool that publishes an artifact to the
outbox updates both sections atomically.

Key design properties:

- **`IN/` is project-local accumulation.** It captures what we've learned *in
  the context of this project*. It may contain partial understanding, working
  hypotheses, or notes that only make sense within the project's scope.
- **`OUT/` is the global availability surface.** Artifacts are filed under
  `projects/OUT/<project-slug>/` so provenance is always clear. The SUMMARY.md
  index makes the outbox scannable without reading individual files.
- **Promotion to the global KB is one-way.** If an outbox artifact should
  become durable root knowledge, it gets promoted to `knowledge/` (or
  `knowledge/_unverified/`). The outbox entry is then marked as promoted in
  the SUMMARY.md index. The artifact file can remain in the outbox as a
  cross-reference or be cleaned up during periodic review.
- **Build outputs also belong in `OUT/`.** Not every project result is
  knowledge. Design documents, specs, implementation notes, and other
  deliverables that are useful beyond the project's scope go here too.
- **Cross-project references remain valid.** Files in `IN/` or `OUT/` can
  reference files in other projects or in the global KB using relative paths.
  The agent should surface cross-project relevance when it notices it.

### Plans within projects

Plans work the same way they do now — checklist-based, phase-structured, with
frontmatter tracking status and next_action. The difference is containment:

- A plan lives inside `projects/<slug>/plans/<plan-slug>.md`.
- A project can have zero, one, or many plans.
- Plans crystallize when there's enough understanding to act. A project might
  start with only questions and accumulate knowledge for several sessions before
  a plan emerges.
- The existing plan tools (`memory_create_plan`, `memory_mark_plan_item_complete`,
  `memory_update_plan_next_action`, `memory_list_plans`) will be updated to work
  within project scope.

### Hard-coded starter projects

These ship with every new Engram instance and serve as the onboarding pathway:

1. **getting-to-know-you** (ongoing)
   - Purpose: Build and maintain the user's identity profile.
   - Starter questions: "What does the user do?", "What tools/languages do they
     use?", "How do they prefer to communicate with AI?", "What are their
     intellectual interests?"
   - This subsumes the current onboarding flow. Instead of a one-shot interview,
     the identity profile is a living project that's never truly complete.

2. **system-literacy** (ongoing)
   - Purpose: Help the user understand what the memory system can do.
   - Starter questions: "Has the user seen persistent memory in action?",
     "Does the user understand the trust model?", "Has the user created or
     completed a project?"
   - Naturally resolves its questions through use. As the user works within
     other projects, system-literacy questions get answered as a side effect.

3. **general-knowledge-base** (ongoing)
   - Purpose: Accumulate broadly useful knowledge on the user's behalf.
   - Starter questions: Seeded from the user's domain (e.g., for a developer:
     "What are the user's core technical domains?", "What areas is the user
     actively learning?").
   - This is the open-ended research home. Topic-specific research that doesn't
     belong to a finite project lives here.

4. **demo-app-build** — **deferred** (Phase 0 decision, 2026-03-21). Not
   included in the initial starter set. Will be added as a future enhancement
   once the core project model is proven. Purpose when added: a concrete
   demonstration of the full project lifecycle (requirements → evaluation →
   build plan → user input on design decisions → hierarchical build passes).
   Optional — offered during onboarding for users who want to see the system
   work end-to-end on a tangible deliverable.

### Session-project interaction protocol

When a session engages with a project, there is an implicit question: "What
cognitive work should we do on this project today, and who leads each part?"
The project model already captures the *what* (current focus, open questions).
This protocol adds the *how* — a lightweight three-beat rhythm that makes the
cognitive routing legible without adding bureaucratic overhead.

**Beat 1: Frame** — The agent reads the project's SUMMARY.md (current focus +
cognitive mode) and questions.md, then proposes a session plan in 2–4 sentences.
The proposal names the cognitive task-types involved and who leads each:

> "This project is in evaluation mode. The highest-priority open question is X —
> that's a human-decision question. I've accumulated three candidate approaches
> in this project's `IN/` folder. I'll summarize the trade-offs; you make the
> call. If we resolve X, the project shifts to crystallization and we can start
> planning."

**Beat 2: Flag** — Before or during the work, the agent briefly surfaces where
its contributions are least reliable. This is the externalized metacognition
principle (see `metacognition/metacognition-synthesis-agent-implications.md`):
the agent cannot assess its own accuracy, but it *can* assess domain difficulty,
novelty, and distance from training distribution.

> "One thing to watch: my survey of locking strategies draws mostly on
> well-documented patterns. The comparison to your specific workload
> characteristics is where I'm interpolating — that's genuinely your call to
> evaluate."

This is not performative humility; it is active solicitation of the human's
calibration function, directing the human's scarce attention to where it has
the highest marginal value.

**Beat 3: Check** — At session end or a natural pause, a brief retrospective
that feeds the consolidation conversation:

> "Here's what we learned this session. I'd resolve question A with this answer
> [link]. Question B decomposed into B1 and B2 — I'll add both. The cognitive
> mode should shift from evaluation to crystallization. What did *you* find most
> important?"

The Check beat serves double duty: it improves future session routing (the agent
learns where its decompositions were miscalibrated) and it makes the session-end
consolidation a joint cognitive act rather than agent-only reflection. The
human's episodic memory and emotional salience detector identifies what matters;
the agent's breadth spots connections to existing knowledge. Together they
consolidate better than either alone.

**When the protocol fires vs. doesn't:** The three-beat pattern activates for
non-trivial project work — multi-step research, evaluation-heavy decisions,
cross-domain synthesis. It does *not* fire for quick lookups, simple file
operations, or tasks the human has already decomposed. The activation test:
would a competent collaborator pause to discuss approach before starting, or
just start? If the former, the protocol fires.

**Maturity adaptation:** In early sessions the Frame beat is explicit and the
Flag beat conservative (the agent doesn't yet know where the human's expertise
covers for its gaps). In mature partnerships, Frame can become telegraphic
("Same pattern as last time — I survey, you evaluate?") and Flag can focus on
genuinely novel risk. The system already tracks system maturity
(`meta/system-maturity.md`); extending it to track *relationship maturity*
would allow protocol behavior to evolve with the partnership.

### The orient–evaluate pattern at multiple scales

The session-project interaction protocol (Frame/Flag/Check) is the session-scale
instance of a more general orient → work → evaluate pattern. This plan extends
that pattern to three additional scales. The pattern is a behavioral convention,
not new infrastructure — it lives in protocol descriptions and governance docs,
not in folder structures or MCP tools.

**The human leads the "before" beats; the agent leads tracking; the "after"
beats are joint.** This mapping — goal-setting is human, sustained attention
is agent, calibration is joint — flows directly from the complementarity
analysis and is consistent across all scales.

#### Scale 1: Single task (minutes)

**When it fires:** Knowledge file creation, knowledge promotion, identity
updates, and any task where the agent produces a durable artifact that will be
read in future sessions. Does *not* fire for ephemeral outputs (chat responses,
quick lookups, routine ACCESS logging).

**Orient (before writing):**
The agent states in 1–2 sentences what gap this artifact fills and what its known
limitations are. This pre-registers what "good" looks like so the evaluate step
has criteria to check against.

> "Writing a knowledge file on Django middleware ordering. This fills a gap in
> the django stack coverage. I'm drawing on training data and your earlier
> conversation about request lifecycle; the production-specific ordering
> considerations are where I'm least confident."

**Evaluate (after writing):**
The agent checks the artifact against the stated orient criteria. For
agent-research artifacts, this can be brief. For joint-evaluation artifacts,
the evaluate beat explicitly invites human grounding:

> "The middleware file is written. The section on async middleware interaction
> is where I'm most likely to have causal gaps — does this match your
> production experience?"

**Complementarity mapping:** Orient: agent states the gap (breadth); human
refines (priorities). Work: agent writes (consistency). Evaluate: joint —
agent checks structural completeness; human checks grounding.

#### Scale 2: Session-project (already specified above)

Frame/Flag/Check beats, cognitive mode, `resolves_by` routing. See
"Session-project interaction protocol" above.

#### Scale 3: Multi-session arc (days to weeks)

**When it fires:** At the start of any session that continues an active project,
when the project has been worked on for 3+ sessions. Does *not* fire in the
first few sessions (not enough trajectory to assess).

**Orient (trajectory review):**
The agent briefly surfaces the project's epistemic trajectory — not just
"here's where we are" (the Frame beat already does that) but "here's how our
understanding has shifted since we started." This is the divergent/convergent
opponent-processing check: are we asking the right questions, or have we
converged prematurely?

> "We've been working on the multi-agent architecture for four sessions. We
> started with a focus on write coordination, but the last two sessions revealed
> that the real constraint is identity isolation. Two of our original five
> questions are now resolved; three remain but two have shifted significantly."

**Evaluate (trajectory assessment):**
Periodically (every 3–5 sessions on an active project, or when the human
triggers it), the agent and human jointly assess whether the project's direction
is still right. Meta-level questions: are we asking the right questions? Has the
original goal shifted? Should we reopen exploration?

**Where this lives:** As a convention in the project SUMMARY.md update protocol.
When updating a project's current focus and cognitive mode at session end, the
agent should also assess whether a trajectory review is due. Heuristic: if the
cognitive mode has changed since last session, or if 3+ sessions have elapsed
since the last trajectory note, include a trajectory observation in the Check
beat.

#### Scale 4: System level (months)

**When it fires:** During periodic review (currently every 30 days per
`meta/update-guidelines.md`).

**Orient (system value framing):**
Before running the periodic review checklist, the agent articulates what "the
system is working well" would mean for this specific user — personalized and
concrete.

**Evaluate (system value assessment):**
After the standard periodic review (freshness, anomalies, maturity signals), a
joint assessment of whether the system is earning its maintenance cost. Four
dimensions:

- **Retrieval hit rate:** Are the files that get loaded actually helping?
  (Quantitative — ACCESS.jsonl tracks this.)
- **Context rebuild savings:** Has session-start context improved?
  (Qualitative — human assessment.)
- **Knowledge base ROI:** Is time spent on curation paying off?
  (Qualitative — human assessment.)
- **Governance overhead:** Are protocols helping or hindering?
  (Mixed — agent estimates context budget; human assesses experience.)

**Where this lives:** As a new section in the periodic review checklist
(`meta/update-guidelines.md`), inserted after step 7 (governance evaluation).

### Project context loading

Loading a project into context is one of the most frequent memory reads in this
system, especially for automated sessions and returning-session routing. The
design must optimize for this path:

- **SUMMARY.md is the single-read routing surface.** A returning agent should
  be able to read one file (the project's SUMMARY.md) and know: what the project
  is, what cognitive mode it's in, what the current focus is, and whether to load
  more. This is why cognitive mode and current focus live in SUMMARY.md rather
  than being derived from questions.md.
- **questions.md is the second read.** If SUMMARY.md indicates the project needs
  active work this session, questions.md is loaded next to understand the
  specific open questions and their routing (`resolves_by`).
- **IN/ is loaded on demand.** Individual files from a project's `IN/` folder
  are loaded only when the session's work requires them, not as part of routine
  project context loading.
- **`projects/OUT/SUMMARY.md` is a cross-project scan surface.** An agent or
  automation can read this single file to see everything newly available across
  all projects, without loading any individual project's context. This makes the
  outbox particularly useful for automated sessions that need to survey what's
  changed.
- **A `memory_load_project` read tool** should be added to the MCP surface. It
  returns the project's SUMMARY.md and questions.md in a single call, optimized
  for the returning-session path. For deeper loads, an optional `depth` parameter
  can include IN/ and OUT/ file listings.
- **The top-level `projects/SUMMARY.md` navigator** is the cross-project routing
  surface. It provides enough information to decide *which* project to load,
  without loading any individual project. This file is part of the compact
  returning orientation path.

### Top-level navigator (`projects/SUMMARY.md`)

The navigator is **tool-generated from per-project frontmatter** — no anchor
blocks, no manual sync. An MCP tool reads all `projects/*/SUMMARY.md`
frontmatter, extracts the routing fields, and writes the navigator as a compact
markdown table. This eliminates the BEGIN/END anchor manipulation logic in the
current `frontmatter_utils.py`, which is the single most complex piece of
string manipulation in the MCP codebase.

```markdown
---
type: projects-navigator
generated: YYYY-MM-DD HH:MM
project_count: N
---

# Projects

| Project | Status | Mode | Open Qs | Focus | Last activity |
|---|---|---|---|---|---|
| getting-to-know-you | ongoing | exploration | 4 | What are the user's intellectual interests? | 2026-03-21 |
| system-literacy | ongoing | exploration | 3 | Has the user seen persistent memory in action? | 2026-03-21 |
| rationalist-ai-discourse | active | execution | 2 | Complete Phase 3 synthesis | 2026-03-20 |
| onboarding-redesign | active | crystallization | 5 | Finalize phase structure | 2026-03-19 |
| general-knowledge-base | ongoing | exploration | 6 | What areas is the user actively learning? | 2026-03-18 |
```

Design properties:

- **Single source of truth is per-project frontmatter.** The navigator is
  derived, never hand-edited. Any tool that updates a project's SUMMARY.md
  frontmatter should regenerate the navigator afterward.
- **The table is sorted by last_activity descending** — most recently active
  projects first. This gives returning agents the right scan order.
- **Frontmatter on the navigator itself** tracks `generated` timestamp and
  `project_count` for staleness detection. Automations can compare the
  `generated` timestamp to the most recent project's `last_activity` to check
  if the navigator is stale.
- **Agent-friendly and protocol-governed.** Because this is one of the most
  frequently loaded orientation documents, the format is strict — the table
  schema is validator-enforced, and the generation logic is a single MCP tool
  call, not ad hoc markdown assembly.
- **Replaces the current `plans/SUMMARY.md` anchor system entirely.** The
  `frontmatter_utils.py` BEGIN/END block builder, plan-block appender, and
  anchor manipulation functions are removed in favor of the table generator.

### Cross-project knowledge flow

Projects don't exist in isolation. Key mechanisms for cross-pollination:

- **Question migration.** Working on one project may surface a question that
  belongs to another. The agent should propose moving it: "This question about
  your state management preferences came up during the app build, but it really
  belongs in the getting-to-know-you project."
- **Knowledge promotion.** Project-scoped findings that prove durable get
  promoted from `OUT/` to the global KB. This is the main pipeline from project
  work to permanent knowledge.
- **Cross-references.** Project files can reference other projects' files.
  The agent should surface these connections when they're relevant.
- **The projects/SUMMARY.md navigator.** The top-level summary provides a
  cross-project view: which projects are active, what their current focus is,
  and where the highest-priority open questions live. Because projects are a
  root-level feature, this navigator becomes part of the compact returning
  orientation path, not an optional add-on.

---

## Migration plan: existing plans → projects

Since backwards compatibility is not required, the migration is a clean
restructuring:

1. **Completed plans** (the vast majority): These stay accessible as historical
   records but don't need active project containers. Options:
   - a) Create a `projects/_archive/` folder and move completed plan files there
     as-is, preserving their content and frontmatter.
   - b) Group completed plans by domain into archived project folders (e.g.,
     `projects/_archive/cognitive-science-research/plans/` collects all the
     cognitive science research plans). More organized but more work.
   - **Recommendation:** Option (a) for the initial migration. Option (b) can
     be done incrementally if the archive grows unwieldy.

2. **Active plans** (onboarding-redesign, rationalist-ai-discourse-research):
   These become projects:
   - `plans/onboarding-redesign.md` → `projects/onboarding-redesign/plans/build-plan.md`
     (plus questions.md seeded from the plan's open design decisions)
   - `plans/rationalist-ai-discourse-research.md` →
     `projects/rationalist-ai-discourse/plans/research-plan.md` (plus
     questions.md seeded from the plan's central questions)

3. **Merged plans** (orient-evaluate-protocol-and-complementarity-docs):
   Content merged into this plan (plans-to-projects-overhaul). The original
   file is archived to `projects/_archive/` for provenance.

4. **plans/SUMMARY.md** → `projects/SUMMARY.md` with updated format.

5. **plans/ACCESS.jsonl** → `projects/ACCESS.jsonl` (file paths in entries will
  need updating to reflect new locations). Project-local `IN/` and `OUT/`
  retrieval logging rules will also need to be defined.

---

## Scope decisions

**In scope:**
- New `projects/` folder structure with SUMMARY.md, questions.md, `IN/`, `OUT/`,
  and plans/ convention
- Project status model (active, ongoing, completed, archived)
- Cognitive mode field in project SUMMARY.md (exploration, evaluation,
  crystallization, execution, verification)
- `resolves_by` routing field in questions.md (agent-research, human-decision,
  joint-evaluation, human-only)
- Stable machine IDs and validator-enforced formatting for project questions
- Collaborative question review protocol with fixed thresholds (3+ sessions
  dormant, 10+ open questions)
- Session-project interaction protocol (Frame / Flag / Check beats)
- Orient–evaluate pattern at single-task, multi-session-arc, and system-level
  scales (merged from orient-evaluate-protocol plan)
- `memory_load_project` read tool optimized for the frequent project-context-
  loading path
- Migration of existing plans to project containers or archive
- Hard-coded starter project templates (getting-to-know-you, system-literacy,
  general-knowledge-base); demo-app-build deferred
- Tool-generated table navigator (`projects/SUMMARY.md`) replacing BEGIN/END
  anchor system; validator-enforced schema, sorted by last_activity
- Hybrid outbox index (`projects/OUT/SUMMARY.md`) with recent table + by-project
  structured index; tool-generated on publish
- Routing-fields-in-frontmatter convention for per-project SUMMARY.md; light
  frontmatter on questions.md with `next_question_id`
- MCP tool updates: plan tools become project-aware, new project/question tools,
  navigator generator, outbox publisher
- Path policy updates: `projects` replaces `plans` in mutation roots
- Bootstrap updates: projects become a root-level orientation surface
- Validator updates: new validation rules for project structure
- Bootstrap/governance updates: references to plans/ become projects/
- Setup script updates: init-worktree.sh creates projects/ structure
- Governance protocol updates: knowledge-creation orient–evaluate convention in
  session-checklists, system-value assessment in periodic review
- Human-facing documentation updates: new cognitive complementarity section in
  DESIGN.md, CORE.md brief addition, GLOSSARY.md new terms
- Knowledge base extension: new §6 in human-llm-cognitive-complementarity.md
  on temporal metacognition externalization

**Out of scope (future work):**
- Onboarding skill rewrite (depends on this landing first, tracked separately)
- Demo-app-build starter project (deferred from initial set, Phase 0 decision)
- Semantic search across project knowledge (requires retrieval infrastructure)
- Project templates beyond the hard-coded starters (user-defined templates)
- Multi-user project sharing (requires multi-agent architecture)
- Automated cross-project question migration (manual for now)
- Relationship maturity tracking (extending system-maturity.md to track how the
  human-agent partnership evolves over time; informs protocol maturity adaptation)
- Formal protocol reference file (the session-project interaction protocol is
  described here; a standalone reference file at `meta/collaboration-protocol.md`
  could be loaded on-demand for complex tasks)
- Purpose-driven context loading (loading decisions driven by session goals
  rather than following the manifest mechanically — architecturally significant,
  deserves its own design review)
- Quantitative context-budget monitoring (DESIGN.md item 6; the system-level
  evaluate step would benefit from actual token-cost data)
- Maturity-guided question review thresholds (fixed thresholds for now; may
  revisit if the system needs tuning as it develops)

---

## Implementation phases

### Phase 0: Design review ✓
- [x] Review this plan with the user (2026-03-21). Confirmed: folder structure,
  status model, cognitive mode in SUMMARY.md, `resolves_by` taxonomy, machine-ID
  format with validator enforcement, Frame/Flag/Check activation threshold,
  completion criterion, starter project set, flat archive migration strategy.
- [x] Decide: demo-app-build deferred from initial starter set. Will be added as
  a future enhancement once the core project model is proven.
- [x] Decide: projects are a root-level orientation feature and should replace
  top-level `plans/` in the compact startup path.
- [x] Decide: project artifacts live in `projects/<slug>/IN/` and
  `projects/<slug>/OUT/`, not a single `knowledge/` subfolder.
- [x] Decide: every question must have a machine ID and a validator-enforced
  format so question tools can edit safely.
- [x] Decide: fixed thresholds for collaborative question review (3+ sessions
  dormant, 10+ open questions). May revisit with maturity-guided thresholds
  if tuning proves necessary.
- [x] Decide: orient-evaluate-protocol plan merged into this plan. The orient–
  evaluate pattern at single-task, multi-session-arc, and system-level scales,
  plus complementarity documentation and knowledge base extension, are now
  in-scope here.
- [x] Decide: project context loading is a first-class optimization target.
  `memory_load_project` read tool added to Phase 2 scope. SUMMARY.md designed
  as a single-read routing surface.
- [x] Decide: frontmatter and summary protocols (2026-03-21):
  - Per-project SUMMARY.md: routing fields in YAML frontmatter (`status`,
    `cognitive_mode`, `open_questions`, `active_plans`, `last_activity`,
    `current_focus`); narrative context in markdown body.
  - Top-level navigator (`projects/SUMMARY.md`): tool-generated table from
    per-project frontmatter. Replaces BEGIN/END anchor system entirely.
    Sorted by last_activity descending. Validator-enforced schema.
  - Global outbox index (`projects/OUT/SUMMARY.md`): hybrid format with a
    "Recently added" table (last ~15 entries, for automations) and a
    "By project" structured index (for browsing and promotion tracking).
  - questions.md: light frontmatter with `type` and `next_question_id` for
    tool-safe ID allocation; future-forward for enrichment.

### Phase 1: Core folder structure and migration
- [ ] Create `projects/` directory with top-level SUMMARY.md and ACCESS.jsonl
- [ ] Create `projects/_archive/` and move all completed plan files there
- [ ] Migrate `plans/onboarding-redesign.md` → full project structure at
  `projects/onboarding-redesign/`
- [ ] Migrate `plans/rationalist-ai-discourse-research.md` → full project
  structure at `projects/rationalist-ai-discourse/`
- [ ] Archive `plans/orient-evaluate-protocol-and-complementarity-docs.md` →
  `projects/_archive/` (content merged into this plan; the original plan file
  is preserved for provenance)
- [ ] Seed questions.md for each migrated active project from their plan files'
  central questions and open design decisions
- [ ] Create `IN/` folders for each migrated and starter project
- [ ] Create `projects/OUT/` global outbox with SUMMARY.md index and per-project
  subdirectories for any projects that already have outbound artifacts
- [ ] Create starter project skeletons (getting-to-know-you, system-literacy,
  general-knowledge-base) with SUMMARY.md and questions.md (demo-app-build
  deferred)
- [ ] Write `projects/SUMMARY.md` with the new cross-project navigator format
- [ ] Remove the old `plans/` folder entirely

### Phase 2: MCP tool updates
- [ ] Update `path_policy.py`: replace `"plans"` with `"projects"` in
  `_RAW_MUTATION_ROOTS` and all path validation functions
- [ ] Update `plan_tools.py` → rename to `project_tools.py`:
  - `_plan_path()` → project-aware path resolution
    (`projects/<project_slug>/plans/<plan_slug>.md`)
  - `memory_create_plan` → accepts `project_id` parameter, creates plan within
    project scope
  - `memory_mark_plan_item_complete` → accepts `project_id` parameter
  - `memory_update_plan_next_action` → accepts `project_id` parameter
  - `memory_list_plans` → `memory_list_project_plans`, scoped to a project
- [ ] Add new project-level tools:
  - `memory_create_project` — creates a new project folder with SUMMARY.md,
    questions.md skeleton, and `IN/`; creates the project's subdirectory in
    `projects/OUT/` if it doesn't already exist
  - `memory_list_projects` — lists all projects with status summary
  - `memory_add_question` — adds an open question to a project's questions.md;
    allocates a stable question ID and accepts optional `resolves_by`
    (agent-research | human-decision | joint-evaluation | human-only) and
    `agent_contribution` fields
  - `memory_resolve_question` — moves a question from open to resolved by
    machine ID with answer text and optional disposition (answered |
    superseded | refactored | no-longer-applicable)
  - `memory_update_question` — updates question text or routing metadata by
    machine ID without changing the question's identity
  - `memory_load_project` — read tool optimized for the frequent project-
    context-loading path. Returns SUMMARY.md + questions.md in a single call.
    Optional `depth` parameter: `summary` (default, SUMMARY.md only),
    `questions` (SUMMARY.md + questions.md), `full` (includes IN/ file
    listing and this project's entries from projects/OUT/SUMMARY.md). This is
    one of the most frequent reads in the system — especially for automations
    and returning-session routing.
- [ ] Update `session_tools.py`: replace `"plans"` with `"projects"` in
  `_ACCESS_ROOTS` and `_REVERT_ALLOWED_TOP_LEVELS`
- [ ] Update `read_tools.py`: update directory enumeration and startup resources
  to use `projects/` as a root-level orientation feature
- [ ] Rewrite `frontmatter_utils.py`:
  - Remove all BEGIN/END anchor manipulation logic (plan-block builder,
    plan-block appender, anchor parsing). This is the single largest
    simplification in the MCP tool refactor.
  - Replace with a navigator table generator: reads all
    `projects/*/SUMMARY.md` frontmatter, extracts routing fields, writes
    `projects/SUMMARY.md` as a sorted markdown table.
  - Update anchor conventions comment to reflect the new project model.
  - Retain any frontmatter parsing/writing utilities that are still needed.
- [ ] Add `memory_publish_to_outbox` tool — writes an artifact file to
  `projects/OUT/<project-slug>/`, updates both sections of
  `projects/OUT/SUMMARY.md` (recent table + by-project index) atomically.
  Accepts optional `promotion_target` for artifacts destined for the global KB.
- [ ] Add `memory_regenerate_navigator` tool — reads all project SUMMARY.md
  frontmatter and regenerates `projects/SUMMARY.md`. Called automatically by
  any tool that modifies a project's routing frontmatter. Also callable
  manually for repair.
- [ ] Update `server.py` if there are any direct references to plans path

### Phase 3: Validation and CI updates
- [ ] Update `validate_memory_repo.py`:
  - Replace `"plans"` with `"projects"` in CONTENT_DIRS, ACCESS_DIRS, and all
    validation functions
  - Add validation for project folder structure (must contain SUMMARY.md)
  - Add validation for questions.md format (open/resolved sections, machine IDs,
    required fields, unique IDs, frontmatter with `next_question_id`)
  - Add validation for per-project `IN/` folders
  - Add validation for global `projects/OUT/` structure: SUMMARY.md index
    format, per-project subdirectories, promotion status tracking
  - Update `plans_summary_has_active_plans()` → `projects_summary_has_active_projects()`
  - Update `validate_plans_summary_shape()` → `validate_projects_summary_shape()`:
    validate navigator table schema (required columns, sort order, row count
    matches actual project count), frontmatter (`type: projects-navigator`,
    `generated` timestamp, `project_count`)
  - Validate per-project SUMMARY.md frontmatter: required routing fields
    (`type: project`, `status`, `cognitive_mode`, `open_questions`,
    `active_plans`, `last_activity`, `current_focus`)
  - Validate `projects/OUT/SUMMARY.md`: recent table format, by-project index
    format, promotion status values
- [ ] Update `initial-commit-paths.txt` to reflect new project paths
- [ ] Update `init-worktree.sh` to create `projects/` structure instead of
  `plans/`
- [ ] Run full test suite; fix any failures from the path changes
- [ ] Run validator against the restructured repo; fix any violations

### Phase 4: Bootstrap, governance, and documentation updates
- [ ] Update `agent-bootstrap.toml`: all `plans/SUMMARY.md` references →
  `projects/SUMMARY.md`; update role descriptions and root orientation order
- [ ] Update `meta/quick-reference.md`: plans/ references → projects/
- [ ] Update `meta/curation-policy.md`:
  - Folder behavioral contracts table: `plans/` row → `projects/`
  - Instruction containment rules updated for project scope
  - Add note on per-project `IN/` lifecycle and global `OUT/` promotion rules
- [ ] Update `meta/update-guidelines.md`:
  - Frontmatter requirements for project files, question-format requirements,
    plans-special-case note updated
  - Add system-value assessment step to periodic review (after step 7,
    governance evaluation). Four dimensions: retrieval hit rate, context rebuild
    savings, knowledge base ROI, governance overhead. Joint assessment — agent
    presents data, human provides calibration judgment.
- [ ] Update `meta/session-checklists.md`:
  - Add knowledge-creation orient–evaluate convention: behavioral expectation
    that durable artifacts (knowledge files, promotions, identity updates) get a
    brief orient (what gap does this fill?) and evaluate (did it fill it?) bracket.
    Activation threshold: fires on durable artifacts only, not ephemeral outputs.
  - Add multi-session trajectory review note: for returning sessions on active
    projects with 3+ sessions of history, include a brief trajectory observation
    in the greeting or Frame beat.
- [ ] Update `README.md`: folder structure, retrieval logging, workflow
  descriptions
- [ ] CHANGELOG entry

### Phase 5: Human-facing documentation updates
- [ ] Write new "Cognitive complementarity principle" section for
  `HUMANS/docs/DESIGN.md`, placed after "The dual-audience problem" in Part I:
  - The core thesis (prosthetic cognitive architecture)
  - Condensed failure-mode complementarity tables
  - Architectural-features-as-complementarity-implementations mapping table
  - The orient–evaluate pattern as temporal metacognition externalization
  - Design implications for future development
  - Cross-reference to knowledge base analysis
  - Target length: 800–1200 words
- [ ] Add brief paragraph to `HUMANS/docs/CORE.md` § "Fundamental design
  decisions" introducing the complementarity principle (3–4 sentences)
- [ ] Add glossary entries to `HUMANS/docs/GLOSSARY.md`: cognitive
  complementarity, orient–evaluate pattern, cognitive mode, `resolves_by`
  routing, Frame/Flag/Check protocol, prospective/retrospective metacognition
- [ ] Update remaining `HUMANS/docs/` files:
  - INTEGRATIONS.md, QUICKSTART.md, MCP.md
  - agent-memory-capabilities.toml
- [ ] Review all additions for tone consistency with existing DESIGN.md prose

### Phase 6: Knowledge base extension
- [ ] Update `knowledge/cognitive-science/human-llm-cognitive-complementarity.md`:
  - Add new §6: "The orient–evaluate pattern: temporal externalization of
    metacognition" — extends the analysis from spatial (trust tiers, SUMMARY
    files) to temporal (before/after brackets around cognitive work)
  - Connect to Nelson-Narens prospective vs. retrospective monitoring
  - Connect to attention synthesis's executive-function-as-context-curation
  - Revise open question #2 to note orient–evaluate provides a mechanism
  - Add open question #6: at which scales does the pattern have highest
    marginal value?
- [ ] Update `knowledge/cognitive-science/SUMMARY.md` to mention new §6
- [ ] Ensure cross-references are bidirectional: DESIGN.md → knowledge file →
  governance docs → knowledge file

### Phase 7: Starter project content
- [ ] Write getting-to-know-you questions.md with thoughtful starter questions
  that replace the interview-style onboarding checklist
- [ ] Write system-literacy questions.md with progressive discovery questions
- [ ] Write general-knowledge-base questions.md seeded from user's known domains
- [ ] Update `meta/first-run.md` to route through starter projects instead of
  the onboarding skill
- [ ] Update or archive `skills/onboarding.md` (may be replaced entirely by the
  getting-to-know-you project flow — decision from Phase 0)

### Phase 8: Integration testing and verification
- [ ] Run the full repo validator on the restructured repo
- [ ] Run the full MCP test suite
- [ ] Verify bootstrap loads correctly with `projects/SUMMARY.md`
- [ ] Manually test project creation, question addition/resolution, plan
  lifecycle, and `memory_load_project` through MCP tools
- [ ] Verify orient–evaluate conventions are present in session-checklists
  and update-guidelines without exceeding context budget (session-checklists
  addition ≤ 100 words; update-guidelines addition ≤ 200 words)
- [ ] Verify cross-references between DESIGN.md, governance docs, and
  knowledge base are bidirectional and accurate
- [ ] Verify init-worktree.sh produces a valid repo structure
- [ ] Verify CI passes on both ubuntu and windows matrices
- [ ] Dry-run the orient–evaluate convention: walk through a knowledge-file
  creation scenario, a 5-session research project, and a periodic review to
  confirm the brackets add value, not noise

---

## Dependencies

- No external dependencies. This is an internal restructuring.
- The onboarding redesign plan (`plans/onboarding-redesign.md`) will be migrated
  into a project as part of Phase 1, then updated to align with the project model.
- The rationalist AI discourse research plan will likewise be migrated.
- The orient-evaluate-protocol plan (`plans/orient-evaluate-protocol-and-complementarity-docs.md`)
  is now merged into this plan. The original file will be archived for provenance.
- The existing MCP test suite covers plan tool behavior extensively — tests will
  need updating but the coverage patterns transfer directly.
- Knowledge base files required for Phase 6: the complementarity analysis
  (`knowledge/cognitive-science/human-llm-cognitive-complementarity.md`) and
  metacognition synthesis must exist in their current form. Both are already
  written and at `trust: medium`.

## Risk assessment

**Risk: Project overhead for simple tasks.** If creating a project requires
multiple files and folders, users might resist using the system for quick tasks.
Mitigation: the MCP `memory_create_project` tool handles all scaffolding in a
single call. A minimal project is just SUMMARY.md + questions.md + empty `IN/`.
The global `projects/OUT/` directory already exists; per-project OUT
subdirectories are created on demand when the project first publishes an
artifact. The plans/ subfolder is likewise created on demand.

**Risk: Starter projects feel prescriptive.** Users who arrive with their own
agenda might find pre-seeded projects unwelcome. Mitigation: starter projects
are framed as suggestions, not requirements. The agent can say "I have a few
starter projects ready, but we can also jump straight into whatever you're
working on." The demo-app-build project is explicitly optional.

**Risk: Question sprawl.** Open-ended projects could accumulate dozens of
unresolved questions, making questions.md unwieldy. Mitigation: machine IDs and
format enforcement make the file governable by tools, and the agent should
periodically review questions for relevance (similar to the existing knowledge
freshness check). Questions that have been open for N sessions without activity
can be proposed for resolution ("still relevant?") or archival.

**Risk: `IN/` / `OUT/` boundary confusion.** If findings live in both a
project's `IN/` and the global `OUT/`, or if the outbox accumulates stale
artifacts, the distinction loses value. Mitigation: the boundary is
architectural — `IN/` is per-project (local inbox), `OUT/` is global (outbox).
An artifact moves from `IN/` to `OUT/` when it's vetted and useful beyond the
project. Promotion to the root KB is tracked in `OUT/SUMMARY.md`. Periodic
review can flag stale outbox entries. The validator enforces the structural
separation.

**Risk: MCP tool surface grows too large.** Adding project tools on top of
existing plan tools could overwhelm the tool surface. Mitigation: project tools
*replace* plan tools rather than supplementing them. `memory_create_plan` gains
a `project_id` parameter instead of creating plans at the top level. The net
tool count increase is modest (add ~4 project tools, remove 0, modify 4).

**Risk: Session-project protocol adds overhead without value.** If the
Frame/Flag/Check beats fire on every trivial interaction, the protocol becomes
noise. Mitigation: the protocol has an explicit activation threshold — it fires
only for non-trivial multi-step project work, not for quick lookups or tasks
the human has already decomposed. The cognitive mode field in SUMMARY.md
pre-computes much of the Frame beat, so the agent can route correctly from a
single-line read rather than running the full protocol each time.

**Risk: Orient–evaluate convention at single-task scale adds noise.** Every
knowledge file gets a brief orient/evaluate bracket. For routine files in
well-understood domains this may feel rote. Mitigation: the convention fires
only on durable artifacts, not ephemeral outputs. For routine files the orient
step can be a single sentence. The convention is guidance, not enforcement.

**Risk: System-level value assessment feels like a survey.** If the periodic
review asks "is this working?" every 30 days, it could feel repetitive.
Mitigation: the assessment should be personalized and specific — not "is this
working?" but "last month we built 12 knowledge files in the Django area; have
you noticed better session starts on Django tasks?" Concrete, falsifiable
questions invite genuine calibration.

**Risk: Multi-session trajectory review is hard to trigger reliably.** Unlike
periodic review (clear 30-day trigger), "3+ sessions on an active project" is
fuzzy. Mitigation: tie the trigger to the project SUMMARY.md's `Last activity`
field and cognitive mode field. If mode has changed or 3+ sessions have elapsed
without a trajectory note, the convention fires.

**Risk: DESIGN.md complementarity section is too theoretical.** Human readers
may not care about cognitive science — they want to understand how to use the
system. Mitigation: lead with practical implications (failure-mode tables,
architectural mapping); put theoretical grounding at the end.

**Risk: Question routing (`resolves_by`) becomes stale.** A question tagged
`agent-research` might turn out to need human grounding once the research
reveals unexpected complexity. Mitigation: `resolves_by` is a routing hint, not
a constraint. The agent should update it when the actual resolution path diverges
from the initial tag. The collaborative question review checkpoint provides a
natural moment for this recalibration.

## Success criteria

- All existing plan content is accessible in the new structure (migrated or
  archived)
- The MCP tool surface supports the full project lifecycle: create project →
  add questions → accumulate material in `IN/` → create plan → execute plan →
  publish vetted artifacts to `projects/OUT/` → resolve questions → complete
  project
- Starter projects provide a natural entry point for new users that replaces
  the interview-style onboarding
- The repo validator enforces project structure invariants
- CI passes on both platforms
- A quick task can be represented as a single-session project without
  disproportionate overhead
- An open-ended research effort can be represented as an ongoing project that
  accumulates work across many sessions
- The cognitive mode field provides enough routing information that a returning
  agent can propose a well-targeted session plan from SUMMARY.md alone, without
  loading the full project contents
- Projects appear as a root-level orientation surface in the compact returning
  path, replacing the old active-plans role in startup context
- Questions tagged with `resolves_by` enable the agent to distinguish between
  questions it can advance autonomously and questions blocked on human input
- Questions can be updated, resolved, and referenced semantically by stable
  machine ID rather than fragile text matching
- The session-project protocol (Frame/Flag/Check) feels like natural
  collaboration, not bureaucratic overhead — verified through manual dry-run
  with diverse task types
- `memory_load_project` returns a project's routing context (SUMMARY.md +
  questions.md) in a single call, optimized for the most frequent read path
- The orient–evaluate convention is described in session-checklists and
  update-guidelines in a way that a new agent can follow without loading
  additional reference material
- The periodic review includes a system-value assessment step that solicits
  the human's calibration judgment, not just system-health metrics
- DESIGN.md includes a coherent explanation of cognitive complementarity that
  a non-technical reader can follow
- The knowledge base analysis is extended to cover temporal metacognition
  externalization
- All cross-references between DESIGN.md, governance docs, and knowledge base
  are bidirectional and accurate
- No new always-load context budget is consumed — governance additions fit
  within existing session-checklists and update-guidelines token budgets
