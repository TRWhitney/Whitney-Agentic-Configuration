# 01 Corpus and conversation runner

**Status:** resolved
**Blocked by:** none
**Type:** research

## Questions

Which runtime can exercise native conversations and compaction? What belongs in shared
infrastructure? How can recovery stay inexpensive as the corpus grows?

## Accepted answers

Use the Codex Python SDK for the first runtime. Reuse case setup, conversation control, checks,
and results. Store case-specific inputs and expectations as data. Keep seeded recovery in the
routine suite and confirmed native compaction in a separately selected integration case.
Use deterministic checks for the starting corpus. Keep every required failure visible.

The [specification](../spec.md) defines the complete behavior and initial cases.

## Evidence

[Tool comparison](../../../docs/research/agent-evaluations.md).
