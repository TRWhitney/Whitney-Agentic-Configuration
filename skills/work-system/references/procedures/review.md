# Review Procedure

Inspect validated work against accepted intent and engineering risk. Keep review independent,
read-only, and distinct from implementation and validation.

## Establish the review scope

Give reviewers the complete work for the accepted outcome, including every task-owned change. If
the task scope cannot be identified, do not dispatch review.

Gather my request, acceptance checks, specification or ticket, accepted decisions and prototype
contracts, current verification evidence, and affected public interfaces. Provide these sources
without prior conclusions, suspected defects, or unrelated project history.

## Dispatch independent review

Prefer separate fresh-context subagents for the intent and engineering axes when available. One
fresh reviewer may cover both for a genuinely small, low-risk change if it reports each axis
separately. If fresh contexts are unavailable, perform both reviews yourself and do not claim
independent review.

Give every reviewer exact file and Git boundaries. Reviewers must work read-only: they must not
edit or format files, stage or commit changes, alter repository history, discard work, or use
destructive commands. They may inspect existing evidence but must not rerun validation checks or
turn review into another validation pass.

- **Intent axis:** Compare the final change and demonstrated behavior with accepted intent. Look
  for missing or incorrect behavior, scope creep, visual or interaction mismatches, unproven
  acceptance checks, and unintended changes.
- **Engineering axis:** Compare the change with applicable engineering constraints. Inspect
  architecture and dependency boundaries, maintainability, types, error handling, security,
  focused test quality, and unnecessary complexity.

Require each finding to identify the affected file and line when applicable, the violated source
or observable consequence, and its impact. Separate objective defects, judgment calls, and missing
evidence. Omit praise and implementation narration, and state `no findings` when an axis is clean.

## Adjudicate findings

Validate every finding against the complete work and accepted sources before accepting it. Reject
unsupported findings and combine duplicates; reviewer agreement does not replace direct evidence.
Keep objective defects distinct from choices that require my judgment and from evidence that is
missing or stale.

Do not modify the work while reviewing it. A validated problem makes the review fail. After
remediation and renewed validation, repeat every review axis whose evidence or conclusions may
have changed.

## Result

Include the reviewed outcome, which axes ran and whether they were independent, and a pass or fail
for each axis. Include each validated finding with its evidence, impact, and classification, plus
any unresolved judgment. State `no findings` explicitly for a clean axis.
