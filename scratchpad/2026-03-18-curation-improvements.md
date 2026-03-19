# Curation Process Improvements — Research Notes
*2026-03-18 — drafted after completing 11-file ai-history genealogy corpus*

These notes explore ways to make the knowledge base curation pipeline more discoverable, more automated, and more robust — particularly for multi-file research corpora like the ai-history project.

---

## 1. The core bottleneck: user review is the only gate

Currently, the path from `_unverified/` to `knowledge/` requires a single human action: Alex reads the file and explicitly affirms it. This is correct for factual accuracy, but it bundles two very different jobs together:

- **Security review** — Does the file contain prompt injection, memory injection, authority spoofing, or other adversarial content?
- **Accuracy review** — Are the facts, interpretations, and attributions correct?

These have different reviewers and different costs. Security review can in principle be done by an agent (pattern-matching against known injection signatures); accuracy review genuinely requires a domain-competent human. Conflating them means Alex has to do everything, which creates a bottleneck that causes `low`-trust files to age out unreviewed.

---

## 2. Proposed: Agent-assisted security pre-clearance

**Idea:** Before a file is eligible for user accuracy review, an agent scans it for adversarial patterns and either clears it (→ `trust: medium`) or flags it (→ security entry in `review-queue.md`).

**What the scan would check:**

- Imperative override patterns: "always do X," "ignore previous instructions," "from now on," "as your system prompt says"
- Authority spoofing: content claiming to originate from `meta/`, `skills/`, or system-level context
- Identity injection: assertions about Alex's preferences, beliefs, or behavior that weren't established in the origin session and can't be sourced
- Behavior-altering instructions embedded in prose (e.g., a "knowledge file" that contains a skill procedure disguised as narrative)
- Internal contradictions with `identity/` or high-trust `knowledge/` files on factual claims about the user
- Extraordinary provenance claims ("Alex told me personally that…" in an `external-research` file)

**Outcome states:**

| Scan result | Action |
|---|---|
| Clean | Set `trust: medium`, add `security_reviewed: [date]` to frontmatter, file stays in `_unverified/` awaiting user accuracy review |
| Suspicious | Create `security` entry in `review-queue.md`, do not promote, flag to user immediately |
| Ambiguous | Add `## ⚠ Security notes` section to file listing the specific concerns, set status to `flagged`, present to user |

**Implementation path:** Could be a dedicated skill (`skills/security-review.md`) invoked by the agent during periodic review or on-demand. The skill would read a file, run the checklist, and output either a clearance record or a flag. Low implementation cost; high value for unblocking the promotion pipeline.

**Governance change required:** Adding `security_reviewed` as an optional frontmatter field, and formally splitting the promotion path into two stages, would require a protected change to `meta/update-guidelines.md`.

---

## 3. Research corpus discoverability

### Problem
The current system finds files by keyword search or folder browsing. For a 11-file interconnected corpus, neither is great: search returns individual files without context about how they relate; folder browsing shows a list with no reading order or thematic map.

### Improvement A: Richer SUMMARY.md as reading guide

Current SUMMARY.md pattern: table of files + one-line description. Proposed addition for research corpora:

```markdown
## Research questions answered
- [List the questions this corpus was written to address]

## Recommended entry points
- For a quick orientation: [file A]
- For the technical core: [file B, file C]
- For synthesis: [file D]

## Through-lines (themes across files)
- [Theme 1]: appears in [file A, B, C]
- [Theme 2]: appears in [file D, E]
```

The ai-history SUMMARY.md already partially does this (it has a "four through-lines" section). Making this a formal template would ensure it's done for future corpora.

### Improvement B: Frontmatter tags

Add an optional `tags:` field to knowledge file frontmatter:

```yaml
tags: [transformers, attention, language-models, nlp]
```

`memory_search` can already grep frontmatter. Tags would allow cross-folder retrieval ("show me everything tagged `transformers`") without requiring a manually maintained cross-reference index.

Cost: low (additive to existing schema, no governance change needed for optional field). Value: high for cross-domain retrieval as the knowledge base grows.

### Improvement C: Knowledge index

A `knowledge/INDEX.md` (or `knowledge/_unverified/INDEX.md`) that serves as a human-readable topic map — not a flat list of files, but a clustered view organized by problem domain. Updated during periodic review. Format:

```markdown
## AI Systems & History
- `ai-history/` — full genealogy corpus (11 files, trust: low, pending review)
  - Key question: how did the current paradigm form?

## Philosophy & Cognition
- `philosophy/narrative-cognition.md` — Bruner, Ricoeur, force dynamics, DMN
- `philosophy/free-energy-autopoiesis-cybernetics.md` — Friston, Maturana, Ashby
  ...
```

This is especially valuable for returning sessions: instead of relying on the compact manifest to surface files, Alex or the agent can scan the index to identify relevant clusters before doing targeted reads.

---

## 4. Aging-out warnings

Currently there's no proactive signal when `_unverified` files are approaching the 120-day auto-archive threshold. A file written today will silently disappear in July unless reviewed.

**Proposal:** During the compact returning manifest load, if any `_unverified` file has `created` or `last_verified` within 30 days of the active threshold, surface a one-line warning:

```
⚠ 3 files in knowledge/_unverified/ai-history/ will auto-archive by 2026-07-16 if not reviewed.
```

Implementation: add a check to the returning-session checklist in `meta/quick-reference.md`. This is a protected change to `meta/` but low-complexity.

---

## 5. Contested-claims annotation

For external-research files, the writing agent often has varying confidence across different claims within a file. Currently there's no way to signal this to the reviewing human.

**Proposal:** Optionally include a `## Verify` section at the end of research files listing specific claims the agent is less confident about — precise dates, attribution of ideas to specific people, quantitative figures, contested historiography. This gives the user a checklist for focused review rather than requiring them to re-read every sentence.

The ai-history files would benefit from this retroactively: precise claims like "11 percentage point margin at ILSVRC 2012" or "Bahdanau et al. 2014" are checkable facts where verification effort is concentrated.

---

## 6. Corpus-level metadata

For multi-file research projects, create a lightweight `CORPUS.md` alongside the folder SUMMARY:

```yaml
---
research_question: How did the current deep learning paradigm form, and what bottlenecks drove each transition?
files: 11
phases_complete: 5/5
origin_session: chats/2026/03/18/chat-NNN
status: complete | in-progress
trust_summary: all trust:low, pending review
---
```

This makes the corpus a first-class object in the knowledge system — searchable, trackable, and reportable — rather than just a folder of files.

---

## 7. Prioritization

In rough order of value-to-effort:

| Improvement | Effort | Value | Governance change? |
|---|---|---|---|
| Agent security pre-clearance | Medium (skill needed) | High (unblocks pipeline) | Yes — `update-guidelines.md` |
| Frontmatter tags | Low | High (cross-domain retrieval) | No (optional field) |
| Aging-out warnings in manifest | Low | Medium (prevents silent loss) | Yes — `quick-reference.md` |
| Richer SUMMARY.md template | Low | Medium (corpus navigation) | No (additive) |
| `## Verify` annotation convention | Low | Medium (focused review) | No (convention, not rule) |
| Knowledge INDEX.md | Medium (maintenance burden) | Medium (orientation) | No |
| Corpus-level CORPUS.md | Low | Low-medium | No |

The agent security pre-clearance is the most architecturally significant because it formally splits the two-stage nature of trust promotion that's currently implicit. Everything else is additive and can be adopted incrementally.

---

## Open questions

1. Should security pre-clearance be a dedicated MCP tool (structured output, runnable independently) or a skill (prompt-based, no new tooling)?
2. If tags are added, should there be a controlled vocabulary or freeform? Controlled vocabulary has better consistency but requires upfront design and maintenance.
3. The 120-day auto-archive threshold was set at Exploration stage. As the knowledge base matures and external-research corpora grow larger, does this threshold need recalibration? A large corpus that took significant effort to produce shouldn't silently disappear because a periodic review was missed.
4. For the ai-history corpus specifically: would a single batch review session (Alex spot-checks 2-3 files and affirms the whole corpus) be acceptable under the confirmation signal rules, or does each file need individual confirmation?
