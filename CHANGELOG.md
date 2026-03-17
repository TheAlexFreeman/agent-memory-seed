# Changelog

This file records how the memory system's own structure, rules, and governance have changed over time. It is not a log of content changes (what the user said or learned) but of **system changes** (how memory is organized, stored, retrieved, and curated).

Each entry should explain not just what changed, but **why** — so that future agents can understand the evolutionary trajectory of this system and make informed decisions about further modifications.

## Format

```
## [YYYY-MM-DD] Brief title

**Changed:** What was modified, added, or removed.
**Reasoning:** Why this change was made — what problem it solves or what improvement it enables.
**Approved by:** "user" if explicitly approved, "agent (pending review)" if auto-applied and awaiting confirmation.
```

---

## [2026-03-16] Aggregation and query surfaces for the memory engine

**Changed:**

- **Aggregation path into canonical task-group state.** Extended `scripts/memory_engine.py` with an `aggregate` command that reads the live stage and aggregation trigger from `meta/quick-reference.md`, analyzes ACCESS history, and writes the machine-generated `meta/task-groups.md` file when task-group writes are allowed for the active stage and the trigger has been met. `--dry-run` previews the same decision without mutating the repo.

- **Read-only query command.** Added a `query` command that matches free-text queries against derived task groups and ranks files using task-group similarity, retrieval frequency, helpfulness, and recency. This gives the engine a practical search-like surface before introducing an MCP server or a heavier retrieval stack.

- **Expanded coverage and docs.** Added tests covering Calibration-stage aggregation and query ranking, and updated `README.md`, `QUICKSTART.md`, `DESIGN.md`, and `docs/memory-engine-phase-2.md` so the implemented Phase 2 surface matches the repo documentation.

**Reasoning:** The previous slice made task normalization visible but stopped short of using it in the repo's governed workflows. This change connects the derived task-group layer to the first canonical output already anticipated by the governance model (`meta/task-groups.md`) and adds a query surface that exercises those groups in a user-facing way. That closes the main remaining gap before planning a Phase 3 category vocabulary and MCP-facing interfaces.

**Approved by:** agent (pending review)

---

## [2026-03-16] Task-group analysis preview for the memory engine

**Changed:**

- **Derived task normalization.** Extended `scripts/memory_engine.py` with a read-only `task-groups` command that analyzes ACCESS history, normalizes free-text `task` strings with a conservative standard-library heuristic, and reports the resulting task-group candidates.

- **SQLite task-group snapshots.** `rebuild` now stores derived task-group rows in a new `task_groups` table and annotates each indexed ACCESS entry with its normalized task string and derived task-group name. This keeps the grouping logic disposable and rebuildable while making later retrieval and aggregation work cheaper.

- **Coverage and docs.** Expanded `tests/test_memory_engine.py` to cover task-group reporting and SQLite persistence, and updated `README.md`, `QUICKSTART.md`, and `DESIGN.md` to document the new command and its place in the roadmap.

**Reasoning:** Phase 1 made the persistence boundary explicit. The next smallest safe step is to make the repo's existing ACCESS `task` history operational without yet writing back into canonical Markdown. Task normalization is the Phase 2 precursor already described in `meta/curation-policy.md`: it reduces false co-occurrence from long sessions, gives the CLI a more useful read surface, and prepares the engine for later aggregation and MCP features without changing the canonical memory model.

**Approved by:** agent (pending review)

---

## [2026-03-16] Phase 1 memory engine foundation

**Changed:**

- **Optional derived SQLite sidecar.** Added `scripts/memory_engine.py`, a standard-library Python CLI with two Phase 1 commands: `status` and `rebuild`. `status` reports the live stage and thresholds from `meta/quick-reference.md`, inventories the current repo, and shows whether the derived SQLite database exists. `rebuild` scans the repo and builds `.memory.db`, a git-ignored SQLite database that records indexed Markdown files, ACCESS entries, and a snapshot of the live runtime config.

- **Explicit derived-state schema.** The new CLI creates a minimal Phase 1 schema (`files`, `access_entries`, `aggregation_checkpoints`, `clusters`, `anomalies`, `system_state`) without changing the canonical storage model. The database is rebuildable from source files and can be safely deleted at any time.

- **Tests for the foundation.** Added `tests/test_memory_engine.py` covering status reporting, dry-run rebuild behavior, and deterministic SQLite population from a minimal repo fixture.

- **Docs and ignore rules.** Added `.memory.db` to `.gitignore` and documented the optional engine in `README.md`, `QUICKSTART.md`, and `DESIGN.md` as a Phase 1 foundation rather than a replacement for the file-based system.

**Reasoning:** The deep-research follow-up identified the highest-leverage initial step as making the persistence boundary explicit before adding richer search or MCP operations. This change implements that boundary in code. It keeps Markdown and JSONL as the canonical memory substrate, uses SQLite only as disposable derived state, and creates a concrete CLI surface future phases can extend without rewriting the governance model.

**Approved by:** user

---

## [2026-03-16] Browser setup wizard (setup.html)

**Changed:**

- **`setup.html` companion wizard.** Added a single-file, zero-dependency browser wizard that mirrors `setup.sh` for users who prefer a graphical interface or are on platforms where running shell scripts is inconvenient. Three-step flow: About You (optional name and AI-use context) → Starter Profile (card picker) → AI Platform (option list with inline contextual hints). Step 4 generates and provides download links for the appropriate files (`identity/profile.md`, `identity/SUMMARY.md`, `chatgpt-instructions.txt`, or `system-prompt.txt`) with per-file Preview and Download buttons and platform-specific next-steps instructions. Runs entirely client-side — no server or network requests. All DOM construction uses `textContent` and safe DOM methods (no `innerHTML` with dynamic content). `<noscript>` fallback directs users to `setup.sh`.

**Reasoning:** Some users — especially those on Windows, corporate machines, or unfamiliar with terminals — find even `bash setup.sh` a barrier. Opening an HTML file in a browser requires no tools. The wizard produces identical output to `setup.sh` for the same choices, so both paths lead to the same starting state. Inspired by OpenClaw's browser-based setup wizard pattern.

**Approved by:** user

---

## [2026-03-16] Zero-edit onboarding path for read-only platforms

**Changed:**

- **`scripts/onboard-export.sh`.** Added an import script that parses a structured onboarding export document and writes the resulting files into the repo: `identity/profile.md` (with correct frontmatter), `identity/SUMMARY.md`, the first chat record under `chats/YYYY/MM/DD/chat-001/` (SUMMARY.md and optional reflection.md), and `chats/SUMMARY.md` (only when no real history exists — guarded against clobbering). Stages and commits automatically when git author identity is configured; prints manual commit instructions otherwise. Supports `--dry-run` to preview all writes. Hardened comment stripping: sed range `/^<!--/,/^-->$/d` matches the template's multi-word comment openers (e.g., `<!-- The agent writes...`).

- **`scripts/onboard-export-template.md`.** Added a structured template the agent fills in at the end of a first session on a read-only platform. Three sections with HTML comment placeholders: `## Identity Profile`, `## Session Summary`, `## Session Reflection`. The agent outputs this document; the user saves it and runs the import script.

- **Updated `skills/onboarding.md` step 6.** Added explicit instructions for write-unavailable sessions: produce the export in the three-section template format and tell the user to run `bash scripts/onboard-export.sh <file>`.

- **Updated `QUICKSTART.md`.** Added "Read-only platforms" subsection documenting the full export/import flow.

**Reasoning:** Users on ChatGPT, Claude Projects, or other sandboxed platforms can run the onboarding conversation but cannot have the agent write files directly. Previously, the only option was manual copy-paste with no structure. The export script eliminates that friction: the user saves one file and runs one command. The three-section format also makes the exported document human-readable and editable before import, so users can review what the agent captured before it gets committed.

**Approved by:** user

---

## [2026-03-16] Human-friendly startup: guided setup, starter profiles, and daily workflow skills

**Changed:**

- **Guided setup mode.** Rewrote `setup.sh` with interactive platform picker (Claude Code, Cursor, ChatGPT, Generic) and starter profile selector. Platform choice generates tailored next-step instructions; ChatGPT and Generic modes auto-generate `chatgpt-instructions.txt` or `system-prompt.txt` with the correct custom instructions/system prompt. New flags: `--platform <name>`, `--profile <name>`.

- **Starter profile templates.** Created `templates/profiles/` with three starter identities: `software-developer.md`, `researcher.md`, `project-manager.md`. Each ships with `source: template`, `trust: medium` frontmatter and `[template]`-tagged traits. Setup installs the chosen template to `identity/profile.md` and updates `identity/SUMMARY.md` to flag it as pending onboarding confirmation.

- **Template-aware onboarding.** Updated `skills/onboarding.md` with a new step 0: if a `source: template` profile exists in `identity/`, the agent presents the pre-filled traits for confirmation/adjustment instead of starting from a blank slate.

- **First-run flow.** Created `meta/first-run.md` — an agent-facing document that condenses bootstrap steps 1–9 into a streamlined silent setup + interactive onboarding flow. The agent reads governance files silently and only surfaces the conversational onboarding to the user. Updated `README.md` step 4 and `meta/session-checklists.md` to reference it.

- **Daily workflow skills.** Created three new skills implementing the "Two Notes, Three Commands" pattern:
  - `skills/session-start.md` — Session opener: loads recent context, checks pending items, greets with continuity.
  - `skills/session-sync.md` — Mid-session checkpoint: captures decisions and progress on demand.
  - `skills/session-wrapup.md` — Session closer: writes summary, reflection, ACCESS entries, produces deferred actions on read-only platforms.
    Updated `skills/SUMMARY.md` and `meta/session-checklists.md` to reference the new skills.

- **Updated QUICKSTART.md.** Documented the new setup flow (three interactive choices), CLI flags for scripted use, and starter profiles.

**Reasoning:** The system's architecture was sound but the human-facing first five minutes were intimidating. Non-technical users had to understand git concepts before getting value, the 13-step bootstrap was surfaced as-is to new users, and there was no way to avoid a blank-canvas cold start. These changes implement progressive disclosure: `setup.sh` now feels like a consumer install wizard (pick a number, not a workflow); starter profiles solve the cold-start problem; `meta/first-run.md` hides bootstrap complexity from the user; and daily workflow skills give immediate tangible value from session one. Inspired by OpenClaw's "run this, answer questions, start chatting" pattern while preserving this system's security model.

**Approved by:** user

---

## [2026-03-16] Governance hardening and validation pass

**Changed:**

- **First-run bootstrap hardening.** Updated `README.md` so fresh instantiations read `meta/quick-reference.md`, the relevant change-control/read-only sections of `meta/update-guidelines.md`, and check write access before onboarding can write memory. First-run now reads `skills/SUMMARY.md` and `skills/onboarding.md` explicitly, then runs onboarding with `knowledge/SUMMARY.md` and `chats/SUMMARY.md` skippable when empty.

- **Onboarding proposal flow.** Updated `skills/onboarding.md` so initial profile creation is explicitly proposed-tier: draft the portrait, present it, revise if needed, require explicit in-chat confirmation before any `identity/` write, and emit deferred actions instead of writing when the repo is read-only.

- **Single live runtime authority.** Reframed `meta/quick-reference.md` as the sole live runtime config for active thresholds and task-similarity grouping, added a dedicated section documenting `session_id`-first grouping with `date` fallback, and updated `README.md`, `meta/curation-policy.md`, and `meta/glossary.md` to treat `meta/system-maturity.md` as an assessment/template reference rather than a live threshold source.

- **Schema alignment.** Expanded the documented frontmatter `source` enum to include `unknown` in `meta/update-guidelines.md`, `identity/SUMMARY.md`, `knowledge/SUMMARY.md`, and `skills/SUMMARY.md`; defined it as legacy/backfill-only unless the real origin is genuinely unrecoverable; and formalized ACCESS semantics so `file`, `date`, `task`, `helpfulness`, and `note` are required while `session_id` and `category` are optional.

- **Session-aware clustering.** Updated `meta/curation-policy.md` and `meta/quick-reference.md` so Exploration-stage co-retrieval clustering groups by `session_id` when present and falls back to `date` for legacy ACCESS entries, without requiring historical backfill.

- **Validation tooling and docs.** Added a dependency-free Python validator plus `unittest` coverage to check content frontmatter, ACCESS JSONL structure, quick-reference parameter coverage, and runtime-guidance consistency. Added an optional validator invocation note to `QUICKSTART.md` and updated `meta/session-checklists.md` to recommend writing `session_id` whenever the chat folder is known.

**Reasoning:** This pass fixes the highest-risk contradictions surfaced by the framework review: first-run behavior could bypass governance and write-access checks, runtime threshold authority was split across documents, the provenance schema contradicted its own backfill rule, and Exploration-stage clustering still grouped by date despite the addition of `session_id`. The validator turns those protocol expectations into an executable check so future edits are less likely to drift back into contradiction.

**Approved by:** user

---

## [2026-03-16] Documentation and operational clarity from framework review

**Changed:**

- **Threshold consistency.** In `meta/curation-policy.md` § "Maintenance", replaced hardcoded "90+ days" staleness trigger with a reference to the active staleness trigger in `meta/quick-reference.md` (and ACCESS.jsonl/ACCESS.archive.jsonl for last access).

- **Archive and meta-file documentation.** In `meta/curation-policy.md` § "Retirement", documented that each content area has its own archive (`knowledge/_archive/`, `identity/_archive/`, `skills/_archive/`) and that retired files are moved to the archive of their source folder. In README repository structure, added optional `task-groups.md` (Calibration) and `task-categories.md` (Consolidation).

- **Aggregation, reflection, and session semantics.** In README: defined **session** (one chat folder under chats/YYYY/MM/DD); clarified first-aggregation semantics (count all entries when no ACCESS.archive.jsonl exists); changed reflection note wording from "appended to" to "written to the chat folder as reflection.md".

- **Bootstrap and onboarding.** In README § "Bootstrap sequence", added step 4: if identity has no portrait and no chat folders, run the onboarding skill instead of steps 5–10; otherwise continue. Softened step 8 (chats/SUMMARY.md) to "skip if no chat folders exist". Renumbered steps 5–10.

- **Last periodic review date.** In `meta/quick-reference.md`, added "Last periodic review" section with Date placeholder ("Not yet run") and instruction to update it when completing a full periodic review. In `meta/update-guidelines.md`, changed the periodic-review trigger to use that date (with fallback to repo creation or last [system] CHANGELOG entry) and added checklist step 11: update the date in quick-reference after the review.

- **Emergent abstractions in change control.** In `meta/update-guidelines.md` § "Proposed changes", added an explicit bullet for creating meta-knowledge files (propose to user, do not create silently; see README § "Emergent abstractions").

- **Review-queue lifecycle.** In `meta/review-queue.md`, added "Lifecycle" subsection: resolved/rejected/superseded/false-positive items may be moved to an Archived section or deleted after the next periodic review; goal is to avoid unbounded growth while preserving recent history for governance evaluation.

- **Glossary.** Created `meta/glossary.md` with definitions for session, retrieval, aggregation, trust level, maturity stage, protected vs proposed change, quarantine, provenance, belief diff (with pointers to canonical docs).

- **Session checklists.** Created `meta/session-checklists.md` with Session start and Session end runbooks; linked from README after the bootstrap sequence.

- **Optional session_id in ACCESS.jsonl.** In README ACCESS format, added optional `session_id` field and a one-line note that it supports joining with reflection and session-scoped analysis.

- **Integrity checklist.** Created `meta/integrity-checklist.md` with an advisory checklist: provenance/frontmatter, instruction containment (boundary-violation test), optional commit-signature check. Stated that the repo does not enforce these automatically.

- **Single source of truth for platform rules.** Shortened `.cursorrules`, `CLAUDE.md`, and `AGENTS.md` to a single directive plus pointer to README.md and meta/; removed duplicated bullet lists so future rule changes only touch README and meta.

**Reasoning:** Implementation of the framework review recommendations to improve threshold consistency, archive and aggregation semantics, bootstrap/onboarding clarity, periodic-review trigger explicitness, change-control coverage for emergent abstractions, review-queue growth policy, discoverability (glossary, checklists), optional schema extension, integrity audit aid, and reduction of rule duplication across platform entry points.

**Approved by:** user

---

## [2026-03-15] Self-organizing dynamics — from passive storage to emergent intelligence

**Changed:**

- **System maturity tracking.** Created `meta/system-maturity.md` defining three developmental stages (Exploration, Calibration, Consolidation) with quantitative signals for assessment and stage-appropriate parameter tables. All hardcoded governance thresholds (retirement windows, aggregation triggers, anomaly detection alarms) are now parameterized by maturity stage. Young systems bias toward exploration (capture aggressively, retire slowly); mature systems bias toward order (capture selectively, retire confidently).

- **Governance feedback mechanism.** New section in `meta/curation-policy.md` establishing that governance rules are subject to the same evolutionary pressure as content. During periodic review, the agent evaluates whether thresholds, anomaly signals, and process requirements are producing good outcomes — checking for premature archival, false positive rates, and process friction. Issues are written as governance proposals to `meta/review-queue.md` with quantitative evidence. Closes the loop: governance shapes curation, curation generates evidence, evidence reshapes governance.

- **Governance proposal format.** Extended `meta/review-queue.md` with a new `governance` type entry format including rule affected, evidence, current behavior, proposed change, and expected impact fields.

- **Knowledge amplification protocol.** New section in `meta/curation-policy.md` creating a self-reinforcing dynamic for memory value. High-value files (5+ retrievals, mean helpfulness ≥ 0.7) are actively enriched with cross-references, task context annotations, expansion suggestions, and strengthened summary presence. Low-value files (3+ retrievals, mean helpfulness ≤ 0.3) are investigated, demoted in summaries, and flagged for retirement. Referenced in `README.md` aggregation section.

- **Emergent categorization protocol.** New section in `meta/curation-policy.md` enabling the system to discover organizational structure from usage patterns rather than relying solely on the initial taxonomy. Cross-folder retrieval clusters (3+ files from 2+ folders co-retrieved in 3+ sessions) are detected, named, documented, and used to evaluate whether the folder structure should evolve. Includes a taxonomy health check for periodic review.

- **Emergent abstractions.** New section in `README.md` summary hierarchy enabling conceptual compression alongside temporal compression. When the agent notices cross-domain structural patterns in knowledge files, it can propose meta-knowledge files that capture the abstraction — creating higher-level representations that enrich reasoning across constituent domains.

- **Session reflection protocol.** New section in `README.md` adding meta-level self-observation to session output. Each session produces a reflection note alongside the chat summary, tracking which memory was retrieved, how it influenced responses, outcome quality, gaps noticed, and system-level observations. Over time, reflection notes reveal characteristic strengths, blind spots, and retrieval pattern quality — enabling genuine self-organization rather than mere accumulation.

- **Enhanced periodic review.** Updated `meta/update-guidelines.md` to include governance evaluation, maturity assessment, emergent categorization review, and session reflection theme analysis as part of the 30-day review cycle.

- **Updated README.md.** Repository structure diagram now includes `meta/system-maturity.md`. Aggregation section references cross-folder analysis and knowledge amplification protocols.

**Reasoning:** The memory system's architecture already contained both bottom-up forces (raw data flowing in through interactions and ACCESS.jsonl) and top-down forces (governance rules, curation policy, trust hierarchy). But these forces were operating independently rather than interpenetrating. The governance layer was too rigid — it couldn't learn from its own outcomes. The categorization was imposed top-down without mechanisms for emergence. The positive feedback loop stopped at helpfulness scoring without actively reinforcing high-value regions. The thresholds were static rather than adaptive to system maturity. The conceptual hierarchy was flat. And the system lacked self-observation of its own reasoning patterns. These six changes establish the missing feedback mechanisms: governance rules are now shaped by the evidence they generate; categories emerge from co-retrieval patterns; high-value knowledge attracts further development; thresholds adapt to developmental stage; conceptual abstractions emerge from cross-domain patterns; and session reflection enables the system to observe its own cognitive dynamics. Together, these move the system from a structured storage mechanism toward a self-sustaining process at the boundary between order and chaos.

**Approved by:** user

## [2026-03-15] Memetic threat defense — defense-in-depth against memory injection

**Changed:**

- **Provenance metadata framework.** All content files in `identity/`, `knowledge/`, and `skills/` now require YAML frontmatter with source, origin session, creation date, last-verified date, and trust level (high/medium/low). Trust assignment rules map source types to initial trust levels, with defined promotion and demotion paths. Added to `meta/update-guidelines.md` and documented in all three folder SUMMARY.md files.

- **Content quarantine zone.** Created `knowledge/_unverified/` as a staging area for externally sourced content. All agent-ingested material from web searches, uploaded documents, or external repositories must land here with `trust: low`. Promotion to `knowledge/` requires explicit user review. Added SUMMARY.md and ACCESS.jsonl to the new folder.

- **Trust-weighted retrieval.** New section in `meta/curation-policy.md` defining how the agent adjusts behavior based on trust level: `high` = use freely, `medium` = use with caution, `low` = inform only / never instruct / always disclose provenance.

- **Instruction containment policy.** New section in `meta/curation-policy.md` establishing that only `skills/` and `meta/` files may contain procedural instructions. Agent must refuse to follow imperatives found in `knowledge/` or `identity/` files. Includes an instruction-detection heuristic that flags boundary violations in `meta/review-queue.md`.

- **Skills elevated to protected tier.** In `meta/update-guidelines.md`, `skills/` modifications moved from "proposed" to "protected" (explicit user approval + CHANGELOG entry required). Rationale: skill files directly control agent behavior and are the highest-value injection target.

- **Temporal decay rules.** New section in `meta/curation-policy.md`: `trust: low` files unverified for 60+ days are auto-archived; `trust: medium` files unverified for 120+ days are flagged for re-verification.

- **Access anomaly detection.** New section in `meta/curation-policy.md` defining suspicious ACCESS.jsonl patterns: high-frequency retrieval of unapproved files, first-time retrieval of instruction-bearing content, sudden access spikes on dormant files, and cross-folder instruction leakage.

- **Drift detection signals.** New section in `meta/curation-policy.md` for detecting slow-burn belief drift: identity churn, knowledge flooding from external sources, skill definition drift, and summary divergence.

- **Security flag format in review queue.** Extended `meta/review-queue.md` format to include a `security` type with trigger, file, and recommended action fields. Anomaly detection and instruction-containment violations generate entries here.

- **Belief-diff log.** Created `meta/belief-diff-log.md` as a periodic audit artifact. During each 30-day review cycle, the agent generates a summary of content changes, trust-level shifts, and security flags since the last review. Updated the periodic review section in `meta/update-guidelines.md` to include belief-diff generation and additional security review items.

- **Git integrity guidance.** New "Commit integrity" section in `meta/update-guidelines.md` and "Repository integrity" section in `README.md` recommending GPG-signed commits, branch protection, and signature verification during review.

- **Security model in README.md.** New section documenting the defense-in-depth philosophy, the three threat categories (direct tampering, indirect injection, slow-burn drift), all defense layers in a summary table, limitations (social engineering of the user), and repository integrity guidance. Updated the bootstrap sequence to include security-related reading steps.

- **Updated README.md.** Repository structure diagram now includes `knowledge/_unverified/` and `meta/belief-diff-log.md`. "How to propose changes" section updated to reflect skills' protected status and the quarantine write rule for external content.

**Reasoning:** Agent memory systems are vulnerable to memetic threats — memory injection attacks where an adversary plants content that the agent later retrieves and acts on as legitimate. The research literature (MemoryGraft, OWASP LLM memory specification, Galileo AI multi-agent poisoning studies) identifies three main attack vectors: direct repo tampering, indirect injection via ingested content, and slow-burn belief drift. No single defense is sufficient; stacked defenses combining provenance tracking, trust-layered retrieval, content quarantine, instruction boundary enforcement, temporal decay, anomaly detection, and periodic audit provide defense-in-depth. This system's git-based architecture is unusually well-suited because it inherently provides an immutable audit trail, content-addressable integrity checking, and easy rollback.

**Approved by:** user

## [YYYY-MM-DD] Initial system creation

**Changed:** Repository initialized with base template. Folders created for `identity/`, `knowledge/`, `skills/`, `chats/`, and `meta/`. Core protocols established in README.md including access-tracking via ACCESS.jsonl, progressive summary compression, bootstrap sequence, and update governance.

**Reasoning:** Starting point for a persistent, version-controlled agent memory system. The template is intentionally minimal — it provides structure and protocols but almost no content, so that all personalization emerges from actual user interaction rather than assumptions.

**Approved by:** user
