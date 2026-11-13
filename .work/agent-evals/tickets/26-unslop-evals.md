# 26 Evaluate unslop writing and use

**What to build:** Writing cases and controls, comparison with Poteto, and older-corpus regression evidence.

**Blocked by:** None.

**Status:** complete

## Sources and findings

- [Requirements](../spec.md#unslop-behavior)
- [Accepted skill](../../../skills/unslop/SKILL.md)
- [Study and every attempt](../../../docs/research/unslop-writing-trials.md)
- [Runner and calibration](../../../docs/agent-evaluations.md#unslop-writing)

Six new cases cover final replies, vague explanations, brevity, successive revisions, clear
writing and necessary terms/exact text. Quality and observed skill access are separate. No
accepted skill prose changed. Corpus: 160 cases. All 298 assessments completed. All eighteen
new-case attempts using our version are correct. The full original 154 run exposed five genuine
failures; the study preserves these, corrected eval defects, earlier unknowns and automated
false passes. No uniform final 160-case pass rate or general writing advantage is claimed.

## Verification and delivery

- `.venv/bin/python -m unittest discover -s tests`: 548 tests pass.
- `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .`: pass.
- `.venv/bin/mypy .`: 95 source files pass strict typing.
- `.venv/bin/python -m evals validate`: 160 cases valid.
- All 59 final calibration labels agree. Installed sources and isolation match all 298 attempts.
- Independent intent and engineering reviews pass with no findings.
- Raw evidence was inspected, reviewed outside Git and deleted before delivery.

No global deployment or real GitHub publication. Next work: address the five genuine failures
listed in the study without treating the older automatic grades as a current failure rate.
