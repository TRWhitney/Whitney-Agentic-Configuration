# Local Work Store

An effort is the durable parent record for one novel-work outcome. Store each effort under
`.work/<effort-slug>/`. Commit the effort directory and treat it as a continuation record, not
scratch space.

```text
.work/<effort-slug>/
├── status.md
├── map.md
├── decisions/
├── spec.md
├── tickets/
├── research/
└── prototypes/
```

Create only the files and directories the effort needs. `map.md` exists only when planning uses
wayfinding. Keep `status.md` and `map.md` separate.

## Status

Use `status.md` as the compact continuation index:

```markdown
# <Effort name>

## Destination

## Current state

## Progress

## Frontier

## Blockers

## Accepted sources

## Verification

## Out of scope

## Continuation
```

Omit empty optional sections. Link the map, decisions, specification, tickets, research, and
prototypes instead of copying their detail. Record the exact next action, current branch,
relevant commits, owned uncommitted paths, and redacted verification results when continuation
requires them.

When `map.md` exists, use `Frontier` to link the map rather than copying its decision list. Keep
the full decision frontier canonical in the map and record the exact next action under
`Continuation`.

## Retention

Retain the completed effort directory as the history and handoff record. Keep accepted domain
terms and architecture decisions in their durable project locations rather than duplicating them
under `.work/`.

Committed `research/` entries preserve reports whose evidence, reasoning, or citations future work
will need to revisit. Keep other findings in their owning artifact. Link external and repository
sources from the report rather than copying full source trees.

Committed `prototypes/` entries preserve accepted self-contained artifacts or link to accepted
prototype source hosted elsewhere in the repository. Keep that source in normal repository
history and clearly isolated from production paths. Remove rejected alternatives, temporary build
products, disposable data, and instrumentation when they no longer provide evidence.

Redact secrets and sensitive values from commands, output, screenshots, traces, payloads, and
linked artifacts before committing the record.
