# 04 Restore through the skill after compaction

**What to build:** Direct recovery through the skill and the saved navigator state.

**Blocked by:** [Optional substates](02-optional-substates.md).

**Status:** complete

- [x] Global instructions direct the agent to read work-system after context compaction and
      restore any active repository workflow before continuing.
- [x] The skill gives the plain resume command and explains conversation identity and work-record
      lookup.
- [x] Existing recovery wording is updated to use the saved state without repeating detailed
      state or wayfinding instructions in the skill entrypoint.
- [x] Restored output includes active substate guidance and formats from their existing sources.
- [x] Standalone installation and deployment checks include the new resources.
- [x] Focused work-system, navigator packaging, and deployment tests pass; note-system behavior
      remains unchanged.
- [x] Skill validation, formatting, lint, type checks, and changed-link checks pass.

## Accepted sources

[Restore through the skill](../spec.md#restore-through-the-skill).

## Completion evidence

Acceptance checks and independent review pass. See [verification](../status.md#verification).
