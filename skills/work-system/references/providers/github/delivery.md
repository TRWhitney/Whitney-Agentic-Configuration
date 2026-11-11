# File and babysit a PR

## File or resume

For planning or implementation delivery, check the issue, repository, head branch, and base.
Find the branch's existing PR. Push the validated commits and create or update the PR using the
title and description guidance below. If the request to create a PR times out or returns no PR
URL, check GitHub for a PR with the same head and base branches before retrying.

Save the PR URL, head revision, base, and next action on the work item. Read the repository's
required checks and reviews, including review bots that run after a push.

## PR title and description

Use the title to say what someone can now do or what behavior changes.

Write the description for someone who has no knowledge of the project, its domain, or its
implementation, and no technical background. Introduce the project or component when needed.
Explain necessary terms before relying on them. The description must explain the change and
what accepting it entails without requiring the reader to follow links.

Use all seven sections below in every PR description, including small changes. Use level-two
headings in this order. Scale the length to the change while keeping each section's required
information:

### Problem

Explain the existing behavior, a recognizable trigger, and the concrete problem it causes.
Say what earlier work already delivered when needed to understand this PR's changes.

### What changed

Describe the resulting behavior and practical consequences. Explain what triggers it, what now happens, what
someone using it must do, and what happens after a failure or edit when relevant. Describe
behavior rather than listing files or internal names.

### Code example

Show a realistic example supported by the implementation. Use code, configuration, a command,
or a concrete interaction as appropriate. Explain what it does and the relevant success or
failure outcomes. Give different concepts separate examples. Do not invent code to fill this
section.

### Why this was needed

Explain why the old behavior was inadequate and the practical requirement this change meets.

### Why this approach

Explain why this solution fits the problem, including the meaningful tradeoff or constraint
behind the choice. Include implementation details only when they help assess that choice.

### Setup and limits

State required installation, configuration, dependencies, and supported environments. Explain
what happens automatically and what a person using or integrating the change must supply.
Keep limitations that affect use or review, including extra work, unsupported cases,
compatibility changes, debugging consequences, and failure behavior. Explain what happens when
a limit is reached, including whether work stops, skips that part, or continues. A small change
may need only a brief statement that no new setup is required.

### Validation

State what was checked, at which revision, and what the results establish. Distinguish completed
checks from pending or unavailable evidence. Include links to the documentation, runnable
examples, and tests that support the claims, using the reviewed revision in each link. Explain
what they demonstrate. Do not dump command histories,
resolved temporary setup problems, or unexplained test counts.

End the description with the relevant issue reference, using a closing reference when appropriate.

Before publishing, check the seven headings, their order, and the final issue reference. Read
the description as someone encountering the project for the first time.
Check that it explains the problem, change, example, need, solution choice, setup, consequences,
limits, and evidence. Read the linked files and verify examples and links against the final
implementation. Rewrite the title, description, examples, and links when the work changes.
Omit conversation history and abandoned approaches unless they explain a necessary tradeoff.

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

While planning, keep document corrections and design questions in planning. During
implementation delivery, take code corrections to implementation
and outdated evidence to validation. Repeat affected checks and required review, commit, push,
and return here with the same PR.

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

For an implementation PR, mark the ticket `awaiting-merge` and keep it open. For a planning PR,
keep the parent issue open and record the pending merge there. Report the PR URL and check/review
results in a progress update, keeping the watch active. Continue waiting and checking. If new feedback,
failing checks, or changes make the PR unready, update its ticket status and address them. Leave
merging to me. Do not enable auto-merge or add the PR to a merge queue.

## Stop watching

Stop only when the PR is merged or closed, or when I explicitly stop the watch. Unregister any
built-in watcher when stopping. After merge, update the work record and its dependents. While
planning, recheck the design and ticket coverage before moving to implementation.
Keep implementation tickets open. Report closed, unmerged work without marking its outcome
complete. Keep work that depends on an
unmerged change blocked. Finish the effort after its accepted changes have merged.
