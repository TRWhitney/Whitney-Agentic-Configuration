# Testing Procedure

Develop each production behavior through a focused red-green-refactor loop. Preserve regression
coverage at a stable public seam without coupling tests to incidental implementation structure.

## Choose the test boundary

Start with one accepted behavior and the highest stable public seam that can demonstrate it.
Prefer an existing seam. Test caller or consumer-visible results, and derive expected values
independently from the production implementation.

For a diagnosed fix, use the focused failing regression test established by diagnosis as the red
boundary. Otherwise write the focused test before changing production code and run it to observe
the expected failure. A test that passes immediately, fails for the wrong reason, or cannot reach
the behavior does not establish the boundary.

## Run the loop

For each behavior:

1. **Red:** Observe the focused test fail for the missing or incorrect behavior.
2. **Green:** Add only enough production behavior to pass it while preserving prior behavior.
3. **Refactor:** Improve names, duplication, boundaries, and dependency injection while the
   focused and affected tests remain green.

Repeat with the next behavior. Correct every red or flaky test encountered; do not finish the
implementation loop with a known failing test.

## Preserve durable coverage

- Name tests for observable capabilities in domain language and keep one behavioral reason to
  fail per test.
- Prefer focused integration coverage at a stable seam over duplicated tests at every layer.
- Replace only system boundaries such as third-party services, nondeterministic time or
  randomness, unavoidable filesystem access, or expensive infrastructure. Do not mock owned
  collaborators or assert call order unless the interaction itself is contractual behavior.
- Avoid broad smoke tests, snapshots too large to explain a failure, and tests whose only purpose
  is proving that removed behavior remains absent.
- Keep the expected result independent from the algorithm used to produce it.

## Result

Include each acceptance behavior, its testing seam, the focused test, and the observed red and
green results. Identify any behavior that still lacks a trustworthy test boundary.
