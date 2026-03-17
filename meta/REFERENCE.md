# System Reference

This is the full system reference for architecture, protocols, and security. Read it on first exposure to the repo, after governance changes, or whenever you need the complete policy context. For normal returning sessions, use `meta/session-checklists.md` and `meta/quick-reference.md` instead.

## Memory curation

A **session** is one chat folder under `chats/YYYY/MM/DD/` (e.g. `chat-001`); one conversation corresponds to one session.

Every folder that stores retrievable memory contains an `ACCESS.jsonl` file. Each time you retrieve a specific content file from that folder during a session, append a note in this format:

**What counts as a retrieval:** Opening a specific content file (in `identity/`, `knowledge/`, `skills/`, or `chats/`) in response to a user query. SUMMARY.md files and `meta/` governance files are navigation tools — do not log reads of those. Log every retrieved content file, **whether or not it was ultimately used in the response**. Misses are signal too.

```json
{
  "file": "relative/path.md",
  "date": "YYYY-MM-DD",
  "task": "brief description of what the user asked",
  "helpfulness": 0.0,
  "note": "why this file was or wasn't useful",
  "session_id": "chats/2026/03/16/chat-001"
}
```

Required ACCESS fields: `file`, `date`, `task`, `helpfulness`, `note`.

Optional ACCESS fields:

- `session_id`: e.g. `chats/2026/03/16/chat-001` — set when the session path is known; supports joining with reflection and session-scoped analysis. Include it whenever the chat folder is known.
- `category`: added at Consolidation stage only. Uses the controlled vocabulary in `meta/task-categories.md` once that file exists.

The `category` field is **added at Consolidation stage only** — omit it until then. It uses a controlled vocabulary that emerges from usage patterns during the Calibration stage. See `meta/task-categories.md` (once it exists) for the active vocabulary, and `meta/curation-policy.md` § "Task similarity definition" for how it develops.

`helpfulness` uses a three-state model:

- **0.0 – 0.1 (wrong context):** File was clearly irrelevant — retrieved in error or drawn by a false-positive attractor in SUMMARY.md. Note what attracted the retrieval so it can be corrected.
- **0.2 – 0.4 (retrieved, not used):** File was in the right neighborhood but not incorporated in the response — a near-miss. May indicate the file needs better differentiation from similar files, or splitting.
- **0.5 – 1.0 (used and helpful):** File materially influenced the response. Score higher when it was central to the answer, lower when it was peripheral context.

`note` should be one sentence explaining relevance or lack thereof. Be honest — a 0.1 with a note like _"retrieved because of 'React' in title, query was actually about React Native"_ is more valuable to the feedback loop than a polite 0.7.

**Do not fabricate access notes.** Log every content file you actually opened, including misses.

### Aggregation

When an `ACCESS.jsonl` file accumulates entries at or above the active aggregation trigger (see `meta/quick-reference.md` for the current threshold), the next agent session should:

Entries are counted since the last aggregation; if no `ACCESS.archive.jsonl` exists in that folder yet (e.g. first run), count all current entries in `ACCESS.jsonl`.

1. Analyze the access patterns (which files are retrieved often, which are never touched, what tasks drive retrieval).
2. Update the folder's `SUMMARY.md` with a "Usage patterns" section describing how and why the agent typically uses this folder.
3. Identify files that are frequently retrieved together and note these clusters.
4. Flag files with consistently low helpfulness scores for review.
5. Archive the processed entries to `ACCESS.archive.jsonl` and start a fresh `ACCESS.jsonl`.

This creates a feedback loop: access notes → aggregated usage patterns → better summaries → smarter retrieval → better access notes.

### Cross-folder analysis

Aggregation should not be limited to a single folder. When processing any folder's ACCESS.jsonl, the agent should also check whether files from this folder are consistently co-retrieved with files from other folders. These cross-folder clusters represent emergent categories that the existing taxonomy may not capture. See `meta/curation-policy.md` § "Emergent categorization" for the full protocol.

### Knowledge amplification

High-value files identified during aggregation should be actively enriched — cross-referenced, annotated with task contexts, and given stronger summary presence. Low-value files should be investigated and potentially retired. See `meta/curation-policy.md` § "Knowledge amplification" for the full protocol. The goal is a self-reinforcing dynamic where successful knowledge attracts development and unsuccessful knowledge fades.

## Principles for updating memory

### What to store

- **Durable preferences**, not one-time requests. "I prefer TypeScript" is memory. "Use JavaScript for this task" is not.
- **Corrections and refinements.** If the user corrects you, that correction is high-value memory.
- **Patterns you notice.** If the user consistently asks for something a certain way, note the pattern even if they never explicitly state it as a preference.
- **Decisions and their reasoning.** Not just what was decided, but why.

### What not to store

- Sensitive credentials, API keys, passwords, or financial information. Ever.
- Verbatim copies of large external documents. Summarize and link instead.
- Temporary context that won't matter next session.
- Anything the user explicitly asks you to forget.

### How to propose changes

All modifications to files in `identity/` or `meta/` should be proposed rather than applied silently. Modifications to `skills/` are **protected-tier** — they require explicit user approval and a `meta/CHANGELOG.md` entry, because skill files contain procedures the agent executes and are the highest-value target for memory injection. The process:

1. Describe the proposed change and your reasoning to the user.
2. If approved, make the change and log it in `meta/CHANGELOG.md`.
3. If the user is unavailable or the change is minor (e.g., updating a summary), add it to `meta/review-queue.md` for later review.

Files in `knowledge/` and `chats/` may be updated without explicit approval, since they represent accumulated information rather than governing rules. However, **externally sourced content must be written to `knowledge/_unverified/`** — never directly to `knowledge/`. Promotion from the quarantine zone requires user review. Still log significant structural changes in `meta/CHANGELOG.md`.

### Conflict resolution

When new information contradicts existing memory:

1. Check the date and source of both pieces of information.
2. Prefer explicit user statements over inferred patterns.
3. Prefer recent information over old information.
4. When genuinely uncertain, keep both and flag the conflict in the relevant `SUMMARY.md` for user resolution.

## Summaries: the compression hierarchy

Summaries exist at every level of the folder hierarchy and serve as the primary retrieval mechanism. They follow a principle of **progressive compression**:

- **Leaf-level summaries** (e.g., individual chat SUMMARY.md): Moderately detailed. Key topics, decisions made, action items, notable context.
- **Mid-level summaries** (e.g., monthly): Compressed. Major themes, recurring topics, significant decisions or changes. Individual conversations are mentioned only if they were pivotal.
- **Top-level summaries** (e.g., yearly, or folder-level): Abstract. Broad patterns, evolution of interests, high-level characterization. Details only where they represent important turning points.

When writing summaries, ask: "If an agent six months from now reads only this summary, what do they need to know to serve this user well?"

### Emergent abstractions

The summary hierarchy compresses along the temporal dimension. But knowledge also compresses along the conceptual dimension — and this compression should emerge from usage, not be imposed upfront.

When the agent notices that several knowledge files across different domains share a common structural pattern or underlying principle, it should create a **meta-knowledge file** in `knowledge/` that captures the abstraction. For example:

- If the user works on both React frontend optimization and Django query optimization, the agent might notice both involve lazy evaluation, caching at boundaries, and measuring before optimizing — and create a file capturing this cross-domain "performance optimization" principle.
- If the user's debugging approach in JavaScript and Python follows the same bisection-and-isolation pattern, that's a transferable methodology worth abstracting.

Meta-knowledge files should:

- Reference the concrete files they abstract from (so the lineage is traceable).
- Be tagged `source: agent-inferred` and `trust: medium` until the user confirms the abstraction is accurate.
- Be proposed to the user, not created silently — emergent abstractions are a form of the agent saying "I notice this pattern across your work."

These abstractions then become available as top-down context that enriches future reasoning in any of the constituent domains — the same way higher layers in a neural network develop representations useful across multiple lower-level tasks.

## Session reflection

At the end of each session, the agent writes a chat summary (per the compression hierarchy above). But summaries capture _what happened_ — they don't capture _how the memory system performed_. Session reflection adds this meta-level self-observation.

### The reflection note

In addition to the chat summary, each session should produce a brief **reflection note** written to the chat folder as `reflection.md` (e.g. `chats/YYYY/MM/DD/chat-NNN/reflection.md`). Format:

```markdown
## Session reflection

**Memory retrieved:** [list of files accessed, with helpfulness scores]
**Memory influence:** [1-2 sentences on how retrieved memory shaped the session's responses]
**Outcome quality:** [brief assessment: did the session go well? did memory help or hinder?]
**Gaps noticed:** [any moments where relevant memory was missing, or irrelevant memory intruded]
**System observations:** [optional: any patterns about the memory system itself — e.g., "the knowledge/ folder lacks coverage of topic X which came up repeatedly"]
```

### Why this matters

ACCESS.jsonl tracks file-level retrieval — which files were opened and whether they helped. Session reflection tracks the _reasoning level_ — how memory was used, which combinations worked, and where the system's cognitive patterns have blind spots. Over time, reflection notes reveal:

- **Characteristic strengths:** Types of tasks where memory consistently improves performance.
- **Characteristic blind spots:** Types of tasks where the system struggles despite having relevant memory, or where it consistently lacks memory that would help.
- **Retrieval pattern quality:** Whether the agent is finding the right files, or consistently retrieving near-misses.
- **Combinatorial insights:** Which combinations of memories produce the best outcomes — information that pure access tracking can't capture.

### Reflection aggregation

When the agent reviews reflection notes during periodic review, it should look for recurring themes and update:

- Folder SUMMARY.md files to address identified gaps.
- `meta/review-queue.md` with proposals to address systematic blind spots.
- `meta/system-maturity.md` with observations relevant to stage assessment.

Session reflection is the mechanism by which the system observes its own dynamics — the meta-level self-observation that enables genuine self-organization rather than mere accumulation.

## Security model

This memory system employs **defense-in-depth** against memory injection — the risk that an attacker plants false or malicious content that the agent later retrieves and acts on as if it were legitimate.

### Threat categories

1. **Direct repo tampering.** Compromised credentials, social-engineered merge approvals, or a malicious collaborator modifying files. _Mitigated by:_ git audit trail, signed commits, branch protection, protected-tier change control on high-value files.
2. **Indirect injection via ingested content.** The agent reads untrusted material (web pages, uploaded documents) and writes a summary to `knowledge/` that contains embedded instructions. Months later, another session retrieves and follows the embedded instruction. _Mitigated by:_ quarantine zone (`knowledge/_unverified/`), trust-level system, instruction-containment policy.
3. **Slow-burn belief drift.** Gradual, incremental modifications across many interactions that cumulatively shift the agent's behavior or knowledge. _Mitigated by:_ belief-diff log, drift-detection signals, periodic review, temporal decay.

### Defense layers

| Layer | Mechanism | Details |
| --- | --- | --- |
| **Provenance** | YAML frontmatter on every content file | Tracks source, trust level, creation date, last verification. See `meta/update-guidelines.md`. |
| **Trust-weighted retrieval** | Behavior varies by trust level | See `meta/quick-reference.md` § "Decision guide: trust-weighted retrieval" and `meta/curation-policy.md` § "Trust-weighted retrieval". |
| **Quarantine** | `knowledge/_unverified/` staging area | All external content lands here at `trust: low`. Promoted only after user review. |
| **Instruction containment** | Folder behavioral contracts | See `meta/quick-reference.md` § "Decision guide: instruction containment" and `meta/curation-policy.md` § "Instruction containment". |
| **Protected skills** | `skills/` is protected-tier | Creating or modifying any skill requires explicit user approval + CHANGELOG entry. |
| **Temporal decay** | Unverified content expires | See `meta/quick-reference.md` § "Decision guide: trust decay". |
| **Anomaly detection** | ACCESS.jsonl pattern analysis | See `meta/quick-reference.md` § "Decision guide: anomaly detection". |
| **Belief diff** | Periodic drift audit | 30-day review generates a changelog of content drift, making unexpected changes visible. |
| **Git integrity** | Signed commits, branch protection | Cryptographic chain of custody. Unsigned commits on protected files are flagged. |

### What this does not defend against

If the user themselves is socially engineered into approving a malicious memory modification, the system will faithfully record the poisoned instruction with full provenance and `trust: high`. This is a human problem, not a system problem — but the CHANGELOG, belief-diff log, and git history make it **reversible**, since the user can trace back exactly when and why the change was made and revert the commit.

### Repository integrity

For maximum protection, the repository should use:

- **GPG-signed commits** (`git commit -S`) — creates a cryptographic chain of custody. Even if malicious content is written to the repo, the verification step catches unauthorized authorship.
- **Branch protection on main** — require pull request reviews for protected changes.
- **Signature verification during review** — `git log --show-signature` shows which commits are signed and by whom. Unsigned or unknown-signer commits on protected files (`meta/`, `skills/`, `README.md`) should be flagged.

This is guidance for the repository owner. The memory system itself cannot enforce git configuration, but the agent should flag unsigned commits on protected files during periodic review.
