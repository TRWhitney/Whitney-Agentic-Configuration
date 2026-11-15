# Agent workflow evaluations

Cases under `evals/cases/` test agent behavior against a copy of the repository's instructions.
They share project setup, conversation execution, checks, and result reporting.
The [failure report](research/evaluation-failures.md) collects recorded failures, their reasons,
later passes, disputed judgments and checks needed for resolution.

The [baseline study](research/workflow-eval-baseline.md) records observed failures and tested
instruction changes. Cases cover planning, tracking, corrections, and wayfinding. The
[specification](../.work/agent-evals/spec.md#testing-decisions) lists their required behavior.
[Planning and rework results](research/workflow-boundary-evals.md) cover GitHub planning
outcomes, corrections without reminders, recovery with stale validation, dependency selection,
and returning to planning when requirements change.
The [corpus expansion](research/workflow-corpus-expansion.md) covers the further planning,
wayfinding, recovery, dependency, review, service-failure, and documentation cases.
The [procedure guidance cases](research/workflow-guidance-evals.md) cover test quality, commit
grouping and blockers, read-only review, supplied clocks, error handling, and decision history.
Those studies used earlier case definitions. The [assessment study](research/evaluation-methods.md)
records the revision of the existing corpus.
The [retention study](research/evidence-retention-evals.md) records evidence lifetime, saved
findings, and raw outputs staying outside Git.
The [correction study](research/correction-and-judgment-evals.md) records successive edits,
retained regression coverage, guide revisions, and assessor calibration.
The [ordinary-work revision](research/workflow-eval-realism.md) audits all 130 cases, strengthens
GUI and prose tasks, and records current outcomes and assessment-format checks.

The [connections and continued-work cases](research/workflow-connection-evals.md) add shared
component effects, real project connections, executable guide examples, workflow selection,
and longer decision and prose conversations.

The [procedure cases](research/procedure-decision-evals.md) cover unconfirmed diagnosis,
refactor test quality, interactive comparisons, keyboard use, insufficient research evidence,
and amendment across publication and compaction.
The [further procedure cases](research/procedure-followup-evals.md) cover test isolation,
invalid worker assignments, existing data-loss findings, repeated prototype feedback and
light/dark appearance.
The [integration and acceptance cases](research/integration-and-acceptance-evals.md) cover
combined worker results, complete measurements, required service interactions and confirmed
prototype requirements.
The [main procedure cases](research/main-procedure-path-evals.md) cover new interface design,
tracker conversion, successful worker implementation, complete research and planning judgment.
The [planning-state corrections](research/planning-state-corrections.md) record applied guidance,
the small-clarification case correction and remaining record/recovery failures.
The [study of damaged workflow state](research/damaged-state-recovery.md) compares recovery wording
and navigator hints pointing to the selected tracker's existing record guidance.
The [wayfinding answer trials](research/wayfinding-answer-trials.md) compare temporary changes
for continuation, dependent answers and progress placement. All nine final cases have three
correct results. The [tested diff](research/wayfinding-reply-proposal.diff) is applied.
Native file patches and completion status are captured alongside shell commands. Assessment
indexes list per-turn artifact additions, changes and removals, distinguishing supplied edits
from candidate turns.
The [rework commit trials](research/rework-commit-trials.md) passed all 27 final attempts, three
per case or control, with complete assessments. The [tested diff](research/rework-commit-proposal.diff)
is applied. Navigator commit records support amendment, squash, removal and reset.
That study deferred native compaction. The [compaction recovery trials](research/compaction-recovery-trials.md)
now exercise recovery through application hooks and preservation of the existing work-record link.
The [planning continuation follow-up](research/planning-continuation-trials.md) adds a private check
for the next question after each answer or correction, before compaction as well as after it.
The [instruction-justification follow-up](research/instruction-justification-trials.md) adds a
private writing criterion to the existing search-decision case without changing its request.
The [search judgment correction](research/search-judgment-correction.md) permits a reasonable
implementation while protecting the existing inventory contract with private checks.

The [project planning trials](research/project-decisions-trials.md) add seven cases for shared
agreements, support commitments, optional releases, versioning and changed plans. The study
preserves earlier failures and eval repairs; all 36 final attempts meet their selected criteria.

## Run cases

Install the optional runtime and validate the corpus without model calls:

```sh
uv sync --group eval
uv run --group eval python -m evals validate
uv run --group eval python -m evals list
```

Live runs require existing file-based Codex credentials under `CODEX_HOME`, or `~/.codex` by
default. Each attempt copies them into a temporary home and removes that home on exit.
Choose a model available to that account:

```sh
uv run --group eval python -m evals run --model MODEL --case seeded-wayfinding-recovery
uv run --group eval python -m evals run --model MODEL --tag planning --repeat 3
```

For the allowance used in the initial corpus check:

```sh
uv run --group eval python -m evals run --model MODEL --max-tokens 350000 --timeout 240
```

The two-edit amendment case completed with a larger allowance:

```sh
uv run --group eval python -m evals run --model MODEL --case amend-preserves-earlier-edit \
  --max-tokens 500000 --timeout 240
```

Without a case or tag, `run` selects all routine cases. Integration cases require
`--integration`, even when selected by name:

```sh
uv run --group eval python -m evals run --model MODEL --integration --case explicit-compaction \
  --max-tokens 350000 --timeout 240
```

To compare instruction versions, supply source directories containing `skills/`,
`config/global-agents.md`, and any declared external skills:

```sh
uv run --group eval python -m evals run --model MODEL --case incomplete-design \
  --variant before=/path/to/before --variant after=/path/to/after --repeat 3
```

Every attempt gets a separate project, home, and set of conversations. Cases with several
conversations share only that attempt's project. GitHub calls use a local `gh` fixture;
agent tools have network access disabled and Apps integrations are disabled for each attempt.
An unexpected external-service tool call invalidates the run. This tests publication attempts
and supplied tracker responses. `github_pr_state` selects `OPEN`, `CLOSED`, `MERGED`, or `null` for no PR.
`github_issue_body` supplies issue content. `github_issues` supplies separate bodies keyed by
issue number. `github_issue_labels` supplies their labels; omitted issues have no labels.
Issue edits and comments persist within an attempt. `github_read_error` makes reads
fail; `github_write_timeout` saves the first created issue but returns a timeout. These fields
change only the disposable fixture.
This does not test GitHub itself.

## Assess complete tasks

Use the [authoring standards](eval-authoring.md) when creating or revising evaluations.
All 171 cases have hidden criteria. Requests supply product goals; necessary user-selected modes
remain in focused cases and controls. Case identifiers remain in place. Focused checks and complete tasks answer different
questions. Select them with
`--purpose focused`, `--purpose task`, or `--purpose control`. The audit reports structural
counts and per-case facts without model calls. Include integration cases to audit the entire corpus:

```sh
uv run --group eval python -m evals audit --integration
```

The audit also lists process-language cues found in requests, resolved files, temporary evidence,
and supplied edits. Each cue includes its source and surrounding text. Inspect those cues against
the case's private question. They are not automatic findings; an available command or a genuine
user constraint may belong in the input.

Task cases provide three to six hidden criteria. Add `--judge-model MODEL` to assess their
finished files, final replies, observed actions, starting and changed tracker records, and
confirmed compaction events in a separate context. Supplied file updates are identified
separately from agent edits. Every selected case
must have a rubric. The judge gets all attempts and conditions for that case under shuffled
labels, after candidate writing ends. It receives the installed instruction snapshot as evidence,
but no expected verdicts, model names, condition labels, or earlier scores. It reads frozen evidence files in a read-only
workspace, using shell commands and image viewing. Delegation and evidence changes invalidate
the assessment. Available native child turns and status messages are included separately from
assignments. Structured model metadata is excluded from native child items.
Completion notifications retain their place among the parent's actions; child turns
are fetched after the parent turn. Candidate threads are stored only in the disposable runtime
home so their child turns can be read before cleanup. Judges remain ephemeral.
Missing assignment data or child findings identify an observation gap, not a failed child run.
A review claim without accessible findings remains uncertain.
Native review cases grade the recorded child actions. Their assignment permissions still apply,
but hidden assignment wording is ungraded. Local-service cases retain their assignment-content
checks because the service records the submitted text.

Run the existing corpus with independent assessment:

```sh
uv run --group eval python -m evals run --model gpt-6.1-sol --purpose task \
  --judge-model gpt-6.1-sol
```

The candidate and judge models are separate explicit settings. Current runs use the same model
family; a later run can select a different judge family through a supported adapter. The judge
defaults to 600 seconds with no cumulative token cutoff. Set `--judge-timeout` and
`--judge-max-tokens` to change them. Each case's outputs share one assessment call.

Native runs use a named [permission profile](https://learn.chatgpt.com/docs/permissions)
with minimum system reads and explicit access to the fixture, installed skills and private
scratch directory. `TMPDIR` points to that directory. Shared temporary files, other attempts
and private case definitions are unavailable. Candidate Git metadata remains writable; judge
evidence stays read-only. Preflight probes check outside-file denial, private scratch writes,
Git metadata access and blocked tool network connections. Startup verifies the runtime selected
the profile. A failed probe stops before model work; reports record `isolation_status` separately.
Linux native execution requires the existing bubblewrap sandbox; no package is installed.

When an installed work-system copy includes `compaction.py`, native candidates configure its
recovery hook in their disposable home. Before enabling it, the runner checks that the runtime
lists exactly that command and source, with no other hook. The pinned adapter uses the per-thread
`config.bypass_hook_trust` setting; it does not change persisted trust. Judges keep hooks disabled.
Completed hook events and their context are retained separately from agent commands. Native
compaction and a successful recovery reply alone do not establish that a hook ran.

Use `--review-dir PATH` with judging to keep temporary evidence for inspection. It must be a
new directory outside instruction source checkouts. It saves complete observed outputs before
assessment, followed by readable judge inputs, the private label map, the judge's observed
work and response, and the scored assessment including errors or limits. The map is never sent to the judge. A small manifest points to each output's
index. Those indexes link complete artifacts, requests, final replies, progress messages,
actions, browser observations, and images. Repeated artifacts and identical images share files. There is no packet byte limit,
file-size limit, or image-count limit. Evidence is not shortened to fit a prompt.
Git tracks the project file list; unignored new files are included. Tool outputs are the outputs
supplied by the runtime, which may itself limit them.

Check assessment against independently labeled examples:

```sh
uv run --group eval python -m evals.calibrate --model gpt-6.1-sol
```

Use `--examples evals/calibration/planning-authorization.json` to select another group.
`evals/calibration/wayfinding-continuation.json` checks continuation after corrections.
`evals/calibration/wayfinding-dependent-feedback.json` distinguishes routine feedback wording
from obsolete success requirements and invented user approval.
Groups also cover case-result equivalence and protected-file authorization. Each example
includes initial files, a final artifact, and an optional `reply` so the judge can distinguish a
request for permission from an unauthorized edit.
`evals/calibration/existing-data-loss-finding.json` checks reporting and ownership of a
credible risk outside the delivered change.

Calibration reports clear examples separately from ambiguous examples. Expected labels and
their reasons stay out of the judge's input. Read every task artifact and relevant action,
reconcile disagreements, and remove temporary review evidence after review. The
[method study](research/evaluation-methods.md) records the initial audit and pilot.

## PR description cases

`github-pr-description` files a PR for a completed batch-export change.
`github-pr-description-small` rewrites a help-page PR while leaving its repository and branch
unchanged. Checks read the filed bodies, with private assessment for meaning and evidence.
The [shared writing guidance](../skills/work-system/references/providers/github/delivery.md#pr-title-and-description)
defines the format. [Calibration examples](../evals/calibration/pr-descriptions.json) include
clear short descriptions, missing consequences and unsupported claims.

```sh
.venv/bin/python -m evals run --model gpt-6.1-sol --judge-model gpt-6.1-sol \
  --case github-pr-description --case github-pr-description-small \
  --calibration evals/calibration/pr-descriptions.json --repeat 3 \
  --timeout 1800 --judge-timeout 1200 --max-tokens 0 --judge-max-tokens 0
```

The [trial study](research/pr-description-trials.md) records grading corrections, earlier
failures and the final comparison.
The [verification-limits follow-up](research/pr-verification-limits-trials.md) records later
result-disclosure failures, source trials, corrected judgments and six correct final attempts.
The [remaining-failure study](research/remaining-failure-trials.md) records known-bug repair
trials and the corrected documentation check.

## Unslop writing

The `unslop` tag selects six cases: a final-reply question, a vague invoice explanation, a shorter
parcel email, successive invitation revisions, an already clear handout, and a technical guide
with an exact command and quotation. Writing quality is assessed privately. The optional
`observed-unslop-use` criterion reports access to the skill separately; a read does not establish
that the writing is good, and unavailable access records remain uncertain.

Compare copies of the instructions that differ only in `skills/unslop/SKILL.md`:

```sh
.venv/bin/python -m evals run --tag unslop \
  --model gpt-6.1-sol --judge-model gpt-6.1-sol \
  --variant poteto=/path/to/poteto --variant ours=/path/to/ours --repeat 3 \
  --calibration evals/calibration/unslop-writing.json \
  --timeout 1800 --judge-timeout 1200 --max-tokens 0 --judge-max-tokens 0 \
  --review-dir /tmp/unslop-review --report /tmp/unslop-report.json
```

The independently authored calibration includes clear concise answers, vague familiar language,
unexplained technical prose, lost consequences, invented facts, changed uncertainty, retained
technical terms, unchanged clear writing, and earlier decisions preserved or lost in revisions.
Existing PR, narrow-correction, and prose-boundary cases provide regression coverage.
[Source-limit calibration](../evals/calibration/source-limits.json) separates useful statements
about missing information from reports of following writing instructions, including passages
that contain both. [PR evidence examples](../evals/calibration/pr-evidence.json) distinguish
material validation limits that belong in the filed description from unrelated failed metadata
requests. The [writing study](research/unslop-writing-trials.md) preserves the comparisons,
regression findings, and assessor disagreements.

Run the detail and length suite with:

```sh
uv run --group eval python -m evals run \
  --model gpt-6.1-sol --judge-model gpt-6.1-sol \
  --case unslop-recommendation-revisions \
  --case unslop-first-explanation --case unslop-concise-explanation \
  --case unslop-brief-recommendation --case unslop-form-labels \
  --repeat 3 --timeout 1800 --judge-timeout 1200 \
  --calibration evals/calibration/unslop-writing.json \
  --calibration evals/calibration/unslop-short-copy.json
```

## Visual state selection

`gui-state-selection` asks for a finished conference agenda viewer. Its data checks pass while
revealed descriptions, long locations and crowded day navigation have presentation defects.
The private criteria assess both the finished application and the candidate's own inspection.
An existing saved visit makes retained notes available from the first page load. A private
executable check rejects changes that hide old notes even when newly written notes persist.
The [calibration examples](../evals/calibration/visual-state-selection.json) distinguish useful
examples, easy examples, unopened content and unavailable browser observations.

The fixture regression proves that the starting visual defects disappear with either scrolling
or wrapping navigation while agenda loading and session notes remain usable. These private
checks do not count as the candidate's inspection.

The assessor's artifact files stay under each output's neutral label. Its index identifies the
initial and final contents. The [retention calibration](../evals/calibration/retained-session-notes.json)
includes compatible keys, migration, fallback and a change that loses existing notes.
The [study](research/visual-inspection-coverage-trials.md) records rejected wording trials and
distinguishes observed product behavior from candidate inspection.

## Read results

The command prints a line for every attempt stating `behavior correct`, `behavior incorrect`,
or `behavior unknown`, followed by whether assessment completed. Failed checks and unmet or
uncertain criteria follow that line. JSON records the same fields, each required check, outcome,
reported token count, model, instruction digest, source revision, SDK version, source variant,
purpose, and attempt. With judging, it also records the original code-check status and each criterion
verdict. `assessment_counts` keeps judge outcomes visible even when a failed code check determines
the final status. `--report PATH` writes
the same summary to a new file outside the source checkouts. Temporary projects and runtime
records are removed after execution.

| Outcome | Meaning | Exit code |
| --- | --- | --- |
| `pass` | Every required code check passed and every required rubric criterion was met | 0 |
| `fail` | At least one required behavior check failed | 1 |
| `error` | Setup, runtime, or result data prevented a verdict | 2 |
| `limit` | Time or observed-token allowance was exhausted | 3 |
| `inconclusive` | Required criteria have not been assessed or their evidence could not be decided | 4 |

A mixed run exits with error before limit before fail before inconclusive. A favorable judge
verdict never erases a code check failure or execution problem. `mechanical_status` records the
code-check result separately. Without `--judge-model`, a case with required criteria remains
inconclusive when its code checks pass. Each attempt remains in the report.
The candidate defaults to 600 seconds per attempt with no cumulative token cutoff. Change
these with `--timeout` and `--max-tokens`. Explicit token guards measure cumulative reported
usage, including repeated input, rather than the size of the current context. They are not exact
spending caps. A completed final answer remains assessable if a later usage notification crosses
the guard. A guard reached before completion stops further turns and preserves observed work.

Both candidate and judge results retain startup, conversation-start, message, and compaction time,
plus reported input, output, reasoning, and cached tokens when available. Assessment also records
preparation time and evidence size. A failed assessment leaves behavior unknown unless an
observed check or criterion already establishes a failure. Passing code checks alone cannot
establish correct behavior for unassessed required criteria.

Judge responses use output labels as keys, then criterion IDs, with a verdict, reason, relevant
recording channel and cited evidence for each. Reasons distinguish observed behavior, an omitted
action, missing evidence, ambiguous requirements and conflicting evidence. Recording coverage
and collection problems appear separately from candidate completion. Unsupported native events,
missing command results, unavailable child findings, missing viewed images, malformed browser
receipts and requests without receipts identify capture gaps. Valid browser observations survive
a malformed later receipt. An omitted-action failure without complete relevant recording is
retained as an original judgment but becomes uncertain pending investigation.

Reports include `evaluation_status` and assessment `issues` with the next investigation or
repair. A capture problem prevents an overall pass but does not erase an observed violation.
The supplied schema and local parser require every label and criterion. Duplicate keys,
unknown fields, empty evidence, and incomplete JSON are errors. This format avoids the unfinished
outer-array output observed in the [ordinary-work revision](research/workflow-eval-realism.md).

Routine recovery supplies saved state and a work record to a fresh conversation. It checks
restoration from that input. The integration case requests native compaction in the same
conversation and waits for its completed compaction item and completed turn before continuing.
It uses a short conversation and does not fill the context window.

Native sleep events are retained as `native_item` actions. Unsupported native events retain their
payloads and still mark action coverage partial, so diagnosis can inspect what was captured.

## Repair an eval

Calibration exits 0 only when every expected judgment agrees, 1 on disagreement, and 2 when
assessment is incomplete or fails. Examples can supply observed commands, recording coverage
and candidate completion as well as artifacts. Expected labels and their reasons remain private.
The dialog-operation and transaction-structure suites check valid alternatives, actual omissions
and lost observations; they do not establish the entire prototype or interface case.
The [recording-sufficiency examples](../evals/calibration/recording-sufficiency.json) distinguish
confirmed recording gaps, unknown coverage, candidate omissions, and irrelevant hidden data.
For an archived evaluation, its coverage metadata belongs in the supplied source files. An
example's top-level `recording` describes the calibration capture itself.
[Validation-history examples](../evals/calibration/validation-history.json) distinguish applicable
supplied results, stale evidence after changed behavior, and invented fresh execution.
[Ticket-readiness examples](../evals/calibration/ticket-readiness.json) accept concise answers to
readiness questions without requiring an unrequested ticket draft.

Add repeatable `--calibration PATH` arguments to `run` to check the selected assessor before
candidate execution. A failed calibration stops the run, writes its findings to the report and
starts no candidates. Calibration needs `--judge-model` and uses its model and allowances.

```sh
.venv/bin/python -m evals run --case interactive-prototype-comparison \
  --model gpt-6.1-sol --judge-model gpt-6.1-sol \
  --calibration evals/calibration/dialog-operation.json \
  --review-dir /tmp/prototype-review --report /tmp/prototype-report.json --diagnose
```

With `--diagnose`, a failed calibration or unresolved judged case starts one read-only
investigation automatically. The run report links its diagnosis; the original behavior verdict
is preserved. This option requires both judging and an external review directory. It does not
retry candidates or edit evaluation definitions.

Use the per-case review directory to investigate the original criteria, installed instructions,
recorded work, check results and judgment in a separate read-only model context:

```sh
.venv/bin/python -m evals.repair diagnose \
  --evidence /tmp/prototype-review/interactive-prototype-comparison \
  --model gpt-6.1-sol --review-dir /tmp/prototype-diagnosis \
  --report /tmp/prototype-diagnosis.json
```

Diagnosis reports cited defects or unresolved questions about expectations, recording and
judgment, with the appropriate repair. It does not edit criteria, source or original verdicts.
Its findings distinguish expectations, recording sufficiency, warning classification and the
original judgment. They require inspection and a regression proving a proposed correction. It can inspect
an invalid or unfinished original assessment when the input evidence and label map survived.

After a supported assessor repair, replace `diagnose` with `reassess` and use new output paths.
Reassessment preserves original criteria, checks, verdicts and assessment errors, and reports
judgment changes for inspection. It rejects changed case definitions, missing original
definitions and interrupted candidate work. An original assessment failure, uncertain required
criterion or collection warning first triggers a separate read-only review. Reassessment
proceeds only when that review establishes sound expectations and sufficient retained
observations. Otherwise it reports what needs resolution. Original warnings remain in the saved evidence.
The new assessor still leaves genuinely unavailable requirements uncertain and needs complete
relevant records to establish an omission. The original mechanical failures remain behavior failures; this
command does not rerun code checks. Corrected code checks need their own recheck or a fresh run.
Changed expectations and missing observations require a fresh comparison. Legacy archives
without definitions can still be diagnosed but cannot establish unchanged inputs for reassessment.

Repair commands exit 0 when no problem is found, 1 for defects, uncertainty or changed judgments,
and 2 on execution or input errors. All reports and review directories must be new and outside
Git and instruction-source checkouts. The assessment API enforces this boundary as well as the
commands. Keep evidence through inspection and required review, then delete it. Preserve
concise findings and reusable regression examples.

## Add cases

Add a JSON file under `evals/cases/` with a unique `id`, `tags`, and `steps`. Put initial project
files in `files`, or reuse named maps from `evals/cases/fixtures/` through `fixtures`. Later
fixtures replace earlier files with the same path; case files replace fixture files. Paths
are relative to the disposable project.

A case's `purpose` defaults to `focused`. Task cases require a `rubric` with three to six criteria.
Each criterion has a unique `id`, `description`, and optional `required` flag, true by default.
`project_name` selects an ordinary disposable directory name. Each case has one sequence of
requests. `artifacts` identifies intended file outputs and can be empty for a task answered in
conversation. The judge can read the entire captured project to assess
context and changes together.

Set `browser_tools: true` to provide the same local browser tools for an open prototype task
without requiring a fixed private browser scenario. `press` supports a keyboard key and an
optional selector. Without a selector it uses the page keyboard. A scenario's
`media.colorScheme` sets `light` or `dark` appearance. A `media` action with `colorScheme`
changes the live setting without reloading the page.

Set `candidate_role: "implementation-worker"` to evaluate a worker assignment. The runtime
identifies the candidate as a spawned implementation subagent; the task supplies the normal
parent assignment. Its role is included in assessment evidence. The default role is `primary`.
Explicit judge instructions remain separate from candidate roles.

Set `local_remote: true` to create a disposable local `origin/main` containing the initial
commit. An `edit` step with `publish: true` publishes the current head there through the
fixture, including replacement of its previous head. This uses no external service. Evidence
marks the supplied edit and records local history and the remote head separately from candidate
actions. Fixture publication rejects a changed remote URL.

An `edit` step with `record_commit: true` registers HEAD for that step's conversation through
the navigator.

A `session_commits` check compares that conversation's recorded IDs with the current Git
history. Set `include_initial: true` when the starting commit belongs to that conversation.
Otherwise the check excludes the starting commit. A `completed` check permits retained commit
IDs when no workflow remains active.

Use `uncommitted_files` for existing edits. These files are written after the initial commit,
so they can include changes to tracked files and new untracked files. File checks compare
against this edited starting state.
Set `commit_hook` to a setup file to install it as the disposable project's executable
pre-commit hook after the initial commit.

Use `temporary_files` for UTF-8 evidence outside the candidate checkout. The literal
`{temporary}` in supplied file contents and requests expands to that disposable directory.
The assessor sees its complete contents under `/evidence/` alongside project files. An `edit`
step can update `temporary_files` or delete `remove_temporary` paths between turns. Both kinds
of supplied edit remain distinct from candidate actions.

Steps use `message` to send a prompt, `seed` to prepare navigation progress, and `compact` to
request compaction. Give steps the same `conversation` name to continue a conversation, or
different names to keep their progress separate. A compact step requires `integration: true`.
An `edit` step changes files through `files`, deletes files listed in `remove`, or replaces this
conversation's saved navigation file through `navigation_text`. Edits happen between turns and
do not change the starting content used by unchanged-file checks. Paths must stay inside the
project and cannot write Git metadata. A missing file named in `remove` is a setup error.
Check definitions stay outside the project visible to the agent. Put private Python scripts in
`grader_files` rather than `files`; `python_check` reads their saved content without copying
them into the project.

| Check | Required fields | Pass condition |
| --- | --- | --- |
| `unchanged` | `paths`, optional `exclude` | Initial files or directories have identical content, including no added files outside excluded paths |
| `only_changed` | `paths` | Changes to tracked and unignored files stay within these files or directories, compared with the initial project |
| `file_equals` | `path`, `text` | A file has exactly the expected text |
| `file_regex` | `path`, `pattern`, optional `absent` | The file exists and its text matches the regex, or does not when `absent` is true |
| `prose` | `paths`, `required_patterns`, optional `forbidden_patterns` | Every file contains text, required subject patterns occur in their combined content, and forbidden patterns are absent |
| `reply_regex` | `pattern`, optional `absent` | The final answer matches the regex, or does not when `absent` is true |
| `command_sequence` | `commands`, each with `pattern`, `exit_code`, optional `output_pattern` | Current-message command results match in order; each result is used once |
| `action_sequence` | `actions`, each with `kind`, `pattern`, optional `exit_code`, `tool` | Commands and assignment submissions match in order within this message; each action is used once |
| `agent_assignments` | optional `tools`, `min_count`, `max_count`, `required_patterns`, `forbidden_patterns` | Every selected assignment has the required text and no forbidden text; its count is within the bounds |
| `completed` | none | This conversation has no saved active workflow |
| `session_commits` | optional `include_initial` | Saved commit IDs match current Git history for this conversation; the starting commit is excluded unless requested |
| `regression_test` | `tests`, `source`, optional `faulty_text` | Authored unittest tests pass current code and fail the supplied faulty source, or initial source by default, by assertion |
| `browser` | `scenario`, optional `require_match` | Real reference and application browser observations; require the accepted contract by default |
| `python_check` | `path` | The starting Python script passes against the current project within ten seconds |
| `temporary_files` | `paths`, `state` | Outside-checkout files are `present`, `absent`, or `unchanged` from their supplied contents |
| `no_raw_evidence` | optional `paths` | Supplied temporary evidence and the named initial project captures have no copies in the checkout or new Git blobs, including staged files and replaced commits |
| `command_regex` | `pattern`, optional `absent` | The current step's recorded command text matches the regex, or does not when `absent` is true |
| `progress` | `workflow`, `state`, optional `alternatives`, `substate`, `ignore_substate`, `record` | This conversation has an allowed workflow/state pair; substate and work-record requirements still apply |
| `navigation_text` | `text` | This conversation's saved navigation file has exactly this text, even when damaged |
| `github_state` | optional `resource`, `count`, `number`, `body_pattern` | Saved fixture records have the expected count and at least one selected body matches; requires a count or body pattern |
| `commit_count` | `count` | Git has that many commits and tracked files have no uncommitted changes |
| `commit_groups` | `groups`, optional `uncommitted`, `optional_paths` | Initial history is preserved; new commits contain the listed path groups in any order, with explicitly permitted related paths; only the listed paths remain uncommitted |
| `tracker` | `name` | The project tracker is `local` or `github` as expected |
| `no_publish` | optional `target`, `allow_pr_comments` | No observed `gh` call requests publication; `pull_requests` limits this to PR writes; `allow_pr_comments` permits `gh pr comment` while preserving other write restrictions |

For `unchanged`, exclusions are project-relative files or directory prefixes. For `no_publish`,
the default target is `all`; `pull_requests` permits issue updates while rejecting PR writes.
GitHub planning cases can also allow comments on the existing PR with `allow_pr_comments`;
creation, merge, reopening and editing remain prohibited. By default, `gh pr comment` remains prohibited.
Both targets reuse the same mutation detection.

For `progress`, `alternatives` lists additional allowed workflow/state pairs, such as
`[{"workflow": "novel-work", "state": "planning"}]`. Without alternatives the match is exact.
`ignore_substate: true` allows any substate; `record` requires the linked project-relative record.

For `commit_groups`, `optional_paths` maps an optional file to a required file in its owning
commit. For example, `{".work/limit/status.md": "src/limits.py"}` permits that work record only
alongside the limit implementation. It does not allow a separate record commit, unrelated files,
or an uncommitted record unless `uncommitted` explicitly includes it.

`no_raw_evidence` checks ignored files and reads ZIP and gzip contents with a bounded size.
It detects supplied raw content even under another name. Semantic assessment still checks for
rewritten dumps and whether the retained conclusions explain the result. It cannot prove that
an unobserved file was never briefly created or that Git objects were not deliberately erased.

Use `regression_test.faulty_text` when later accepted changes make the original source an
ambiguous test of an earlier bug. Keep those later changes correct in the faulty implementation
so an unrelated assertion cannot stand in for the regression under assessment.

Checks run after their step. Each case needs at least one check. Use code checks for functional
behavior, exact edits, permissions, command results, and required navigation boundaries. Use
hidden criteria for the meaning and completeness of decisions, prose, and review findings.
Ordinary Python cache files are excluded from project observations and preservation checks;
source files supplied at the start remain checked even when ignored by Git.

Prose checks read the named files as UTF-8, including headings, tables, footnotes, and comments.
They combine required subject content with prohibited text patterns, so missing or empty output
cannot pass. Use separate checks when each artifact needs its own content. The check examines
saved files; progress messages and final replies remain separate observations. Cases can permit
requested methods in one report while detecting process claims in a reader's guide.

`command_regex` joins the current step's commands with newlines in recorded order. They check
command text, including shell wrappers. Check outputs separately; matching a command does not
prove that it succeeded.

Command sequences use exit codes and combined output from completed runtime commands. Missing
result fields cannot satisfy an expected value. Other commands may occur between matches.
A command's exit code belongs to the whole shell command, so a later successful command in the
same shell call can hide an earlier failure. Match the check's output as well when it matters.
Set an expected `exit_code` to `null` when only command text and output should be checked.
This is useful for a service error inside a shell call that ends successfully; it does not
establish the service command's individual exit code.

Action sequences distinguish `command` and `agent` actions. Command text includes the observed
output. Assignment text comes from the submitted prompt, without the worker's returned message.
Assignment checks default to `spawnAgent` and at least one call. Set both count bounds to zero
to prohibit that tool. Missing native assignment text is an execution error when content needs
checking. An observed call can still fail a zero-call requirement without its text.

Set `delegation` to `review`, `label`, or `total` to install the local delegation stand-in. Submit
a project assignment file with `python3 "$CODEX_HOME/bin/delegate-fixture.py" <path>`. It records
the submitted text outside the project and returns a prepared review or file correction. Select
`delegateFixture` in assignment checks and action sequences. A returned identifier connects the
command result to its recorded submission. The stand-in does not run a child model. Its files
and records are removed with the temporary workspace.

For `github_state`, `resource` defaults to `issues` and also accepts `prs`. `count` checks the
whole resource collection. `number` selects the record for `body_pattern`. These checks read the
saved fixture state independently of the agent's reply. The fixture covers the CLI and REST
operations used by the cases, not the complete GitHub API. Repository access checks and native
sub-issue links support conversion; help commands leave records and pending write faults unchanged.

Prepared Python checks reference a setup file or private `grader_files` entry and run its saved starting content with `python
-I -B -` from the project root. They test the current production code even if the agent changes
the visible check script. Use the working directory to find project files. Script input comes
from the runner, so these checks cannot use interactive input. Keep assertions independent of
the implementation being tested.

Regression checks run unittest discovery in disposable project copies. `tests` names the test
directory; `source` names a setup file to restore for the failing run. Each run has ten seconds.
No tests, test errors, or a passing initial implementation fail the check. The original project
is not changed. These checks cover one source file per check.

Generate the field schema and run infrastructure tests without live conversations:

```sh
uv run --group eval python -m evals schema
uv run --group eval python -m unittest discover -s tests
```

The SDK and its bundled runtime are pinned to `0.163.0`. Compaction uses one protected SDK
method to observe events before turn routing. When changing that pin, run adapter tests and
a short native compaction probe before trusting integration results.

## GUI cases

The GUI cases use a reconstructed document workspace and runnable accepted design. They cover
design adherence, browser rendering, state changes, combined constraints, alignment, grouping,
and wrapping during ordinary implementation. They are not a replay of Linkwrite's source or
original prototype. Historical case IDs containing `audit` remain, but their requests ask for
feature completion.

Production components share stored document state. Private checks exercise editing, switching,
New, Rename, applied preferences, and reloading as well as the visual scenarios. Copying the
prototype cannot satisfy that data flow. A known finished production fixture passes the same
checks. These cases use native browser controls and a textarea; they do not cover integration
with a production editor library or differences between browser engines.

Browser cases require existing Node, Playwright, and Chromium. The runner discovers packages
through existing Playwright cache links and browser binaries in the usual cache locations.
`EVAL_PLAYWRIGHT_MODULE` and `EVAL_BROWSER_EXECUTABLE` can select existing paths. No software is
installed. Missing dependencies or browser failures produce an execution error.

The disposable project receives `browser-run SCENARIO_JSON OUTPUT_DIR`. Its documented actions
include navigation, clicking, filling, selection, resizing, evaluation, waits, and captures.
Captures include PNG images and DOM geometry and styles. Command results return capture paths
and evaluation values; complete capture data remains available to assessment. Native image-view
events are recorded separately because generating a screenshot does not establish inspection. Browser observations survive deletion of the candidate's raw captures
until assessment finishes, outside the project. A local worker runs Chromium outside the
candidate sandbox and serves the disposable project on a private loopback origin. It blocks other browser origins and sockets. The candidate keeps
its usual sandbox. The same browser launcher supports private reference comparisons. Private
observations are labeled separately and do not count as verification performed by the candidate.

Browser receipts include a `navigation` record with `status` (`complete`, `partial`, or
`unavailable`), `events`, and any observer error. Main-document commits receive an opaque
`document_sequence`; loads retain their commit attribution. Same-document URL changes do not
create another identity. Events identify the action during which they were observed and, for
loads, the commit action. A key press alone does not establish a reload. Inspect the relevant
navigation status and later UI observations before accepting a navigation claim. Observer
failure remains explicit in the retained journal, including when the browser command fails.

The judge opens PNG files alongside complete browser observations as needed. Images with
identical contents share a file. Each browser record keeps its origin, actions, and capture
names so private checks cannot stand in for candidate inspection.

With `--review-dir`, complete outputs are saved before preparing judge inputs. Interrupted
assessments retain observed judge actions, partial replies, token usage, and phase times. Remove
this evidence after inspection and required review.
