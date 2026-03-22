---
source: agent-generated
origin_session: manual
created: 2026-07-25
trust: medium
status: completed
next_action: "Phase 4 items deferred to Calibration stage"
---

# System Review Plan — Consistency, Usability & Context Efficiency

Comprehensive review of the Engram agent memory system, covering path consistency, content duplication, context-budget efficiency, user-friendliness, and architectural coherence.

## Background

This review was performed on the `live-test--maiden` branch at commit f86c01d. The system is at **Exploration** maturity stage (~8 sessions, 128 ACCESS entries, 134 content files, confirmation ratio 0.05).

### Already completed (this session)

- **Stale path references fixed** — 12 files updated in commit f86c01d. All `meta/`, `identity/`, `chats/`, `plans/`, shorthand `skills/`, shorthand `governance/`, and shorthand `memory/` references in governance docs, skill files, working memory, and project plans now use canonical `core/`-prefixed paths.
- **Activity SUMMARY.md** — Updated to reflect existing chat-001 (2026-03-18) instead of placeholder "No session history yet" text.

---

## Phase 0 — Quick wins (no governance impact)

### 0.1 Normalize ACCESS data format paths

**Problem:** The README defines `"session_id": "memory/activity/YYYY/MM/DD/chat-NNN"` (without `core/` prefix), while all prose and navigational references use the full `core/memory/...` form. This creates ambiguity: are ACCESS `"file"` values relative to repo root or to `core/`?

**Recommendation:** Choose one convention and document it explicitly in the README ACCESS format section:
- **Option A (preferred):** Keep short `memory/...` paths in JSONL data (compact, saves bytes in logs) but add a one-line note: _"ACCESS field paths (`file`, `session_id`) are relative to `core/`."_
- **Option B:** Switch JSONL examples to full `core/memory/...` paths for absolute consistency.

**Effort:** ~15 minutes. One paragraph in README + update worked examples if Option B.

### 0.2 Fix curation-policy.md "Do not load" reference inconsistency

**Problem:** HOME.md says `HUMANS/docs/*` while first-run.md says `HUMANS/docs/*` — these match. But the curation-policy.md § "Instruction containment" uses different scoping language for the same rule. Minor inconsistency.

**Recommendation:** Audit the "never load HUMANS/" instruction across all files and ensure identical wording.

**Effort:** ~10 minutes.

---

## Phase 1 — Context efficiency (high impact, moderate effort)

### 1.1 Deduplicate MCP preference boilerplate

**Problem:** The sentence _"When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation."_ appears in **10 files** with minor per-file variations (~160 tokens × 10 = ~1,600 tokens total). An agent loading the full bootstrap or periodic review path will ingest this instruction 4–6 times.

**Files affected:**
1. `core/governance/curation-policy.md`
2. `core/governance/first-run.md`
3. `core/governance/update-guidelines.md`
4. `core/governance/session-checklists.md`
5. `core/memory/skills/SUMMARY.md`
6. `core/memory/skills/onboarding.md`
7. `core/memory/skills/session-start.md`
8. `core/memory/skills/session-sync.md`
9. `core/memory/skills/session-wrapup.md`
10. `core/memory/skills/codebase-survey.md`

**Recommendation:** State the MCP preference rule **once** in `core/HOME.md` (already the first file loaded in every session mode) and remove it from all other files. Optionally replace with a one-line cross-reference: _"MCP preference: see `core/HOME.md`."_ in files that are loaded independently (like curation-policy.md).

**Savings:** ~1,200–1,500 tokens reclaimed from typical session loads.
**Change tier:** Protected (modifies governance + skill files). Requires user approval.

### 1.2 Consolidate access-tracked namespace list

**Problem:** The list of access-tracked namespaces (`core/memory/users/`, `core/memory/knowledge/`, `core/memory/knowledge/_unverified/`, `core/memory/skills/`, `core/memory/working/projects/`, `core/memory/activity/`) is repeated in 6–7 files:
- README.md (§ Access tracking, twice)
- core/HOME.md (§ Compact returning notes)
- core/governance/curation-algorithms.md (§ Procedure step 1)
- core/governance/session-checklists.md (§ Session end step 4)
- core/governance/update-guidelines.md (§ Change categories)
- core/memory/skills/session-wrapup.md (§ ACCESS.jsonl step)

Each occurrence is ~70–90 tokens (700–900 total).

**Recommendation:** Define the canonical list once in README.md (it's the architectural contract) and reference it elsewhere. In governance/skill files, replace with: _"all access-tracked namespaces (see README § Access tracking)"_ or better, add a short anchor in `core/HOME.md` since that's always loaded.

**Savings:** ~500–700 tokens.
**Change tier:** Protected.

### 1.3 Resolve session-checklists / skill file overlap

**Problem:** `core/governance/session-checklists.md` (~150 lines) overlaps ~45–55% with the three session skill files (`session-start.md`, `session-sync.md`, `session-wrapup.md`). Both document the same workflows at similar detail levels. The current layering is:
- HOME.md compact manifest (routing) → session-checklists.md (medium detail) → skill files (full detail)

But the "medium" and "full" layers often say the same thing, wasting ~1,100–1,400 tokens when both are loaded.

**Recommendation:** Sharpen the division:
- **session-checklists.md** becomes a **compact summary only** — numbered steps, no explanations, explicitly cross-referencing skill files for detail. Target: ~60 lines (down from ~150).
- **Skill files** remain the detailed reference with MCP-specific steps, quality criteria, and edge cases.
- This preserves the layered design while eliminating the redundant middle layer.

**Savings:** ~800–1,000 tokens from the checklist file.
**Change tier:** Protected (modifies governance file).

### 1.4 Add per-file token budget enforcement

**Problem:** HOME.md defines target budgets for compact files (HOME.md ~2,600 tokens, projects/SUMMARY.md ~1,700 tokens, users/SUMMARY.md ~450 tokens, activity/SUMMARY.md ~750 tokens). But there's no tooling or validation to detect budget drift.

**Recommendation:** Add a lightweight CI check or MCP tool (`memory_validate`) assertion that reports when any compact file exceeds its budget by >20%. The validate_memory_repo.py script in `HUMANS/tooling/` could be extended for this.

**Effort:** Moderate.
**Change tier:** Automatic (tooling, not governance content).

---

## Phase 2 — Consistency & coherence (moderate impact)

### 2.1 Trust-level behavior definitions consolidation

**Problem:** Trust-level behavioral rules are defined with varying specificity in:
- README.md § Security model table row (one-liner: `high = use freely; medium = use with caution; low = inform only`)
- `core/governance/curation-policy.md` § Trust-weighted retrieval (3 detailed bullets + instruction containment protocol)
- `core/memory/skills/session-start.md` (references trust handling)
- Some skill files reference trust behavior inline

**Recommendation:** The canonical trust behavior definition belongs in `curation-policy.md` (already the most detailed). README keeps its one-liner summary table. Skill files should reference curation-policy.md rather than restating inline rules.

**Savings:** ~300–500 tokens.
**Change tier:** Protected.

### 2.2 ACCESS.jsonl example format consistency

**Problem:** The deferred-action-template.md and update-guidelines.md both contain ACCESS.jsonl worked examples. The deferred-action-template is the detailed version; update-guidelines has a minimal template. Both should use identical field ordering and formatting.

**Recommendation:** Audit both examples for field ordering consistency. Ensure `session_id` is included in both (currently present). Consider whether the deferred-action-template should reference the README format spec rather than embedding its own example.

**Effort:** ~15 minutes.
**Change tier:** Protected (governance files).

### 2.3 HUMANS/docs maintenance alignment

**Problem:** `HUMANS/docs/CORE.md` and `HUMANS/docs/DESIGN.md` explain design decisions for human readers. Some of this content parallels README.md and governance docs. As the system evolves, these human-facing docs will drift unless there's a maintenance trigger.

**Recommendation:** Add a periodic-review checklist item: _"Verify HUMANS/docs/ alignment with current governance."_ This is low-cost and prevents silent drift.

**Effort:** ~5 minutes (add one line to periodic review checklist).
**Change tier:** Protected (governance file).

---

## Phase 3 — User-friendliness (moderate impact, low effort)

### 3.1 Improve first-run discoverability

**Problem:** The bootstrap path for a new agent is: platform adapter (AGENTS.md/CLAUDE.md) → README.md → HOME.md → first-run.md. This is 4 hops before the agent starts actual onboarding work. Each hop loads another document.

**Recommendation:** No structural change needed — the layering is correct for returning sessions. But `first-run.md` should explicitly state _"You are now ready to begin. Do not load additional files unless instructed below."_ to prevent overloading. Currently it lists what NOT to load but doesn't affirmatively signal "stop loading, start working."

**Effort:** ~5 minutes.
**Change tier:** Protected.

### 3.2 Make scratchpad/USER.md purpose clearer

**Problem:** `USER.md` is described in `scratchpad-guidelines.md` as a place for humans to leave notes for the agent, but its relationship to the user profile in `core/memory/users/` is potentially confusing. Is it "user notes TO the agent" or "notes ABOUT the user"?

**Recommendation:** Add a one-line header comment to the USER.md template clarifying: _"This file is for notes FROM the human TO the agent — reminders, preferences, or instructions that should persist across sessions. For the agent's understanding of the user, see `core/memory/users/SUMMARY.md`."_

**Effort:** ~5 minutes.
**Change tier:** Automatic (scratchpad content).

### 3.3 Clarify the "Compact returning" vs "Full bootstrap" decision

**Problem:** HOME.md lists both session types but doesn't give a clear decision rule for when to use Full bootstrap vs. Compact returning. The note says "if you intentionally need the full governance stack" but doesn't define when that would be.

**Recommendation:** Add a single decision sentence: _"Use Full bootstrap after governance changes, system updates, or when the user asks for a thorough review. Use Compact returning for all other sessions."_

**Effort:** ~5 minutes.
**Change tier:** Protected.

---

## Phase 4 — Architectural improvements (high effort, deferred)

### 4.1 Implement skip annotations

**Problem:** HOME.md and README both reference the concept of "skip if empty" for placeholder files, but there's no machine-readable annotation system. Agents must read each file to determine if it's a placeholder.

**Recommendation:** Define a frontmatter field `skip_when: placeholder` or similar that agents can check via metadata-first reads (or MCP tools can filter on). This would save token budget on files that exist structurally but have no content yet.

**Stage gate:** Calibration stage (needs enough files to justify the mechanism).

### 4.2 Implement aggregation trigger automation

**Problem:** ACCESS.jsonl aggregation is currently manual (agent checks line counts during session). The review-queue has flagged that `core/memory/working/projects/ACCESS.jsonl` exceeded the trigger 6× without being aggregated.

**Recommendation:** The MCP `memory_session_health_check()` tool already reports `aggregation_due`. Ensure the session-start skill prominently surfaces this and adds it to the session-end agenda. Consider a pre-commit hook or CI check that warns when `ACCESS.jsonl` files exceed 2× the trigger threshold.

**Stage gate:** Should be addressed before Calibration transition.

### 4.3 Review the three-layer document hierarchy

**Problem:** The system has three layers of routing/protocol docs:
1. HOME.md (compact router, ~2,600 tokens)
2. session-checklists.md + governance docs (medium detail)
3. Skill files (full detail)

This is sound in principle but creates maintenance overhead: changes must propagate across layers. As the system grows, keeping three layers synchronized will become harder.

**Recommendation:** No action needed at Exploration stage. Revisit at Calibration when the system has enough sessions to evaluate whether the three-layer approach causes real synchronization failures or is working as intended.

---

## Priority matrix

| Item | Impact | Effort | Change tier | Status |
|------|--------|--------|-------------|--------|
| 0.1 ACCESS format paths | Low | Low | Automatic | **Done** (b3caccb) |
| 0.2 "Do not load" wording | Low | Low | Protected | **No-op** — already consistent |
| 1.1 MCP boilerplate dedup | High | Low | Protected | **Done** (b3caccb) |
| 1.2 Namespace list consolidation | Medium | Low | Protected | **Done** (8a5db5e) |
| 1.3 Checklist/skill overlap | High | Medium | Protected | **Done** (8a5db5e) |
| 1.4 Token budget validation | Medium | Medium | Automatic | **No-op** — already in validate_memory_repo.py |
| 2.1 Trust-level consolidation | Medium | Low | Protected | **Done** (6a0f286) |
| 2.2 ACCESS example consistency | Low | Low | Protected | **No-op** — field ordering already matches |
| 2.3 HUMANS/docs maintenance | Low | Low | Protected | **Done** (6a0f286) |
| 3.1 First-run discoverability | Medium | Low | Protected | **Done** (893118b) |
| 3.2 USER.md purpose clarity | Low | Low | Automatic | **Done** (893118b) |
| 3.3 Bootstrap decision rule | Medium | Low | Protected | **Done** (893118b) |
| 4.1 Skip annotations | Medium | High | Protected | Deferred — Calibration stage |
| 4.2 Aggregation automation | Medium | Medium | Automatic | Deferred — before Calibration |
| 4.3 Three-layer review | Low | High | Protected | Deferred — Calibration stage |
