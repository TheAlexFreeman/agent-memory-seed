---
created: '2026-03-20'
last_verified: '2026-03-20'
next_action: 'Phase 3: define a shared preview envelope and add preview support to proposed/protected semantic writes.'
origin_session: manual
source: agent-generated
status: active
title: MCP Agent-Friendliness Improvements
trust: medium
type: implementation-plan
category: build
---

# Implementation Plan: MCP Agent-Friendliness Improvements

## Goals

Improve the repo-local MCP surface so capable agents can choose the right operation more reliably, preview risky changes more consistently, follow common memory workflows with fewer round trips, and reason about provenance and policy without reconstructing the contract from multiple files. The plan prioritizes operational leverage over raw feature count.

This plan implements the recommendations from the 2026-03-20 architecture and governance review:
- fix remaining semantic inconsistencies in the current tool surface
- add machine-readable routing and policy-state helpers
- make preview a first-class governed-write capability
- compress common workflows into semantic bundle tools
- reduce flat-tool discovery burden
- expose stable read/navigation state through MCP-native resources and prompts
- strengthen provenance and large-file retrieval ergonomics

Architectural guardrails from `README.md` and `meta/quick-reference.md` apply throughout: every phase must improve or at least preserve **consistency**, **user-friendliness**, and **context efficiency**.

---

## Problem statement

The current MCP tooling is directionally strong but still imposes too much reasoning burden on the caller.

**Gap 1 — semantic parity is incomplete.**
The single-file promotion path can now auto-create missing summary sections, but the batch path still relies on pre-existing sections. This leaves one of the highest-value workflows with inconsistent behavior and avoidable warnings.

**Gap 2 — tool selection remains too implicit.**
The server exposes a rich semantic surface, but callers still infer the right tool from names, docstrings, and scattered governance context. There is no first-class routing layer that answers "what operation should I call for this intent, and why?"

**Gap 3 — preview is mostly host-owned rather than server-native.**
The capabilities manifest clearly distinguishes automatic, proposed, and protected changes, but semantic write tools do not yet expose one uniform preview contract. This weakens portability across MCP hosts and makes safe fallback behavior harder.

**Gap 4 — common workflows still require too many round trips.**
Reviewing unverified content, preparing periodic review, or bootstrapping a session still involves orchestration across multiple tools when the workflow shape is already known.

**Gap 5 — the flat tool surface is approaching discovery limits.**
The MCP surface is now large enough that discovery itself is becoming a usability problem. The repo needs profiles or dynamic subsets rather than continuing to expose everything as one undifferentiated registry.

**Gap 6 — the server underuses MCP-native read/navigation primitives.**
Many repo-state queries are really resources or reusable prompts rather than tool calls. Keeping everything in tools increases token cost and selection ambiguity.

**Gap 7 — provenance and large-file reads are still harder than they need to be.**
Trust reasoning would be stronger with more queryable provenance fields, and large-file inspection still degrades from a semantic read into temp-file plumbing rather than structured extraction.

---

## Phases

### Phase 1 — Contract unification and parity fixes

*Goal: remove obvious inconsistencies before adding more surface area.*

**1.1 Unify summary-update behavior across promotion paths**
Refactor the shared summary insertion logic so `memory_promote_knowledge_batch` and `memory_promote_knowledge_subtree` can create missing target sections the same way the single-file tool does. Avoid one-off copies of insertion logic.

**1.2 Extract shared governed-operation metadata helpers**
Introduce one internal representation for operation group, change class, preview availability, fallback behavior, and commit model. Reuse it in tool registration and capability-manifest generation where practical.

**1.3 Tighten semantic docstring cross-linking**
Audit high-traffic semantic tools and add brief "use this when / use X instead when" guidance plus nearby alternatives. Prioritize promotion, aggregation, review, plan, and session-recording tools.

**1.4 Add regression coverage for parity behaviors**
Write focused tests for missing-section creation, consistent warnings, and identical result-shape guarantees across single, batch, and subtree promotion flows.

**1.5 Record remaining inconsistencies as explicit backlog**
If any contract mismatches cannot be closed in this phase, add them to the plan notes with file-level follow-up targets rather than leaving them implicit.

Checklist:
- [x] 1.1 Refactor shared summary-update helper for all promotion variants
- [x] 1.2 Introduce shared governed-operation metadata model
- [x] 1.3 Improve docstring disambiguation on high-traffic semantic tools
- [x] 1.4 Add regression tests for promotion-path parity
- [x] 1.5 Document any deferred contract mismatches

---

### Phase 2 — Intent routing and compiled policy state

*Goal: let agents ask the server what to do instead of inferring it every time.*

**2.1 Implement `memory_route_intent`**
Add a read-only tool that accepts a short natural-language intent plus optional target path and returns the recommended operation, likely alternates, change class, and rationale.

**2.2 Implement `memory_get_policy_state`**
Add a read-only tool that resolves the current contract for an operation/path pair: change class, approval requirement, preview requirement, trust constraints, protected-surface status, and read-only fallback behavior.

**2.3 Reuse manifest and governance sources, not a shadow policy layer**
The new tools should compile state from the capability manifest and authoritative governance docs rather than introducing a second disconnected ruleset.

**2.4 Define failure modes clearly**
When the route is ambiguous, return ranked candidates plus uncertainty reasons instead of pretending certainty. When a target is outside the semantic model, return the contract-preserving fallback path.

**2.5 Add contract tests for representative intents**
Cover plan creation, proposed knowledge promotion, protected meta edits, automatic ACCESS logging, and uninterpretable targets.

Checklist:
- [x] 2.1 Implement `memory_route_intent`
- [x] 2.2 Implement `memory_get_policy_state`
- [x] 2.3 Compile results from manifest + governance, not duplicated constants
- [x] 2.4 Add ambiguity and fallback result handling
- [x] 2.5 Add focused routing/policy tests for representative operations

---

### Phase 3 — Universal preview contract for governed writes

*Goal: make safe write planning portable across hosts and predictable across tools.*

**3.1 Define a preview envelope**
Standardize preview output fields for all proposed/protected semantic writes: summary, reasoning, target files, invariant effects, commit suggestion, warnings, and resulting state preview.

**3.2 Add `dry_run` or `preview` support to proposed/protected semantic tools**
Prioritize `memory_create_plan`, knowledge promotion/demotion/archive operations, review-queue resolution, periodic review recording, skill updates, identity updates, and revert flows.

**3.3 Preserve existing apply semantics**
Preview mode must not stage, move, or commit. Apply mode must remain backward-compatible where possible, with additive result fields instead of breaking schema changes.

**3.4 Expose preview availability in the capability surface**
Update the capabilities manifest and any derived tool summaries so hosts can discover preview support rather than hardcoding it.

**3.5 Add preview/apply equivalence tests**
For representative tools, assert that preview accurately predicts target files, warnings, and commit metadata seen on the eventual apply path.

Checklist:
- [ ] 3.1 Define shared preview envelope/result schema
- [ ] 3.2 Add preview mode to proposed/protected semantic tools
- [ ] 3.3 Keep apply semantics backward-compatible
- [ ] 3.4 Publish preview support in capabilities output
- [ ] 3.5 Add preview-vs-apply equivalence tests

---

### Phase 4 — Workflow bundle tools

*Goal: compress known multi-step workflows into fewer semantic calls.*

**4.1 Implement `memory_session_bootstrap`**
Return one compact payload for the returning-session start path: capability status, session health, active plans, relevant review warnings, and recommended next checks.

**4.2 Implement review/preparation bundle tools**
Add helpers such as `memory_prepare_unverified_review`, `memory_prepare_promotion_batch`, and `memory_prepare_periodic_review` that gather the minimal high-signal state for each workflow.

**4.3 Keep bundle tools read-only and compositional**
These tools should not replace the semantic write surface. They should orchestrate existing read-side state into workflow-shaped responses.

**4.4 Add response-size budgets**
Bundle tools must stay compact enough to help rather than overwhelm. Add explicit truncation/summarization rules plus tests for large repos.

Checklist:
- [ ] 4.1 Implement `memory_session_bootstrap`
- [ ] 4.2 Implement unverified-review, promotion-prep, and periodic-review bundle tools
- [ ] 4.3 Keep bundle tools read-only and layered over existing semantics
- [ ] 4.4 Add compactness/truncation rules and tests

---

### Phase 5 — Tool-surface shaping and dynamic profiles

*Goal: reduce flat-tool discovery burden without removing power.*

**5.1 Define tool profiles**
Create explicit profile groupings such as `core`, `curation`, `governance`, `plans`, `session`, and `forensics`. Each profile should have a small, coherent activation story.

**5.2 Implement selective tool exposure or profile reporting**
Depending on MCP client constraints, either expose dynamic subsets directly or add server-side profile metadata that hosts can use to request or display narrowed views.

**5.3 Add `listChanged` support if the runtime can honor it safely**
If profile switching changes the live surface, declare and emit tool-list change notifications in a standards-compliant way.

**5.4 Update the capabilities manifest and docs**
Publish profile boundaries, host expectations, and degradation behavior. Make sure the compact path still works for clients that cannot consume profiles.

Checklist:
- [ ] 5.1 Define coherent tool profiles and selection rules
- [ ] 5.2 Implement profile-aware exposure or profile metadata reporting
- [ ] 5.3 Add `listChanged` support where runtime-safe
- [ ] 5.4 Update capability docs and fallback behavior for non-profile-aware hosts

---

### Phase 6 — MCP-native resources and prompts

*Goal: move stable read/navigation state out of ad hoc tool calls where MCP already has a better primitive.*

**6.1 Add resources for stable repo state**
Expose resources for capability summary, policy summary, session-health snapshot, and active-plan summary. Keep them read-mostly and cheap to retrieve.

**6.2 Add prompts for recurring governed workflows**
Expose reusable prompts for unverified review, periodic review, governed promotion preview, and session wrap-up. Prompts should help hosts structure user-facing workflows without embedding policy prose in every turn.

**6.3 Document resources-vs-tools boundaries**
Clarify when callers should use resources, prompts, or tools. Avoid duplicating full results across multiple primitives unless there is a clear client-compatibility reason.

**6.4 Add integration tests or inspector fixtures**
Verify that resources and prompts enumerate cleanly and remain consistent with the live capabilities contract.

Checklist:
- [ ] 6.1 Add stable MCP resources for capability, policy, health, and active-plan state
- [ ] 6.2 Add prompts for review, promotion preview, periodic review, and session wrap-up workflows
- [ ] 6.3 Document resources-vs-tools boundaries
- [ ] 6.4 Add integration coverage for resource/prompt enumeration and consistency

---

### Phase 7 — Provenance enrichment and structured large-file reads

*Goal: make trust reasoning and large-file retrieval more semantic and less manual.*

**7.1 Extend provenance fields additively**
Add optional fields such as `origin_commit`, `produced_by`, `verified_by`, and `inputs` or `related_sources` where they materially improve queryability without forcing a full backfill migration.

**7.2 Expose provenance more directly in read tools**
Update file/provenance tools to surface the new fields when present and summarize lineage in a way that supports trust-weighted retrieval.

**7.3 Implement structured extraction for large files**
Add a read-only tool such as `memory_read_sections` or `memory_extract_file` that can return heading outlines, selected sections, preview windows, and frontmatter without forcing callers through temp-file handling.

**7.4 Add migration and compatibility tests**
Ensure older files without the new fields remain valid and that the new structured-read flow works on both frontmatter-heavy and plain markdown files.

Checklist:
- [ ] 7.1 Add optional provenance fields and schema guidance
- [ ] 7.2 Surface enriched provenance through read tools
- [ ] 7.3 Implement structured large-file extraction tool
- [ ] 7.4 Add backward-compatibility and extraction tests

---

## Implementation order and dependencies

1. **Phase 1 first.** The remaining semantic inconsistency should be closed before new routing or preview layers are added.
2. **Phase 2 next.** Intent routing and compiled policy state are the highest-leverage usability additions once the surface is internally consistent.
3. **Phase 3 after Phase 2.** The preview envelope should reuse the operation metadata introduced earlier.
4. **Phase 4 after Phase 2, parallelizable with Phase 3.** Workflow bundle tools depend on routing/policy helpers but can ship independently from universal preview.
5. **Phase 5 after Phase 2.** Tool profiling should be informed by real routing patterns, not guessed upfront.
6. **Phase 6 after Phase 5.** Resources/prompts should reflect the shaped surface and stable workflow boundaries.
7. **Phase 7 last.** Provenance enrichment and structured extraction are valuable, but they are lower-leverage than routing, preview, and workflow compression.

---

## Progress tracking

- [ ] 1.1 Refactor shared summary-update helper for all promotion variants
- [ ] 1.2 Introduce shared governed-operation metadata model
- [ ] 1.3 Improve docstring disambiguation on high-traffic semantic tools
- [ ] 1.4 Add regression tests for promotion-path parity
- [ ] 1.5 Document any deferred contract mismatches
- [ ] 2.1 Implement `memory_route_intent`
- [ ] 2.2 Implement `memory_get_policy_state`
- [ ] 2.3 Compile results from manifest + governance, not duplicated constants
- [ ] 2.4 Add ambiguity and fallback result handling
- [ ] 2.5 Add focused routing/policy tests for representative operations
- [ ] 3.1 Define shared preview envelope/result schema
- [ ] 3.2 Add preview mode to proposed/protected semantic tools
- [ ] 3.3 Keep apply semantics backward-compatible
- [ ] 3.4 Publish preview support in capabilities output
- [ ] 3.5 Add preview-vs-apply equivalence tests
- [ ] 4.1 Implement `memory_session_bootstrap`
- [ ] 4.2 Implement unverified-review, promotion-prep, and periodic-review bundle tools
- [ ] 4.3 Keep bundle tools read-only and layered over existing semantics
- [ ] 4.4 Add compactness/truncation rules and tests
- [ ] 5.1 Define coherent tool profiles and selection rules
- [ ] 5.2 Implement profile-aware exposure or profile metadata reporting
- [ ] 5.3 Add `listChanged` support where runtime-safe
- [ ] 5.4 Update capability docs and fallback behavior for non-profile-aware hosts
- [ ] 6.1 Add stable MCP resources for capability, policy, health, and active-plan state
- [ ] 6.2 Add prompts for review, promotion preview, periodic review, and session wrap-up workflows
- [ ] 6.3 Document resources-vs-tools boundaries
- [ ] 6.4 Add integration coverage for resource/prompt enumeration and consistency
- [ ] 7.1 Add optional provenance fields and schema guidance
- [ ] 7.2 Surface enriched provenance through read tools
- [ ] 7.3 Implement structured large-file extraction tool
- [ ] 7.4 Add backward-compatibility and extraction tests

**Progress:** 10/31 items complete

---

## Acceptance criteria

- An agent can ask one tool which governed operation fits a goal and get a correct, policy-aware answer.
- Every proposed/protected semantic write can return a no-side-effect preview with consistent structure.
- Common workflows that currently require 4–10 MCP round trips can be started with a single read-only bundle tool.
- Hosts that understand profiles can see a narrowed tool surface; hosts that do not still work correctly.
- Stable state that is fundamentally navigational is available as resources or prompts rather than only tools.
- Provenance becomes more queryable without breaking old files.
- Large-file reads no longer degrade into temp-file plumbing for common inspection tasks.

---

## Design constraints

- Preserve the single-writer governed-mutation model; no phase should broaden raw write access just to improve ergonomics.
- Prefer additive schema changes and result fields over breaking changes.
- Keep compact returning sessions compact: new bundle tools and resources must summarize rather than dump.
- Maintain one authority chain. Routing/policy helpers may compile existing rules, not redefine them.
- Do not let resources or prompts become a second hidden governance layer.
- If client support for dynamic tool subsets or prompts/resources is too inconsistent, ship server-side metadata first and keep behavior correct in the fallback path.

---

## Notes

- 2026-03-20: Plan created after the architecture/governance review identified four immediate findings and seven concrete improvement tracks. Priority is weighted toward reducing agent reasoning overhead, not maximizing the number of new primitives.
- 2026-03-20: Phase 1 intentionally starts with a small parity fix because the current promotion inconsistency is both real and easy to regress if higher-level routing or preview work lands first.
- 2026-03-20: Resources/prompts and dynamic profiles are explicitly downstream of contract unification because they should expose a stable semantic model rather than locking in current inconsistencies.
- 2026-03-20: Completed Phase 1. Promotion paths now share summary-update helpers, batch promotion auto-creates missing target sections like the single/subtree paths, high-traffic knowledge-tool docstrings now disambiguate when to use each operation, and focused regression coverage locks in the parity behavior. No additional Phase 1 contract mismatches were left open.
- 2026-03-20: Completed Phase 2. Added `memory_route_intent` and `memory_get_policy_state` to the Tier 0 read surface, compiled policy responses from the capability manifest plus governance-file signals, handled ambiguous and uninterpretable targets with explicit fallback state, and added focused tests for plan creation, knowledge promotion, protected meta paths, automatic ACCESS logging, and unsupported targets.