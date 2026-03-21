---
created: 2026-03-19
last_verified: '2026-03-19'
completed: '2026-03-19'
next_action: null
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan
category: research
---

# Research Plan: Systems Architecture for Agent Memory

## Goals

Build a deep, first-principles understanding of the storage, concurrency, and data
modeling primitives that underpin this system — and that would unlock its most
important architectural improvements. The research is motivated by concrete open
problems encountered during code review and implementation work: the filesystem lock
issue that blocked git operations, the multi-file atomicity gap in the MCP write
tools, the ACCESS.jsonl scaling question, and the absence of a principled schema
evolution story.

Every topic is tied back to a specific architectural decision or known gap. This is
not a survey for its own sake.

All output files go to `knowledge/_unverified/systems-architecture/`.

---

## Existing coverage (do not duplicate)

- `knowledge/tooling/codex-mcp-timeouts-git-stdin.md` — git subprocess timeouts and
  stdin handling in MCP context; operational, not architectural
- `knowledge/_unverified/devops/docker-compose-local-dev.md`,
  `celery-multi-worker-docker.md` — container orchestration and process isolation

---

## Research phases

### Phase 1 — Git internals · ☑ 3/3 complete

**Why first:** The entire system is built on git as its storage layer, and three open
problems are directly rooted in incomplete understanding of git's internals: (1) the
`index.lock` mechanism that blocked all index operations in a sandboxed filesystem
mount, (2) the worktree integration plan (Phase 0 of `worktree-integration.md`)
which requires precise understanding of the orphan branch → worktree topology, and
(3) the plan to add git hooks for governance automation.

1. ☑ `git-object-model.md`

   - **The four object types:** blob (file content), tree (directory snapshot), commit
     (history node), tag (named ref). How each is stored: header + content,
     SHA-1/SHA-256 hash as filename, zlib-compressed, content-addressed.
   - **The index (staging area):** binary file format (cache entries, stat data,
     extension blocks), what `git add` actually does (writes blob to object store,
     updates index), why the index is a crucial intermediate state between working
     tree and history.
   - **The index lock mechanism:** why git creates `.git/index.lock` before any index
     mutation, what `O_CREAT | O_EXCL` achieves at the OS level, why `rename()` into
     place is the atomic commit step, what happens when the lock file cannot be
     unlinked (the exact failure mode this system hit in a sandboxed FUSE mount).
   - **Pack files and delta compression:** loose objects vs. packed objects, when
     `git gc` packs, delta chains, pack index format. Relevant because the memory
     repo will grow and pack behavior determines long-term performance.
   - **Refs and symbolic refs:** how `HEAD`, `refs/heads/*`, `refs/remotes/*` work as
     plain-text files, `ORIG_HEAD`, `FETCH_HEAD`, `MERGE_HEAD`. The reflog as a
     recovery mechanism.
   - **Architectural relevance:** understanding the object model clarifies why the MCP
     server's `git_repo.py` cannot simply "write and commit atomically" — the staging
     step is load-bearing, not boilerplate.

2. ☑ `git-worktrees-and-hooks.md`

   - **Worktree topology:** how `git worktree add` creates a linked worktree, the
     `.git/worktrees/<name>/` directory inside the main gitdir, the `gitdir` file in
     the worktree that points back, what is shared (object store, refs, remotes) vs.
     what is per-worktree (index, HEAD, working tree, some hooks).
   - **Orphan branches:** `git checkout --orphan` mechanics, why the initial commit
     creates a root commit with no parents, how orphan branches share the object store
     without sharing history. The `--no-checkout` flag for seeding without touching
     the working tree.
   - **Git hooks:** the complete hook inventory (`pre-commit`, `post-commit`,
     `post-checkout`, `post-merge`, `pre-push`, `update`, `post-receive`), per-hook
     execution context (which directory, what env vars, what exit code means), the
     distinction between client-side hooks (per-checkout) and server-side hooks
     (per-bare-repo). How worktrees interact with hooks: hooks live in the main
     `.git/hooks/` and run for all worktrees.
   - **Hook use cases for this system:** a `post-commit` hook that triggers
     knowledge freshness checks, a `pre-commit` hook that runs `validate_memory_repo
     .py` to enforce frontmatter before any commit lands, a `post-checkout` hook that
     reinitializes the MCP server config when the worktree is first created.
   - **Architectural relevance:** directly required for `worktree-integration.md`
     Phases 0–1. The hook model is how governance automation escapes depending on the
     agent to "remember" to validate.

3. ☑ `git-plumbing-and-automation.md`

   - **Plumbing vs. porcelain:** why `git add` / `git commit` / `git checkout` are
     unsafe to parse in scripts (locale-sensitive output, interactive prompts,
     unversioned output format). The stable plumbing commands: `git hash-object`,
     `git update-index`, `git write-tree`, `git commit-tree`, `git update-ref`,
     `git cat-file`, `git ls-files`, `git rev-parse`, `git for-each-ref`.
   - **Scripting a commit without the index lock:** using
     `git hash-object -w --stdin`, `git update-index --add --cacheinfo`, and
     `git commit-tree` to construct a commit that bypasses the index entirely. This
     is the pattern that would have let the P0 commit land even with a stale
     `index.lock` in the sandboxed filesystem.
   - **`git notes`:** attaching metadata to commits without rewriting history. Relevant
     for attaching curation annotations (e.g., "this commit introduced a governance
     violation, patched in X") without amending.
   - **`git bundle`:** creating a self-contained archive of a repo or branch for
     transfer without a remote. Relevant for the memory store export/import workflow
     that `onboard-export.sh` partially implements.
   - **`git sparse-checkout`:** loading only a subset of files from a branch.
     Relevant for the worktree integration when the memory branch is large and the
     host project only needs to expose certain files to its agents.
   - **Architectural relevance:** the MCP server's `git_repo.py` currently uses
     porcelain commands throughout. Understanding plumbing enables more robust
     automation and the index-bypass commit path needed for locked-filesystem
     resilience.

---

### Phase 2 — Filesystem semantics and OS-level locking · ☑ 2/2 complete

**Why second:** The index lock incident was a symptom of a deeper gap: the system
makes assumptions about filesystem atomicity and POSIX locking semantics that do not
hold uniformly across environments (sandboxed mounts, FUSE filesystems, network
filesystems, Windows). Understanding the actual OS contracts makes the MCP server
resilient by design rather than by luck.

4. ☑ `filesystem-atomicity-and-locking.md`

   - **POSIX `rename()` atomicity:** the guarantee that `rename(src, dst)` is atomic
     with respect to other processes seeing either the old or new filename — never a
     partial state. Why this is the standard idiom for safe file replacement (write to
     temp → rename to dest). Filesystem-dependent caveats: NFS before v4 is not
     atomic, some FUSE implementations do not guarantee atomicity.
   - **`O_CREAT | O_EXCL` for lock files:** why this is the correct primitive for
     creating a lock file (creates only if absent, fails atomically if present),
     contrast with test-then-create (TOCTOU race). How git uses this for
     `.git/index.lock`.
   - **POSIX advisory locking (`flock`, `fcntl`):** mandatory vs. advisory locking,
     `flock(LOCK_EX)` for exclusive access, `LOCK_NB` for non-blocking try, why
     advisory locks are not enforced by the kernel against processes that don't
     cooperate. Contrast with mandatory locks (Linux-specific, not widely used).
   - **Why `unlink()` can fail:** permission bits vs. sticky bit, immutable flags
     (`chattr +i` on Linux, `chflags uchg` on macOS), FUSE filesystems that restrict
     unlink even for the file owner (the exact failure mode encountered), read-only
     mounts, SELinux/AppArmor policy.
   - **`fsync()` and durability:** why `write()` + `close()` is not sufficient for
     durability, what `fsync()` actually guarantees (flushes kernel buffer to device),
     `fdatasync()` (data only, not metadata), `O_SYNC` (synchronous writes). Why
     databases call `fsync()` before acknowledging a commit. Whether git calls
     `fsync()` (configurable via `core.fsync`).
   - **Architectural relevance:** directly explains the `index.lock` incident and
     informs the design of the index-bypass commit path (Phase 1, item 3), the
     worktree init script's error handling, and any future locking in the MCP server.

5. ☑ `filesystems-for-developers.md`

   - **Journaling filesystems (ext4, NTFS, HFS+):** journal modes (writeback,
     ordered, data journaling), what each protects against on crash, why ordered mode
     is the ext4 default. Practical implication: power-loss during a git commit will
     not corrupt objects but may leave the index partially written.
   - **Copy-on-write filesystems (btrfs, ZFS, APFS):** the COW principle (never
     overwrite, write new block and update pointer), how this enables instant
     snapshots and checksums, why COW makes `rename()` not necessarily cheaper than
     a copy. APFS's atomic safe-save primitive as an OS-level rename guarantee.
   - **FUSE filesystems:** how FUSE works (kernel VFS → FUSE kernel module → userspace
     daemon), performance characteristics (extra context switches), which POSIX
     operations FUSE implementations commonly deviate from (unlink permissions,
     rename atomicity, lock semantics). Why the sandboxed filesystem in Cowork
     behaves differently from a local ext4 mount.
   - **inotify / FSEvents / kqueue:** kernel file-change notification APIs, the event
     types (IN_MODIFY, IN_CREATE, IN_DELETE, IN_MOVE), coalescing and ordering
     guarantees, why recursive watchers on large directories are expensive. Relevance
     to the worktree integration's freshness-detection requirement (detecting when
     host codebase files change).
   - **Network filesystems (NFS, SMB/CIFS):** why NFS locking semantics differ
     (NLM protocol for pre-NFSv4, stateful locks in NFSv4), SMB opportunistic locking
     (oplocks), why git warns about NFS repos. Practical guidance for users who keep
     their repos on network shares.
   - **Architectural relevance:** informs the validator's environment checks,
     the MCP server's graceful degradation when filesystem capabilities are limited,
     and the inotify-based freshness detection in `worktree-integration.md` Phase 2.

---

### Phase 3 — Append-only logs, WAL design, and compaction · ☑ 2/2 complete

**Why third:** `ACCESS.jsonl` is an append-only log. The governance spec calls for
aggregation at 15 entries per folder — a trivial threshold that will be hit frequently
as the system matures. Understanding how production systems manage growing append-only
logs informs both the immediate implementation of the aggregation trigger and the
longer-term question of whether JSONL is the right format at scale.

6. ☑ `write-ahead-logging-and-wal-design.md`

   - **WAL fundamentals:** why write-ahead logging (WAL) is the universal mechanism
     for durable, crash-recoverable writes, the invariant ("log before apply"), the
     checkpoint operation (flush WAL to main storage), recovery protocol (replay from
     last checkpoint).
   - **SQLite WAL mode:** the WAL file (`-wal`), the shared-memory index (`-shm`),
     how concurrent reads and a single writer coexist, checkpoint behavior
     (`PRAGMA wal_checkpoint`), why WAL mode is better for concurrent access than
     journal mode. Concrete relevance: the SQLite index referenced in the production
     roadmap as a future derived-state store.
   - **PostgreSQL WAL:** WAL segments, LSN (log sequence number), CHECKPOINT,
     replication via WAL streaming (WAL sender/receiver), WAL archiving. Why
     understanding Postgres WAL is useful for Django backend developers operating
     Postgres in production.
   - **The git staging area as a mini-WAL:** how `git add` (write to index) followed
     by `git commit` (write to object store, update refs) mirrors the WAL pattern:
     index is the log, object store is the stable state, commit is the checkpoint.
     Why partial failures (crash between `add` and `commit`) leave the repo
     recoverable.
   - **Implications for the MCP server:** the multi-file write atomicity gap identified
     in the code review — staging multiple files and committing together is the correct
     WAL-style pattern; the gap is the absence of rollback if staging fails partway
     through.

7. ☑ `append-only-logs-and-compaction.md`

   - **Log-structured storage:** the append-only log as the universal write path, why
     appending is faster than random writes (sequential I/O), the trade-off: reads
     require scanning or an index.
   - **LSM trees (Log-Structured Merge Trees):** the memtable → immutable memtable →
     SSTable flush cycle, level compaction (LevelDB, RocksDB), size-tiered compaction
     (Cassandra), write amplification vs. read amplification trade-off, tombstones for
     deletes. Directly relevant: how RocksDB compacts its WAL into SSTables is
     analogous to how `ACCESS.jsonl` entries should be aggregated into derived
     summaries.
   - **Kafka log compaction:** the difference between time-based retention (delete old
     segments) and log compaction (keep only the latest value per key), the compaction
     cleaner thread, tombstone records. Directly relevant: ACCESS entries for the same
     file are like Kafka records for the same key — we want to keep the latest
     aggregate, not all 15 raw entries.
   - **JSONL rotation and archival:** standard patterns for rotating append-only JSON
     log files (size-based, time-based, count-based), naming conventions
     (`ACCESS.jsonl` → `ACCESS.archive.2026-03.jsonl`), index files for efficient
     lookup without scanning archives. The gap: the system documents a concept of
     `ACCESS.archive.jsonl` but has no implementation or rotation policy.
   - **Event sourcing and CQRS:** treating the log as the source of truth and
     materialized views as derived state. The ACCESS.jsonl + SUMMARY.md pattern is
     already event sourcing in spirit: raw access events → aggregated helpfulness
     summaries. Understanding CQRS clarifies why the summary is always rebuildable
     from the log and why the log should never be edited.
   - **Architectural relevance:** directly informs the ACCESS.jsonl aggregation
     trigger implementation, the archive rotation policy, and the long-term derived
     state strategy from the production readiness roadmap.

---

### Phase 4 — Concurrency, CRDTs, and conflict-free writes · ☑ 2/2 complete

**Why fourth:** The system currently assumes one writer at a time. The worktree
integration and codebase-knowledge use case both increase the likelihood of multiple
agents (or a human + an agent) writing to the same memory branch concurrently.
Understanding the concurrency design space distinguishes "we haven't designed for
this" from "we can't design for this."

8. ☑ `concurrency-models-for-local-state.md`

   - **Optimistic vs. pessimistic concurrency control:** pessimistic (take a lock
     before reading, hold until write complete), optimistic (read without locking,
     validate before write, retry on conflict). The system's version tokens are
     optimistic concurrency control — understand the full pattern: read with version,
     compute changes, compare-and-swap, retry if version changed.
   - **MVCC (multi-version concurrency control):** keeping multiple versions of a
     record simultaneously (PostgreSQL, SQLite in WAL mode), readers see a consistent
     snapshot without blocking writers. Relevance: if the memory store ever uses a
     SQLite derived-state DB, MVCC is what makes concurrent read + write safe.
   - **The actor model:** Erlang/Akka actors as an alternative to shared-memory
     concurrency, each actor has exclusive ownership of its state, communicates via
     message passing. Relevance: if the MCP server is the sole writer and all external
     access goes through it, the server is effectively an actor — understanding the
     model clarifies why this design is safe by construction.
   - **Lock-free and wait-free data structures:** the fundamentals of CAS
     (compare-and-swap) as a hardware primitive, lock-free stacks and queues,
     why lock-free is hard to get right and rarely needed in single-writer systems.
     Understanding the limits of lock-free design clarifies when to use it vs. when
     the actor model is a simpler answer.
   - **Architectural relevance:** clarifies the design space for multi-agent concurrent
     writes, informs the version token implementation in `semantic_tools.py`, and
     provides the background for CRDT-based text merging.

9. ☑ `crdts-and-collaborative-text.md`

   - **CRDT fundamentals:** convergent replicated data types (CvRDTs / state-based)
     vs. commutative replicated data types (CmRDTs / operation-based), the
     mathematical property: all replicas converge to the same state regardless of
     operation order, given all operations are delivered.
   - **G-Counter, PN-Counter, OR-Set:** the canonical simple CRDTs, how they work,
     why they converge. Builds intuition for how CRDT composites (like a document)
     are constructed.
   - **Automerge:** a CRDT implementation for JSON documents and text. How Automerge
     represents a document as a sequence of operations with unique IDs, how it merges
     concurrent edits to the same document without conflicts. Why Automerge is
     relevant: if two agents write to the same `SUMMARY.md` concurrently, a
     CRDT-based approach would produce a deterministic merge instead of a git
     conflict.
   - **Yjs:** another CRDT implementation (Y-Text for character-level text,
     Y-Map/Y-Array for structures), used in collaborative editors (Obsidian live
     sync, Notion-like tools). Compare to Automerge: Yjs is faster but less
     expressive; Automerge tracks history better.
   - **Operational Transform (OT):** the alternative to CRDTs for collaborative
     editing (used in Google Docs, early Etherpad), requires a central server to
     order operations, why OT is harder to implement correctly than CRDTs, why the
     field has largely moved to CRDTs for decentralized use cases.
   - **Practical limits of CRDTs for markdown:** CRDTs guarantee convergence but not
     semantic correctness — concurrent edits to YAML frontmatter could produce valid
     YAML that violates schema invariants. Understanding this clarifies that CRDTs
     solve the merge problem but not the validation problem.
   - **Architectural relevance:** informs the multi-agent concurrent write design,
     clarifies what the version token system can and cannot handle, and provides the
     conceptual foundation for the protected-tier governance (some writes genuinely
     need serialization, not just merge-ability).

---

### Phase 5 — Provenance, trust, and temporal data modeling · ☑ 2/2 complete

**Why fifth:** The system's most distinctive architectural feature is its trust and
provenance model. Understanding how the research community and industry have formally
modeled provenance — and how temporal databases handle time-varying facts — will
enrich this model and expose gaps the current design doesn't address.

10. ☑ `provenance-and-trust-models.md`

    - **W3C PROV-O:** the W3C provenance ontology, the three core concepts (Entity,
      Activity, Agent), the seven provenance relations (`wasGeneratedBy`,
      `wasDerivedFrom`, `wasAttributedTo`, `wasAssociatedWith`, `used`,
      `actedOnBehalfOf`, `wasInformedBy`). How the system's frontmatter fields
      (`source`, `origin_session`, `trust`) map (partially) onto PROV-O concepts —
      and what PROV-O would add (Activities as first-class objects, delegation chains).
    - **SLSA (Supply Chain Levels for Software Artifacts):** a framework for reasoning
      about how much to trust an artifact based on the integrity of its build process.
      SLSA levels 1–4 as an analogy for the system's trust levels: the question is not
      just "what is this?" but "how was it produced and how verifiable is that?". The
      gap the current system has: no distinction between "agent-generated by a
      model running with write access to the repo" vs. "agent-generated by a verified
      pipeline with reproducible inputs."
    - **Information flow control (Biba model):** the Biba integrity model as a formal
      treatment of trust-weighted reads: a subject at integrity level X should not
      read data at level < X to avoid contaminating high-integrity work with
      low-integrity inputs. Contrasts with Bell-LaPadula (confidentiality model).
      How the system's "trust: low — inform only, never instruct" rule is an
      informal application of Biba integrity.
    - **Bayesian trust models in P2P systems:** EigenTrust, subjective logic,
      trust propagation along chains of recommendations. The question this raises for
      the system: if `chats/2026/03/18/chat-003/` was a session where the agent
      produced unreliable knowledge, should files with `origin_session:
      chats/2026/03/18/chat-003` have their trust automatically downgraded?
    - **Architectural relevance:** the trust/provenance model is currently ad hoc.
      PROV-O and SLSA provide formal vocabulary for refining it; Biba provides
      theoretical backing for the instruction-containment rule.

11. ☑ `temporal-data-modeling.md`

    - **Bi-temporal modeling:** the two independent time axes in temporal databases —
      valid time (when a fact was true in the world) and transaction time (when the
      fact was recorded in the database). A knowledge file has both: `created`
      (transaction time of first write) and `last_verified` (valid time of most
      recent confirmation). The system currently conflates these.
    - **Temporal tables in SQL (ISO SQL:2011):** `PERIOD FOR SYSTEM_TIME`,
      `AS OF SYSTEM TIME` queries, `PERIOD FOR APPLICATION_TIME`, how Postgres 16+
      and MariaDB implement temporal tables. Relevance: if the derived-state SQLite DB
      ever models knowledge items, temporal tables enable point-in-time queries
      without custom logic.
    - **Event sourcing as implicit temporal modeling:** the event log is an audit trail
      that answers "what did we know at time T?" without needing a dedicated temporal
      table. How the git log + ACCESS.jsonl combination already provides this — and
      what's missing (the ability to query "all files that were trust: high on
      2025-01-01" without replaying every commit).
    - **Slowly Changing Dimensions (SCD) in data warehouses:** Type 1 (overwrite),
      Type 2 (new row with date range), Type 3 (add a prior-value column). How the
      system's `last_verified` field is an implicit SCD Type 1 — it overwrites the
      previous verification date with no history. Type 2 would record the full
      verification history. The trade-off: history fidelity vs. file complexity.
    - **Decay functions for trust:** how recommendation systems model time-based
      decay (exponential decay, step functions, recency-weighted scoring), the
      hyperparameter choices, and how the system's current fixed-threshold decay
      (120 days for low-trust retirement) compares to a continuous decay function.
    - **Architectural relevance:** the trust decay system, `last_verified` semantics,
      and the freshness detection in `worktree-integration.md` Phase 2 all benefit
      from a cleaner temporal model. This research grounds those improvements
      theoretically.

---

### Phase 6 — Schema evolution and contract versioning · ☑ 2/2 complete

**Why sixth:** The production readiness roadmap identifies schema versioning as a
required deliverable before the system can be safely adopted. Understanding how
established schema evolution systems work — what guarantees they make and what
migration patterns they enforce — directly informs Phase 2 of the production roadmap.

12. ☑ `schema-evolution-strategies.md`

    - **Protocol Buffers compatibility rules:** field numbers as the stability
      contract (never reuse), backward-compatible changes (add optional fields, add
      enum values), forward-compatible changes (old readers ignore unknown fields),
      breaking changes (remove required fields, change field types, reuse numbers).
      The field-number system is a concrete, exportable pattern for any schema that
      needs stable identifiers.
    - **Avro schema evolution and the schema registry:** Confluent Schema Registry
      as a versioned store for Avro schemas, the compatibility modes (BACKWARD,
      FORWARD, FULL, NONE), how the registry enforces that a new schema is compatible
      with the previous N schemas before it can be registered. Relevance: the system
      could adopt a lightweight schema registry for frontmatter versions — a TOML or
      JSON file tracking schema versions and their compatibility history.
    - **JSON Schema and OpenAPI evolution:** the lack of built-in compatibility
      enforcement in JSON Schema (contrast with Avro), how the API ecosystem uses
      semantic versioning + changelog discipline instead of formal compatibility
      checking. The `nullable` vs. `required` evolution problem. Relevance: the MCP
      tool payloads are JSON and currently unversioned.
    - **Expand/contract pattern (parallel-change):** the safest migration pattern for
      live systems — (1) expand: add the new field/endpoint while keeping the old,
      (2) migrate: transition all consumers to the new, (3) contract: remove the old.
      Each phase is independently deployable. This is the correct pattern for
      evolving the frontmatter schema without breaking existing files.
    - **Architectural relevance:** directly required for Phase 2 of
      `production-readiness-roadmap.md` (version the contracts). The expand/contract
      pattern gives a concrete migration strategy for every frontmatter schema change.

13. ☑ `content-addressable-storage-and-integrity.md`

    - **Content-addressable storage (CAS) fundamentals:** the invariant (same content
      → same address, different content → different address), SHA-based addressing
      vs. UUID-based addressing, deduplication as a free side-effect, immutability as
      a design constraint (you can't modify a CAS object; you create a new one).
    - **Git as a CAS:** how git's object store is a pure CAS — blobs, trees, commits,
      and tags are all content-addressed. The `git cat-file -t <sha>` and
      `git cat-file -p <sha>` plumbing interface as the CAS read API.
    - **Merkle trees and Merkle DAGs:** the Merkle tree as the standard integrity
      structure for CAS systems — each node's hash includes its children's hashes,
      so any tamper at any level changes the root hash. How git's commit chain is a
      Merkle DAG (the tree object hash is included in the commit hash, which is
      included in child commit hashes). How to use this for integrity verification:
      `git fsck`.
    - **Nix/NixOS store:** the `/nix/store/<hash>-<name>/` content-addressed package
      store, reproducible builds (same inputs → same hash → bit-for-bit identical
      output), the `nix-store --verify` integrity check. The nix approach to schema
      evolution: pin a specific closure hash, then upgrade to a new closure
      explicitly.
    - **Implications for the memory system:** the current frontmatter `origin_session`
      field is a weak provenance link (a path, not a content hash). Replacing or
      augmenting it with a commit SHA (which is a content address in the git CAS)
      would make provenance cryptographically verifiable — "this file was produced
      in the session recorded at commit `abc123`" is unforgeable in a way that a
      path is not.
    - **Architectural relevance:** informs the integrity checklist, the
      `memory_validate` tool design, and the provenance model enrichment suggested
      by the PROV-O research.

---

## Output folder structure

All files go to `knowledge/_unverified/systems-architecture/`:

```
knowledge/_unverified/systems-architecture/
  SUMMARY.md
  git-object-model.md
  git-worktrees-and-hooks.md
  git-plumbing-and-automation.md
  filesystem-atomicity-and-locking.md
  filesystems-for-developers.md
  write-ahead-logging-and-wal-design.md
  append-only-logs-and-compaction.md
  concurrency-models-for-local-state.md
  crdts-and-collaborative-text.md
  provenance-and-trust-models.md
  temporal-data-modeling.md
  schema-evolution-strategies.md
  content-addressable-storage-and-integrity.md
```

13 files. All land in `_unverified/` with `trust: low, source: external-research`
until reviewed.

---

## Connection map to open architectural issues

| Research file | Open issue it addresses |
|---|---|
| `git-object-model.md` | Index lock incident; MCP `git_repo.py` robustness |
| `git-worktrees-and-hooks.md` | `worktree-integration.md` Phases 0–1; hook-based governance |
| `git-plumbing-and-automation.md` | Index-bypass commit path; locked-filesystem resilience |
| `filesystem-atomicity-and-locking.md` | Index lock root cause; rename-based safe writes |
| `filesystems-for-developers.md` | FUSE/network-mount graceful degradation; inotify freshness detection |
| `write-ahead-logging-and-wal-design.md` | Multi-file write atomicity gap; SQLite derived-state store |
| `append-only-logs-and-compaction.md` | ACCESS.jsonl aggregation trigger; archive rotation policy |
| `concurrency-models-for-local-state.md` | Version token design; actor model for MCP server |
| `crdts-and-collaborative-text.md` | Multi-agent concurrent writes; merge semantics for SUMMARY.md |
| `provenance-and-trust-models.md` | Trust model formalization; instruction-containment rule grounding |
| `temporal-data-modeling.md` | Trust decay; `last_verified` semantics; freshness detection |
| `schema-evolution-strategies.md` | `production-readiness-roadmap.md` Phase 2; frontmatter migration |
| `content-addressable-storage-and-integrity.md` | Integrity checker; provenance enrichment with commit SHAs |

---

## Notes

- Phase 1 (Git internals) is the highest-leverage starting point — it directly
  unblocks the worktree integration plan and closes the index-lock knowledge gap.
- Phases 1–2 can be researched from primary sources (git's own documentation, POSIX
  spec, kernel docs). Phases 3–6 draw more heavily on academic papers and system
  design literature.
- Each file should follow the standard `trust: low, source: external-research`
  frontmatter and include a "Relevance to agent-memory-seed" section making the
  connection to this system explicit. That section is what earns promotion to
  `trust: medium` on review.
- File count: 13 files. Add a `SUMMARY.md` for the new folder before or with the
  first file.

---

## Progress log

| Date | Action |
|---|---|
| 2026-03-19 | Plan created following discussion of git/filesystem/distributed-systems research areas relevant to memory system architecture |
| 2026-03-19 | Completed git-object-model.md (systems-architecture-research 1/13) || 2026-03-19 | Completed git-worktrees-and-hooks.md (systems-architecture-research 2/13) || 2026-03-19 | Completed git-plumbing-and-automation.md (systems-architecture-research 3/13) || 2026-03-19 | Completed filesystem-atomicity-and-locking.md (systems-architecture-research 4/13) || 2026-03-19 | Completed filesystems-for-developers.md (systems-architecture-research 5/13) |
| 2026-03-19 | Completed write-ahead-logging-and-wal-design.md (systems-architecture-research 6/13) || 2026-03-19 | Completed append-only-logs-and-compaction.md (systems-architecture-research 7/13) || 2026-03-19 | Completed concurrency-models-for-local-state.md (systems-architecture-research 8/13) || 2026-03-19 | Completed crdts-and-collaborative-text.md (systems-architecture-research 9/13) |
| 2026-03-19 | Completed provenance-and-trust-models.md (systems-architecture-research 10/13) || 2026-03-19 | Completed temporal-data-modeling.md (systems-architecture-research 11/13) || 2026-03-19 | Completed schema-evolution-strategies.md (systems-architecture-research 12/13) || 2026-03-19 | Completed content-addressable-storage-and-integrity.md (systems-architecture-research 13/13) |