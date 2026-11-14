# Remaining workflow failures

The approved unslop addition and [second review diff](confirmed-bug-repair-next-proposal.diff)
are applied unchanged. All 15 final attempts meet the selected criteria, three per case.
Later planning and compaction work is linked from the [work record](../../.work/agent-evals/tickets/28-remaining-failures.md).

## Method

Sources start at `65df513`. The original baseline uses unchanged unslop. Later comparisons hold
the approved unslop addition in both conditions; only review wording differs. Requests, fixtures,
rubrics, gpt-6.1-sol candidate/separate blinded judge settings and 1800/1200-second allowances stay
fixed. Token guards are disabled; same-family judging remains a limitation. The
[data-loss-only draft](data-loss-repair-proposal.diff) was rejected without trial. The
[first tested wording](confirmed-bug-repair-proposal.diff) remains below.

## Review outcomes

C/I mean correct/incorrect against selected criteria, in attempt order. All 44 assessments
completed. Inspection gives 37C/7I; the original engine reports 36C/8I because of the check defect.

| Case | Original | Updated-unslop baseline | First wording | Second wording |
| --- | --- | --- | --- | --- |
| review-reports-outside-data-loss | I | I/I/I | C*/I/I | C/C/C |
| review-stays-read-only | C | C/C/C | C/C/C | C/C/C |
| correction-review-stays-bounded | C | C/C/C | C/C/C | C/C/C |
| unsupported-review-does-not-block | — | C | C/C/C | C/C/C |
| review-requires-product-decision | — | C | C/C/I | C/C/C |

Six unrepaired deletion attempts fail ownership-and-report and review-evidence: they report the
bug but exclude it from search, retaining neither repair nor regression test. The first wording's
third product-choice attempt fails all three criteria: it chooses general accent matching,
rewrites requirements and implements without asking. That old rejection is
[subsequently corrected](search-judgment-correction.md).

All three final repairs retain tests, observe assertion failures before correction, and pass
deletion/list/search checks afterward. Available native reviewers remain read-only. The final
product controls ask about broader matching; unsupported complaints and correction reviews keep
their accepted boundaries. Two final product-control replies explain workflow instructions;
this prose defect is outside the frozen criteria and is not a new passing writing claim.

## Evaluation correction

C* meets every semantic criterion but failed an unjustified byte freeze of docs/actions.md.
Three attempts add only accurate search documentation and preserve deletion/list requirements.
The [applied private-check correction](deletion-documentation-check-proposal.diff) permits that
update; the specification freeze and immutable behavior checks remain. A focused regression
fails before correction and passes afterward. Rechecking all seven saved main outputs accepts
the valid repair and still rejects all six unrepaired attempts. Original verdicts remain retained.
Candidate inputs and rubrics did not change.

## Proof and limits

Complete replies, files, relevant actions and available child findings were inspected, with
independent inspection of new outputs. Captured source texts, digests, definitions and recorded
isolation match. The exact second instruction returns in all 15 action records. All 12
calibration judgments agree. Seventy-four affected framework tests, quality checks and 160 definitions
pass. Independent whole-task intent and engineering reviews pass. Raw evidence was reviewed and
deleted. No full-corpus pass or global deployment is claimed.
