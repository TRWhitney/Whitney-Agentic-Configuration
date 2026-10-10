# Delegate Procedure

Delegate a bounded outcome when fresh context or parallel execution helps. Remain responsible
for scope and integration.

## Define the assignment

Give the subagent one independently completable outcome. Include:

- The observable result and its acceptance checks.
- Accepted decisions and source artifacts needed to act without rediscovery.
- Genuine blockers and dependencies.
- Explicit writable file scope.
- The existing tests or other checks the subagent must make pass.
- Discard-by-default retention rules and any exceptions I explicitly requested. Generate raw
  outputs outside the checkout, return concise findings, and identify temporary evidence needed
  for integration or required review. The owner deletes it when that need ends, before delivery.

Provide the accepted ticket, relevant artifact paths, and the context needed to interpret them.
Exclude unrelated history and unresolved reasoning. Do not delegate work whose outcome,
authority, or writable scope cannot be bounded.

Include the exact navigator command that starts `subagent-implementation`. That command
establishes the workflow context for the assignment.

For behavior-changing work, delegate only after its focused test has failed for the expected
reason. The subagent implements the assigned behavior; it does not establish the test-first
boundary on the delegating agent's behalf.

## Protect ownership

- Give each change and writable path one owner at a time.
- Do not delegate overlapping scopes in parallel or modify a delegated scope while it is active.
- Delegate only unblocked work and sequence dependent assignments.
- Restrict the subagent to read-only Git inspection. It must not stage, commit, change branches,
  rewrite history, discard changes, or otherwise mutate repository state through Git.
- Require the subagent to report scope gaps, conflicts, or invalid assumptions instead of
  silently expanding its authority.

## Integrate the result

Have the subagent run the named assignment checks until they pass. Do not ask it to add broader
coverage or perform unassigned linting, type checking, or validation. Passing checks supports
only the bounded result; it does not validate the integrated outcome.

Inspect the returned changes and check results against the assignment. Do not accept a completion
summary as proof. Resolve integration issues and preserve unrelated work.

Treat work discovered outside the assignment as a new bounded outcome rather than silently
absorbing it into the delegation.

## Result

Include the completed outcome, changed paths, named check results, and any remaining uncertainty
or blocker.
