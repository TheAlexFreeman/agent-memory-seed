---
created: 2026-03-18
session: chats/2026/03/18/chat-006
type: research-and-design
status: draft — awaiting Alex review
---

# LLM Agent Loops and Proactive Memory: Research Note

## Motivation

The current memory system is reactive. Every useful thing it does is in response to a user request: load context when asked, write knowledge when asked, run periodic review when asked. Sessions are episodic — the agent starts with the compact manifest, serves the user, and closes. Nothing happens in between. Nothing is synthesized across sessions. Nothing is surfaced proactively.

This note covers: (1) what agent loop research says about proactive behavior, (2) what specifically is missing in the current architecture, and (3) concrete design proposals for adding a proactive dimension.

---

## What LLM agent loop research says

### The basic perception-action loop

The simplest agent loop is: observe → reason → act → observe. ReAct (Yao et al., 2022) made this explicit for language models: interleave "Thought" (internal reasoning) and "Action" (tool call or output) steps, with "Observation" steps feeding results back. The key insight is that making the reasoning explicit in the output constrains the action space and dramatically improves reliability on multi-step tasks.

The current memory system's session structure already resembles a ReAct loop: the agent reads context (observe), reasons about the user's request (think), performs memory operations (act), and reads results back. What it lacks is a *between-session* loop — any cycle that runs without the user present.

### Generative Agents (Park et al., 2023)

The most directly relevant architectural work. Park et al. built simulated social agents with:

1. **Memory stream** — a timestamped log of raw observations ("Alex asked about LSTM gradients", "Alex expressed frustration with the plan file format")
2. **Retrieval** — embedding-based retrieval over the memory stream, weighted by recency, importance, and relevance
3. **Reflection** — a periodic process that reads the memory stream and synthesizes higher-level insights: "Alex is primarily focused on practical production infrastructure this month, not theory"
4. **Planning** — using reflections to generate intentions that guide future behavior
5. **Action** — executing plans, which creates new observations, closing the loop

The key contribution was **reflection**: the agent periodically asked itself "What are the most important things I've noticed recently?" and synthesized the answers into higher-level beliefs. Without reflection, the agent was good at episodic recall but could not form generalizations.

The memory system has a good version of (1) in ACCESS.jsonl and scratchpad entries, and a weak version of (2) in compact manifest loading. It has (3) only as a 30-day periodic review triggered by the user. It has (4) in `plans/`. It has (5) in session execution. But the loop is open: there is no automatic pipeline from observation → reflection → planning that runs independently of user-triggered sessions.

### Reflexion (Shinn et al., 2023)

Agents that maintain a "verbal reinforcement" memory: after each action cycle, the agent writes a short summary of what went wrong or what it learned, and reads this at the start of the next cycle. The agent's behavior improves across episodes not because weights change but because the reflection notes accumulate in the context window.

The current system does something like this with `scratchpad/CURRENT.md` and session `reflection.md` files. But these are written for the *agent's own future reference*, not synthesized into actionable suggestions for the user or the next agent instance. The reflection currently answers "what did I notice?" — it does not answer "what should I do about it?" or "what should I surface to Alex?"

### SOAR / cognitive architectures inspiration

Older cognitive architectures (SOAR, ACT-R) distinguish between working memory (active session context), long-term declarative memory (facts), long-term procedural memory (skills), and episodic memory (past experiences). They also distinguish between reactive (stimulus-response) and deliberate (goal-directed) action.

The memory system maps reasonably well onto this:
- Working memory = session context window
- Declarative = `knowledge/`
- Procedural = `skills/`
- Episodic = `chats/` + `scratchpad/CURRENT.md`

What's missing from the cognitive architecture model is **deliberate background processing**: in SOAR, the system chunked experience into new rules and patterns continuously, not just when triggered. The closest analog in the current system is periodic review, but that's a heavyweight manual process, not a lightweight continuous one.

### The Voyager pattern (Wang et al., 2023)

Voyager (Minecraft agent) used a curriculum discovery loop: after each episode, the agent proposed the next skill to learn based on what it had accomplished and what remained out of reach. The system was proactive about its own skill development — it did not wait for external prompting to decide what to work on next.

This pattern is relevant to the research plans system: rather than waiting for Alex to say "do some React research", a proactive system would notice the current plan state, observe which plans have the most value relative to idle time, and generate a ranked suggestion of "this is what I think would be most valuable to work on next session."

---

## What's specifically missing in the current architecture

### Gap 1: No semantic observation layer

ACCESS.jsonl records *what files were retrieved* and a helpfulness score. It does not record *what was noticed* — the semantic content of the agent's observations during a session. If the agent notices "Alex keeps asking about Celery beat scheduling and we have no knowledge file on it", this should be recorded somewhere. Currently it would either be silently lost or land in `scratchpad/CURRENT.md` if the agent remembers to write it.

There is no formal "things I noticed" log that the system could synthesize into proactive suggestions.

### Gap 2: Reflection produces no actionable queue

The session `reflection.md` format records: what went well, what didn't, gaps, and helpfulness scores. But it produces no structured output that future agent instances can act on without re-reading the full reflection. The valuable observations are buried in prose. There is no mechanism that says "here are three specific things worth doing next session, ranked by value."

### Gap 3: Session start is entirely passive

The current session-start checklist is: load context, check write access, run metadata probes, greet user. The agent surfaces what the user was working on last time (continuity), but does not surface anything the agent has identified as worth discussing. The agent has no voice at session start — it only responds.

A proactive agent would show up to the session with 1-2 things it thought of between sessions.

### Gap 4: Plans are push-only

Plans are worked on when explicitly directed. There is no mechanism by which a high-priority plan that has been idle for two weeks generates any kind of nudge. The plan system is entirely pull-based: Alex looks at plans when she wants to, and the agent works on them when told.

### Gap 5: Knowledge gaps are not tracked

The system knows what knowledge it has. It does not track what knowledge it suspects is missing. If multiple sessions involve questions in a domain with no knowledge file, this pattern is visible in ACCESS.jsonl (low helpfulness on adjacent files, or missing entries entirely), but no mechanism synthesizes this into "we should probably write a file about X."

---

## Design proposals

These are presented as distinct layers that could be added independently. They are ordered from lowest to highest architectural overhead.

---

### Proposal 1: Structured "things to surface" list in CURRENT.md

**Scope:** Minimal. No new files or schemas.

**Mechanism:** Add a `## To surface next session` section to `scratchpad/CURRENT.md`. During session end, when the agent writes reflection notes, it also writes 1-5 structured bullet points in this section:

```
## To surface next session

- [nudge] Django async plan has been idle 14 days; worth asking if still a priority
- [gap] Three sessions touched Celery beat scheduling; no knowledge file exists — suggest writing one
- [research] TanStack Router file written but not reviewed; worth flagging for promotion
```

Each item has a type tag (`nudge`, `gap`, `research`, `review`) and is short enough to scan in one pass.

**Session start change:** Add one step to the session-start checklist: after loading context, check `CURRENT.md` for items in the `## To surface next session` section, and surface the top 1-2 naturally in the greeting or early in the session.

**Why this is lightweight:** No new files, no new schemas. It reuses an existing file with an explicit new section. The agent's behavior change is a single additional step at session end (write to this section) and a single additional step at session start (scan and surface).

**Risk:** Items accumulate if never cleared. Mitigation: clear surfaced items from the list when they are addressed or become stale (older than N sessions).

---

### Proposal 2: Semantic observation appends during sessions

**Scope:** New semantic layer on top of ACCESS.jsonl.

**Mechanism:** During session end, the agent writes short semantic observations to a new `scratchpad/observations.md` file. Unlike ACCESS.jsonl (which records file access events), this records inferences:

```
## 2026-03-18

- Alex spent most of the session on AI history research — pattern of sustained interest in AI theory/genealogy (not just practical tooling)
- The Django async plan is flagged as next but has not been touched in 3 sessions — possible deprioritization signal
- Celery beat scheduling has come up tangentially in 2 sessions but no knowledge file exists for it
- Alex's phrasing "keep it up" suggests satisfaction with research pace and quality
```

These are distinct from `scratchpad/CURRENT.md` (which is working notes) and `reflection.md` files (which are session-level). They are a persistent semantic stream that builds across sessions.

**Reflection synthesis:** During periodic review (or via a lightweight scheduled process), the agent reads recent observations and synthesizes them into belief updates: identity traits to consider, knowledge gaps to research, plans to advance, patterns to act on.

**Why this adds value over existing structures:** The existing `reflection.md` files are written *per session* and are not designed to be read cumulatively. The observation stream is designed to be read in aggregate — the value is in patterns across sessions, not individual entries.

**Cost:** One additional file to maintain, with a small write at session end. The file is read only during periodic review or when the task specifically involves "what have I noticed recently."

---

### Proposal 3: Proactive suggestion queue (formal structure)

**Scope:** New file + new session-start behavior.

**Mechanism:** A dedicated `scratchpad/proactive-queue.md` with a structured schema:

```markdown
# Proactive Queue

Items the agent wants to surface proactively. Cleared when addressed or expired.

## Active items

| Priority | Type | Item | Added | Expires |
|---|---|---|---|---|
| high | gap | Write `knowledge/_unverified/django/celery-beat-scheduling.md` — came up in 3 sessions | 2026-03-18 | 2026-04-18 |
| medium | nudge | Django async plan idle 14 days; verify still prioritized | 2026-03-18 | 2026-04-01 |
| low | review | AI history files ready for trust review when Alex has time | 2026-03-18 | 2026-06-01 |
```

**Session-start change:** The compact returning manifest adds one step: after loading context, scan `proactive-queue.md` for high-priority items and surface the top 1 in the greeting. Medium items are surfaced if there's a natural opportunity. Low items are held.

**Item lifecycle:** Items are added by the agent at session end. Items are cleared when: addressed explicitly in a session, or expired. The expiry date prevents the queue from accumulating noise.

**Why this is better than Proposal 1:** Explicit structure means future agent instances can scan the queue without reading prose. Priority and expiry fields make the queue self-maintaining. The type field enables filtering ("just show me knowledge gaps" vs "just show me nudges").

**Architectural note:** This is a new file and involves a change to the session-start checklist, which is technically a `meta/` change (protected tier). Would require Alex's approval to implement.

---

### Proposal 4: Reflection pass as a lightweight background process

**Scope:** New scheduled automation + new reflections folder.

**Mechanism:** A scheduled task (building on the existing automation infrastructure) that runs independently of user sessions, perhaps every 3-7 days:

1. Read recent entries from `scratchpad/observations.md` (Proposal 2)
2. Read plan states from `plans/SUMMARY.md`
3. Read ACCESS.jsonl entry counts and helpfulness scores
4. Synthesize into a short `reflections/YYYY-MM-DD.md` file with:
   - **Belief updates**: things I've revised my understanding about
   - **Proactive suggestions**: ranked list of things worth doing
   - **Patterns noticed**: cross-session themes that might inform future work
5. Write high-priority suggestions to `scratchpad/proactive-queue.md` (Proposal 3)

**The key innovation:** The agent is thinking between sessions. It is not waiting for Alex to initiate. The reflection pass produces outputs that the next session-starting agent instance finds already prepared.

**Dependency:** Requires Proposals 2 and 3 as foundations (observation stream to read from; queue to write to). Also requires the Codex automation infrastructure discussed in the existing automation backlog.

**Risk:** Scheduled reflection passes on a sparse observation stream will produce low-quality syntheses. The mechanism is only valuable once the observation stream is rich enough to support synthesis — probably after 10+ sessions with Proposal 2 running.

---

### Proposal 5: Pattern library for automatic gap detection

**Scope:** Extension to `meta/curation-algorithms.md` (protected tier).

**Mechanism:** Define a small library of named patterns that the agent checks during session end and periodic review:

| Pattern name | Detection condition | Proactive output |
|---|---|---|
| `knowledge-gap` | 3+ sessions on topic X, no knowledge file in that domain | Add gap item to proactive queue |
| `idle-plan` | Active plan with `next_action` unchanged for 14+ days | Add nudge item to proactive queue |
| `stale-unverified` | `_unverified/` file older than 45 days with 3+ retrievals | Add review item to proactive queue |
| `high-value-unrewarded` | File with 7+ retrievals and still `trust: low` | Surface as promotion candidate |
| `topic-drift` | Last 5 sessions in domain X, but most plans/knowledge are domain Y | Observation note |
| `plan-cascade` | Plan A's `next_action` blocks plan B's `next_action` | Dependency alert |

These are not new algorithms — they are formalizations of things the agent already does informally. Making them named and explicit means: (a) the agent can apply them systematically rather than ad hoc, (b) they can be extended over time, (c) they can be enabled/disabled per pattern.

**Why this matters for the proactive loop:** Right now, gap detection depends on the agent noticing something during a session and remembering to write it. With a pattern library, the detection is systematic and runs at defined points regardless of what the session was about.

---

## Synthesis: A Minimal Viable Proactive Loop

Of the five proposals, the highest-value/lowest-cost path is:

**Phase 1 (can do immediately, no protected changes):**
- Add `## To surface next session` section to `scratchpad/CURRENT.md` conventions (Proposal 1)
- Start writing semantic observations in session reflection notes, as a new section in `reflection.md` — "Observations for future synthesis"

**Phase 2 (requires protected-tier approval for session-start checklist change):**
- Create `scratchpad/proactive-queue.md` with structured schema (Proposal 3)
- Modify session-start checklist to scan the queue

**Phase 3 (requires automation infrastructure):**
- Create `scratchpad/observations.md` as a persistent stream (Proposal 2)
- Add a scheduled lightweight reflection pass (Proposal 4)
- Formalize pattern library in `meta/curation-algorithms.md` (Proposal 5)

**The core architectural shift:** The current system treats the agent as a *servant* (responds when addressed). The proactive loop treats it as a *collaborator* (notices things, forms opinions, shows up with suggestions). The servant model is appropriate when the agent has low confidence in its situational awareness. As the memory system matures and the observation stream accumulates, the collaborator model becomes more valuable. The proposals above can be adopted incrementally as maturity increases.

---

## Open questions for Alex

1. **How proactive is too proactive?** There's a risk of the agent surfacing suggestions that feel like nagging. The queue approach (surface 1 item per session) seems right, but the right cadence is a user preference.

2. **Should proactive items be opt-in?** It would be easy to add a field in `identity/` like `proactive_surfacing: enabled | disabled | high-priority-only`. This makes the behavior configurable without changing the architecture.

3. **Reflection quality on sparse data:** Proposals 2-4 become more valuable as the observation stream grows. In the current early stage (Exploration), the system may not have enough signal for quality reflections. A natural trigger: enable scheduled reflections when the system reaches Stage 2 (Calibration), i.e., 20+ sessions with adequate ACCESS density.

4. **The automation infrastructure dependency:** Proposals 4+ depend on the Codex automation work (scheduled tasks running between sessions). This is already in the automation backlog. The question is sequencing: build proactive loop design now and implement when automation infrastructure is ready, or wait to design until infrastructure exists.

---

*Status: draft for Alex review. Proposals 1 and part of Proposal 2 can be implemented immediately. Proposals 3-5 are design proposals requiring review and phased implementation. No memory system changes have been made — this is a scratchpad-only working note.*
