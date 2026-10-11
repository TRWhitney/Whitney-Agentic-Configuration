# Wayfinding formats

## Decision map

Store the map in the repository's planning documentation. Follow its existing layout, or use
`docs/planning/<effort-slug>/map.md`. Link decisions to the combined research-and-planning ticket
for their feature. Several decisions may link to sections of the same ticket:

```markdown
# <Effort name>

## Destination

## Notes

## Decisions so far

- [<Decision subject>](<owning-record-location>): <one-line conclusion>

## Not yet specified

## Out of scope
```

The map is an index. Link the current frontier from the map; keep questions and accepted answers
in their owning record. Multiple map entries may link to sections of the same design issue.
Keep an area under `Not yet specified` until a question can be stated precisely and its effect
on the first deliverable is known. Later concerns belong under `Out of scope` for that deliverable.

## Feature research-and-planning ticket

Use one combined research-and-planning ticket per distinct feature. If the subject cannot be
considered a distinct feature, it does not get its own planning or research ticket. Record the
feature's questions, subcontracts, technical concerns, research findings, and accepted answers
together. Follow the provider's ownership rules to find or create that feature's ticket.

Use the following format for the feature ticket. For individual questions or contract sections
within it, include only the fields needed to understand the unresolved work and accepted answers:

```markdown
# <NN> <Feature title>

**Status:** open | claimed | resolved | out-of-scope
**Blocked by:** <decision links or none>
**Type:** research | prototype | discussion | task

## Questions

## Accepted answers

## Evidence
```

Use `Type` to identify how the next unresolved part will be settled. Update it when the method
changes; needing both discussion and research does not itself require separate tickets:

- `discussion` requires my judgment;
- `research` requires factual investigation;
- `prototype` requires concrete exploration;
- `task` requires a prerequisite action that answers the decision without implementing the
  destination.

Use `Accepted answers` for the current contract, material rationale, and consequences. Fold
follow-up answers into that contract rather than preserving a question-by-question transcript.
Link supporting research, accepted prototypes, and canonical domain or architecture records from
`Evidence` instead of copying them.

Keep the feature ticket's current contract concise and link supporting artifacts. Context size
does not justify splitting a feature's planning into several tickets. The frontier contains its
unresolved, unblocked decisions that gate the first deliverable. Claim the feature ticket before
working it. Mark its planning resolved only when its blocking questions are settled. Follow the
provider's native closure rules and add only a linked conclusion to the map. Decompose actual
implementation separately into logical units of work with their own acceptance checks.

Refer to decisions by linked title in prose. Use numbers only for ordering and dependency
identity. When a resolution invalidates another record, consolidate its useful conclusions into
the current owner, link the replacement, and retire the superseded record under the provider's
lifecycle. Recompute the frontier and remaining fog.
