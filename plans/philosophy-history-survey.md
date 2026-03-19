---
source: agent-generated
type: research-plan
origin_session: chats/2026/03/18/chat-001
created: 2026-03-18
last_verified: 2026-03-18
trust: medium
status: active
next_action: "Begin synthesis files — write knowledge/_unverified/philosophy/history/synthesis/mind-body-across-history.md"
---

# Research Plan: History of Philosophy — Broad Survey

## Goals

Alex wants the overarching *story* of how philosophical ideas developed: what mattered most to philosophers in different times and places, how schools of thought influenced and interpreted one another, and the big picture from ancient times to today. This is explicitly a narrative of philosophy, not a reference guide. Files should be written with the arc in mind.

Given Alex's interests (cognitive science, self-organizing systems, language, narrative, consciousness), research will track four through-lines across all periods:

1. **Mind, knowledge, and world** — How do we know anything? What is the mind? How is it related to the body and the world?
2. **Language and meaning** — What is the relationship between thought, language, and reality?
3. **Ethics, politics, and the self** — What should we do? How should we live together? Who or what is the "self" that acts?
4. **Science, metaphysics, and religion** — What is the status of different kinds of knowledge claims? How have the boundaries between science, philosophy, and theology shifted?

---

## Output file structure: `knowledge/_unverified/philosophy/history/`

Each file covers a period or tradition, organized by the four through-lines. A `synthesis/` subfolder will hold cross-cutting thematic files once enough period files exist. A `SUMMARY.md` will be maintained throughout.

---

## Research phases and priority order

### Phase 1 — The Greek Foundation (highest priority) · ✓ 4/4 complete

The whole Western tradition refers back to this period constantly. Cannot understand anything else without it.

1. ✓ `ancient/pre-socratics.md`
   - The question of *arche* (what is fundamental?): Thales (water), Anaximander (the Unlimited), Heraclitus (flux, logos), Parmenides (being as unchanging, the One), Empedocles (four elements), Democritus (atoms and void)
   - The Parmenides/Heraclitus opposition — the problem of change and permanence — runs through the entire subsequent tradition
   - The transition: from mythological to rational-cosmological explanation

2. ✓ `ancient/plato.md`
   - The Theory of Forms: why it matters (the first systematic account of universal concepts, the problem of the one and the many)
   - Epistemology: the divided line, the cave, degrees of knowledge vs. opinion
   - The Socratic legacy: what virtue is, the examined life, the nature of the good
   - Political philosophy: the Republic — justice, the philosopher-king, noble lies, why this is both compelling and troubling
   - The Symposium and Phaedrus: eros as a form of philosophical motivation
   - Later Plato: Parmenides dialogue (self-critique of the Forms), the Timaeus (cosmology)

3. ✓ `ancient/aristotle.md`
   - Aristotle as systematizer and critic of Plato: the forms are in things, not separate
   - Logic: the Organon — syllogistic, categories, the first systematic formal logic
   - Metaphysics: substance, form/matter (hylomorphism), actuality/potentiality, the four causes, the unmoved mover
   - Psychology: *De Anima* — the soul as form of the body (directly relevant to the mind-body discussions in the existing files); active vs. passive intellect
   - Ethics: eudaimonia, virtue as hexis (stable disposition), the mean, friendship, the good life — connect to MacIntyre
   - Politics: humans as political animals, the *polis*, constitutions, justice
   - Poetics: mimesis, catharsis, the unity of plot — Aristotle as the first narrative theorist
   - Note: Aristotle on causation and form is the predecessor to the dynamical systems discussions

4. ✓ `ancient/hellenistic.md`
   - Philosophy as therapy: the shift from cosmology to how to live
   - Epicureans: atoms and void; tranquility through limiting desires; friendship; the clinamen (swerve) and free will
   - Stoics: logos pervading nature; reason as both cosmic principle and human nature; *oikeiôsis* (belonging to oneself and extending to others); Epictetus, Marcus Aurelius, Seneca — practical ethics
   - Skeptics (Pyrrho, Academic skepticism, Sextus Empiricus): suspend judgment (*epoché*), achieve tranquility; the ten modes of skepticism; the regress argument against knowledge
   - Neo-Platonism (Plotinus, Porphyry, Iamblichus): the One beyond being; emanation; soul, intellect, and matter; contemplation — the ancestor of mystical traditions East and West

---

### Phase 2 — The Medieval Synthesis (high priority) · ✓ 3/3 complete

Usually underweighted in popular accounts, but the medieval period does serious philosophical work — not just "reason in service of faith" but genuine innovations in logic, metaphysics, and philosophy of mind. Also the transmission channel through which Greek thought reached the West.

5. ✓ `medieval/augustine-neoplatonism.md`
   - Augustine: the Christianization of Neo-Platonism; time and eternity (Confessions Book XI — Ricoeur's starting point for narrative temporality); the will and original sin; the City of God; inner illumination (precursor to Descartes' innate ideas?)
   - The problem of evil, predestination, free will — seeds debates that run to the present

6. ✓ `medieval/islamic-jewish-transmission.md`
   - The real history: Greek texts preserved and substantially developed in Islamic world while Western Europe largely lost them
   - Al-Kindi, Al-Farabi: first Islamic Aristotelians; Al-Farabi's political philosophy
   - Avicenna (Ibn Sina): the "floating man" thought experiment — a direct precursor to Descartes' cogito and phenomenological self-awareness arguments; his modal metaphysics; psychology
   - Averroes (Ibn Rushd): the great commentator on Aristotle; "double truth" controversy; his actual position (more nuanced); his enormous influence on Latin Scholasticism
   - Al-Ghazali: the Incoherence of the Philosophers — critique of Aristotelian metaphysics from within Islamic thought; occasionalism
   - Maimonides: negative theology; reconciling Aristotle and Torah; the Guide for the Perplexed
   - Note: this transmission story is important for the arc — the West recovered Aristotle largely through Arabic

7. ✓ `medieval/scholasticism.md`
   - The project: synthesize faith and Aristotelian reason
   - Anselm: the ontological argument (God exists necessarily, as that than which nothing greater can be conceived) — first version of a proof that will be argued about forever
   - Aquinas: the five ways; essence/existence distinction; natural law; the synthesis of Aristotle and Christianity — the most ambitious intellectual project of the medieval period; hylomorphic psychology (the soul as form of the body — closer to Aristotle than to Plato/Descartes)
   - Duns Scotus: haecceity (individual essence, "thisness"); the univocity of being; will over intellect
   - William of Ockham: nominalism — universals are just names; Ockham's razor; fideism; the seeds of the dissolution of Scholasticism

---

### Phase 3 — Early Modern: The Break (high priority) · ✓ 4/4 complete

The most dramatic rupture in Western philosophy. Everything changes: the subject becomes central, science replaces theology as the model of knowledge, the problem of the external world becomes urgent.

8. ✓ `early-modern/renaissance-scientific-revolution.md`
   - Humanism: return to classical texts, rhetoric over scholastic logic, the dignity of man
   - Machiavelli: the first political scientist (amoral analysis of power); the shock to political philosophy
   - Bacon: the *Novum Organum*, induction, the idols (biases) — philosophy in service of practical mastery of nature
   - Galileo and the mechanization of nature: the book of nature written in mathematics; the primary/secondary quality distinction — huge consequences for philosophy of mind
   - The general shift: nature as mechanism, not as purposive form

9. ✓ `early-modern/rationalists.md`
   - Descartes: the method of doubt; the cogito; the mind-body problem (substance dualism) — this is the fork in the road that produces most of subsequent philosophy; the pineal gland and why it fails; innate ideas; the role of God in his system
   - Spinoza: the most radical monist in the tradition — God/Nature is the one substance; mind and body are two attributes of the same thing (a serious response to Descartes); determinism; the Ethics as geometric proof; the political theology
   - Leibniz: monads; pre-established harmony (another response to Cartesian dualism); the principle of sufficient reason; the calculus dispute with Newton; optimism (the best of all possible worlds — later mocked by Voltaire in Candide)

10. ✓ `early-modern/empiricists.md`
    - Locke: tabula rasa; ideas of sensation and reflection; primary/secondary qualities; personal identity (consciousness and memory — precursor to Ricoeur); the social contract; toleration
    - Berkeley: esse est percipi — to be is to be perceived; immaterialism as a response to Locke; God as the permanent perceiver
    - Hume: the bundle theory of the self; the problem of induction; the is-ought gap (Hume's guillotine); causation as habit; skepticism about the external world; the limits of reason
    - Note: Hume "awoke Kant from his dogmatic slumber"

11. ✓ `early-modern/kant.md` (warrants its own file)
    - The Copernican revolution: instead of asking how the mind conforms to the world, ask how the world conforms to the mind — the objects of experience are structured by the forms of intuition (space, time) and the categories of understanding
    - The synthetic a priori — connect explicitly to Alex's question in the 2026-03-18 session
    - The three Critiques: Pure Reason (knowledge); Practical Reason (morality, the categorical imperative); Judgment (aesthetics, teleology)
    - The thing-in-itself (noumenon) — we never know reality as it is, only as it appears to us
    - Transcendental idealism vs. empirical realism
    - Moral philosophy: the categorical imperative (three formulations), autonomy, the kingdom of ends
    - Kant's enormous influence: the problem he sets is the problem every subsequent philosopher has to respond to

---

### Phase 4 — Nineteenth Century: Responses to Kant (high priority) · ✓ 4/4 complete

The most intellectually turbulent century — German Idealism, Romanticism, Marx, Darwin, Nietzsche, pragmatism all emerge here.

12. ✓ `nineteenth/german-idealism.md`
    - Fichte: the absolute ego posits itself and the non-ego — the turn to absolute subjectivity; the practical nature of reason
    - Schelling: nature as unconscious mind; the identity philosophy; nature philosophy (Naturphilosophie) — precursor to later emergence thinking
    - Hegel: the Phenomenology of Spirit; the dialectic (not just thesis-antithesis-synthesis but *Aufhebung* — sublation, preserving while overcoming); absolute idealism; history as the development of Spirit toward self-knowledge; the master-slave dialectic; the Logic; political philosophy (the rational state, civil society)
    - Hegel as the most influential and most contested philosopher of the 19th and 20th centuries — everyone is either continuing or reacting against him

13. ✓ `nineteenth/marx-materialism.md`
    - The inversion of Hegel: material conditions drive history, not Spirit
    - Historical materialism; base/superstructure; modes of production
    - Alienation and species-being: the early Marx and human nature
    - Ideology critique: ideas as reflecting material interests
    - Capital and political economy
    - The Communist Manifesto and the political program
    - Marx's enormous downstream influence — but also the philosophical questions he raises (about ideology, false consciousness, the social constitution of knowledge) that are independent of his political program

14. ✓ `nineteenth/kierkegaard-nietzsche.md`
    - Kierkegaard: the three stages (aesthetic, ethical, religious); the leap of faith; anxiety and the self; subjectivity as truth; indirect communication; precursor to existentialism
    - Nietzsche: the death of God and its consequences; the critique of morality (slave morality, ressentiment); the will to power; the eternal recurrence; the Übermensch; perspectivism (all knowledge is from a perspective) — connect to Langacker's construal theory
    - Their shared opposition to Hegel's system: philosophy must engage the singular, existing individual, not dissolve them into the universal

15. ✓ `nineteenth/pragmatism-schopenhauer.md`
    - Schopenhauer: the world as will and representation; will as blind, striving force; the role of art (especially music) as temporary escape; influence on Nietzsche, Freud, later pessimism
    - Peirce: pragmaticism, the pragmatic maxim (the meaning of a concept is its practical consequences), semiotics (sign/object/interpretant — enormous influence on linguistics and cognitive science)
    - James: radical empiricism; the stream of consciousness (a direct precursor to Husserl's time-consciousness); the will to believe; pragmatic theory of truth
    - Dewey: instrumentalism; education; democracy as a way of life; continuity with nature (anti-Cartesian dualism in a pragmatist key)

---

### Phase 5 — Twentieth Century: The Great Bifurcation (high priority) · ✓ 5/5 complete

The analytic/continental split — two traditions that largely stopped talking to each other for most of the century, though that has partly changed.

16. ✓ `twentieth/phenomenology-existentialism.md`
    - Husserl: intentionality (consciousness is always consciousness *of* something); the epoché and phenomenological reduction; time-consciousness (retention, primal impression, protention — connect to Ricoeur and the earlier discussion); the life-world; the crisis of European sciences
    - Heidegger: Dasein and being-in-the-world; care (Sorge); thrownness, projection, fallenness; death and authenticity; temporality; the question of Being vs. the forgetting of Being; the turn (*Kehre*); language as the house of Being; technology and *Gestell*; the connection to Aristotle
    - Merleau-Ponty: the primacy of perception; the lived body (*corps propre*); the body-subject; motor intentionality — the most direct philosophical precursor to embodied cognition and Lakoff/Johnson
    - Sartre: being-in-itself and being-for-itself; bad faith and radical freedom; the look and intersubjectivity; existentialism is a humanism; political engagement
    - de Beauvoir: the second sex; situated freedom; the ethics of ambiguity
    - Camus: the absurd; rebellion vs. suicide; the Myth of Sisyphus

17. ✓ `twentieth/analytic-foundations.md`
    - Frege: the concept/object distinction; sense and reference (*Sinn* und *Bedeutung*); the context principle; quantificational logic — the technical machinery that makes modern logic possible; his influence on Russell and the analytic tradition
    - Russell: logical atomism; the theory of descriptions; Principia Mathematica (with Whitehead); the attempt to reduce mathematics to logic; the paradoxes
    - Early Wittgenstein: the Tractatus — picture theory of meaning; what can be said vs. what can only be shown; whereof one cannot speak, thereof one must be silent
    - Logical Positivism (Vienna Circle): the verification principle; the analytic/synthetic distinction; the attempt to unify science and eliminate metaphysics; Carnap, Schlick, Neurath
    - Quine's demolition of logical positivism: "Two Dogmas of Empiricism" — the analytic/synthetic distinction and reductionism both fail; holism; ontological relativity

18. ✓ `twentieth/later-wittgenstein-ordinary-language.md`
    - The Philosophical Investigations: language games; meaning as use; family resemblance (connect to prototype theory!); private language argument; forms of life; rule-following — the dissolution of traditional philosophy rather than its solution
    - Ordinary language philosophy: Austin (speech acts — connect to Sweetser's speech-act domain), Ryle (the category mistake and the ghost in the machine), Strawson
    - The profound influence on cognitive linguistics: Wittgenstein's anti-essentialism and attention to ordinary use prefigures Lakoff's prototype theory and the whole cognitive linguistics program

19. ✓ `twentieth/philosophy-of-mind-language.md`
    - The mind-body problem after Ryle: functionalism (Putnam — mental states as functional states, multiple realizability), physicalism, eliminativism (Churchland), anomalous monism (Davidson)
    - Philosophy of language: Quine's indeterminacy of translation; Kripke's *Naming and Necessity* (rigid designators, the necessity of identity, the philosophical consequences); Putnam's Twin Earth and semantic externalism — meaning ain't in the head
    - Intentionality: Brentano's revival; Husserl's account; Searle's biological naturalism vs. the Chinese Room
    - Consciousness: Nagel's "What is it like to be a bat?"; Chalmers' hard problem (in our existing files); Dennett's heterophenomenology and multiple drafts

20. ✓ `twentieth/continental-structuralism-poststructuralism.md`
    - Structuralism: Saussure (the signifier/signified distinction, the arbitrariness of the sign, langue vs. parole — the direct ancestor of everything in cognitive linguistics); Lévi-Strauss (mythological structures); the structuralist program
    - Derrida: différance; deconstruction; the critique of presence; the instability of the signifier — what it actually says vs. the caricature
    - Foucault: power-knowledge; discourse analysis; genealogy (after Nietzsche); the archaeology of knowledge; discipline and punish; the history of sexuality — probably the most empirically grounded of the poststructuralists
    - Deleuze: difference and repetition; rhizomes vs. trees; desiring machines (with Guattari); immanence and the plane of consistency; Deleuze as genuinely novel (not just a critic)
    - The continental tradition's influence on literary theory, cultural studies, political thought — and why analytic philosophers mostly ignored it for so long

---

### Phase 6 — Non-Western Traditions (high priority, usually underweighted) · ✓ 3/3 complete

Not an afterthought — these are independent developments of comparable depth and sophistication.

21. ✓ `non-western/indian-philosophy.md`
    - The Vedic background: karma, dharma, the self (atman) and its relation to Brahman (the universal)
    - Upanishadic philosophy: *tat tvam asi* — "that art thou"; the non-dual traditions
    - Nyaya: logic and epistemology; the debate about inference and perception; realism about universals
    - Vaisheshika: atomism (comparable to Democritus but independent)
    - Samkhya-Yoga: dualism of purusha (consciousness) and prakriti (matter); the three gunas
    - Mimamsa: hermeneutics and the eternal validity of the Vedas
    - Vedanta (especially Shankara): Advaita (non-dualism) — only Brahman is real, the world is maya; compare to Western idealism
    - Buddhist philosophy: Nagarjuna's Madhyamaka (the doctrine of emptiness, *shunyata* — everything lacks inherent existence; the two truths); Dignaga and Dharmakirti on epistemology and logic (among the most sophisticated epistemologists in any tradition); Yogacara (mind-only school); the influence on Tibetan philosophy
    - Jain philosophy: anekantavada (many-sidedness of truth) — perhaps the most systematic theory of perspectivism in any tradition; syadvada

22. ✓ `non-western/chinese-philosophy.md`
    - Confucius and early Confucianism: *ren* (benevolence/humaneness), *li* (ritual propriety), self-cultivation, political philosophy — the most influential tradition in Chinese history
    - Mencius vs. Xunzi: human nature debate — are we fundamentally good (Mencius) or neutral/requiring cultivation (Xunzi)?
    - Taoism: Laozi (the *Tao Te Ching* — the way that cannot be named; *wu wei*, non-action; the reversal of conventional values); Zhuangzi (perspectivism, the relativity of all viewpoints, humor and paradox — one of the most philosophically interesting texts in any tradition)
    - Mohism: logic, consequentialist ethics, opposition to Confucian ritual
    - Legalism: Shang Yang, Han Feizi — the political philosophy of control, rule by law rather than virtue
    - Neo-Confucianism (Song dynasty): the synthesis of Confucianism with Buddhist and Taoist ideas; Zhu Xi and the investigation of things; Wang Yangming — the mind is principle
    - Modern Chinese philosophy: the encounter with Western philosophy in the 19th-20th centuries; the New Culture Movement; contemporary Chinese philosophy

23. ✓ `non-western/islamic-philosophy-modern.md`
    - The medieval Islamic tradition was covered in Phase 2; this covers the modern period
    - The 19th-20th century encounter with Western modernity: pan-Islamism; reformers (Al-Afghani, Abduh)
    - The question of secular vs. religious political philosophy in Muslim-majority societies
    - Contemporary Islamic philosophy and theology
    - The underappreciated extent to which Islamic philosophy independently developed ideas later appearing in Western philosophy

---

### Phase 7 — Contemporary Philosophy (medium priority) · ✓ 3/3 complete

24. ✓ `contemporary/ethics-political-philosophy.md`
    - Rawls: *A Theory of Justice*, the original position, the veil of ignorance, the difference principle — the most influential political philosophy text of the 20th century
    - Nozick: libertarian response to Rawls; the minimal state; the experience machine thought experiment
    - MacIntyre: *After Virtue* — the failure of the Enlightenment project in ethics; virtue ethics and narrative (connect to our existing discussion)
    - Singer: effective altruism, the expanding circle, animal liberation
    - Feminist ethics: care ethics (Noddings, Gilligan), feminist political philosophy (Nussbaum, Butler)
    - Environmental ethics, global justice, non-ideal theory — where political philosophy is now

25. ✓ `contemporary/philosophy-of-science.md`
    - Popper: falsificationism; the demarcation problem; the open society
    - Kuhn: paradigms and scientific revolutions — probably the most influential philosophy of science text of the 20th century, despite the conceptual problems
    - Lakatos, Feyerabend: responses to Kuhn
    - The current landscape: scientific realism vs. anti-realism; the metaphysics of science; philosophy of physics, biology, cognitive science

26. ✓ `contemporary/synthesis-open-questions.md`
    - Where does philosophy stand today? The analytic/continental divide narrowing?
    - The revival of metaphysics in analytic philosophy (Kripke, Lewis, Fine)
    - Experimental philosophy
    - The influence of cognitive science on philosophy (philosophy of mind, epistemology)
    - Philosophy in the age of AI: consciousness, moral status, knowledge, democracy
    - Connect to all existing knowledge files in the philosophy cluster

---

## Synthesis files (to write after period files are complete) · ☐ 0/4 complete

These cut across periods and track the four through-lines:

- ☐ `synthesis/mind-body-across-history.md` — Aristotle's hylomorphism → Descartes' dualism → Kant's transcendental idealism → Hegel's absolute idealism → phenomenology → functionalism → embodied cognition. The longest sustained argument in Western philosophy.
- ☐ `synthesis/language-thought-meaning-across-history.md` — Aristotle on meaning → medieval linguistics → Locke's ideas → Leibniz's universal characteristic → Frege/Russell → Wittgenstein → cognitive linguistics. Connect to our existing cognitive linguistics files.
- ☐ `synthesis/the-self-across-history.md` — Plato's soul → Aristotle's psyche → Augustine's inner self → Descartes' cogito → Hume's bundle → Kant's transcendental unity → Hegel's spirit → Nietzsche's will to power → Ricoeur's narrative identity → contemporary.
- ☐ `synthesis/science-metaphysics-religion-across-history.md` — The shifting authority claims across intellectual history; how the boundary between philosophy and science moved; secularization as philosophical process.

---

## Research approach and practical notes

- Each file: ~2000–4000 words. Focus on the *story* and *through-lines* rather than exhaustive coverage. For figures with enormous output (Aristotle, Kant, Hegel), focus on what was most influential and what connects to Alex's interests.
- Non-Western traditions: resist the temptation to organize them purely in relation to Western development. Each should be introduced on its own terms before noting connections.
- Sources: use WebSearch for recent scholarship; for primary texts, the Stanford Encyclopedia of Philosophy (plato.stanford.edu) is reliable and usually accessible. Mark all output files `trust: low`.
- Cross-reference: each file should link to adjacent files and the existing philosophy cluster (`synthesis-intelligence-as-dynamical-regime.md`, `narrative-cognition.md`, `cognitive-linguistics-metaphor-blending.md`, etc.) where relevant.

## Progress log

| Date | Action |
|---|---|
| 2026-03-18 | Plan created; approved by Alex; migrated to `plans/` folder |

Last updated: 2026-03-18
