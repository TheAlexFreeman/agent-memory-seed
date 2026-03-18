---
source: agent-generated
type: implementation-plan
origin_session: manual
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Phase 1 — define the semantic memory operation set and invariant ownership model"
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

### Phase 1 — Semantic write model · ☐ 0/3 complete

1. ☐ Define the minimal semantic tool set
   - highest-frequency memory operations first
   - clear separation between semantic tools and raw fallback tools
   - repo-agnostic core plus repo-specific extensions

2. ☐ Define invariant ownership per operation
   - which tool updates frontmatter
   - which tool updates `SUMMARY.md`
   - which tool logs ACCESS or review-queue artifacts

3. ☐ Define result and error taxonomy
   - conflict
   - validation failure
   - already-done
   - protected-change blocked
   - partial sync warning

### Phase 2 — Governance and policy integration · ☐ 0/3 complete

4. ☐ Map repo governance to app-side affordances
   - automatic changes
   - proposed changes
   - protected changes
   - read-only/deferred action mode

5. ☐ Design approval and confirmation UX
   - semantic preview before protected writes
   - clear explanation of what files and invariants will change
   - explicit commit-category suggestions where applicable

6. ☐ Define fallback behavior
   - use raw edit tools only when no semantic tool exists
   - preserve repo contract when the semantic layer cannot interpret a file
   - support dry-run / preview mode

### Phase 3 — Desktop and MCP integration · ☐ 0/3 complete

7. ☐ Decide integration boundary
   - Codex-native semantic tools
   - MCP-discovered semantic tools
   - hybrid model

8. ☐ Define repo capability discovery
   - how the app detects that a repo exposes semantic memory operations
   - versioning and compatibility checks
   - graceful degradation when only read tools exist

9. ☐ Add structured UI feedback
   - operation preview
   - changed-file summary
   - resulting next action or plan state

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

- Should the app own the semantic operations directly, or should it always delegate to repo-local MCP tools when present?
- How should protected-change approvals appear in Codex desktop without interrupting flow too aggressively?
- Should semantic writes auto-commit, stage only, or support both modes?
- How much repo-specific schema knowledge should Codex ship with vs. discover dynamically?

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created from identified Codex desktop gap: governed, invariant-aware memory writes |

---

## Notes

- This plan overlaps with `agent-memory-mcp.md` but is broader: that file is a repo-local MCP plan, while this plan is for Codex desktop product support.
- The success criterion is fewer "memory write by convention" operations and more "memory write by validated semantic contract."
