# MCP Tooling Development Notes

Origin session: `chats/2026/03/19/chat-001`

## Scope of the work so far

This MCP effort has moved in layers rather than in a straight checklist line.

- First, the repo gained a governed MCP baseline: manifest-driven capability discovery, semantic write contracts, raw fallback boundaries, shared result envelopes, and Git-backed publication semantics.
- Second, the runtime was hardened: explicit single-writer assumptions, degraded publication fallback when the normal index path is blocked, and provenance-rich commit results.
- Third, the read surface expanded to cover governance and maintenance workflows more directly: aggregation trigger analysis, access aggregation support, periodic-review reporting, file provenance inspection, and commit inspection.
- Fourth, the semantic layer gained a protected governance write path for recording approved periodic-review outputs.

## Process observations

- The most reliable implementation pattern has been: add read-side visibility first, then add the corresponding governed write path once the shape of the operation is clear.
- The capability manifest is part of the product surface, not just repo documentation. Runtime work is incomplete until the manifest, export coverage, and capability-contract tests are aligned.
- Protected semantic tools are more expensive than ordinary write tools because they need three things to move together: repo invariants, approval semantics, and UI/result-contract metadata.
- A meaningful share of MCP work is architectural groundwork rather than checklist closure. That needs to be tracked explicitly in plans, or the plans will imply less progress than the system actually made.

## Repeated friction points

- The active MCP implementation plans were written around concrete missing tools, so adjacent platform-hardening work does not automatically show up as progress even when it clearly lowers future delivery risk.
- Manifest omissions are an easy failure mode. A tool can be implemented correctly and still fail validation because result labels, operation tables, or desktop-operation mappings were not added.
- Documentation drift is real around the MCP surface. Launch semantics, environment variables, and client examples need periodic correction because they are easy to stale while the runtime evolves.
- Branch/worktree context needs extra care. Repo metadata attached to the conversation may not match the branch currently checked out in the local working tree.

## Working heuristics worth reusing

- Treat the capability manifest as executable contract text: update it in the same slice as runtime code.
- Prefer narrow semantic tools over broad protected raw-edit exceptions.
- Land provenance and inspection tools before automation that mutates high-leverage governance files.
- When a session produces architectural progress without direct checklist completion, add a note to the relevant plan instead of forcing a misleading checkbox update.

## Likely next slices

- `memory_get_capabilities` and `memory_search` context lines remain clean cross-cutting next steps because they improve discoverability and reduce manual orchestration without opening new protected-write surfaces.
- `memory_session_health_check` remains the highest-value read-side consolidation tool.
- `memory_resolve_review_item` looks like the next natural protected semantic follow-on after `memory_record_periodic_review`.