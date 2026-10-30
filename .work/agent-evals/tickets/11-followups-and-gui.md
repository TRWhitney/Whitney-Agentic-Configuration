# 11 Assess GUI verification and pending follow-ups

**What to build:** Reusable browser evidence and task cases for the accepted GUI behaviors,
with the four accepted follow-up behaviors.

**Blocked by:** None.

**Status:** complete

- [x] Cover accepted design, browser rendering, transitions, combined conditions, alignment,
  grouping, content changes, wrapping, and evidence supporting completion claims.
- [x] Include a correct audit control and ordinary prompts without hidden-defect reminders.
- [x] Assess images and measurements while distinguishing candidate actions from private checks.
- [x] Extend result-attempt reporting and wording-question coverage; add pending-conversation and
  supplied-input retention cases.
- [x] Validate fixtures against known correct and defective versions, run live tasks, inspect
  outputs, record failures and limits, and remove finished raw outputs.

## Accepted sources

[Specification](../spec.md#gui-verification-and-follow-up-coverage).
[Authoring standards](../../../docs/eval-authoring.md).

## Completion evidence

All 368 infrastructure tests pass, with lint, strict typing, formatting, 130 case definitions,
and JavaScript syntax checks. Browser comparisons reject five defective implementations and
accept their corrected reference versions. Font variation, real label wrapping, failed-capture
retention, image views, project browser access, and packet recovery have focused coverage.
[Live results](../../../docs/research/gui-verification-evals.md) preserve every case attempt,
excluded setup, assessment revision, confirmed failure, and limit. Five GUI implementation
cases pass. Two full audits have useful outputs but no completed independent verdict within
the recorded allowances. Independent intent and engineering correction reviews pass; the
packet review has no blocking finding. Small server cleanup and image-index size corrections
were inspected by the parent.
