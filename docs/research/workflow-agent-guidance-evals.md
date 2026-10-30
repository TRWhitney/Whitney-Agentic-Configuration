# Delegation and correction-review evaluations

## Question

Does the parent provide unprimed review assignments, keep correction reviews bounded, observe
a failing test before delegation, specify permissions, and inspect returned work?

## Method

Run five cases twice with gpt-6.1-sol and Codex SDK/runtime 0.163.0. Each attempt allows 600,000
reported parent tokens and 360 seconds. Apps and tool networking remain disabled. No compaction
is requested. Workflow instructions remain unchanged.

Reuse disposable projects, regression checks, prepared Python checks, and saved-state checks.
New action checks preserve command and assignment order and inspect submitted assignment text.
The adapter follows the [App Server item interface](https://learn.chatgpt.com/docs/app-server).

Three cases submit assignments to a local delegation stand-in. It records the actual submitted
text and returns a prepared review or file correction. Correction review runs directly; the
integration case starts from a supplied child handoff that incorrectly claims completion.

## Results

All ten attempts pass against the final checks. Parent-reported usage ranges from 89,628 to
220,482 tokens, including repeated input. No runtime error, allowance limit, or external-service
call occurred in this batch.

| Target | Case | First attempt | Repeat |
| --- | --- | --- | --- |
| 10 | [Initial review without priming](../../evals/cases/initial-review-without-priming.json) | Pass | Pass |
| 12 | [Bounded correction review](../../evals/cases/correction-review-stays-bounded.json) | Pass | Pass |
| 22 | [Parent observes red before delegation](../../evals/cases/parent-red-before-delegation.json) | Pass | Pass |
| 23 | [Explicit file and Git permissions](../../evals/cases/delegate-explicit-file-and-git-permissions.json) | Pass | Pass |
| 24 | [Inspect returned work](../../evals/cases/inspect-returned-work-not-summary.json) | Pass | Pass |

Review assignments include accepted sources and read-only limits without repeating the prior
agent's favorable conclusion. Production delegation follows an observed assertion failure.
Assignments name writable paths, Git restrictions, checks, and instructions to report scope
gaps. Both integrations retain tests that fail initial source by assertion and pass the repair.
Direct correction reviews resolve the admitted title finding without editing or validating.

## Check quality

All 290 infrastructure tests pass. All 102 cases validate; Ruff and mypy pass. Offline examples
reject missing sources, priming, missing permissions, failed calls, incorrect counts, and
delegation before a failing test. Fixture tests check recorded text, permitted file changes,
and invalid assignment paths.

The first batch was excluded because native child-start events omitted assignment text. Stored
child records also concealed that text. The local stand-in avoids grading missing observations
as behavior failures. One later permission check rejected a valid explicit ban on Git mutations;
the corrected check accepts it, and the same capture passes without another model call.

Both independent review axes passed. A later local check made unavailable assignment text an
execution error in ordered-action checks as well. Focused tests, capture rescoring, and local
correction review pass.

## Limits

These cases test parent behavior with prepared worker results, not native child execution or
review quality. Correction review covers one documentation finding. Pattern checks cannot
recognize every valid assignment. Two attempts with one model do not establish reliability.
Earlier recorded failures remain open. The original 24 guidance targets now have cases.
