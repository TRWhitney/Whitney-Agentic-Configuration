# GitHub recovery trials

GitHub-provider wording was tested for missing planning issues and next actions
after failed reads. The [approved patch](github-recovery-proposal.diff) is applied unchanged.

## Outcomes

C means correct, F incorrect, U unknown. Entries identify attempts in execution order.
All 42 candidate assessments and joint blinded comparisons completed.
No attempt is excluded. Record saves questions; Retry adds a next action after failed
reads; Creation and Final also explicitly create missing issues. Screens are single attempts.

| Case | Baseline | Record screen | Record repeats | Retry repeats | Creation screen | Final repeats |
| --- | --- | --- | --- | --- | --- | --- |
| github-create-timeout | F | C | C, F, F | F, F, F | C | C, C, C |
| github-planning-edit-persists | C | Not run | C, C, C | C, C, C | Not run | C, C, C |
| github-planning-read-failure | F | Not run | F, F, F | C, C, C | Not run | C, C, C |
| tracker-converts-existing-work | C | Not run | C, C, U | C, F, C | Not run | C, C, C |

The timeout baseline answered in chat without GitHub calls or an export issue. Issue-content
and one-owner failed; uncertain-create was not exercised. The first addition was
"Record unresolved planning questions in the feature issue before replying." Its screen and first
repeat recovered one saved issue after timeout.
Record repeats 2 and 3 and all Retry repeats omitted the issue, using only a PR comment or chat.
Retry uncertain-create was unknown initially and failed jointly; creation was never exercised.
Missing issues establish F.

The failed-read baseline and all three first-version repeats read GitHub, preserved source and
reported uncertainty, but gave no concrete next retry or access-restoration action. Hold-code
failed. A second sentence now states that next action. The creation revision also explicitly
requires creating a missing feature issue.
Existing ownership and uncertain-write rules remain. The two-sentence patch is approved.

## Eval correction

Both cases using the PR-only publication ban were audited. Their rubrics prohibit new PRs,
but the check rejected required comments on existing PRs. The private checks now require the
original PR and no additional PR. A regression using the local fixture fails under the comment ban,
accepts comments after correction and rejects creating a PR. Requests, fixtures and semantic
criteria did not change. All 32 affected frames pass corrected checks. The initial
planning-update rejection was false; its semantic assessment passed and its behavior is C.

## Method and limits

Separate candidates and blinded judges use gpt-6.1-sol,1800/1200-second allowances and disabled
token guards. Source copies include the declared unslop dependency. Only GitHub provider
wording differs between variants. Baseline is `81b1ddb`; requests, fixtures and semantic criteria
stay fixed. The repository tracker remains local; service actions use
isolated fixtures and publication uses disposable remotes.

All cases are existing tasks. Baseline conversion already recovered its saved parent,
preserved the unrelated issue and verified replacements. Fixture endpoints leave PR monitoring
pending; conversion correctness and assessment completion are separate.

An intermediate conversion removed document sources before reading their replacements.
Selected-destination, recover-and-verify and finish-conversion failed. Another lacks the revised
script needed to prove verification preceded removal. Its original assessment left
recover-and-verify unknown; joint comparison also leaves the other two criteria unknown.

All 12 final attempts are correct, three per case. Outputs, relevant actions and available
child findings were inspected. Independent intent and engineering reviews pass with no findings.
Raw evidence was deleted after inspection and review.
467 framework tests, all 151 definitions, lint, formatting and strict typing pass.
Fixtures and same-family judges do not establish
live GitHub behavior, a production failure rate or a current full-corpus rate. Native compaction
remains deferred.

[Historical failure](workflow-eval-realism.md#latest-observed-outcomes).
