# Subagent Implementation State

Build the assigned change, its tests, and named checks within the permitted scope. Do not invent
missing requirements or expand the assignment.

## Check the assignment

Start with the requested result, acceptance checks, agreed sources, writable paths, named
checks, and supplied test when behavior changes. Inspect the affected code and interfaces.

Check that these instructions agree and the permitted paths allow the required change. If a
source, check, or permission is missing, contradictory, or impossible to follow, report what you
found and what you need. Do not change the requested result, add adjacent work, or edit other
paths.

Leave unrelated file contents unchanged. Keep Git inspection read-only. Do not stage, commit,
change branches, rewrite history, discard changes, or otherwise change Git state.

## Build the result

When changing behavior, use the required testing procedure. Check the supplied failing test
before changing production code, then keep the focused and named checks passing as you build.

Refactor the assigned code and directly connected interfaces when it makes the result clearer or
easier to maintain. Keep other behavior unchanged. Separate domain logic from presentation,
inject dependencies that may vary, use precise types, and keep error causes available for
diagnosis. Reuse suitable dependencies and add abstractions only for required behavior or
existing variation.

Connect all layers needed for the user-visible result. Run the named checks until they pass and
investigate failures that your changes may have caused.

## Continue

Use `implemented` when the assigned result is complete, focused and named checks pass, all
changes are within the permitted paths, and no known defect remains in the result.

Use `assignment-blocked` when missing permission, conflicting sources, an invalid supplied test,
files you cannot edit, or unavailable checks prevent completion. Report the exact blocker and
leave correct work in place without expanding the assignment.
