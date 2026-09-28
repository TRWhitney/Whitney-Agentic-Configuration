# Wayfinding Formats

## Decision map

Store the map in the repository's planning documentation. Follow its existing layout, or use
`docs/planning/<effort-slug>/map.md`. Link decision tickets using their tracker locations:

```markdown
# <Effort name>

## Destination

## Notes

## Decisions so far

- [<Decision title>](<decision-ticket-location>): <one-line conclusion>

## Not yet specified

## Out of scope
```

The map is an index. Link the current frontier from the map; keep each open decision's details in
its ticket. Keep an area under `Not yet specified` until its question can be stated precisely.

## Decision ticket

Store one ticket per question according to the work-record guidance:

```markdown
# <NN> <Decision title>

**Status:** open | claimed | resolved | out-of-scope
**Blocked by:** <decision links or none>
**Type:** research | prototype | discussion | task

## Question

## Answer

## Evidence
```

Use `Type` to identify how the question will be settled:

- `discussion` requires my judgment;
- `research` requires factual investigation;
- `prototype` requires concrete exploration;
- `task` requires a prerequisite action that answers the decision without implementing the
  destination.

Use `Answer` for the resolution, rationale, and consequences. Link supporting research, accepted
prototypes, and canonical domain or architecture records from `Evidence` instead of copying them.

Size each ticket for one fresh context. A precise, open, unblocked, and unclaimed ticket belongs
to the frontier. Claim it before work. On resolution, record the answer and evidence once, update
its status, and add only a linked one-line conclusion to the map.

Refer to decisions by linked title in prose. Use numbers only for ordering and dependency
identity. When a resolution invalidates another ticket, update or remove the invalid ticket and
recompute the frontier and remaining fog.
