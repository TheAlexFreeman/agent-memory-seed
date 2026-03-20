---
created: 2026-03-20
origin_session: chats/2026/03/20/cowork-enrichment
source: agent-generated
trust: medium
---

# File Format Research for Engram

Research into the utility of different file formats (`.md`, `.json`, `.yml`,
`.toml`, etc.) for a persistent AI memory system like Engram, and whether the
current Markdown-with-YAML-frontmatter approach is optimal or should be
reconsidered.

---

## Current Engram approach

Engram uses **Markdown with YAML frontmatter** for all content files, **JSONL**
for access logs, and **TOML** for machine-readable configuration
(`agent-bootstrap.toml`). This was a deliberate design choice favoring
human-readability, git-friendliness, and auditability.

---

## Format-by-format analysis

### Markdown (`.md`)

**Token efficiency:** Most token-efficient format for prose content. Benchmarks
show 34–38% fewer tokens than JSON and ~10% fewer than YAML for equivalent
content. One benchmark: 38,357 tokens (Markdown) vs. 57,933 (JSON) vs. 42,477
(YAML) for the same dataset on GPT-5 Nano.

**LLM accuracy:** Mixed. YAML outperformed Markdown on structured data extraction
tasks for GPT-5 Nano (62.1% vs. 54.3%) and Gemini 2.5 Flash Lite (51.9% vs.
48.2%). Llama 3.2 showed minimal format sensitivity. Markdown's accuracy
advantage is for *prose comprehension*, not structured field extraction.

**Strengths for Engram:**
- Human-readable and editable in any text editor
- Git diffs are clean and meaningful
- LLMs are heavily trained on Markdown — it's the native prose format
- Zero-friction human-in-the-loop editing
- No parsing library required — the LLM reads it natively

**Weaknesses for Engram:**
- Poor for structured/tabular data (markdown tables are *more* expensive
  than JSON — 40% overhead from pipe/dash formatting)
- No native schema validation — frontmatter correctness depends on the
  validator, not the format itself
- Querying requires full-text search or the LLM reading the file; no
  native field-level indexing
- Scales poorly beyond ~5MB total memory footprint without external indexing

**Verdict:** Correct choice for knowledge files, chat summaries, identity,
plans — anything that is primarily prose with metadata. Engram's content is
overwhelmingly this type.

---

### JSON (`.json`)

**Token efficiency:** Worst of the common formats for LLM context. Repeated
keys, quotes on every string, curly braces and commas add 34–38% overhead
vs. Markdown, 20–30% vs. YAML. The overhead is worst for arrays of objects
(repeated key names on every entry).

**LLM accuracy:** Middling. JSON performed well on Llama 3.2 (52.7%, best
format for that model) but poorly on GPT-5 Nano (50.3%) and Gemini Flash Lite
(43.1%). Models are trained on JSON heavily, but the syntactic noise seems to
hurt more than the familiarity helps.

**Strengths:**
- Universal machine interoperability — every language parses it natively
- Schema validation via JSON Schema
- Precise, unambiguous structure — no whitespace sensitivity
- Best format for tool/API communication (MCP already uses JSON)

**Weaknesses:**
- Worst token efficiency of common formats
- Not human-friendly for long-form content
- Git diffs are noisy (reordering keys, trailing commas, etc.)
- No native comments — metadata must be inline

**Where it fits in Engram:** Tool communication (MCP protocol), structured
API responses, and machine-readable artifacts that don't need to live in
context long. *Not* a good replacement for knowledge or identity files.

---

### YAML (`.yml` / `.yaml`)

**Token efficiency:** ~20–30% more efficient than JSON, ~10% less efficient
than Markdown. Saves 1,000–2,000 tokens per 100 items vs. JSON.

**LLM accuracy:** Best performer for structured data on two of three models
tested (GPT-5 Nano: 62.1%, Gemini Flash Lite: 51.9%). The indentation-based
structure seems to map well to how LLMs parse hierarchical information.

**Strengths:**
- Clean representation of nested/hierarchical data
- Human-readable (more so than JSON, less so than Markdown)
- Supports comments (unlike JSON)
- Mature ecosystem (validators, linters, schema tools)

**Weaknesses:**
- Whitespace sensitivity creates subtle bugs (the Norway problem: `NO`
  parses as boolean `false`)
- Type coercion surprises are well-documented and dangerous
- Deserialization vulnerabilities in some parsers (arbitrary code execution)
- More verbose than Markdown for prose; more verbose than JSON for deeply
  nested structures past 3–4 levels

**Where it fits in Engram:** Already used correctly — as *frontmatter inside
Markdown files*, not as a standalone content format. YAML frontmatter gives
Engram the structured metadata benefits (source, trust, dates, tags) without
the prose overhead. Full YAML files would make sense for structured data that
isn't primarily prose — e.g., a machine-readable taxonomy, a schema definition,
or a configuration manifest.

**Potential opportunity:** Some Engram files that are currently prose-heavy
but structurally repetitive — like `plans/SUMMARY.md` with its repeated
`Scope / Progress / Next / Blocks` blocks — might be more token-efficient
and more accurately parsed as YAML. But the tradeoff is that the compact
bootstrap path reads these files raw into context, and Markdown is the
format LLMs handle most naturally for mixed prose+structure.

---

### TOML (`.toml`)

**Token efficiency:** Similar to YAML for flat/shallow structures. Becomes
verbose for deeply nested data (repeated section headers vs. YAML's
indentation).

**Strengths:**
- Unambiguous — maps directly to a hash table, no type coercion surprises
- No deserialization vulnerabilities (the spec prohibits arbitrary objects)
- Native datetime support
- Python ecosystem standard (`pyproject.toml`)
- Explicit section headers make structure visible regardless of whitespace

**Weaknesses:**
- Awkward beyond 2–3 levels of nesting
- Not widely used in LLM training data — models handle it less fluently
- No support for complex data structures (no anchors/aliases like YAML)
- Smaller ecosystem for schema validation

**Where it fits in Engram:** Already used correctly — `agent-bootstrap.toml`
is a configuration manifest, which is TOML's sweet spot. TOML is not a
content format and should not be used for knowledge, identity, or chat files.
Could potentially be used for more machine-readable manifests (e.g., a
structured capability declaration, a taxonomy definition).

---

### JSONL (`.jsonl`)

**Token efficiency:** Same per-entry cost as JSON, but append-only structure
avoids the overhead of maintaining a complete JSON array.

**Strengths:**
- Append-only by design — ideal for logs and event streams
- Each line is independently parseable — no need to load the full file
- Grep-friendly
- Natural fit for deterministic recovery (replay the log)

**Weaknesses:**
- Not human-friendly for reading (each line is a full JSON object)
- No schema enforcement without external tooling
- Querying requires scanning the full file or external indexing

**Where it fits in Engram:** Already used correctly — `ACCESS.jsonl` is an
append-only access log, which is exactly what JSONL is designed for.
The aggregation-and-archive cycle prevents unbounded growth.

---

### TOON (Token-Oriented Object Notation)

A new format (launched November 2025) designed specifically for LLM token
efficiency. Uses a tabular layout for arrays of objects, eliminating repeated
keys.

**Token efficiency:** 30–60% fewer tokens than JSON for large uniform arrays.
Benchmark: 2,744 tokens (TOON) vs. 4,545 tokens (JSON) for the same data.
99.4% accuracy on GPT-5 Nano with 46% fewer tokens.

**Strengths:**
- Specifically designed for LLM consumption
- Lossless round-trip to/from JSON
- Schema-aware (declares array length and field names once)
- Implementations in TypeScript, Python, Go, Rust, .NET

**Weaknesses:**
- Very new — limited adoption and training data exposure
- Optimizes for *tabular* data, not prose or hierarchical content
- Not human-readable in the way Markdown is
- Community is small; spec is still evolving

**Where it might fit in Engram:** The ACCESS log is the best candidate —
it's a uniform array of objects with repeated fields (file, date, task,
helpfulness, note, session_id). Converting ACCESS.jsonl to TOON could save
significant tokens if the log is ever loaded into context. However, the
current design loads ACCESS entries only during aggregation, so the token
savings would be marginal in practice. Worth watching, not worth adopting yet.

---

### MIF (Memory Interchange Format)

An open specification (February 2026) for AI memory portability. Uses a
dual-format approach: `.memory.md` (Markdown with YAML frontmatter) and
`.memory.json` (JSON-LD).

**Key features:**
- Three cognitive memory types: semantic, episodic, procedural
- W3C PROV-O compatible provenance tracking
- Bi-temporal tracking (when recorded vs. when true)
- Entity relationships that create knowledge graphs
- Confidence scores on a 0.0–1.0 scale
- Namespace federation for multi-agent scenarios
- Lossless conversion between Markdown and JSON-LD representations

**Relevance to Engram:** MIF is solving many of the same problems Engram
solves — provenance, trust, temporal tracking, memory classification — but
with a different approach:

| Dimension | Engram | MIF |
|---|---|---|
| Provenance | YAML frontmatter (source, trust, origin_session) | W3C PROV-O compatible |
| Temporal | created + last_verified | Bi-temporal (record time + valid time) |
| Classification | Folder structure (identity/, knowledge/, skills/) | Cognitive types (semantic, episodic, procedural) |
| Relationships | Cross-references via relative links | Formal entity-relationship graph |
| Validation | Custom pytest validator | JSON Schema |
| Portability | Git clone | Dual-format with lossless conversion |
| Human editing | Native (just edit the .md) | Native for .memory.md, not for .memory.json |

**Assessment:** MIF's dual-format approach is elegant but adds complexity
that Engram doesn't currently need. The W3C PROV-O provenance and bi-temporal
tracking are genuinely more rigorous than Engram's current frontmatter scheme.
The entity-relationship graph would address one of Engram's blind spots (no
formal representation of how knowledge files relate to each other beyond
cross-references). Worth studying as a reference design, not worth adopting
wholesale — Engram's simpler approach is appropriate for its current
single-user, git-backed architecture.

---

### Semantic graphs (Neo4j, AIngle, Mem0 knowledge graphs)

Not a file format per se, but a competing architecture. The key argument:
"vectors find similar text, but graphs preserve how facts connect across
sessions."

**Strengths:**
- Relational reasoning (A relates to B, which relates to C)
- Cryptographic verification of claim provenance (AIngle)
- Efficient complex queries ("all users who completed KYC AND were flagged")
- Automatic entity extraction and relationship mapping

**Weaknesses:**
- Opaque — you can't open a graph database in a text editor
- Not git-friendly — no meaningful diffs or version history
- Requires infrastructure (database server, query language)
- Vendor lock-in risk
- The claimed advantage — relational reasoning — is something LLMs do
  naturally when the relevant context is loaded

**Assessment for Engram:** The transparency and auditability arguments that
motivated Engram's Markdown-first design are directly opposed to graph
databases. A semantic graph would give Engram better relational querying
but would sacrifice the core design bet: that human-readable, git-versioned
files are worth the tradeoff. This is a values question, not a technical one.

The hybrid approach (Mem0-style: Markdown files + a derived graph index) is
worth considering as Engram scales — the Markdown files remain the source of
truth, but a graph index provides faster relational queries for the MCP
server without changing the storage layer.

---

## Synthesis: what should change?

### What Engram gets right

The current format choices are well-matched to the system's values and
scale:

1. **Markdown for content** — correct. Token-efficient, human-readable,
   git-friendly, LLM-native. The alternative formats are either less
   readable (JSON, YAML, TOON) or less structured (plain text).

2. **YAML frontmatter for metadata** — correct. Gives structured fields
   without leaving the Markdown ecosystem. YAML's accuracy advantage
   for structured data applies exactly where Engram uses it (metadata
   extraction), while the prose body benefits from Markdown's efficiency.

3. **JSONL for access logs** — correct. Append-only, grep-friendly,
   independently parseable lines.

4. **TOML for configuration** — correct. Unambiguous, safe to parse,
   Python-ecosystem standard.

### What could potentially be improved

1. **Structured data within Markdown files.** Some files contain
   structured/tabular data (plans/SUMMARY.md plan blocks, the thresholds
   table in quick-reference.md, knowledge SUMMARY file indexes) where
   YAML or even a compact notation would be more token-efficient than
   Markdown tables. But the LLM reads these files raw — and Markdown
   tables are the format it handles most fluently for mixed content. The
   token savings (~100–200 tokens for the current tables) don't justify
   the readability cost. **No change recommended.**

2. **A derived index layer.** As the knowledge base grows, full-text
   search and SUMMARY-file navigation will become increasingly slow and
   token-expensive. A lightweight derived index — a SQLite database, a
   JSON graph, or even a structured YAML index — built from the Markdown
   files could support faster MCP queries without changing the source
   format. This is the "Mem0 hybrid" approach applied to Engram. **Worth
   planning, but not urgent at current scale (~100 files).**

3. **MIF-style provenance rigor.** Engram's frontmatter is adequate but
   could be strengthened: bi-temporal tracking (distinguishing "when the
   file was written" from "when the content was true") and formal
   entity-relationship metadata would improve curation quality. These
   could be added as optional frontmatter fields without changing the
   format. **Low-cost improvement, worth considering.**

4. **TOON for bulk data exchange.** If Engram ever needs to pass large
   structured datasets through the context window (e.g., full ACCESS logs,
   bulk plan state), TOON's 30–60% token savings over JSON would be
   significant. But this is a future concern — the current design
   minimizes bulk data in context. **Watch, don't adopt.**

### What should definitely not change

- **Do not replace Markdown with YAML or JSON for content files.** The
  prose readability, git-diff quality, and human-editing experience would
  degrade significantly. The token efficiency data confirms Markdown is
  the right choice for prose-heavy content.

- **Do not adopt a graph database as primary storage.** It would sacrifice
  the core design bet (transparency, auditability, portability) for
  querying speed that isn't yet a bottleneck.

- **Do not adopt MIF wholesale.** It solves a portability problem
  (multiple AI tools sharing memory) that Engram doesn't have. Engram is
  a single-user, single-repo system. Cherry-pick MIF's best ideas
  (bi-temporal tracking, confidence scores, cognitive type classification)
  as frontmatter enhancements instead.

---

## Sources

- [Which Nested Data Format Do LLMs Understand Best?](https://www.improvingagents.com/blog/best-nested-data-format/) — benchmark of JSON/YAML/XML/Markdown accuracy across GPT-5 Nano, Llama 3.2, Gemini 2.5 Flash Lite
- [JSON vs. YAML vs. Markdown: The Token Benchmarks](https://shshell.com/blog/token-efficiency-module-13-lesson-2-format-comparison) — token cost comparison
- [AI Agent Memory Management - When Markdown Files Are All You Need?](https://dev.to/imaginex/ai-agent-memory-management-when-markdown-files-are-all-you-need-5ekk) — case for file-based memory
- [I replaced my agents markdown memory with a semantic graph](https://dev.to/eahm60/i-replaced-my-agents-markdown-memory-with-a-semantic-graph-1elp) — case for graph-based memory
- [Introducing MIF: Memory Interchange Format](https://zircote.com/blog/2026/02/introducing-mif-memory-interchange-format/) — open specification for AI memory portability
- [TOON vs JSON: Why AI Agents Need Token-Optimized Data Formats](https://jduncan.io/blog/2025-11-11-toon-vs-json-agent-optimized-data/) — TOON specification and benchmarks
- [Markdown is 15% more token efficient than JSON](https://community.openai.com/t/markdown-is-15-more-token-efficient-than-json/841742) — OpenAI community analysis
- [TOON: Token-Oriented Object Notation (GitHub)](https://github.com/toon-format/toon) — spec and SDK
- [MIF GitHub repository](https://github.com/zircote/MIF) — specification and reference implementation
- [Graph Memory for AI Agents (Mem0)](https://mem0.ai/blog/graph-memory-solutions-ai-agents) — hybrid vector+graph approach
