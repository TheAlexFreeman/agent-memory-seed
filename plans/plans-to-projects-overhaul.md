---
source: agent-generated
origin_session: manual
created: 2026-03-20
trust: medium
type: build-plan
category: build
status: active
next_action: "Phase 0 — decide demo-app-build timing and whether question-review thresholds should be fixed or maturity-guided"
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

4. **demo-app-build** (active, optional)
   - Purpose: A concrete demonstration of the full project lifecycle.
   - The system walks through: outlining requirements → evaluating
     constraints/tradeoffs → creating a build plan → soliciting user input on
     key design decisions → building in hierarchical passes.
   - This is optional — offered during onboarding for users who want to see the
     system work end-to-end on a tangible deliverable.
   - Completion criterion: the app is built and deployed (or the user is
     satisfied with the output). All design questions resolved.

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

3. **plans/SUMMARY.md** → `projects/SUMMARY.md` with updated format.

4. **plans/ACCESS.jsonl** → `projects/ACCESS.jsonl` (file paths in entries will
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
- Collaborative question review protocol (joint calibration, not agent-only)
- Session-project interaction protocol (Frame / Flag / Check beats)
- Migration of existing plans to project containers or archive
- Hard-coded starter project templates (getting-to-know-you, system-literacy,
  general-knowledge-base, demo-app-build)
- MCP tool updates: plan tools become project-aware, new project/question tools
- Path policy updates: `projects` replaces `plans` in mutation roots
- Bootstrap updates: projects become a root-level orientation surface
- Validator updates: new validation rules for project structure
- Bootstrap/governance updates: references to plans/ become projects/
- Setup script updates: init-worktree.sh creates projects/ structure
- Human-facing documentation updates

**Out of scope (future work):**
- Onboarding skill rewrite (depends on this landing first, tracked separately)
- Semantic search across project knowledge (requires retrieval infrastructure)
- Project templates beyond the hard-coded starters (user-defined templates)
- Multi-user project sharing (requires multi-agent architecture)
- Automated cross-project question migration (manual for now)
- Relationship maturity tracking (extending system-maturity.md to track how the
  human-agent partnership evolves over time; informs protocol maturity adaptation)
- Formal protocol reference file (the session-project interaction protocol is
  described here; a standalone reference file at `meta/collaboration-protocol.md`
  could be loaded on-demand for complex tasks)

---

## Implementation phases

### Phase 0: Design review
- [ ] Review this plan with the user; confirm or adjust:
  - The project folder structure (SUMMARY.md, questions.md, `IN/`, `OUT/`, plans/)
  - The status model (active, ongoing, completed, archived)
  - The cognitive mode model (exploration, evaluation, crystallization,
    execution, verification) and whether it belongs in SUMMARY.md or a
    separate metadata surface
  - The `resolves_by` question routing taxonomy (agent-research,
    human-decision, joint-evaluation, human-only)
  - The machine-ID question format and whether validator enforcement should be
    strict enough to keep the file semantically editable by MCP tools
  - The session-project interaction protocol (Frame/Flag/Check) — is the
    activation threshold right? Should it be documented inline in the project
    structure or as a separate reference file?
  - The completion criterion (no open questions + all plans done)
  - The starter project set and their purposes
  - The migration strategy for existing completed plans
- [ ] Decide: should the demo-app-build starter project be included in the
  initial set, or added later as an enhancement?
- [x] Decide: projects are a root-level orientation feature and should replace
  top-level `plans/` in the compact startup path.
- [x] Decide: project artifacts live in `projects/<slug>/IN/` and
  `projects/<slug>/OUT/`, not a single `knowledge/` subfolder.
- [x] Decide: every question must have a machine ID and a validator-enforced
  format so question tools can edit safely.
- [ ] Decide: should the collaborative question review protocol specify a fixed
  threshold (3+ sessions dormant, 10+ open questions) or leave thresholds to
  the agent's judgment guided by the system maturity stage?

### Phase 1: Core folder structure and migration
- [ ] Create `projects/` directory with top-level SUMMARY.md and ACCESS.jsonl
- [ ] Create `projects/_archive/` and move all completed plan files there
- [ ] Migrate `plans/onboarding-redesign.md` → full project structure at
  `projects/onboarding-redesign/`
- [ ] Migrate `plans/rationalist-ai-discourse-research.md` → full project
  structure at `projects/rationalist-ai-discourse/`
- [ ] Seed questions.md for each migrated active project from their plan files'
  central questions and open design decisions
- [ ] Create `IN/` and `OUT/` folders for each migrated and starter project,
  with initial README or placeholder conventions if needed
- [ ] Create starter project skeletons (getting-to-know-you, system-literacy,
  general-knowledge-base) with SUMMARY.md and questions.md
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
- [ ] Update `meta/update-guidelines.md`: frontmatter requirements for
  project files, question-format requirements, plans-special-case note updated
- [ ] Update `README.md`: folder structure, retrieval logging, workflow
  descriptions
- [ ] Update `HUMANS/docs/` files:
  - CORE.md, GLOSSARY.md, INTEGRATIONS.md, QUICKSTART.md, MCP.md
  - agent-memory-capabilities.toml
- [ ] CHANGELOG entry

### Phase 5: Starter project content
- [ ] Write getting-to-know-you questions.md with thoughtful starter questions
  that replace the interview-style onboarding checklist
- [ ] Write system-literacy questions.md with progressive discovery questions
- [ ] Write general-knowledge-base questions.md seeded from user's known domains
- [ ] Optionally: sketch demo-app-build project structure and questions.md
- [ ] Update `meta/first-run.md` to route through starter projects instead of
  the onboarding skill
- [ ] Update or archive `skills/onboarding.md` (may be replaced entirely by the
  getting-to-know-you project flow — decision from Phase 0)

### Phase 6: Integration testing and verification
- [ ] Run the full repo validator on the restructured repo
- [ ] Run the full MCP test suite
- [ ] Verify bootstrap loads correctly with `projects/SUMMARY.md`
- [ ] Manually test project creation, question addition/resolution, and plan
  lifecycle through MCP tools
- [ ] Verify init-worktree.sh produces a valid repo structure
- [ ] Verify CI passes on both ubuntu and windows matrices

---

## Dependencies

- No external dependencies. This is an internal restructuring.
- The onboarding redesign plan (`plans/onboarding-redesign.md`) will be migrated
  into a project as part of Phase 1, then updated to align with the project model.
- The rationalist AI discourse research plan will likewise be migrated.
- The existing MCP test suite covers plan tool behavior extensively — tests will
  need updating but the coverage patterns transfer directly.

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
