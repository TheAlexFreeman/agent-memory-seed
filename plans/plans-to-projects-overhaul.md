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

  getting-to-know-you/          # hard-coded starter project
    SUMMARY.md                  # project status, description, completion state
    questions.md                # open and resolved questions
    IN/                         # research inputs and accumulated project knowledge
    OUT/                        # vetted/promotable knowledge and build outputs
    plans/                      # action plans (optional, may be empty)

  system-literacy/              # hard-coded starter project
    SUMMARY.md
    questions.md
    IN/
    OUT/
    plans/

  general-knowledge-base/       # perpetual project
    SUMMARY.md
    questions.md
    IN/
    OUT/
    plans/

  rationalist-ai-discourse/     # migrated from plans/rationalist-ai-discourse-research.md
    SUMMARY.md
    questions.md
    IN/                         # research-plan findings live here first
    OUT/                        # vetted synthesis promoted from this project
    plans/
      research-plan.md          # the current plan, relocated

  <user-created-projects>/
    ...
```

### Project SUMMARY.md

Each project's `SUMMARY.md` is its status dashboard. It contains:

```markdown
---
source: agent-generated
origin_session: <session>
created: YYYY-MM-DD
trust: medium
type: project
status: active | ongoing | completed | archived
---

# Project: <title>

## Description
<1-3 sentences: what this project is about and why it exists>

## Status
- Open questions: N
- Active plans: N
- Status: <active|ongoing|completed|archived>
- Last activity: YYYY-MM-DD

## Artifact flow
- IN/: <what kind of accumulated research material lives here>
- OUT/: <what kind of vetted/promotable artifacts live here>

## Current focus
<The most important open question or active plan item right now>

## Cognitive mode
<exploration | evaluation | crystallization | execution | verification>
<1 sentence: what this means for session routing — e.g., "agent surveying;
human evaluation needed before we proceed">
```

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
# Open Questions

## q-001: <question text>
**Asked:** YYYY-MM-DD | **Context:** <why this question matters>
**Resolves by:** <agent-research | human-decision | joint-evaluation | human-only>
**Agent contribution:** <what the agent can do to help — even for human-only questions>

<optional elaboration, constraints, candidate answers>

---

# Resolved Questions

## q-001: <question text>
**Asked:** YYYY-MM-DD | **Resolved:** YYYY-MM-DD
**Disposition:** <answered | superseded | refactored | no-longer-applicable>
**Answer:** <the resolution — concise, linking to knowledge files if detailed>

<optional: how we got here, what changed our understanding>
```

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

### Project artifact flow: `IN/` and `OUT/`

Each project has two artifact folders with distinct semantics:

- **`IN/`** — accumulated project research and other inward-facing context.
  This is where findings from research plans live first. `IN/` is the
  project-scoped understanding surface: notes, partial syntheses, comparisons,
  and other materials that matter primarily in the context of the project.
- **`OUT/`** — vetted and outward-facing artifacts. This includes knowledge that
  is ready to be promoted to the root knowledge base, plus non-knowledge
  deliverables generated by build plans such as design documents, specs,
  implementation notes, migration guides, or other outputs worth preserving as
  products of the project.

The relationship to the global knowledge base:

- **`IN/` is project-local accumulation.** It captures what we've learned *in
  the context of this project*. It may contain partial understanding, working
  hypotheses, or notes that only make sense within the project's scope.
- **`OUT/` is the staging surface for durable artifacts.** If a project result
  should become durable root knowledge, it is vetted in `OUT/` first and then
  promoted to the top-level `knowledge/` folder (or `knowledge/_unverified/` if
  it still requires human review).
- **Build outputs also belong in `OUT/`.** Not every project result is knowledge.
  Some outputs are project-specific artifacts that should remain in the project
  even after completion.
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
- **IN/ and OUT/ are loaded on demand.** Individual files from these folders are
  loaded only when the session's work requires them, not as part of routine
  project context loading.
- **A `memory_load_project` read tool** should be added to the MCP surface. It
  returns the project's SUMMARY.md and questions.md in a single call, optimized
  for the returning-session path. For deeper loads, an optional `depth` parameter
  can include IN/ and OUT/ file listings.
- **The top-level `projects/SUMMARY.md` navigator** is the cross-project routing
  surface. It provides enough information to decide *which* project to load,
  without loading any individual project. This file is part of the compact
  returning orientation path.

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
- MCP tool updates: plan tools become project-aware, new project/question tools
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
- [ ] Create `IN/` and `OUT/` folders for each migrated and starter project,
  with initial README or placeholder conventions if needed
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
  - `memory_create_project` — creates a new project folder with SUMMARY.md and
    questions.md skeleton plus `IN/` and `OUT/`
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
    `questions` (SUMMARY.md + questions.md), `full` (includes IN/ and OUT/
    file listings). This is one of the most frequent reads in the system —
    especially for automations and returning-session routing.
- [ ] Update `session_tools.py`: replace `"plans"` with `"projects"` in
  `_ACCESS_ROOTS` and `_REVERT_ALLOWED_TOP_LEVELS`
- [ ] Update `read_tools.py`: update directory enumeration and startup resources
  to use `projects/` as a root-level orientation feature
- [ ] Update `frontmatter_utils.py`: update anchor conventions comment and any
  hardcoded `plans/` references
- [ ] Update `server.py` if there are any direct references to plans path

### Phase 3: Validation and CI updates
- [ ] Update `validate_memory_repo.py`:
  - Replace `"plans"` with `"projects"` in CONTENT_DIRS, ACCESS_DIRS, and all
    validation functions
  - Add validation for project folder structure (must contain SUMMARY.md)
  - Add validation for questions.md format (open/resolved sections, machine IDs,
    required fields, unique IDs)
  - Add validation for `IN/` and `OUT/` folder semantics and access logging
    expectations
  - Update `plans_summary_has_active_plans()` → `projects_summary_has_active_projects()`
  - Update `validate_plans_summary_shape()` → `validate_projects_summary_shape()`
  - Validate project SUMMARY.md frontmatter (type: project, valid status)
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
  - Add note on `IN/` and `OUT/` lifecycle and promotion rules
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
single call. A minimal project is still lightweight, but it now has a clear
artifact model: SUMMARY.md + questions.md plus empty `IN/` and `OUT/` folders.
The plan subfolder can still be created on demand.

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

**Risk: `IN/` / `OUT/` drift creates duplication or confusion.** If findings live
in both `IN/` and `OUT/`, or if `OUT/` mixes promotable knowledge with random
build artifacts, the distinction loses value. Mitigation: `IN/` is for project
accumulation, `OUT/` is for vetted or outward-facing artifacts, and promotion to
the global KB is one-way. Once promoted, the project file can be replaced with a
cross-reference. The validator and documentation should make the boundary crisp.

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
  produce vetted artifacts in `OUT/` → resolve questions → complete project
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
