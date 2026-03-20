created: 2026-03-19
last_verified: 2026-03-19
next_action: "Complete — all 13 items done. Human review of knowledge/_unverified/philosophy/ethics/ files recommended."
origin_session: chats/2026/03/19
origin_session: chats/2026/03/19/chat-001
source: agent-generated
status: complete
trust: medium
type: research-plan

# Research Plan: Ethics and Metaethics in Depth

## Goals

The existing knowledge base covers alignment technically — reward modeling, constitutional AI, scalable oversight — without grounding any of it in systematic normative ethics or metaethics. It covers the rationalist community's Bayesian epistemology and EA movement without engaging the philosophy these communities selectively draw from. This plan fills that gap: deep systematic engagement with the major normative frameworks, the metaethical question of what moral claims are, and the applied ethics of AI specifically. Parfit's work is the keystone: his *Reasons and Persons* connects personal identity (already its own plan), population ethics, and rational choice — while having been enormously influential on effective altruism and the AI safety movement.

Primary connections to existing files:
- `rationalist-community/` — EA movement theoretical foundations
- `ai-frontier/alignment/frontier-alignment-research.md` — technical alignment needs philosophical foundations
- `philosophy/narrative-cognition.md` — ethical life as narrative (MacIntyre thread)
- `plans/personal-identity-memory-research.md` — Parfit appears in both plans; build on that work

---

## Problem statement

Without systematic ethics, alignment debates default to folk intuitions applied inconsistently. "The model should be helpful and harmless" is an inchoate moral claim; whether helpfulness and harmlessness can even be jointly maximized, whether "harmless" means deontologically constrained or consequentially assessed, whether the right moral unit is individual users or society — none of this is resolvable without framework. Similarly, the EA community's confident moral arithmetic (comparing the welfare of future people, trading off lives against quality-adjusted life years) imports strong metaethical commitments that are contested.

---

## Scope decisions

**In scope:**
- Classical normative frameworks: utilitarianism, Kantian deontology, virtue ethics, contractualism
- Parfit's *Reasons and Persons* in depth: self-interest, consequentialism, personal identity, population ethics
- Metaethics: what moral claims mean and whether any are true (moral realism, expressivism, error theory, relativism)
- Applied AI ethics: moral status of AI systems, responsibility attribution, algorithmic fairness, AI welfare
- Moral epistemology: how we come to have moral knowledge; reflective equilibrium; moral intuitions as evidence

**Out of scope:**
- Full political philosophy (Rawls deserves his own plan if pursued)
- Detailed normative bioethics (Singer's animal ethics covered in passing; full bioethics is too wide)
- Legal theory and jurisprudence

---

## Phases

### Phase 1 — Classical normative frameworks

**1.1 Utilitarianism: Bentham to Singer**
- Bentham's felicific calculus: all and only pleasure/pain matter; impartial aggregation
- Mill's refinements: quality of pleasures, rule utilitarianism as practical guide, harm principle
- Sidgwick's dualism: hedonistic consequentialism but acknowledgment of rational intuitionism
- Moore's ideal utilitarianism: valuable states beyond pleasure (beauty, knowledge, friendship)
- Singer's preference utilitarianism: satisfying informed preferences rather than producing pleasure
- The expanding moral circle: from persons to animals to future persons to AI

**1.2 Kantian Deontology**
- The categorical imperative: three formulations (universalizability, humanity formula, kingdom of ends)
- Perfect vs. imperfect duties; the strict duty not to lie
- Rational autonomy as the basis of moral worth: why rational agents have dignity rather than price
- Contemporary Kantians: Korsgaard's constitution of agency, O'Neill on publicity and trust
- Deontological constraints on AI: regardless of consequences, are there things AI systems must not do?
- The alignment tax in Kantian terms: is there a duty to refuse harmful instructions even at performance cost?

**1.3 Virtue Ethics**
- Aristotle's eudaimonism: living well as the expression of excellent character virtues
- The doctrine of the mean, practical wisdom (phronesis), the unity of virtue
- MacIntyre's revival: virtues require a tradition and a practice; emotivism's failure (from *After Virtue*)
- Foot's natural goodness: virtue as biological flourishing concept applied to rational animals
- Can AI have virtues? The virtue account of reliability, honesty, and judgment in AI systems

**1.4 Contractualism and Contractarianism**
- Contractarianism (Hobbes/Gauthier): morality as rational agreement among self-interested parties
- Rawls' contractualism (preview): veil of ignorance, difference principle — reserved for its own plan
- Scanlon's contractualism: an act is wrong if its performance can be reasonably rejected by someone seeking principles for mutual agreement
- Why Scanlon matters for AI: "reasonable rejection" provides a concrete test for AI outputs — would any affected person reasonably reject the principle under which this output was generated?
- T.M. Scanlon's application to moral responsibility and blame

### Phase 2 — Parfit's *Reasons and Persons*

**2.1 Self-Defeating Theories and Rational Inconsistency**
- The self-interest theory (S): always do what is best for yourself in the long run — and why it is self-defeating
- Collective action and prisoner's dilemmas: morality vs. rationality
- The distinction between directly and indirectly self-defeating theories: how consequentialism can be directly self-defeating but indirectly justified

**2.2 Consequentialism and Its Implications**
- Parfit's critique of agent-relative consequentialism and defense of agent-neutral reasons
- The Repugnant Conclusion: any population with lives barely worth living, if large enough, is better than a happier smaller population — and why every classical theory leads to something repugnant
- Person-affecting views: an outcome can only be worse if it is worse *for* someone — and why this is hard to maintain across generations

**2.3 Population Ethics**
- Total view vs. average view vs. critical level utilitarianism
- Non-identity problem: future people don't exist yet; how can we wrong people who only exist because of our choices?
- The asymmetry: it seems bad to bring into existence people with terrible lives but not obligatory to bring into existence people with great lives
- Why this is AI-relevant: decisions about training future AI systems affect which systems exist, not just what existing systems are like

**2.4 What We Together Do**
- Collective ethics: problems where each individual's contribution is imperceptible but the collective effect is enormous
- Five mistakes in moral mathematics: ignoring small probabilities, tiny harms from each, the counterfactual problem, the bad event is inevitable anyway, overdetermination
- Application to AI: no single AI output causes mass harm, but collectively, patterns of AI output shape epistemic culture profoundly

### Phase 3 — Metaethics

**3.1 Moral Realism**
- What moral realism claims: there are objective moral facts, not dependent on what anyone thinks or feels
- Cornell realism (Sturgeon): moral properties are natural properties; moral facts explain observations
- Non-naturalist realism (Huemer's phenomenal conservatism, Ross's intuitionism): moral facts are sui generis
- The argument from disagreement against realism: persistent moral disagreement suggests no facts
- Companions in guilt: mathematical realism faces the same challenges and is typically accepted — why not moral realism?

**3.2 Anti-Realism: Expressivism and Error Theory**
- Error theory (Mackie): moral claims purport to be objective but nothing is objectively prescriptive; all moral claims are false
- Quasi-realism (Blackburn): starting from expressivism, earning back the features of moral discourse that look realist
- The Frege-Geach problem for expressivism: how to handle moral claims embedded in complex logical contexts ("If lying is wrong, then getting your brother to lie is wrong")
- Why metaethics matters for AI: if moral realism is true, moral knowledge is possible and AI could in principle be morally knowledgeable; if expressivism is true, moral "knowledge" is a different kind of thing entirely

**3.3 Moral Epistemology**
- Intuitionism as moral epistemology: moral intuitions are evidence; reflective equilibrium
- Ideal observer theory: what a fully rational, fully informed observer would judge
- The limits of moral intuitions: known biases (in-group favoritism, identifiable victim effect, scope insensitivity)
- How to handle moral disagreement: when to revise intuitions vs. reject arguments
- Application: AI alignment as a problem of aggregating moral evidence from human feedback that is biased and inconsistent

### Phase 4 — Applied AI ethics

**4.1 Moral Status and AI Welfare**
- Criteria for moral status: sentience (capacity to suffer), sapience (capacity for rational self-direction), moral agency
- Whether current LLMs meet any criteria: no scientific consensus; the question is live
- The precautionary case for AI welfare research (Anthropic's interpretability-as-welfare research direction)
- Moral circle expansion: how the circle has historically expanded (slaves, women, animals); the direction of argument for AI

**4.2 Responsibility Attribution in AI Systems**
- The responsibility gap: when an AI system causes harm, who is responsible?
- Distributed responsibility: designers, deployers, users, the system — and how liability is distributed in practice
- Moral luck and responsibility: if an AI output causes harm due to unforeseen user misuse, are developers responsible?
- Meaningful human control as a design criterion: reversibility, oversight, explainability as responsibility conditions

**4.3 Algorithmic Fairness and the Alignment of Values**
- Impossibility theorem of fairness (Chouldechova/Kleinberg): certain common fairness criteria are mathematically incompatible
- Which fairness criterion to optimize is a normative choice, not a technical one
- RLHF as implicit value alignment: whose preferences are the raters'? What is the distribution of moral views in crowdworker populations?
- Constitutional AI as an explicit normative commitment: what does Anthropic's constitution actually commit to?

---

## Output format

Files go in `knowledge/_unverified/philosophy/ethics/` with standard frontmatter. Phase 4 files may also be placed in `knowledge/_unverified/ai-frontier/alignment/` given direct application to alignment debates.

---

## Progress tracking

### Phase 1 — Classical frameworks
- [x] 1.1 Utilitarianism: Bentham to Singer
- [x] 1.2 Kantian deontology
- [x] 1.3 Virtue ethics
- [x] 1.4 Contractualism

### Phase 2 — Parfit
- [x] 2.1 Self-defeating theories
- [x] 2.2 Consequentialism implications
- [x] 2.3 Population ethics
- [x] 2.4 What we together do

### Phase 3 — Metaethics
- [x] 3.1 Moral realism
- [x] 3.2 Anti-realism: expressivism and error theory
- [x] 3.3 Moral epistemology

### Phase 4 — Applied AI ethics
- [x] 4.1 Moral status and AI welfare
- [x] 4.2 Responsibility attribution
- [x] 4.3 Algorithmic fairness

**Progress:** 13/13 items complete

---

## Priority order

1. **Phase 2.3** (population ethics) — Parfit's most influential contribution to EA; directly relevant to AI safety debates about future AI populations
2. **Phase 1.1** (utilitarianism) — foundational; EA's implicit moral framework
3. **Phase 3.1** (moral realism) — metaethical question that underlies all alignment debates
4. **Phase 4.1** (moral status and AI welfare) — most direct applied ethics relevance
5. **Phase 1.4** (Scanlon contractualism) — the "reasonable rejection" criterion is practically useful for AI output evaluation
