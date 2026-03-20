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

## [2026-03-20] Worktree validator profile and CI enforcement landed

**Changed:**

- **Made the validator worktree-aware.** `HUMANS/tooling/scripts/validate_memory_repo.py` now treats `host_repo_root` as a worktree-mode signal, verifies that the host path exists and is a git repo, rejects host paths nested under the memory worktree, requires the memory checkout itself to be a git worktree, and warns when the memory branch shares history with the host repo's default branch.

- **Added adapter-duplication warnings.** In worktree mode, the validator now compares host-root adapter files against the worktree copies and warns when they are byte-for-byte duplicates, which catches a common setup mistake where the host root is not given worktree-specific routing guidance.

- **Finalized the deployed-worktree bootstrap contract.** Deployed worktree manifests now remove standalone `CHANGELOG.md` bootstrap steps, generated survey/template files use validator-compatible `origin_session: setup` provenance, and starter compact-summary placeholders now match the validator's compact-path rules.

- **Expanded regression coverage and CI for worktree setup.** Added targeted git-backed validator tests for valid, missing, nested, shared-history, duplicate-adapter, and deployed-worktree-profile scenarios; restored the validator-backed `init-worktree.sh` end-to-end setup test; added a dedicated Windows `worktree-e2e` CI job; and fixed `setup/init-worktree.sh` so deployed bootstrap manifests insert `host_repo_root` at top level with normalized forward-slash paths.

**Reasoning:** Worktree mode was usable after the deployment and survey-scaffold slices, but it still relied on convention rather than enforceable topology checks, and its bootstrap manifest still described standalone-only surfaces. This change closes that gap by formalizing a deployed-worktree validator profile, aligning generated starter files with that contract, and pinning the full init-worktree plus validator flow into CI. That completes the worktree-integration roadmap and leaves ACCESS-log tooling as the next build priority.

**Approved by:** user

---

## [2026-03-20] Worktree deployment hygiene and survey scaffolds landed

**Changed:**

- **Added practical worktree integration guidance.** Replaced the generic integrations write-up in `HUMANS/docs/INTEGRATIONS.md` with a deployment-focused guide covering worktree-mode CI/CD exemptions, branch-protection expectations, PR/release-note noise reduction, and ready-to-paste ignore snippets for GitHub Actions, GitLab CI, Bitbucket Pipelines, ESLint, Prettier, Ruff, TypeScript, VS Code, JetBrains, and ripgrep.

- **Extended `init-worktree.sh` with friction-reduction stubs.** Deployed worktrees now get a generated `.ignore` that keeps memory folders out of host-repo search by default, a root `.editorconfig` that pins neutral text-file defaults, a starter `plans/codebase-survey.md`, and a `knowledge/codebase/` skeleton so new codebase memory stores start with an actionable survey path instead of an empty shell.

- **Updated onboarding templates and skill support for codebase mode.** The software-developer and project-manager profile templates now reserve a codebase-context block, a new protected skill (`skills/codebase-survey.md`) captures the expected module-survey workflow, and setup tests now assert that the worktree survey plan, codebase stubs, and hygiene files are actually present after initialization.

- **Refreshed the canonical seed manifest.** Added the new survey templates and skill file to `setup/initial-commit-paths.txt` so the tracked setup contract stays aligned with the repository state.

**Reasoning:** The worktree topology was functionally correct after Phase 2, but still too easy to misconfigure and too blank after first install. This change closes that gap by documenting how to keep the memory branch out of host automation, making host-tooling bleed less likely by default, and giving every new worktree a concrete codebase-survey scaffold that agents can advance immediately. That completes the friction-reduction slice before the remaining validator/CI enforcement work.

**Approved by:** user

---

## [2026-03-20] Host-repo freshness checks landed

**Changed:**

- **Added a host-backed freshness read tool.** `memory_check_knowledge_freshness` now reads knowledge-file frontmatter, resolves `related` host source files through `host_repo_root`, compares them against host git history, and returns structured freshness reports with `status`, `current_head`, `host_changes_since`, and `suggested_action`.

- **Extended trust audit with source-change awareness.** `memory_audit_trust` now reuses the same freshness signal when a host repo is configured, so recent source churn can escalate medium-trust notes for re-verification while older but unchanged notes avoid being treated as equally urgent.

- **Added host-history counting support to the git wrapper.** `GitRepo` now exposes a commit-count helper used to measure host changes since a note's `last_verified` date without duplicating git subprocess logic in the read-tool layer.

- **Expanded MCP regression coverage.** Added targeted tests for stale/fresh/unknown freshness reports, freshness-aware trust auditing, and export visibility for the new read tool.

**Reasoning:** Host-repo git access by itself only exposed raw history; it did not make that history actionable for memory governance. This slice turns the new worktree topology into a usable staleness signal that agents can query directly and that trust auditing can consume automatically, which closes the core Phase 2 loop before moving on to CI/tooling-hygiene templates.

**Approved by:** user

---

## [2026-03-20] Worktree-init foundation landed

**Changed:**

- **Added the first worktree deployment flow.** Created `setup/init-worktree.sh` so an existing host repository can spawn a dedicated `agent-memory` orphan branch, seed it through a temporary detached worktree, and materialize the final `.agent-memory` worktree without rewriting the host checkout.

- **Defined a minimal worktree seed.** Added `setup/init-worktree-paths.txt` to copy only the generic MCP/runtime/governance surfaces into the memory branch while generating fresh identity, plans, chats, knowledge, and scratchpad stubs instead of cloning personalized repo content.

- **Wired host-side MCP output into the flow.** The new init script appends `host_repo_root` to the deployed bootstrap file, writes host-root Codex config when requested, and emits a generic MCP example for other clients.

- **Made worktree MCP launchers less brittle.** Host-side worktree config now prefers a discovered `engram-mcp` CLI when available and falls back to the existing Python-plus-script entrypoint only when the CLI is unavailable.

- **Added host-root agent adapters for worktree mode.** `init-worktree.sh` now writes trimmed `AGENTS.md`, `CLAUDE.md`, and `.cursorrules` files into the host repository so agent sessions start from the memory worktree's `meta/quick-reference.md` instead of assuming the host root is the memory store.

- **Promoted `host_repo_root` into the bootstrap contract.** Added an optional `host_repo_root` field to `agent-bootstrap.toml`, taught the bootstrap resolver to return host-repo git state when configured, and taught the validator to reject malformed non-absolute values.

- **Updated the live router for host/worktree topology.** `meta/quick-reference.md` now makes the worktree split explicit: use `host_repo_root` for host-code git operations and the memory worktree for memory files and governance surfaces.

- **Enabled host-repo git log reads from the MCP layer.** `memory_git_log` now accepts a host-repo mode that resolves `host_repo_root` from `agent-bootstrap.toml`, rejects host paths nested inside the memory worktree, and returns commit history from the configured application repo.

- **Extended setup regression coverage.** Added end-to-end setup tests for orphan-branch creation, committed worktree materialization, worktree-targeted MCP config paths, and `--dry-run` safety. Also refreshed `setup/initial-commit-paths.txt`, `.gitattributes`, and the setup fixture so the new worktree tooling is preserved in the canonical seed commit.

**Reasoning:** The top-priority build plan was blocked on having a real entry point for worktree mode. Landing the Phase 0 path first creates a usable deployment command, proves the orphan-branch topology in tests, and establishes the minimal seed boundary that later adapter, validator, and host-repo freshness work can build on without mixing user-specific content into new worktree branches.

**Approved by:** user

---

## [2026-03-20] MCP runtime boundary formalized and semantic shim removed

**Changed:**

- **Finished the semantic split cleanup.** Deleted the transitional `engram_mcp/agent_memory_mcp/tools/semantic_tools.py` shim after the `semantic/` package became the complete Tier 1 registration surface.

- **Made the format/runtime boundary executable.** Added `engram_mcp/agent_memory_mcp/core/` as an import-safe namespace for the format and validation layer, made `engram_mcp.agent_memory_mcp` resolve runtime exports lazily, and added a `core` optional dependency group in `pyproject.toml`.

- **Updated seed and documentation surfaces.** Refreshed `setup/initial-commit-paths.txt` to include the new `core/` modules and `engram_mcp/tests/test_core_boundary.py`, and updated the MCP architecture docs to point at the semantic package rather than the removed monolithic file.

- **Added regression coverage for the boundary.** The new `engram_mcp/tests/test_core_boundary.py` asserts that the package root does not import the server eagerly and that the `core` namespace re-exports the format-layer modules consistently.

**Reasoning:** The runtime split was already complete in practice, but the repo still carried a tracked compatibility shim and an implicit package boundary. Removing the shim in the same commit that updates the tracked-file manifest closes the last Phase 3 cleanup without breaking setup-flow invariants. Formalizing the `core` namespace and lazy package-root behavior makes the format/runtime separation structural, not just descriptive, which improves reuse by validator/setup tooling and reduces accidental `mcp` coupling.

**Approved by:** user

---

## [2026-03-19] Compact bootstrap contract and validator enforcement

**Changed:**

- **Refactored the compact startup surfaces.** Rewrote `meta/quick-reference.md`, `plans/SUMMARY.md`, `chats/SUMMARY.md`, and `scratchpad/CURRENT.md` so the returning-session path is explicitly metadata-first: live state, next actions, retrieval guidance, and drill-down links remain in startup-loaded files while narrative history and extended analysis move out.

- **Defined explicit compact-path budgets and a whole-file strategy.** The live router now records per-file token targets for each startup-loaded file and makes the operating choice explicit: startup files should stay compact as whole files rather than depending on hidden startup-safe sections.

- **Aligned plan-summary generation with the new compact shape.** Updated the MCP helper that rewrites `plans/SUMMARY.md` blocks so routine plan updates preserve the compact `Scope / Progress / Next` format instead of reintroducing longer prose blocks.

- **Added validator and test coverage for compact drift.** Extended the validator and seed fixtures to check the compact-path contract directly, including localized file-size budgets, aggregate returning-session budget measurement, summary-shape requirements, and drift heuristics for archive-like narrative sprawl.

- **Added explicit drill-down and startup-conditional enforcement.** The validator now requires compact plan blocks, chat continuity, and current scratchpad handoffs to include drill-down references, and it enforces the expected `skip_if` rules for optional startup reads so manifest intent matches actual retrieval behavior.

- **Added a compact-budget inspection helper and recorded the post-migration measurement.** `HUMANS/tooling/scripts/inspect_compact_budget.py` now reports per-file compact-path usage in human or JSON form; the current compact startup payload measures `5705 / 7000` tokens, leaving `1295` tokens of headroom.

**Reasoning:** The compact returning path had drifted into an archive-like startup payload, blowing past its own budget and wasting recurring context on material that should have been loaded on demand. Making the compact contract explicit in the live router, preserving it in summary-generation helpers, enforcing drill-down and conditional-load behavior in the validator, and adding a lightweight inspection helper closes that loop. This improves consistency between docs, tooling, manifest behavior, and generated summaries; improves user-friendliness by keeping startup state readable and actionable; and improves context efficiency by restoring measurable headroom in the returning-session path.

**Approved by:** agent (pending review)

---

## [2026-03-19] First periodic review

**Changed:**

- **Ran the system's first full periodic review.** Loaded the full governance stack (`meta/integrity-checklist.md`, `meta/system-maturity.md`, `meta/update-guidelines.md`, `meta/belief-diff-log.md`, `meta/review-queue.md`, `meta/curation-policy.md`) and executed each checklist phase.

- **Assessed maturity as Stage 1 Exploration (retained).** All six maturity signals fell within Exploration bounds: ~8 sessions, 128 total ACCESS entries, ~15% file coverage, 0.05 confirmation ratio, zero identity drift, mean helpfulness ~0.6 in plans ACCESS sample. First formal assessment block written to `meta/system-maturity.md`.

- **Completed and published first belief diff.** Replaced the placeholder in `meta/belief-diff-log.md` with a full review entry documenting all knowledge files written since system inception, zero trust-level changes, zero identity drift, and the single integrity fix listed below.

- **Fixed one integrity violation.** `knowledge/_unverified/rationalist-community/SUMMARY.md` incorrectly carried `last_verified` in its frontmatter (quarantine-zone files must not set this field). Field removed.

- **Confirmed no instruction containment violations.** Grep flagged two files (`knowledge/literature/man-who-was-thursday.md`, `knowledge/literature/tree-of-smoke-top-down-bottom-up.md`); both confirmed false positives (ordinary prose, not imperative instructions).

- **Added two maintenance proposals to `meta/review-queue.md`:** (1) aggregate `plans/ACCESS.jsonl`, which has 100 entries against a 15-entry Exploration trigger; (2) establish a next-periodic-review trigger (20 sessions or first `_unverified/` promotion).

- **Updated `meta/quick-reference.md`** to record the first assessment date (2026-03-19, Exploration retained) and last periodic review date (2026-03-19).

**Reasoning:** The system had no prior periodic review on record. The maturity assessment was overdue (threshold: any time after first-run, by convention before significant plan execution). Running it now establishes a baseline, confirms governance parameters are appropriate for the current volume, and surfaces a practical maintenance debt (`plans/ACCESS.jsonl` aggregation). No stage transition was warranted.

**Approved by:** agent (pending review)

---

## [2026-03-18] Task-readiness contract for GitHub, network, and local tooling

**Changed:**

- **Added a repo-declared readiness manifest.** Created `HUMANS/tooling/agent-task-readiness.toml` to define task-aware preflight profiles for pull requests, branch publish, Python validation and dependency installs, Node validation and dependency installs, plus a generic workspace fallback. The contract now records cache/freshness rules, automation blocker carry-forward behavior, UI labels, and per-check fallback paths.

- **Added an executable readiness resolver prototype.** Created `HUMANS/tooling/scripts/resolve_task_readiness.py`, which validates the manifest, infers the relevant profile from task text and repo hints, runs GitHub/network/runtime/package-manager probes, classifies blockers (`missing`, `auth`, `config`, `connectivity`, `policy`, `repo_state`, `runtime`), and emits structured UI feedback including blocker carry-forward and restored-blocker attention states.

- **Added test and validator coverage.** Created `HUMANS/tooling/tests/test_task_readiness.py` to cover healthy publish readiness, missing `gh`, locked `gh` config, missing Python runtime, unauthenticated push, unchanged carried-forward blockers, and resolved blocker recovery. Extended `HUMANS/tooling/scripts/validate_memory_repo.py` and `HUMANS/tooling/tests/test_validate_memory_repo.py` so the readiness manifest becomes part of the repo contract and the minimal seed fixture includes the current MCP-preference guidance.

- **Kept seed and documentation surfaces aligned.** Updated `README.md`, `plans/codex-desktop-github-network-ergonomics.md`, `plans/SUMMARY.md`, and `setup/initial-commit-paths.txt` so the readiness prototype is documented, tracked in the canonical initial commit, and reflected in plan state. Also fixed stale seed-validator issues by restoring missing `origin_session` frontmatter on the AI-history quarantine files and normalizing the completed automation-continuity plan frontmatter.

**Reasoning:** The ergonomics gap was late discovery of environment blockers: GitHub auth issues, unreachable remotes, missing runtimes, and package-network failures were often discovered only after the work was already done. The new readiness contract makes those checks explicit, task-aware, and testable. It improves consistency by encoding the preflight logic once in a manifest plus resolver, improves user-friendliness by standardizing blocker messages and recovery states, and improves context efficiency by letting the app know which checks matter for the current task instead of front-loading every possible diagnostic.

**Approved by:** user

---

## [2026-03-18] MCP-preference contract aligned across entrypoints and setup

**Changed:**

- **Made MCP preference explicit in the agent entrypoints and governance docs.** Updated `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `README.md`, `meta/quick-reference.md`, `meta/update-guidelines.md`, `meta/curation-policy.md`, `meta/first-run.md`, and `meta/session-checklists.md` so the live contract now says: when local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes, with raw file access as a fallback when the MCP surface is missing or incomplete.

- **Extended the same contract into protected skill execution.** Updated `skills/SUMMARY.md`, `skills/onboarding.md`, `skills/session-start.md`, `skills/session-sync.md`, and `skills/session-wrapup.md` so both onboarding and returning-session procedures explicitly prefer the local memory MCP surface before falling back to direct file operations.

- **Aligned human setup surfaces with the same rule.** Updated `HUMANS/docs/QUICKSTART.md`, `setup/setup.sh`, and `setup/setup.html` to mention Codex desktop, describe the project-scoped `.codex/config.toml`, and add the same MCP-preference sentence to generated ChatGPT and generic prompt text.

- **Kept repo and validator surfaces in sync.** Added `.codex/config.toml` to `setup/initial-commit-paths.txt` and updated `HUMANS/tooling/scripts/validate_memory_repo.py` so adapter files, prompt-copy surfaces, governance runbooks, and the protected skill layer must all retain the MCP-preference contract.

**Reasoning:** The repo already shipped a local memory MCP and now includes a project-scoped Codex config, but the authoritative instruction surfaces still described startup and governance as if raw file access were the default interface. Making MCP preference explicit closes that gap. It improves consistency by aligning the adapters, governance docs, protected skill procedures, setup copy, and validator with the actual tool surface; improves user-friendliness by documenting Codex desktop behavior directly instead of leaving it implicit; and improves context efficiency by steering compatible agents toward the narrower memory-specific tool surface before they fall back to broader file operations.

**Approved by:** user

---

## [2026-03-18] Executable bootstrap resolver prototype

**Changed:**

- **Added a runtime bootstrap resolver prototype.** Created `HUMANS/tooling/scripts/resolve_bootstrap_manifest.py`, a repo-side tool that turns `agent-bootstrap.toml` into a concrete startup resolution with mode selection, ordered preload traces, skip reasons, and startup warnings for detached HEAD, branch drift, and branch collisions across worktrees.

- **Added test coverage for Phase 2 behavior.** Created `HUMANS/tooling/tests/test_bootstrap_resolver.py` to exercise mode-detection precedence, first-run heuristics, placeholder and inactive-plan skipping, duplicate-path deduplication, and warning generation.

- **Advanced the bootstrap implementation plan and reprioritized the queue.** Updated `plans/codex-desktop-bootstrap-support.md` and `plans/SUMMARY.md` to count startup-mode detection and deterministic preload ordering as completed prototype tasks, set the next bootstrap step to budgeting behavior, and move `codex-desktop-governed-memory-writes.md` into the top priority slot for the next plan.

- **Kept setup parity intact.** Added the new resolver script and test file to `setup/initial-commit-paths.txt` so fresh seed installs include the executable bootstrap prototype in the canonical initial commit.

**Reasoning:** The bootstrap-support plan had already progressed from prose into a manifest and validator-backed contract, but it still lacked an executable runtime model. Adding a resolver prototype makes the next layer of startup behavior concrete: the repo can now simulate mode detection, preload order, dedup semantics, and warning emission instead of describing them abstractly. That improves consistency between plan and tooling, preserves user-friendliness by making startup behavior inspectable, and protects context efficiency by keeping skip logic and summary-first loading visible in a trace rather than buried in agent convention.

**Approved by:** agent (pending review)

---

## [2026-03-18] Governed memory capability contract prototype

**Changed:**

- **Added a machine-readable governed-write contract.** Created `HUMANS/tooling/agent-memory-capabilities.toml` to define the current read-support tools, raw fallback write tools, semantic extension tools, shared `MemoryWriteResult` envelope, error taxonomy, operation ownership model, and explicit desktop-surface gaps.

- **Added capability resolution tooling.** Created `HUMANS/tooling/scripts/resolve_memory_capabilities.py`, which reads the contract and validates it against the live MCP runtime so the semantic write surface can be discovered and audited programmatically instead of inferred from code and prose separately.

- **Added contract tests and seed parity.** Created `HUMANS/tooling/tests/test_memory_capabilities.py` and added the new manifest, script, and tests to `setup/initial-commit-paths.txt` so the prototype is exercised in CI and preserved in the canonical initial commit.

- **Advanced the governed-writes product plan.** Updated `plans/codex-desktop-governed-memory-writes.md` and `plans/SUMMARY.md` to mark Phase 1 complete, document the invariant-ownership and result/error-taxonomy decisions, and move the next action to governance-class mapping.

**Reasoning:** The governed-memory-writes plan had a clear target but no executable contract tying the desktop product idea to the repo's existing MCP surface. The new capability manifest closes that gap: it makes the semantic tool set explicit, records which invariants each semantic operation owns, and separates covered desktop operations from known gaps such as ACCESS appends and reflection writes. That improves consistency between plan and code, gives future desktop discovery a concrete substrate, and keeps context efficiency high by encoding the contract once instead of re-deriving it from large source files each session.

**Approved by:** agent (pending review)

---

## [2026-03-18] Bootstrap manifest prototype and validator-backed preload contract

**Changed:**

- **Added a repo-declared bootstrap manifest prototype.** Created `agent-bootstrap.toml` as a machine-readable startup contract covering `first_run`, `returning`, `full_bootstrap`, `periodic_review`, and `automation` modes, along with mode-detection hints, token-budget ceilings, maintenance probes, on-demand summary expansions, and ordered preload steps.

- **Made the contract executable in tooling.** Extended `HUMANS/tooling/scripts/validate_memory_repo.py` and its test suite to parse and validate the manifest, enforce mode coverage and ordered step paths, and keep the manifest aligned with the repo's existing routing surface.

- **Aligned architecture and setup surfaces.** Updated `README.md` to describe `agent-bootstrap.toml` as the tool-facing companion to `meta/quick-reference.md`, and added the new file to `setup/initial-commit-paths.txt` so first-run setup preserves the bootstrap contract in the canonical seed commit.

- **Advanced the bootstrap product plan.** Updated `plans/codex-desktop-bootstrap-support.md` and `plans/SUMMARY.md` with Phase 2 runtime decisions: startup-mode precedence, dedup/skip semantics, budget hints, and the default rule that preloads remain visible but do not automatically count as ACCESS retrievals.

**Reasoning:** The bootstrap-support plan was already the highest-priority active implementation track, but it still lived mostly as prose. Adding a concrete manifest and validator-backed contract turns it into a working repo prototype: the preload graph is now explicit, reviewable in git, and testable for drift. That improves consistency across router/docs/tooling, gives compatible app runtimes a real artifact to consume, and preserves context efficiency by encoding compact-returning budgets and metadata-first probes in a single machine-readable place.

**Approved by:** user

---

## [2026-03-18] Human-facing core architecture guide

**Changed:**

- **Added a middle-layer architecture guide for people.** Created `HUMANS/docs/CORE.md` to explain the system's core design decisions, architectural principles, tradeoffs, and guiding philosophy in plain language for readers with different technical backgrounds.

- **Surfaced the new guide in the seed itself.** Updated `README.md` to point users to `CORE.md` alongside Quickstart and Design, expanded the repository structure listing to include it, and added the file to `setup/initial-commit-paths.txt` so it is part of the canonical first commit.

**Reasoning:** The repo already had a setup guide, a deep design essay, and a glossary, but it lacked a clear "why this architecture exists and how to think about it" document for people who need fundamentals before implementation detail. Adding that middle layer improves user-friendliness without increasing agent startup context, and it makes the system's core philosophy easier to understand, review, and preserve as the project evolves.

**Approved by:** user

---

## [2026-03-18] Setup commit allowlist, browser local dates, and wider contract enforcement

**Changed:**

- **Initial setup commit is now path-scoped.** Added `setup/initial-commit-paths.txt` as the canonical allowlist for the first setup commit, updated `setup/setup.sh` to stage only those repo-managed paths, and changed both the auto-commit and missing-git-identity guidance to use safe path-scoped commits instead of `git add -A`.

- **Shell/browser setup date parity restored.** Updated `setup/setup.html` to generate `created` dates from local date components rather than UTC ISO timestamps, preventing browser-generated starter files from drifting by a day near local midnight.

- **Operational wording and enforcement widened.** Updated the current setup, onboarding, wrap-up, and quickstart guidance to reinforce quick-reference-first routing rather than vague bootstrap language. The validator and tests are expanded to enforce this on the remaining high-value operational surfaces beyond `session-start`.

**Reasoning:** The repo already had strong routing and setup contracts, but three gaps remained: initial setup could still scoop unrelated local files into the first commit, browser setup did not actually match shell provenance semantics near midnight, and some high-value operational surfaces could drift back toward stale bootstrap-era wording without CI catching it. These changes make first-run setup safer, shell/browser behavior truly consistent, and the contract-enforcement layer cover the operator-facing and wrap-up surfaces that matter most.

**Approved by:** user

---

## [2026-03-18] Architectural guardrails for governance evolution

**Changed:**

- **System-change guardrails made explicit.** Added a new architectural guardrail section to `README.md` and a matching note to `meta/quick-reference.md` making consistency, user-friendliness, and context efficiency first-order considerations whenever agents review or modify the system itself.

- **Governance review criteria tightened.** Updated `meta/curation-policy.md` and `meta/update-guidelines.md` so periodic reviews and system-level change proposals must explicitly evaluate these three dimensions rather than treating them as implicit quality concerns.

- **Proposal and audit templates aligned.** Updated `meta/review-queue.md` and `meta/integrity-checklist.md` so governance proposals and integrity checks now capture architectural impact, operational drift, and context-budget regressions tied to those same guardrails.

**Reasoning:** The repo already emphasized routing authority, progressive disclosure, and context budgets, but those concerns were distributed across documents rather than stated as a shared architectural standard for self-modification. Making them explicit at the governing control points reduces the chance of future drift where a technically sound local change degrades cross-doc consistency, user operability, or compact-session efficiency.

**Approved by:** user

---

## [2026-03-18] Research plans architecture, SUMMARY anchors, MCP design, and commit conventions

**Changed:**

- **Four research plans created.** Added `plans/django-stack-research.md` (10 files across 7 phases: Celery Canvas, worker/beat ops, drf-spectacular, test factories, async, security, migrations), `plans/react-stack-research.md` (9 files across 8 phases: TanStack Query, react-hook-form+zod, TanStack Router, TypeScript patterns, Vitest/RTL/MSW, auth, performance, Vite build), `plans/devops-docker-research.md` (10 files across 9 phases: local compose, multi-worker celery, nginx, production config, CI/CD, zero-downtime deploys, secrets, Flower monitoring, database ops, dev tooling), and `plans/agent-memory-mcp.md` (the MCP enhancement plan — see separate changelog entry). `plans/SUMMARY.md` updated with BEGIN/END anchor blocks for each plan.

- **TanStack Router replacing React Router.** After creating the react-stack-research plan, all React Router references were updated to TanStack Router throughout the plan: Phase 2 tool description, prefetching note, auth protected routes, testing routing, performance code splitting, error boundaries, and the Notes section. Key topics: `validateSearch` + zod, `routerContext` + QueryClient, `beforeLoad` + `redirect()`, `lazyRouteComponent`.

- **SUMMARY.md machine-readable section anchors.** Applied `<!-- section: {id} -->` single anchors above each subject heading in `knowledge/SUMMARY.md` and `knowledge/_unverified/SUMMARY.md` to enable surgical section-level writes without full file replacement. Chose single-anchor scheme (not BEGIN/END pairs) for knowledge SUMMARY files since insert-at-section is sufficient; plans/ uses BEGIN/END pairs for full block replacement.

- **Commit message conventions expanded.** Added a comprehensive commit conventions section to `plans/agent-memory-mcp.md` covering: format (`[{category}] {Verb} {≤60 chars}`), a verb vocabulary table per category, deterministic Tier 1 tool commit message templates, optional structured body fields (`Session:`, `Plan:`, `Sources:`), and granularity rules (one logical unit per commit; not per-file-write, not end-of-session dump). `memory_commit` warns (not errors) on unrecognised prefix.

**Reasoning:** The system's first full working session established the knowledge-building roadmap and the tooling needed to maintain the memory system at scale. Research plans give the agent persistent, structured work queues that survive context resets. The SUMMARY anchors enable atomic targeted updates without read-modify-write overhead on full files. The commit conventions make agent-generated git history meaningful and reviewable rather than opaque.

**Approved by:** user

---

## [2026-03-18] Agent-memory MCP — enhanced read/write/commit layer plan

**Changed:**

- **`plans/agent-memory-mcp.md` created.** Full design plan for a two-tier MCP write layer. Tier 1 semantic tools (5 planned: `memory_mark_plan_item_complete`, `memory_promote_knowledge`, `memory_add_knowledge`, `memory_update_identity`, `memory_add_access_entry`) own all invariants and auto-commit. Tier 2 low-level tools (`memory_write`, `memory_edit`, `memory_delete`, `memory_move`, `memory_update_frontmatter`, `memory_commit`, `memory_diff`) are staged without auto-commit for batching. All tools use version tokens (git hash-object) for optimistic locking and return a `MemoryWriteResult` dataclass.

- **`memory_delete` directory restriction designed.** Hard `PermissionError` before any filesystem access for paths outside `knowledge/`, `plans/`, `scratchpad/`. Within allowed directories, the tool auto-calls `allow_cowork_file_delete` on the caller's behalf. `identity/`, `meta/`, `chats/`, and `skills/` are protected.

- **Error taxonomy defined.** `ConflictError` (version mismatch), `NotFoundError`, `ValidationError`, `AlreadyDoneError` (idempotency — distinct from success), `StagingError`, `PermissionError`. `AlreadyDoneError` is intentional: callers need to distinguish "I just did it" from "it was already done."

**Reasoning:** All memory writes currently go through raw Edit/Write/Bash tools with no knowledge of the system's invariants. The MCP layer moves correctness obligations (frontmatter updates, SUMMARY.md sync, ACCESS.jsonl entries, commit format) from the agent's attention to the tool implementation, making memory writes reliably correct instead of fragile by convention.

**Approved by:** user

---

## [2026-03-18] Optional verification dates, setup parity, and scoped onboarding commits

**Changed:**

- **Provenance contract updated.** Reworked `meta/update-guidelines.md`, `meta/curation-policy.md`, `meta/quick-reference.md`, `meta/integrity-checklist.md`, and `HUMANS/docs/GLOSSARY.md` so `last_verified` is now optional until a human actually confirms the content. Decay and freshness guidance now use the effective verification date (`last_verified` when present, otherwise `created`).

- **Template setup no longer self-verifies content.** Removed `last_verified` from the starter profile templates and the browser-generated template frontmatter. Updated `setup/templates/profiles/README.md` to document that onboarding is the point where template-backed content becomes human-verified.

- **Shell/browser setup parity restored.** Extended `setup/setup.sh` with `--user-name` and `--user-context` plus matching interactive prompts, and changed its generated `identity/SUMMARY.md` to include the same personalization markers and copy used by `setup/setup.html`. Updated `HUMANS/docs/QUICKSTART.md` to document the new flags and parity.

- **Returning-session startup contract aligned.** Rewrote `skills/session-start.md` so it expands the compact returning manifest from `meta/quick-reference.md` rather than assuming a README-first bootstrap, and switched its review-queue guidance to the metadata-first rule.

- **Validator and tests hardened.** Relaxed `HUMANS/tooling/scripts/validate_memory_repo.py` to accept missing `last_verified`, added startup-skill contract checks, expanded validator tests for optional verification dates, added shell/browser setup parity tests, and added an onboarding import regression test for dirty worktrees.

- **Onboarding import commits scoped to written paths.** Updated `HUMANS/tooling/scripts/onboard-export.sh` so it stages only files written by the current import and uses a path-scoped commit, preventing unrelated pre-staged changes from being swept into the onboarding commit. Manual commit instructions now use the same safe path-scoped form.

**Reasoning:** The previous implementation had drifted in four connected ways: it could not represent genuinely unverified content despite the trust model depending on that state, template setup flows were marking content as verified before any human confirmation, the detailed session-start skill still pulled agents toward the deprecated README-heavy path, and onboarding imports could accidentally commit unrelated staged work. These changes make the provenance model, setup flows, startup guidance, import behavior, validator, and tests agree on one safer operational contract.

**Approved by:** user

---

## [2026-03-17] Quick-reference routing, root setup wrappers, and contract enforcement

**Changed:**

- **Operational routing moved to `meta/quick-reference.md`.** Updated `README.md`, `meta/quick-reference.md`, `meta/session-checklists.md`, `meta/first-run.md`, `meta/update-guidelines.md`, and the platform adapter files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`) so normal returning sessions start with `meta/quick-reference.md`. `README.md` now serves as architecture and full-bootstrap reference material rather than mandatory returning-session overhead.

- **Compact returning manifest redesigned.** Tightened the compact path to `meta/quick-reference.md`, `identity/SUMMARY.md`, non-placeholder `chats/SUMMARY.md`, substantive scratchpad files, and only task-relevant `knowledge/` or `skills/` summaries. Added metadata-first maintenance guidance for `meta/review-queue.md` and `ACCESS.jsonl` checks, and restated the compact-session budget as `~3,000–6,000` across the canonical docs.

- **Repo-root setup compatibility entrypoints.** Added root `setup.sh` and `setup.html` wrappers that forward to the canonical implementation in `setup/`. Updated `README.md`, `HUMANS/docs/QUICKSTART.md`, `setup/setup.sh`, and `setup/setup.html` to prefer the root entrypoints while keeping `setup/` as the implementation home.

- **Validator, tests, and CI hardened.** Reworked `HUMANS/tooling/scripts/validate_memory_repo.py` to enforce quick-reference-first routing, root setup entrypoints, adapter/prompt consistency, and the compact-manifest contract. Expanded `HUMANS/tooling/tests/test_validate_memory_repo.py` to cover the new routing language, root wrappers, manifest shape, and compact-budget ceiling. Updated CI shellcheck coverage to include the new root `setup.sh`.

**Reasoning:** The prior contract drifted in three damaging ways: returning sessions were routed through the heavyweight `README.md` path instead of the live manifest, human-facing setup instructions pointed to entrypoints that did not exist at the repo root, and CI only validated copied phrases rather than the actual operational model. These changes make the routing authority, user-facing setup surface, context-budget guidance, and enforcement tooling agree on a single compact returning-session workflow while preserving compatibility for existing setup instructions.

**Approved by:** user

---

## [2026-03-17] Canonical provenance, read-only onboarding fidelity, and setup routing cleanup

**Changed:**

- **Canonical `origin_session` contract.** Updated `meta/update-guidelines.md`, onboarding examples, and related docs so `origin_session` now uses the canonical form `chats/YYYY/MM/DD/chat-NNN | setup | manual | unknown`. Bare `chat-NNN` values are now documented as legacy-only. Tightened `scripts/validate_memory_repo.py` to enforce the canonical form while warning on legacy bare chat ids.

- **Read-only onboarding round-trip preservation.** Expanded `scripts/onboard-export-template.md` to include top-level `session_id` / `session_date` metadata and a `## Session Transcript` section. Reworked `scripts/onboard-export.sh` to parse canonical exports, preserve the original session path/date, recreate `transcript.md`, write chat summaries without provenance frontmatter, and fall back with a visible warning for legacy three-section exports.

- **README-routed setup prompts.** Updated the ChatGPT and generic prompt text in `setup.sh`, `setup.html`, and `QUICKSTART.md` so generated prompts tell models to start with `README.md` and follow its routing rules, explicitly pointing returning sessions to `meta/session-checklists.md` instead of hardcoding the full bootstrap on every run.

- **Browser setup scope clarity.** Reframed `setup.html` and `QUICKSTART.md` to describe the browser flow as a local starter-file generator rather than a full parity replacement for `setup.sh`. Browser copy now explicitly states that git remote setup remains manual.

- **Unified context-budget messaging and broader tests.** Replaced conflicting token estimates in `README.md`, `QUICKSTART.md`, and `meta/quick-reference.md` with a shared three-row planning table for first-run bootstrap, returning compact sessions, and full bootstrap / periodic review. Expanded the test suite to cover canonical/legacy provenance validation, onboarding import behavior, prompt-copy consistency, and context-budget copy drift.

**Reasoning:** The prior system had a real contract drift problem: provenance examples emitted incompatible `origin_session` formats, read-only onboarding could not faithfully recreate the original first session, generated prompts ignored the compact returning-session path and wasted context, and the browser setup copy overpromised parity with the shell setup flow. These changes make the written rules, generated artifacts, and enforcement tooling agree on one operational model, while preserving backward compatibility for older exports and legacy provenance values.

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
