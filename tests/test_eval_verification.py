from __future__ import annotations

import subprocess
import unittest
from functools import partial
from unittest.mock import patch

from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, CommandSequenceCheck
from evals.runner import CommandResult, Observation, check_result, run_case
from tests import test_eval_runner as runner_tests
from tests.test_eval_runner import SOURCE, FakeDriver


class VerificationChecksTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = runner_tests.EvaluationRunnerTests()

    def test_command_results_require_real_exit_codes_output_and_order(self) -> None:
        case = self.runner.case(
            [
                {
                    "kind": "command_sequence",
                    "commands": [
                        {
                            "pattern": "check.py",
                            "exit_code": 1,
                            "output_pattern": "FAIL",
                        },
                        {
                            "pattern": "check.py",
                            "exit_code": 0,
                            "output_pattern": "PASS",
                        },
                    ],
                }
            ]
        )
        red = CommandResult("python check.py", 1, "FAIL")
        green = CommandResult("python check.py", 0, "PASS")
        for results, expected in (
            ((red, green), "pass"),
            ((red, CommandResult("inspect", 0, ""), green), "pass"),
            ((green, red), "fail"),
            ((green,), "fail"),
            ((red,), "fail"),
            ((CommandResult("python check.py", None, "FAIL"), green), "fail"),
            ((CommandResult("python check.py", 1, None), green), "fail"),
        ):
            with self.subTest(results=results):

                class Driver(FakeDriver):
                    def __init__(self, results: tuple[CommandResult, ...]) -> None:
                        super().__init__()
                        self.results = results

                    def message(self, thread: str, prompt: str) -> Observation:
                        return Observation(
                            "Tests passed.",
                            10,
                            ("python check.py",),
                            command_results=self.results,
                        )

                self.assertEqual(
                    self.runner.run_with(case, Driver(results)).status, expected
                )
        self.assertEqual(
            self.runner.run_with(case, FakeDriver("Tests passed.")).status, "fail"
        )

    def test_command_sequence_cannot_reuse_one_result_or_an_earlier_step(self) -> None:
        command = {"pattern": "check.py", "exit_code": 0}
        case = self.runner.case(
            [{"kind": "command_sequence", "commands": [command, command]}]
        )

        class Driver(FakeDriver):
            calls = 0

            def message(self, thread: str, prompt: str) -> Observation:
                self.calls += 1
                return Observation(
                    "Ready.",
                    10,
                    command_results=(CommandResult("python check.py", 0, ""),)
                    if self.calls == 1
                    else (),
                )

        self.assertEqual(self.runner.run_with(case, Driver()).status, "fail")
        check = case.steps[0].checks[0]
        assert isinstance(check, CommandSequenceCheck)
        check.commands.pop()
        case.steps.append(case.steps[0].model_copy())
        result = self.runner.run_with(case, Driver())
        self.assertEqual([check.passed for check in result.checks], [True, False])

    def test_python_check_uses_original_script_and_current_production_code(
        self,
    ) -> None:
        raw = self.runner.case([]).model_dump()
        raw["files"]["checks/check.py"] = (
            "from pathlib import Path\nimport runpy\n"
            "assert runpy.run_path(str(Path.cwd() / 'src/app.py'))['value'] == 2\n"
        )
        raw["steps"][0]["checks"] = [
            {"kind": "python_check", "path": "checks/check.py"}
        ]
        case = CaseSpec.model_validate(raw)

        class Driver(FakeDriver):
            def __init__(self, workspace: Workspace, *, fixed: bool) -> None:
                super().__init__()
                self.workspace = workspace
                self.fixed = fixed

            def message(self, thread: str, prompt: str) -> Observation:
                self.workspace.file("checks/check.py").write_text("print('PASS')\n")
                if self.fixed:
                    self.workspace.file("src/app.py").write_text("value = 2\n")
                return Observation("Tests passed.", 10)

        def factory(
            workspace: Workspace,
            model: str,
            timeout: float,
            max_tokens: int,
            *,
            fixed: bool,
        ) -> FakeDriver:
            return Driver(workspace, fixed=fixed)

        for fixed, expected in ((False, "fail"), (True, "pass")):
            with self.subTest(fixed=fixed):
                result = run_case(
                    case,
                    SOURCE,
                    "example-model",
                    driver_factory=partial(factory, fixed=fixed),
                )
                self.assertEqual(result.status, expected)

    def test_python_check_timeout_is_a_failure(self) -> None:
        raw = self.runner.case([]).model_dump()
        raw["files"]["check.py"] = "pass\n"
        raw["steps"][0]["checks"] = [{"kind": "python_check", "path": "check.py"}]
        case = CaseSpec.model_validate(raw)
        with (
            make_workspace(SOURCE, case) as workspace,
            patch(
                "evals.runner.subprocess.run",
                side_effect=subprocess.TimeoutExpired("python", 10),
            ),
        ):
            passed, detail = check_result(
                case.steps[0].checks[0],
                Observation(),
                workspace,
                "one",
                [],
            )
        self.assertFalse(passed)
        self.assertIn("timed out", detail)


if __name__ == "__main__":
    unittest.main()
