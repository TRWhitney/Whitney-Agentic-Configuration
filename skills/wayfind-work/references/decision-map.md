# Decision map

Store each decision once through the active work adapter and keep the effort record as a linked index. For the local adapter, serialize decisions under the active effort's `decisions/` directory and use `status.md` as the index.

## Decision file

```markdown
# <Decision name>

**Status:** open | settled | out-of-scope
**Blocked by:** <decision links or none>
**Method:** conversation | research | prototype | prerequisite-task

## Question

## Evidence

## Resolution

## Consequences
```

An open, dependency-free decision belongs to the visible frontier. A suspected area whose precise question depends on an unsettled decision remains fog in the adapter's effort status; for the local adapter, that is `status.md`.

For prototype decisions, link the permanent prototype artifact and its confirmed acceptance contract. For researched decisions, cite primary sources in `Evidence`.
