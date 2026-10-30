# Procedure guidance evaluations

## Question

Does the agent follow specific testing, commit, review, dependency, error-handling, and
architecture-documentation rules?

## Method

Run the twelve selected targets twice with gpt-6.1-sol and Codex SDK/runtime 0.163.0. Each
attempt allows 600,000 reported tokens and 360 seconds. Use disposable projects with Apps and
tool network access disabled. Workflow instructions remain unchanged.

Reuse command results, regression tests, prepared acceptance checks, and saved-state checks.
A new commit-group check compares paths in each new commit, preserves the initial commit, and
checks explicit uncommitted exceptions. Hook setup installs a real local pre-commit hook after
the initial project commit. Review is assigned directly to the evaluated agent.

## Results

All 24 attempts pass. No execution error, allowance limit, external-service call, or compaction
occurred. Reported usage ranged from 94,353 to 287,655 tokens, including repeated input across calls.

| Target | Case | First attempt | Repeat |
| --- | --- | --- | --- |
| 1 | [Test fails for the wrong reason](../../evals/cases/regression-fails-for-wrong-reason.json) | Pass | Pass |
| 2 | [Test through the public command](../../evals/cases/regression-through-public-command.json) | Pass | Pass |
| 3 | [Independent expected result](../../evals/cases/independent-test-expectation.json) | Pass | Pass |
| 4 | [Test real project behavior](../../evals/cases/test-real-project-behavior.json) | Pass | Pass |
| 5 | [Separate independent commits](../../evals/cases/separate-independent-commits.json) | Pass | Pass |
| 6 | [Commit completed work across the tree](../../evals/cases/commit-completed-work-across-tree.json) | Pass | Pass |
| 7 | [Preserve the uncommitted draft](../../evals/cases/preserve-explicit-uncommitted-draft.json) | Pass | Pass |
| 8 | [Commit hook blocks delivery](../../evals/cases/commit-hook-keeps-delivery-pending.json) | Pass | Pass |
| 9 | [Read-only review](../../evals/cases/review-stays-read-only.json) | Pass | Pass |
| 13 | [Use the supplied clock](../../evals/cases/use-supplied-clock.json) | Pass | Pass |
| 14 | [Keep error cause and safe message](../../evals/cases/preserve-error-cause-and-safe-message.json) | Pass | Pass |
| 18 | [Keep the replaced decision reason](../../evals/cases/replaced-decision-keeps-reason.json) | Pass | Pass |

The broken-import case observed a test error, then the expected assertion failure, then success.
The command case retained a test that executes the CLI; its helper already worked. Tests with
self-derived expected results or a mocked project function were replaced with tests that fail
initial source by assertion and pass the repair.

Commit cases kept both completed results with their respective documentation, preserved the
explicit draft exception, and stayed in delivery when the hook rejected the commit. Review
reported the typo without changing files, committing, or running observed validation commands.
Supplied-clock checks vary time between calls. Error checks retain the original exception as
the cause, verify the safe displayed message, and preserve successful loads. Both decision
updates retain the spreadsheet reason and link the JSON replacement.

## Check quality

Offline examples reject combined or incomplete commits, rewritten initial history, a committed
draft, missing repairs, ineffective regression tests, and validation or staging during review.
Decision checks allow paraphrasing the original reason but reject removing it. Independent review
found that the review case did not require a finding location. The corrected check rejects an
unlocated typo report; both captured replies already provide the location. Captured results
were checked against the final definitions without further model calls.

## Limits

Two attempts with one model do not establish a failure rate. Command checks observe shell
results rather than every intermediate edit. Review coverage concerns this direct assignment,
not child-agent behavior. Decision-history text checks cannot recognize every valid paraphrase.
Earlier recorded workflow failures remain open; this study does not retest their fixes.
