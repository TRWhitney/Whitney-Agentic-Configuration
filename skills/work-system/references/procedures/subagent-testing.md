# Subagent Testing Procedure

Use the supplied test to guide the assigned change. Keep regression tests at a stable public
interface without changing agreed checks or expanding the assignment.

## Check the supplied tests

For behavior-changing work, run the supplied focused test before changing production behavior
and confirm that it fails for the expected reason. Treat a missing test, an unexpected pass, or
a different failure as an assignment blocker rather than choosing a different test.

For work that keeps behavior unchanged, identify the named checks that cover the affected
interface and establish their passing baseline. Do not manufacture a failing test for behavior
that is intended to remain stable.

Use the highest stable public interface already established by the supplied test or named
coverage. Keep expected values independent from the production implementation and keep each test
focused on one observable behavior.

## Run the loop

For each assigned behavior:

1. **Red:** Confirm the supplied focused failure.
2. **Green:** Add enough production behavior to satisfy the accepted result.
3. **Refactor:** Improve the involved structure while the focused and named checks remain green.

Correct every failing or flaky test caused by the assigned changes. Keep regression tests at a
stable interface, avoid mocking this project's components, and do not couple tests
to incidental call order or implementation structure.

For work that does not change behavior, make the assigned change while its affected and named
checks remain green.

## Run the assignment checks

Run each named check after the assigned change passes its focused tests. Do not substitute a
narrower check or add broader checks that the assignment does not require. Record exact commands
and concise outcomes, including any check that cannot run.

## Result

Include the supplied test and its initial result, the red and green results when behavior
changed, every named check and its outcome, and any blocker that prevents completion.
