---
created: 2026-03-20
origin_session: chats/2026/03/20/cowork-enrichment
source: agent-generated
trust: medium
---

# Architecture Review Notes — 2026-03-20

Observations from a full read of the repo's current state, including all
governance files, knowledge base, plans, chat history, and the newly enriched
identity folder.

---

## 1. identity/SUMMARY.md is over its compact budget

The enriched `identity/SUMMARY.md` is now ~628 tokens against a 450-token
target. The total compact payload is 5959/7000 (1041 tokens headroom), so
the system is still within overall budget, but `identity/SUMMARY.md` is the
only file over its per-file target (+178 tokens).

**Options:**
- Trim the SUMMARY back toward 450 tokens by moving the Eve Sweetser and
  Engram-relationship paragraphs into drill-down-only content (they're in
  `profile.md` and `engram-relationship.md` already).
- Accept the overshoot and redistribute budget from files that are under
  target (scratchpad/USER.md is 274 tokens under, plans/SUMMARY.md is 251
  tokens under).
- Formally adjust the per-file targets in `meta/quick-reference.md` to
  reflect the richer identity portrait.

**Recommendation:** The identity portrait is the single most useful piece of
startup context for personalizing a session. The 178-token overshoot is worth
it. Formally adjust the target from ~450 to ~650 and note the tradeoff in
quick-reference.md. This is a genuine architectural tradeoff: richer identity
improves personalization at the cost of context budget. The overall budget
still has headroom.

---

## 2. The belief-diff log needs a post-enrichment entry

The last belief-diff was 2026-03-19. Since then, identity/ went from 2 files
(profile.md, SUMMARY.md) to 5 files (added intellectual-portrait.md,
literary-tastes.md, engram-relationship.md, plus substantial edits to the
existing two). This is a significant content change that should be captured
in the next belief-diff review, even though it's within the normal
governance model (agent-inferred, trust: medium, user-approved).

The identity churn alarm threshold is 5 traits/session. The enrichment added
many new traits but was explicitly requested by the user, so this should not
trigger an alarm — but it should be noted.

---

## 3. plans/ACCESS.jsonl aggregation is overdue (review-queue item)

The review queue has a pending item from 2026-03-19 noting that
`plans/ACCESS.jsonl` has 100 entries against a 15-entry aggregation trigger.
This has been pending for at least one full day. Not urgent, but it's the
kind of maintenance debt that accumulates quietly.

---

## 4. The `_unverified/` backlog is growing

The knowledge base has a large number of files in `_unverified/` across
django/, react/, devops/, philosophy/, rationalist-community/, ai/frontier/,
ai-tools/, mcp/, and system-notes/. The 120-day low-trust retirement
threshold means these files will start auto-archiving around mid-July 2026
if not reviewed. Some of these (django stack, react stack) are directly
useful for Alex's daily work and should be promoted sooner rather than later.

The ai-history/ folder has already been promoted (2026-03-19), setting a
precedent for the review process. But the remaining backlog is substantial —
probably 80+ files across all unverified subdirectories.

**Observation:** The human review gate works structurally but has a bandwidth
problem at scale. The Exploration-stage knowledge flooding alarm (5 files/day)
was presumably triggered during the initial research burst but doesn't appear
to have been flagged. Worth checking whether the alarm mechanism is actually
operational or just documented.

---

## 5. The scratchpad is stale

`scratchpad/CURRENT.md` still references `compact-bootstrap-efficiency.md` as
an active plan, but it's listed as completed in `plans/SUMMARY.md`. The
"Immediate next actions" section mentions finishing the compact-bootstrap plan
and keeping access-log tooling behind the `mcp-reorganization.md` dependency
chain — but `mcp-reorganization.md` is also completed. These references are
stale by at least one session.

**This is exactly the kind of drift the scratchpad lifecycle rules are meant
to catch:** entries should be promoted or cleared after ~3 sessions without
action. The current entries are from 2026-03-19 (one session ago, arguably
two), so they're within the window but trending stale.

---

## 6. Worktree integration is the top build priority and it's moving

7/24 items complete on `worktree-integration.md`. Next action requires
protected-file approval (editing `meta/quick-reference.md`). This is a
genuine blocker — the agent can't unilaterally edit identity-critical routing.
The plan is well-structured and the init script already works.

---

## 7. The self-knowledge folder is a novel and valuable pattern

`knowledge/self/` with four files (engram-system-overview, engram-governance-model,
intellectual-threads, session-2026-03-20) is an unusual design choice that
I haven't seen in other memory systems. The system literally writes about
itself — its architecture, its governance model, its intellectual character,
its session history. This is the "self-reference as feature" thread from
`intellectual-threads.md` made concrete.

Worth noting: these files are `trust: medium` and `source: agent-generated`.
They're the system's self-image, not the user's description of the system.
The governance model correctly flags the self-referential risk, but the
mitigation (git audit trail + human review) applies here too.

---

## 8. Multi-agent coordination remains an unresolved design question

The two-agent workflow (Cowork sandbox + laptop Claude Code) is documented
but not governed. There's no `agent_id` claim protocol, no merge conflict
resolution beyond git's native machinery, and no way to attribute ACCESS
entries to a specific agent instance. The scratchpad notes from 2026-03-19
flag this as an open question.

The worktree-integration plan assumes single-writer-per-worktree, which
sidesteps the problem for the host-repo use case. But for the standalone
repo, the two-agent pattern is already in use and ungoverned.

---

## Summary assessment

The system is healthy, coherent, and well-governed for its Exploration stage.
The main risks are not architectural but operational: the _unverified backlog
is growing faster than review capacity, the scratchpad has minor staleness,
and the identity SUMMARY is slightly over budget. None of these are urgent.
The intellectual content (philosophy, AI history, literature, self-knowledge)
is the repo's most distinctive feature and is well-organized.
