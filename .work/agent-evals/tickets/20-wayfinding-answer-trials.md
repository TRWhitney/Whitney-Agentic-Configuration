# 20 Trial wayfinding after answers

**What to build:** Compare current wayfinding guidance with temporary changes for continuing
questions and updating answers affected by revisions. Check the existing derived-choice case.
Apply the approved tested change to the repository skill.

**Blocked by:** none.

**Status:** complete

- [x] Prepare isolated current and trial sources; retain the existing cases and scoring.
- [x] Inspect comparisons and confirm any supported change in fresh attempts.
- [x] Save the findings, complete review and remove temporary evidence.
- [x] Require continuation after corrections in the existing hidden criteria, then freeze them.
- [x] Trial the full set until repeated attempts meet every requirement without context clearing.
- [x] Review the complete tested proposal, remove raw evidence and present the unapplied diff.

[Requirements](../spec.md#wayfinding-after-answers).

[Findings and tested change](../../../docs/research/wayfinding-answer-trials.md).

Verification: `.venv/bin/python -m unittest discover -s tests -q` passes 444 tests.
Ruff check and format pass; strict mypy passes across 80 files; all 151 cases validate.
The navigator passes 29 session tests, lint, formatting, strict typing and skill validation.
Independent intent and engineering reviews pass with no findings. Reviewed raw evidence was removed.

- [x] Apply the approved skill changes and retain their regression tests.
