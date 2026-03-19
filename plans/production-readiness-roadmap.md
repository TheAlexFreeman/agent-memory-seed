---
created: 2026-03-18
last_verified: 2026-03-18
next_action: "Reconcile this roadmap with the current HUMANS/tooling layout before reactivating it"
origin_session: manual
source: agent-generated
status: paused
trust: medium
type: implementation-plan
---

# Production-Readiness Roadmap

This roadmap assumes the current repository remains a beta proving ground. The production target is not "ship this branch unchanged"; it is "extract the smallest durable governance core from this branch into the next architecture iteration without losing the working safety model."

## Scope and intent

- Preserve what is already working: markdown/JSONL as canonical state, explicit provenance, trust-weighted retrieval, protected-tier boundaries, and derived-state rebuildability.
- Treat setup UX, template polish, and backward compatibility as secondary until the governance core is stable enough to freeze.
- Use this branch to prove contracts, tests, and operational behavior before lifting the core into a cleaner production-oriented package.

## Sanity-checked current baseline

The repository already has meaningful building blocks that should be treated as inputs to the extraction plan rather than rewritten casually:

- Runtime and governance guidance exists and is internally cross-checked through [`meta/quick-reference.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/meta/quick-reference.md), [`meta/session-checklists.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/meta/session-checklists.md), [`meta/update-guidelines.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/meta/update-guidelines.md), and [`meta/curation-policy.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/meta/curation-policy.md).
- The repo already ships a validator and test coverage for the file-format contract in [`scripts/validate_memory_repo.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/scripts/validate_memory_repo.py) and [`tests/test_validate_memory_repo.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/tests/test_validate_memory_repo.py).
- A derived-state engine exists in [`engine/memory_engine_core/engine.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/engine/memory_engine_core/engine.py) with a shared service layer in [`engine/memory_engine_service/service.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/engine/memory_engine_service/service.py).
- A thin MCP surface already exists in [`engine/memory_mcp/server.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/engine/memory_mcp/server.py), with CI smoke coverage in [`.github/workflows/ci.yml`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/.github/workflows/ci.yml) and behavioral coverage in [`tests/test_memory_mcp.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/tests/test_memory_mcp.py).
- The design docs already distinguish current capability from future direction in [`docs/DESIGN.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/docs/DESIGN.md), [`docs/memory-engine-phase-2.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/docs/memory-engine-phase-2.md), and [`docs/memory-engine-phase-3-ready.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/docs/memory-engine-phase-3-ready.md).

## What is not production-ready yet

The current branch proves ideas, but it does not yet define a production-grade extraction boundary:

1. Governance rules are still split between prose and code. Validation exists, but key behaviors still depend on models following markdown instructions correctly.
2. There is no versioned public contract for the canonical schema, derived-state schema, CLI surface, or MCP tool semantics.
3. Release engineering is thin. CI exists, but there is no packaged distribution, release process, upgrade path, or compatibility policy.
4. Operational safety is partial. The repo has provenance and protected-tier concepts, but not a hardened proposal/apply workflow, rollback tooling, or audit-focused observability.
5. Migration is undefined. There is no formal plan for extracting the governance kernel into a new package or service while keeping this repo as a seed/reference implementation.

## Target architecture for extraction

The production extraction should separate three layers cleanly:

1. `canonical memory format`
   - The file/folder contract, frontmatter schema, ACCESS schema, and governance categories.
2. `governance runtime`
   - Deterministic code that enforces validation, trust policy, read/write boundaries, aggregation rules, proposal workflows, and migration rules.
3. `adapters`
   - CLI, MCP, setup flows, browser wizard, and future platform integrations.

The production milestone is reached when layer 2 is stable and testable independent of this repository's human-facing docs.

## Roadmap

### Phase 0: Freeze the extraction boundary

Goal: decide what the "functional governance core" actually includes before more beta features accrete around it.

Deliverables:

- Write a short architecture decision record that names the production core modules and explicitly excludes beta-only surfaces.
- Define the canonical contracts that must survive extraction:
  - frontmatter schema
  - ACCESS entry schema
  - trust/provenance decision points
  - aggregation trigger semantics
  - protected/proposed/automatic change classes
- Mark each existing file or subsystem as one of:
  - `core and extract`
  - `reference only`
  - `beta UX`
  - `defer`

Exit criteria:

- There is a written list of production-owned contracts.
- There is a clear answer to whether the next iteration is a library, service, or both.

### Phase 1: Move governance from prose-first to code-first

Goal: make the production core executable and deterministic.

Work:

- Extract policy evaluation into code-level primitives instead of leaving behavior distributed across markdown instructions.
- Add explicit modules for:
  - schema validation
  - trust-weighted retrieval decisions
  - change-category classification
  - aggregation eligibility
  - protected-write gating
- Keep markdown docs as explanations and operator guides, not the only source of truth.
- Add tests that prove the runtime behavior matches the documented policy.

Concrete repository implications:

- Build on [`scripts/validate_memory_repo.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/scripts/validate_memory_repo.py) rather than replacing it with a second validator.
- Build on [`engine/memory_engine_service/service.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/engine/memory_engine_service/service.py) as the first stable runtime boundary.
- Keep [`meta/quick-reference.md`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/meta/quick-reference.md) as data, but stop encoding critical behavior only in prose.

Exit criteria:

- Policy behavior can be exercised by tests without reading markdown.
- A reference implementation can explain every important read/write decision from code paths, not just documentation.

### Phase 2: Version the contracts

Goal: make the core safe to adopt outside this branch.

Work:

- Introduce explicit versioning for:
  - canonical file schema
  - ACCESS schema
  - derived database schema
  - CLI command contract
  - MCP tool payloads and errors
- Publish a compatibility policy:
  - what is stable
  - what is beta
  - what can break between minor iterations
- Add migration fixtures covering old repo states and mixed-version content.

Concrete repository implications:

- The typed result shapes in [`engine/memory_engine_service/service.py`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/engine/memory_engine_service/service.py) and the MCP smoke coverage in [`.github/workflows/ci.yml`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/.github/workflows/ci.yml) are the starting point, not the finish line.
- The validator tests should gain compatibility fixtures, not just happy-path checks.

Exit criteria:

- A downstream consumer can pin to a documented contract version.
- Schema and tool changes require migration notes and compatibility tests.

### Phase 3: Harden write-path safety

Goal: make production writes reviewable, auditable, and rollback-safe.

Work:

- Add a formal proposal/apply model for non-automatic writes.
- Make protected-tier enforcement a runtime rule, not just a documented convention.
- Add idempotent write helpers, conflict detection, and audit events for state-changing operations.
- Implement rollback-oriented tests for partially failed writes and concurrent update attempts.

Concrete repository implications:

- Reuse the existing service error boundary and lock-based write patterns where they already exist.
- Keep canonical writes narrow until the proposal/apply flow is proven.
- Do not broaden MCP writes beyond ACCESS logging until protected-write behavior is enforced centrally.

Exit criteria:

- Every non-automatic mutation has a deterministic enforcement path.
- Failed writes are recoverable and leave the repo in a valid state.

### Phase 4: Production packaging and operations

Goal: make the extracted core installable, observable, and supportable.

Work:

- Package the governance core as a proper distributable Python package.
- Add release automation, changelog discipline, and tagged versions.
- Expand CI into a release-quality pipeline:
  - matrix testing
  - packaging/install smoke tests
  - migration fixtures
  - performance regression checks on large synthetic repos
- Add operator-facing diagnostics:
  - health/status command
  - structured error codes
  - audit-friendly logs

Concrete repository implications:

- Existing CI in [`.github/workflows/ci.yml`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/.github/workflows/ci.yml) is a good seed, but production needs install-time and upgrade-time verification.
- [`pyproject.toml`](/C:/Users/Owner/.codex/worktrees/e83a/agent-memory-seed/pyproject.toml) is currently enough for local tooling, not for a real release story.

Exit criteria:

- A fresh environment can install, validate, and run the core from a release artifact.
- Operational failures are diagnosable without reading source.

### Phase 5: Extract into the next architecture iteration

Goal: move the proven core out of this beta branch without losing the branch as a live seed/reference repo.

Work:

- Create the new home for the production core with the minimum viable module split:
  - canonical schema and validation
  - governance runtime
  - adapter interfaces
- Keep this repository as:
  - a seed template
  - a reference corpus
  - a compatibility fixture set
  - a beta feature incubator
- Add an import/export or migration tool that can verify a repo created here works against the extracted core.
- Document the ownership boundary between the new production package and this repository.

Exit criteria:

- The new core can govern this repo from the outside.
- This branch can continue experimenting without silently redefining the production contract.

## Recommended sequencing

If time is limited, the highest-leverage order is:

1. Freeze the extraction boundary.
2. Move governance-critical behavior into executable code.
3. Version the contracts.
4. Harden write paths.
5. Package and release.
6. Extract into the next iteration.

This order avoids a common failure mode: packaging a beta architecture before the real stability boundary is known.

## Non-goals for the first production cut

These can stay beta unless they directly block the governance core:

- richer setup UX
- more starter templates
- visualization/dashboard work
- broad third-party sync
- multi-user support
- semantic retrieval beyond the existing derived-state/query model

## Production readiness bar

The extracted governance core is ready for a first production release when all of the following are true:

- Canonical schemas and runtime decision points are versioned.
- Policy behavior is enforceable from code without relying on a model to interpret prose correctly.
- Non-automatic writes have centralized gating, auditability, and rollback behavior.
- CLI and MCP surfaces are explicitly documented as stable or beta.
- Upgrade and downgrade behavior is tested against real historical repo fixtures.
- This repository can act as a compatibility corpus for the extracted core.
