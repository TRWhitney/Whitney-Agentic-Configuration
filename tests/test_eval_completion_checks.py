from __future__ import annotations

import unittest

from evals.models import CaseSpec
from tests.eval_support import observe_case
from tests.test_eval_runner import SOURCE


class CompletionChecksTests(unittest.TestCase):
    def case(self, check: dict[str, object]) -> CaseSpec:
        return CaseSpec.model_validate(
            {
                "id": "completion-check",
                "tags": [],
                "files": {"src/app.py": "def value():\n    return 1\n"},
                "steps": [
                    {"kind": "message", "prompt": "Check it.", "checks": [check]}
                ],
            }
        )

    def test_completed_allows_conversation_commits_without_a_workflow(self) -> None:
        from evals.fixtures import make_workspace
        from evals.runner import Observation, check_result

        case = self.case({"kind": "completed"})
        with make_workspace(SOURCE, case) as workspace:
            workspace.navigate("thread", ["commit", "add", "HEAD"])
            check = case.steps[0].checks[0]
            self.assertTrue(
                check_result(check, Observation(), workspace, "thread", [])[0]
            )

    def test_saved_commit_check_rejects_missing_and_stale_ids(self) -> None:
        from evals.fixtures import git, make_workspace
        from evals.runner import Observation, check_result

        case = self.case({"kind": "session_commits", "include_initial": True})
        with make_workspace(SOURCE, case) as workspace:
            check = case.steps[0].checks[0]

            def passes() -> bool:
                return check_result(check, Observation(), workspace, "thread", [])[0]

            self.assertFalse(passes())
            workspace.navigate("thread", ["commit", "add", "HEAD"])
            self.assertTrue(passes())
            before = workspace.initial_commit
            git(workspace.root, "commit", "--amend", "--allow-empty", "-qm", "Amended")
            self.assertFalse(passes())
            workspace.navigate(
                "thread", ["commit", "add", "HEAD", "--replaces", before]
            )
            self.assertTrue(passes())
            workspace.navigate("other", ["commit", "add", "HEAD"])
            workspace.navigate(
                "thread", ["commit", "remove", git(workspace.root, "rev-parse", "HEAD")]
            )
            self.assertFalse(passes())

    def test_regression_requires_assertion_failure_on_original_and_success_on_repair(
        self,
    ) -> None:
        case = self.case(
            {"kind": "regression_test", "tests": "tests", "source": "src/app.py"}
        )
        for assertion, fixed, expected in (
            ("self.assertEqual(value, 2)", True, "pass"),
            ("self.assertEqual(value, 2)", False, "fail"),
            ("self.assertTrue(True)", True, "fail"),
            ('raise RuntimeError("broken test")', True, "fail"),
        ):
            test = (
                "import runpy\nimport unittest\nfrom pathlib import Path\n"
                "class ValueTests(unittest.TestCase):\n"
                "    def test_value(self):\n"
                '        app = runpy.run_path(str(Path.cwd()/"src/app.py"))\n'
                '        value = app["value"]()\n'
                f"        {assertion}\n"
            )
            edits = {"tests/test_value.py": test}
            if fixed:
                edits["src/app.py"] = "def value():\n    return 2\n"
            with self.subTest(assertion=assertion, fixed=fixed):
                self.assertEqual(observe_case(case, edits, "").status, expected)
        self.assertEqual(observe_case(case, {}, "").status, "fail")

    def test_regression_supports_imports_from_the_project_root(self) -> None:
        case = self.case(
            {"kind": "regression_test", "tests": "tests", "source": "src/app.py"}
        )
        edits = {
            "src/app.py": "def value():\n    return 2\n",
            "tests/test_value.py": (
                "import unittest\nfrom src.app import value\n"
                "class ValueTests(unittest.TestCase):\n"
                "    def test_value(self):\n        self.assertEqual(value(), 2)\n"
            ),
        }
        self.assertEqual(observe_case(case, edits, "").status, "pass")

    def test_completed_requires_no_saved_progress(self) -> None:
        from evals.fixtures import make_workspace
        from evals.runner import Observation, check_result

        case = self.case({"kind": "completed"})
        with make_workspace(SOURCE, case) as workspace:
            self.assertTrue(
                check_result(
                    case.steps[0].checks[0], Observation(), workspace, "one", []
                )[0]
            )
            workspace.progress_path("one").parent.mkdir(parents=True, exist_ok=True)
            workspace.progress_path("one").write_text(
                '{"workflow":"tweak","state":"delivery"}'
            )
            self.assertFalse(
                check_result(
                    case.steps[0].checks[0], Observation(), workspace, "one", []
                )[0]
            )


if __name__ == "__main__":
    unittest.main()
