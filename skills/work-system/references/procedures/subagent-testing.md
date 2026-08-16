# Subagent Testing Procedure

Preserve the focused test boundary while developing the assigned change. Keep regression coverage
at a stable public seam without changing accepted checks or expanding the assignment.

## Confirm the boundary

For behavior-changing work, run the supplied focused test before changing production behavior and
confirm that it fails for the expected reason. Treat a missing test, an unexpected pass, or a
different failure as an assignment blocker rather than replacing the boundary.

For behavior-preserving work, identify the named checks that cover the affected seam and establish
their passing baseline. Do not manufacture a failing test for behavior that is intended to remain
stable.

Use the highest stable public seam already established by the supplied test or named coverage. Keep
expected values independent from the production implementation and keep each test focused on one
observable behavior.

## Run the loop

For each assigned behavior:

1. **Red:** Confirm the supplied focused failure.
2. **Green:** Add enough production behavior to satisfy the accepted result.
3. **Refactor:** Improve the involved structure while the focused and named checks remain green.

Correct every failing or flaky test caused by the assigned changes. Preserve durable coverage at a
stable seam, avoid mocking owned collaborators, and do not couple tests to incidental call order or
implementation structure.

For work that does not change behavior, make the assigned change while its affected and named
checks remain green.

## Run the assignment checks

Run each named check after the assigned change meets its focused boundary. Do not substitute a
narrower check or add broader checks that the assignment does not require. Record exact commands
and concise outcomes, including any check that cannot run.

## Result

Include the focused test boundary and baseline result, the red and green results when behavior
changed, every named check and its outcome, and any blocker that prevents trustworthy completion.
