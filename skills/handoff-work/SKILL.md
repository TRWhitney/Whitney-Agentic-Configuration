---
name: handoff-work
description: Use when unfinished repository work must continue in a fresh context, session, or agent without losing decisions or verification state.
---

# Handoff Work

Make the durable work record sufficient for immediate continuation. Point to canonical artifacts instead of rewriting them.

## Ownership

Own only continuation state. Do not duplicate specifications, decisions, prototype contracts, work-item bodies, diffs, or command logs.

## Prepare continuation

1. Update the active work adapter's effort status with the current phase, completed work, available frontier, blockers, and next concrete action. For the local adapter, this is `status.md`.
2. Record the current branch, relevant commits, owned uncommitted paths, and unrelated worktree changes that must remain untouched.
3. Record the latest proven verification commands and their outcomes. Redact secrets and link large evidence rather than embedding it.
4. Link the active work item, specification, settled decisions, accepted prototypes, and unresolved user question when one exists.
5. State which skills the next context should use first.
6. Check every pointer resolves from the repository root.

Keep the user-facing handoff concise: name the current state, next action, and canonical status path.

## Completion

Complete when a fresh Codex context can identify the exact next action, its acceptance checks, its dependencies, the trusted sources, and the worktree boundary without reconstructing prior conversation.
