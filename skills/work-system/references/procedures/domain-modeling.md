# Domain Modeling Procedure

Document agreed project terms and architecture decisions that future work needs to understand.
Record decisions after they are agreed; do not make them by writing documentation.

## Decide what needs documenting

- Record a domain term when it names a project-specific concept used in multiple parts of the
  project and inconsistent language would create ambiguity.
- Record an architecture decision when it is costly to reverse, surprising without context, and
  the result of a genuine tradeoff.
- Leave proposed terminology, open choices, implementation plans, and temporary assumptions in
  their working notes until they are accepted.
- Do not create permanent documentation for ordinary programming vocabulary, self-evident code
  structure, or every technical choice.

## Record it once

Use the associated domain documentation format and create only the documents needed for agreed
terms and decisions.

- Give each concept one standard term and identify misleading alternatives only when doing so
  prevents real confusion. Keep definitions concise and free of implementation detail.
- Store a decision with its context, accepted choice, and reason. Do not turn it into a
  specification, ticket, or progress log.
- Mark an obsolete decision as replaced and link its replacement. Keep its original reason.
- Link specifications, work records, and related decisions to the original document instead of
  copying its content into each one.

## Result

Include the created or updated terms, decision references, and any knowledge left in working
notes because it remains unsettled.
