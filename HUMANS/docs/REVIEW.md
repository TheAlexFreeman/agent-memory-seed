# Comprehensive Review: Engram Memory System

I reviewed all governance documents, the MCP server codebase, bootstrap configuration, setup flows, SUMMARY files, and cross-references. Here is the analysis along the three architectural dimensions you define as first-order constraints.

---

## I. Consistency

### A. Strong points

- **Threshold single-source-of-truth is well-maintained.** Every governance doc defers to quick-reference.md for active values. No hardcoded threshold numbers contradict the authoritative source.
- **ACCESS lifecycle scope is consistent everywhere.** All four documents that mention it agree on the six tracked namespaces and meta exclusion.
- **Token budgets agree** across README.md, quick-reference.md, and agent-bootstrap.toml.
- **Protected directory policy is aligned** across path_policy.py, README.md, and update-guidelines.md.
- **SUMMARY.md files all exist** — no broken references in the routing chain.

### B. Issues found

**1. Commit prefix documentation gap** (medium severity)

update-guidelines.md lists 6 commit prefixes: `[chat]`, `[knowledge]`, `[skill]`, `[identity]`, `[curation]`, `[system]`. The code in path_policy.py enforces 9: the documented six plus `[plan]`, `[scratchpad]`, and `[access]`. Agent or human committers could be confused about whether `[plan]` and `[scratchpad]` are valid categories.

**2. `automation` mode defined in TOML but absent from quick-reference.md** (medium severity)

agent-bootstrap.toml defines a `[modes.automation]` section with its own steps and 7k token budget, matched by `mode_detection.automation = "scheduled_or_recurring_run"`. Neither quick-reference.md's session routing section nor its context loading manifest table mentions an "automation" session type. An agent or tooling that consults the TOML could try to use a mode the markdown docs don't acknowledge.

**3. Helpfulness scoring guide is duplicated between two authoritative surfaces** (low severity)

README.md has the full helpfulness scale table. quick-reference.md has a condensed copy. Both are loaded during full bootstrap and periodic review. The information is identical, but dual-source means they can drift and agents pay the context cost twice. The compact router could link to README instead.

**4. Two `.patch` files in repo root** (low severity)

complementarity-and-orient-evaluate.patch (921 lines) and complementarity-protocol.patch (319 lines) sit in the root. They look like development artifacts from the plans-to-projects overhaul. They're tracked by git, contribute to repo noise, and could confuse agents scanning the root.

**5. Change tier and commit prefix mapping is ambiguous** (low severity)

There's no explicit mapping between the three change tiers (automatic/proposed/protected) and the nine commit prefix categories. For example: is `[knowledge]` always "proposed"? It depends on context (writing to `_unverified/` is automatic, promoting to knowledge is proposed). This nuance is implicit.

---

## II. User-Friendliness

### A. Strong points

- **Progressive disclosure is well-designed.** The three-layer entry: HUMANS/docs/ for people, README.md for architectural grounding, quick-reference.md for runtime routing — works cleanly.
- **Setup flow is practical.** Both setup.sh (CLI) and setup.html (browser) exist, with profile templates and clear QUICKSTART docs.
- **Scratchpad design is excellent.** The USER.md/CURRENT.md split with clear trust levels and the three-session promotion rule gives agents practical guidelines.
- **Review queue format is well-structured.** The triage timing table (security=immediate, protected=session-end, proposed=non-urgent, governance=periodic review) makes prioritization unambiguous.
- **Session checklists are well-condensed.** At 44 lines, they expand the compact manifest without bloat.

### B. Issues found

**6. README.md is doing too much work as both human-entry and agent-reference** (medium severity)

At 421 lines, README.md contains the full architecture, the memory curation protocol, the aggregation spec, the full bootstrap sequence, the entire security model, commit conflict resolution, the summary compression hierarchy, and the session reflection format. A significant portion of this (security model details, reflection format, full bootstrap steps 1-13) is not needed on the compact returning path but is loaded during full bootstrap.

The quick-reference.md budgets README itself at the full_bootstrap tier — but there's no guidance for which README sections matter most during which session types. Agents reading it for a full bootstrap are loading security model details they rarely need alongside the architecture they always need.

**7. The relationship between plans/ and projects/ is unclear from the architecture docs alone** (medium severity)

README.md says to use SUMMARY.md as the primary orientation surface, and SUMMARY.md as a drill-down. But the structure section shows both plans and projects at the same hierarchy level, with projects having project-specific "plans" inside them. The plans-to-projects overhaul plan describes the intended evolution, but the README's structure diagram still presents them as parallel peers without explaining the containment relationship (projects contain plans, plans/ is a legacy flat namespace).

**8. The meta folder has 13 files — cognitive load for periodic review is high** (low severity)

An agent doing periodic review must load 7+ meta files plus README plus CHANGELOG plus content summaries. The system acknowledges ~18-25k tokens for this, which is within budget, but the sheer number of files means an agent must juggle many cross-referencing documents. The on-demand annotations help, but a "periodic review checklist" that sequences exactly which files to read and when would reduce cognitive overhead further. (The integrity-checklist partially fills this role but focuses on audit, not the full review workflow.)

**9. No explicit guidance for when agents should NOT log an ACCESS entry** (low severity)

The documentation says "log every content file you actually opened" but there's no concise list of exemptions. Scattered across README and session-checklists: SUMMARY.md files and meta/ governance files are exempt. Scratchpad files are exempt (in scratchpad-guidelines). An agent cobbling together the full exempt list must read 3 documents. A single-line summary of all exemptions in one place would help.

---

## III. Context Efficiency

### A. Strong points

- **Compact returning path is well-guarded.** The ~3-7k token budget with whole-file compact mode and metadata-first probes is carefully designed.
- **On-demand loading discipline is correctly applied.** Plans/knowledge/skills SUMMARY.md files are deferred to task-driven loading.
- **agent-bootstrap.toml gives tooling a machine-readable manifest** so agents don't have to parse markdown to know what to load.
- **MCP `memory_session_bootstrap` provides a single-call compact returning bundle** eliminating multi-file orchestration.
- **Skip-if-placeholder guards** prevent loading empty files.

### B. Issues found

**10. Content duplication between README.md and other governance docs increases full-bootstrap cost** (medium severity)

Key overlaps:
- **Helpfulness scoring**: full table in README.md + condensed version in quick-reference.md.
- **Aggregation steps**: described in README.md, quick-reference.md, AND curation-algorithms.md at varying levels of detail.
- **Trust decay rules**: appear in README.md (security model), quick-reference.md (decision guide), and curation-policy.md (full rationale).
- **Context budget table**: identical in both README.md and quick-reference.md.

This is intentional progressive disclosure, but during full bootstrap (when both README and quick-reference are loaded), agents get the same information 2-3 times, burning ~500-800 tokens of redundancy.

**11. README's bootstrap sequence (steps 1-13) is vestigial** (medium severity)

README.md contains a 13-step bootstrap sequence that the doc itself says is now "reference documentation" since first-run.md condenses it. But it's still 36 lines of text in a file that's loaded during full bootstrap. It's not gated by a "skip if you've already followed quick-reference routing" note until step 10.

**12. Two large `.patch` files (1,240 lines total) in the repo root** (low severity)

These consume disk and show up in directory listings agents run. They appear to be development artifacts from the plans-to-projects work.

**13. CURRENT.md mentions "implement memory_log_access_batch" as next MCP priority** (low severity)

This is outdated — `memory_log_access_batch` is already implemented in the session_tools.py. The scratchpad has stale working state that should be reviewed.

---

## IV. MCP Server — Tool Surface Review

The MCP implementation is impressive (73+ tools across 3 tiers). Key observations:

- **Good**: Version tokens for optimistic locking, preview mode on all semantic tools, the tier separation (read/semantic/raw-write), path policy enforcement.
- **Good**: `memory_session_bootstrap` and `memory_session_health_check` as single-call orchestration helpers.
- **Minor concern**: The raw write tools require `MEMORY_ENABLE_RAW_WRITE_TOOLS=1` which is a useful safety measure, but this is only documented in code. MCP.md should mention the env var.
- **Minor concern**: The `preview_contract.py` defines `change_class: proposed|protected|automatic` but there's no mapping table connecting tools to their change class. An agent discovering tools for the first time must call each with `preview=True` to learn its governance tier.

---

## V. Prioritized Recommendations

### High priority (consistency risks)

1. **Document the missing commit prefixes** in update-guidelines.md — add `[plan]`, `[scratchpad]`, `[access]` to the "Commit conventions" section.
2. **Add `automation` mode** to quick-reference.md's session routing and context loading manifest, or remove it from agent-bootstrap.toml if it's not yet ready.

### Medium priority (user-friendliness / context efficiency)

3. **Deduplicate the helpfulness scoring guide** — keep the full table in README and replace the quick-reference copy with a one-line pointer: "See README § Memory curation for the helpfulness scale."
4. **Deduplicate the context budget table** — keep it only in quick-reference.md (the operational router), remove from README's bootstrap sequence.
5. **Condense or fence the README bootstrap sequence** (steps 1-13) — add a clear "skip this section during compact/returning sessions" note at the top, or move it to a drill-down doc since first-run.md replaces it.
6. **Clarify the plans/projects relationship** in README's structure diagram with a brief annotation.

### Low priority (cleanup)

7. **Clean up the .patch files** from the repo root.
8. **Review CURRENT.md** to clear the stale `memory_log_access_batch` note and any other outdated entries.
9. **Add an ACCESS logging exemption summary** to one canonical location (session-checklists.md or README).
10. **Add a commit-prefix-to-tier mapping reference table** in update-guidelines.md.

---

**Overall assessment**: This is a remarkably well-designed system. The architecture is coherent, the governance model is thoughtful, the MCP implementation is thorough, and the security model is serious. The issues I found are documentation completeness and content duplication — not structural flaws. The biggest operational risk is the `automation` mode gap between TOML and markdown, and the most impactful improvement would be deduplicating content between README and quick-reference to trim ~500-800 tokens off the full bootstrap path.

Completed: *Synthesize findings report* (8/8)

