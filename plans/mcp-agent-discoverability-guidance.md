---
type: build
category: build
status: draft
next_action: Execute Phase 1 — Server name discovery doc and tool description disambiguation
last_verified: 2026-03-21
trust: medium
---

# MCP Agent Discoverability and Guidance Improvements

## Scope

Address friction points identified during the 2026-03-21 AI frontier promotion session. Prioritize highest-leverage improvements: server discovery, tool-relationship clarity, routing accuracy for promotion workflows, and warning clarity. Build on the existing mcp-agent-friendliness surface (`memory_route_intent`, `memory_get_policy_state`, workflow bundles).

## Problem statement

**Server name discovery.** Cursor exposes the MCP server under a project-namespaced identifier (e.g. `project-0-agent-memory-seed-agent-memory`), not the config key (`agent-memory`). Agents must fail once to discover the correct name.

**Tool relationship ambiguity.** `memory_list_pending_reviews` and `memory_prepare_unverified_review` both relate to unverified content but serve different purposes. Descriptions do not clearly distinguish "review queue verdicts" from "survey folder for promotion decisions."

**Routing prefers batch over subtree.** For intents like "promote all unverified ai/frontier", `memory_route_intent` recommends `memory_promote_knowledge_batch` instead of `memory_promote_knowledge_subtree`. Subtree is the right tool for full-folder moves with nested structure.

**Opaque promotion warnings.** Subtree promotion warns "Section not found in knowledge/_unverified/SUMMARY.md" without clarifying that the operation succeeded and no action is required.

**No cheap full-file list for batch prep.** `memory_prepare_unverified_review` truncates (e.g. 12 of 31 files). For batch promotion with manual selection, agents cannot cheaply see all paths.

---

## Phases

### Phase 1 — Server name discovery and tool disambiguation (high leverage, low effort)

**1.1 Add MCP server discovery note to quick-reference**

In `meta/quick-reference.md`, add a compact "MCP discovery" note: Cursor may expose the agent-memory server under a project-prefixed name; if a tool call fails with "server does not exist," use the server name from the error's "Available servers" list.

**1.2 Clarify memory_list_pending_reviews vs memory_prepare_unverified_review**

- `memory_list_pending_reviews`: Add "Use when: You need the latest approve/defer/reject verdicts for files already in the review workflow. Use memory_prepare_unverified_review instead when surveying a folder to decide what to promote."
- `memory_prepare_unverified_review`: Add "Use when: Surveying an unverified folder to decide promote vs defer. Returns a digest with extracts and recommended operation. Use memory_list_pending_reviews for verdict status of files already in the queue."

**1.3 Add subtree vs batch disambiguation to promotion tools**

- `memory_promote_knowledge_subtree`: Add "Use when the source is a nested folder hierarchy; preserves structure. Use memory_promote_knowledge_batch when promoting a flat list of specific file paths."
- `memory_promote_knowledge_batch`: Add "Use when promoting a flat list of specific paths. Use memory_promote_knowledge_subtree when moving an entire nested folder tree."

**Checklist:**
- [ ] 1.1 Add MCP server discovery note to meta/quick-reference.md
- [ ] 1.2 Update memory_list_pending_reviews and memory_prepare_unverified_review descriptions
- [ ] 1.3 Add subtree vs batch disambiguation to promotion tool descriptions

---

### Phase 2 — Routing accuracy for promotion intents (high leverage, medium effort)

**2.1 Extend memory_route_intent for subtree vs batch**

When intent suggests "promote all" or "promote entire folder" and path is a directory, check if the path has nested subdirectories. If yes, recommend `memory_promote_knowledge_subtree` with subtree rationale; otherwise recommend batch.

**2.2 Add workflow hint to route result**

When recommending promotion, include a short `workflow_hint` field: e.g. "1) memory_prepare_unverified_review(folder_path) for digest; 2) memory_promote_knowledge_subtree(source, dest, dry_run=True); 3) memory_promote_knowledge_subtree(..., dry_run=False)".

**2.3 Add regression test for subtree vs batch routing**

Cover: "promote all unverified ai/frontier" → subtree; "promote these 5 specific files" → batch.

**Checklist:**
- [ ] 2.1 Implement subtree vs batch discrimination in memory_route_intent
- [ ] 2.2 Add workflow_hint to promotion route results
- [ ] 2.3 Add routing tests for subtree and batch intents

---

### Phase 3 — Warning clarity and full-file list (medium leverage)

**3.1 Clarify subtree promotion warning**

Change the "Section not found in source SUMMARY" warning to: "No matching section in source SUMMARY; target SUMMARY was updated. No action required." Or suppress when the operation succeeded and target was updated.

**3.2 Add paths-only option for unverified enumeration**

Add optional parameter `paths_only: bool = False` to `memory_prepare_unverified_review`, or a lightweight `memory_list_unverified_paths(folder_path)` tool. When paths_only is true / when using the new tool, return only file paths (no extracts), enabling cheap full enumeration for folders with many files.

**Checklist:**
- [ ] 3.1 Improve subtree promotion section-not-found warning
- [ ] 3.2 Add paths_only option or memory_list_unverified_paths tool

---

## Success criteria

- Agents can discover the correct MCP server name without trial-and-error.
- Tool descriptions reduce confusion between list_pending_reviews and prepare_unverified_review.
- `memory_route_intent` recommends subtree for full-folder promotion intents.
- Promotion workflow is discoverable via route result `workflow_hint`.
- Subtree promotion warnings are actionable or clearly non-actionable.
- Agents can enumerate full file list for unverified folders when needed.

---

## References

- `plans/mcp-agent-friendliness-improvements.md` — completed; memory_route_intent, workflow bundles, tool profiles
- `plans/mcp-unverified-review-workflow-improvements.md` — completed; prepare_unverified_review, subtree promotion
- `meta/quick-reference.md` — session routing, compact path
- `HUMANS/tooling/agent-memory-capabilities.toml` — capability manifest
