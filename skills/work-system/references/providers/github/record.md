# GitHub work store

Use the repository in the project's settings for `gh` commands. Add issues to `project_url` when
set.

Prefix issue bodies, issue comments, and PR comments with your model name, e.g. `[GPT-6.1-Sol]`.
Before posting updates or finishing, read and address all issue and PR comments and reviews
added or edited since your last read, across all pages. Your own posts do not advance that
checkpoint.

## Questions and discussion

Find the open PR for the current work from the work item's links or the working branch. When one
exists, keep questions, clarification, decision requests, and work discussion in its comments.
Reply in the relevant review thread when the discussion concerns that finding; otherwise use a
PR conversation comment. Read the existing discussion before asking or replying.

A request to rewrite or clarify a PR description authorizes editing that description. It does
not, by itself, authorize repository changes or a commit or push. Identify a separate code
change already covered by the agreed scope before changing repository files. If that need would
change the scope, ask me in the PR before proceeding.

Check the PR for my replies and continue the discussion there. Keep work that needs my answer
pending until I respond, while continuing independent work and the PR watch. A posted question
or elapsed time is not an answer or approval. In chat, link the PR discussion when an update is
needed rather than repeating the question.

When no open PR exists for the current work, ask in chat. If GitHub access prevents posting or
reading the discussion, report that blocker in chat and ask there for any input needed to
proceed.

## Records

Use one parent issue for the effort's specification and status. Each feature has one combined
research-and-planning issue containing its questions, investigations, requirements, and agreed
design. For a single-feature effort, the parent may serve as that feature issue. For a
multi-feature effort, use feature sub-issues. Reuse the existing issue for that work. A tweak or
fix uses one issue for its work, reusing an existing issue when available rather than creating
another planning issue for an existing feature.

Decompose actual implementation into logical units of work, each with its own useful
deliverable, acceptance checks, and genuine dependencies. Store these implementation tickets as
sub-issues of the effort. One feature may need several implementation tickets. Use native
dependencies for genuine blockers. Do not create `.work/` or repository copies of these tracking
records.

Before creating any issue, check existing records for this work, including any parent, related
open and closed issues, their discussions, and linked planning maps or specifications. Extend
the existing design issue or ticket when the subject belongs to its feature. Reopen a resolved
feature-planning issue if its design becomes unsettled again; do not create a successor for each
refinement. Only a distinct feature qualifies for a separate research-and-planning issue. A
question, detailed requirement, architecture concern, method, evidence requirement, or context
limit within a feature does not. State the distinct feature in a new planning issue's body and
why it does not belong in existing feature issues. For a new implementation issue, state its
logical delivery unit and check for another ticket already covering that work. The feature-only
rule for planning does not restrict implementation decomposition.

When requirements settle and before a planning handoff, check for overlapping records. Move
useful questions, agreed answers, reasons, and source links into the existing design issue,
ticket, or linked specification. Do not copy every conversational step. Update map links, native
blockers, and dependent accepted sources, then close superseded issues with a replacement link.
Reuse an existing record where possible; consolidation does not require another maintenance
issue. Changing nesting or closing issues alone is not consolidation.

Keep planning maps, research reports, and prototype notes in repository documentation. Link that
documentation from the issues that use it. Use the shared wayfinding format for the map and
decision records, with issue URLs or section links for their owners.

Read issue bodies, comments, dependencies, and linked PRs before updating work. Link accepted
documentation and executable sources at published revisions when available. Use system temporary
files for command input and remove them after use.

Use `--body-file` for multiline writes. Save returned URLs and check created records. After an
uncertain response, look for the record before retrying creation.

## Status

Use `ready-for-agent`, `active`, `blocked`, or `awaiting-merge` labels on open implementation
tickets. Reuse equivalent repository labels. Omit Status from implementation issue bodies.
Project fields follow the labels. Feature research-and-planning issues use the status field in
their shared format.

Keep native issue state aligned with the decision record. `open` and `claimed` decisions remain
open. When a feature's planning is settled, record its agreed requirements and supporting
sources, set `resolved`, and close its planning issue as completed without requiring a PR. Close
an `out-of-scope` or superseded planning issue as not planned, with its reason and any
replacement link. Keep unresolved feature planning open. Resolving a design section within the
parent does not close the parent while its accepted outcome remains unfinished.

Close an implementation ticket as completed after its PR merges and its acceptance checks are
met. Before cancelling or superseding work, update dependent work and blockers; cancellation
does not itself require another issue. Close the parent when its accepted outcome is done.

## Continuation

Store status and continuation only in the parent issue, or the single issue for a tweak or fix.
Update its `Continuation` section with the workflow, state, exact resume command, next action,
branch, relevant commits, this task's uncommitted paths, and verification results needed to
continue. Link decision tickets, the planning map, accepted sources, and any PR. Replace stale
details rather than appending a running log. Keep ticket-specific progress on its existing
issue; do not create a status issue.
