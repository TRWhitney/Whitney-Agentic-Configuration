# 01 Support measured performance work

**What to build:** A selectively loaded performance procedure that guides investigation,
implementation, and final acceptance through the existing navigator.

**Blocked by:** none

**Status:** complete

- [x] Approved procedure is available in discovery, implementation, and validation only.
- [x] State output contains its cue, while explicit loading supplies its detailed instructions.
- [x] Behavioral cases demonstrate measured work, appropriate conclusions, and scoped controls.
- [x] Calibration, relevant regressions, quality checks, and independent reviews pass.

## Accepted sources

[Specification](../spec.md) and approved proposal in this conversation.

## Completion evidence

[Trial findings](../../../docs/research/performance-procedure-trials.md): all four task cases
pass three attempts each; the clarified control passes three fresh attempts. The original
control reporting failure is retained. Eight independent calibration labels match.
Independent intent and engineering delivery reviews passed with no findings.

Repository checks:

- `uv run --group dev python -m unittest tests.test_work_system tests.test_project_context tests.test_navigators tests.test_deploy`: 86 pass.
- `uv run --group eval python -m unittest tests.test_performance_cases tests.test_eval_cases tests.test_eval_planning_cases`: 33 pass.
- `uv run --group dev python -m unittest tests.test_work_system_compaction tests.test_work_system_sessions tests.test_project_eval_fixtures`: 49 pass.
- After clarification, `uv run --group dev python -m unittest tests.test_work_system`: 36 affected tests pass again.
- `uv run --group eval python -m evals validate`: 184 definitions valid.
- `uv run --group dev ruff check .`, `uv run --group dev ruff format --check .`,
  `uv run --group dev mypy .`, structural skill validation, and `git diff --check`: pass.
