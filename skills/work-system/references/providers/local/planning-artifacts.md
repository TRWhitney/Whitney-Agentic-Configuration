# Planning document formats

## Specification

Store the accepted specification as `spec.md`:

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

Under `Implementation Decisions`, link each wayfinding decision and domain term or architecture
decision that constrains the specification. State the agreed conclusion without copying its
rationale or evidence. Each implementation ticket's `Accepted sources` section links to the
specification and the decisions, research, prototypes, or project documents needed for its
result.

## Implementation ticket

An implementation ticket is a self-contained unit of accepted work sized for one fresh
implementation context.

Store one ticket per result as `tickets/<NN>-<slug>.md`:

```markdown
# <NN> <Ticket title>

**What to build:** <observable end-to-end behavior>

**Blocked by:** <ticket links or none>

**Status:** ready-for-agent

- [ ] <acceptance criterion>
- [ ] <acceptance criterion>

## Accepted sources

## Completion evidence
```

Use `ready-for-agent`, `active`, `blocked`, and `complete` as the ticket lifecycle. Each ticket
must fit one fresh context, connect the layers needed for one working result, and be
independently demonstrable or verifiable. Use dependency order for numbering, but choose the
next tickets by which dependencies are complete, not ticket numbers.

Prefer tickets that each deliver a working result across all needed layers. For a mechanical
change too large to keep tests passing in one ticket, split it into adding the new structure,
moving callers, and removing the old structure. Make their dependencies explicit. Do not include
specific file paths or code snippets unless a prototype-derived fragment is itself an accepted
source.
