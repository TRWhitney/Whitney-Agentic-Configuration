# 01 Save and restore navigation progress

**What to build:** Restore a workflow in a new process without reconstructing its state.

**Blocked by:** none.

**Status:** complete

- [x] Save each conversation's workflow, state, optional substate, and optional work-record link
      under the Codex configuration directory, outside the repository.
- [x] Plain `resume` restores that conversation's guidance and work-record link.
- [x] Missing conversation identity requires an explicit ID instead of selecting another file.
- [x] Separate conversations in the same directory keep independent progress.
- [x] Writes are locked and atomic; failed commands leave the prior progress unchanged.
- [x] Invalid records and stale transition arguments produce errors without resetting progress.
- [x] Completion and cancellation remove only the conversation's navigation file.
- [x] Named-location resume reads guidance without moving the workflow.
- [x] Process restart, concurrent writes, subdirectories, worktrees, projects without Git, and
      absolute work-record links have focused tests.

## Accepted sources

[Save navigation progress and restore through the skill](../spec.md#save-navigation-progress).

## Completion evidence

See [verification](../status.md#verification).
