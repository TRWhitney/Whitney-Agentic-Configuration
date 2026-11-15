# 01 Preserve reusable project operating instructions

**What to build:** Discoverable operating-document authoring guidance integrated with the
existing workflow and demonstrated through behavioral evaluations.

**Blocked by:** none

**Status:** complete

- [x] Approved guidance is available through implementation and documentation.
- [x] Existing project context points to relevant operating docs; validation retains its rules.
- [x] Creation, fresh-agent reuse, maintenance, and controls have inspected behavioral evidence.
- [x] Navigator, affected regressions, configured quality checks, and independent review pass.

## Accepted sources

[Specification](../spec.md).

## Completion evidence

[Trial findings](../../../docs/research/project-operations-trials.md): 15 valid task attempts pass;
10/10 independently authored calibration examples match. Independent intent and engineering
reviews pass with no findings. Three initial feature attempts were superseded after eval repairs;
approved subject guidance was unchanged.

Repository checks:

- `uv run --group dev python -m unittest tests.test_work_system tests.test_project_context`: 45 pass.
- `uv run --group eval python -m unittest tests.test_project_operations_cases tests.test_eval_cases tests.test_eval_planning_cases`: 30 pass.
- `uv run --group dev python -m unittest tests.test_deploy`: 33 pass.
- `uv run --group dev python -m unittest tests.test_navigators`: 7 pass.
- `uv run --group eval python -m evals validate`: 179 definitions valid.
- `uv run --group dev ruff check .`, `uv run --group dev ruff format --check .`,
  `uv run --group dev mypy .`, and `git diff --check`: pass.

Navigator probes load the format in all three implementation states and delivery documentation;
validation access and text remain unchanged. Structural skill validation passes.
Python-version and service-lifecycle limits are recorded in the findings.
