---
name: implement-work
description: Use when a request, specification, or ready work item has settled acceptance checks and is ready for production implementation.
---

# Implement Work

Execute the smallest ready production slice through its selected completion profile, then continue the work frontier automatically.

## Ownership

Own production edits, completion-profile fidelity, frontier execution, remediation, and logical commits. Delegate development tests to `$test-first`, durable knowledge to `$document-change`, completion proof to `$verify-change`, and risk-based assessment to `$review-change`.

## Execute one item

1. Load the active acceptance checks, dependencies, accepted sources, repository instructions, and the `focused-production` or `full-production` completion profile selected by `$manage-work`.
2. Inspect the worktree. Preserve unrelated user changes and define the files or hunks this item owns.
3. Mark the item active and state its concrete acceptance checks before production edits.
4. Use `$test-first` for each behavioral vertical slice. Treat an accepted prototype and its contract as binding sources, not loose inspiration. Rebuild production behavior under normal quality constraints rather than promoting untested prototype code.
5. Keep the change within the active outcome. Record unrelated opportunities without expanding scope.
6. Use `$document-change` to perform the documentation-impact pass without creating documentation solely to narrate a focused tweak.
7. Use `$verify-change` to prove the exact acceptance checks under the selected profile.
8. Apply risk-based review. For `focused-production`, perform a concise intent and engineering pass locally unless a concrete risk warrants `$review-change`. For `full-production`, use `$review-change`; request clean-context reviewers only when repository instructions and user authority permit them. Fix objective defects automatically, rerun affected verification, and repeat review where remediation was material. Ask the user only when a finding requires a new product, UX, architecture, or scope decision.
9. Record completion evidence and mark the item complete in the durable work record.
10. Commit only the item's owned changes, including that record update, after all gates are green. Follow repository commit conventions and do not include unrelated worktree changes.

## Continue the frontier

Select the next ready item and repeat without requiring another user command. If no item is ready, identify the actual blocker. Use `$handoff-work` when a context boundary arrives before the frontier is empty.

Do not commit while significant assumptions await user confirmation, accepted visual behavior is unverified, or review has unresolved objective defects.

## Completion

Complete when the direct request or every planned item has green proof under its completion profile, the required review is clean, durable documentation is current, logical commits contain only owned changes, and the active work record has no unfinished in-scope item.
