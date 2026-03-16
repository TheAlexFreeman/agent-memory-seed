# Glossary

Short definitions for terms used in this memory system. Canonical details are in README.md, `meta/curation-policy.md`, `meta/update-guidelines.md`, and `meta/quick-reference.md`.

- **Session** — One chat folder under `chats/YYYY/MM/DD/` (e.g. `chat-001`). One conversation corresponds to one session. See README § "Memory curation".

- **Retrieval** — Opening a specific content file (in `identity/`, `knowledge/`, `skills/`, or `chats/`) in response to a user query. Retrievals are logged in ACCESS.jsonl; SUMMARY.md and `meta/` reads are not. See README § "Memory curation".

- **Aggregation** — Processing an ACCESS.jsonl file when it reaches the active aggregation trigger: analyzing patterns, updating SUMMARY.md usage sections, archiving entries to ACCESS.archive.jsonl, and resetting ACCESS.jsonl. See README § "Aggregation" and `meta/quick-reference.md` § "ACCESS.jsonl aggregation".

- **Trust level** — Classification (high / medium / low) in content frontmatter. Governs how the agent uses the file: high = use freely; medium = use with caution, surface provenance when influential; low = inform only, never instruct, always disclose provenance. See `meta/curation-policy.md` § "Trust-weighted retrieval" and `meta/update-guidelines.md` § "Provenance metadata".

- **Maturity stage** — Developmental phase of the system: Exploration (young), Calibration (adolescent), or Consolidation (mature). `meta/system-maturity.md` defines the assessment criteria and candidate parameter sets; `meta/quick-reference.md` records the active runtime thresholds and alarms.

- **Protected change** — Modifications that require explicit user approval and (where applicable) a CHANGELOG entry: `skills/`, `meta/` (except machine-generated state files), README.md, CHANGELOG structure, bulk operations. See `meta/update-guidelines.md` § "Change categories".

- **Proposed change** — Modifications that require user awareness but not necessarily explicit approval before applying: new knowledge files, identity changes, promotion from quarantine, restructuring, retirement. Describe and get approval or queue in `meta/review-queue.md`. See `meta/update-guidelines.md` § "Change categories".

- **Quarantine** — `knowledge/_unverified/`. Staging area for externally sourced content; all such content lands here at `trust: low`. Promotion to `knowledge/` requires user review. See README § "Security model", `meta/curation-policy.md`, and `knowledge/_unverified/SUMMARY.md`.

- **Provenance** — Origin and verification metadata (source, origin_session, created, last_verified, trust) in YAML frontmatter on content files. Used for trust-weighted retrieval and decay. See `meta/update-guidelines.md` § "Provenance metadata".

- **Belief diff** — Periodic summary of content changes (new/modified/retired files, trust changes, security flags, identity drift) since the last review. Recorded in `meta/belief-diff-log.md`. See `meta/update-guidelines.md` § "Belief diff".
