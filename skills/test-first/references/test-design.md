# Test design

## Durable tests

- Name observable capabilities in domain language.
- Exercise public interfaces and assert externally meaningful results.
- Derive expected values independently from the implementation.
- Keep one behavioral reason to fail per test.
- Prefer integration-style coverage at a stable seam over duplicated tests at every internal layer.

## Doubles

Use dependency injection and replace only system boundaries such as third-party APIs, nondeterministic time or randomness, unavoidable filesystem access, or expensive infrastructure. Prefer real controlled databases when practical. Avoid mocking owned internal collaborators or asserting call order unless the order itself is contractual behavior.

## Warning signs

- A refactor breaks a test while behavior is unchanged.
- The expected value recomputes the same algorithm as production.
- The test reaches around the public interface to inspect internal storage.
- Tests are written in a horizontal batch before any slice runs end to end.
- Snapshot size hides which behavior matters.
