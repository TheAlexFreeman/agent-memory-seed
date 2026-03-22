# Governance File Consolidation Roadmap

**Created:** 2026-03-22
**Context:** The 12 governance files were established early in development and haven't been substantially revised since major architectural changes (the `meta/` → `core/governance/` reorganization, the introduction of `core/memory/HOME.md`, the README refactor). This roadmap identifies concrete consolidation and revision work.

---

## Current state: 12 files, 1,109 lines

| File | Lines | Role | Load pattern |
|---|---|---|---|
| `curation-policy.md` | 235 | Memory lifecycle, retrieval, containment, decay, anomaly detection, governance feedback | Full bootstrap + periodic review |
| `update-guidelines.md` | 280 | Provenance, change-control tiers, approval workflow, publication, read-only, periodic review, commits | Full bootstrap + periodic review |
| `curation-algorithms.md` | 131 | Task similarity phases, cluster detection, aggregation runbook | On-demand (aggregation or stage transition) |
| `system-maturity.md` | 108 | Stage definitions, parameter tables, transition rules, assessment log | Periodic review |
| `scratchpad-guidelines.md` | 85 | Scratchpad lifecycle, promotion path, three-session rule | On-demand (writing to scratchpad) |
| `review-queue.md` | 62 | Queue format, triage timing, lifecycle rules | On-demand (when it has entries) |
| `first-run.md` | 44 | Streamlined first-session bootstrap | First run only |
| `deferred-action-template.md` | 41 | Worked example for read-only deferred-action output | First read-only session only |
| `session-checklists.md` | 38 | Quick-reference session start/end runbooks | On-demand |
| `belief-diff-log.md` | 37 | Drift audit entry format and log | Periodic review |
| `quick-reference.md` | 33 | Legacy compatibility pointer to INIT.md | Legacy redirect |
| `integrity-checklist.md` | 15 | Advisory audit checklist (5 items) | Periodic review |

---

## Phase 1: Fix integration gaps (no file structure changes)

These are documentation fixes — updating existing files to reflect the current architecture without moving or merging anything. Low risk, high value for test-user readiness.

### 1a. Add HOME.md references to governance files

**Problem:** `core/memory/HOME.md` was recently added as the session entry point (per README and INIT.md), but no governance file references it. An agent reading only governance docs would not know HOME.md exists.

**Changes:**

- `first-run.md` § "After first run" (line 44): Change "use `core/memory/working/projects/SUMMARY.md` as the primary orientation surface" to "follow the Compact returning manifest in `core/INIT.md` → `core/memory/HOME.md`". The projects summary is a task-driven drill-down, not the session entry point.

- `session-checklists.md` § "Session start (returning)" (line 13): Change "Follow the compact returning manifest in `core/INIT.md`" to "Follow `core/INIT.md` → `core/memory/HOME.md` for the context loading order." This makes the two-step routing explicit.

- `integrity-checklist.md`: Add item 6: "**HOME.md alignment** — Verify that `core/memory/HOME.md` context loading order matches `core/INIT.md` § Context loading manifest and `agent-bootstrap.toml` step lists. Flag any divergence." This catches future split-brain issues.

### 1b. Update curation-policy.md "skip if loaded" headers

**Problem:** Three sections in curation-policy.md begin with "if you've already loaded `core/INIT.md`, skip this section." These were written when curation-policy was always loaded alongside INIT.md. Now that the compact returning path skips curation-policy entirely, the conditional phrasing is misleading — an agent loading curation-policy during a full bootstrap *will* have loaded INIT.md, so the conditional is always true and the section is always skipped.

**Changes:** Replace the three conditional skip headers with forward-references:

- § Trust-weighted retrieval: "Active thresholds are in `core/INIT.md` § Decision guide: trust decay. The rules below govern retrieval behavior at each trust level."
- § Temporal decay: "Active decay windows are in `core/INIT.md`. This section explains the rationale behind the freshness-vs-confidence model."
- § Access anomaly detection: "Active anomaly thresholds are in `core/INIT.md` § Decision guide: anomaly detection. The signal taxonomy and response protocol are below."

This removes ambiguity without losing the pointer to INIT.md.

### 1c. Fix the architectural guardrails duplication

**Problem:** The three-dimension framework (consistency, user-friendliness, context efficiency) is repeated in: README.md § "Architectural guardrails", update-guidelines.md § "Architectural standard", curation-policy.md § "Governance feedback", and review-queue.md proposal format. The README definition is the most complete. The others paraphrase it with slight variations, creating drift risk.

**Changes:**

- `update-guidelines.md` § "Architectural standard for system changes" (lines 78-86): Replace the self-contained definition with a reference: "When the agent is reviewing or modifying the memory system itself, the proposal must address the three architectural guardrails defined in `README.md` § 'Architectural guardrails for system changes': consistency, user-friendliness, and context efficiency." Then keep only the operational guidance specific to update-guidelines (the "change summary is incomplete unless it explains..." sentence).

- `curation-policy.md` § "Governance feedback" (lines 219-223): Same treatment — replace the repeated definitions with a reference to README.md.

- `review-queue.md` already uses reference-style ("include a brief note on its impact to consistency, user-friendliness, and context efficiency") — no change needed.

**Effect:** README.md becomes the single canonical definition. All three governance files point there.

---

## Phase 2: Retire or absorb small files

These changes reduce the governance file count without losing any content. Each removes one file.

### 2a. Retire quick-reference.md

**Problem:** `quick-reference.md` is a 33-line compatibility pointer from the old `meta/` directory structure. It redirects to `core/INIT.md` and lists current governance files. Now that the reorganization is complete and no governance files reference `meta/` paths, the redirect serves no discovery purpose that INIT.md doesn't already serve.

**Dependencies to address first:**
- `core/tools/agent_memory_mcp/tools/semantic/session_tools.py` (lines 106-110): Falls back to `quick-reference.md` as a bootstrap path. Update to point to `core/INIT.md` directly.
- `core/tools/agent_memory_mcp/tools/read_tools.py` (line 58, 118): References `quick-reference.md` for trust decay defaults. Update to read from `core/INIT.md`.
- `setup/initial-commit-paths.txt`: Remove the line.
- Knowledge files that reference `quick-reference.md` (5-6 files in `core/memory/knowledge/`): These are historical/analytical references — no changes needed, as the references describe the system's evolution.
- `HUMANS/docs/DESIGN.md` (line 100): Update the "quick-reference pattern" reference.
- Validator and test files: Update any assertions that check for `quick-reference.md` existence.

**Process:** Protected-tier change. Update the MCP code and validators first, verify tests pass, then remove the file.

### 2b. Absorb integrity-checklist.md into session-checklists.md

**Problem:** `integrity-checklist.md` is 15 lines (5 audit items). It is loaded only during periodic review and serves as an advisory audit aid. `session-checklists.md` (38 lines) is the existing on-demand runbook file for session workflows. Adding an "Integrity audit" section to session-checklists.md would give agents a single file for all checklists.

**Changes:**
- Add a `## Periodic integrity audit` section to `session-checklists.md` containing the 5 items from `integrity-checklist.md`, plus the new HOME.md alignment item from Phase 1.
- Update `core/INIT.md` context loading manifest: replace `integrity-checklist.md` in the Periodic review row with `session-checklists.md`.
- Update `agent-bootstrap.toml` periodic_review mode steps accordingly.
- Update references in knowledge files and tests.
- Remove `integrity-checklist.md`.

**Process:** Protected-tier change. The merged file stays under 75 lines.

### 2c. Absorb deferred-action-template.md into update-guidelines.md

**Problem:** `deferred-action-template.md` is 41 lines, loaded exactly once (first read-only session), and consists of a single worked example for a format already defined in `update-guidelines.md` § "How to communicate deferred actions". It exists as a separate file only to avoid loading it unnecessarily.

**Changes:**
- Move the worked example into `update-guidelines.md` as an appendix section at the end of the "How to communicate deferred actions" subsection. Frame it as: "### Worked example (reference only)" with a note that this section can be skimmed after the first read-only session.
- Update references in `first-run.md`, skill files (`session-start.md`, `session-wrapup.md`), and `HUMANS/docs/DESIGN.md`.
- Update `setup/initial-commit-paths.txt`.
- Remove `deferred-action-template.md`.

**Process:** Protected-tier change. Adds ~30 lines to update-guidelines.md (which becomes ~310 lines — still within the reasonable range for a full-bootstrap governance file).

---

## Phase 3: Structural revisions (larger scope)

These are deeper changes that improve the architecture but require more careful planning and testing.

### 3a. Split curation-policy.md by concern

**Problem:** At 235 lines, `curation-policy.md` covers six distinct concerns: memory lifecycle (capture through retirement), access-driven curation (the ACCESS feedback loop), content boundaries (instruction containment, folder behavioral contracts), temporal mechanics (decay, freshness), security signals (anomaly detection, drift detection), and governance self-evaluation (feedback, evaluation protocol). These concerns have different audiences: the lifecycle and access-driven curation are relevant during aggregation; instruction containment is relevant during retrieval; anomaly detection is relevant during periodic review.

**Proposed split:**
- **`curation-policy.md`** (retained, ~120 lines): Memory lifecycle, access-driven curation, knowledge amplification, summary refresh cadence (including session reflection format), size limits, conflict resolution, emergent categorization, and maturity-adaptive thresholds. This becomes the "how memory is maintained" file.
- **`content-boundaries.md`** (new, ~70 lines): Trust-weighted retrieval, instruction containment, folder behavioral contracts, boundary-violation test, and updating folder contracts. This becomes the "what content is allowed to do" file.
- **`security-signals.md`** (new, ~50 lines): Temporal decay rationale (freshness vs. confidence), access anomaly detection (signal taxonomy and response protocol), drift detection (identity churn, knowledge flooding, skill drift, summary divergence), and governance feedback. This becomes the "how the system detects problems" file.

**Why this helps:**
- Agents can load `content-boundaries.md` during retrieval without also loading lifecycle and security signal details.
- The periodic review loads `security-signals.md` without re-reading curation lifecycle.
- Each file has a clearer, single-purpose mandate.

**Dependencies:** Update all cross-references (README, INIT.md, update-guidelines, integrity-checklist, curation-algorithms, knowledge files), the TOML, validators, and tests. Update the context loading manifest to map each new file to the session types that need it.

**Process:** Protected-tier. This is the largest change in the roadmap. Consider doing it alongside a broader governance review rather than as isolated work.

### 3b. Clarify periodic review choreography

**Problem:** The periodic review involves content from four governance files (`update-guidelines.md` for the 11-step checklist, `system-maturity.md` for stage assessment, `curation-algorithms.md` for aggregation, `integrity-checklist.md`/`session-checklists.md` for the audit), but the orchestration and dependencies between them are implicit. An agent has to piece together the flow from cross-references.

**Proposed change:** Add a `## Periodic review orchestration` section to `update-guidelines.md` (or to the new `security-signals.md` if Phase 3a is done) that explicitly documents:

1. The dependency graph: security flags (review-queue) → unverified content → conflict resolution → review queue → unhelpful memory → maturity assessment → governance evaluation → folder structure → emergent categorization → reflection themes → update last review date.
2. Which governance file provides the procedure for each step.
3. Exit conditions (when a step can abort or modify later steps).

This doesn't add new rules — it makes implicit choreography explicit.

### 3c. Evaluate the governance/skills boundary

**Problem:** `session-checklists.md` is a governance file that primarily summarizes three skill files (`session-start.md`, `session-sync.md`, `session-wrapup.md`). The skill files contain the detailed procedures; the governance file is a quick-reference. This creates a question: should session lifecycle procedures be governed by skill files or governance files?

**Current answer:** Both — the skill files are the detailed authority, the governance file is a compact on-demand summary. This works but means changes to session workflows require updating both.

**Proposed evaluation:** During the next periodic review, assess whether the skill files or the governance summary is actually loaded more frequently. If agents consistently load only the governance summary and never drill into the skills, the skills may be overbuilt. If agents skip the summary and go straight to skills, the summary may be unnecessary overhead.

This is an observation-driven decision, not a predetermined change. Log the evaluation in the assessment notes.

---

## Phase 4: Future considerations

These are not actionable yet but should be tracked for when the system matures.

### 4a. Governance file versioning

As the system reaches Consolidation stage, governance files will have been through multiple revision cycles. Consider adding a `last_revised` date to each governance file header (not YAML frontmatter — governance files are exempt from provenance metadata, but a simple comment) so that periodic reviews can quickly identify files that haven't been touched in a long time.

### 4b. Machine-readable governance

`agent-bootstrap.toml` already expresses loading rules in machine-readable form. If the MCP server evolves to enforce governance rules programmatically (beyond what the validator already checks), consider extracting key rules (folder contracts, change-control tiers, trust assignment) into a machine-readable format alongside the human-readable governance docs. This is a "when the need arises" item, not a proactive change.

### 4c. Governance doc token budget

Add governance files to the compact bootstrap contract in `core/INIT.md` with target token budgets, similar to how memory summaries have targets today. This would make the context-efficiency constraint measurable for governance files, not just memory files. Relevant once the system has enough periodic-review data to know which governance files are actually loaded per session type.

---

## Summary

| Phase | Changes | Files affected | File count after |
|---|---|---|---|
| **Current** | — | — | 12 files, 1,109 lines |
| **Phase 1** | Fix integration gaps | 5 files edited | 12 files (~1,100 lines) |
| **Phase 2** | Retire 3 small files | 3 removed, 2 absorb content | 9 files (~1,050 lines) |
| **Phase 3** | Split curation-policy, add choreography | 1 split → 3, orchestration added | 11 files (~1,100 lines) |

Phase 1 should be done before test users. Phase 2 is low-risk and can be done alongside other launch prep. Phase 3 is worth doing but not urgent — it improves maintainability without changing any behavior. Phase 4 is tracked for future assessment.
