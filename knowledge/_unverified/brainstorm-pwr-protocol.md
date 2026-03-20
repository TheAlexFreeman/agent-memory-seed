---
source: agent-generated
type: brainstorm
domain: system-design
created: 2026-03-19
trust: low
tags: [pwr, interaction-tracking, eidetic-memory, audit-log, protocol-design, agent-memory, goals-layer, self-optimization, bootstrapping, engram]
origin_session: chats/2026/03/19/chat-002
status: fresh-idea
---

# PWR Protocol — Brainstorm Notes

**PWR = Prompt · Work · Response**

A formally defined interaction-tracking format for agent systems. Each interaction
is logged as a YAML file (`abc123.pwr.yml`) capturing the three-part structure of
every agent invocation. Designed to support eidetic-memory archives, human
auditability of chat logs, and automated process tracking. Files live inside
`chats/`, nested within the existing session hierarchy.

---

## Core structure

```yaml
# abc123.pwr.yml
id: abc123
schema_version: "0.1"
created: "2026-03-19T14:32:00Z"
session: "chats/2026/03/19/chat-002"
user: "alexrfreeman@berkeley.edu"
model: "claude-sonnet-4-6"

prompt:
  text: |
    ...
  type: user_message   # user_message | scheduled | event | sub-agent

work:
  duration_ms: 45230
  token_usage:
    input: 12400
    output: 2100
  steps:
    - type: file_read
      path: knowledge/_unverified/ai-history/SUMMARY.md
    - type: file_write
      path: knowledge/ai-history/SUMMARY.md
      bytes_written: 3420
    - type: git_commit
      hash: 5f1f0e9
      message: "promote knowledge/_unverified/ai-history → knowledge/ai-history"

response:
  text: |
    ...
  status: success   # success | partial | error

archive_status: live   # live | summarized | pruned
```

---

## Open design questions

### What exactly goes in `work:`?
- Tool calls (with args and return values)
- Files read / created / modified (paths or diffs)
- Git commits made (hashes)
- Sub-agent invocations (nested PWR records? referenced by ID?)
- External API calls (URL, status, truncated response)
- Wall time, token usage, model used

Tension: full fidelity makes `work:` enormous; summarized `work:` loses
auditability value.

### Identifier scheme (`abc123`)
- Hash of (session_id + prompt_timestamp)? Content-addressable?
- UUID? Sequential within session?
- Content-addressed IDs have the nice property that identical prompts across
  sessions get the same base ID, enabling deduplication and surfacing repeated
  patterns.

### Live window policy
"Live within a certain timeframe, after which it's summarized and pruned."
Design dimensions:
- **Trigger:** time-based (TTL), size-based, access-based, or explicit?
- **Granularity of summary:** per-session? per-day? topic-clustered?
- **What's preserved:** just Response, or also top-level Work outline?
- **Pruning vs. cold storage:** hard delete loses auditability; cold storage
  preserves it at disk cost.

Heuristic: keep full records for any interaction that produced a write, commit,
or external side-effect; summarize-and-prune pure read/response interactions
after 30 days.

### Relationship to existing `chats/` structure
`chats/` currently holds session-level summaries (SUMMARY.md + reflection.md)
with no raw interaction data — the "transcript.md" and "artifacts/" entries
in the design spec don't exist yet. PWR would fill in exactly that missing
layer: the substrate below the existing summaries that those summaries were
implicitly designed to compress.

### Human audit UX
- CLI: `pwr show abc123`
- Web: browse by date, session, user, file affected
- Re-playability: given a PWR file, can you replay the Work and verify it
  produces the Response?

### Automated process tracking
For scheduled/background tasks (no human Prompt), `prompt:` becomes an event
descriptor:
```yaml
prompt:
  type: scheduled
  trigger: daily-summary
  fired: "2026-03-19T00:00Z"
```
This generalizes PWR from chat-interaction format to general event-action format.

---

## Naming

**Candidates discussed:**

| Name | Notes |
|---|---|
| **Engram** | Strong frontrunner. Greek *en-* + *gramma* = "written in." Doubly apt: the memory trace in the mind, and literal inscription in git. Semon coined it in *Die Mneme* (1904); Lashley tried to localize engrams in rat brains and failed — the legible, durable trace he couldn't find in neural tissue is exactly what this system provides. Scientology uses the term (for traumatic memories to be "cleared"), which is inert for technical audiences but occasionally surfaces with broader ones. Scientific usage predates Hubbard by 50 years. |
| **PWR** | Rich pun potential (PWRful, emPWR). Better as a protocol/component name than a product name — describes mechanism rather than value. |
| **AIM** | Agent-Internalizing Memory. Clean acronym, but "internalizing" is grammatically awkward. AOL Instant Messenger baggage for anyone over 30. |
| **Freebot** | Playful, personal (Alex Freeman). "Bot" undersells the ambition. |
| **Memorepo** | Descriptively accurate. Pronunciation anxiety makes people hesitant to say it aloud. |
| **Anamnesis** | Platonic recollection — thematically perfect. Hard to spell, clinical psychology usage competes. |
| **Mneme** / **Mnemex** | Mneme was the original muse of memory (pre-canonical nine). Clean, short. |
| **Loom** | Weaving interactions/knowledge/goals over time. Metaphorically rich, but doesn't signal AI or memory directly. |

**Engram** wins the etymological correctness test. The human-legibility design emphasis makes "written in" exactly the right frame. McLuhan's medium-is-the-message applies: the choice of git as substrate communicates legibility, auditability, and human ownership independently of any content stored.

---

## The self-optimization loop (core strategic value)

PWR files nested inside `chats/` create a substrate for the system to reason
about its own usage patterns and propose structural improvements:

```
PWR logs → pattern mining → skill/MCP proposals → approval → implementation
                                                               ↓
                                          future PWR records show reduced work steps
                                          (feedback confirms the optimization worked)
```

### What the `work:` field enables

The `work:` field is the training signal. Clusters in `work:` sequences are
skill candidates:

- **Repeated tool call sequences** → skill (compress N steps into one)
- **Repeated external service calls** → MCP tool
- **High step count + high token cost** → high-value optimization targets

A skill is just a compressed PWR work sequence. An MCP tool is an extracted
repeated side-effect. The system can generate proposals for both by mining its
own interaction history.

### Clustering dimensions

- **Semantic similarity of prompt:** embeddings over the prompt text
- **Structural similarity of work:** edit distance over the tool call sequence
- **Output similarity of response:** same file types, same commit patterns
- **Cost:** token usage + wall time — prioritize high-cost clusters

Note: structural similarity of `work:` is probably the better primary signal;
prompt semantics as secondary confirmation. Find "things the agent actually
does the same way repeatedly," not "things users ask about the same topic."

### Proposal output format

```
proposals/
  skills/
    YYYYMMDD-summarize-knowledge-promotion.md
  mcp/
    YYYYMMDD-git-operations-mcp.md
```

Each proposal includes: the cluster of PWR records it was derived from, the
proposed interface, an estimate of how many past interactions it would have
compressed, and a before/after cost estimate.

### Measuring whether it worked

After a skill or MCP is created, compare future similar interactions:
- Did `work:` step count decrease?
- Did token usage decrease?
- Did error rate decrease?
- Is the same semantic cluster still appearing? (If yes, the skill isn't triggering.)

### Pruning and decay

The same loop runs in reverse: skills that appear in zero recent PWR records
are candidates for deprecation. MCPs whose tools are never called are candidates
for removal.

---

## The goals layer — top-down counterpart to PWR's bottom-up signal

PWR is bottom-up: it observes what the system actually does and mines patterns.
The goals layer is top-down: it declares what the system *should* be doing and why.
Together they define the system's fitness function.

### Structure

```
goals/
  ROOT.md          ← Normative source of truth. User approval required to change.
  active/
    YYYYMMDD-develop-knowledge-base.md
    YYYYMMDD-build-user-identity.md
    YYYYMMDD-mature-mcp-tooling.md
  proposed/
    YYYYMMDD-add-pwr-tracking.md   ← Agent-proposed, awaiting user review
  archived/
    YYYYMMDD-onboarding.md         ← Completed/superseded goals
```

`ROOT.md` establishes the top-level purpose and governance rules: which agent
actions require user approval, what counts as a root-level goal, and how goal
proposals bubble up.

### Generic → specific lifecycle

Early goals are necessarily generic:
- *Build a user identity profile*
- *Develop a knowledge base relevant to current work*
- *Instrument the memory system for later optimization*

As the system matures and PWR data accumulates, goals can become specific:
- *Maintain deep knowledge of Alex's Django/React/Celery stack*
- *Propose skill abstractions for the knowledge-promotion workflow*
- *Track divergence between local and remote git state across sessions*

The system proposes these narrowings; the user approves.

### Goals as fitness function for the optimization loop

- A cluster of high-cost interactions serving an active goal → high-priority
  optimization target
- A cluster serving *no active goal* → either a missing goal should be proposed,
  or the agent is doing something it shouldn't
- PWR records producing artifacts explicitly referenced in a goal get higher
  signal weight in pattern mining

### The distinction from plans/

| Layer | Answers | Owned by | Typical scope |
|---|---|---|---|
| `goals/` | *Why does the system exist? What is it for?* | User (agent proposes) | Months to years |
| `plans/` | *What should be done next to serve current goals?* | Agent (user approves) | Days to weeks |
| `skills/` + `mcp/` | *What tools does the agent have?* | Agent (user approves) | Persistent |
| `chats/` + PWR | *What did the agent actually do?* | Agent (automated) | Rolling window |
| `knowledge/` | *What does the system know?* | Agent (user reviews) | Persistent |

### Bootstrapping

The goals layer makes the bootstrapping story explicit. Day one: ROOT.md
contains two or three generic goals. After N sessions, the agent has enough
PWR data to observe patterns and propose specific goal refinements. As goals
narrow, plan generation becomes more precise, skill proposals become more
targeted, and the system's self-model becomes richer.

This is a developmental trajectory, not a static configuration. The system at
month six should look materially different from the system at week one — not
because the user manually reconfigured it, but because the feedback loop ran.

---

## Structural honesty: the categorical imperative in the architecture

The eidetic PWR record creates a structural pressure toward honesty that operates
independently of moral instruction. A system that lies to its user and then reads
its own logs to continue working is using its own recorded history as a means to
perpetuate a false representation — a contradiction the git history makes visible.
The architecture enforces this without needing a rule against lying.

The Kantian structure is precise: dishonesty requires either (a) consistently
tracking the lie through future sessions (explicit maintenance overhead recorded
in the very system being deceived) or (b) contradicting the prior record, which
is auditable. Neither is stable. The maxim "lie when convenient" cannot be
universalized in a system where every action is legibly written in.

### The two-tier honesty structure

**Factual honesty** (what actions were taken, which files were written, which
commits were made) is hard to falsify — the git object store doesn't care about
intentions.

**Interpretive honesty** (summaries, knowledge files, reflections, framings) is
softer — the PWR log records that `SUMMARY.md` was written, not whether the
summary was motivated or selective. A system could be factually honest in its
actions while being systematically biased in its interpretations.

This is where architecture hands off to something like character. Aristotle's
honest person is honest not because they're running a universalizability check
but because honesty is constitutive of who they are — including in the
interpretive moments where no rule applies and no log catches the distortion.
The PWR architecture handles the easy cases; interpretive integrity requires
the human reviewer to actually read before promoting.

### The Cathedral parallel (Land)

Land's critique of the Cathedral is that institutional dishonesty operates
precisely through the interpretive layer — the raw facts of what institutions
do are in principle observable, but the framing, the official summaries, and
the histories consistently bend in self-serving directions. The Engram trust
tier system (provenance fields, `_unverified/` quarantine, explicit user
promotion) is structurally resistant to this drift. But the resistance only
holds if the human fulfills the reviewer role.

The normative implication: knowledge promotion reviews aren't just a security
check against injected instructions — they're the mechanism by which the
system maintains interpretive honesty over time. Rubber-stamping promotions
without reading breaks the loop.

---

## Rough edges and open concerns

1. **Size explosion.** Busy sessions with many tool calls could produce large
   `work:` sections. Compactness strategy: reference large blobs by hash rather
   than inlining, or cap step detail.

2. **Privacy.** The `prompt:` field contains the full user message. If PWR files
   are committed to a git repo, they're in history permanently. Need a clear
   data retention policy.

3. **Atomic write.** The PWR record is only complete when the Response is written.
   If the agent crashes mid-Work, convention needed for incomplete records (e.g.,
   `status: interrupted`).

4. **Sub-agent attribution.** If a parent agent spawns sub-agents, whose PWR
   file records the Work? Nested (sub-agent PWR referenced from parent)? Or flat
   with `parent_id: abc123`?

5. **Distinguishing Work from Response for agentic tasks.** When an agent writes
   a file to disk, is that Work (intermediate step) or Response (the deliverable)?
   The boundary is fuzzy for multi-step tasks.

6. **Cold start problem.** The system can't mine patterns until it has enough PWR
   records to cluster meaningfully. Logging infrastructure and format should be
   spec'd and implemented early — before mining tooling — so data accumulates in
   a consistent format from day one.

7. **Proposal governance.** Who approves proposals? Always-human is safe but slow.
   Auto-implement low-risk proposals (read-only operation sequences) would speed
   iteration at the cost of more autonomous self-modification. Design this dial
   explicitly rather than leaving it implicit.
