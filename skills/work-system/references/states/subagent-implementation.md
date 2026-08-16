# Subagent Implementation State

Turn one accepted assignment into a coherent, maintainable repository change within its stated
authority. This state owns the assigned production changes, supporting tests, and named checks. It
does not choose missing intent or enlarge the assignment.

## Establish the assignment

Begin from the observable result, acceptance checks, accepted sources, writable paths, named
checks, and the supplied test boundary when behavior changes. Inspect the existing seams needed to
understand and implement that result cleanly.

Confirm that the assignment is internally consistent and that its writable scope contains the
change it requires. When a source, check, or boundary is missing, contradictory, or no longer
feasible, preserve the supported facts and identify the exact gap. Do not reinterpret the accepted
result, add adjacent work, or modify paths outside the assignment.

Preserve unrelated work already present in the repository. Keep Git inspection read-only: do not
stage, commit, change branches, rewrite history, discard changes, or otherwise mutate repository
state through Git.

## Build the result

For behavior-changing work, use the required testing procedure as the implementation loop. Confirm
the supplied test boundary before changing production behavior, then keep the focused and named
checks green while the implementation evolves.

Refactor within the assigned code and its directly coupled seams when doing so leaves the result
clearer, more cohesive, or easier to maintain. Preserve behavior outside the assignment. Keep
domain behavior separate from presentation concerns, make varying collaborators explicit, retain
precise types, and preserve actionable failure causes. Use established dependencies when they fit,
and add abstractions only for accepted behavior or demonstrated variation.

Integrate every layer needed for the assigned observable result. Do not stop at an internal
mechanism when the acceptance checks require consumer-visible behavior. Run the named checks until
they pass, and investigate any failure that may have been caused by the assigned changes.

## Continue

Use the `implemented` route when the assigned result is complete, its focused and named checks
pass, every change remains within the writable scope, and no known defect remains in the result.

Use the `assignment-blocked` route when missing authority, contradictory sources, an invalid test
boundary, an unavoidable scope conflict, or unavailable evidence prevents trustworthy completion.
State the exact blocker and preserve valid work without expanding the assignment.
