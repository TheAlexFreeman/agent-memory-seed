# System Maturity

This document tracks the memory system's developmental stage and parameterizes governance thresholds accordingly. The core insight: a young system should bias toward exploration (capturing aggressively, retiring slowly), while a mature system should bias toward order (capturing selectively, retiring confidently).

## Maturity signals

The system's developmental stage is assessed from quantitative signals, not calendar time:

| Signal | How to measure | What it indicates |
|--------|---------------|-------------------|
| **Total sessions** | Count of chat folders in `chats/` | Volume of interaction |
| **ACCESS density** | Total ACCESS.jsonl entries across all folders | Depth of retrieval history |
| **File coverage** | Percentage of content files accessed at least once | How much of the memory has proven relevant |
| **Confirmation ratio** | Ratio of `trust: high` files to total content files | How much of the memory has been validated |
| **Identity stability** | Sessions since last identity trait change | Whether the user portrait has converged |
| **Retrieval success rate** | Mean helpfulness score across recent ACCESS entries | Whether the system is serving useful memory |

## Maturity stages

### Stage 1: Exploration (young system)

**Typical signals:** < 20 sessions, < 50 ACCESS entries, file coverage < 30%, confirmation ratio < 0.3

**Bias:** Toward chaos. The system doesn't yet know what matters.

| Parameter | Exploration setting | Rationale |
|-----------|-------------------|-----------|
| Low-trust retirement threshold | 120 days | Keep unverified content longer — it might prove useful |
| Medium-trust flagging threshold | 180 days | Don't rush to flag content for re-verification |
| Staleness trigger (no access) | 120 days | Tolerate dormant files — usage patterns haven't stabilized |
| Aggregation trigger | 15 entries | Aggregate sooner to build retrieval patterns faster |
| Identity churn alarm | 5 traits/session | Allow more identity exploration before flagging |
| Knowledge flooding alarm | 5 files/day | Allow more aggressive knowledge capture |

### Stage 2: Calibration (adolescent system)

**Typical signals:** 20–80 sessions, 50–200 ACCESS entries, file coverage 30–60%, confirmation ratio 0.3–0.6

**Bias:** Balanced. The system has patterns but they're still evolving.

| Parameter | Calibration setting | Rationale |
|-----------|-------------------|-----------|
| Low-trust retirement threshold | 60 days | Matches curation-policy default; start applying pressure on unverified content |
| Medium-trust flagging threshold | 120 days | Matches curation-policy default; moderate verification expectations |
| Staleness trigger (no access) | 90 days | Standard maintenance cadence |
| Aggregation trigger | 20 entries | Standard aggregation frequency |
| Identity churn alarm | 3 traits/session | Standard drift detection |
| Knowledge flooding alarm | 3 files/day | Standard flooding detection |

### Stage 3: Consolidation (mature system)

**Typical signals:** > 80 sessions, > 200 ACCESS entries, file coverage > 60%, confirmation ratio > 0.6

**Bias:** Toward order. The system knows what matters and should be selective.

| Parameter | Consolidation setting | Rationale |
|-----------|----------------------|-----------|
| Low-trust retirement threshold | 45 days | Aggressive cleanup — the system has enough signal to judge value quickly |
| Medium-trust flagging threshold | 90 days | Expect timely verification |
| Staleness trigger (no access) | 60 days | Unused memory in a mature system is likely genuinely irrelevant |
| Aggregation trigger | 25 entries | Larger batches for more statistically meaningful patterns |
| Identity churn alarm | 2 traits/session | Mature identity should be stable — changes are more suspicious |
| Knowledge flooding alarm | 2 files/day | The system should be past bulk knowledge acquisition |

## Current stage assessment

_Not yet assessed._ The first assessment should be generated when the system has accumulated enough sessions for the signals to be meaningful (approximately 5+ sessions). Record each assessment below with the date and signal values.

### Assessment log

```
## [YYYY-MM-DD] Stage assessment

**Stage:** Exploration | Calibration | Consolidation
**Signals:**
- Total sessions: N
- ACCESS density: N entries
- File coverage: N%
- Confirmation ratio: N
- Identity stability: N sessions since last change
- Retrieval success rate: N mean helpfulness

**Active parameter set:** [stage name]
**Notes:** Any observations about whether the system is transitioning between stages.
```

---

_No assessments yet._

## Stage transitions

Transitions are not hard boundaries. The agent should:

1. **Assess maturity** during each periodic review (see `meta/update-guidelines.md`).
2. **Advance only on a clear majority** — 4 or more of the 6 signals must agree on the later stage before advancing. A 3-3 split is not sufficient to move forward.
3. **Tiebreaker: stay put, or prefer the earlier stage.** If signals are evenly split (3-3) between two adjacent stages, remain in the current stage. If there is no prior assessment (first evaluation ever), default to Exploration regardless of the split.
4. **Regress only on sustained signal drop.** Do not revert to an earlier stage based on a single signal crossing back. If 4 or more signals drop back to an earlier stage's range, flag for re-assessment in `meta/review-queue.md` rather than auto-reverting — regression should be a deliberate decision, not a reflexive one.
5. **Log all transitions and close calls** in both this file's assessment log and in `CHANGELOG.md`. A "close call" (3-3 split that was resolved by tiebreaker) is worth noting so future assessments can see the trend.

The system can also regress: if a user's focus shifts dramatically (new job, new domain), many existing files may become irrelevant, file coverage drops, and the system should temporarily revert toward exploration parameters for the new domain while maintaining consolidation parameters for stable areas. This is a judgment call for the agent, documented in the assessment log.
