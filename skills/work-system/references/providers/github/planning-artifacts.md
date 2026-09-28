# Planning Artifact Formats

## Specification

Use the parent issue body for the specification:

```markdown
# <Outcome>

## Problem Statement

## Solution

## User Stories

1. As an <actor>, I want <behavior>, so that <benefit>.

## Implementation Decisions

## Testing Decisions

## Out of Scope

## Further Notes
```

Use the project glossary and respect applicable architecture decisions. Capture the accepted
behavior, boundaries, interfaces, schemas, interactions, and testing seams. Prefer the highest
stable testing seam that already exists. Avoid file-by-file instructions and code snippets that
will go stale. A concise prototype-derived state machine, schema, reducer, or type shape may be
included when it preserves a decision more precisely than prose.

Under `Implementation Decisions`, link each wayfinding decision and canonical domain or
architecture record that constrains the specification. Preserve the accepted conclusion without
copying its rationale or evidence. Each implementation ticket's `Accepted sources` section links to
the specification and the decisions, research, prototypes, or canonical records needed for its
slice.

## Implementation ticket

An implementation ticket is a self-contained unit of accepted work sized for one fresh
implementation context.

Use a sub-issue for each implementation ticket:

```markdown
# <NN> <Ticket title>

**What to build:** <observable end-to-end behavior>

**Blocked by:** <ticket links or none>

- [ ] <acceptance criterion>
- [ ] <acceptance criterion>

## Accepted sources

## Completion evidence
```

Use the issue lifecycle described by the work store. Each ticket
must fit one fresh context, cut a narrow but complete path through the required layers, and be
independently demonstrable or verifiable. Use dependency order for numbering, but determine the
frontier from completed blockers rather than ticket numbers.

Prefer vertical slices. For a mechanical change whose blast radius cannot remain green as one
slice, use expand, migrate, and contract tickets with explicit blocking edges. Do not include
specific file paths or code snippets unless a prototype-derived fragment is itself an accepted
source.
