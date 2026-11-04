# Agent workflow evaluations

## Destination

[Assess the existing corpus](spec.md#corpus-assessment) and
[evidence retention](spec.md#evidence-retention), with
[correction and assessment coverage](spec.md#corrections-and-assessment-examples).

## Current state

Study complete. [Interface and prototype trials](../../docs/research/interface-prototype-trials.md)
cover 59 attempts across both historical failures and three related cases. All candidate
assessments and all five joint comparisons completed. The final set reconciles to 13 correct
and two unknown. Incomplete interface inspection and one uncompleted volunteer-first checkout
remain unproved. Earlier failures and criterion disagreements remain in the table and findings.
The [tested proposal](../../docs/research/interface-prototype-proposal.diff) remains unapplied.
The prototype eval now allows production after necessary product and architecture decisions
are settled. Its two blanket `src`-preservation checks are removed; the focused regression
reproduced their false rejection before correction. All 13 focused tests, lint, formatting,
strict typing and 151 definitions pass. The correction passes independent intent and engineering
review. Historical trial verdicts remain under the earlier criteria; no fresh candidate or
reassessment has run under the corrected expectation.
The private GUI locator now anchors through editor and Save. Its footer-format regression
failed before correction and passes after, including rejection of a missing dialog frame.
All four saved baseline/visual GUI outputs passed 30 corrected checks each. All 468 framework
tests, lint, formatting, typing, 151 definitions, 52 local links, patch applicability,
tested-source identity and whitespace checks pass. Independent intent and engineering reviews
pass. Intent review's criterion-retention finding was corrected and passed correction review.
Raw evidence was inspected, reviewed and deleted before delivery. Native compaction remains deferred.

Complete. The [deletion eval](../../evals/cases/review-reports-outside-data-loss.json)
now expects repair of its documented bug without a permission question. Its private behavior
check accepts two repair approaches and rejects the original bug, ineffective deletion and
changed list behavior. The focused regression failed under the old checks and passes after
correction. Existing calibration examples now distinguish repair from unnecessary deferral.
Skill guidance and candidate inputs are unchanged. No candidate has run under the revised criteria.
All seven focused tests, all 151 definitions, lint, formatting, strict typing and 172 local links
and anchors pass. All four revised examples agree with a blinded gpt-6.1-sol judge; every
assessment completed. This calibration does not establish candidate behavior. Independent intent
and engineering reviews pass with no findings. Raw assessment evidence was inspected, reviewed
and deleted before delivery.
Focused checks: `.venv/bin/python -m unittest tests.test_eval_calibration tests.test_eval_procedure_followups`.

Complete. [GitHub recovery trials](../../docs/research/github-recovery-trials.md) cover
42 attempts across the timeout case and related planning-update, failed-read and local-conversion
cases. All 12 final attempts are correct, three per case; all candidate assessments and joint
blinded comparisons completed. Earlier failures, one unknown conversion and criterion
disagreements remain in the report. The
[approved two-sentence patch](../../docs/research/github-recovery-proposal.diff) is applied unchanged.
Application passes 49 focused checks, all 151 definitions, 174 local links and anchors, and
reverse-patch verification. The failure report lists six remaining cases, including compaction.
The private PR checks now allow required comments on the existing PR while rejecting extra PRs;
all 32 affected frames pass recheck. The regression failed before correction and passes after.
467 framework tests, all 151 definitions, lint, formatting and strict typing pass. All 48 local
links and anchors, patch applicability, tested-source identity and whitespace checks pass.
Independent intent and engineering reviews pass with no findings. Raw evidence was inspected
and reviewed, then deleted before delivery. Native compaction remains deferred.

Study complete. [Testing-procedure placement trials](../../docs/research/test-quality-trials.md)
add 16 attempts to the earlier 17. All 12 revised attempts passed the frozen criteria; all
assessments and joint blinded comparisons completed. All three refactors loaded testing and
retained passing public-output tests after an observed original baseline. One retained the
double helper call after removing the mocked assertions; this limitation is saved in the report.
The [revised diff](../../docs/research/test-quality-proposal.diff) remains unapplied for review.
All 151 definitions, changed local links, patch applicability and whitespace checks pass.
Earlier framework and quality checks remain applicable because their source is unchanged.
Independent intent and engineering reviews pass with no findings. Raw evidence was inspected
and reviewed, then deleted before delivery. Native compaction remains deferred.

Complete. [Evidence retention trials](../../docs/research/evidence-retention-trials.md)
cover 96 attempts. All 27 final attempts are correct, three per case or control; every assessment
completed. All 149 raw-evidence checks passed. The
[tested diff](../../docs/research/evidence-retention-proposal.diff) adds cleanup wording and
allows delivery while another conversation's unfinished work record remains uncommitted.
The approved wording is applied unchanged. All 52 focused application checks pass, as do
all 151 definitions and 170 local links. The failure report now lists seven remaining cases,
including the deferred compaction case.
The private eval checks that the pending record stays uncommitted; its regression accepts an
export-only commit and rejects committing the pending import record.
466 framework tests, all 151 definitions, lint, formatting, strict typing, and changed local
links pass. Independent intent and engineering reviews pass with no findings. Raw evidence was
inspected and reviewed, then deleted before delivery. Native compaction remains deferred.

Verification commands: `.venv/bin/python -m unittest discover -s tests`,
`.venv/bin/ruff check .`, `.venv/bin/ruff format --check .`,
`.venv/bin/mypy evals scripts tests`, and `.venv/bin/python -m evals validate`.
Application checks: `.venv/bin/python -m unittest tests.test_work_system tests.test_navigators tests.test_eval_retention`
and reverse application of the tested diff.

Complete. [Ticket 21](tickets/21-rework-commit-trials.md) applies the accepted commit conditions
and navigator operations. [Results](../../docs/research/rework-commit-trials.md): all 27 final
attempts correct, three per case or control; every assessment complete. The three unchanged
coverage outputs also pass reassessment after correction of a stale rubric phrase.
465 framework tests, including 41 navigator tests, pass. The 11 affected grading and coverage
tests pass after the rubric correction. Lint, formatting, strict typing, skill validation,
all 151 definitions and changed local links pass. Independent intent and engineering reviews
pass with no findings. Raw evidence was inspected and reviewed, then removed before delivery.
The only trial-supported prose change makes commit lookup happen before creating a new commit.
[Remaining failures](../../docs/research/evaluation-failures.md#failures-needing-follow-up) cover
12 cases without a later pass. Native compaction remains deferred.

Complete. [Ticket 20](tickets/20-wayfinding-answer-trials.md) delivers the tested wayfinding change.
[Final results](../../docs/research/wayfinding-answer-trials.md): all nine cases have three correct
results. Every assessment completed, with no context clearing. All 33 active-wayfinding replies
copied successful reply-command output exactly. The
[tested diff](../../docs/research/wayfinding-reply-proposal.diff) adds reply building, map checks,
recap support and a linked-record update hint. The tested navigator, guide and regression tests are applied.

The two existing correction rubrics now require the next question after corrections. Feedback
calibration allows routine refusal wording without inventing user approval. Native edits and
per-turn artifact changes now reach the judge. Three earlier blocked-question failures pass
reassessment of unchanged outputs and criteria. Earlier judgments and exclusions remain in the report.

444 framework tests, all 151 definitions, lint, formatting and strict typing pass. The
skill passes 29 session tests, lint, formatting, strict typing and skill validation. Independent
intent and engineering reviews pass with no findings. Raw evidence was removed after inspection
and review. [Remaining failures](../../docs/research/evaluation-failures.md#failures-needing-follow-up) cover
16 cases without a later pass. Context-clearing work stays deferred.

Complete. [Ticket 19](tickets/19-planning-state-corrections.md) exposes the selected tracker's
work-record guidance after failed restoration. [Recovery results](../../docs/research/damaged-state-recovery.md):
all eight final-prompt attempts correct, with complete assessments. All 434 framework tests,
lint, formatting, strict typing across 73 files, skill validation and all 151 definitions pass.
Independent intent and engineering reviews pass, including bounded correction review for
unreadable state bytes. Those bytes have command-line regression coverage; the eight earlier
malformed-JSON results remain applicable. Raw evidence was removed after inspection and review.
Compaction changes remain deferred.

Complete. [Ticket 19](tickets/19-planning-state-corrections.md) applies the planning-state wording
and corrects the diagnosis case's forced transition. [Fresh results](../../docs/research/planning-state-corrections.md#approved-version):
four correct and two incorrect. All six assessments completed; 18 prior trials are retained
separately. 432 framework tests, skill validation, lint, formatting, strict typing and all 151
definitions pass. Independent intent and engineering reviews pass; raw evidence was removed
after review. Remaining failures and assessment defects are recorded for the next approved change.

Complete. [Recorded failures](../../docs/research/evaluation-failures.md) reconciles all 20 saved
studies with observed failures, later passes, disputed judgments and resolution checks. Case IDs,
local links and heading links pass checks. Independent intent and engineering reviews pass.
No live evals were rerun.

Complete. [Ticket 18](tickets/18-main-procedure-paths.md) adds five main procedure and wayfinding
cases. [Results](../../docs/research/main-procedure-path-evals.md#outcomes): three correct and two
incorrect behaviors. All eight assessments completed; three fixture attempts are excluded.
432 framework tests, lint, strict typing and all 151 definitions pass. Independent intent and
engineering reviews pass, including bounded correction review. Raw evidence was removed after
inspection and review.

Complete. [Ticket 17](tickets/17-integration-and-acceptance.md) adds three cases and extends
prototype selection. [Results](../../docs/research/integration-and-acceptance-evals.md#outcomes):
three correct and one incorrect behavior. All five assessments completed; one earlier prototype
attempt is excluded. The report retains its criterion dispute and the final assessor correction.
422 framework tests, strict typing and all 146 definitions pass. Independent intent and
engineering reviews pass. Raw evidence was removed after inspection and review.

Complete. [Ticket 16](tickets/16-procedure-followups.md) delivers three new cases and two existing
extensions. [Results](../../docs/research/procedure-followup-evals.md#outcomes): three correct
and two incorrect behaviors. All ten task assessments completed; five earlier comparisons are
excluded with individual statuses and reasons. Four calibration judgments agree with their
expected outcomes. 419 framework tests, strict typing and all 143 definitions pass. Independent
intent and engineering correction reviews pass. Raw evidence was removed after inspection
and review.

Complete. [Ticket 15](tickets/15-procedure-coverage.md) delivers this addition.
[Procedure decisions](spec.md#procedure-decisions) add six cases and the session-based commit
rule. 412 framework tests and all 140 definitions pass.
[Results](../../docs/research/procedure-decision-evals.md#outcomes): five correct and five
incorrect behaviors across ten valid attempts. Two earlier inputs are excluded; all twelve
assessments completed. Independent intent and engineering reviews pass with no findings.
Raw evidence was removed after inspection and review.

The previous addition is complete. [Ticket 14](tickets/14-accepted-coverage.md) delivers this addition. Four new cases and two existing
conversation extensions cover [connections and continued work](spec.md#connections-and-continued-work).
[Results](../../docs/research/workflow-connection-evals.md#outcomes): five correct behaviors and
one incorrect. All six assessments completed. Recovery after compaction passed, but required
wayfinding records were missing. 406 framework tests and all 134 definitions pass. Independent
intent and engineering correction reviews pass. Raw evidence was removed after inspection
and review.

The previous revision is complete. [Ticket 13](tickets/13-unprompted-workflow.md) delivers the
[unprompted-workflow revision](spec.md#unprompted-workflow-behavior).

The [grading follow-up](../../docs/research/workflow-eval-realism.md#grading-equivalence)
corrects five conflicts across 18 cases. No new live outcomes are claimed.

[Results](../../docs/research/workflow-eval-realism.md) retain all 39 executions: 30 correct,
four incorrect, and five unknown. The latest 30 include 22 correct, three incorrect, and five
unknown. The earlier GUI transition failure remains recorded. Subject skills are unchanged.

403 framework tests, lint, formatting, strict typing, JavaScript syntax, and 130 definitions pass.
All 42 task assessments using the new format and four calibration calls completed. All 17 clear
calibration examples agree. Three ambiguous examples remain disputed. Independent intent and
engineering correction reviews pass with no findings. Reviewed raw evidence was removed before
delivery.

The confirmed skill failures, missing child-review evidence, priming dispute, and remaining
realism gaps are findings for later work, not additional accepted implementation in this task.

## Progress

[Tickets 05–11](tickets/) are complete.
Shared temporary storage and private checks now distinguish pending evidence, completed raw
outputs, and concise findings. Requests and supplied records give ordinary task intent
and project context. Genuine user constraints remain. Subject skills and global instructions
are unchanged. [Results, confirmed failures, disputed judgments, and assessment
limits](../../docs/research/evaluation-methods.md#validation) remain separate from infrastructure
validation.

## Accepted sources

[Specification](spec.md#corpus-assessment).
[Authoring standards](../../docs/eval-authoring.md).
[Runner](../../docs/agent-evaluations.md).

## Verification

The previous corpus passed 340 tests. Lint, strict typing, formatting, all 116 definitions, and
private-grader compilation pass. Live artifacts, replies, and relevant actions were inspected
for all original cases. The additional valid ticket-writing execution is reported separately.
Independent engineering review and intent correction review pass with no blocking findings.
The corrected public-command case passes with unprompted regression coverage and observed red
and green results.

The retention addition passes 349 infrastructure tests, lint, typing, formatting, and validation
of all 121 definitions. Every completed live output and relevant action was inspected.
[Retention results](../../docs/research/evidence-retention-evals.md) preserve all seven primary
outcomes, three excluded fixture attempts, disputed judgments, and the prototype assessment limit.
Independent intent and engineering reviews pass, including bounded correction reviews.

The correction addition passes 354 tests, lint, typing, formatting, and validation of all 121
definitions. [Results](../../docs/research/correction-and-judgment-evals.md) retain all task runs
and thirteen calibration outcomes, including interruptions, limits, and disputed judgments.
Independent intent and engineering correction reviews pass.

## GUI verification

All 368 infrastructure tests, lint, strict typing, formatting, JavaScript syntax, and validation
of 130 definitions pass. Independent intent and engineering correction reviews pass. The packet
review has no blocking finding. [Results](../../docs/research/gui-verification-evals.md) distinguish
five passing GUI implementation cases, two audit assessment limits, three follow-up failures,
and the corrected factual-question assessment. Source skills and config remain unchanged.

## Earlier continuation

At that delivery, no accepted implementation work remained. Evidence cleanup failures, the active export workflow,
three ambiguous assessor disagreements, and the unexplained stalled judge remain recorded.
The same audit output has a completed fresh verdict.

## Assessment completion

[Results](../../docs/research/assessment-completion-evals.md) retain all 21 existing calibration
outcomes and every audit judgment. All 17 clear examples agree; three ambiguous examples remain
disputed. Both audit behaviors are correct and have completed four-criterion judgments. One
flawed-audit judgment reached its wall-time guard before a fresh assessment of the same output
passed. The clean-control fixture's shared post-Apply defect is corrected and rechecked.

All 384 framework tests pass, with lint, formatting, strict typing across 60 files, all 130 case
definitions, and JavaScript syntax checks. Independent intent and engineering correction reviews
pass. Finished raw evidence was inspected and reviewed, then removed before delivery.
