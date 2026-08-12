# Local work store

Use this adapter when the repository has no existing work-tracking convention. Keep the model tracker-neutral so a future GitHub adapter can replace storage without changing workflow semantics.

## Location

Store durable effort artifacts under `.work/<effort-slug>/`. Commit the directory. Do not treat it as scratch space.

```text
.work/<effort-slug>/
├── status.md
├── spec.md
├── decisions/
├── items/
└── prototypes/
```

Create only the directories an effort needs.

## Required operations

Any future adapter must support the same operations:

1. Create or load an effort by stable identifier.
2. Record its destination, route, current phase, and out-of-scope boundary.
3. Record a decision once and link to it from the effort index.
4. Create a work item with acceptance checks and dependency identifiers.
5. List the frontier: ready items whose dependencies are complete. Exclude items whose status is blocked even when their item dependencies are complete.
6. Link accepted sources such as specs, prototypes, and research.
7. Record redacted verification evidence and the next resumable action.

Redact secrets and sensitive values from commands, output, screenshots, traces, payloads, and linked artifacts before writing them to this committed store. Use descriptive placeholders such as `<REDACTED_TOKEN>`.

## Status file

Use these headings and omit empty optional sections:

```markdown
# <Effort name>

## Destination

## Route

## Current state

## Progress

## Accepted sources

## Decisions

## Work items

## Verification

## Out of scope

## Continuation
```

Keep `status.md` an index. Store a decision, work item, or prototype contract in exactly one file and link it rather than copying its content into the index.

## GitHub extension seam

Map an effort to a parent issue, decisions and work items to child issues, dependencies to native blocking relationships, accepted sources to linked artifacts, and the frontier to an issue query. Do not introduce GitHub identifiers or assumptions into the core skills until that adapter is deliberately added.
