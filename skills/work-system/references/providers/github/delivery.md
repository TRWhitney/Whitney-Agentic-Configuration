# File and babysit a PR

## File or resume

Check the issue, repository, head branch, and base. Find the branch's existing PR. Push the validated
commits and create or update the PR with the problem, change, checks, and ticket link. After an
uncertain creation response, look for the PR before retrying.

Save the PR URL, head revision, base, and next action on the work item. Read the repository's required
checks and reviews, including review bots that run after a push.

## Watch and respond

Watch checks, published reviews, open threads, merge conflicts, and relevant base changes. Read
existing feedback on entry. Check findings against the current code and accepted scope.

Fix valid findings. Explain incorrect or out-of-scope findings in the PR. Take changes to accepted
intent back to planning or discovery. Close addressed threads under the repository's review rules.

Take code corrections to implementation and outdated evidence to validation. Repeat affected checks
and required review, commit, push, and return here with the same PR.

Read failed check logs before fixing code or retrying. Apply the existing validation rules to
repository failures. Retry temporary service failures up to three times, then report the blocker.
Refresh affected evidence after updating the base.

Use watch tools or paced polling while checks and reviews run. Save the revision, pending feedback,
and next action when an access failure or a needed human decision stops progress.

## Handoff

Read the PR head again. Check that required checks and reviews pass, expected bot reviews have
finished, no actionable feedback is open, and the PR can merge. Repeat on the new revision if the
head changes during this check.

Mark the ticket `awaiting-merge`, keep it open, and report the PR URL and check/review results.
Save the next action and stop watching. Leave merging to me. Do not enable auto-merge or add the PR
to a merge queue.

On continuation, check the PR's current state. After merge, update the ticket and its dependents.
For new feedback or changes on an open PR, return to watching. Report closed, unmerged work without
marking its outcome complete.

After a ready-for-merge handoff, another independent ticket may proceed. Keep work that depends on
an unmerged change blocked. Finish the effort after its accepted changes have merged.
