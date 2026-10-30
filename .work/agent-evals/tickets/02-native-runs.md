# 02 Run isolated native conversations

**What to build:** Execute selected cases through the official SDK and report measured outcomes.

**Blocked by:** [Case definitions](01-case-definitions.md).

**Status:** done

- [x] The SDK dependency is optional and pinned; existing Codex file credentials are reused in disposable homes.
- [x] Shared setup copies subject instructions and creates isolated Git projects and local service fixtures.
- [x] Messages run in the selected native conversation; checks consume structured replies, files, calls, state, and Git history.
- [x] Time limits, observed-token limits, failed turns, and missing usage produce explicit outcomes.
- [x] Cleanup removes temporary projects, credentials, and raw runtime records on success and failure.
- [x] Offline adapter tests and one short native run establish execution and reporting.

## Accepted sources

[Specification](../spec.md).

## Completion evidence

[Checks and measured observations](../status.md#verification).
