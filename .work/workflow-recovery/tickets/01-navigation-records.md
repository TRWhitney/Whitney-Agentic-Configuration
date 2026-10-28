# 01 Save and restore navigation progress

**What to build:** Restore a workflow in a new process without reconstructing its state.

**Blocked by:** The planning PR must merge before implementation starts.

**Status:** blocked

- [ ] Workflow start, move, and completion save navigation progress under project metadata.
- [ ] Plain `resume` restores the selected record and provider guidance, or reports no active work.
- [ ] Printed continuation commands select the same record explicitly.
- [ ] Multiple records require a selection when the conversation cannot be identified.
- [ ] Separate conversations and checkouts cannot overwrite one another's progress.
- [ ] Writes are locked and atomic; failed commands leave the prior record unchanged.
- [ ] Invalid records and stale transition arguments produce errors without resetting progress.
- [ ] Cancellation closes navigation progress without marking the effort complete.
- [ ] Named-location resume remains available for reading guidance without moving the workflow.
- [ ] Process restart, ambiguous selection, concurrent writes, subdirectories, worktrees, and
      projects without Git have focused tests.

## Accepted sources

[Save navigation progress and restore through the skill](../spec.md#save-navigation-progress).

## Completion evidence

Pending implementation.
