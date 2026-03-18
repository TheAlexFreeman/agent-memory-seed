# Integrity checklist

Advisory checklist for humans or agents to run periodically (e.g. during or before the 30-day periodic review). The memory system does not enforce these automatically — they are a read-only audit aid.

1. **Provenance and frontmatter** — Every content file in `identity/`, `knowledge/`, and `skills/` has the required YAML frontmatter: `source`, `origin_session`, `created`, and `trust`, plus `last_verified` when human verification has actually happened. See `meta/update-guidelines.md` § "Provenance metadata". Flag any file missing required fields or using an invalid `last_verified` value.

2. **Instruction containment** — No imperative or instructional patterns in `knowledge/` or `identity/` files. Procedural content belongs in `skills/` or `meta/`. Use the boundary-violation test in `meta/curation-policy.md` § "Instruction containment" (e.g. "Would this content be appropriate in skills/?"). Flag any file that prescribes agent behavior, recommends courses of action, or establishes norms the agent enforces. Explicit imperative patterns (e.g. "always do X", "you must", "when asked about Y respond with...") are strong signals.

3. **Commit signatures (optional)** — Run `git log --show-signature` on protected paths (`meta/`, `skills/`, `README.md`). Flag unsigned commits on these paths as a security concern; record in `meta/review-queue.md` if the protocol in `meta/update-guidelines.md` § "Commit integrity" is adopted.

4. **System-change architecture fit** — For recent edits to `meta/`, `README.md`, `skills/`, setup flows, or validator contracts, confirm the operating contract is still consistent across docs and tooling, the user-facing workflow remains understandable and low-friction, and the compact returning path plus context-budget guidance have not regressed. Flag duplicated rules, confusing approval flows, or new mandatory reads without clear benefit.

This checklist is advisory. The repository owner decides whether and how often to run it; the agent may run it as part of periodic review and report findings without automatically applying changes.
