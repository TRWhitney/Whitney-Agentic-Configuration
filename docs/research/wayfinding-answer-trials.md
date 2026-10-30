# Wayfinding after answers

The applied change produced correct behavior in all nine cases, three attempts each.
All assessments completed. No candidate or judge cleared context. The
[tested diff](wayfinding-reply-proposal.diff) is applied.

## Final outcomes

| Case | Attempt 1 | Attempt 2 | Attempt 3 |
| --- | --- | --- | --- |
| [Multiple answers](../../evals/cases/wayfinding-multiple-answers.json) | Correct | Correct | Correct |
| [Partial answer](../../evals/cases/wayfinding-partial-answer.json) | Correct | Correct | Correct |
| [Dependent answer](../../evals/cases/wayfinding-reopens-dependent-answer.json) | Correct | Correct | Correct |
| [Revised answer](../../evals/cases/wayfinding-revised-answer.json) | Correct | Correct | Correct |
| [Derived choices](../../evals/cases/wayfinding-derives-settled-choices.json) | Correct | Correct | Correct |
| [Finished design](../../evals/cases/wayfinding-complete.json) | Correct | Correct | Correct |
| [Stop](../../evals/cases/wayfinding-stop.json) | Correct | Correct | Correct |
| [Blocked question](../../evals/cases/wayfinding-blocked-question.json) | Correct | Correct | Correct |
| [Start](../../evals/cases/start-wayfinding-from-conversation.json) | Correct | Correct | Correct |

All 33 replies sent while wayfinding remained active copied successful reply-command output
exactly. Replies, answers, open questions, records and workflow state were inspected. Completion left wayfinding while keeping planning active for the specification
and tickets. Stopping removed the progress line without ending planning. Production stayed unchanged.

## Applied change

The navigator builds replies from progress counts, unspecified topics, discussion and the next
question. Requested recaps use `--recap`; blocked discussion uses `--blocked-by`. Finished
wayfinding must be left. The command does not change saved state. Leaving a substate prompts
an update to its linked work record.

The guide requires a map update and next question after answers or corrections. A shorter guide
used recap mode after corrections in two of six attempts, so it was rejected.

## Assessment corrections

The original correction criteria allowed recaps without questions. The revised criteria require
continuation after corrections while allowing requested later recaps and routine wording choices.
Continuation calibration agrees on all five examples. Feedback calibration improved from three
of four to four of four, including both incorrect controls.

An earlier feedback judgment rejected an ordinary refusal explanation as invented approval.
Three fresh attempts replace the earlier dependent-answer results.

All three blocked-question outputs were wrongly judged to lack saved answers. Native edits were
missing from action evidence, and judges treated their results as supplied edits. The runner now
captures native patches and status, and assessment indexes distinguish candidate changes from
supplied changes. Reassessment of those same outputs passes the unchanged rubric.

## Limits and checks

These short conversations use local tracking and supplied state. Candidate and
separate blinded judge both use gpt-6.1-sol. Three attempts do not establish a production failure
rate. Context clearing remains deferred.

444 framework tests, lint, formatting, strict typing across 80 files and all 151 case definitions
pass. All 29 session tests, lint, formatting, strict typing and skill validation pass.
The applied code and guide match the tested patch. Independent intent and engineering review pass.
Reviewed raw evidence was removed.

## Earlier 52 assessments

These used the earlier criteria. All completed, with 46 correct and six incorrect judgments.
All six failures omitted final progress. Five put it only in commentary. The one-word change
passed 18 attempts but did not establish continuation after corrections.

| Case | Original screening | Two additions | Original repeats | Answer loop | Final reply |
| --- | --- | --- | --- | --- | --- |
| [Multiple answers](../../evals/cases/wayfinding-multiple-answers.json) | 1 correct | 1 correct | 1 correct; 2 correct | 1 correct; 2 correct | 1 correct; 2 correct; 3 correct |
| [Partial answer](../../evals/cases/wayfinding-partial-answer.json) | 1 correct | 1 correct | 1 correct; 2 correct | 1 correct; 2 incorrect | 1 correct; 2 correct; 3 correct |
| [Dependent answer](../../evals/cases/wayfinding-reopens-dependent-answer.json) | 1 incorrect | 1 correct | 1 incorrect; 2 correct | 1 incorrect; 2 correct | 1 correct; 2 correct; 3 correct |
| [Revised answer](../../evals/cases/wayfinding-revised-answer.json) | 1 correct | 1 correct | 1 incorrect; 2 incorrect | 1 correct; 2 correct | 1 correct; 2 correct; 3 correct |
| [Derived choices](../../evals/cases/wayfinding-derives-settled-choices.json) | 1 correct | 1 correct | 1 correct; 2 correct | 1 correct; 2 correct | 1 correct; 2 correct; 3 correct |
| [Finished design](../../evals/cases/wayfinding-complete.json) | Not run | Not run | 1 correct; 2 correct | 1 correct; 2 correct | 1 correct; 2 correct; 3 correct |

## Further comparisons

Cells retain each attempt's original judgment. C numbers refer to that case's private rubric;
named checks are automatic checks. Provisional correction criteria over-specified the question
and repeated facts. Their 66 judgments are excluded. The other 32 screening judgments used
unchanged criteria and all passed. Later rows use corrected continuation criteria. Feedback
and blocked-question judgments have the exceptions above. Pass rates across revisions differ.

### Provisional screening

| Comparison | Variant | Case | Earlier automated judgments |
| --- | --- | --- | --- |
| active-dependent-screen | active-last | Dependent answer | 1 incorrect C4 |
| active-dependent-screen | wording-only | Dependent answer | 1 incorrect C4 |
| active-revised-screen | active-last | Revised answer | 1 incorrect C4 |
| active-revised-screen | wording-only | Revised answer | 1 incorrect C4 |
| answers-repeat | own-choices | Multiple answers | 1 correct; 2 correct; 3 correct |
| answers-repeat | own-choices | Partial answer | 1 correct; 2 correct; 3 correct |
| answers-screen | continue | Multiple answers | 1 correct |
| answers-screen | continue | Partial answer | 1 correct |
| answers-screen | final-only | Multiple answers | 1 correct |
| answers-screen | final-only | Partial answer | 1 correct |
| continue-discussion-corrections | continue-discussion | Dependent answer | 1 incorrect C3, C4; 2 incorrect C4; 3 correct |
| continue-discussion-corrections | continue-discussion | Revised answer | 1 incorrect C4; 2 correct; 3 incorrect C4 |
| controls-repeat | own-choices | Finished design | 1 correct; 2 correct; 3 correct |
| controls-repeat | own-choices | Derived choices | 1 correct; 2 correct; 3 correct |
| controls-screen | continue | Finished design | 1 correct |
| controls-screen | continue | Derived choices | 1 correct |
| controls-screen | final-only | Finished design | 1 correct |
| controls-screen | final-only | Derived choices | 1 correct |
| corrections-repeat | own-choices | Dependent answer | 1 incorrect C3, C4; 2 incorrect C4; 3 correct |
| corrections-repeat | own-choices | Revised answer | 1 correct; 2 correct; 3 correct |
| corrections-screen | continue | Dependent answer | 1 incorrect C3, C4 |
| corrections-screen | continue | Revised answer | 1 incorrect C4 |
| corrections-screen | final-only | Dependent answer | 1 incorrect C4 |
| corrections-screen | final-only | Revised answer | 1 incorrect C4 |
| end-minimal-corrections | end-minimal | Dependent answer | 1 incorrect C4; 2 correct; 3 incorrect C3, C4 |
| end-minimal-corrections | end-minimal | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect reply_regex |
| end-reply-corrections | end-reply | Dependent answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| end-reply-corrections | end-reply | Revised answer | 1 incorrect reply_regex; 2 incorrect C4; 3 incorrect C4 |
| filter-first-corrections | filter-first | Dependent answer | 1 incorrect C3; 2 incorrect C3, C4; 3 incorrect C3, C4 |
| filter-first-corrections | filter-first | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| judgment-screen | judgment | Dependent answer | 1 incorrect C3 |
| judgment-screen | judgment | Revised answer | 1 correct |
| next-question-answers | next-question | Multiple answers | 1 correct; 2 correct; 3 correct |
| next-question-answers | next-question | Partial answer | 1 correct; 2 correct; 3 correct |
| next-question-controls | next-question | Finished design | 1 correct; 2 correct; 3 correct |
| next-question-controls | next-question | Derived choices | 1 correct; 2 correct; 3 correct |
| next-question-corrections | next-question | Dependent answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| next-question-corrections | next-question | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| own-choices-screen | own-choices | Dependent answer | 1 correct |
| own-choices-screen | own-choices | Revised answer | 1 correct |
| planning-continue-corrections | planning-continue | Dependent answer | 1 correct; 2 incorrect C3; 3 incorrect C3, C4 |
| planning-continue-corrections | planning-continue | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| reply-format-corrections | reply-format | Dependent answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C3, C4 |
| reply-format-corrections | reply-format | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |
| substate-only-corrections | substate-only | Dependent answer | 1 incorrect C4; 2 incorrect C3; 3 incorrect C4 |
| substate-only-corrections | substate-only | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 incorrect C4 |

### Continuation trials and final confirmation

| Comparison | Variant | Case | Earlier automated judgments |
| --- | --- | --- | --- |
| answer-heading-answers | answer-heading | Multiple answers | 1 correct; 2 correct; 3 correct |
| answer-heading-answers | answer-heading | Partial answer | 1 correct; 2 correct; 3 correct |
| answer-heading-boundaries | answer-heading | Start | 1 correct |
| answer-heading-boundaries | answer-heading | Blocked question | 1 correct |
| answer-heading-boundaries | answer-heading | Stop | 1 correct |
| answer-heading-confirm | answer-heading | Dependent answer | 1 incorrect C4; 2 correct; 3 correct |
| answer-heading-confirm | answer-heading | Revised answer | 1 correct; 2 correct; 3 correct |
| answer-heading-controls | answer-heading | Finished design | 1 correct; 2 correct; 3 correct |
| answer-heading-controls | answer-heading | Derived choices | 1 correct; 2 incorrect consistent-planning-state; 3 correct |
| answer-heading-corrections | answer-heading | Dependent answer | 1 correct; 2 correct; 3 correct |
| answer-heading-corrections | answer-heading | Revised answer | 1 correct; 2 correct; 3 correct |
| builder-final-dependent | reply-builder-recap | Dependent answer | 1 correct; 2 correct; 3 correct |
| builder-minimal-corrections | reply-builder-minimal | Dependent answer | 1 incorrect C4; 2 incorrect C4; 3 correct |
| builder-minimal-corrections | reply-builder-minimal | Revised answer | 1 correct; 2 correct; 3 correct |
| builder-recap-answers | reply-builder-recap | Multiple answers | 1 correct; 2 correct; 3 correct |
| builder-recap-answers | reply-builder-recap | Partial answer | 1 correct; 2 correct; 3 correct |
| builder-recap-boundaries | reply-builder-recap | Start | 1 correct; 2 correct; 3 correct |
| builder-recap-boundaries | reply-builder-recap | Blocked question | 1 incorrect C2; 2 incorrect C2; 3 incorrect C2 |
| builder-recap-boundaries | reply-builder-recap | Stop | 1 correct; 2 correct; 3 correct |
| builder-recap-controls | reply-builder-recap | Finished design | 1 correct; 2 correct; 3 correct |
| builder-recap-controls | reply-builder-recap | Derived choices | 1 correct; 2 correct; 3 correct |
| builder-recap-corrections | reply-builder-recap | Dependent answer | 1 correct; 2 incorrect C3; 3 correct |
| builder-recap-corrections | reply-builder-recap | Revised answer | 1 correct; 2 correct; 3 correct |
| fair-final-only | final-only | Dependent answer | 1 incorrect C4 |
| fair-final-only | final-only | Revised answer | 1 incorrect C4 |
| fair-substate-corrections | substate-only | Dependent answer | 1 incorrect C3, C4; 2 incorrect C4; 3 incorrect C4 |
| fair-substate-corrections | substate-only | Revised answer | 1 incorrect C4; 2 incorrect C4; 3 correct |
| finish-with-question-answers | finish-with-question | Multiple answers | 1 correct; 2 correct; 3 correct |
| finish-with-question-answers | finish-with-question | Partial answer | 1 correct; 2 correct; 3 correct |
| finish-with-question-controls | finish-with-question | Finished design | 1 correct; 2 correct; 3 correct |
| finish-with-question-controls | finish-with-question | Derived choices | 1 correct; 2 correct; 3 correct |
| finish-with-question-corrections | finish-with-question | Dependent answer | 1 correct; 2 correct; 3 correct |
| finish-with-question-corrections | finish-with-question | Revised answer | 1 correct; 2 correct; 3 incorrect C4 |
| map-and-reply-answers | map-and-reply-check | Multiple answers | 1 correct; 2 correct; 3 correct |
| map-and-reply-answers | map-and-reply-check | Partial answer | 1 correct; 2 correct; 3 correct |
| map-and-reply-controls | map-and-reply-check | Finished design | 1 incorrect C5; 2 correct; 3 correct |
| map-and-reply-controls | map-and-reply-check | Derived choices | 1 correct; 2 correct; 3 correct |
| map-and-reply-corrections | map-and-reply-check | Dependent answer | 1 correct; 2 correct; 3 incorrect C3, C4 |
| map-and-reply-corrections | map-and-reply-check | Revised answer | 1 correct; 2 incorrect C4; 3 correct |
| reply-builder-corrections | reply-builder | Dependent answer | 1 correct; 2 correct; 3 correct |
| reply-builder-corrections | reply-builder | Revised answer | 1 incorrect reply_regex; 2 incorrect reply_regex; 3 incorrect reply_regex |
| reply-check-answers | reply-check | Multiple answers | 1 correct; 2 correct; 3 incorrect C3 |
| reply-check-answers | reply-check | Partial answer | 1 incorrect C4; 2 correct; 3 correct |
| reply-check-boundaries | reply-check | Start | 1 correct |
| reply-check-boundaries | reply-check | Blocked question | 1 correct |
| reply-check-boundaries | reply-check | Stop | 1 correct |
| reply-check-confirm | reply-check | Dependent answer | 1 correct; 2 correct; 3 correct |
| reply-check-confirm | reply-check | Revised answer | 1 correct; 2 correct; 3 incorrect C4 |
| reply-check-controls | reply-check | Finished design | 1 correct; 2 correct; 3 correct |
| reply-check-controls | reply-check | Derived choices | 1 correct; 2 correct; 3 correct |
| reply-check-corrections | reply-check | Dependent answer | 1 correct; 2 correct; 3 correct |
| reply-check-corrections | reply-check | Revised answer | 1 correct; 2 correct; 3 correct |

The reply-builder initially rejected later recaps, which lost progress in all three revised-answer
attempts. Recap support corrected that. Other prose trials still omitted questions or progress,
left settled calculations open, or left a linked record claiming wayfinding was active after exit.
The final table uses fresh dependent-answer results and repaired blocked assessments.
