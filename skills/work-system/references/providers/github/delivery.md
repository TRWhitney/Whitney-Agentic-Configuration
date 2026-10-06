# File and babysit a PR

## File or resume

For implementation delivery, check the issue, repository, head branch, and base. Find the branch's
existing PR. Push the validated commits and create or update the PR using the description guidance
below. After an uncertain creation response, look for the PR before retrying.

Save the PR URL, head revision, base, and next action on the work item. Read the repository's required
checks and reviews, including review bots that run after a push.

## PR description

Apply this guidance when creating, rewriting, or clarifying a GitHub PR description. Explain the
problem and what this PR makes possible or changes compared with existing behavior, including
earlier slices of the same feature. Link the ticket and report the checks and their results.

For behavior changes:

- Show a concrete consumer action and its observable result. Explain what previously failed or
  behaved differently. An API declaration or list of supported signatures alone does not
  demonstrate functionality.
- Use examples that exercise the claimed change. An unchanged example can explain setup, but
  cannot demonstrate a newly delivered capability.
- Link relevant documentation and runnable examples or acceptance fixtures at the reviewed
  revision. Explain what each demonstrates. Verify that the linked material supports the claim;
  do not present general setup or earlier functionality as evidence of the new behavior.
- State required setup, supported environments, and material limitations when they affect usage.

Scale detail to the change. Use plain, concrete language and include only what helps a reviewer
understand or use the result. A small change may need only a few sentences and validation. Do not
turn every PR into a long checklist.

## Watch and respond

Use a monitoring or wake-up mechanism provided by the harness or environment when available.
Register the PR and follow that mechanism's waiting instructions, including yielding the turn
when it will wake you automatically. If no provided mechanism is available, stay in the active
session and poll every 30 to 60 seconds.

Run this cycle on entry and whenever monitoring reports an update or a poll is due:

1. Read the PR state, head revision, base, checks, PR comments, reviews, open review threads,
   and mergeability. Read existing feedback on entry and check findings against the current code
   and accepted scope.
2. Address actionable changes using the rules below. After every push, including a rewritten
   branch, start a fresh cycle. Earlier readiness results do not apply to the new head. Refresh
   affected evidence when the base changes.
3. When no action is needed, wait using the selected monitoring mechanism. For polling, sleep or
   use a waiting tool for 30 to 60 seconds, then check again. Keep monitoring after checks pass
   or the PR becomes ready to merge. Yield for an automatic wake-up only after registration;
   when polling, do not end the turn just because the current feedback has been addressed.

Fix valid findings. Explain incorrect or out-of-scope findings in the PR. Take changes to accepted
intent back to planning or discovery. Close addressed threads under the repository's review rules.

Take code corrections to implementation and outdated evidence to validation. Repeat affected checks
and required review, commit, push, and return here with the same PR.

Read failed check logs before fixing code or retrying. Apply the existing validation rules to
repository failures. Retry temporary service failures up to three times, then report the blocker.
Refresh affected evidence after updating the base.

Ask for needed decisions in the PR and read my replies while continuing to watch. Keep work that
depends on my answer pending. If access prevents further checks, report the blocker in chat and
save the revision, pending feedback, and next monitoring action in the owning issue when accessible.
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
