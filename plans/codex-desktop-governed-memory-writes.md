---
created: 2026-03-18
last_verified: 2026-03-18
next_action: Add structured UI feedback
origin_session: manual
source: agent-generated
status: active
trust: medium
type: implementation-plan
---

# Implementation Plan: Codex Desktop Governed Memory Writes

## Goals

Give Codex desktop first-class support for governed memory operations so the app can perform safe, invariant-aware writes instead of relying on generic file edits for structured memory repos. The target outcome is a semantic write layer that understands frontmatter, summaries, ACCESS logs, plan progression, and protected/proposed/automatic change categories.

This plan builds on the repo's current direction toward MCP-backed memory operations, but scopes the work at the Codex desktop product layer.

---

## Problem statement

Generic edit tools are too low-level for governed memory systems:

- they do not know which fields are required in frontmatter
- they do not keep `SUMMARY.md` files synchronized
- they do not understand change categories like automatic vs. proposed vs. protected
- they do not offer semantic operations like plan advancement, knowledge promotion, or access logging

That means correctness depends on the agent remembering repo-specific invariants every time.

---

## Desired capabilities

1. **Semantic memory operations**
   - create plan
   - mark plan item complete
   - add knowledge file
   - promote/demote/archive knowledge
   - append ACCESS entry
   - record session summary / reflection

2. **Invariant-aware execution**
   - frontmatter validation and updates
   - `last_verified` / trust handling
   - summary synchronization
   - optimistic locking or version-token checks

3. **Governance enforcement**
   - block protected writes without explicit approval path
   - surface proposed changes clearly
   - allow automatic changes to proceed with proper audit trail

4. **Structured results**
   - return changed files
   - return new semantic state
   - return warnings for partial sync or unexpected repo structure

---

## Research and design phases

### Phase 1 — Semantic write model · ☑ 3/3 complete

1. ☑ Define the minimal semantic tool set
   - highest-frequency memory operations first
   - clear separation between semantic tools and raw fallback tools
   - repo-agnostic core plus repo-specific extensions

2. ☑ Define invariant ownership per operation
   - which tool updates frontmatter
   - which tool updates `SUMMARY.md`
   - which tool logs ACCESS or review-queue artifacts

3. ☑ Define result and error taxonomy
   - conflict
   - validation failure
   - already-done
   - protected-change blocked
   - partial sync warning

### Phase 1 decisions (2026-03-18)

#### 1. Capability contract shape

The governed-write layer should be declared as a machine-readable tooling contract, not inferred from prose alone. Repo-side prototype: `HUMANS/tooling/agent-memory-capabilities.toml` now records:

- read-support tools
- raw fallback tools
- semantic extension tools
- the shared `MemoryWriteResult` envelope
- desktop-surface gaps that are still missing semantic coverage

This keeps the semantic surface reviewable in git and gives the desktop layer a stable object to discover later.

#### 2. Invariant ownership model

Each semantic tool owns the full invariant set for its operation:

- **Plan tools** own plan frontmatter plus `plans/SUMMARY.md` synchronization
- **Knowledge tools** own trust/frontmatter transitions plus the relevant `SUMMARY.md` moves
- **Identity tools** own `last_verified` updates and identity-churn guarding
- **Chat tools** own per-session summary creation plus `chats/SUMMARY.md` indexing
- **Governance tools** own `meta/review-queue.md` mutation directly

Raw fallback tools remain intentionally non-semantic. They can write, move, delete, and commit, but they do not own repo invariants.

#### 3. Result and error taxonomy

The Phase 1 contract now treats `MemoryWriteResult` as the shared write envelope across semantic and raw tools:

- `files_changed`
- `commit_sha`
- `commit_message`
- `new_state`
- `warnings`

Error taxonomy is also explicit now. Current runtime support is:

- implemented: `ConflictError`, `NotFoundError`, `ValidationError`, `StagingError`, `MemoryPermissionError`
- defined but not yet emitted consistently: `AlreadyDoneError`

Repo-side prototype: `HUMANS/tooling/scripts/resolve_memory_capabilities.py` now validates the capability contract against the MCP runtime and highlights declared desktop-surface gaps such as ACCESS appends and session reflections.

### Phase 2 — Governance and policy integration · ☑ 3/3 complete

4. ☑ Map repo governance to app-side affordances
   - automatic changes
   - proposed changes
   - protected changes
   - read-only/deferred action mode

5. ☑ Design approval and confirmation UX
   - semantic preview before protected writes
   - clear explanation of what files and invariants will change
   - explicit commit-category suggestions where applicable

6. ☑ Define fallback behavior
   - use raw edit tools only when no semantic tool exists
   - preserve repo contract when the semantic layer cannot interpret a file
   - support dry-run / preview mode

### Phase 2 decisions (2026-03-18)

#### 1. Change classes belong in the capability contract

The repo-side capability manifest should declare the same three change classes used by `README.md` and `meta/update-guidelines.md`: `automatic`, `proposed`, and `protected`. Each class now carries explicit app-facing metadata:

- approval rule
- user-awareness requirement
- expected UI affordance
- read-only/deferred behavior

This makes governance discoverable by the app instead of forcing Codex to reconstruct it from prose during each write.

#### 2. Semantic operations now map cleanly onto repo change policy

Current mapping in the prototype:

- **Automatic**: routine plan progression, `_unverified/` knowledge-file creation, scratchpad appends, chat-summary writes, and review-queue flagging
- **Proposed**: plan creation, identity updates, and knowledge promotion / demotion / archival
- **Protected**: no current repo-local semantic tool yet; protected paths still require a higher-friction approval path or future dedicated operations

The notable edge case is `memory_flag_for_review`: it targets `meta/review-queue.md`, but the operation is intentionally narrow and machine-generated, so the contract treats it as an automatic governance exception rather than as a general protected meta edit.

#### 3. Raw fallback tools inherit, not redefine, governance class

The prototype contract now states that raw write/edit/move/delete tools do not get their own independent approval tier. They inherit the change class of the semantic operation or caller intent, require preview for `proposed` and `protected` work, and fall back to deferred-action summaries in read-only contexts.

#### 4. Approval UX should be contract-driven, not prompt-only

The repo-side prototype now declares an explicit `approval_ux` contract for `proposed` and `protected` writes so the desktop layer can render the same preview shape consistently across semantic operations and raw fallbacks. The preview must include:

- concise change summary
- reasoning for the write
- target files
- invariant effects
- commit-category suggestion
- fallback behavior when the app must defer or drop to raw tools

The prototype also now distinguishes the two confirmation flows:

- **Proposed writes** use a lightweight preview with explicit confirmation before apply, plus `open_files` and `defer` actions
- **Protected writes** use a higher-friction approval step with explicit protected-change framing, `open_files` / `defer` / `cancel` actions, and a blocked outcome until the user approves

To support preview fidelity, each semantic operation now carries a `commit_category_hint`, and the capability resolver validates both the approval UX contract and those hints.

#### 5. Fallback behavior should be explicit and scenario-based

The governed-write contract now distinguishes four fallback scenarios instead of treating fallback as one vague escape hatch:

- **`semantic_gap`**: use raw tools only when no semantic operation exists yet, and only when the caller still preserves the repo contract
- **`uninterpretable_target`**: do not drop to raw writes when the semantic layer cannot model the file or repo shape confidently; defer instead and surface a contract warning
- **`preview_only`**: support dry-run behavior that returns the same preview shape without writing
- **`read_only`**: return a deferred-action summary instead of attempting writes when the runtime cannot write

Repo-side prototype: `HUMANS/tooling/agent-memory-capabilities.toml` now declares these fallback profiles directly, gap operations point to the `semantic_gap` profile, and `HUMANS/tooling/scripts/resolve_memory_capabilities.py` plus `HUMANS/tooling/tests/test_memory_capabilities.py` validate the profile contract. This keeps raw fallback narrow, auditable, and distinct from contract-preserving defer paths.

### Phase 3 — Desktop and MCP integration · ☐ 2/3 complete

7. ☑ Decide integration boundary
   - Codex-native semantic tools
   - MCP-discovered semantic tools
   - hybrid model

8. ☑ Define repo capability discovery
   - how the app detects that a repo exposes semantic memory operations
   - versioning and compatibility checks
   - graceful degradation when only read tools exist

9. ☐ Add structured UI feedback
   - operation preview
   - changed-file summary
   - resulting next action or plan state

### Phase 3 decisions (2026-03-18)

#### 1. The integration boundary should be hybrid, with repo-local MCP as the semantic authority

Codex desktop should not hardcode repo-specific semantic write behavior as its default path. The app should prefer repo-local MCP semantic tools whenever a repo declares them, because those tools own the repo's invariants and can evolve in git with the repo itself. The desktop layer still remains responsible for the user-facing write experience.

Repo-side prototype: `HUMANS/tooling/agent-memory-capabilities.toml` now declares an explicit `integration_boundary` section with:

- `model = "hybrid"`
- preference for `repo_local_semantic_mcp`
- native semantic scope limited to generic behavior
- an explicit degradation order from repo-local semantics to desktop preview/policy handling to raw fallback or defer

#### 2. Responsibility split should be explicit

The boundary is only useful if ownership is unambiguous:

- **Desktop owns** approval UX, change-class enforcement, capability discovery, preview rendering, result presentation, and fallback selection
- **Repo-local MCP owns** semantic execution, repo-specific invariants, schema validation, the authoritative mutation itself, and structured post-write state
- **Codex-native fallback** remains narrow: generic preview support, raw-tool orchestration, and deferred-action summaries when no repo-local semantic path exists

This keeps product UX consistent without moving repo-specific correctness logic into the app.

#### 3. Native semantics should stay generic unless a repo contract exists

The prototype now makes a stricter claim: Codex desktop may ship generic governed-write behavior, but it should not invent repo-specific semantic mutations unless the repo exposes a contract for them. That avoids silent schema drift and keeps the repo contract auditable instead of prompt-derived.

Repo-side prototype: `HUMANS/tooling/scripts/resolve_memory_capabilities.py` and `HUMANS/tooling/tests/test_memory_capabilities.py` now validate the hybrid boundary and its required ownership markers.

#### 4. Capability discovery should be manifest-first and runtime-verified

Desktop should detect repo-specific memory semantics from a well-known manifest path, not from prompt heuristics or file-tree guesses. Repo-side prototype: `HUMANS/tooling/agent-memory-capabilities.toml` now declares a `capability_discovery` contract with:

- the well-known manifest path the app should probe first
- supported manifest versions and required `kind`
- a required MCP entrypoint for repo-local semantic authority
- minimum read tools for read-only compatibility
- minimum semantic tools for enabling repo-local governed writes
- the expected degradation targets for semantic, read-only, and incompatible runtimes

The resolver now classifies runtime state into three concrete modes:

- **`semantic`** when the manifest is compatible and the runtime exports the minimum semantic tool set
- **`read_only`** when the manifest is compatible and the runtime exposes only the minimum read contract
- **`fallback`** when compatibility checks fail or the runtime exposes a partial semantic surface that is too weak to trust

That gives Codex desktop a stable decision point for choosing between repo-local semantic MCP, native preview/policy handling, or raw fallback/defer behavior without hardcoding repo-specific invariants into the app.

### Phase 4 — Hardening and evaluation · ☐ 0/2 complete

10. ☐ Build test coverage around invariants
   - frontmatter round trips
   - summary sync
   - protected-change blocking
   - concurrent write conflict handling

11. ☐ Define rollout metrics
   - semantic write success rate
   - number of raw-edit fallbacks
   - invariant drift incidents prevented

---

## Open questions

- How should protected-change approvals appear in Codex desktop without interrupting flow too aggressively?
- Should semantic writes auto-commit, stage only, or support both modes?
- How much repo-specific schema knowledge should Codex ship with vs. discover dynamically?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: governed, invariant-aware memory writes |
| 2026-03-18 | Added `HUMANS/tooling/agent-memory-capabilities.toml` plus a resolver and tests to define the semantic tool set, invariant ownership model, shared result envelope, and current desktop-surface gaps |
| 2026-03-18 | Extended the capability contract with `automatic` / `proposed` / `protected` change classes, read-only deferred behavior, raw-fallback inheritance rules, and validator coverage for operation-to-class mapping |
| 2026-03-18 | Completed Design approval and confirmation UX (codex-desktop-governed-memory-writes 5/11) |
| 2026-03-18 | Defined explicit fallback profiles for semantic gaps, uninterpretable targets, preview-only runs, and read-only contexts; completed Phase 2 (codex-desktop-governed-memory-writes 6/11) |
| 2026-03-18 | Chose a hybrid integration boundary: repo-local MCP remains the semantic authority, Codex desktop owns UX/policy/discovery, and native semantics stay generic unless the repo declares a contract |
| 2026-03-18 | Completed Decide integration boundary (codex-desktop-governed-memory-writes 7/11) |
| 2026-03-18 | Added a manifest-driven capability discovery contract plus resolver classification for semantic/read-only/fallback runtimes; completed Define repo capability discovery (codex-desktop-governed-memory-writes 8/11) |

---

## Notes

- This plan overlaps with `agent-memory-mcp.md` but is broader: that file is a repo-local MCP plan, while this plan is for Codex desktop product support.
- The success criterion is fewer "memory write by convention" operations and more "memory write by validated semantic contract."
