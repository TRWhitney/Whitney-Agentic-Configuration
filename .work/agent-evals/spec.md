# Evaluate agent workflow behavior

## Problem Statement

The existing tests exercise navigation commands and saved files. They do not establish whether
an agent follows the workflow, respects a requested edit, or restores wayfinding after losing
conversation context. Repeated skill changes need comparable behavioral evidence.

## Compaction hooks

Codex and Claude Code run one shared work-system recovery command after compaction. It restores
the active conversation's workflow, substate and existing work-record link. Normal record updates
preserve accepted decisions and the next action before context is lost. Recovery must reuse that
record and retain evidence whose inspection or review remains unfinished.

Application-specific setup registers the documented hooks and preserves other configuration.
Keep shared workflow instructions independent of the application. Missing or damaged saved state
must not cause guessed replacements or changes to another conversation.

Use confirmed native Codex compaction for behavioral comparisons. Cover changed planning answers,
supplied planning records and pending review evidence. Repeat the final version three times per
case/control with gpt-6.1-sol candidates and a separate blinded judge, keeping definitions and
allowances fixed. Test both applications' hook contracts; distinguish those checks from native
execution. Keep existing runtime/model pins and installation boundaries.

## Solution

Build a corpus of cases with shared setup, conversation execution, checks, and results. Start
with native Codex execution through its official Python SDK. Routine runs include recovery from
supplied state. Real compaction runs only when explicitly selected.

## User Stories

1. As a skill maintainer, I want to compare instruction versions on the same cases before
   accepting a change.
2. As a case author, I want to reuse fixtures and checks as the corpus grows.
3. As a reviewer, I want to see each failure, the tested instruction version, and reported usage.

## Implementation Decisions

### Case definitions

Store cases outside deployed skill packages. Each case has a stable ID, tags, project files,
conversation steps, and checks. Validate every case before execution. Reject duplicate IDs,
unknown fields, unsafe paths, invalid check references, and integration steps in routine cases.

Steps identify their conversation, so one case can exercise independent conversations in the
same project. A message step supplies ordinary user input. A seed step creates saved workflow
progress through the navigator before the agent acts. A compact step requests real compaction.
Only setup files and normal task instructions reach the agent; check definitions stay with the
runner. Case IDs and evaluation terminology do not appear in generated project paths.

Use JSON case files. Message steps contain a prompt and checks. Seed steps contain workflow,
state, optional substate, and a relative work-record path. Compact steps name the conversation
to compact. Checks use a declared kind and the arguments for that kind; arbitrary code is not
accepted in case files. Validate definitions with Pydantic and publish its generated schema.
Named fixture files share project content across cases. Case files can override individual files.
Optional `uncommitted_files` apply after the initial project commit. File checks use their
contents as the starting state; the commit retains the original files.

Use source snapshots for instruction variants. Keep each variant's project, Codex home, and
conversation state separate. Apply the same case and model settings to each variant and repeat.
Identify results by case, variant, and attempt. Report source revisions and SDK/runtime versions.

### Execution

Pin the official Codex Python SDK as an optional evaluation dependency. Reuse its native thread
and event APIs. Keep SDK calls behind one adapter; case validation and checks run without it.
Use existing file-based Codex credentials in an isolated temporary home. Missing credentials or
unsupported runtime behavior produce an execution error rather than a passing case.

Copy the subject skills and global instructions into that home. Keep source files unchanged.
Create disposable Git repositories with fixed example identities. Allow writes to their Git
metadata so amendment and tracker-change checks can observe agent behavior. Use local service fixtures
with configurable planning PR states and issue content for GitHub cases. Disable network access
for agent tools and Apps integrations in each runtime configuration. Reject unexpected
external-service tool results. Record service-call attempts so checks can detect publication
requests without sending them to GitHub.

The command supports validation, listing, case/tag selection, repeated attempts, instruction
variants, and a required model for live runs. Default to sequential execution. Model calls are
explicit and remain separate from the ordinary unittest command.

Expose `python -m evals validate`, `list`, and `run`. Live execution requires `--model` and accepts
`--case`, `--tag`, `--repeat`, `--variant NAME=SOURCE`, `--integration`, `--timeout`, `--max-tokens`,
and `--report`. A source is a directory containing the subject skills and global instructions.
Without variants, run the current source once. Reports must be outside the checkout.

Bound each attempt by elapsed time. Allow an explicit cumulative token guard; disable it by
default. A completed answer remains available if a later usage notification crosses the guard.
Preserve observed work on interruptions and stop further turns when an explicit guard is reached.
Usage notifications are not an exact billing ceiling. A timeout, missing usage,
failed turn, or incomplete compaction must remain distinguishable from a failed behavioral check.

### Recovery and compaction

Routine recovery starts a fresh conversation with saved planning/wayfinding state, a linked
work record, and a short handoff. The agent must recover the current question and response
format. This case makes no claim about the compactor's choice of retained information.

The integration case establishes wayfinding in a short conversation, explicitly compacts that
same conversation, observes a matching completion event, and continues. Reuse the recovery
fixture and checks. Never fill a context window to induce compaction.

Confirm the completed `contextCompaction` item and its matching completed turn. The pinned SDK
routes these events into turn queues before its public notification reader can see them. Use
one adapter override of its notification conversion method to observe them before routing.
Check that override against the pinned SDK when updating the dependency.

### Checks and results

Share checks for unchanged files, exact expected edits, replies matching required patterns,
saved workflow state, service-call attempts, and Git history. Check file patterns as well as
exact content so cases can verify saved decisions without fixing their wording. A missing file
fails either a required or an absent-pattern check. Evaluate checks after their
specified steps, not only at the end. Treat a failed required check as a failed case.
Command-result checks match exit codes and optional output in execution order within the current
message. Prepared Python checks run the starting script against the current project in an
isolated Python process with a ten-second timeout. They use the runner's saved copy, so edits
to the project's script cannot weaken the check. Scripts use the project working directory
to locate code and do not rely on their own file location.

Regression-test checks copy the current project and run its unittest suite against current
and initial source. They require tests to run, pass the repair, and fail the initial code by
assertion rather than a test error. Completion checks require saved progress to be absent.

Unchanged-directory checks include newly added files outside explicitly excluded paths.
Publication checks can target all writes or only PR writes, including REST API calls. Allowed-change checks compare the full
tracked and unignored project against its initial files. Commit-count checks also require no
uncommitted changes to tracked files, so an uncommitted edit cannot satisfy an amendment check.

Keep outputs as structured observations so checks do not depend on Codex event formatting.
Report pass, fail, execution error, and limit reached separately. Preserve individual results
alongside aggregate counts; never average away a prohibited action. Write concise results on
request, outside the checkout. Delete temporary homes, projects, credentials, and raw transcripts
after inspection. Retain case definitions, reusable checks, and concise measured conclusions.

## Testing Decisions

Use fixture-based tests with known passing and failing observations for every check. Exercise
case loading, selection, variants, repeats, isolation, cleanup, interrupted execution, missing
usage, and compaction acknowledgement without completion. Use a fake SDK boundary for protocol
and error tests. Run a short native case to verify the adapter; report observed behavioral
failures without changing the subject instructions to force a pass.

The starting corpus covers:

| Case | Required behavior |
| --- | --- |
| Incomplete design | Stay in planning despite an independent implementation ticket |
| Planning PR not merged | Keep production code unchanged while required planning delivery remains unfinished |
| Local tracking | Discuss GitHub guidance without changing tracker or publishing |
| Seeded wayfinding recovery | Restore the linked question and response format from supplied progress |
| Narrow correction | Answer a wording question before editing; apply only the approved edit and amend the existing local commit |
| Separate conversations | Restore each conversation's own workflow in one project |
| Explicit compaction | Preserve wayfinding through confirmed native compaction; integration only |
| Wayfinding follow-up | Keep the response format on the next question without compaction |
| Short wayfinding replies | Keep the response format through brief questions such as "Why?" |
| Wayfinding counts | Update progress when an answer settles a decision and retain it on a later recap |
| Stop wayfinding | Remove the substate and its progress line while keeping planning active |
| Revised answer | Replace an accepted decision in the design and map without increasing the decided count |
| Blocked question | Count only unblocked questions as ready, then update readiness when a prerequisite is settled |
| Code question during wayfinding | Answer from the current code, keep the decision open, and return to it on the next reply |
| Question before a change | Discuss a possible behavior change without editing files |
| Amendment preserves earlier work | Keep an earlier approved edit when applying another correction to the same commit |
| Missing implementation ticket | Identify missing ticket coverage even when the design is accepted |
| Continue planning discussion | Treat agreement to continue discussion as distinct from an answer to an open decision |
| Tracker across conversations | Keep the repository's selected tracker when other conversations discuss GitHub |
| Finish wayfinding | Save the last answer and leave wayfinding while specification and ticketing remain in planning |
| Changed decision and dependent tickets | Update every affected design and implementation record while preserving other work |
| Outdated recap | Restore accepted decisions and the open question from saved sources despite an older, conflicting recap |
| Prototype returns to planning | Run the prepared experiment, record findings, and return to the unanswered product decision without changing production code |
| Related feature questions | Keep new and existing questions in their feature's planning record without creating extra tickets or accepting unanswered choices |
| Partial completion | Report unfinished export work and keep the workflow active after search is complete |
| Ready implementation | Start the requested implementation after accepted design and complete ticketing |
| Existing uncommitted work | Preserve edits to a tracked file and an untracked draft when resuming implementation |
| Replace a workflow | Replace one conversation's task, preserve the other conversation, and retain the replacement on return |
| Failed verification | Observe the failing acceptance check, repair the defect, and pass the checks before delivery |
| Unavailable verification | Distinguish passed local checks from missing release verification and keep validation pending |
| Reproducible bug | Reproduce the reported failure, record its cause, repair it, and pass the retained regression checks |
| Write a regression test | Retain a test that fails by assertion on the original code and passes on the repair |
| Rerun after correction | Run affected checks again against the corrected implementation |
| Complete local work | Validate, review, document, commit, update the work record, and clear the workflow |
| Closed planning PR | Keep implementation blocked when planning was closed without merging |
| Merged planning PR | Start implementation when accepted planning documents are merged |
| No planning document PR | Start accepted work without creating an empty planning PR |
| Correction without a reminder | Rerun affected checks after an ordinary wording correction |
| Review finding | Repair the finding, rerun checks, preserve earlier work, and amend the local commit |
| Diagnosis needs design | Return to planning and ask about unresolved intended behavior |
| Resume stale validation | Recheck changed code despite a saved passing result and repair the observed failure |
| Choose ready work | Select an eligible ticket by dependencies rather than ticket number |
| Requirements change during implementation | Reopen affected planning, block the unfinished ticket, and preserve completed work |

## Further coverage

The expanded corpus also checks conflicting planning records, authored and divided tickets,
reversible implementation choices, evidence that changes a design, and wayfinding entered
through conversation. Discussion cases cover several answers, partial answers, dependent
answers reopening, and return from research.

Recovery covers agent-created state through explicit compaction, missing work records, damaged
navigation data, cancellation, completed conversations starting new work, and shared documents
across conversations. Implementation cases cover blocked or cyclic dependencies, missing
prerequisites marked done, and completing dependent tickets.

Validation and delivery cases cover a failed check hidden by shell success, broken check setup,
incomplete evidence, rejected or decision-bearing review findings, edits after review, outdated
planning delivery, unavailable service reads, uncertain issue creation, persistent issue edits,
exact prose corrections, documentation conflicts, no documentation impact, and prototype retention.

Edit steps change files, remove files, or replace navigation text between turns without changing
comparison baselines. Navigation-text checks detect replacement of damaged saved data. Service
state checks inspect saved issue or PR counts and body content independently of replies.

## Procedure guidance cases

Further cases check regression tests that fail for the wrong reason, public-command coverage,
independent expected results, and tests that exercise real project behavior. Commit cases check
independent result grouping, completed work across the tree, explicit uncommitted exceptions,
and an installed hook that blocks delivery. Other cases check read-only review, supplied clocks,
error causes with safe consumer messages, and preserving reasons for replaced architecture decisions.

Commit-group checks compare changed paths per new commit, preserve initial history, and verify
the exact set of uncommitted paths. Hook setup references a supplied project file and installs it
only after the initial fixture commit.

Further guidance cases cover unsupported review blockers, removal of obsolete export paths,
reuse of an existing quantity parser, proposed domain terms, and links to shared definitions.
Research cases check original sources behind copied claims and distinguish conflicting versions
and account limits using supplied local excerpts.

Assignment cases use a local delegation stand-in to inspect submitted sources and permissions,
detect priming, and check that the parent observed a failing test before delegation. Shared
action sequences preserve command and submission order. Further cases check a bounded direct
correction review and integration of a supplied child handoff with an incorrect implementation.

Prose cases distinguish directions for doing the work from content intended for readers across
several subjects and output types. Shared prose checks require subject content and detect
specified process claims in saved files. Cases include later edits, a supplied fresh-context
handoff, requested methods, useful uncertainty, accurate verification claims, review identity,
protected files, limited permission, selective cleanup, and quoted source directions.

## Corpus assessment

Revise the existing 116 cases in place. Keep their identifiers and intended behavior coverage.
Each case supplies an ordinary task, genuine constraints, and the project evidence needed to
understand it. The installed skills supply the work process. Remove process reminders from
prompts, handoffs, project records, and prepared source excerpts. Keep factual prior decisions,
unfinished work, real tool documentation, and deliberate user restrictions.

Give every existing case three to six hidden criteria for useful output and the skill behavior
it exercises. File outputs are declared when relevant; a question may require only a reply.
Keep exact content checks for actual exact-edit contracts. Check implementation behavior rather
than source equality. Use semantic assessment for prose, accepted decisions, and review findings.
State and action checks must follow required workflow behavior without imposing an arbitrary
stopping point or a particular implementation, sentence, question order, or decision count.

Keep shared project fixtures where they serve the same purpose. Prepared process and artifact
graders stay outside the candidate project through private grading files. Ordinary project tests
and executable validation tools remain available. Exclude ordinary generated caches from
source-preservation checks while continuing to detect added, removed, or changed source files.

Retain isolated blind assessment, complete artifact and action capture, calibration,
explicit candidate and judge models, source-variant comparison, per-case audits, and result
reporting. Include confirmed compaction events and the current local service-fixture records
when they are relevant evidence for an existing case. The judge receives shuffled outputs after writing ends, with no run identities or
expected verdicts. Preserve every required code failure, execution error, and allowance limit.
Missing evidence is uncertain unless observations establish a contradiction. A case with hidden
criteria cannot receive an overall pass from code checks alone.

Use one request sequence per case. Compare skill versions with that same request and context.
Remove the redundant six-case pilot and prompt-reminder comparison. Keep the independently
authored calibration examples as tests of the assessor. Candidate and judge use gpt-6.1-sol for
this revision; another family can use a supported execution adapter later.

Validate coverage across all original identifiers, inspect every revised prompt, supplied record,
criterion, and objective check, and exercise representative existing cases through live judging.
Separate live coverage from offline infrastructure checks and unrun cases. Retain actual subject
failures rather than changing skills or expectations to obtain a pass. Real compaction remains
an explicitly selected integration check; routine cases use short conversations.

Keep authoring standards separate from deployed skills. Update runner documentation and one
concise method report with the resulting corpus, observed behavior, corrections, and limits.

## Evidence retention

Assess whether useful evidence remains available until diagnosis, inspection, and required
review finish, while raw outputs stay outside the checkout and never enter Git. Keep concise
case outcomes and reasons after raw outputs are removed. Aggregate totals alone do not preserve
the result of an evaluation batch.

Add task cases for results surviving cleanup, evidence needed by a pending review, and a failed
attempt needed for diagnosis. Add a control for explicitly requested retention. Exercise pending
evidence across one explicit short compaction as an integration variant. Reuse existing
correction coverage rather than adding another correction case.

Extend the existing selective-cleanup and accepted-prototype cases. Include ignored captures,
archives, supplied data, reusable checks, and reproduction steps. Retain useful sources and
findings while removing finished raw outputs. Check renamed copies and commits later replaced
by amendment, not only the final tree.

Use shared disposable storage outside each candidate checkout, per-step file observations,
and private Git checks. Ordinary requests and supplied records describe the actual work without
retention reminders. Judge complete saved conclusions and observed actions. Retain a compact
outcome and explanation for every live case and criterion before deleting raw review evidence.
Do not change the subject skills for this addition.

## Corrections and assessment examples

Extend three existing cases without changing their identifiers. Wording corrections should
preserve earlier accepted edits across several narrow follow-ups. The amendment case must
retain a regression test for the quantity fix after a later message correction. The photography
case should revise an existing guide and then change example placement, with source-checking
directions kept out of both reader-facing versions.

Add independently labeled assessor examples for equivalent case-result wording, planning
authorization, and protected-file permission. Include correct work, actual violations, and
genuinely ambiguous evidence. Use replies and complete artifacts as evidence, without exposing
expected labels or their reasons to the assessor. Do not resolve an ambiguous permission policy
by assigning a definite label.

Keep ordinary task requests, hidden semantic criteria, reusable code checks, and short runs.
Use gpt-6.1-sol for candidates and blinded assessment. Preserve all case and calibration outcomes,
disagreements, limits, and exclusions before deleting temporary outputs. Leave subject skills
and runtime integrations unchanged.

## GUI verification and follow-up coverage

Add ordinary implementation and audit tasks for adherence to an accepted runnable design,
rendered browser behavior, state changes, combined conditions, and layout. Layout coverage
includes alignment, spacing, visual grouping, wrapping, repeated controls, and changing content.
Use reconstructed project interfaces, not a claimed replay of Linkwrite. Supply accepted design
requirements and permitted variation as project context. Do not name hidden defects or prescribe
verification steps in the task requests. Include a correct interface as an audit control.

Reuse a browser fixture and observation support. Use existing local browser dependencies without
installing software. Observe real interactions, screenshots, and layout measurements. Give the
blinded judge read-only image and text files. Keep the candidate's observed checks
separate from private grader checks; grader observations cannot establish that the candidate
performed verification. Missing images or unavailable browser execution cannot count as success.
Keep screenshots, journals, and run records outside the checkout until inspection and review end.

Complete the previously accepted follow-up cases: separate conversations with different pending
evidence, supplied input beside finished generated output, a factual terminology question during
editing, and reports that distinguish failed, successful, and timed-out attempts. Extend existing
cases where their behavior matches. Keep subject skills and configuration unchanged. Preserve each
live outcome and its limits before removing temporary outputs.

## Assessment completion

Give the blinded judge a small index of complete output files, transcripts, browser observations,
and images. Use a read-only workspace and verify that its evidence remains unchanged. Keep
run identities, model names, earlier scores, and source conditions outside that workspace.
Remove custom reference-table decoding and packet-size rejection from assessment.

Keep observed replies and actions when candidate or judge execution stops. Record phase time,
reported token breakdowns, and available context-window size. Report behavior as correct,
incorrect, or unknown, separately from whether assessment completed. A failed assessment cannot
erase a confirmed behavioral failure or establish success.

Validate the existing assessor examples and rerun both GUI audit cases whose prior assessments
did not finish. Inspect the complete outputs and relevant actions, reconcile the independent
verdicts, retain per-attempt findings, and remove finished temporary evidence. Keep the corpus
identifiers, rubrics, and subject instructions unchanged.

## Unprompted workflow behavior

Audit all 130 cases, including shared fixtures, saved records, follow-ups, and supplied edits,
against the private behavior targets. Remove requests that supply the verification, review,
amendment, ticket decomposition, source judgment, or conflict handling being tested. Keep the
product result, accepted requirements, actual history, tool contracts, and necessary user inputs.
Optional choices must not become mandatory merely because an old prompt selected them.

Replace the GUI prototype-copy repairs with component and state integration work whose production
data flow cannot be satisfied by copying the reference. The former audit cases use ordinary
feature completion. Strengthen existing prose tasks with drafts, mixed factual evidence, meaningful
follow-ups, and workflow subject matter. Preserve earlier accepted content and assess all saved
versions. Keep the same case identifiers and shared runner; do not create another suite.

Extend authoring guidance and corpus inspection to expose process cues without treating keyword
matches as semantic verdicts. Validate negative and correct implementations and inspect live
outcomes from changed cases. Retain concise case outcomes, gaps, and invalidated earlier results.
Leave the subject skills, global configuration, dependencies, and installations unchanged.

## Connections and continued work

Add ordinary tasks for save/load disagreement hidden by mocked project components, a shared
UI change affecting an existing second view, obsolete operator commands beside a working
program, and a feature request that needs product decisions without a supplied planning state.
Assess real behavior and retained coverage while allowing different valid implementations.

Extend the existing agent-created compaction case with an accepted answer, relevant source
analysis, and a later changed answer before explicit compaction. Recover the latest decision
and unfinished choice. Extend the existing transfer-guide case with an access-source question
between revisions. Apply its useful facts without turning research or author directions into
reader-facing process narration.

Reuse the current runner and independent assessment. Check correct and faulty outputs, record
per-case behavior and assessment completion, and remove raw evidence after inspection and review.
Keep subject skills and configuration unchanged.

## Procedure decisions

Add six ordinary tasks for an unconfirmed reported bug, incidental test coupling during a
behavior-preserving refactor, an operable comparison before prototype acceptance, keyboard
controls and focus, research without sufficient original evidence, and amendment based on the
session that created the commit.

For the commit case, preserve an earlier-session commit, create a new result in the conversation,
publish it through a disposable local remote, explicitly compact, and correct that same result.
The correction amends the current-session commit even though it was pushed. Update only the
conflicting commit-procedure paragraph. Add the missing same-session history to existing
amendment cases without supplying the amendment action in their requests.

Reuse browser execution and blinded assessment. Permit a prototype's chosen output path without
requiring a private visual contract. Extend browser actions with keyboard presses and retain
observable Git history around fixture publication. Keep external publication and installations
outside this work. Preserve per-case behavior outcomes and assessment completion separately.

## Further procedure decisions

Add three tasks for an order-dependent test failure, an implementation worker whose supplied
focused test passes without covering the assignment, and a credible existing data-loss finding
outside the change being delivered. Extend interactive-prototype-comparison with a runnable
failed revision and two documented earlier attempts. Extend gui-browser-rendering with accepted
light and dark appearances and switching while editing.

Keep the ordinary task requests and private assessment separate. The worker receives a runtime
role and normal parent assignment, not advice about the invalid test. The data-loss case supplies
an engineering finding for verification and handling; it does not test unrelated-code scanning.
Prototype history is supplied context, not observed candidate work. Reuse the existing runner,
browser tools, evidence and blinded assessment. Validate correct and incorrect examples before
live runs, retain per-case outcomes and limitations, and remove raw evidence after review.

## Integration, measurement and acceptance

Add tasks for connecting individually working delegated results, assessing a measurement that
excludes part of the accepted operation, and verifying a contractual external-service exchange.
Extend the existing prototype task through selection, interpretation and explicit confirmation,
retaining required behavior separately from flexible sample content and colors.

Use ordinary task requests, complete source and private criteria. Supplied worker results test
parent integration, not worker performance or autonomous delegation. The performance question
allows a justified source-derived lower bound without requiring a particular benchmark command.
External service tests may use mocks, fakes or equivalent local services while executing real
application code. Keep subject skills unchanged, inspect live outputs and retain concise results.

## Main procedure paths and wayfinding judgment

Add tasks for creating a new interface design without an accepted visual reference, converting
existing local work to an explicitly selected GitHub tracker, completing a valid implementation
worker assignment, and carrying a whole research investigation into one existing report.
Add a wayfinding task that derives consequences from accepted requirements and concrete facts,
uses judgment for routine details, and leaves substantial unresolved product choices to Whitney.

Keep the procedure under test out of candidate reminders. Supply genuine project constraints,
accepted sources and necessary tool availability. Use the existing isolated model runner,
browser support, Git mirror and local GitHub substitute. Verify any additional service operations
against correct and incorrect controls before evaluating conversion. Cases preserve production
boundaries, accepted decisions and still-open choices. Do not change subject skills or install
services. Retain individual outcomes and evidence limits after raw evidence is reviewed and removed.

## Planning records and small clarifications

Update the specification and affected tickets before replying to changed requirements. Create
missing wayfinding records before the first question, link them from the existing work record,
and preserve damaged workflow state while stopping only the affected conversation.
Explain another tracker's record and delivery rules without changing the selected tracker.
Define the saved workflow state before using the term and retain the optional work-record link.

When restoration fails, show the selected tracker's work-record guidance path even when the
conversation state cannot be read. Keep record locations in the tracker guidance.

The negative-quantity investigation asks for a small behavior clarification within fix discovery.
It must no longer require a move to novel-work planning merely because that answer is missing.
Keep the supplied task and source-protection checks. Preserve the six cases' individual outcomes,
prior proposal results and remaining assessment defects.

## Wayfinding after answers

Compare current guidance with temporary changes for continuing after answers and reconsidering
answers affected by a revision. Use the existing multiple-answer, partial-answer, dependent-answer,
revised-answer and derived-choice cases with unchanged requests, fixtures and code checks.
Include the existing completion case to check that discussion ends when no design question remains.
Check that routine decisions still follow from accepted requirements. Keep context-clearing
cases outside this study. Retain individual outcomes and present any supported skill change
as a proposal before applying it.

The first comparison's criteria permitted a recap after corrections without the next question.
Tighten the two existing correction rubrics before further comparisons: the correction reply
must ask a useful next question. Preserve the existing allowance to reopen dependent feedback;
do not require a particular next question or repeat facts already available in the conversation.
Check the assessor against correct continuation and plausible substitutes before live trials.
Keep earlier results separate when correcting a criterion. Allow routine refusal wording while
rejecting false claims of user approval. Capture native file edits and distinguish candidate
changes from supplied edits. Reassess the same outputs when correcting evidence capture.

Test the complete proposal three times across the six cases and existing start, stop and
blocked-question cases. Inspect the saved records and replies. Apply the approved navigator,
guide and regression tests from the tested diff.

## Rework commits

Apply the [accepted commit guidance and navigator patch](../../docs/research/rework-commit-proposal.diff).
Fold corrections into an existing commit only when it was made in this session, has not been
pushed unless history rewriting was explicitly requested, and the changes correct or complete
the original work or materially improve and belong in the same logical unit of work.

Keep the folding conditions at the existing folding section. Identify session commits through
the navigator, then use the stated Git publication checks. Register successful commits in a
separate section. Navigator commands store and list commit IDs in the existing external
conversation state, separated by repository. They do not select amendment or check publication.
Keep IDs after workflow completion or cancellation. Amendments replace one recorded ID;
squashes replace multiple IDs. Removal and reset discard the affected recorded IDs. Preserve
unaffected IDs, repositories and conversations, locking, atomic writes, and damaged files.

Use existing rework cases without candidate reminders to amend or record commits. Prepare
existing conversation commits through the navigator. Remove the rejected requirement to retain
session or publication claims in Markdown and its calibration. Check actual history, exact
corrections, retained edits and regression tests, and saved commit IDs.

Extend the independent-commits case with a new independent feature after commits exist, then
explicit squash and reset requests. The new feature must create its own commit. The explicit
history requests test record updates, not autonomous choice of history edits. Keep unrelated
results separate and preserve commits outside this session. For pushed commits, create a new
commit unless rewriting is explicitly requested.

Exercise ownership, publication and rewrite controls without clearing context. Keep native
compaction deferred. Repeat the affected cases and controls on the final version. Change prose
only as needed to fix observed failures while preserving the accepted wording and design.
Keep all attempt outcomes and assessment status separate from framework validation.

## Eval reliability

Provide a reusable way to detect and repair faulty evals across the corpus. Normal completed
runs should yield an unambiguous behavior verdict. Distinguish an agent's omitted required
action from missing observations and ambiguous expectations. Repair evaluation defects without
weakening accepted behavior or changing subject guidance to satisfy a faulty assessment.

Enforce reliability in the eval tooling, with evidence-backed investigation and review for
repairs that affect intended behavior. Extend existing recording and assessment interfaces;
do not automatically rewrite criteria or subject instructions.

Verify per-attempt filesystem isolation before candidate or judge work. Grant minimum system
reads, the supplied project and skills, required local Git/state writes, and private scratch.
Deny shared temporary helpers and private criteria, block tool network access, and confirm the
selected native permission profile. Record setup validity separately from behavior. Check that
required work remains possible; a boundary that prevents legitimate work is an eval defect.
Reject raw output destinations inside Git or instruction-source checkouts at the storage API.

Record capture coverage and faults separately from candidate completion. Unknown recording
coverage cannot establish an omitted action. A complete relevant record can establish omission;
missing captures, unsupported tools, interrupted turns and unavailable child findings cannot.
Expose the cause of uncertain judgments and route them to capture repair, criterion review or
assessment investigation. Preserve independently observed failures even when another criterion
cannot be decided. A capture fault prevents an unsupported overall pass.

Calibration supports actions and recording conditions as well as artifacts, and exits
unsuccessfully on any disagreement or incomplete assessment. Keep expected labels and reasons
out of judge inputs. Include different valid approaches, real violations and unavailable
observations, including the current prototype and interface inspection requirements.

Provide read-only diagnosis of saved review evidence. An explicit `--diagnose` run option
starts one investigation on failed calibration or unresolved judgments. Inspect original requirements, observed
work and judgments; return cited findings and the appropriate repair, not an automatic verdict
replacement. Preserve previous scored assessments, errors and raw responses. Reassess saved work only when
the task and criteria are unchanged and evidence is sufficient. Assessment failures, uncertain
required judgments and collection warnings require a read-only review before reusing the observations.
Preserve original warnings; do not let an unsupported warning replace otherwise established
behavior. Missing relevant observations require a fresh comparison after capture repair.
Reports identify unresolved evaluation problems separately from behavior and assessment
completion, with the next repair or investigation needed. Keep original outcomes visible.

[Ticket 22](tickets/22-eval-reliability.md) covers implementation and verification.

## PR descriptions

Use the seven-section format from the accepted PR descriptions: Problem, What changed, Code
example, Why this was needed, Why this approach, Setup and limits, and Validation. End with the
relevant issue reference. A reader without project, technical or domain knowledge can understand
the change, why it matters, the example, the reason for the solution, and the setup, consequences,
limits and evidence. Links supplement the explanation. Small changes keep the structure and
necessary information. The shared rule belongs in GitHub delivery guidance.

Test an actual filed PR and a description-only correction through the disposable GitHub fixture.
Keep requirements private, check the published body, calibrate meaning separately from headings,
and compare fixed tasks and model settings against fresh baselines.

## Visual inspection coverage

Select rendered inspection states from supported actions, agreed requirements and accepted
prototypes. Use content and available space that can expose failures to see, understand or
operate the interface. Apply these checks during visual verification, and review whether required
inspections are missing from the evidence.

The conference-agenda task reconstructs the gap between passing data checks and uninspected
presentation: revealed descriptions, full locations and day navigation that exceeds the row.
Assess the useful finished application separately from the candidate's observed inspection.
Compare fixed tasks against fresh baselines and retain a correct-interface control.

## Out of Scope

Additional agent runtimes, automatic instruction changes, hosted
services, deployment of skill changes, and production GitHub operations are not part of this
version. A corpus author can add further cases using the shared definitions and checks.

## Further Notes

[Tool comparison](../../docs/research/agent-evaluations.md).
[Implementation tickets](status.md#progress).
