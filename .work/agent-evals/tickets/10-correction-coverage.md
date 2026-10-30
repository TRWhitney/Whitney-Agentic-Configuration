# 10 Assess corrections and judgment boundaries

**What to build:** Stronger follow-up tasks and assessor examples for the recorded gaps in
correction behavior and judgment.

**Blocked by:** None.

**Status:** complete

- [x] Extend the existing narrow wording case across successive edits without losing accepted text.
- [x] Require retained quantity regression coverage in both amendment turns.
- [x] Extend the existing verification-to-guide case with an existing draft and a layout correction.
- [x] Add independently labeled equivalent-result, planning-authorization, and file-permission examples.
- [x] Pass replies and artifacts through the shared blinded calibration runner without labels.
- [x] Inspect all three live cases and all calibration examples; retain each outcome and limitation.

## Accepted sources

[Specification](../spec.md#corrections-and-assessment-examples).
[Authoring standards](../../../docs/eval-authoring.md).
[Recorded assessment gaps](../../../docs/research/evaluation-methods.md#limits-and-next-work).

## Completion evidence

All 354 tests pass, along with lint, typing, formatting, and validation of all 121 definitions.
Observed red checks covered missing reply evidence, missing case extensions and examples, and
the missing targeted regression interface. The targeted check then accepted retained quantity
coverage and rejected a suite testing only the later message. The final wording check also
rejects loss of the earlier accepted edit.
[Live results](../../../docs/research/correction-and-judgment-evals.md) retain every run,
criterion gap, interrupted assessment, and calibration disagreement. The third wording turn
remains unverified after the run reached its token allowance. Independent intent review and
engineering correction review pass. The regression test distinguishes the old-message baseline
from the targeted faulty source, including a baseline-only control that exposes the unrelated
message assertion.
