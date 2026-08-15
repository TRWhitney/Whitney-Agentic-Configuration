# Domain Modeling Procedure

Preserve accepted domain language and consequential architecture decisions as durable project
knowledge. Record accepted decisions; do not make them through documentation.

## Decide what is durable

- Record a domain term when it names a project-specific concept used across a meaningful
  boundary and inconsistent language would create ambiguity.
- Record an architecture decision when it is costly to reverse, surprising without context, and
  the result of a genuine tradeoff.
- Leave proposed terminology, open choices, implementation plans, and temporary assumptions in
  their working artifacts until they are accepted.
- Do not create durable documentation for ordinary programming vocabulary, self-evident code
  structure, or every technical choice.

## Record it once

Use the associated domain documentation format and create only the artifacts accepted knowledge
requires.

- Give each concept one canonical term and identify misleading alternatives only when doing so
  prevents real confusion. Keep definitions concise and free of implementation detail.
- Store a decision with its context, accepted choice, and reason. Do not turn it into a
  specification, ticket, or progress log.
- Supersede an obsolete decision instead of erasing the reason it once governed the project.
- Link specifications, work records, and related decisions to the canonical artifact instead of
  copying its content into each one.

## Result

Include the created or updated canonical terms, decision references, and any knowledge left in a
working artifact because it remains unsettled.
