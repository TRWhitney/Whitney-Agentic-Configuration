# GitHub work store

Use the repository in the project's settings for `gh` commands. Add issues to `project_url` when set.

## Records

Store the specification in a parent issue and each implementation ticket in a sub-issue. A tweak
or fix uses one issue. Use the shared artifact formats with issue URLs in place of local paths.

Store a wayfinding map in a separate issue with decision sub-issues. Keep answers and evidence in
the decision that owns them. Use native dependencies for blockers and sub-issues for membership.

Read issue bodies, comments, dependencies, and linked PRs before updating work. Put accepted sources
in the issue or link files at a published revision. Keep machine paths and temporary state local.

Update tickets on GitHub. Keep converted local files as history with links to their issues. Use
`--body-file` for multiline writes. Save returned URLs and check created records. After an uncertain
response, look for the record before retrying creation.

## Status

Use `ready-for-agent`, `active`, `blocked`, or `awaiting-merge` labels on open implementation tickets.
Reuse equivalent repository labels. Omit Status from the issue body. Project fields follow the labels.

Close a ticket as completed after its PR merges and its acceptance checks are met. Cancellation
needs a separate decision about dependent work. Close the parent when its accepted outcome is done.

Keep the workflow, state, next action, revision, and evidence links on the issue or PR. Keep exact
installed navigator commands in the local continuation record.
