# Restore workflow state and finish planning before implementation

## Problem Statement

The navigator prints guidance but does not save the active workflow or state. After context
compaction, an agent must reconstruct both before it can load the right instructions. Loading
wayfinding also leaves no saved indication that its discussion and response format remain active.

Planning currently permits implementation once one part is specified, while design and tickets
for the rest of the effort can remain unfinished. GitHub planning has no route for reviewing
and merging repository documents before implementation starts.

## Solution

Save navigation progress, restore it through the skill, and let planning declare optional
substates. Wayfinding is the first substate. Finish the full design and ticketing, then deliver
planning documents before starting implementation.

## User Stories

1. As someone continuing a long discussion, I want the agent to restore the current question
   and response format after context compaction.
2. As someone planning a feature, I want research to return to the discussion it serves.
3. As someone reviewing a design, I want the full design, tickets, and planning documents
   finished before implementation starts.

## Implementation Decisions

### Save navigation progress

The work-system navigator saves a record when a workflow starts or moves, a substate is entered
or left, or a workflow completes. The record contains a version, identifier, checkout path,
status, workflow, state, optional substate, and optional work-record path or URL. Status is
`active`, `complete`, or `cancelled`. Requirements, decisions,
and the next task stay in the existing work record.

Store records under the checkout's Git metadata, using Git to locate that directory. A project
without Git uses `.work/navigation/`. The installed skill directory stores no project progress.
Write records atomically. Failed commands leave the previous record unchanged. Invalid or
outdated records produce an error rather than silently starting another workflow.

Each record has a generated identifier. A conversation ID supplied by the environment may
associate commands with a record, but is not required. Without that association, restore the
only active record for the checkout. If several exist, list their work-record links and exact
resume commands; require an explicit selection. Never select a record by its modification time.
Use a lock when creating or changing records so simultaneous commands cannot overwrite progress.

`start <workflow>` starts a record only when no active record has been selected. Repeating it
for the selected workflow restores that record. Starting another workflow requires completing
the current one or explicitly creating another record with `--new-session`. Replacing an active
record is not an implicit effect of starting work.

`cancel` closes the selected navigation record when the effort is cancelled. It does not mark
the effort complete or remove its work record. Failed or cancelled work remains distinguishable
from completed work when selecting records.

Add `--session <id>` to navigation commands and `--record <path-or-url>` to `start`. Printed
continuation commands include the record identifier. Paths remain relative to their checkout
when possible. An explicitly selected record from another checkout is rejected.

### Restore through the skill

`resume` without workflow and state arguments selects the saved record and loads its current
state, provider guidance, required procedures, active substate, and that substate's formats.
It also prints the work-record link so the agent can read the current question and next task.
No active record produces a clear result and leaves workflow selection to the skill.

Keep `resume <workflow> <state>` for reading guidance at a named location. It does not move a
saved workflow. When that location differs from the selected record, label the output as guidance
for another location and print the command that restores the active record.

The global instructions direct the agent to read the work-system skill after context
compaction. The skill supplies the restore command. Existing state and procedure files supply
the restored guidance; there is no second copy in the saved record.

### Optional substates

A workflow state may declare named substates with their guidance, entry cue, related procedures,
and formats. Entry is optional. A substate does not add a mandatory workflow stage or change
the parent state's permitted procedures and routes. Only one substate is active at a time.

`substate enter <name>` enters a substate declared by the selected state. Re-entering the same
substate restores it. Entering a different one requires leaving the first.
`substate leave` returns to the parent state. A move out of the parent state is rejected while
a substate remains active. Completion closes its navigation record so plain resume no longer
selects it as active work.

Wayfinding moves from the planning procedure list to the optional substate list. Keep its
existing decision map, feature records, progress line, and discussion format. Its questions
cover the full agreed scope. Research, prototypes, and record updates do not replace or end it.
Their displayed return command restores the parent state and active substate. Other procedures
remain procedures, and states without substates retain their existing behavior.

### Finish planning

Planning covers the full agreed scope. All required product and architecture decisions and all
implementation tickets must be settled before implementation starts. The first useful result
can order discussion and tickets, but cannot shorten the design scope. Scope changes require
agreement. A ticket with no dependencies does not bypass planning.

Add a `planning-delivery` state between planning and implementation. It checks the specification,
ticket coverage, supporting documents, links, and required review. It permits document corrections,
review, and commits. Design findings return to planning. It never permits production implementation.

For GitHub tracking, publish required repository documents through a planning PR and wait for
its merge. Keep specifications and tracking records in their owning issues. If no repository
document changes, record that result instead of creating an empty PR. Leave merging to Whitney.
Closing an unmerged PR keeps implementation blocked. After merge, check that review changes have
reached the design and affected tickets before moving to implementation.

For local tracking, commit the specification, tickets, and supporting planning documents after
review. Delivery of implementation continues to use the existing delivery state.

The navigator enforces available routes and the active substate. Agents check design and ticket
coverage against the work record; a saved state alone does not prove that either is complete.

## Testing Decisions

Exercise the CLI in temporary Git repositories and standalone skill installations. Check saved
records and command results rather than exact prose.

- Start a workflow, end the process, and restore it in a new process.
- Enter wayfinding, load research, and restore wayfinding and its format.
- Reject unknown substates, stale transitions, ambiguous selection, invalid records, and writes
  that would replace another active record. Failed commands preserve the saved state.
- Check separate conversations, subdirectories, Git worktrees, and projects without Git.
- Verify that planning reaches planning delivery before implementation and that unresolved
  planning can return for correction.
- Preserve provider selection, existing procedure access, standalone installation, deployment,
  and note-system behavior.

## Out of Scope

Automatic hook installation, changes to T3, deployment into the live Codex home, new note-system
behavior, and automatic judgment that a design is complete are outside this change. Recovery
depends on the global compaction instruction being present and followed.

## Further Notes

Implementation order and acceptance checks are in the [tickets](status.md#frontier).
