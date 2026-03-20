# Multi-Agent Management Notes

Working notes on how this repo could support multiple agents without turning the memory store into a conflict magnet.

## Strongest near-term pattern: one worktree per agent

- Use a separate git worktree for each active agent so branch state, index state, and uncommitted edits stay isolated while objects remain shared.
- Keep one long-lived coordination branch for accepted memory changes, and let each agent work on a task branch or detached worktree until its output is ready to merge.
- This matches the existing worktree integration plan and avoids the highest-friction failure mode: two agents editing the same working tree and stomping each other's index or unstaged files.

## Use the repo as shared state, not shared scratch space

- Treat `plans/`, `identity/`, and trusted `knowledge/` as serialized coordination surfaces. These should not be edited opportunistically by many agents at once.
- Let exploratory agents write first to `scratchpad/` or `knowledge/_unverified/`, then have a narrower reviewer/promoter step decide what becomes durable shared memory.
- This aligns with the existing trust model in `HUMANS/docs/DESIGN.md`: user-provided context stays high trust, agent-generated observations stay medium trust until reviewed.

## Add explicit ownership to active work

- The current system has priority and next-action fields, but not task leases. A simple extension would be an optional `owner` or `claimed_by` field on active plans, review items, or scratchpad notes.
- A lightweight claim protocol could be: claim item, do work in a dedicated worktree, publish result, release claim.
- If the repo stays file-based, ownership metadata is cheaper than full distributed locking and would prevent duplicated effort on the same plan item.

## Separate orchestration from execution

- One orchestrator agent should decide task decomposition, assign work, and merge accepted outputs.
- Worker agents should focus on bounded tasks: research one file, draft one plan section, validate one change, or inspect one subtree.
- The memory repo already fits an orchestrator/subagent shape better than a swarm. Shared summaries, `next_action`, and review queues are legible when one coordinator is responsible for promotion.

## Improve traceability before increasing concurrency

- Multi-agent use gets easier if ACCESS and commit metadata gain `agent_id`, reliable `session_id`, and a clearer task identifier.
- That would let the repo answer: which agent touched this file, under which task, and whether another agent is already active nearby.
- The existing access-log improvement ideas are therefore a prerequisite for scaling the number of concurrent agents with confidence.

## Escalation path if contention becomes real

- The current version-token model is logically correct for concurrent writes, but conflict frequency will rise as more agents touch the same files.
- First escalation: per-file claims or lock files for hot coordination files such as `plans/SUMMARY.md` and `meta/review-queue.md`.
- Second escalation: a small SQLite-backed coordination layer for leases, append-only event logging, and derived summaries, while markdown remains the human-readable surface.

## Practical operating model

1. Orchestrator picks tasks from active plans.
2. Each worker gets a dedicated worktree and task id.
3. Workers write drafts to `_unverified/` or `scratchpad/` first.
4. Reviewer/orchestrator promotes, merges, and updates summaries.
5. Shared high-trust files stay single-writer or claim-gated.

That keeps the current repo model recognizable while adding just enough structure to prevent multi-agent chaos.