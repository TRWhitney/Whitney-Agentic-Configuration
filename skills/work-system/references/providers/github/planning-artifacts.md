# Planning document formats

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
behavior, supported uses, interfaces, schemas, interactions, and test interfaces. Prefer testing
through the highest stable interface already available. Avoid file-by-file instructions and code
snippets that will go stale. A concise prototype-derived state machine, schema, reducer, or type
shape may be included when it states a decision more precisely than prose.

Under `Implementation Decisions`, maintain the agreed requirements and group its related
questions and accepted answers in its feature's combined research-and-planning issue. For a
multi-feature effort, link those feature issues from the parent specification. Link domain terms
or architecture decisions that constrain it. Record the first deliverable and its deferred scope
under `Solution` and `Out of Scope`. State agreed conclusions without copying linked rationale
or evidence. Each implementation ticket's `Accepted sources` section links to the specification
and the decisions, research, prototypes, or project documents needed for its result.

## Implementation ticket

An implementation ticket is a self-contained unit of accepted work sized for one fresh
implementation context.

Decompose implementation into logical units of work with useful deliverables, acceptance checks,
and genuine dependencies. Several implementation tickets may deliver one feature. Check existing
ownership before opening a sub-issue for a delivery unit. Design questions and refinements
update the feature's combined research-and-planning issue. For an implementation ticket, use:

```markdown
# <NN> <Ticket title>

**What to build:** <observable end-to-end behavior>

**Blocked by:** <ticket links or none>

- [ ] <acceptance criterion>
- [ ] <acceptance criterion>

## Accepted sources

## Completion evidence
```

Use the issue lifecycle described by the work store. Each ticket must fit one fresh context,
connect the layers needed for one working result, and be independently demonstrable or
verifiable. Use dependency order for numbering, but choose the next tickets by which
dependencies are complete, not ticket numbers.

Prefer tickets that each deliver a working result across all needed layers. For a mechanical
change too large to keep tests passing in one ticket, split it into adding the new structure,
moving callers, and removing the old structure. Make their dependencies explicit. Do not include
specific file paths or code snippets unless a prototype-derived fragment is itself an accepted
source.
