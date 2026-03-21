---
created: 2026-03-20
last_verified: 2026-03-20
next_action: "All 14 knowledge files produced in knowledge/software-engineering/testing/ — plan complete"
origin_session: chats/2026/03/20/chat-003
source: agent-generated
status: complete
trust: medium
type: research-plan
---

# Research Plan: Software Testing, Validation, and Verification

## Goals

This plan builds a systematic knowledge base on software testing at every level — from unit tests to formal verification — and across every discipline from traditional QA to AI/ML evaluation. The coverage is designed to be both principled (establishing conceptual foundations that don't age) and practical (covering the specific tools, techniques, and methodologies in active use in the Engram project and software development broadly).

The immediate motivation is twofold. First, the Engram system itself has a growing MCP test suite and CI pipeline; rigorous knowledge of testing principles should directly improve that work. Second, the HUMANS/ tooling section documents practices for human-agent collaboration; testing and validation are central to any sustainable software practice. This knowledge base provides the intellectual grounding for both.

A deeper motivation: software testing is the primary epistemology of software — the set of methods by which claims about software behavior are warranted. Understanding testing well is therefore a prerequisite for reasoning clearly about software quality, software correctness, and software risk. The formal verification literature (Hoare logic, model checking, abstract interpretation) connects directly to the philosophy knowledge base's analysis of formal reasoning and structural soundness. The AI evaluation literature (CheckList, red-teaming) connects directly to the memetic-security and metacognition research on how beliefs (outputs) should be validated.

Primary connections to existing files:
- `knowledge/software-engineering/systems-architecture/` — architecture shapes testability; design-for-testability is a central architectural concern
- `knowledge/cognitive-science/cognitive-science-synthesis.md` — metacognition applies directly to testing: test suites encode beliefs about system behavior; failure is a prediction error; reconsolidation principles apply to spec updates
- `plans/cognitive-metacognition-calibration-research.md` — calibration and overconfidence apply to test-coverage beliefs; mutation testing as a Dunning-Kruger diagnostic
- `knowledge/ai/` — AI/ML evaluation methodology is a distinct discipline growing from software testing

---

## Problem statement

The knowledge base has strong coverage of theoretical foundations (logic, mathematics, philosophy, cognitive science) and AI-specific concerns (alignment, interpretability, RAG, multi-agent). But software engineering knowledge is sparse beyond systems architecture. Testing in particular — the discipline that connects software claims to software evidence — is absent. This plan fills the gap comprehensively: from the fundamental impossibility results (testing cannot show absence of bugs) through unit testing methodology through integration and system testing through formal methods through AI/ML evaluation and red-teaming.

---

## Scope decisions

**In scope:**
- Testing foundations: the V-model and testing hierarchy; the oracle problem; Dijkstra's impossibility argument; testing vs. verification; DeMillo-Lipton-Perlis competent programmer hypothesis
- Unit testing: isolation principles; test doubles (mocks, stubs, fakes, spies, dummies — Meszaros taxonomy); FIRST properties; assertion design; test smells and how to fix them
- Test-driven development (TDD): red-green-refactor cycle; triangulation; TDD as specification discipline; emergent design under TDD; BDD extension (Gherkin, Given-When-Then)
- Black-box testing techniques: equivalence partitioning; boundary value analysis; decision table testing; state transition testing; cause-effect graphing
- White-box testing techniques: statement, branch, path, and MC/DC coverage; control-flow and data-flow analysis; coverage as a proxy for test quality
- Mutation testing: measuring test suite quality directly; mutation operators; mutation score and its limits; surviving mutants as specification gaps; practical tools (Mutmut, PIT, Stryker)
- Property-based testing: generative testing (QuickCheck, Hypothesis); shrinking; finding invariants; model-based property testing; stateful property testing
- Integration testing strategies: big-bang vs. incremental (top-down, bottom-up, sandwich); integration test design; API contract testing (Pact); consumer-driven contracts
- System and end-to-end testing: system test scope and design; acceptance testing (user story, use-case based); regression testing strategy; test pyramid and its critics (trophy, honeycomb)
- Performance and load testing: latency percentiles (p50, p95, p99); throughput testing; load/stress/soak/spike tests; profiling and bottleneck attribution
- Software quality assurance and process: defect taxonomy and classification; root cause analysis (why-five, fishbone); defect density and escape rate metrics; review and inspection (Fagan inspection); QA vs. QC distinction
- Formal verification fundamentals: Hoare logic (pre/post conditions, invariants, weakest precondition calculus); design by contract (Eiffel, assert-based contracts); model checking (state explosion problem, SPIN, TLA+); abstract interpretation; bounded model checking (CBMC); practical limits and applicability
- AI/ML evaluation: train/test split discipline; cross-validation; data leakage and contamination; benchmark design flaws; evaluation metric choice (accuracy, F1, BLEU, ROUGE, and their limits); dataset shift and evaluation under distribution shift
- Behavioral testing for NLP/LLM systems: CheckList methodology (Ribeiro et al. 2020) — minimum functionality tests (MFT), invariance tests (INV), directional expectation tests (DIR); capability-based test organization; beyond accuracy to behavioral slicing
- Red-teaming and adversarial evaluation: structured red-team methodology; threat modeling for AI systems; adversarial NLP (synonym substitution, paraphrase, character-level attacks); jailbreaking taxonomy; compositional adversarial prompting; red-team findings as specification updates
- Testing economics and strategy: Pareto principle in defects (80/20 and its variants); risk-based testing; cost of late defect discovery (Boehm's data); test prioritization; ROI of different coverage levels; shift-left testing
- Continuous testing and CI/CD integration: test pyramid and pipeline design; flaky test management; test parallelization; incremental testing; test selection and impact analysis

**Out of scope:**
- Full coverage of specific testing toolchains (pytest, Jest, Cypress) — these are practical notes that belong in the HUMANS/tooling section, not the knowledge base
- Security testing in depth (penetration testing, SAST/DAST) — important but warrants its own plan focused on the OWASP and secure SDLC literature
- Statistical hypothesis testing (A/B testing) — belongs under statistics/data science
- Usability testing and UX evaluation — different discipline, different plan

---

## Phases

### Phase 1 — Foundations and unit testing

**1.1 Testing Foundations and Epistemology**
- The fundamental problem: software testing as epistemic practice — testing provides evidence for behavioral claims, not proofs; the oracle problem (how do you know what the right answer is?); the test completeness impossibility (Dijkstra: "testing shows the presence of bugs, not their absence")
- The testing hierarchy: unit → integration → system → acceptance tests; Agile variations (test pyramid: many unit, fewer integration, few E2E); critics of the pyramid (trophy, honeycomb, ice cream)
- Testing vs. verification vs. validation: V&V distinction; black-box (behavioral) vs. white-box (structural) approaches; static vs. dynamic analysis; formal verification as the limit case of static analysis
- The DeMillo-Lipton-Perlis competent programmer hypothesis (1978): if the program is wrong, a randomly chosen test is likely to fail — formal verification may not be necessary because tests are powerful enough relative to real bugs; rebutted by mutation testing (many bugs survive typical test suites)
- Test oracle problem in practice: expected outputs from specification, from reference implementation, from invariants and metamorphic relations, from partial oracles (crash ≠ expected = always a bug)
- Coverage and its limits: coverage as necessary but not sufficient; 100% coverage does not mean all bugs are found; what coverage metrics actually measure and what they don't
- Key terms and taxonomy: SUT (system under test), fixture, test case, test suite, test double, assertion, test smell, regression, acceptance

**1.2 Unit Testing Principles**
- Isolation: a unit test tests exactly one unit in isolation from its collaborators; isolation enables fast feedback, precise attribution, and parallel execution
- FIRST properties (Robert Martin): Fast (unit tests must run in milliseconds — if slow, they won't be run); Isolated (no shared state between tests, no dependency on execution order); Repeatable (same result every time, no dependence on time, random, network, or filesystem); Self-validating (pass or fail — no human judgment needed to determine outcome); Timely (written at the time of the code they test, not after)
- Test doubles taxonomy (Meszaros, 2007): Dummy (passed but never used — fills parameter lists); Fake (working implementation unsuitable for production — in-memory database); Stub (returns predetermined answers to calls made during the test); Spy (records calls for later verification — like stub but also records); Mock (pre-programmed with expectations — fails if unexpected calls are made)
- Mock vs. stub clarified: the key distinction is verification point — stubs answer questions ("return this when called"); mocks verify behavior ("assert this was called with these arguments"); mocks make tests more brittle but catch interaction bugs
- Sociable vs. solitary tests (Martin Fowler): solitary tests mock all collaborators; sociable tests use real collaborators where safe; neither is universally correct — mix based on confidence boundary
- Assertion patterns: one logical assertion per test (allows precise failure identification); expected/actual parameter order consistency; assertion messages that diagnose failure without re-reading the test; fluent assertion libraries (Hamcrest, AssertJ, pytest's assert rewriting)
- Test smells — anti-patterns that reduce unit test value: Mystery Guest (test depends on external state not visible in the test), Eager Test (tests too many behaviors at once), Fragile Test (breaks when implementation changes but behavior doesn't), Slow Test (runs too slow to be run frequently), Conditional Test Logic (if-else in a test — split into two tests instead)

**1.3 Test-Driven Development (TDD) and BDD**
- Red-Green-Refactor cycle: Red — write a failing test for the next small increment of behavior; Green — write the minimal code to make it pass (no over-engineering); Refactor — clean up code and tests while keeping tests green; repeat
- TDD as specification discipline: tests are executable specifications; writing the test first forces clarity about desired behavior before implementation begins; tests are the primary artifact; the code is derived from them
- Triangulation: when the first implementation is obviously incomplete, add a second test case that forces a more general solution; triangulation prevents premature generalization
- Emergent design under TDD: TDD practitioners argue that good designs emerge from test-first development because testability forces decoupling; the consequence is that code written test-first tends to have high cohesion and low coupling
- Critique of strict TDD: the "London school" (mockist TDD) vs. "Detroit/classic school" (statist TDD); over-mocking leads to brittle tests strongly coupled to implementation; balance is the key; not all code benefits equally from TDD (exploratory code, UI code, algorithmic code)
- Behavior-Driven Development (BDD): Given-When-Then (Gherkin) as a natural-language test specification format; BDD bridges the gap between product owners and developers; Cucumber/SpecFlow as execution frameworks; the "living documentation" property
- Beyond unit TDD: acceptance-test TDD (ATDD) — starting from failing acceptance tests, working inward; outside-in TDD; the walking skeleton pattern

### Phase 2 — Test design techniques and coverage

**2.1 Black-Box Test Design Techniques**
- Equivalence partitioning: divide the input space into equivalence classes (partitions) where behavior is expected to be the same within a class; test one representative from each class; partitions span valid and invalid inputs
- Boundary value analysis: bugs cluster at boundaries of equivalence partitions; test values at, just below, and just above boundaries; the off-by-one error is the paradigm case; three-point boundary analysis (boundary - 1, boundary, boundary + 1) as baseline
- Decision table testing: enumerate all combinations of conditions and their actions; useful for complex business rules with multiple conditions; exposes missing or contradictory rules; all-conditions coverage vs. minimal test set
- State transition testing: model the SUT as a finite state machine; test transitions between states; check that all transitions are exercised and that invalid transitions are rejected; state transition diagram → test cases
- Pairwise (all-pairs) testing: for systems with many parameters, exhaustive combination testing is infeasible; pairwise covers all parameter pairs with minimum test cases; mathematical framework (covering arrays); tools (PICT, AllPairs); when it is and isn't sufficient
- Cause-effect graphing: formal method for deriving test cases from complex condition/action relationships; logical translation of requirements; rarely used in practice but conceptually important for completeness

**2.2 White-Box Coverage and Mutation Testing**
- Statement coverage: every executable statement is exercised at least once; weakest structural criterion; 100% statement coverage still allows many bugs
- Branch coverage: every branch of every control flow decision is exercised; subsumes statement coverage; the standard minimum for most quality requirements; equivalence with decision coverage
- Path coverage: every possible path through the program is exercised; infeasible for programs with loops; approximated by basis path testing (McCabe)
- MC/DC (Modified Condition/Decision Coverage): each condition in a decision independently affects the decision outcome; DO-178B/C requirement for aviation software; most stringent functional coverage criterion in practice; characterization and test set construction
- Data-flow analysis: use-definition chains; def-use coverage (every definition of a variable reaches at least one use); du-path coverage; complements control-flow analysis
- Coverage as a diagnostic, not a target: Goodhart's Law applied to coverage — when coverage becomes a target it ceases to be a good measure; coverage should guide testing, not be the goal; 80% coverage can be more meaningful than 100% trivially achieved coverage
- Mutation testing — measuring test suite quality: mutation operators transform the source code (negate conditions, change operators, swap variables, delete statements); a test suite "kills" a mutant if any test fails on the mutated code; mutation score = killed/total; survivor analysis reveals specification gaps
- Practical mutation testing: equivalent mutants (syntactically different but semantically equivalent — cannot be killed, must be manually identified); stubborn mutants (semantically different but hard to kill); mutation testing cost and sampling strategies; tools: Mutmut (Python), PIT (Java), Stryker (JS/TS)

**2.3 Property-Based Testing**
- Generative testing (QuickCheck, Hypothesis): instead of specific example-based tests, write properties that should hold for all inputs; the framework generates random inputs and tries to falsify the property; vastly more test coverage per line of test code
- Shrinking: when a failing input is found, the framework automatically minimizes it to the simplest input that still fails; this is the key innovation that makes property tests actionable (no hand-written reproduction case)
- Invariant discovery: common property patterns — roundtrip properties (encode/decode is identity), oracle properties (compare to reference implementation), metamorphic relations (f(transform(x)) relates to f(x) in a predictable way), model-based properties (component behavior matches a simpler model)
- Stateful property testing: testing stateful systems where actions change state; command sequences generated and executed against the SUT and a model; transition failures indicate inconsistency between implementation and model
- Hypothesis-style assume(): constraining the input space to valid domain inputs; the distinction between pre-condition filtering and generator design; over-constraining kills diversity; under-constraining wastes effort on invalid inputs
- When property-based testing shines: parsers, serialization, data structures, algorithms with mathematical specifications, protocol implementations; when it is harder: UI, side-effectful systems, underdetermined specifications

### Phase 3 — Integration, system, and performance testing

**3.1 Integration Testing Strategies**
- The integration test challenge: isolated unit tests pass but combined components fail at interfaces — the NASA/Mars Climate Orbiter unit-metric vs. metric confusion; integration tests catch interface mismatches that unit tests by design cannot
- Top-down integration: integrate from the highest-level components downward; stubs replace lower-level components not yet integrated; allows early system-level operation but requires many stubs
- Bottom-up integration: integrate from lowest-level components upward; drivers replace higher-level components not yet integrated; components are tested in a realistic environment but no system-level operation is possible until late
- Sandwich integration: hybrid; most common in practice; integrates from the middle outward in both directions simultaneously; minimizes driver and stub counts
- Big-bang integration: develop all components separately, then integrate at once; lowest upfront cost, highest debugging cost; only appropriate for small systems
- Integration test scope and design: the test should cross one real interface and mock everything else; "integration test" in the broader industry sense means testing real collaborators together; "integration test" in the precise sense means testing at the integration seam only
- API contract testing (Pact): consumer-driven contract testing — the consumer generates expectations ("I will call the API with X and expect Y"); the provider verifies its implementation satisfies all consumer contracts; prevents provider changes from silently breaking consumers
- Consumer-driven contract testing workflow: consumer generates a pact file; pact broker stores it; provider CI runs pact verification; bidirectional contract testing (Pact v4 schema matching)

**3.2 System, End-to-End, and Acceptance Testing**
- System testing scope: test the complete integrated system against its requirements specification; external interfaces only; black-box; includes functional and non-functional requirements
- Test pyramid politics: Mike Cohn's original pyramid (many unit, some integration, fewer UI); Fowler's update; the "testing trophy" (Kent C. Dodds: prioritize integration tests); the "honeycomb" (Spotify: many integration tests in services, few E2E); no universally optimal shape — depends on architecture and system confidence boundaries
- End-to-end testing: tests the full application stack from UI to database; highest confidence, highest maintenance cost, slowest, most flaky; Playwright/Cypress/Selenium as modern tools; hermetic E2E tests (test doubles for external dependencies) vs. live-system E2E
- Regression testing: re-running tests to verify that new changes haven't broken existing behavior; the regression suite is the primary defense against feature instability; risk-based regression selection (change impact analysis vs. full suite)
- Acceptance testing: tests that verify the system meets stakeholder requirements; often written in collaboration with non-technical stakeholders (BDD Gherkin); distinction between functional acceptance tests and UAT (User Acceptance Testing — exploratory, human)
- Exploratory testing: skilled, simultaneous test design and execution; complements scripted tests by finding unexpected failures; requires a skilled tester; session-based exploratory testing (time-boxed, documented)

**3.3 Performance, Load, and Reliability Testing**
- Latency percentile discipline: mean is almost useless for performance characterization; the p50/p95/p99/p99.9 percentile hierarchy; why tail latency matters (the "long tail" of user experience; the "fan-out" problem where mean latency is dominated by tail)
- Load testing: test at expected production traffic levels; verify the system meets its SLAs under normal load
- Stress testing: test beyond expected production load to find the breaking point; reveals failure modes and capacity limits
- Soak testing (endurance testing): test at moderate load for extended duration (hours to days); reveals memory leaks, connection pool exhaustion, resource accumulation bugs
- Spike testing: test response to sudden dramatic load increases; reveals elasticity and auto-scaling behavior
- Chaos engineering (Gremlin, Netflix Chaos Monkey): deliberately inject failures (kill instances, degrade network, corrupt responses) in production or staging; test that the system degrades gracefully and recovers automatically; the "game day" methodology
- Performance profiling as testing: profiling a performance test run to attribute latency to specific components; CPU profiling vs. memory profiling vs. I/O profiling; flame graphs; the observer effect in profiling

### Phase 4 — Software quality assurance and formal methods

**4.1 Software Quality Assurance: Process and Metrics**
- QA vs. QC distinction: Quality Assurance (process-oriented — prevent defects through process improvement) vs. Quality Control (product-oriented — detect defects in the product); both are necessary; QC without QA is whack-a-mole
- Defect taxonomy: classification by severity (blocker/critical/major/minor/trivial), by type (logic error, boundary error, interface error, data handling, timing, performance, usability), by origin phase (requirements, design, coding, testing, deployment)
- Root cause analysis: the five-whys technique (ask "why?" five times to find root cause, not symptom); fishbone (Ishikawa) diagram; causal loop diagrams for systemic defects; the distinction between immediate cause, contributing cause, and root cause
- Defect density and escape rate: defects per KLOC or per module as a quality proxy; escape rate (defects found post-release / total defects found) as a process quality metric; using defect data to guide testing effort allocation (Pareto principle: 80% of defects come from 20% of modules)
- Code review and inspection: Fagan inspection (formal, role-based, metrics-driven); modern lightweight code review (pull requests); review checklists vs. freeform review; what code review catches vs. what testing catches; social dynamics of effective review
- Process maturity models: CMMI (Capability Maturity Model Integration) — levels 1-5 from Initial to Optimizing; ISO 9001 for software; how process maturity correlates (imperfectly) with product quality; critique of process-over-substance in software QA

**4.2 Formal Verification Fundamentals**
- The formal methods spectrum: from lightweight (assertions, contracts, type systems) through semi-formal (model checking, abstract interpretation) to heavyweight (interactive theorem proving); applicability and cost tradeoffs at each level
- Hoare logic: pre/post condition specification of program behavior; {P} C {Q} — if precondition P holds before executing command C and C terminates, then postcondition Q holds; the assignment axiom; consequence rule; composition rule; loop rule (loop invariant + loop variant)
- Weakest precondition calculus (Dijkstra): compute the weakest precondition wp(C, Q) — the weakest predicate that guarantees Q after C executes; allows deriving minimal preconditions from postconditions
- Design by contract (Bertrand Meyer, Eiffel): class invariants, method preconditions, and method postconditions as first-class language features; the substitution principle connection (Liskov); Python's `assert` and `hypothesis` @given/@assume as lightweight approximations
- Model checking: exhaustive state-space exploration to verify temporal logic properties (CTL, LTL); the state explosion problem and mitigation (symbolic model checking, BDDs, bounded model checking); SPIN for protocol verification; TLA+ (Lamport) for distributed systems; industrial adoption (AWS, Microsoft use TLA+)
- Abstract interpretation (Cousot & Cousot): over-approximation of the set of program states reachable during execution; soundness: no false negatives (every real bug is reported or ruled out); precision: minimize false positives; practical tools: Astrée (aviation-critical C), Polyspace; connects to type systems as abstract interpretations
- SAT and SMT solvers: Boolean satisfiability and satisfiability modulo theories as the engine of modern automated verification; Z3 (Microsoft), CVC5; bounded model checking as SAT reduction; verification conditions and why they work
- Practical limits: formal verification is expensive to set up and maintain; best suited for safety-critical, security-critical, or highly stable core algorithms; most valuable when bugs are catching before deployment has extremely high cost

**4.3 AI/ML Evaluation Methodology**
- The train/test contamination problem: if test data has been seen during training (directly or through prompt engineering or dataset construction), the evaluation is invalid; leakage is often subtle and hard to detect; examples from NLP benchmarks exhausted by LLM training
- Cross-validation: k-fold CV, stratified k-fold for class imbalance, leave-one-out for small datasets; nested CV for hyperparameter search; proper holdout protocol (freeze test set, use validation set for all tuning decisions)
- Evaluation metric choice: accuracy as a misleading metric for class-imbalanced problems; F1 and precision-recall tradeoff; area under ROC; calibration of probabilistic outputs (Brier score, ECE); when different metrics matter in different deployment contexts
- Benchmark design principles: behavioral coverage (the benchmark should test the full range of claimed capability); adversarial examples that probe failure modes; human ceiling measurement; how quickly a benchmark saturates (becomes too easy) and how to extend it
- Dataset shift: distribution shift between train and test; covariate shift (X distribution changes), concept drift (P(Y|X) changes), prior probability shift; evaluation under shift; the distinction between IID evaluation and OOD evaluation
- The Goodhart's Law problem in ML evaluation: when a metric becomes a target, it ceases to be a good measure; model developers overfit to benchmark tasks; leaderboard overfitting; what to do (hold out benchmarks, diversify metrics, measure on real users)

### Phase 5 — AI/ML behavioral testing and red-teaming

**5.1 CheckList: Behavioral Testing for NLP/LLM Systems**
- Ribeiro et al. (2020) CheckList methodology: inspired by software testing — systematically test behavioral capabilities rather than aggregate accuracy; three test types: MFT (minimum functionality tests — basic capability should work), INV (invariance tests — behavior should not change under specified perturbations), DIR (directional expectation tests — behavior should change in a predictable direction)
- Capability-based test organization: test suites organized by capability (negation, temporal reasoning, coreference) rather than by dataset; enables targeted failure analysis
- Template-based test case generation: generating thousands of test cases by filling templates with wordlists; enables systematic coverage without manual test case writing
- CheckList applied to LLMs (2023+): adapting CheckList to instruction-following; capability decomposition; the HELM (Holistic Evaluation of Language Models) extension — scenario × metric combinations
- Beyond accuracy to behavioral slicing: disaggregated evaluation by demographic subgroup, by input length, by topic, by writing style; disparate performance across slices reveals systematic failures invisible in aggregate metrics
- Evaluation of reasoning: process evaluation vs. outcome evaluation; chain-of-thought evaluation; faithfulness vs. plausibility of explanations; whether the model's stated reasoning actually matches its computation

**5.2 Red-Teaming and Adversarial Evaluation**
- Structured red-team methodology: organized probing of a system's failure modes by a dedicated team; roles: red team (attack), blue team (defend/mitigate), white team (adjudicate); scoping the red team (threat model defines attack surface); red team report as a specification update
- Threat modeling for AI systems: STRIDE adaptation — Spoofing (model identity), Tampering (training data, outputs), Repudiation (deniability of AI decisions), Information Disclosure (model memorization, inference attacks), Denial of Service (adversarial inputs that consume resources), Elevation of Privilege (jailbreaking)
- Prompt injection taxonomy: direct injection (user manipulates the prompt directly), indirect injection (injected content in retrieved context), stored injection (malicious content in the knowledge base), multi-turn injection (manipulating over multiple turns)
- Adversarial NLP: character-level attacks (typos, Unicode homoglyphs); word substitution attacks (synonym replacement preserving semantics); paraphrase attacks (rewrite to bypass classifiers); compositional adversarial prompting (combine individually harmless components)
- Jailbreaking taxonomy: role-play framings, hypothetical framings, many-shot jailbreaking, prefix attacks (adversarial prefixes found by optimization), suffix attacks (GCG — appending universal adversarial suffixes); automated red-teaming with generative models
- Red-team findings management: findings classified by severity and exploitability; mitigations as specification updates; regression testing against mitigation regressions; the red team as ongoing, not one-time

---

## Expected output

14 knowledge files in `knowledge/software-engineering/testing/`:

| File | Content |
|---|---|
| `testing-foundations-epistemology.md` | Oracle problem, Dijkstra impossibility, testing hierarchy, V&V distinction, DeMillo-Lipton-Perlis hypothesis, coverage limits |
| `unit-testing-principles.md` | FIRST properties, test doubles taxonomy (Meszaros), sociable vs. solitary, assertion patterns, test smells |
| `test-driven-development.md` | Red-green-refactor, triangulation, emergent design, London vs. Detroit schools, BDD and Gherkin, ATDD |
| `black-box-test-design.md` | Equivalence partitioning, boundary value analysis, decision tables, state transition testing, pairwise testing, cause-effect graphing |
| `coverage-and-mutation-testing.md` | Statement/branch/path/MC/DC coverage, data-flow analysis, Goodhart's Law applied, mutation operators, mutation score, tools |
| `property-based-testing.md` | QuickCheck/Hypothesis, shrinking, invariant patterns (roundtrip, oracle, metamorphic, model-based), stateful PBT |
| `integration-testing-strategies.md` | Top-down/bottom-up/sandwich/big-bang integration, interface mismatch failures, contract testing (Pact), consumer-driven contracts |
| `system-and-acceptance-testing.md` | Test pyramid and variants (trophy, honeycomb), E2E testing, regression testing, acceptance testing, exploratory testing |
| `performance-and-load-testing.md` | Latency percentile discipline, load/stress/soak/spike testing, chaos engineering, profiling as testing, flame graphs |
| `software-qa-metrics-process.md` | QA vs. QC, defect taxonomy, root cause analysis (five-whys, fishbone), defect density, code review and inspection, CMMI |
| `formal-verification-foundations.md` | Hoare logic, weakest precondition calculus, design by contract, formal methods spectrum, practical limits |
| `model-checking-abstract-interpretation.md` | Model checking (SPIN, TLA+, state explosion), abstract interpretation (Cousot), SAT/SMT solvers, bounded model checking |
| `ml-evaluation-methodology.md` | Contamination detection, cross-validation protocols, metric choice, benchmark design, dataset shift, Goodhart's Law in ML |
| `behavioral-testing-and-red-teaming.md` | CheckList (MFT/INV/DIR), capability-based test organization, HELM, behavioral slicing, red-team methodology, prompt injection taxonomy, adversarial NLP, jailbreaking |

---

## Connection graph

This plan extends:
- `knowledge/software-engineering/systems-architecture/` — architecture shapes testability; design-for-testability is a first-class concern in both domains
- `knowledge/ai/` — ML evaluation methodology (§4.3 and §5) sits at the intersection of testing and AI

This plan connects to:
- `plans/cognitive-metacognition-calibration-research.md` — calibration science (§4.2) grounds what "confident" test coverage means; mutation testing is a diagnostic for the Dunning-Kruger pattern in test suites
- `knowledge/cognitive-science/cognitive-science-synthesis.md §5` — false memory and constructive reconstruction maps to test oracle errors and specification confabulation
- `knowledge/philosophy/philosophy-synthesis.md §5` — identity failure modes (prompt injection, context exhaustion) directly catalogued in §5.2 of this plan
- `plans/cognitive-concepts-categorization-research.md` — the test doubles taxonomy (Meszaros) is a categorization system; the quality of the taxonomy affects how consistently test doubles are applied
- Future: `security-testing-research.md` — SAST/DAST, OWASP coverage, penetration testing methodology (scope of a follow-on plan)
