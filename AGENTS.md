# Agent Memory System

This repository is a persistent AI memory system. At the start of every session, follow the routing rules in `meta/quick-reference.md`. When local agent-memory MCP tools are available, prefer them for memory reads, search, and governed writes; fall back to direct file access only when the MCP surface is unavailable or lacks the needed operation. Do not duplicate the full rule list here — `README.md` and `meta/` are the single source of truth.
