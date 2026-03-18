---
source: agent-generated
type: implementation-plan
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 0 — implement git integration layer and version token model"
---

# Implementation Plan: Enhanced Agent-Memory MCP

## Goals

The existing `agent-memory` MCP exposes four read-only tools: `memory_read_file`, `memory_list_folder`, `memory_search`, `memory_validate`. All write operations currently go through raw `Edit`/`Write`/`Bash` tools, which have no knowledge of the memory system's invariants and cannot provide transactional guarantees.

This plan extends the MCP with a two-tier write layer:

- **Tier 1 — Semantic tools**: Coarse-grained, own all invariants for their operation, and auto-commit. The primary interface for routine memory operations.
- **Tier 2 — Low-level tools**: Raw file write/edit/delete/move, staged without auto-commit, plus an explicit `memory_commit`. Used only when no Tier 1 tool covers the operation, or when batching multiple changes into one commit.

Both tiers use **version tokens** for optimistic locking and return structured state so the agent does not need to re-read after writing.

---

## Architecture

### Git as the transaction layer

The memory repo is already a git repo. A git commit is atomic across any number of files: the working tree can be in a partial state, but a committed snapshot never is. This makes git the right transaction boundary rather than anything we need to build ourselves.

Consequence: every Tier 1 tool ends with `git add -A && git commit -m "<message>"`. The staging area serves as the write buffer. Tier 2 tools write files and stage them; `memory_commit` seals the transaction.

### Version tokens

Every `memory_read_file` response includes a `version_token: str` alongside the content. The token is the git object hash of the file at read time (`git hash-object <path>`). Every Tier 2 write tool and every Tier 1 tool that modifies an existing file accepts an optional `version_token` parameter. Before writing, the tool recomputes the current hash; if it differs from the provided token, it returns a `ConflictError` rather than overwriting. Callers that omit `version_token` get last-write-wins semantics.

This is intentionally lightweight — no locking server, no fencing tokens. It handles the real threat (a linter or user edit races with a tool call) without requiring infrastructure.

### Return contract

All write tools return a `MemoryWriteResult`:

```python
@dataclass
class MemoryWriteResult:
    files_changed: list[str]       # repo-relative paths of all written files
    commit_sha: str | None         # None if not yet committed (Tier 2 staged tools)
    commit_message: str | None
    new_state: dict                # operation-specific updated fields (see per-tool contracts)
    warnings: list[str]            # non-fatal issues (e.g., SUMMARY.md section not found)
```

`new_state` eliminates the read-after-write round trip. For `memory_mark_plan_item_complete` it contains `next_action`, `items_remaining`, and `phase_progress`. For `memory_promote_knowledge` it contains `new_path` and `trust`. Etc.

### Error taxonomy

```
MemoryError (base)
├── ConflictError        — version_token mismatch; include current_token so caller can re-read
├── NotFoundError        — file or section does not exist
├── ValidationError      — frontmatter schema violation, broken invariant, malformed checkbox
├── AlreadyDoneError     — idempotency: the operation is already in the target state (not an error, but distinct from success so callers can tell)
├── StagingError         — git add/commit failed; include stderr
└── PermissionError      — file deletion requires cowork permission (caller should invoke allow_cowork_file_delete then retry)
```

`AlreadyDoneError` is important: `memory_mark_plan_item_complete` called on an already-complete item should return this cleanly rather than succeed silently or error out, so the agent can distinguish "I did it" from "it was already done."

---

## Tool inventory

### Tier 0 — Enhanced read tools (extend existing)

---

#### `memory_read_file`
_Existing — add `version_token` to response._

```python
def memory_read_file(path: str) -> dict:
    # Returns: { "content": str, "version_token": str, "frontmatter": dict | None }
```

The `frontmatter` field is parsed and returned separately when the file has valid YAML frontmatter, so callers don't need to parse it themselves.

---

#### `memory_audit_trust`
_New._

```python
def memory_audit_trust(
    include_categories: list[str] | None = None,  # e.g. ["knowledge", "plans"]; None = all
) -> dict:
    # Returns: {
    #   "overdue_low": list[AuditEntry],     # low-trust files past 120-day threshold
    #   "overdue_medium": list[AuditEntry],  # medium-trust files past 180-day threshold
    #   "upcoming_low": list[AuditEntry],    # low-trust files within 30 days of threshold
    #   "upcoming_medium": list[AuditEntry], # medium-trust files within 30 days of threshold
    #   "checked_at": str,                   # ISO date
    # }
```

`AuditEntry` includes `path`, `trust`, `effective_date` (last_verified or created), `days_since_verified`, `days_until_threshold`, and `action_required` ("archive" | "flag" | "review").

Applies the exact thresholds from `meta/quick-reference.md` (currently: low=120 days, medium=180 days). Does not modify any files — pure read.

---

#### `memory_git_log`
_New._

```python
def memory_git_log(n: int = 10) -> list[dict]:
    # Returns list of: { "sha": str, "message": str, "date": str, "files_changed": list[str] }
```

Useful at session start to see what changed since the last session.

---

#### `memory_diff`
_New._

```python
def memory_diff() -> dict:
    # Returns: { "staged": list[str], "unstaged": list[str], "untracked": list[str] }
    # Each entry is a repo-relative path. Full diff text available via memory_read_file on the path.
```

Shows the working tree state — what's been written but not yet committed. Helps the agent verify staged changes before calling `memory_commit`.

---

### Tier 2 — Low-level write tools (staged, no auto-commit)

These replace raw `Edit`/`Write`/`Bash` calls for all memory writes. They stage changes but do not commit; call `memory_commit` when ready.

---

#### `memory_write`

```python
def memory_write(
    path: str,
    content: str,
    version_token: str | None = None,  # if provided, checked before write
    create_dirs: bool = True,
) -> MemoryWriteResult:
```

Creates or overwrites a file. Stages it. `new_state` in result contains the new file's `version_token`.

---

#### `memory_edit`

```python
def memory_edit(
    path: str,
    old_string: str,
    new_string: str,
    replace_all: bool = False,
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Exact string replacement, equivalent to the current `Edit` tool but with version checking and staging. Raises `ValidationError` if `old_string` is not found or is ambiguous (multiple matches when `replace_all=False`).

---

#### `memory_delete`

```python
def memory_delete(
    path: str,
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Deletes a file and stages the removal.

**Allowed directories**: `memory_delete` may only target paths under `knowledge/`, `plans/`, and `scratchpad/`. Attempts to delete files under `identity/`, `meta/`, `chats/`, `skills/`, or any path outside the repo root raise `PermissionError` immediately, without calling the cowork MCP. This is a hard constraint enforced in the tool before any filesystem access, not a runtime policy that can be overridden by the caller.

**Cowork permission handling**: For paths within the allowed directories, the tool calls `allow_cowork_file_delete` automatically before the `rm` — the caller does not need to invoke it separately. If the cowork MCP is unavailable or the permission grant fails, the tool raises `PermissionError` with the file path so the caller can handle it. The automatic grant is scoped to the specific file being deleted, not to the directory.

---

#### `memory_move`

```python
def memory_move(
    source: str,
    dest: str,
    version_token: str | None = None,  # checked against source
    create_dirs: bool = True,
) -> MemoryWriteResult:
```

Renames/moves a file. Stages both the deletion of source and creation of dest as a git rename (`git mv`) so history is preserved. `new_state` contains `new_version_token` for the destination path.

---

#### `memory_update_frontmatter`

```python
def memory_update_frontmatter(
    path: str,
    updates: dict,                    # key-value pairs to set; None values remove the key
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Parses YAML frontmatter, merges `updates` in, serializes back. Does not touch file body. Stages the result. Always sets `last_verified` to today's date unless `updates` explicitly includes `last_verified`. `new_state` contains the full updated frontmatter dict.

---

#### `memory_commit`

```python
def memory_commit(
    message: str,
    allow_empty: bool = False,
) -> MemoryWriteResult:
```

Commits all staged changes. `message` should follow the memory system's commit convention: a bracketed category prefix (`[knowledge]`, `[plan]`, `[identity]`, `[system]`, `[curation]`) followed by a one-line description. Raises `StagingError` if there is nothing staged and `allow_empty=False`.

---

### Tier 1 — Semantic write+commit tools

These are the primary interface. Each encapsulates a complete, named operation on the memory model, owns all invariants for that operation, and auto-commits. Internally they use the Tier 2 tools.

---

#### `memory_mark_plan_item_complete`

```python
def memory_mark_plan_item_complete(
    plan_id: str,        # e.g. "react-stack-research" — matches filename without .md
    phase_index: int,    # 0-based
    item_index: int,     # 0-based within phase
    version_token: str | None = None,
) -> MemoryWriteResult:
```

**Invariants maintained:**
1. `☐` → `☑` for the target item in the plan file
2. Phase counter updated: `☐ N/M complete` → `☐ (N+1)/M complete`; if all items done, checkbox becomes `☑`
3. `next_action` frontmatter updated to the first unchecked item across all phases; if all phases complete, set `status: complete` and `next_action: null`
4. `last_verified` updated to today
5. Progress log table gets a new row: `| {date} | Completed {filename} |`
6. `plans/SUMMARY.md` progress line updated to match new counts and `next_action`
7. All changes committed as `[plan] Mark {item_filename} complete ({plan_id} {n}/{total})`

**`new_state`:** `{ "next_action": str | null, "phase_progress": [n, total], "plan_progress": [n, total], "status": str }`

**Idempotency:** If the item is already `☑`, returns `AlreadyDoneError`.

---

#### `memory_promote_knowledge`

```python
def memory_promote_knowledge(
    source_path: str,              # relative to repo root, must be under knowledge/_unverified/
    trust_level: str = "high",     # "medium" or "high"
    target_path: str | None = None, # inferred by removing _unverified/ segment if None
    version_token: str | None = None,
) -> MemoryWriteResult:
```

**Invariants maintained:**
1. Frontmatter updated: `trust` set to `trust_level`, `last_verified` set to today
2. File moved to `target_path` (git mv for history preservation)
3. Source SUMMARY.md entry removed (matched by filename in the relevant section)
4. Target SUMMARY.md entry added (or created if absent) in the matching subject section
5. Committed as `[curation] Promote {filename} to knowledge/{subject}/ (trust: {level})`

**`new_state`:** `{ "new_path": str, "trust": str }`

**Validation:** Raises `ValidationError` if `source_path` is not under `_unverified/`, or if `target_path` is under `_unverified/`.

---

#### `memory_demote_knowledge`

```python
def memory_demote_knowledge(
    source_path: str,              # must be under knowledge/ but not _unverified/
    reason: str | None = None,     # appended to commit message
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Inverse of promote. Sets `trust: low`, moves back to the matching `_unverified/` subfolder, updates both SUMMARYs. Committed as `[curation] Demote {filename} to _unverified/ ({reason})`.

---

#### `memory_archive_knowledge`

```python
def memory_archive_knowledge(
    source_path: str,
    reason: str | None = None,
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Moves file to `knowledge/_archive/`, removes from source SUMMARY.md, updates frontmatter with `status: archived` and today's `last_verified`. Does **not** add to a SUMMARY.md (the archive is intentionally unlisted). Committed as `[curation] Archive {filename} ({reason})`. Used by the trust decay workflow for low-trust files past 120 days.

---

#### `memory_add_knowledge_file`

```python
def memory_add_knowledge_file(
    path: str,                    # under knowledge/_unverified/; directory is created if needed
    content: str,                 # file body (not including frontmatter)
    source: str,                  # e.g. "external-research", "agent-generated"
    trust: str = "low",
    session_id: str | None = None,
    summary_entry: str | None = None,  # one-line description for SUMMARY.md; inferred from H1 if None
) -> MemoryWriteResult:
```

Creates a new knowledge file with correct frontmatter (`source`, `created`, `last_verified`, `trust`, `origin_session`), adds or creates the folder's SUMMARY.md entry, commits as `[knowledge] Add {filename}`.

---

#### `memory_append_scratchpad`

```python
def memory_append_scratchpad(
    target: str,          # "user" → scratchpad/USER.md, "current" → scratchpad/CURRENT.md
    content: str,         # markdown content to append (a `---` separator is prepended if file is non-empty)
    section: str | None = None,  # if provided, appends under a matching `## {section}` heading
) -> MemoryWriteResult:
```

Append-only; never conflicts with concurrent writes — uses a merge strategy (append regardless of intermediate changes). No version token needed. Committed as `[scratchpad] Append to {target}`.

---

#### `memory_update_identity_trait`

```python
def memory_update_identity_trait(
    file: str,            # e.g. "professional", "preferences", "communication-style"
    key: str,             # frontmatter key or body section heading
    value: str,
    mode: str = "upsert", # "upsert" | "append" | "replace"
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Updates a named field in the specified identity file. If the key exists in frontmatter, updates frontmatter. If it exists as a body section, replaces or appends to that section. If it does not exist, creates it. Respects the identity churn alarm: if this session has already updated ≥5 identity traits, returns a `ValidationError` with message `"Identity churn alarm: 5 trait updates this session — confirm before proceeding"`. Committed as `[identity] Update {key} in identity/{file}.md`.

---

#### `memory_record_chat_summary`

```python
def memory_record_chat_summary(
    session_id: str,       # e.g. "chats/2026/03/18/chat-001"
    summary: str,          # full SUMMARY.md content (without frontmatter — tool adds it)
    key_topics: list[str] | None = None,
) -> MemoryWriteResult:
```

Creates or replaces `{session_id}/SUMMARY.md` with correct frontmatter, then updates `chats/SUMMARY.md` to reference the session. Committed as `[chat] Record summary for {session_id}`.

---

#### `memory_create_plan`

```python
def memory_create_plan(
    plan_id: str,           # kebab-case; becomes plans/{plan_id}.md
    title: str,
    description: str,       # one-line description for plans/SUMMARY.md
    content: str,           # full plan body (without frontmatter)
    next_action: str,
    plan_type: str = "research-plan",
) -> MemoryWriteResult:
```

Creates `plans/{plan_id}.md` with correct frontmatter (`type`, `status: active`, `next_action`, `created`, `last_verified`, `trust: medium`, `source: agent-generated`), then adds an entry to `plans/SUMMARY.md`. Raises `ValidationError` if `plans/{plan_id}.md` already exists. Committed as `[plan] Create {plan_id}`.

---

#### `memory_update_plan_next_action`

```python
def memory_update_plan_next_action(
    plan_id: str,
    next_action: str,
    version_token: str | None = None,
) -> MemoryWriteResult:
```

Updates only `next_action` and `last_verified` in the plan's frontmatter, and syncs the `plans/SUMMARY.md` line. Committed as `[plan] Update next_action for {plan_id}`. Lighter-weight alternative to `memory_mark_plan_item_complete` when manually adjusting the pointer without completing an item.

---

#### `memory_flag_for_review`

```python
def memory_flag_for_review(
    path: str,
    reason: str,
    priority: str = "normal",  # "normal" | "urgent"
) -> MemoryWriteResult:
```

Adds an entry to `meta/review-queue.md` with the path, reason, date, and priority. Does not modify the flagged file. Committed as `[system] Flag {path} for review`. Used by the trust decay workflow and anomaly detection.

---

## Invariant contracts: summary table

| Tool | Files touched | Key invariants |
|---|---|---|
| `mark_plan_item_complete` | plan file, `plans/SUMMARY.md` | checkbox, counter, `next_action`, `last_verified`, progress log |
| `promote_knowledge` | source file, source SUMMARY, target SUMMARY | `trust`, `last_verified`, path, both SUMMARY sections |
| `demote_knowledge` | source file, source SUMMARY, target SUMMARY | `trust`, path, both SUMMARY sections |
| `archive_knowledge` | source file, source SUMMARY | `status: archived`, `last_verified`, removed from SUMMARY |
| `add_knowledge_file` | new file, folder SUMMARY | frontmatter completeness, SUMMARY entry |
| `append_scratchpad` | scratchpad file | append-only, separator |
| `update_identity_trait` | identity file | churn alarm, upsert/append/replace modes |
| `record_chat_summary` | session SUMMARY, `chats/SUMMARY.md` | frontmatter, chats index entry |
| `create_plan` | plan file, `plans/SUMMARY.md` | frontmatter completeness, SUMMARY entry, no duplicate |
| `update_plan_next_action` | plan file, `plans/SUMMARY.md` | `next_action`, `last_verified`, SUMMARY sync |
| `update_frontmatter` | target file | `last_verified` auto-update, valid YAML |
| `flag_for_review` | `meta/review-queue.md` | entry format, date |

---

## Commit message conventions

### Format

```
[{category}] {Verb} {what changed, ≤60 chars}

{optional body}
```

The subject line (first line) must fit within 72 characters total. The bracketed prefix consumes roughly 10–12 characters, leaving ~60 for the description. The body, when present, is separated from the subject by a blank line.

---

### Category prefixes and verb vocabulary

Each category has a defined set of imperative-mood verbs. Using consistent verbs makes `git log --oneline` reliably scannable without opening the diff.

| Prefix | Used by | Verbs |
|---|---|---|
| `[knowledge]` | `add_knowledge_file`, low-level knowledge writes | Add, Update, Expand, Split, Merge |
| `[plan]` | `create_plan`, `mark_plan_item_complete`, `update_plan_next_action` | Create, Mark complete, Update next-action, Pause, Complete |
| `[identity]` | `update_identity_trait` | Update, Add, Remove |
| `[chat]` | `record_chat_summary` | Record |
| `[curation]` | `promote_knowledge`, `demote_knowledge`, `archive_knowledge`, `flag_for_review` | Promote, Demote, Archive, Flag |
| `[scratchpad]` | `append_scratchpad` | Append, Clear |
| `[system]` | structural/governance changes, `memory_commit` catch-all | Add, Update, Migrate, Fix, Remove |

**Imperative mood, no past tense.** Write "Add tanstack-query.md", not "Added tanstack-query.md."

**Multi-category commits use the dominant category.** If writing a knowledge file also updates plan progress, use `[knowledge]` — the knowledge file is the substantive work, and the plan update is bookkeeping. Reach for `[system]` only when the commit has no dominant content category (e.g., migrating anchors, reorganising folders, fixing SUMMARY.md structure).

---

### Tier 1 tool subject line templates

These are generated deterministically by the tool and require no agent judgment:

| Tool | Template |
|---|---|
| `add_knowledge_file` | `[knowledge] Add {filename}` |
| `mark_plan_item_complete` | `[plan] Mark {filename} complete ({plan_id} {n}/{total})` |
| `create_plan` | `[plan] Create {plan_id}` |
| `update_plan_next_action` | `[plan] Update next-action for {plan_id}` |
| `promote_knowledge` | `[curation] Promote {filename} to knowledge/{subject}/ (trust: {level})` |
| `demote_knowledge` | `[curation] Demote {filename} to _unverified/ ({reason})` |
| `archive_knowledge` | `[curation] Archive {filename} ({reason})` |
| `flag_for_review` | `[curation] Flag {path} for review ({priority})` |
| `update_identity_trait` | `[identity] Update {key} in identity/{file}.md` |
| `record_chat_summary` | `[chat] Record summary for {session_id}` |
| `append_scratchpad` | `[scratchpad] Append to {target}` |

---

### Agent commits via `memory_commit`: subject line

The agent calls `memory_commit` when using Tier 2 tools for operations no Tier 1 tool covers, or when batching several related writes into one commit. The same subject line rules apply:

```
[knowledge] Add celery-canvas-in-depth.md
[plan] Update react-stack-research phase 1 progress
[system] Add machine-readable anchors to SUMMARY.md files
```

When a batch of Tier 2 writes produces a commit that would otherwise be described as multi-category, use the dominant category and note secondary changes in the body rather than stacking prefixes.

---

### Agent commits via `memory_commit`: optional body

A body is optional for routine single-operation commits and expected for anything that involves a judgment call, multiple files, or external sources. Three structured fields, each on its own line:

```
Session: chats/2026/03/18/chat-001
Plan: django-stack-research phase 1/10
Sources: external-research (Celery docs, Celery Canvas guide)
```

`Session` anchors the commit to a specific chat for cross-referencing with `chats/` history. `Plan` identifies which research plan and phase drove the work — useful context when reading the log months later. `Sources` is for external-research commits and mirrors the frontmatter `source` field at the commit level for audit purposes.

Free-form notes go after a blank line following the structured fields:

```
Session: chats/2026/03/18/chat-001
Plan: django-stack-research phase 1/10
Sources: external-research (Celery docs)

Covers chain/group/chord in depth. chord reliability section expanded
beyond original plan scope based on session discussion.
```

Body fields are optional individually — include whichever are relevant. Do not pad with boilerplate when the subject line is self-explanatory.

---

### Commit granularity for extended workflows

**One logical unit per commit.** A logical unit is a piece of work that is independently meaningful and independently revertable. Not one commit per file write, and not one commit per session.

Good heuristics:
- Completing one knowledge file → one commit
- Completing a plan phase (even if it spans multiple files) → one or a few commits, not one per file and not one for the whole phase
- A structural change (adding anchors, reorganising a folder) → one commit, separate from content changes
- Updating plan bookkeeping after writing content → fold into the content commit rather than making a separate trivial commit

The failure modes to avoid: a giant end-of-session "catch-all" commit that buries multiple substantive changes and makes rollback destructive; and a per-write commit storm that fills the log with noise. When in doubt, ask: "would reverting this commit revert exactly the thing I'd want to undo?"

---

### Validation in `memory_commit`

The tool warns (not errors) if the message does not begin with a recognised `[{category}]` prefix, since agents may legitimately need novel categories for unanticipated operations. The warning is surfaced in `new_state.warnings` so the agent can decide whether to proceed or revise the message. Unknown prefixes are logged but not blocked.

---

## Implementation stack

- **Framework**: FastMCP (Python) — `@mcp.tool()` decorators, automatic schema generation from type hints and docstrings
- **Git operations**: `subprocess` calls to git CLI (not `gitpython` — the CLI is more predictable for staging/commit workflows and has no import overhead)
- **Frontmatter parsing**: `python-frontmatter` library — handles YAML front matter round-trips cleanly
- **Checkbox regex**: `r'^(\s*\d+\.\s*)(☐|☑)'` for plan item detection; `r'(☐ )(\d+)/(\d+)( complete)'` for phase counters
- **Path handling**: all paths are repo-relative strings; the MCP resolves them against the repo root at startup via an env var (`MEMORY_REPO_ROOT`)
- **Version token computation**: `subprocess.run(["git", "hash-object", abs_path])` — fast, no extra deps
- **SUMMARY.md section parsing**: regex-based section detection; sections delimited by `---` horizontal rules and `###` headings. Falls back to appending at end-of-file with a warning in `new_state.warnings` if section structure is unexpected.

---

## Phased build plan

### Phase 0 — Foundation · ☐ 0/3 complete

1. ☐ Git integration layer: `GitRepo` class wrapping subprocess git — `hash_object`, `add`, `commit`, `log`, `diff`, `mv`, `rm`; repo root resolution from env; error normalization to `StagingError`
2. ☐ Version token model: `check_version_token(path, token)` helper; `MemoryWriteResult` dataclass; error taxonomy as typed exceptions
3. ☐ Frontmatter utilities: `read_with_frontmatter`, `write_with_frontmatter`, `update_frontmatter_fields`; checkbox and counter regex helpers; SUMMARY.md section parser

### Phase 1 — Tier 2 low-level tools · ☐ 0/5 complete

4. ☐ `memory_write` and `memory_edit`
5. ☐ `memory_delete` (with cowork permission handling) and `memory_move`
6. ☐ `memory_update_frontmatter`
7. ☐ `memory_commit`
8. ☐ `memory_diff` (extend existing read toolset)

### Phase 2 — High-value semantic tools · ☐ 0/3 complete

9. ☐ `memory_mark_plan_item_complete` — highest-frequency write operation once plan execution begins
10. ☐ `memory_promote_knowledge` / `memory_demote_knowledge` / `memory_archive_knowledge`
11. ☐ `memory_add_knowledge_file`

### Phase 3 — Remaining semantic tools · ☐ 0/4 complete

12. ☐ `memory_append_scratchpad`
13. ☐ `memory_record_chat_summary`
14. ☐ `memory_create_plan` / `memory_update_plan_next_action`
15. ☐ `memory_update_identity_trait` / `memory_flag_for_review`

### Phase 4 — Enhanced read tools · ☐ 0/2 complete

16. ☐ `memory_audit_trust` — trust decay audit against thresholds in `meta/quick-reference.md`
17. ☐ `memory_git_log` and update `memory_read_file` to return `version_token` and parsed `frontmatter`

---

## Open questions

- **`plans/SUMMARY.md` parsing robustness**: ~~resolved~~. Using HTML comment anchors — invisible in rendered markdown, stable regardless of heading text edits, backwards-compatible. Two anchor shapes depending on usage pattern:
  - `plans/SUMMARY.md`: BEGIN/END pairs wrapping each plan's full entry block (`<!-- BEGIN: {plan-id} -->` / `<!-- END: {plan-id} -->`), enabling full section replacement without boundary inference.
  - `knowledge/SUMMARY.md` and `knowledge/_unverified/SUMMARY.md`: single `<!-- section: {subject} -->` anchors above each `###` subject heading, enabling targeted entry insertion/removal within a subject section.
  - Entry-level anchors within knowledge SUMMARY sections are not needed — individual bullet entries can be found by filename match within the correct section.
  - Migration is a single explicit `[system]` commit rather than auto-migration on first write access, so the structural change is visible and reviewable in history.
  - Plans SUMMARY files should remain legible to humans even with anchors present; `---` section separators stay outside BEGIN/END blocks as visual dividers.

- **Multi-agent writes**: the version token model handles races between the agent and a linter/user. If a future use case involves two agent instances writing the same repo simultaneously (e.g., parallel research tasks), the version token model is still correct but the commit conflict rate will be higher. At that point, per-file lock files or a SQLite-backed locking layer would be worth considering. Not a concern for the current single-agent use case.

- **`memory_audit_trust` threshold source**: the thresholds are currently hardcoded in `meta/quick-reference.md`. The audit tool should read them from that file at runtime rather than hardcoding them, so threshold changes during a stage transition are automatically picked up. This requires parsing the active thresholds table from the quick-reference file.

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from design discussion; two-tier architecture, version token model, and full tool inventory defined |
| 2026-03-18 | `memory_delete` scoped: auto-calls `allow_cowork_file_delete` only for paths under `knowledge/`, `plans/`, `scratchpad/`; hard `PermissionError` for all other paths |
| 2026-03-18 | Anchor design resolved and migration applied: BEGIN/END pairs in `plans/SUMMARY.md`; `<!-- section: {id} -->` anchors in `knowledge/SUMMARY.md` and `knowledge/_unverified/SUMMARY.md` |
| 2026-03-18 | Commit message conventions expanded: verb vocabulary, Tier 1 templates, agent body format, granularity guidance, `memory_commit` validation behaviour |
