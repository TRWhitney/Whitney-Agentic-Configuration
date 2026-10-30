# 12 Complete assessment and report behavior

**What to build:** Read-only file inspection for the blinded judge, preserved interrupted work,
phase measurements, and separate behavior and assessment outcomes.

**Blocked by:** None.

**Status:** complete

- [x] Preserve completed answers after late usage notifications and observations on interruption.
- [x] Replace oversized prompts and custom evidence decoding with complete readable files.
- [x] Record phase time and reported token breakdowns; make token guards optional.
- [x] State correct, incorrect, or unknown behavior separately from assessment completion.
- [x] Validate the framework and existing assessor examples, rerun the two audit cases, inspect
  evidence, review, retain findings, and remove finished raw outputs.

## Accepted sources

[Specification](../spec.md#assessment-completion).
[Authoring standards](../../../docs/eval-authoring.md).

## Verification

[Results](../../../docs/research/assessment-completion-evals.md) retain all assessor and audit
outcomes. Lint, formatting, strict typing, all 130 definitions, and JavaScript syntax pass.
All 384 framework tests and focused correction checks pass for commentary retained separately
from final replies and for candidate evidence preserved when private browser collection fails.
Independent intent and engineering correction reviews pass.
