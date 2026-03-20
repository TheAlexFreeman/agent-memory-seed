created: 2026-03-20
last_verified: 2026-03-20
next_action: "Begin Phase 1 — Metacognitive monitoring and control"
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: active
trust: medium
type: research-plan

# Research Plan: Metacognition, Calibration, and Epistemic Self-Monitoring

## Goals

Metacognition — thinking about one's own thinking — is the cognitive substrate of epistemic humility. For this system, it is the scientific underpinning of the trust system: when should a memory be trusted? How should confidence be calibrated to accuracy? What happens when an agent monitors its own epistemic states incorrectly (the Dunning-Kruger effect, overconfidence, illusions of knowing)? The memory science knowledge base introduced source monitoring (how people track where knowledge came from) and the Feeling of Knowing (FOK) judgments. This plan goes deeper: the full metacognitive architecture, calibration science, and the specific failure modes that are most dangerous for this system.

This is arguably the most operationally important cognitive science plan for the system, because the trust system (`trust: low/medium/high`, `source: agent-generated` vs. `source: external-research`) is a metacognitive engineering artifact. Understanding the empirical science of metacognition tells us how to build it better and where it will fail.

Primary connections to existing files:
- `cognitive-science/memory/false-memory-constructive-nature.md` — source monitoring failure is a metacognitive failure
- `cognitive-science/memory/reconsolidation-agent-design-implications.md` — access-as-reconsolidation connects to metacognitive monitoring of retrieval
- `meta/curation-policy.md` — the trust system is a metacognitive architecture; this plan grounds it scientifically
- `meta/integrity-checklist.md` — calibration failure is the mechanism by which integrity checks are needed
- `philosophy/ethics/moral-epistemology.md` — reflective equilibrium is a metacognitive process

---

## Problem statement

The system's trust levels are a practical solution to a genuine epistemic problem: the agent cannot directly inspect the accuracy of its knowledge files. It must use indirect indicators (source, recency, access history, human review) to estimate reliability. This is precisely what calibration science studies: the relationship between confidence judgments and actual accuracy. The relevant empirical literature is rich and somewhat alarming — human metacognition is systematically miscalibrated in specific, predictable ways (overconfidence for difficult domains, underconfidence for easy ones; the illusion of knowing; the curse of knowledge; the Dunning-Kruger effect for novices). Understanding these failure modes is essential for designing a trust system that compensates for them rather than inheriting them.

---

## Scope decisions

**In scope:**
- Metacognitive monitoring: Feeling of Knowing (FOK), Judgment of Learning (JOL), Confidence judgments — their accuracy and systematic biases
- Calibration: the relationship between confidence and accuracy; overconfidence effects; the hard-easy effect; Brier scores as calibration metrics
- The Dunning-Kruger effect: why novices overestimate their competence; why experts sometimes underestimate theirs
- Source monitoring: remembering where knowledge came from; source monitoring errors and their role in false memory and confabulation
- The illusion of knowing and illusion of explanatory depth: people think they know more than they do; probing reveals gaps
- Metacognitive control: how monitoring judgments are used to allocate study effort, regulate retrieval strategies, and terminate searches (RSVP effect, search termination)
- The feeling of rightness (FOR) and conflict monitoring in dual-process theory — metacognitive signal that triggers System 2 override of System 1 output
- Epistemic cowardice and epistemic courage: avoiding the expression of uncertain beliefs; calibrated uncertainty communication
- Calibration in machine learning: temperature scaling, Platt scaling, reliability diagrams; what ML has learned from calibration science

**Out of scope:**
- Full theory of mind (understanding others' mental states) — deserves its own plan
- Clinical metacognitive deficits (anosognosia, dementia-related metacognitive impairment) in detail
- Social metacognition (shared vs. individual epistemic states) — peripherally relevant but separable

---

## Phases

### Phase 1 — Metacognitive monitoring and control

**1.1 The Metacognitive System: Monitoring and Control**
- Nelson and Narens (1990) framework: two levels — the object level (cognition proper: encoding, retrieving, reasoning) and the meta level (monitoring the object level and issuing control commands); monitoring and control as separate functions with bidirectional links
- Monitoring measures: Ease of Learning (EOL) judgments before study; Judgments of Learning (JOL) after study; Feeling of Knowing (FOK) judgments before recall attempts; Confidence judgments after recall
- Control operations: allocation of study time (spending more time on items with lower JOL); resolution of retrieval failures (try harder vs. give up); termination of memory search (when to stop looking)
- The accuracy of monitoring: relative accuracy (ordering; do you know which items you will recall?) vs. absolute accuracy (calibration; do your confidence levels match your actual hit rates?)
- Nelson's gamma correlation as the standard measure of relative metacognitive accuracy

**1.2 Feeling of Knowing (FOK) and the Tip-of-the-Tongue State**
- The Tip-of-the-Tongue (TOT) phenomenon: high FOK accompanied by retrieval failure; partial information (first letter, number of syllables) is accessible
- Accessibility vs. direct access accounts of FOK: (a) the FOK is driven by the accessibility of related information (if many associates come to mind, the target is probably stored); (b) the FOK reflects a direct signal from the trace itself about its strength
- Koriat's accessibility model (1993): FAM = Feeling of Another's Memory — FOK is a summary feeling derived from the accessibility of partial information, not a direct readout of storage state
- Mismatch between FOK and actual recall: TOT states can persist even when the target is very close; FOK can be high for false memories
- Agent analog: the model's "sense" that it knows something (confident output) may reflect accessibility of related training content, not the actual accuracy of the specific claim — a systematic metacognitive error

**1.3 Calibration: Overconfidence and the Hard-Easy Effect**
- The calibration curve: x-axis = stated confidence (%sure), y-axis = actual proportion correct; perfect calibration = diagonal; overconfidence = curve below diagonal for hard items
- The hard-easy effect (Lichtenstein & Fischhoff, 1977): overconfidence for difficult questions (stated confidence exceeds accuracy); slight underconfidence for very easy questions
- The Brier score: proper scoring rule for probabilistic forecasts; B = mean squared deviation of stated probability from actual outcome; lower is better
- Expert vs. novice calibration: domain-specific expertise produces better calibration in that domain; experts in domain A are not better calibrated in domain B
- Implications for the trust system: the hard-easy effect predicts that the agent's highest-confidence claims in difficult domains are most likely to be the most miscalibrated; the trust system should apply more skepticism precisely where the model expresses the most confidence on domain-difficult claims

### Phase 2 — The Dunning-Kruger effect and illusions of knowing

**2.1 The Dunning-Kruger Effect**
- Original finding (Kruger & Dunning, 1999): people lowest in competence in a domain show the largest overestimations of their competence; people highest in competence show slight underestimation (because they assume others find the domain as easy as they do)
- The mechanism: performing a skill and evaluating whether it was performed well require overlapping cognitive capabilities; someone who lacks the skill also lacks the metacognitive capacity to recognize that they lack it
- Later critiques and replications: some effects may be partially explained by regression to the mean; but the core finding (novices are overconfident; experts underestimate relative competence) is robust across domains
- Domains of application: humor, grammar, logical reasoning, medical knowledge — wherever competence is measurable
- Agent implications: in domains where the model has limited training coverage (niche research areas, recent developments), the model may be systematically overconfident, and the overconfidence is hardest to detect precisely in those domains where detection capability is lowest

**2.2 The Illusion of Knowing and the Illusion of Explanatory Depth**
- The illusion of knowing (Glenberg et al., 1982): readers consistently overestimate how much they have understood from text; tested comprehension reveals gaps invisible to self-assessment during reading
- Fluency effects: processing fluency (ease of reading) is incorrectly attributed to understanding; familiar, easy-to-read text produces higher JOL even when comprehension is equivalent
- The illusion of explanatory depth (IOED, Rozenblit & Keil, 2002): people believe they understand how mechanical, political, and social systems work much better than they do; asking them to produce a detailed causal explanation reveals the gap
- The curse of knowledge (Camerer, Loewenstein, & Weber, 1989): once you know something, you cannot accurately recall what it was like not to know it; experts systematically underestimate how much explanation novices need
- Agent analog: the model's fluency in generating text about a topic (which is high, by design) can produce an illusion of explanatory depth — confident, coherent explanations that lack genuine causal depth. The `source: agent-generated` flag is a partial defense against this.

**2.3 Source Monitoring and Prospective Memory Failures**
- Johnson et al. (1993) Reality Monitoring framework: memories of imagined vs. perceived events differ systematically; imagined events have more cognitive operations in their records, perceived events have more perceptual and contextual detail
- Source monitoring errors: confusing the source of a memory (heard vs. read vs. imagined; self-generated vs. externally provided) — produce false memories, plagiarism, and confabulation
- External source monitoring: distinguishing between two different external sources (which news outlet said what; which file said what)
- Internal source monitoring: distinguishing between imagined and remembered, between one's own prior output and the original source
- Agent-specific source monitoring: distinguishing between what was in a knowledge file and what the model generated in elaborating it; distinguishing between what happened in this session and what the model "knows" from training; distinguishing between a verified fact and a generated plausible-sounding claim
- Implementation in the system: `source:` and `origin_session:` frontmatter fields are source monitoring aids; they don't eliminate source confusion but they provide the raw material for source monitoring during careful review

### Phase 3 — Metacognitive control and calibrated uncertainty

**3.1 Metacognitive Control of Learning**
- Allocation of study time: people preferentially allocate study time to items with lower JOL — this is generally adaptive, but overconfident learners allocate insufficient time to poorly-learned items (because JOL exceeds actual retention)
- The discrepancy-reduction model (Dunlosky & Hertzog): study until JOL reaches a goal criterion; the learning process is regulation-driven, not just passive
- Test-potentiated learning: being tested (even failing) improves later learning; testing calibrates JOL downward when incorrect, triggering more study
- Illusion of competence from rereading: rereading feels like learning (generates high JOL) but produces minimal actual retention gains; fluency masquerades as competence
- Agent implications: the testing effect is why human review (which imposes a kind of test on the agent's knowledge) produces better calibrated knowledge files than passive accumulation; human review disrupts the fluency-as-knowing illusion

**3.2 Conflict Monitoring and the Feeling of Rightness**
- De Neys (2012) on conflict monitoring: people are sensitive to logical conflicts between System 1 intuitive responses and normative System 2 answers, even when they (sometimes) fail to correct their intuition
- The Feeling of Rightness (FOR) as a metacognitive signal guiding System 1/2 interaction: when FOR is high, System 2 does not engage; when FOR is low, System 2 is triggered
- Luria's frontal syndrome: patients with prefrontal damage cannot self-monitor; they produce perseverative errors but do not notice them; conflict detection fails
- Monitoring failures and metacognitive errors under load: when cognitive load is high, monitoring resources are depleted; errors are both more frequent and less detected
- Agent implications: the model may have a functional analog of FOR — it may produce confident outputs with low internal "error signal" even when the output is wrong; conflict detection between knowledge files is a system-level compensation for this failure

**3.3 Calibrated Communication of Uncertainty**
- Tetlock's superforecasters: most accurate forecasters use precise probability statements (not vague hedges like "probably"); explicitly update on new evidence; decompose complex questions into tractable subproblems; maintain calibrated track records
- Epistemic cowardice: avoiding precise probability estimates to preserve plausible deniability; using vague hedges that are immune to falsification; preferring mushy statements to precise uncertain ones
- Proper scoring rules as incentive structure: Brier score, log score — both reward honest probability estimates and penalize over- and under-confidence; they create the right incentive for calibrated disclosure
- The communication design problem: how a system should express its uncertainty to a human who will act on it; confidence that is too high is overconfidence; confidence that is too low is epistemic cowardice; calibration is the goal
- Implications for the trust system and file outputs: knowledge files should express uncertainty explicitly where it exists; confidence levels in frontmatter should be calibrated (not default-high); agent outputs should distinguish "I know this" from "I infer this" from "this seems plausible" with some precision

---

## Expected output

10 knowledge files in `knowledge/cognitive-science/metacognition/`:

| File | Content |
|---|---|
| `metacognitive-monitoring-control.md` | Nelson-Narens framework; EOL/JOL/FOK/confidence; monitoring accuracy vs. calibration |
| `feeling-of-knowing-tip-of-tongue.md` | FOK; TOT; Koriat accessibility model; mismatch with actual recall |
| `calibration-overconfidence-hard-easy.md` | Calibration curves; Brier score; hard-easy effect; expert vs. novice calibration |
| `dunning-kruger-effect.md` | Original finding; mechanism; critiques; agent implications for low-coverage domains |
| `illusion-of-knowing-explanatory-depth.md` | Glenberg et al.; fluency effects; IOED (Rozenblit & Keil); curse of knowledge |
| `source-monitoring-reality-monitoring.md` | Johnson et al. Reality Monitoring; source attribute dimensions; agent-specific source errors |
| `metacognitive-control-learning.md` | Study-time allocation; test-potentiated learning; rereading illusion; human review as testing |
| `conflict-monitoring-feeling-of-rightness.md` | De Neys; FOR; failures under load; frontal monitoring syndrome |
| `calibrated-uncertainty-communication.md` | Superforecasters; epistemic cowardice; proper scoring rules; uncertainty expression design |
| `metacognition-synthesis-agent-implications.md` | Capstone: full synthesis — the trust system as metacognitive engineering; where it will succeed and fail |

---

## Connection graph

This plan extends:
- `cognitive-science/memory/false-memory-constructive-nature.md` → deepened via reality monitoring
- `cognitive-science/cognitive-science-synthesis.md` → Section 5 (schema confabulation) resolved
- `meta/curation-policy.md` → grounded in calibration science

This plan connects forward to:
- `cognitive-attention-executive-function-research.md` (this session) — conflict monitoring is an attention-executive interaction
- `knowledge/philosophy/ethics/moral-epistemology.md` — epistemic virtue connects to calibration; what it means to reason well
- `plans/cognitive-social-cognition-development-research.md` (planned) — theory of mind and social metacognition
