# Workflow recovery

## Destination

[Restore workflow state and finish planning before implementation](spec.md).

## Current state

Planning. The design and implementation tickets have completed document review. Implementation
waits for the planning PR on `design/workflow-recovery` to merge.

## Frontier

1. [Save and restore navigation progress](tickets/01-navigation-records.md).
2. [Preserve optional wayfinding substates](tickets/02-optional-substates.md).
3. [Deliver the full plan before implementation](tickets/03-planning-delivery.md).
4. [Restore through the skill after compaction](tickets/04-recovery-guidance.md).

## Accepted sources

- [Specification](spec.md).
- [Work-system skill](../../skills/work-system/SKILL.md).

## Verification

The design and tickets cover the agreed scope. Intent and engineering review were performed
without a separate reviewer. All 15 document links resolve. Whitespace checks pass.

## Continuation

Resume with `python3 skills/work-system/scripts/navigate.py resume novel-work planning`.
Branch: `design/workflow-recovery`. Base: `origin/main`.

Publish these planning records and wait for merge. After the planning PR merges, start the first
ticket from the merged planning commit.
