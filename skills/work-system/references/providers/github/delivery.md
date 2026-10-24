# File and babysit a PR

## File or resume

For implementation delivery, check the issue, repository, head branch, and base. Find the
branch's existing PR. Push the validated commits and create or update the PR using the
title and description guidance below. If the request to create a PR times out or returns no PR
URL, check GitHub for a PR with the same head and base branches before retrying.

Save the PR URL, head revision, base, and next action on the work item. Read the repository's
required checks and reviews, including review bots that run after a push.

## PR title and description

Write for someone who has not read the ticket history or code. Link the ticket.

- Use the title to say what someone can now do or what behavior changes.
- Describe the old behavior and what this PR changes. Say what earlier PRs already delivered.
- Explain the change before showing an example.
- Include a realistic example in every PR description. Show what someone does and what happens.
  Use code, a command, or a concrete interaction. Give separate concepts separate examples.
- State required setup and limits that affect use. Say what runs automatically and what the
  person using it must do or provide.
- Report the checks you ran and their results. Link relevant docs and runnable examples or
  acceptance tests at the commit under review. Say what each explains or tests. Read the linked
  files to confirm they support your claims.
- After changing the implementation, update the title, description, examples, and links to match.
  Leave out abandoned approaches and conversation history unless they explain a needed tradeoff.
- Use simple words and short sentences. A small change may need only a few sentences, an example,
  and check results. Include technical details when they explain behavior, compatibility, or
  risk. Cut vague benefits, lists of changed files, and claims about following instructions.

## Watch and respond

Use a monitoring or wake-up mechanism provided by the harness or environment when available.
Register the PR and follow that mechanism's waiting instructions, including yielding the turn
when it will wake you automatically. If no provided mechanism is available, stay in the active
session and poll every 30 to 60 seconds.

Green CI, completed reviews, and merge readiness are progress within the watch. They do not
complete delivery or authorize handing the PR back. Keep handling feedback and monitoring until
one of the conditions under Stop watching applies.

When yielding to a built-in watcher, leave the watch registered and resume the full cycle on
each wake-up. Yielding for automatic monitoring is not a handoff. Do not invoke an
unwatch-before-handoff instruction merely because checks pass or the PR is ready to merge.

Run this cycle on entry and whenever monitoring reports an update or a poll is due:

1. Read the PR state, head revision, base, checks, PR comments, reviews, open review threads,
   and mergeability. Read existing feedback on entry and check findings against the current code
   and accepted scope.
2. Address findings that require changes using the rules below. After every push, including a
   rewritten branch, start a fresh cycle. Earlier readiness results do not apply to the new
   head. Refresh affected evidence when the base changes.
3. When no action is needed, wait using the selected monitoring mechanism. For polling, sleep or
   use a waiting tool for 30 to 60 seconds, then check again. Keep monitoring after checks pass
   or the PR becomes ready to merge. Yield for an automatic wake-up only after registration;
   when polling, do not end the turn just because the current feedback has been addressed.

Fix confirmed problems. Explain incorrect or out-of-scope findings in the PR. Return changed
requirements to planning or discovery. Close addressed threads under the repository's review
rules.

Take code corrections to implementation and outdated evidence to validation. Repeat affected
checks and required review, commit, push, and return here with the same PR.

Read failed check logs before fixing code or retrying. Apply the existing validation rules to
repository failures. Retry temporary service failures up to three times, then report the
blocker. Refresh affected evidence after updating the base.

Ask for needed decisions in the PR and read my replies while continuing to watch. Keep work that
depends on my answer pending. If access prevents further checks, report the blocker in chat and
save the revision, pending feedback, and next monitoring action in the issue for the work when
accessible. Record an interrupted watch as unfinished and resume the full cycle when continuing
the work.

## Ready to merge

Read the PR head again. Check that required checks and reviews pass, expected bot reviews have
finished, no actionable feedback is open, and the PR can merge. Repeat on the new revision if
the head changes during this check.

Mark the ticket `awaiting-merge`, keep it open, and report the PR URL and check/review results
in a progress update, keeping the watch active. Continue waiting and checking. If new feedback,
failing checks, or changes make the PR unready, update its ticket status and address them. Leave
merging to me. Do not enable auto-merge or add the PR to a merge queue.

## Stop watching

Stop only when the PR is merged or closed, or when I explicitly stop the watch. Unregister any
built-in watcher when stopping. After merge, update the ticket and its dependents. Report
closed, unmerged work without marking its outcome complete. Keep work that depends on an
unmerged change blocked. Finish the effort after its accepted changes have merged.
