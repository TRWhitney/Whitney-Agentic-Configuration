# GitHub work store

Use the repository in the project's settings for `gh` commands. Add issues to `project_url` when set.

Prefix issue bodies, issue comments, and PR comments with your model name, e.g. `[GPT-6.1-Sol]`.
Before posting updates or finishing, read and address all issue and PR comments and reviews
added or edited since your last read, across all pages. Your own posts do not advance that checkpoint.

## Questions and discussion

Find the open PR for the current work from the work item's links or the working branch. When one
exists, keep questions, clarification, decision requests, and work discussion in its comments.
Reply in the relevant review thread when the discussion concerns that finding; otherwise use a
PR conversation comment. Read the existing discussion before asking or replying.

Check the PR for my replies and continue the discussion there. Keep work that needs my answer
pending until I respond, while continuing independent work and the PR watch. A posted question
or elapsed time is not an answer or approval. In chat, link the PR discussion when an update is
needed rather than repeating the question.

When no open PR exists for the current work, ask in chat. If GitHub access prevents posting or
reading the discussion, report that blocker in chat and ask there for any input needed to proceed.

## Records

Use one parent issue for the effort's specification and status. Store decision tickets and
implementation tickets as sub-issues of that parent. A tweak or fix uses one issue. Use native
dependencies for blockers. Do not create `.work/` or repository copies of these tracking records.

Keep planning maps, research reports, and prototype notes in repository documentation. Link that
documentation from the issues that use it. Use the shared wayfinding format for the map and decision
tickets, with issue URLs for ticket links.

Read issue bodies, comments, dependencies, and linked PRs before updating work. Link accepted
documentation and executable sources at published revisions when available. Use system temporary
files for command input and remove them after use.

Use `--body-file` for multiline writes. Save returned URLs and check created records. After an uncertain
response, look for the record before retrying creation.

## Status

Use `ready-for-agent`, `active`, `blocked`, or `awaiting-merge` labels on open implementation tickets.
Reuse equivalent repository labels. Omit Status from implementation issue bodies. Project fields
follow the labels. Decision tickets use the status field in their shared format.

Close a ticket as completed after its PR merges and its acceptance checks are met. Cancellation
needs a separate decision about dependent work. Close the parent when its accepted outcome is done.

## Continuation

Store status and continuation only in the parent issue, or the single issue for a tweak or fix.
Update its `Continuation` section with the workflow, state, exact resume command, next action, branch, relevant
commits, owned uncommitted paths, and verification results needed to continue. Link decision
tickets, the planning map, accepted sources, and any PR. Replace stale details rather than appending
a running log. Keep ticket-specific progress on its existing issue; do not create a status issue.
