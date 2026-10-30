from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Literal

from evals.assessment import assess
from evals.evidence import EvidenceFrame, EvidenceRun
from evals.fixtures import Workspace
from evals.models import RubricCriterion
from evals.runner import CaseResult, CommandResult, DriverFactory, Observation
from tests.test_eval_runner import FakeDriver


class JudgeExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = [
            RubricCriterion(id="reader", description="Useful reader content.")
        ]
        self.evidence = EvidenceRun("private", "candidate", "condition")
        self.evidence.frames = [
            EvidenceFrame(
                0,
                "main",
                "Write a guide.",
                "Done.",
                {"guide.md": "Useful text"},
                [],
                None,
                {},
            )
        ]
        self.paths: list[Path] = []

    def factory(self, verdict: str, tools: bool = False) -> DriverFactory:
        parent = self

        class Judge(FakeDriver):
            workspace: Workspace

            def message(self, thread: str, prompt: str) -> Observation:
                packet = json.loads(prompt.split("\n\n", 1)[1])
                parent.paths.append(self.workspace.root)
                if tools:
                    (self.workspace.root / "unsafe").write_text("changed")
                    return Observation(
                        "{}",
                        10,
                        command_results=(CommandResult("touch unsafe", 0, ""),),
                    )
                return Observation(
                    json.dumps(
                        {
                            item["label"]: {
                                "reader": {
                                    "verdict": verdict,
                                    "evidence": ["guide.md has the requested content."],
                                }
                            }
                            for item in packet["outputs"]
                        }
                    ),
                    10,
                )

        def make(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> Judge:
            judge = Judge()
            judge.workspace = workspace
            return judge

        return make

    def test_judge_reports_uncertainty_and_cleans_its_environment(self) -> None:
        result = assess(
            self.rubric,
            [self.evidence],
            "judge",
            driver_factory=self.factory("uncertain"),
        )
        self.assertEqual(result[0].status, "inconclusive")
        self.assertFalse(any(path.exists() for path in self.paths))

    def test_judge_cannot_change_evidence(self) -> None:
        result = assess(
            self.rubric,
            [self.evidence],
            "judge",
            driver_factory=self.factory("met", tools=True),
        )
        self.assertEqual(result[0].status, "error")

    def test_judge_cannot_erase_a_failed_code_check(self) -> None:
        from evals.assessment import apply_assessment
        from evals.assessment_models import AssessmentResult

        mechanical = CaseResult("sample", "candidate", status="fail")
        apply_assessment(mechanical, AssessmentResult("pass", "judge"))
        self.assertEqual(mechanical.status, "fail")
        self.assertIsNotNone(mechanical.assessment)
        assert mechanical.assessment is not None
        self.assertEqual(mechanical.assessment.status, "pass")

    def test_prior_errors_and_limits_remain_visible(self) -> None:
        from evals.assessment import apply_assessment
        from evals.assessment_models import AssessmentResult

        statuses: list[Literal["error", "limit"]] = ["error", "limit"]
        for status in statuses:
            result = CaseResult("sample", "candidate")
            result.status = status
            apply_assessment(result, AssessmentResult("pass", "judge"))
            self.assertEqual(result.status, status)
