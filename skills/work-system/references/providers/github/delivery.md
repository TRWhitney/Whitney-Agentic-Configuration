# File and babysit a PR

## File or resume

Check the issue, repository, head branch, and base. Find the branch's existing PR. Push the validated
commits and create or update the PR with the problem, change, checks, and ticket link. After an
uncertain creation response, look for the PR before retrying.

Save the PR URL, head revision, base, and next action on the work item. Read the repository's required
checks and reviews, including review bots that run after a push.

## Watch and respond

Stay in the active session and repeat this cycle while the PR is open:

1. Read the PR state, head revision, base, checks, PR comments, reviews, open review threads,
   and mergeability. Read existing feedback on entry and check findings against the current code
   and accepted scope.
2. Address actionable changes using the rules below. After every push, including a rewritten
   branch, start a fresh cycle. Earlier readiness results do not apply to the new head. Refresh
   affected evidence when the base changes.
3. When no action is needed, sleep or use a waiting tool for 30 to 60 seconds, then check again.
   Keep polling after checks pass or the PR becomes ready to merge. Do not end the turn just
   because the current feedback has been addressed.

Fix valid findings. Explain incorrect or out-of-scope findings in the PR. Take changes to accepted
intent back to planning or discovery. Close addressed threads under the repository's review rules.

Take code corrections to implementation and outdated evidence to validation. Repeat affected checks
and required review, commit, push, and return here with the same PR.

Read failed check logs before fixing code or retrying. Apply the existing validation rules to
repository failures. Retry temporary service failures up to three times, then report the blocker.
Refresh affected evidence after updating the base.

Ask for needed decisions in the PR and read my replies while continuing to watch. Keep work that
depends on my answer pending. If access prevents further checks, report the blocker in chat and
save the revision, pending feedback, and next polling action in the owning issue when accessible.
Record an interrupted watch as unfinished and resume the full cycle when continuing the work.

## Ready to merge

Read the PR head again. Check that required checks and reviews pass, expected bot reviews have
finished, no actionable feedback is open, and the PR can merge. Repeat on the new revision if the
head changes during this check.

Mark the ticket `awaiting-merge`, keep it open, and report the PR URL and check/review results in a
progress update. Continue waiting and checking. If new feedback, failing checks, or changes make
the PR unready, update its ticket status and address them. Leave merging to me. Do not enable
auto-merge or add the PR to a merge queue.

## Stop watching

Stop when the PR is merged or closed, or when I explicitly stop the watch. After merge, update the
ticket and its dependents. Report closed, unmerged work without marking its outcome complete.
Keep work that depends on an unmerged change blocked. Finish the effort after its accepted changes
have merged.
