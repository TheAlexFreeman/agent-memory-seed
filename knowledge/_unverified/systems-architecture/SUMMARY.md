# Systems Architecture Knowledge — Summary

Research notes on the storage, concurrency, and automation primitives that underlie agent-memory-seed as a Git-backed memory system.

## Files

| File | Topics |
|---|---|
| `git-object-model.md` | Git object graph, index as staging boundary, lock-file semantics, refs, reflog, packfiles, and why the current MCP write path depends on them |
| `git-worktrees-and-hooks.md` | Linked worktree topology, per-worktree vs shared refs, orphan branches, bootstrap implications, hook execution model, and governance automation seams |
| `git-plumbing-and-automation.md` | Porcelain vs plumbing, explicit commit publication path, `update-ref`, `cat-file`, `notes`, `bundle`, sparse-checkout, and resilient scripting patterns |
| `filesystem-atomicity-and-locking.md` | `rename()` atomicity, `O_CREAT|O_EXCL`, advisory locks, unlink failure modes, `fsync()` durability, and why lockfile assumptions break on unusual mounts |
| `filesystems-for-developers.md` | Journaling vs copy-on-write filesystems, FUSE and network-share behavior, watcher caveats, and capability-tier thinking for stateful developer tools |

## Cross-references

- [plans/systems-architecture-research.md](plans/systems-architecture-research.md) — the active research plan these files satisfy
- [plans/worktree-integration.md](plans/worktree-integration.md) — downstream integration plan that depends on worktree/orphan-branch semantics
- [tools/agent_memory_mcp/git_repo.py](tools/agent_memory_mcp/git_repo.py) — current Git wrapper discussed throughout these notes