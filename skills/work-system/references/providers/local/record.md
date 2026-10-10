# Local Work Store

An effort is the durable parent record for one novel-work outcome. Store each effort under
`.work/<effort-slug>/` and keep it as an uncommitted continuation record while the workflow is
active. Commit the current effort record and its supporting documentation with the completed
outcome during delivery.

```text
.work/<effort-slug>/
├── status.md
├── decisions/
├── spec.md
└── tickets/
```

Store decision tickets as `decisions/<NN>-<slug>.md`. Create only the files and directories the
effort needs. Keep planning maps, research, and prototype notes in repository documentation and
link them from the effort record. Move existing copies out of the effort directory and update
their links.

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
prototypes instead of copying their detail. Record the exact resume command and next action,
current branch, relevant commits, owned uncommitted paths, and redacted verification results when
continuation requires them.

Keep the index current by replacing superseded state, blockers, next actions, and verification
summaries. Do not append a chronological narration of implementation, validation, or review
cycles.

When a planning map exists, use `Frontier` to link it rather than copying its decision list. Keep
the full decision frontier canonical in the map and record the exact next action under
`Continuation`.

## Retention

After delivery, retain the committed effort directory as the history and handoff record. Keep
accepted domain terms and architecture decisions in their durable project locations rather than
duplicating them under `.work/`.

Retain planning maps, research reports, and prototype notes as repository documentation after
delivery. Keep each study to one report of at most 500 words plus a compact results table unless I
explicitly request more. Link canonical findings from the work record rather than copying them.

Retain accepted, self-contained prototype artifacts after delivery. When an accepted prototype
source is hosted elsewhere in the repository, link to it instead. Keep that source in normal
repository history and clearly isolated from production paths. Remove rejected alternatives,
temporary build products, disposable data, and instrumentation after inspection and required
review, before delivery. Keep conclusions about rejected alternatives in the existing notes.

Do not commit raw captures, transcripts, per-run JSON, screenshots, logs, duplicate snapshots,
hash inventories, or evidence manifests unless I explicitly requested retention. Preserve concise
findings and reusable source or checks. Do not replace deleted outputs with cleanup inventories or
elaborate review records. Redact secrets from the concise evidence retained in the record.
