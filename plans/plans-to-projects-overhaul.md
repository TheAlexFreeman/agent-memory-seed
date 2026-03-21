---
source: agent-generated
origin_session: manual
created: 2026-03-20
trust: medium
type: build-plan
category: build
status: active
next_action: "Phase 0 — review design decisions with user before implementation"
---

# Build Plan: Plans → Projects Architectural Overhaul

## Goals

Replace the top-level `plans/` folder with a `projects/` folder that elevates
projects to a first-class organizational unit. A project bundles **open
questions**, **accumulated knowledge**, and **action plans** into a single scoped
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
  get resolved, and plans crystallize when readiness is sufficient.
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

---

## Problem statement

The current `plans/` folder is flat and one-dimensional. A plan is a checklist
with frontmatter — it tracks what to do, but not what's unknown, what's been
learned, or how the work relates to a broader context. This creates several
gaps:

1. **No place for open questions.** When a research project surfaces uncertainties
   that aren't actionable yet, they have nowhere to live. They end up in the
   scratchpad, disconnected from the work that generated them.

2. **No project-scoped knowledge.** Findings from a research plan get written
   directly to `knowledge/` or `_unverified/`, losing their connection to the
   project that produced them. There's no way to see "everything we learned
   while working on X."

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
    knowledge/                  # project-scoped findings
    plans/                      # action plans (optional, may be empty)

  system-literacy/              # hard-coded starter project
    SUMMARY.md
    questions.md
    knowledge/
    plans/

  general-knowledge-base/       # perpetual project
    SUMMARY.md
    questions.md
    knowledge/
    plans/

  rationalist-ai-discourse/     # migrated from plans/rationalist-ai-discourse-research.md
    SUMMARY.md
    questions.md
    knowledge/                  # will receive output files instead of _unverified/
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

## Current focus
<The most important open question or active plan item right now>
```

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

Each project's `questions.md` tracks open and resolved questions:

```markdown
# Open Questions

## <question-slug>
**Asked:** YYYY-MM-DD | **Context:** <why this question matters>

<optional elaboration, constraints, candidate answers>

---

# Resolved Questions

## <question-slug>
**Asked:** YYYY-MM-DD | **Resolved:** YYYY-MM-DD
**Answer:** <the resolution — concise, linking to knowledge files if detailed>

<optional: how we got here, what changed our understanding>
```

Design notes on questions:
- Questions use natural language. They can be precise ("which ORM should we
  use?") or exploratory ("what are the failure modes of this approach?").
- Resolved questions stay visible with their answers. The resolution history is
  itself valuable knowledge — it records the project's epistemic trajectory.
- A question can be resolved by answering it, by deciding it's no longer
  relevant, or by refactoring it into more specific sub-questions.
- Questions can reference each other and link to knowledge files. A research
  finding might resolve one question and open two more.
- Questions can be tagged with priority or category if the project warrants it,
  but this is optional — most projects won't need it.

### Project-scoped knowledge

Each project has an optional `knowledge/` subfolder for findings that are
specific to the project's context. This is the "messy, in-progress
understanding" space. The relationship to the global knowledge base:

- **Project knowledge is provisional.** It captures what we've learned *in the
  context of this project*. It may contain partial understanding, working
  hypotheses, or notes that only make sense within the project's scope.
- **Promotion to global KB.** When a project-scoped finding is durable and
  generally applicable, it gets promoted to the top-level `knowledge/` folder
  (or `knowledge/_unverified/` if it hasn't been human-reviewed). The promotion
  follows the same trust pipeline as any other knowledge file.
- **Cross-project references.** Project knowledge files can reference files in
  other projects or in the global KB using relative paths. The agent should
  surface cross-project relevance when it notices it.

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

### Cross-project knowledge flow

Projects don't exist in isolation. Key mechanisms for cross-pollination:

- **Question migration.** Working on one project may surface a question that
  belongs to another. The agent should propose moving it: "This question about
  your state management preferences came up during the app build, but it really
  belongs in the getting-to-know-you project."
- **Knowledge promotion.** Project-scoped findings that prove durable get
  promoted to the global KB. This is the main pipeline from project work to
  permanent knowledge.
- **Cross-references.** Project files can reference other projects' files.
  The agent should surface these connections when they're relevant.
- **The projects/SUMMARY.md navigator.** The top-level summary provides a
  cross-project view: which projects are active, what their current focus is,
  and where the highest-priority open questions live.

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
   need updating to reflect new locations).

---

## Scope decisions

**In scope:**
- New `projects/` folder structure with SUMMARY.md, questions.md convention
- Project status model (active, ongoing, completed, archived)
- Migration of existing plans to project containers or archive
- Hard-coded starter project templates (getting-to-know-you, system-literacy,
  general-knowledge-base, demo-app-build)
- MCP tool updates: plan tools become project-aware, new project/question tools
- Path policy updates: `projects` replaces `plans` in mutation roots
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

---

## Implementation phases

### Phase 0: Design review
- [ ] Review this plan with the user; confirm or adjust:
  - The project folder structure (SUMMARY.md, questions.md, knowledge/, plans/)
  - The status model (active, ongoing, completed, archived)
  - The completion criterion (no open questions + all plans done)
  - The starter project set and their purposes
  - The migration strategy for existing completed plans
- [ ] Decide: should the demo-app-build starter project be included in the
  initial set, or added later as an enhancement?
- [ ] Decide: should project-scoped knowledge live in `projects/<slug>/knowledge/`
  or should projects just reference files in the global KB? (Plan recommends
  project-scoped knowledge with promotion pipeline, but this adds complexity.)

### Phase 1: Core folder structure and migration
- [ ] Create `projects/` directory with top-level SUMMARY.md and ACCESS.jsonl
- [ ] Create `projects/_archive/` and move all completed plan files there
- [ ] Migrate `plans/onboarding-redesign.md` → full project structure at
  `projects/onboarding-redesign/`
- [ ] Migrate `plans/rationalist-ai-discourse-research.md` → full project
  structure at `projects/rationalist-ai-discourse/`
- [ ] Seed questions.md for each migrated active project from their plan files'
  central questions and open design decisions
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
    questions.md skeleton
  - `memory_list_projects` — lists all projects with status summary
  - `memory_add_question` — adds an open question to a project's questions.md
  - `memory_resolve_question` — moves a question from open to resolved with
    answer text
- [ ] Update `session_tools.py`: replace `"plans"` with `"projects"` in
  `_ACCESS_ROOTS` and `_REVERT_ALLOWED_TOP_LEVELS`
- [ ] Update `read_tools.py`: update directory enumeration to use `projects/`
- [ ] Update `frontmatter_utils.py`: update anchor conventions comment and any
  hardcoded `plans/` references
- [ ] Update `server.py` if there are any direct references to plans path

### Phase 3: Validation and CI updates
- [ ] Update `validate_memory_repo.py`:
  - Replace `"plans"` with `"projects"` in CONTENT_DIRS, ACCESS_DIRS, and all
    validation functions
  - Add validation for project folder structure (must contain SUMMARY.md)
  - Add validation for questions.md format (open/resolved sections)
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
  `projects/SUMMARY.md`; update role descriptions
- [ ] Update `meta/quick-reference.md`: plans/ references → projects/
- [ ] Update `meta/curation-policy.md`:
  - Folder behavioral contracts table: `plans/` row → `projects/`
  - Instruction containment rules updated for project scope
  - Add note on project-scoped knowledge lifecycle
- [ ] Update `meta/update-guidelines.md`: frontmatter requirements for
  project files, plans-special-case note updated
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
single call. A minimal project is just SUMMARY.md + questions.md — two small
files. The plan subfolder and knowledge subfolder are created on demand, not
upfront.

**Risk: Starter projects feel prescriptive.** Users who arrive with their own
agenda might find pre-seeded projects unwelcome. Mitigation: starter projects
are framed as suggestions, not requirements. The agent can say "I have a few
starter projects ready, but we can also jump straight into whatever you're
working on." The demo-app-build project is explicitly optional.

**Risk: Question sprawl.** Open-ended projects could accumulate dozens of
unresolved questions, making questions.md unwieldy. Mitigation: the agent
should periodically review questions for relevance (similar to the existing
knowledge freshness check). Questions that have been open for N sessions without
activity can be proposed for resolution ("still relevant?") or archival.

**Risk: Project-scoped knowledge creates duplication.** If findings live in both
project knowledge and the global KB, there's a maintenance burden. Mitigation:
the promotion pipeline is one-way — project knowledge gets promoted *to* the
global KB, not mirrored. Once promoted, the project file can be replaced with
a cross-reference. The agent should prefer promotion over duplication.

**Risk: MCP tool surface grows too large.** Adding project tools on top of
existing plan tools could overwhelm the tool surface. Mitigation: project tools
*replace* plan tools rather than supplementing them. `memory_create_plan` gains
a `project_id` parameter instead of creating plans at the top level. The net
tool count increase is modest (add ~4 project tools, remove 0, modify 4).

## Success criteria

- All existing plan content is accessible in the new structure (migrated or
  archived)
- The MCP tool surface supports the full project lifecycle: create project →
  add questions → accumulate knowledge → create plan → execute plan → resolve
  questions → complete project
- Starter projects provide a natural entry point for new users that replaces
  the interview-style onboarding
- The repo validator enforces project structure invariants
- CI passes on both platforms
- A quick task can be represented as a single-session project without
  disproportionate overhead
- An open-ended research effort can be represented as an ongoing project that
  accumulates work across many sessions
