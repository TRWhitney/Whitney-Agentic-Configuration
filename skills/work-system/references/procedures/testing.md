# Testing Procedure

Develop each production behavior through a focused red-green-refactor loop. Keep regression
tests at a stable public interface. Test behavior rather than code structure.

## Choose what to test

Start with one accepted behavior and the highest stable public interface that can demonstrate
it. Prefer an existing interface. Test caller or consumer-visible results, and derive expected
values independently from the production implementation.

For a diagnosed fix, use the regression check chosen during diagnosis. During implementation,
write or reuse a focused regression test and confirm that it fails for the diagnosed behavior
before changing production code. For other behavior-changing work, derive the test from the
accepted behavior and confirm the expected failure before changing production code. A test that
passes immediately, fails for the wrong reason, or cannot reach the behavior does not prove the
test covers the change.

## Run the loop

For each behavior:

1. **Red:** Observe the focused test fail for the missing or incorrect behavior.
2. **Green:** Add only enough production behavior to pass it without changing other behavior.
3. **Refactor:** Improve names, duplication, boundaries, and dependency injection while the
   focused and affected tests remain green.

Repeat with the next behavior. Correct every red or flaky test encountered; do not finish the
implementation loop with a known failing test.

## Keep useful regression tests

- Name tests for observable capabilities in domain language and keep one behavioral reason to
  fail per test.
- Prefer focused integration coverage at a stable interface over duplicated tests at every
  layer.
- Replace only system boundaries such as third-party services, nondeterministic time or
  randomness, unavoidable filesystem access, or expensive infrastructure. Do not mock this project's components or assert call order unless the interaction itself is contractual
  behavior.
- Avoid broad smoke tests, snapshots too large to explain a failure, and tests whose only
  purpose is proving that removed behavior remains absent.
- Do not match human-authored prose in tests unless its exact wording is itself contractual.
  Test behavior or structured contracts instead.
- Keep the expected result independent from the algorithm used to produce it.

## Result

Include each acceptance behavior, the interface tested, the focused test, and the observed red
and green results. Identify any behavior that still lacks a test that reliably checks it.
