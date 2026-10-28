# Workflow recovery

## Destination

[Restore workflow state and finish planning before implementation](spec.md).

## Current state

The planning, provider, and conversation-specific persistence changes are implemented and
validated.

## Frontier

1. [Save and restore navigation progress](tickets/01-navigation-records.md).
2. [Preserve optional wayfinding substates](tickets/02-optional-substates.md).
3. [Complete design and tickets before implementation](tickets/03-complete-planning.md).
4. [Restore through the skill after compaction](tickets/04-recovery-guidance.md).
5. [Keep tracker selection tied to the current task](tickets/05-tracker-selection.md).

## Accepted sources

[Specification](spec.md).

## Verification

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest`: 162 tests passed.
- `.venv/bin/ruff check .`: passed.
- `.venv/bin/mypy --no-incremental .`: 19 source files passed.
- Skill validation, navigator synchronization, and whitespace checks passed.
- New CLI tests failed before implementation and pass with saved state and substate support.
- Independent intent and engineering reviews passed.
- All 21 local document links resolve.

## Continuation

No remaining implementation work.
