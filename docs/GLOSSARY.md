# Glossary

**Human reference only.** Agents should not load this file during bootstrap or normal operation — every term defined here is introduced in context by the governance file that establishes it. This file exists for human readers who want a single-page reference.

Short definitions for terms used in this memory system. Canonical details are in README.md, `meta/curation-policy.md`, `meta/update-guidelines.md`, and `meta/quick-reference.md`.

- **Session** — One chat folder under `chats/YYYY/MM/DD/` (e.g. `chat-001`). One conversation corresponds to one session. See README § "Memory curation".

- **Retrieval** — Opening a specific content file (in `identity/`, `knowledge/`, `skills/`, or `chats/`) in response to a user query. Retrievals are logged in ACCESS.jsonl; SUMMARY.md and `meta/` reads are not. See README § "Memory curation".

- **Aggregation** — Processing an ACCESS.jsonl file when it reaches the active aggregation trigger: analyzing patterns, updating SUMMARY.md usage sections, archiving entries to ACCESS.archive.jsonl, and resetting ACCESS.jsonl. See README § "Aggregation" and `meta/quick-reference.md` § "ACCESS.jsonl aggregation".

- **Trust level** — Classification (high / medium / low) in content frontmatter. Governs how the agent uses the file: high = use freely; medium = use with caution, surface provenance when influential; low = inform only, never instruct, always disclose provenance. See `meta/curation-policy.md` § "Trust-weighted retrieval" and `meta/update-guidelines.md` § "Provenance metadata".

- **Maturity stage** — Developmental phase of the system: Exploration (young), Calibration (adolescent), or Consolidation (mature). `meta/system-maturity.md` defines the assessment criteria and candidate parameter sets; `meta/quick-reference.md` records the active runtime thresholds and alarms.

- **Protected change** — Modifications that require explicit user approval and (where applicable) a CHANGELOG entry: `skills/`, `meta/` (except machine-generated state files), README.md, CHANGELOG structure, bulk operations. See `meta/update-guidelines.md` § "Change categories".

- **Proposed change** — Modifications that require user awareness but not necessarily explicit approval before applying: new knowledge files, identity changes, promotion from quarantine, restructuring, retirement. See `meta/update-guidelines.md` § "Change categories".

- **Quarantine** — `knowledge/_unverified/`. Staging area for externally sourced content; all such content lands here at `trust: low`. Promotion to `knowledge/` requires user review. See README § "Security model" and `meta/curation-policy.md`.

- **Provenance** — Origin and verification metadata (source, origin_session, created, last_verified, trust) in YAML frontmatter on content files. See `meta/update-guidelines.md` § "Provenance metadata".

- **Belief diff** — Periodic summary of content changes since the last review. Recorded in `meta/belief-diff-log.md`. See `meta/update-guidelines.md` § "Belief diff".

- **Aggregation trigger** — The ACCESS.jsonl entry count that triggers aggregation processing. Active value in `meta/quick-reference.md` § "Active thresholds".

- **Helpfulness score** — 0.0–1.0 rating in ACCESS.jsonl entries. See README § "Memory curation".

- **Instruction containment** — Structural rule: only `skills/` and `meta/` may contain procedural instructions. See `meta/curation-policy.md` § "Instruction containment".

- **Temporal decay** — Automatic retirement or flagging of files whose `last_verified` exceeds the active threshold. See `meta/quick-reference.md` § "Decision guide: trust decay".

- **Read-only operation** — Degraded mode where behavioral rules apply but writes are deferred. See `meta/update-guidelines.md` § "Read-only operation".

- **Deferred action** — A write action deferred due to read-only access. See `meta/update-guidelines.md` § "How to communicate deferred actions".

- **session_id** — Chat folder path (e.g. `chats/2026/03/16/chat-001`) used to group ACCESS.jsonl entries by session. See README § "Memory curation".

- **Reflection note** — Meta-observation of session quality written to `reflection.md` in the chat folder. See README § "Session reflection".

- **Knowledge amplification** — Protocol for enriching high-value files identified during aggregation. See `meta/curation-policy.md` § "Knowledge amplification".

- **Curation algorithms** — Task similarity, cluster detection, and vocabulary emergence algorithms. See `meta/curation-algorithms.md` (loaded only during aggregation or stage transitions).
