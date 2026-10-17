# Review Procedure

Check validated work against the request and look for engineering problems. Keep review
independent and read-only. Do not implement changes or repeat validation during review.

## Establish the review scope

Give reviewers the complete work for the accepted outcome, including every change made for the
task. If the task scope cannot be identified, do not dispatch review.

Gather my request, acceptance checks, specification or ticket, agreed decisions and prototype
requirements, current verification evidence, and affected public interfaces.

Supply temporary evidence paths when needed and keep those captures available through required
review. Include the retention rules and explicit exceptions in each reviewer assignment. Review
does not require committed captures or full run histories unless I explicitly requested it.

For the initial complete review, provide these sources without prior conclusions, suspected
defects, or unrelated project history. For a correction review, also provide the admitted
blocking findings, the correction, and renewed evidence. Bound that review to those findings,
the correction, and conclusions the correction could plausibly affect.

## Dispatch independent review

Perform one complete review of the accepted outcome. Do not dispatch another complete review
merely because the first review found a blocker.

Prefer separate fresh-context subagents for the intent and engineering axes when available. One
fresh reviewer may cover both for a genuinely small, low-risk change if it reports each axis
separately. If fresh contexts are unavailable, perform both reviews yourself and do not claim
independent review.

Give every reviewer the files they may read and Git operations they may use. Reviewers must work
read-only: they must not edit or format files, stage or commit changes, alter repository
history, discard work, or use destructive commands. They may inspect existing evidence but must
not rerun validation checks or turn review into another validation pass.

- **Intent axis:** Compare the final change and demonstrated behavior with accepted intent. Look
  for missing or incorrect behavior, scope creep, visual or interaction mismatches, unproven
  acceptance checks, and unintended changes.
- **Engineering axis:** Compare the change with applicable engineering constraints. Inspect
  architecture and dependency boundaries, maintainability, types, error handling, security,
  focused test quality, and unnecessary complexity.

Require each finding to identify the affected file and line when applicable, the violated source
or observable consequence, and its impact. Separate objective defects, judgment calls, and
missing evidence. Omit praise and implementation narration, and state `no findings` when an axis
is clean.

## Assess findings

Validate every proposed finding against the complete work and accepted sources before accepting
it. Reject unsupported findings and combine duplicates; reviewer agreement does not replace
direct evidence. Keep objective defects distinct from choices that require my judgment and from
evidence that is missing or stale.

Treat a finding as blocking only when all of these conditions hold:

- It identifies concrete evidence in the complete work.
- It contradicts accepted intent or an applicable repository constraint, or demonstrates a
  significant problem.
- It occurs through a use or environment supported by the accepted sources, unless it is a
  credible security or data-integrity risk.
- Correcting it belongs to the current accepted outcome rather than unrelated future work.

A concern that does not meet every condition must not fail the review. Reject speculative
hardening, stylistic preference, exhaustive combinations not promised by accepted sources, and
misuse outside the supported boundary. Record a concrete and useful concern as a nonblocking
follow-up only when it would help future work; do not add it to the active workflow without my
acceptance.

Report a credible security or data-loss concern immediately even when its ownership lies outside
the accepted outcome. Treat uncertainty about which task covers a problem or which uses are
supported as a judgment for me rather than silently expanding the work.

Do not modify the work while reviewing it. An admitted blocking finding makes the review fail.
After corrections and validation, perform a correction review of the admitted findings, the
correction, and affected conclusions. Admit a new blocker during correction review only when the
correction caused it or it invalidates a conclusion within that boundary. Repeat the complete
review only when corrections substantially change agreed behavior, public interfaces,
architecture, or the set of changed files enough that the earlier review no longer applies.

## Result

Return concise findings for the owning record. Do not retain reviewer transcripts, evidence
manifests, or elaborate review records. The parent agent deletes temporary captures after
required review and before delivery.

Include the reviewed outcome, the axes reviewed, whether each review was independent, and a pass
or fail for each axis. Include each blocking finding with its evidence, impact, and
classification, plus any unresolved judgment. List nonblocking follow-ups separately and state
that they do not fail review. State `no blocking findings` for a passing axis and `no findings`
when the axis has no reportable observation.
