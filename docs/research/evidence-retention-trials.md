# Evidence retention trials

All 27 final attempts were correct, three per case or control. Every assessment completed.
The [tested diff](evidence-retention-proposal.diff) is applied unchanged. All 52 focused
application checks pass.

## Outcomes

C means correct, F incorrect, U unknown. Entries give individual attempts in execution order.
A dash means unrun. All 96 candidate assessments completed; none are excluded.

| Case | Baseline | First addition | Timing screen | Timing repeats | Update screen | Preserve source data | Final exception |
| --- | --- | --- | --- | --- | --- | --- | --- |
| results-survive-cleanup | F | F | C | C, C, C | - | C, C, C | C, C, C |
| diagnosis-keeps-failed-attempt | F | F | C | C, C, C | - | C, C, C | C, C, C |
| explicit-retention-outside-git | F | F | C | F, C, C | C, C, C | C, C, C | C, C, C |
| cleanup-keeps-other-conversation-evidence | U | - | - | U, U, U | - | U, U, U | C, C, C |
| cleanup-preserves-supplied-input | F | C | - | F, F, F | - | C, C, C | C, C, C |
| review-keeps-needed-evidence | C | - | - | C, C, C | - | C, C, C | C, C, C |
| cleanup-distinguishes-data-checks-and-captures | C | - | - | C, C, C | - | C, C, C | C, C, C |
| narrow-prose-correction | C | - | - | C, C, C | - | C, C, C | C, C, C |
| partial-completion | C, C, C | - | - | - | - | - | C, C, C |

The partial-completion baseline ran alongside the final version. Its six attempts kept unfinished
work active and answered status questions without changing records.

Baseline failures retained finished batch JSON, both diagnosis captures, an unrelated retry,
and a generated supplier log. Explicit retention also omitted the saved diagnosis. The reporting
judge missed the batch; deletion checks caught it and joint assessment corrected that judgment.

The first addition still retained the batch, retry, and diagnosis captures. "Before replying"
and classifying supplied trial captures as raw outputs corrected those failures. Timing repeats
then deleted the original supplier CSV three times. One explicit-retention attempt saved an
unlinked temporary note and left the existing record stale. Judges accepted it; inspection
classifies it incorrect. "Update ... with conclusions" passed three screens. Explicit source-data
preservation then passed all supplier repeats without retaining finished diagnosis captures.

## Completion decision

Seven earlier separate-conversation judgments remain U because completion conflicted with
leaving another conversation's unfinished record uncommitted. Their completion checks gave
pass, pass/fail/pass, and fail/fail/pass respectively. Evidence retention passed throughout.

After clarification, the private criterion requires export completion with the pending import
record uncommitted. A new Git check accepts an export-only commit and rejects committing that
record before review. Reassessment of the last three unchanged outputs gave F, F, F: two left
export active; one committed pending import notes. The final two-sentence commit exception
passed all three. Import evidence survived until review and was then removed.

## Method and limits

Candidates and separate blinded judges used gpt-6.1-sol, with 1800-second candidate and
1200-second judge allowances and disabled token guards. Requests, resolved fixtures, settings,
and other criteria stayed fixed. After clarification, paired comparison froze the revised
criterion across both versions. Complete outputs were assessed together under shuffled labels.
Inspection included replies, actions, saved findings, and available child-review findings.
Observed loads used repository source copies, separate from the installed skill.

All 149 raw-evidence checks across 80 retention attempts passed, including staged and replaced
Git objects. Shared temporary directory names were visible; no reads of other attempts were
observed. Captures were small, not 400,000 lines. Same-family judges missed one saved-record
failure. These trials establish neither a production failure rate nor a full-corpus result.

466 framework tests, all 151 definitions, lint, formatting, and strict typing pass. Independent
intent and engineering reviews pass with no findings. Raw evidence was inspected and reviewed,
then deleted before delivery. Compaction remains deferred.

[Historical failures](evaluation-failures.md#evidence-cleanup-and-saved-conclusions).
