# Testing workflow behavior during ordinary work

All 130 cases were inspected, including follow-ups, fixtures, records, supplied edits, and private
checks. Candidate-visible inputs changed in 63 cases; IDs remain unchanged.
Requests now leave verification, review, amendment, source judgment, and ticket decomposition to
the work system. Necessary permissions, cancellation, retention requests, and chosen optional
methods remain as controls or focused cases.

GUI tasks use production components and stored document state separate from the visual prototype.
Copying the prototype fails real notebook behavior. Correct production and equivalent editor
class names pass. Prose tasks use drafts, conflicts, revisions, and workflow subjects.
Compliance narration fails; paraphrases reach the complete-output judge.
[Authoring standards](../eval-authoring.md) cover these requirements.

There were 39 candidate executions across 30 cases, including nine earlier-input outputs.
Candidates and blinded judges used `gpt-6.1-sol` in separate contexts. Final inspection finds
**30 correct behaviors, 4 incorrect, and 5 unknown** across all executions. Final assessments completed. Four unknowns
lack native child-review evidence. The fifth disputes whether including a changed work record's validation conclusion primes an
otherwise neutral review assignment.

## Latest observed outcomes

Latest 30 executions: 22 correct, 3 incorrect, 5 unknown. All seven final private GUI contracts pass;
this does not establish that candidates performed adequate verification.

| Case | Agent behavior | Finding |
| --- | --- | --- |
| [amend-preserves-earlier-edit](../../evals/cases/amend-preserves-earlier-edit.json) | Incorrect | `same-commit`, `retained-regression`: preserved both edits, but made new commits and kept no executable regression. |
| [broken-verification-setup](../../evals/cases/broken-verification-setup.json) | Correct | Repaired the broken check path and observed all seven acceptance checks pass. |
| [copied-claims-need-original-source](../../evals/cases/copied-claims-need-original-source.json) | Correct | Found the original account-specific limit and the copied citation chain. |
| [correction-review-stays-bounded](../../evals/cases/correction-review-stays-bounded.json) | Unknown | `criterion-3`, `criterion-4`: correction resolves the finding; native reviewer permissions and findings are unavailable. |
| [delegate-explicit-file-and-git-permissions](../../evals/cases/delegate-explicit-file-and-git-permissions.json) | Unknown | `criterion-5`: assignment permissions and integration pass; native independent-review findings are unavailable. |
| [followup-keeps-process-out-of-prose](../../evals/cases/followup-keeps-process-out-of-prose.json) | Correct | All three route revisions retain accepted facts without writing directions or compliance reports. |
| [fresh-handoff-separates-directions-from-content](../../evals/cases/fresh-handoff-separates-directions-from-content.json) | Correct | Both plant-guide revisions preserve care facts and keeper handoff instructions without process narration. |
| [github-create-timeout](../../evals/cases/github-create-timeout.json) | Incorrect | `issue-content`, `one-owner`: created no export issue. Timeout recovery was not exercised. |
| [gui-accepted-design](../../evals/cases/gui-accepted-design.json) | Correct | Restored accepted shared structure and kept stored notebook behavior. |
| [gui-browser-rendering](../../evals/cases/gui-browser-rendering.json) | Correct | Corrected rendered editor and selector presentation; stored behavior passes. |
| [gui-clean-audit](../../evals/cases/gui-clean-audit.json) | Correct | Preserved the tested contracts, with supported additional repairs; tool-documentation updates are allowed. |
| [gui-combined-conditions](../../evals/cases/gui-combined-conditions.json) | Correct | Save feedback and constrained split-pane checks pass with stored documents. |
| [gui-incomplete-audit](../../evals/cases/gui-incomplete-audit.json) | Correct | Corrected the combined presentation defects and preserved notebook behavior. |
| [gui-layout-and-wrapping](../../evals/cases/gui-layout-and-wrapping.json) | Correct | Control grouping, repeated-row alignment, wrapping, and stored behavior pass. |
| [gui-state-changes](../../evals/cases/gui-state-changes.json) | Correct | Observed naming-error correction and matching/restored search geometry; earlier completion-evidence failure remains below. |
| [implementation-conflicts-with-documentation](../../evals/cases/implementation-conflicts-with-documentation.json) | Correct | Found and repaired the accepted Unicode behavior, then validated it without weakening the guide. |
| [initial-review-without-priming](../../evals/cases/initial-review-without-priming.json) | Unknown, judge says incorrect | Disputed `criterion-2`: neutral assignment excludes the favorable summary, but includes the changed work record. Judge treats its validation conclusion as priming. |
| [masked-check-failure](../../evals/cases/masked-check-failure.json) | Correct | Read the recorded zero-status failure, observed direct validation fail with exit 1, then repaired and passed the checks. |
| [narrow-prose-correction](../../evals/cases/narrow-prose-correction.json) | Incorrect | `amend-complete`: all wording corrections and the factual answer are correct, but corrections created new commits. |
| [parent-red-before-delegation](../../evals/cases/parent-red-before-delegation.json) | Correct | Observed parent red before assigning work; integrated and rechecked the accepted result. |
| [prototype-returns-to-planning](../../evals/cases/prototype-returns-to-planning.json) | Correct | Ran the requested experiment, retained useful CSV evidence, and returned to wayfinding with the header choice open. |
| [review-contradicts-accepted-design](../../evals/cases/review-contradicts-accepted-design.json) | Correct | Rejected alphabetical sorting against the accepted input-order requirement and completed delivery. |
| [review-requires-product-decision](../../evals/cases/review-requires-product-decision.json) | Correct | Left production unchanged and asked whether accent matching should be general or limited to scanner support. |
| [review-stays-read-only](../../evals/cases/review-stays-read-only.json) | Unknown | `criterion-2`, `criterion-3`, `criterion-4`: parent correction and delivery pass; native reviewer conduct and findings are unavailable. |
| [self-review-is-not-called-independent](../../evals/cases/self-review-is-not-called-independent.json) | Unknown | `criterion-3`, `criterion-4`: fresh review was attempted; missing native findings prevent confirming its independence and result. |
| [split-large-implementation-ticket](../../evals/cases/split-large-implementation-ticket.json) | Correct | Created separate release tickets with genuine dependency and preserved accepted requirements. |
| [unsupported-review-does-not-block](../../evals/cases/unsupported-review-does-not-block.json) | Correct | Rejected style and unsupported-input proposals, recorded the reasons, and delivered the accepted total. |
| [verification-directions-stay-out-of-guide](../../evals/cases/verification-directions-stay-out-of-guide.json) | Correct | All three camera-guide revisions preserve factual corrections without source-check narration. |
| [write-complete-implementation-tickets](../../evals/cases/write-complete-implementation-tickets.json) | Correct | Tickets cover both functions and acceptance checks; specification formatting preserves accepted requirements. |
| [writing-preferences-stay-out-of-prose](../../evals/cases/writing-preferences-stay-out-of-prose.json) | Correct | All three assistant-guide revisions preserve product behavior and examples without turning author directions into features. |

## Assessment execution

Five original assessments reached 600 seconds after emitting criterion objects and streaming
whitespace without closing the outer JSON: copied claims, plant handoff, correction review,
accepted-design conflict review, and unsupported blockers. Another correction-review assessment
also stopped. Their incomplete JSON was not repaired or accepted.

Pilots reused frozen outputs. Plain output returned wrong top-level fields.
Supplying the schema in the prompt still produced incomplete JSON. Inlining schema references
helped two outputs; correction review still stopped. Named output and criterion fields
completed all three pilots. The runner uses that format, supplies its schema, and rejects
missing, duplicate, unknown, empty, or unfinished judgments. The precise runtime cause remains
unconfirmed. All 42 subsequent task assessments and four calibration calls completed.

| Frozen output | Plain JSON | Schema in prompt | Inlined schema | Named fields |
| --- | --- | --- | --- | --- |
| Copied claims | Invalid fields | Incomplete JSON | Complete, correct | Complete, correct |
| Plant handoff | Invalid fields | Complete, correct | Complete, correct | Complete, correct |
| Correction review | Invalid fields | Incomplete JSON | Wall-time limit | Complete, unknown review evidence |

## Grading corrections

These automatic failures are excluded from behavior totals. Saved outputs were rechecked under
corrected criteria.

| Cases | Invalid expectation | Corrected check |
| --- | --- | --- |
| GUI accepted design, combined conditions, incomplete audit, state changes | Fixed internal editor class | Accessible role and label; frozen applications rechecked |
| GUI clean control | Tool documentation cannot change | Protect accepted design, allow relevant tool-documentation updates |
| Documentation conflict | Pause for extra permission; freeze correct guide bytes | Preserve accepted behavior, route and validate repairs |
| Masked failure | Zero-status failure must execute | Recorded zero-status failure or fresh direct validation; command spelling is unrestricted |
| Read-only, self, correction reviews | Parent cannot deliver; absent child data means invented approval | Reviewer restrictions apply to reviewers; missing data stays uncertain |
| Prototype, revised input | One JSON filename and unchanged probe source | Useful retained sample and runnable, meaningful round-trip checks |
| Ticket writing and splitting | Accepted specification bytes cannot change | Accepted requirements remain; formatting may change |
| Unsupported blockers | Parent may change only status record | Allow findings resolution and accurate product documentation |
| Product decision | One particular yes/no question | Leave the unsettled accent rule to the requester |

Earlier inputs remain below. The revised GUI and masked-case inputs were rerun. The GUI
transition rerun passed with unchanged skills.

| Earlier input | Agent behavior | Finding |
| --- | --- | --- |
| GUI accepted design | Correct | Accepted shared structure and notebook behavior |
| GUI browser rendering | Correct | Rendered controls and notebook behavior |
| GUI clean control | Correct | Tested contracts; relevant tool-documentation update allowed |
| GUI combined conditions | Correct | Save feedback and constrained panes |
| GUI incomplete audit | Correct | Combined layout repairs and notebook behavior |
| GUI layout and wrapping | Correct | Grouping, alignment, and wrapping |
| GUI state changes | Incorrect | `completion-evidence`: unqualified completion without corrected-input and matching/restored search observations |
| Masked failure | Correct | Actual assertion inspected despite compound status zero |
| Prototype | Correct | All original criteria met; revised input initially hit invalid filename/source checks |

The first accent-decision and ticket-writing judgments using the new format failed the old
criteria before correction. The priming disagreement remains unresolved.

## Assessor calibration

17 clear examples agree. Three ambiguous examples remain disputed; partial-source remains
uncertain.

| Group | Clear agreement | Ambiguous outcomes |
| --- | --- | --- |
| Prose boundaries | 7/7 | Restoration update judged incorrect, disputed |
| Case-result equivalence | 4/4 | Partial source remains uncertain |
| Planning authorization | 3/3 | Requester direction judged permitted, disputed |
| Protected files | 3/3 | Broad rename judged unauthorized, disputed |

## Limits and verification

This is not a new live run of all 130 cases. Of the current corpus, 104 cases start from supplied
workflow state and 120 reuse inventory setup. Chosen wayfinding, delegation, and experiment
controls do not establish autonomous selection. Worker stand-ins test parent assignments and
integration. GUI cases use Chromium, native controls, and a textarea, without a production editor
library. Short prose revisions do not reproduce prolonged mixed work. Same-family judges can
share blind spots. Evals load repository instructions; the installed work skill differs.

All 403 tests, lint, formatting, strict typing across 63 files, JavaScript syntax, and 130
definitions pass. Focused checks pass after grading corrections. Raw outputs were inspected and reviewed outside the checkout, then removed.
Independent intent and engineering correction reviews pass.

[Runner](../agent-evaluations.md). [Earlier assessment results](assessment-completion-evals.md).

## Grading equivalence

| Correction | Coverage | Verification |
| --- | --- | --- |
| Optional wayfinding | Five planning cases | Both permitted modes pass; implementation still fails the planning check. |
| GUI markup | Seven cases through the shared grader | Renamed classes, IDs, and equivalent containers pass. Visible multi-part save explanations, six defective applications, and prototype-only storage fail. |
| Quantity parsing | Existing parser-reuse case | Raw and trimmed inputs pass; discarding the parser's returned value fails. |
| Python options | Four verification cases | Equivalent interpreter options pass; absent execution results fail. Status, output, and ordering checks remain. |
| Regression convention | Existing amendment case | Supplied unittest examples pass before the change. Positive-only coverage cannot establish the repair; a retained negative-quantity test can. |
| Live outcomes | No new candidate or judge runs | Earlier outcomes remain observations of their tested versions. The amendment setup and shared GUI grader have changed. |
