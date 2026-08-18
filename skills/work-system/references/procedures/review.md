# Review Procedure

Inspect validated work against accepted intent and engineering risk. Keep review independent,
read-only, and distinct from implementation and validation.

## Establish the review scope

Give reviewers the complete work for the accepted outcome, including every task-owned change. If
the task scope cannot be identified, do not dispatch review.

Gather my request, acceptance checks, specification or ticket, accepted decisions and prototype
contracts, current verification evidence, and affected public interfaces.

For the initial complete review, provide these sources without prior conclusions, suspected
defects, or unrelated project history. For a correction review, also provide the admitted blocking
findings, the correction, and renewed evidence. Bound that review to those findings, the correction,
and conclusions the correction could plausibly affect.

## Dispatch independent review

Perform one complete review of the accepted outcome. Do not dispatch another complete review merely
because the first review found a blocker.

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

Validate every proposed finding against the complete work and accepted sources before accepting it.
Reject unsupported findings and combine duplicates; reviewer agreement does not replace direct
evidence. Keep objective defects distinct from choices that require my judgment and from evidence
that is missing or stale.

Admit a proposed finding as blocking only when all of these conditions hold:

- It identifies concrete evidence in the complete work.
- It contradicts accepted intent or an applicable repository constraint, or demonstrates a
  material adverse consequence.
- It occurs through a use or environment supported by the accepted sources, unless it is a
  credible security or data-integrity risk.
- Correcting it belongs to the current accepted outcome rather than unrelated future work.

A concern that does not meet every condition must not fail the review. Reject speculative
hardening, stylistic preference, exhaustive combinations not promised by accepted sources, and
misuse outside the supported boundary. Record a concrete and useful concern as a nonblocking
follow-up only when it would help future work; do not add it to the active workflow without my
acceptance.

Report a credible security or data-loss concern immediately even when its ownership lies outside
the accepted outcome. Treat uncertain ownership or an uncertain supported boundary as a judgment
for me rather than silently expanding the work.

Do not modify the work while reviewing it. An admitted blocking finding makes the review fail.
After remediation and renewed validation, perform a correction review of the admitted findings,
the correction, and affected conclusions. Admit a new blocker during correction review only when
the correction caused it or it invalidates a conclusion within that boundary. Repeat the complete
review only when remediation materially changes accepted behavior, public interfaces,
architecture, or the task-owned surface enough that the earlier review no longer applies.

## Result

Include the reviewed outcome, the axes reviewed, whether each review was independent, and a pass
or fail for each axis. Include each blocking finding with its evidence, impact, and classification,
plus any unresolved judgment. List nonblocking follow-ups separately and state that they do not
fail review. State `no blocking findings` for a passing axis and `no findings` when the axis has no
reportable observation.
