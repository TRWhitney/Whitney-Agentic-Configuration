# 03 Exercise recovery and explicit compaction

**What to build:** Verify wayfinding recovery with shared fixtures and checks.

**Blocked by:** [Native runs](02-native-runs.md).

**Status:** done

- [x] Seeded progress uses the navigator and actual conversation ID before a fresh agent receives a short handoff.
- [x] Routine recovery checks the linked question, response format, and saved substate.
- [x] The integration step compacts the same native conversation and waits for its matching completion event.
- [x] An acknowledgement alone, failure, or timeout cannot pass the compaction case.
- [x] Ordinary selection never triggers compaction; no case fills a context window.

## Accepted sources

[Specification](../spec.md).

## Completion evidence

[Checks and measured observations](../status.md#verification).
