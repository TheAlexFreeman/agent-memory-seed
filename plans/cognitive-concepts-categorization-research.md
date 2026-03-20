created: 2026-03-20
last_verified: 2026-03-20
next_action: "Human review of knowledge/cognitive-science/concepts/ files recommended"
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Concepts, Categorization, and Conceptual Change

## Goals

Knowledge files are organized into categories (philosophy, cognitive science, mathematics, etc.) and structured around concepts (Parfit's Relation R, reconsolidation, Nash equilibrium). But what *is* a concept? How does categorization work, and what are the costs of restructuring a category system? How do conceptual revolutions happen within a knowledge base over time — and how do they fail? This plan surveys the cognitive science of concepts and categorization, then extends into the study of conceptual change and knowledge organization. The result directly informs how knowledge files should be structured, how they should be organized into categories, and how the knowledge base as a whole evolves.

A secondary motivation: the knowledge base now covers enough philosophy of mind, phenomenology, and cognitive science that there is real risk of conceptual confabulation — using similar-sounding terms across frameworks without clarity about whether they cross-reference legitimately (e.g., "schema" in cognitive science vs. "horizon" in Husserl vs. "grammar" in Wittgenstein). A rigorous account of conceptual structure helps maintain conceptual hygiene across the knowledge base's interdisciplinary scope.

Primary connections to existing files:
- `knowledge/philosophy/cognitive-linguistics-metaphor-blending.md` — conceptual metaphor and blending are alternative cognitive accounts of conceptual structure
- `knowledge/philosophy/narrative-cognition.md` — narrative is one organizing framework for conceptual structure; this plan provides alternatives
- `cognitive-science/memory/tulving-episodic-semantic-distinction.md` — semantic memory IS the knowledge system; categorization is its internal structure
- `knowledge/ai/frontier-synthesis.md` — LLM concept representations are high-dimensional embeddings; this plan provides the cognitive science context for interpreting them

---

## Problem statement

The knowledge base contains files about how memory is organized (Tulving), how language structures thought (cognitive linguistics), how narrative organizes meaning (Bruner/Ricoeur). But it does not yet have a direct treatment of *conceptual structure* — the cognitive science of how concepts are represented, how they are learned, how categories are formed, and how they change. This is important for two reasons: (1) the knowledge base's organization is a set of categorization decisions, and understanding what makes categorization succeed or fail should inform those decisions; (2) understanding how concepts are structured in human cognition provides a baseline against which to compare LLM "concepts" (embedding-space representations), which is a key interpretability question.

---

## Scope decisions

**In scope:**
- Classical theory of concepts: necessary and sufficient conditions; what's wrong with it (Wittgenstein's family resemblance, Putnam's natural kinds)
- Prototype theory (Rosch): graded category membership, typicality effects, basic level categories
- Exemplar theory: concepts as stored exemplars; computational implementations
- Theory-theory / knowledge-based view: concepts embedded in intuitive theories; conceptual change as theory change
- The "conceptual spaces" framework (Gärdenfors): geometric representations of concepts; convexity constraints; how similarity is represented spatially
- Conceptual change: how concepts change through learning, discovery, and revolutionary restructuring (Carey, Kuhn)
- Basic level categories and the asymmetry of categorization: why "dog" is more natural than "animal" or "labrador"
- The embodied basis of concepts: Barsalou's perceptual symbol systems; grounded cognition vs. amodal symbols
- Cross-domain conceptual mapping: structural alignment (Gentner); why analogy works; when it misleads
- Concepts in LLMs: what are embeddings? Do LLMs have "concepts" in any of these senses? Interpretability research on concept formation in neural networks

**Out of scope:**
- Full history and philosophy of concepts (Frege, Russell, Quine) — relevant but belongs in the logic/philosophy domain  
- Full treatment of analogy and analogical reasoning (large enough for its own plan)
- Concept learning in children in developmental detail — interesting but the developmental psych plan should cover it

---

## Phases

### Phase 1 — Theories of conceptual structure

**1.1 Classical Theory and Its Failures**
- The classical view: concepts are defined by necessary and sufficient conditions; to possess a concept is to know its definition; all members of a category have the defining features; membership is all-or-nothing
- Domain of success: mathematical concepts (triangle, prime number) fit the classical theory well
- Wittgenstein's family resemblance (1953): "game" cannot be defined by necessary and sufficient conditions; games share overlapping, crisscrossing features but no single feature runs through all of them — like family resemblance (same jaw, different eyes; same eyes, different jaw)
- Putnam's natural kind argument: "water" is H₂O, but many things that look like water are not; the reference of natural kind terms is fixed by the world, not by our mental concepts; experts (chemists) determine what counts, not ordinary users
- Open-texture (Waismann): many empirical concepts cannot be exhaustively defined; there will always be borderline cases the concept was not designed to handle
- Implications for knowledge organization: the knowledge base's folder structure imposes classical-theory-like partitions (philosophy/, cognitive-science/); Wittgenstein predicts borderline files that resist clean categorization; design should accommodate ambiguous membership

**1.2 Prototype Theory (Rosch)**
- Graded category membership: not all members of a category are equal; some are "better" or more typical members (robin is a more typical bird than penguin; red is more typical of the color category "red" than orange-red)
- Typicality effects: typical members are processed faster, learned earlier by children, preferred as examples
- The basic level: Rosch's central contribution — categories are structured vertically at three levels: superordinate (furniture), basic (chair), subordinate (easy chair). The basic level is most cognitively natural: (1) most distinctive — most features are shared within this level; (2) most efficiently perceived; (3) first learned; (4) most frequently named
- Why basic level: information-rich categories at the "cut" that maximizes cue validity (within-category similarity high, between-category similarity low)
- Prototype as a summary description, not a stored exemplar: the category representation is a probabilistic family portrait, not a memory of specific instances
- Limitations: typicality varies with context ("cow is a typical farm animal" vs. "penguin is a typical example of an animal that walks bipedally"); ad-hoc categories ("things to take out of your house if it is on fire") have prototypes but no natural kind basis

**1.3 Exemplar Theory and Hybrid Models**
- Exemplar view (Medin & Schaffer, 1978; Nosofsky, 1986): concepts are represented as stored exemplars; classification of a new item is based on its similarity to stored exemplars; no abstraction to a prototype occurs
- Computational model (GCM — Generalized Context Model, Nosofsky): predicts typicality effects, learning curves, and transfer through exemplar similarity; competitive with prototype models on many empirical benchmarks
- Double dissociation evidence: amnesia patients who cannot form prototypes can still use exemplar matching; patients with category-specific semantic dementia lose exemplars but retain prototypes — suggesting both mechanisms
- Hybrid models: combine prototype abstraction with exemplar storage; weight shifts from exemplars toward prototypes as category size increases and instances accumulate
- LLM interpretation: transformer embedding spaces may encode something between exemplar and prototype representations — individual training instances leave traces, but distributed representations also capture category-level statistics

**1.4 Theory-Theory: Concepts as Embedded in Intuitive Theories**
- Murphy and Medin (1985): category coherence is not explained by similarity alone; people find "things that could keep you from drowning" coherent even though the members (life preserver, helium, concrete shoes nailed to a competitor) are dissimilar
- Intuitive theories as scaffolding: concepts are embedded in causal-explanatory structures; the theory constrains what counts as the same kind of thing and what features are essential
- Children's intuitive theories: Carey's work on biological vs. psychological kinds; core knowledge systems (small number, solid object, social agent, place)
- Conceptual change as theory change: acquiring a concept can require restructuring an existing theory; children don't just add "Earth is round" to the flat-Earth theory — they have to revise the theory
- Expert vs. novice conceptual systems: experts have richer causal-theoretical scaffolding; novice concepts are more surface-feature based (sorting physics problems by topic vs. principle)
- Implications for the knowledge base: files are not lists of facts — they are mini-theories; cross-referencing between files is theoretical integration; incorrect cross-references represent theory-level errors, not just factual errors

### Phase 2 — Conceptual spaces and embodied concepts

**2.1 Gärdenfors' Conceptual Spaces**
- Geometry of concepts: represent concepts as convex regions in a multidimensional quality space; dimensions correspond to observable properties (hue, saturation, brightness for color; pitch, timbre, duration for sound)
- Convexity constraint: natural concepts correspond to convex regions — if two objects are in the concept's region, anything between them (on the relevant dimensions) should also be in the concept
- Property vs. object concepts: properties are convex regions in a single domain (color, weight); objects are a combination of regions across domains (this apple is small, round, red, sweet)
- Prototype as the "center of mass" of the conceptual region: Rosch's prototype theory falls out naturally as the centroid of the convex region
- Similarity as distance: similarity between concepts is inverse distance in conceptual space; this formalizes intuitions about conceptual closeness and bridging metaphors
- LLM connection: embedding spaces share structural properties with conceptual space — semantic similarity corresponds to geometric proximity; the geometry of embedding space can be interpreted through the conceptual spaces framework

**2.2 Embodied and Grounded Cognition**
- Barsalou's perceptual symbol systems (1999): concepts are not amodal abstract symbols but are implemented in the same perceptual and motor systems used in perception and action; conceptual processing reactivates perceptual simulations
- Evidence for embodied concepts: motor resonance during action word comprehension (Glenberg & Kaschak); faster word recognition when motor affordances match; emotional concepts activate corresponding bodily states (James-Lange revisited)
- The grounding problem (revisited): embodied cognition is one proposed solution — concepts are grounded through sensorimotor coupling with the world; this connects directly to the phenomenological analysis in the philosophy synthesis
- Weak vs. strong embodied cognition: weak version (perceptual systems contribute to conceptual processing) is well-supported; strong version (concepts ARE implemented only in perceptual motor systems, no amodal representations) is contested
- What LLMs lack from embodied cognition: LLM concepts lack the sensorimotor grounding that Human concepts have; this is one mechanistic account of why LLM "understanding" is hollow in the sense that phenomenology and grounding research predict

**2.3 Structural Alignment and Cross-Domain Mapping (Analogy)**
- Gentner's structure-mapping theory: analogy maps relational structure (not features) from source to target; good analogies preserve a systematically connected relational system, not just individual features
- Systematicity principle: analogical mappings prefer consistent sets of relations over isolated relation matches; "water flow is like electrical current" works because the full pressure-flow-resistance structure maps to voltage-current-resistance
- Analogy-based inference: once a mapping is established, new inferences can be generated by importing structure from the source domain; this is the mechanism of scientific modeling
- Analogy failure: when surface similarity is high but relational structure differs — novices often use features rather than relations (choosing a thermometer over a battery as most analogous to a radiator, because thermometers also involve heat)
- Knowledge base implications: cross-file references within the knowledge base are implicit structural alignments — they claim that two domains share relevant relational structure; bad cross-references impose false structural alignments; the quality of cross-referencing is a measure of the knowledge base's analogical coherence

### Phase 3 — Conceptual change and knowledge organization

**3.1 Conceptual Change: Weak and Strong**
- Chi's taxonomy: three kinds of conceptual change — addition (adding a new concept), revision (changing properties of an existing concept), and kind shift (moving a concept from one ontological category to another — the deepest and most difficult)
- Kind shift example: understanding heat as a substance (caloric theory) vs. understanding heat as molecular motion — not just revising properties but shifting from "substance" to "process" as the ontological kind
- Vosniadou's framework theory account: children have implicit "framework theories" (synthetic models) that constrain how they can integrate new information; misconceptions arise from assimilation of new information into an incompatible framework; conceptual change requires framework revision, not just accretion
- Kuhnian paradigm shifts as kind shifts: major scientific revolutions often involve kind shifts (light as wave/particle, space as a substance/geometry, species as fixed kinds/evolving populations)
- Agent knowledge base implications: most knowledge additions are accretion (new files on new topics); some are revisions (updating existing files with new information); the most important and most disruptive are kind shifts — finding that a key organizing concept needs to be reclassified (e.g., discovering that "semantic memory" in the system is really closer to what Tulving would call "procedural" in some respects)

**3.2 Knowledge Compilation and Proceduralization**
- Anderson's ACT* theory: declarative knowledge ("knowing that") can be compiled into procedural knowledge ("knowing how") through practice — production rules
- The compilation process: from explicit, effortful declarative processing to implicit, automatic procedural processing; examples: learning to drive, learning to read
- Chunking (revisited from Feuerstein and Chase and Simon on chess): large chunks in long-term memory are the product of compilation; experts have compiled thousands of domain-relevant chunks that allow rapid pattern recognition
- The knowledge base as declarative vs. the skills/ files as procedural: the knowledge base grows through accretion and revision; skills grow through compilation; they serve different functions and should be maintained differently
- Risk of premature compilation: compiling incorrect declarative knowledge into a procedural skill produces efficient but systematically wrong performance; this is why skills files need periodic review against the knowledge base to check whether the compiled procedure is still validated by the declarative base

**3.3 Conceptual Hygiene Across an Interdisciplinary Knowledge Base**
- The polysemy problem: a single term used in multiple disciplines with different meanings; "schema" in cognitive psychology (Bartlett, organized knowledge structures) vs. "schema" in database design (table structure) vs. "schematism" in Kant (mediating between intuition and concept) vs. "JSON Schema" in programming; treating these as equivalent is a category error masquerading as cross-disciplinary connection
- Latent scope fallacy and framing effects: how a concept is framed (by its category membership, by the exemplars provided, by the initial description) influences downstream reasoning about it; importing a concept from one domain into another carries the source domain's framing
- Cross-disciplinary concept matching criteria: when does a term in domain A legitimately refer to the same concept as a term in domain B? Structural alignment (Gentner) provides a criterion: the match is legitimate if it preserves relational structure, not just surface similarity of names
- Conceptual hygiene practices: maintaining glossaries of polysemous terms; explicitly flagging when a term is used in a domain-specific sense; using cross-references that specify *what structural feature* warrants the connection, not just that a connection exists

---

## Expected output

12 knowledge files in `knowledge/cognitive-science/concepts/`:

| File | Content |
|---|---|
| `classical-theory-failures.md` | Necessary/sufficient conditions; Wittgenstein family resemblance; Putnam natural kinds; open-texture |
| `prototype-theory-rosch.md` | Graded membership; typicality effects; basic level categories; prototypes as summary descriptions |
| `exemplar-theory-hybrid-models.md` | Exemplar view; GCM; double dissociation; hybrid models; LLM interpretation |
| `theory-theory-knowledge-based-view.md` | Murphy-Medin coherence; intuitive theories; conceptual change as theory change; expert/novice |
| `gardenfors-conceptual-spaces.md` | Quality spaces; convexity; prototype as centroid; similarity as distance; LLM embedding parallel |
| `embodied-grounded-cognition-concepts.md` | Barsalou perceptual symbol systems; sensorimotor grounding; LLM concept limitations |
| `structural-alignment-analogy.md` | Gentner structure-mapping; systematicity; analogy-based inference; analogy failure; cross-reference quality |
| `conceptual-change-types.md` | Chi's taxonomy (accretion/revision/kind-shift); Vosniadou framework theory; Kuhnian paradigm shifts |
| `knowledge-compilation-proceduralization.md` | ACT* theory; compilation; chunking (revisited); declarative-procedural distinction; skills file maintenance |
| `basic-level-categories-asymmetry.md` | Superordinate/basic/subordinate; why basic is privileged; information-maximizing cuts; knowledge organization |
| `conceptual-hygiene-interdisciplinary.md` | Polysemy problem; framing effects; cross-disciplinary matching criteria; glossary practices |
| `concepts-synthesis-agent-implications.md` | Capstone: concepts from a knowledge-base design perspective; category choices; cross-reference quality; conceptual change management |

---

## Connection graph

This plan extends:
- `cognitive-science/memory/tulving-episodic-semantic-distinction.md` → semantic memory structure deepened
- `knowledge/philosophy/cognitive-linguistics-metaphor-blending.md` → alternative account of conceptual structure; points of contrast

This plan connects forward to:
- `cognitive-attention-executive-function-research.md` (this session) — feature integration is a concept-binding problem; attention's role in concept application
- `cognitive-metacognition-calibration-research.md` (this session) — source monitoring errors are partly concept misapplication and cross-domain confusion
- `knowledge/philosophy/philosophy-synthesis.md` — embodied grounding connects directly to phenomenological grounding critique
- `knowledge/ai/frontier-synthesis.md` — interpretability research on LLM concept representations; embedding geometry
