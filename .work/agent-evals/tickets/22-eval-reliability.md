# 22 Detect and repair faulty evals

**What to build:** A general mechanism for finding evaluation defects and verifying repairs,
so normal completed runs produce clear behavior verdicts.

**Blocked by:** None.

**Status:** complete

- [x] Separate omitted required behavior, unavailable evidence, and ambiguous expectations.
- [x] Check that an eval accepts different valid approaches and rejects actual violations.
- [x] Verify that required behavior is observable through the available capture mechanisms.
- [x] Enforce and probe per-attempt read/write/network boundaries; exclude contaminated trials.
- [x] Diagnose unresolved judgments before attributing them to subject guidance.
- [x] Provide read-only diagnosis and reassessment commands that preserve original judgments.
- [x] Verify repairs with retained regression examples and fresh runs where evidence is missing.
- [x] Exercise the mechanism on the existing prototype and interface inspection uncertainties.

## Accepted design

Before this change, calibration disagreements did not fail the command, examples lacked action
records, and uncertain judgments did not identify their cause. The accepted implementation
extends those interfaces with action records, recording coverage, explicit causes and reviewed
reassessment.

Enforcement builds on those interfaces: make calibration disagreement fail, include
action-based calibration, and identify why an assessment cannot reach a verdict. An omitted
required action can fail when its occurrence was observable and the relevant record is complete.
Unavailable observations require capture repair; unclear expectations require criterion review.
Judge disagreement triggers investigation, not a majority-vote replacement for evidence.

Keep earlier attempts distinct when changing expectations. Reassess unchanged recorded work
when sufficient evidence survives; otherwise rerun after the repair. Verify shared corrections
against affected cases and preserve genuine agent failures.

## Accepted sources

[Specification](../spec.md#eval-reliability).
[Authoring standards](../../../docs/eval-authoring.md#check-the-assessor).
[Current uncertainties](../../../docs/research/interface-prototype-trials.md#reviewed-wording).

## Completion evidence

Implementation and validation are complete. Offline regressions cover capture boundaries,
recording classification, calibration enforcement, preserved judgments and reassessment.
Independent reviews exposed reassessment paths that ignored expectation defects and archived
assessment failures. Both now have passing regressions. The [trial study](../../../docs/research/eval-reliability-trials.md)
preserves calibration disagreements, excluded attempts and original case judgments.
All 489 framework tests, lint, formatting, strict typing, JavaScript syntax and all 151 case
definitions pass. All 18 revised editability calibration judgments agree. Final inspected
outcomes are six correct and three verification omissions, with no unknown
behavior; all nine assessments completed. All three clarified GUI attempts pass independent
evidence inspection.

## Case expectations

Visual comparison requires opening both the finished application and the accepted prototype
in a browser. Reading prototype source and written requirements alone does not establish the
required comparison. All three fresh attempts pass the clarified private criterion.

Blank-name feedback must leave the name editable. Interaction or equivalent runtime evidence
can verify that behavior without a fixed sequence. Verified prototype repeat 3 checks only the
open dialog, error and summary, then cancels; it never establishes post-error input editability.
The implementation flows pass, while required candidate verification remains incomplete.
The clarified calibration accepts equivalent runtime inspection in all three repeats.
Finished raw evidence was deleted after inspection and required review.
