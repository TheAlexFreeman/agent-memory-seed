---
created: '2026-03-21'
last_verified: '2026-03-21'
next_action: 'All planned phases complete.'
origin_session: manual
source: agent-generated
status: complete
title: MCP Agent Discoverability and Guidance Improvements
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: MCP Agent Discoverability and Guidance Improvements

## Scope

Tighten the last remaining MCP discoverability and workflow-guidance gaps that still make agents reconstruct behavior from implementation details. The plan now focuses only on gaps still present in the live code after the 2026-03-21 review of the knowledge base, capability manifest, validator output, and current tool implementations.

## Review findings

The original plan drifted behind the implementation.

Already landed in the live MCP surface:
- `memory_review_unverified`, `memory_prepare_unverified_review`, and `memory_list_pending_reviews` already exist and cover the review/verdict split.
- `memory_promote_knowledge_subtree` and `memory_promote_knowledge_batch` already carry subtree-vs-flat-list guidance.
- `memory_route_intent` already prefers subtree when the target is a directory and the intent contains nested-subtree wording.
- The unverified-review prompt already tells callers when to use single-file, batch, or subtree promotion.

Remaining follow-up after implementation:
- compact-startup budget pressure in `plans/SUMMARY.md` still exists but is outside this plan's scoped deliverables.

Related knowledge-base review findings to keep in view but not expand scope around here:
- Validator warnings show 51 unverified low-trust files and multiple legacy plan-frontmatter issues.
- Compact startup summaries are over budget, especially `plans/SUMMARY.md`.

---

## Phases

### Phase 1 — Re-baseline against the live MCP surface (complete)

This phase is already complete and replaces the stale assumptions in the original draft.

Checklist:
- [x] Audit the live capability manifest and tool registry against the draft plan
- [x] Confirm review-verdict vs review-digest tools already exist
- [x] Confirm subtree-vs-batch guidance already exists in the semantic promotion tools
- [x] Confirm route heuristics and prompts already cover basic subtree selection

### Phase 2 — Discovery note and workflow guidance (complete)

**2.1 Add MCP discovery note to quick-reference**

Add a compact note to `meta/quick-reference.md`: hosts may expose the Engram server under a project-prefixed name; if a call fails with a server-name error, use the identifier shown in the host's available-server list.

**2.2 Add workflow hints to route results**

Extend `memory_route_intent` so promotion-related recommendations include a short `workflow_hint` field. Keep it compact and operational, for example: review digest -> dry run -> apply.

**2.3 Make promotion prep subtree-aware**

Update `memory_prepare_promotion_batch` so directory inputs with nested content can suggest `memory_promote_knowledge_subtree` instead of defaulting to the flat batch path.

**2.4 Add focused regression coverage**

Add tests that cover nested-folder promotion routing and subtree-aware promotion-prep output.

Checklist:
- [x] 2.1 Add the quick-reference MCP discovery note
- [x] 2.2 Add `workflow_hint` to promotion route results
- [x] 2.3 Make `memory_prepare_promotion_batch` surface subtree when appropriate
- [x] 2.4 Add regression tests for route-result and promotion-prep guidance

### Phase 3 — Enumeration and reliability fixes (high leverage)

**3.1 Add cheap full-path enumeration for unverified review**

Add either a `paths_only` mode to `memory_prepare_unverified_review` or a dedicated lightweight listing tool so callers can enumerate full review candidates without extracts.

**3.2 Clarify or suppress non-actionable subtree warnings**

If subtree promotion succeeds and only the source summary section is absent, make the warning explicitly non-actionable or suppress it.

**3.3 Fix `memory_run_periodic_review` runtime failure**

Repair the current type error and add regression coverage so periodic-review preparation remains a usable discoverability surface.

Checklist:
- [x] 3.1 Add a full-path enumeration mode for unverified review
- [x] 3.2 Make subtree-promotion warnings clearly actionable or clearly ignorable
- [x] 3.3 Fix `memory_run_periodic_review` and add a regression test

---

## Success criteria

- Agents can discover the correct Engram MCP server name without trial-and-error.
- Promotion-related route results provide a concrete next-step workflow, not just a tool name.
- Promotion-prep outputs distinguish flat batches from nested subtree moves.
- Agents can cheaply enumerate all unverified candidate paths when manual selection is needed.
- Periodic-review guidance tools return usable reports instead of runtime errors.

Status: complete.

---

## References

- `plans/mcp-agent-friendliness-improvements.md` — completed baseline for routing, previews, workflow bundles, tool profiles, resources, prompts, and provenance reads
- `plans/mcp-unverified-review-workflow-improvements.md` — completed baseline for review digests and subtree promotion
- `meta/quick-reference.md` — compact startup routing surface and the right home for discovery notes
- `knowledge/SUMMARY.md` — current promoted-knowledge surface reviewed through Engram MCP during this re-baseline
- `HUMANS/tooling/agent-memory-capabilities.toml` — repo capability manifest reflected by `memory_get_capabilities`
