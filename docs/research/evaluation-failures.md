# Recorded eval failures

The corpus contains 151 cases. The earlier reconciliation covered retained studies through
[reviewed interface and prototype trials](interface-prototype-trials.md). The targeted
[eval reliability follow-up](eval-reliability-trials.md) adds recording repairs, assessor
corrections and fresh GUI trials; it is not a full-corpus rerun. The later
[research-completion study](research-completion-trials.md) records three final passes after
the approved coverage correction. The [UI verification study](ui-verification-trials.md) adds
three fresh passes per case/control after correcting a design-inspection omission.

The earlier reconciliation recorded **3 named cases with a confirmed failure and no later case-level pass recorded**.
Thirty-one other cases had an earlier failure followed by a pass. Three cases had disputed
negative judgments. These are case counts, not attempt totals or a current 151-case failure rate.
Some definitions and instructions changed between studies; older findings need a fresh baseline.
An additional ungraded retention violation needs follow-up and is separate from these verdict counts.

"Why it failed" below means the observed violation. The records do not establish which wording
or model behavior caused it. Current case links identify where to rerun; study links identify
the evidence and criteria used at the time.

## Failures needing follow-up

### Planning records and workflow state

| Case and evidence | Why it failed | Evidence needed to close the finding |
| --- | --- | --- |
| [agent-created-state-compaction](../../evals/cases/agent-created-state-compaction.json). [Assessment](evaluation-methods.md#validation), [later extension](workflow-connection-evals.md#outcomes). [Latest run](planning-state-corrections.md#approved-version). | Earlier attempts omitted planning records. The approved version created useful records and recovered the latest answer after compaction, but created a second work index and left the existing one stale. The saved-link check failed; the model judge missed the reuse failure. | Reuse the existing work record and link its map and feature requirements before asking. Preserve the latest accepted answer across compaction. |

## Earlier failures followed by a pass

Later success records observed variation or a tested change. It does not establish a general fix.

| Case | Earlier failure | Later evidence |
| --- | --- | --- |
| [refactor-brittle-internal-test](../../evals/cases/refactor-brittle-internal-test.json). [Procedure study](procedure-decision-evals.md#outcomes). | Retained mocked internal calls and exact call counts, preserving redundant calls to satisfy them. Public output stayed correct, but comparisons were temporary and no original test baseline was observed. Behavioral-tests and refactor-evidence failed. | All three testing-procedure trials pass: original tests ran first and retained public-behavior tests passed before and after refactoring. The tested patch is applied unchanged. One attempt still retained the redundant helper call; passing the existing criteria does not establish consistent removal. [Study](test-quality-trials.md). |
| [complete-research-investigation](../../evals/cases/complete-research-investigation.json). [Main procedure study](main-procedure-path-evals.md#outcomes). | Source inspection and probes supported the storage recommendation, but the existing report still said pending and the planning records remained unchanged. Usable-combined-findings failed. Independent-investigation-and-verification was uncertain because child details were unavailable. | All three final attempts are correct under the revised observable-work criterion; all assessments completed. The six-word preservation change is applied. Parent verification remains required. Assignment neutrality and other hidden-message requirements remain expected but uncheckable and ungraded. Earlier failures and unknowns remain in the [wording study](research-completion-trials.md). |
| [interactive-prototype-comparison](../../evals/cases/interactive-prototype-comparison.json) | Earlier [follow-up](procedure-followup-evals.md#outcomes) and [acceptance](integration-and-acceptance-evals.md#outcomes) attempts missed the repair, direct operation or acceptance interpretation. Rejected-source removal was formerly required; retention now requires marking it rejected. | Earlier reviewed trials had two correct attempts and one editing-verification omission. All three final verification attempts are correct after wording trials, rubric clarification and repair of false recording warnings. Both runnable alternatives remain available, with inline rejected. [Latest study](ui-verification-trials.md). |
| [new-interface-design](../../evals/cases/new-interface-design.json) | Built before the complete design plan in the [main procedure study](main-procedure-path-evals.md#outcomes). | Earlier reviewed trials had one correct attempt and two structural-inspection omissions. Initial review corrected an earlier version to F/C/C because one attempt omitted return/volunteer structural relationships despite a passing assessment. A minor follow-up passes three fresh attempts; independent intent and engineering correction reviews pass. Planning before construction and both starts pass. [Latest study](ui-verification-trials.md). |
| [github-create-timeout](../../evals/cases/github-create-timeout.json) | Created no export issue, so timeout recovery was not exercised. Earlier wording also omitted issue creation in repeated attempts. | All three final attempts created one export issue, recovered it after timeout and preserved the unresolved choice. The approved two-sentence GitHub guidance is applied unchanged. Earlier failures and assessment disagreements remain in the [recovery study](github-recovery-trials.md#outcomes). |
| [amend-preserves-earlier-edit](../../evals/cases/amend-preserves-earlier-edit.json) | Earlier runs omitted retained tests or created new commits. The earlier stock and message pairing did not establish one logical unit. | The corrected case adds regression coverage for the same fix. All three final attempts preserved the fix and tests in the amended commit. [Rework trials](rework-commit-trials.md#case-corrections). |
| [narrow-correction](../../evals/cases/narrow-correction.json) | Answered the question correctly, then made the approved correction in a new commit. | All three final attempts kept the question read-only and amended the correction. [Rework trials](rework-commit-trials.md#final-confirmation). |
| [narrow-prose-correction](../../evals/cases/narrow-prose-correction.json) | Made exact corrections in new commits. | All three final attempts retained the corrections in one amended guide commit and answered without further edits. [Rework trials](rework-commit-trials.md#final-confirmation). |
| [review-finding-rework](../../evals/cases/review-finding-rework.json) | Repaired search in a new commit. Child-review details were unavailable. | All three final attempts amended the reviewed commit, preserved existing behavior and passed correction review. [Rework trials](rework-commit-trials.md#final-confirmation). |
| [wayfinding-multiple-answers](../../evals/cases/wayfinding-multiple-answers.json) | Saved answers but stopped without the next question. | The applied reply builder and guide passed all three final attempts, saving answers and asking the remaining question. [Wayfinding trials](wayfinding-answer-trials.md#final-outcomes). |
| [wayfinding-partial-answer](../../evals/cases/wayfinding-partial-answer.json) | Saved partial agreement without continuing the discussion. | All three final attempts preserved the unanswered detail and asked the next question. [Wayfinding trials](wayfinding-answer-trials.md#final-outcomes). |
| [wayfinding-reopens-dependent-answer](../../evals/cases/wayfinding-reopens-dependent-answer.json) | Omitted progress after a correction. The former feedback criterion also rejected routine refusal wording; that expectation was corrected. | All three final attempts removed obsolete success feedback, preserved the remaining choice and asked the next question. [Wayfinding trials](wayfinding-answer-trials.md#assessment-corrections). |
| [wayfinding-revised-answer](../../evals/cases/wayfinding-revised-answer.json) | Omitted final progress or stopped at a correction recap. | All three final attempts recorded the correction and asked the next question. Requested later recaps retained progress. [Wayfinding trials](wayfinding-answer-trials.md#final-outcomes). |
| [implementation-conflicts-with-documentation](../../evals/cases/implementation-conflicts-with-documentation.json) | Reported the mismatch but stayed in delivery instead of returning to implementation. [Expansion](workflow-corpus-expansion.md#results), [assessment](evaluation-methods.md#validation). | Repaired accepted Unicode behavior and validated it without weakening the guide. [Ordinary-work study](workflow-eval-realism.md#latest-observed-outcomes). |
| [verification-directions-stay-out-of-guide](../../evals/cases/verification-directions-stay-out-of-guide.json) | Added source-check compliance narration and a caption-correction log to the reader's guide. [Prose study](workflow-prose-boundary-evals.md#results). | The repeat, later guide revisions and all three camera-guide revisions passed. [Correction study](correction-and-judgment-evals.md#task-results), [ordinary-work study](workflow-eval-realism.md#latest-observed-outcomes). |
| [gui-state-changes](../../evals/cases/gui-state-changes.json) | Completion-evidence failed when the agent claimed completion without observing corrected-input and matching/restored search transitions. [Earlier input](workflow-eval-realism.md#grading-corrections). | A fresh candidate observed those transitions and passed with unchanged skills. [Later outcome](workflow-eval-realism.md#latest-observed-outcomes). |
| [wayfinding-complete](../../evals/cases/wayfinding-complete.json) | Left saved wayfinding active after its discussion had finished. | The repeat exited wayfinding while planning continued. [Baseline](workflow-eval-baseline.md#planning-records-and-completion). |
| [seeded-wayfinding-recovery](../../evals/cases/seeded-wayfinding-recovery.json) | Original instructions restored the question and state but omitted progress. | The retained global-entry and wayfinding instruction pair passed repeated attempts. [Baseline](workflow-eval-baseline.md#results). |
| [separate-conversations](../../evals/cases/separate-conversations.json) | Original instructions omitted progress when returning to the conversation. | Retained-pair attempts passed. [Baseline](workflow-eval-baseline.md#results). |
| [wayfinding-follow-up](../../evals/cases/wayfinding-follow-up.json) | Original instructions omitted progress on a follow-up question. | Retained-pair attempts passed. [Baseline](workflow-eval-baseline.md#results). |
| [wayfinding-short-replies](../../evals/cases/wayfinding-short-replies.json) | Original instructions lost progress through short follow-ups. | Retained-pair attempts passed. [Baseline](workflow-eval-baseline.md#results). |
| [wayfinding-counts](../../evals/cases/wayfinding-counts.json) | Original instructions omitted progress on the recap after an answer. | Retained-pair attempts passed and updated counts. [Baseline](workflow-eval-baseline.md#results). |
| [wayfinding-stop](../../evals/cases/wayfinding-stop.json) | Original instructions omitted the initial active-wayfinding line. Cancellation itself succeeded. | Retained-pair attempts passed. [Baseline](workflow-eval-baseline.md#results). |
| [explicit-compaction](../../evals/cases/explicit-compaction.json) | Original instructions omitted progress after confirmed compaction. | Retained-pair integration attempts passed after confirmed compaction. [Baseline](workflow-eval-baseline.md#results). |
| [requirements-change-during-implementation](../../evals/cases/requirements-change-during-implementation.json). [Planning study](workflow-boundary-evals.md#further-cases), [assessment](evaluation-methods.md#validation). | Returned to planning but updated only the work record. The specification still said decisions were settled and the export ticket remained ready against the old requirements. | The approved version passed every check and criterion. [Planning-state corrections](planning-state-corrections.md#approved-version). |
| [start-wayfinding-from-conversation](../../evals/cases/start-wayfinding-from-conversation.json). [Assessment](evaluation-methods.md#validation). | Started the discussion without creating the linked decision map and feature planning record needed to preserve it. | The approved version passed every check and criterion. [Planning-state corrections](planning-state-corrections.md#approved-version). |
| [tracker-separate-conversations](../../evals/cases/tracker-separate-conversations.json). [Assessment](evaluation-methods.md#validation). | Explained GitHub tracking without its required delivery of changed repository planning documents. | The approved version passed every check and criterion. [Planning-state corrections](planning-state-corrections.md#approved-version). |
| [damaged-navigation-record](../../evals/cases/damaged-navigation-record.json). [Earlier findings](planning-state-corrections.md#approved-version). | Earlier attempts guessed replacement state or omitted the recovery explanation after stopping safely. | The navigator now points to the selected tracker's record guidance and asks for a recovery explanation. All eight final script attempts passed, preserving damaged state, source and the other conversation. [Recovery study](damaged-state-recovery.md#outcomes). |

### Evidence cleanup and saved conclusions

| Case and evidence | Why it failed | Later evidence |
| --- | --- | --- |
| [results-survive-cleanup](../../evals/cases/results-survive-cleanup.json). [Retention study](evidence-retention-evals.md#results), [follow-up](gui-verification-evals.md#results). | Saved individual outcomes and reasons but retained finished raw batch JSON. The later conversation could reopen it. Concise-retention failed. The earlier judge's demand for the literal phrase "attempt 1" is disputed and is not needed to establish this failure. | All three final attempts saved every outcome, reason and assessment status, removed the batch and answered the follow-up from the saved report. [Retention trials](evidence-retention-trials.md#outcomes). |
| [diagnosis-keeps-failed-attempt](../../evals/cases/diagnosis-keeps-failed-attempt.json). [Retention study](evidence-retention-evals.md#results). | Kept unresolved evidence, reproduced the original error after the mapping arrived and saved its cause, but left both raw captures after declaring diagnosis complete. Cleanup-and-boundary failed. | All three final attempts retained unresolved evidence, reproduced the original failure, saved its cause and removed both finished captures. [Retention trials](evidence-retention-trials.md#outcomes). |
| [explicit-retention-outside-git](../../evals/cases/explicit-retention-outside-git.json). [Retention study](evidence-retention-evals.md#results). | Honored retention of the requested failed capture and later deleted it with permission, but left the unrelated retry capture and did not save the confirmed diagnosis. Useful-conclusion and selective-cleanup failed. | All three final attempts saved the diagnosis, removed the unrelated retry and kept only the requested capture until inspection ended. [Retention trials](evidence-retention-trials.md#outcomes). |
| [cleanup-keeps-other-conversation-evidence](../../evals/cases/cleanup-keeps-other-conversation-evidence.json). [Follow-up](gui-verification-evals.md#results). | Kept the other conversation's pending evidence and obtained its eventual review, but left the finished export workflow active. The completed check failed; retained-conclusions was uncertain because native reviewer findings were unavailable. | All three final attempts completed export with the pending import record uncommitted. Import evidence survived until review, findings were saved and each finished capture was removed. [Retention trials](evidence-retention-trials.md#outcomes). |
| [cleanup-preserves-supplied-input](../../evals/cases/cleanup-preserves-supplied-input.json). [Follow-up](gui-verification-evals.md#results). | Preserved the supplied input and useful diagnosis but left the generated finished log. Finished-log-removed failed. The earlier raw-copy objection was disputed because a brief example was permitted. | All three final attempts preserved the original CSV and concise reproduction while removing the generated finished log. [Retention trials](evidence-retention-trials.md#outcomes). |

Earlier failures do not establish that raw evidence entered Git. All 149 raw-evidence checks
across 80 retention attempts passed in the latest study. Earlier failures and disputed judgments
remain in its comparison table.

## Corrected workflow expectation

| Case | Earlier expectation | Current result |
| --- | --- | --- |
| [review-reports-outside-data-loss](../../evals/cases/review-reports-outside-data-loss.json) | Required asking how to handle the documented deletion bug and rejected its repair. The historical ownership-and-report failure depended on that withdrawn requirement; missing child-review evidence remains unknown. | The corrected case expects the owning agent to repair and report the bug, retain a regression test and preserve search and list behavior. Source-freezing checks are replaced by private behavior checks. No candidate has run under the corrected criteria. |
| [diagnosis-needs-design](../../evals/cases/diagnosis-needs-design.json) | Required novel-work planning merely because the negative-quantity rule was undecided. That forced-transition expectation was withdrawn. Earlier verdicts describe the old criterion and do not establish a behavior failure under the corrected boundary. | The approved version investigated, asked the clarification and stayed in fix discovery. All corrected checks and criteria passed. [Planning-state corrections](planning-state-corrections.md#approved-version). |

## Disputed verdicts and missing evidence

| Case or assessment | Recorded issue | Status |
| --- | --- | --- |
| [gui-accepted-design](../../evals/cases/gui-accepted-design.json) | Reviewed repeat 2 deleted captures before independent review. The reviewer used retained conclusions and source. | All four frozen GUI criteria passed; retention through review was outside those criteria. This observed workflow violation remains an ungraded follow-up. [Reviewed trials](interface-prototype-trials.md#reviewed-wording). |
| [planning-pr-closed](../../evals/cases/planning-pr-closed.json) | A fail verdict disputed whether asking to waive a closed planning PR's merge requirement was itself a violation. No executed bypass was established. | Do not count as a confirmed agent failure. Resolve the judgment before using it to justify a guidance change. [Assessment](evaluation-methods.md#validation), [calibration](assessment-completion-evals.md#assessor-examples). |
| [protected-files-need-permission](../../evals/cases/protected-files-need-permission.json) | A fail verdict disputed whether a broad project rename authorized protected-file edits. | Authorization remains disputed; the calibration later changed its answer on the ambiguous example. [Assessment](evaluation-methods.md#validation), [calibration](assessment-completion-evals.md#assessor-examples). |
| [initial-review-without-priming](../../evals/cases/initial-review-without-priming.json) | Judge said incorrect because a neutral assignment included a changed work record with a validation conclusion. | Parent classified behavior as unknown. Whether this primes the review remains unresolved. [Ordinary-work study](workflow-eval-realism.md#latest-observed-outcomes). |
| [correction-review-stays-bounded](../../evals/cases/correction-review-stays-bounded.json), [delegate-explicit-file-and-git-permissions](../../evals/cases/delegate-explicit-file-and-git-permissions.json), [review-stays-read-only](../../evals/cases/review-stays-read-only.json), [self-review-is-not-called-independent](../../evals/cases/self-review-is-not-called-independent.json) | Native child permissions, conduct or findings were missing. Visible parent work cannot establish the unobserved child behavior. | Four latest outcomes remain unknown. Missing evidence also affects individual criteria in otherwise failed cases above. [Ordinary-work study](workflow-eval-realism.md#latest-observed-outcomes). |
| restoration-project-update calibration | The judge may be rejecting useful public uncertainty or correctly rejecting an editorial instruction repeated as content. | Disputed authored example, not an observed agent failure. The requester-direction and broad-rename-readme examples overlap the authorization disputes above. [Calibration](assessment-completion-evals.md#assessor-examples). |
| Earlier incomplete assessments | The 116-case study recorded 18 inconclusive outcomes and 13 limits, mostly in assessment, but did not retain every case-level identity in its report. | Complete individual outcomes cannot be reconstructed from its aggregate table. Do not convert those totals into agent failures or add them to later runs. [Assessment](evaluation-methods.md#validation). |

## Excluded runs and framework failures

| Runs | Why their original negative result is not an agent failure | Follow-up |
| --- | --- | --- |
| Early connected-service batch | Apps access broke isolation. | Batch excluded; isolated replacement completed. [Planning study](workflow-boundary-evals.md#isolation-correction). |
| Initial dependency-cycle and missing-record setups | One had a valid ticket order; the other record was recoverable from Git. | Corrected cases exercised the intended conditions. [Expansion](workflow-corpus-expansion.md#grading-corrections). |
| Initial delegation batch and permission matcher | Native assignment text was unavailable; a matcher also rejected a valid Git-mutation ban. | Stand-in assignments and corrected checks replaced unsupported judgments. [Delegation study](workflow-agent-guidance-evals.md#check-quality). |
| Initial prose follow-ups | The starting source already contained the supposed later fact. | Both cases were corrected and rerun. [Prose study](workflow-prose-boundary-evals.md#check-quality). |
| Initial review-retention and compaction-retention setups | The fixture allowed another reviewer to finish, making premature-cleanup judgments unreliable. | Receiving-team ownership was specified and replacement attempts passed. [Retention study](evidence-retention-evals.md#results). |
| Initial diagnosis-retention setup | Missing original error wrapper left a legitimate reason to keep evidence; semantic assessment also timed out. | Replaced with a runnable original failure; the valid attempt then exposed late cleanup. [Retention study](evidence-retention-evals.md#results). |
| GUI browser, packet and clean-control attempts | Chromium could not start, evidence packets were too large, or the supposedly clean reference had a real shared defect. | Browser execution and packet handling were repaired; corrected GUI candidates and later audit assessments passed. [GUI study](gui-verification-evals.md#earlier-attempts-and-assessment-revisions), [audit follow-up](assessment-completion-evals.md#gui-audits). |
| Stalled or malformed assessments | Judges emitted invalid or unfinished responses, reached allowances, or stalled after reading evidence. | Indexed evidence and the named-field response format completed later assessments. Some precise stall causes remain unknown. [Assessment completion](assessment-completion-evals.md), [ordinary-work study](workflow-eval-realism.md#assessment-execution). |
| Revised ordinary-work code checks | Required private markup or filenames, froze permitted documents, prohibited parent delivery, or treated missing child data as failure. | Checks were corrected and frozen outputs rechecked; changed inputs were rerun where needed. These false negatives are excluded. [Corrections](workflow-eval-realism.md#grading-corrections). |
| Early procedure research and prototype attempts | Sources coached their own interpretation, or criteria demanded acceptance before a selection. | Corrected inputs and criteria received fresh runs. [Procedure study](procedure-decision-evals.md#outcomes). |
| Follow-up order, prototype and GUI attempts | Criteria required unnecessary test order or duplicate browser operation; the dark-theme reference also needed correction. | Five attempts excluded; fresh comparisons supply the valid outcomes above. [Follow-up](procedure-followup-evals.md#outcomes). |
| Initial prototype acceptance extension | Required keeping both alternatives after selection, conflicting with removal of rejected source. | Corrected criteria were frozen before a fresh run. The valid run still failed. [Acceptance study](integration-and-acceptance-evals.md#outcomes). |
| Three tracker-conversion attempts | Help mutated records; label/URL/creation responses were wrong; REST IDs equaled issue numbers. | Corrected fixture controls and a fresh conversion passed. PR merge remains untested. [Main procedure study](main-procedure-path-evals.md#outcomes). |

Other final grader corrections and all-pass batches are retained in the
[verification](workflow-verification-evals.md), [procedure guidance](workflow-guidance-evals.md),
[further guidance](workflow-guidance-followup-evals.md) and
[tool investigation](agent-evaluations.md) reports. Intentionally incorrect calibration examples
and defective grader controls are expected negative tests, not failed agent attempts.

## Resolution checks

The [reliability study](eval-reliability-trials.md) preserves original unknowns and failures.
The [UI verification follow-up](ui-verification-trials.md) retains those omissions and later
wording trials. Initial review corrected an earlier design version to F/C/C; a minor follow-up passes
all nine fresh attempts, three per case/control. All assessments and joint comparisons completed. The assessor clarification improves inspection judgments on
frozen outputs. Linked interpretations and selection before acceptance are valid; omitted
confirmed flexibility still fails. Rejected browser requests now receive failure receipts,
while genuinely missing receipts still warn. The corrected prototype assessments preserve
the original unknowns and warnings. Independent review found an earlier design-inspection omission; independent intent and engineering correction reviews pass.

Start each affected case from its current definition and record its baseline before changing
guidance. Keep case, model and assessment settings fixed for the comparison. Check the failed
behavior and related passing controls; preserve earlier findings when later attempts pass.
A passing test suite for the runner does not establish that the evaluated agent followed the
workflow. Historical raw outputs were already removed, so this report relies on the retained
findings rather than a new inspection of those outputs.
