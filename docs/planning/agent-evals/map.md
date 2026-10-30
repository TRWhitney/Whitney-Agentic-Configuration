# Agent workflow evaluations

## Destination

A growing corpus that measures workflow behavior through shared case infrastructure.

## Notes

[Specification](../../../.work/agent-evals/spec.md).

## Decisions so far

- [Runtime](../../../.work/agent-evals/decisions/01-corpus-and-runner.md): use the official Codex Python SDK.
- [Corpus](../../../.work/agent-evals/spec.md#case-definitions): keep cases as data outside deployed skills.
- [Reuse](../../../.work/agent-evals/spec.md#checks-and-results): share setup, execution, checks, and results.
- [Recovery](../../../.work/agent-evals/spec.md#recovery-and-compaction): seed state for routine runs.
- [Compaction](../../../.work/agent-evals/spec.md#recovery-and-compaction): request and confirm it explicitly in integration runs.
- [Limits](../../../.work/agent-evals/spec.md#execution): report execution limits separately from behavioral failures.

## Not yet specified

None.

## Out of scope

See the [specification](../../../.work/agent-evals/spec.md#out-of-scope).
