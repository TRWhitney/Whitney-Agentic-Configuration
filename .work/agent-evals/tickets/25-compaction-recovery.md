# 25 Recover work after compaction

**What to build:** Restore the active workflow and existing work record after compaction in
Codex and Claude Code through a shared command.

**Blocked by:** None.

**Status:** complete

- [x] Preserve current decisions and next work in the existing record before compaction.
- [x] Recover the same conversation, workflow, substate and record through either application's hook.
- [x] Keep unrelated conversations, damaged state and evidence awaiting review intact.
- [x] Configure either application without replacing its other settings or hooks.
- [x] Confirm native Codex compaction and repeat final affected cases and controls three times.
- [x] Test Claude's documented configuration and input contract; report native execution separately.

## Accepted sources

- [Specification](../spec.md#compaction-hooks)
- [Authoring standards](../../../docs/eval-authoring.md)
- [Earlier compaction finding](../../../docs/research/evaluation-failures.md#earlier-failures-followed-by-a-pass)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks#sessionstart)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks#sessionstart)
- [Claude session identity](https://code.claude.com/docs/en/env-vars)

## Verification

The [study](../../../docs/research/compaction-recovery-trials.md) records all 81 primary
assessments, five calibration judgments, three frozen-output audits and 62 comparison judgments.
The final twelve attempts meet the selected criteria, three per case/control. Final blinded comparisons agree.
All nine final native compactions restore the original record; the agent reads it before
continuing. The changed planning answer and pending review evidence survive recovery.

All six applied skill files match the tested V7 source. Proposal reversal and skill validation
pass. The applied package initially fails its old file-inventory assertion; the expected setup
guide is added and all 83 affected checks pass. All 510 framework tests pass. All 154
definitions, 267 local links/anchors, lint, formatting and typing checks pass. Focused red/green
checks cover setup, restoration, record binding and capture alignment.

Claude Code is unavailable locally. Its native compaction, automatic compaction thresholds and
context clearing remain unverified. Configuration and input-contract tests pass for both
applications.

## Review and completion

Independent intent and engineering reviews pass. Intent review records an ungraded observation:
V7 agent-created attempts 2 and 3 acknowledge an answer without the next question before
compaction, despite the reply command rejecting its absence. Both preserve the answer and ask
the pending question after recovery. This limits broader wayfinding claims and does not block
the accepted compaction outcome.

Raw evidence was inspected, reviewed and deleted. The full corpus was not rerun.
