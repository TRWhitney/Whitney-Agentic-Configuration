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

Save one file per conversation under `<Codex home>/work-system/state/`. Derive its filename from
the conversation ID using SHA-256 so IDs that differ only in letter case keep separate files.
Use `CODEX_HOME` when set, or `.codex` under the home directory. The file contains the workflow
and state, with substate and work-record link only when present. Save local links as absolute
paths and preserve issue URLs. Requirements, decisions, and the next task stay in the linked
work record.

Use `CODEX_THREAD_ID` to identify the conversation. When it is unavailable, require
`--conversation <id>`. A session ID may be shared by related conversations and must not select
their progress. Explicit conversation arguments also appear in printed continuation commands.
Restoration reads only that conversation's file.

Save progress when a workflow starts or moves, or a substate is entered or left. Write atomically
and lock each conversation's file while reading or changing it. Failed commands leave the
previous progress unchanged. Invalid saved progress produces an error instead of a reset.

`start <workflow>` creates progress only when that conversation has none. Repeating it for the
active workflow restores its state. Complete or cancel that workflow before starting another.
Completion and `cancel` remove the navigation file. Neither removes the linked work record.
Use `--record <path-or-url>` with `start` to attach or update that link.

### Restore through the skill

`resume` without workflow and state arguments reads the conversation's file and loads its current
state, provider guidance, required procedures, active substate, and that substate's formats.
It also prints the work-record link so the agent can read the current question and next task.
No active record produces a clear result and leaves workflow selection to the skill.

Keep `resume <workflow> <state>` for reading guidance at a named location. It does not move a
saved workflow. When a workflow is active, label the output as guidance
for a named location and print the command that restores the active record.

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
a substate remains active. Completion removes its navigation file so plain resume no longer
restores it as active work.

Wayfinding moves from the planning procedure list to the optional substate list. Keep its
existing decision map, feature records, progress line, and discussion format. Its questions
cover the full agreed scope. Research, prototypes, and record updates do not replace or end it.
Their displayed return command restores the parent state and active substate. Other procedures
remain procedures, and states without substates retain their existing behavior.

### Finish planning

Finish the full design and write all implementation tickets before starting implementation.
Tickets cover the accepted design and leave no product or architecture decision for the
implementing agent to invent. A ticket with no dependencies does not bypass unfinished planning.

Keep the direct planning-to-implementation route. For GitHub tracking, expose the review,
commit, and publishing procedures from planning. Deliver changed repository planning documents
through a PR and remain in planning until it merges. Keep specifications and tracking records
in their owning issues. If no repository document changes, record that result instead of
creating an empty PR. After merge, check that review changes reached the affected records.

Local tracking retains its existing commit timing: effort records remain uncommitted while
active and are committed with the completed outcome. Publication requirements belong to the
GitHub provider and do not add a shared workflow state.

The navigator enforces available routes and the active substate. Agents check design and ticket
coverage against the work record; a saved state alone does not prove that either is complete.

### Keep the current task separate from the workflow being changed

The current repository setting selects its tracker. Discussing or editing GitHub tracking does
not select GitHub for that task. The navigator displays the selected tracker with state guidance.
Tracker setup is used only when Whitney explicitly sets or changes the repository tracker.
Publishing through GitHub requires that selection or a direct request to publish the current work.

## Testing Decisions

Exercise the CLI in temporary Git repositories and standalone skill installations. Check saved
records and command results rather than exact prose.

- Start a workflow, end the process, and restore it in a new process.
- Enter wayfinding, load research, and restore wayfinding and its format.
- Reject unknown substates, stale transitions, invalid records, missing conversation identity,
  and writes that would replace an active workflow. Failed commands preserve the saved state.
- Check separate conversations in the same directory, concurrent commands, subdirectories,
  Git worktrees, projects without Git, and absolute work-record links.
- Verify the direct planning-to-implementation route and provider-specific access to planning
  publication procedures.
- Preserve provider selection, existing procedure access, standalone installation, deployment,
  and note-system behavior.

## Out of Scope

Automatic hook installation, changes to T3, deployment into the live Codex home, new note-system
behavior, and automatic judgment that a design is complete are outside this change. Recovery
depends on the global compaction instruction being present and followed.

## Further Notes

Implementation order and acceptance checks are in the [tickets](status.md#frontier).
