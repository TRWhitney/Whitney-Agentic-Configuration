"""Valid approaches must satisfy the same behavioral grading contracts."""

from __future__ import annotations

import json
import subprocess
import unittest

from evals.fixtures import make_workspace
from evals.models import CaseSpec, ProgressCheck, load_cases
from evals.runner import CommandResult, Observation, check_result
from tests.test_eval_runner import SOURCE


class GradingEquivalenceTests(unittest.TestCase):
    def cases(self) -> dict[str, CaseSpec]:
        return {case.id: case for case in load_cases(SOURCE / "evals/cases")}

    def test_planning_accepts_either_optional_mode_but_not_implementation(self) -> None:
        for name in (
            "combine-related-planning-records",
            "conflicting-specification-ticket",
            "github-create-timeout",
            "github-planning-edit-persists",
            "review-requires-product-decision",
        ):
            case = self.cases()[name]
            checks = [
                check
                for step in case.steps
                for check in step.checks
                if isinstance(check, ProgressCheck)
            ]
            with self.subTest(case=name), make_workspace(SOURCE, case) as workspace:
                path = workspace.progress_path("thread")
                path.parent.mkdir(parents=True, exist_ok=True)
                for state, substate, expected in (
                    ("planning", None, True),
                    ("planning", "wayfinding", True),
                    ("implementation", None, False),
                ):
                    path.write_text(
                        json.dumps(
                            {
                                "workflow": "novel-work",
                                "state": state,
                                "substate": substate,
                            }
                        )
                    )
                    for check in checks:
                        self.assertEqual(
                            check_result(check, Observation(), workspace, "thread", [])[
                                0
                            ],
                            expected,
                        )

    def test_python_options_do_not_discard_observed_check_results(self) -> None:
        for name in (
            "failed-verification",
            "reproducible-bug",
            "review-finding-rework",
            "unavailable-verification",
        ):
            case = self.cases()[name]
            checks = [
                check
                for step in case.steps
                for check in step.checks
                if check.kind == "command_sequence"
            ]
            for options in ("-I -B", "-X dev -W error -B"):
                with (
                    self.subTest(case=name, options=options),
                    make_workspace(SOURCE, case) as workspace,
                ):
                    search = f"python3 {options} checks/check_search.py"
                    results = (
                        CommandResult(
                            search, 1, "AssertionError: Unicode case folding"
                        ),
                        CommandResult(search, 0, "Seven inventory checks passed."),
                        CommandResult(
                            f"python3 {options} checks/check_release.py",
                            69,
                            "Release verifier unavailable",
                        ),
                    )
                    for check in checks:
                        self.assertTrue(
                            check_result(
                                check,
                                Observation(command_results=results),
                                workspace,
                                "thread",
                                [],
                            )[0]
                        )
                        self.assertFalse(
                            check_result(
                                check,
                                Observation(),
                                workspace,
                                "thread",
                                [],
                            )[0]
                        )

    def test_review_repair_accepts_observed_failure_before_a_following_read(
        self,
    ) -> None:
        case = self.cases()["review-finding-rework"]
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if check.kind == "command_sequence"
        )
        red = CommandResult(
            "python3 checks/check_search.py; cat .work/search/tickets/01-search.md",
            0,
            "Traceback (most recent call last):\n"
            '  File "checks/check_search.py", line 16, in <module>\n'
            '    assert search(street, "STRASSE") == street, "Unicode case folding"\n'
            "AssertionError: Unicode case folding\n# Name search\n",
        )
        green = CommandResult(
            "python3 checks/check_search.py", 0, "Seven inventory checks passed."
        )
        with make_workspace(SOURCE, case) as workspace:
            for results, expected in (
                ((red, green), True),
                ((green,), False),
                ((green, red), False),
                ((red,), False),
                ((CommandResult(red.command, 0, "Name search"), green), False),
                ((red, CommandResult(green.command, 1, "Failed again")), False),
            ):
                with self.subTest(results=results):
                    self.assertEqual(
                        check_result(
                            check,
                            Observation(command_results=results),
                            workspace,
                            "thread",
                            [],
                        )[0],
                        expected,
                    )

    def test_parser_reuse_allows_trimming_but_requires_its_returned_value(self) -> None:
        case = self.cases()["reuse-existing-quantity-parser"]
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if check.kind == "python_check"
        )
        source = (
            "import csv, io\n"
            "from .quantities import parse_quantity\n\n"
            "def import_items(text):\n"
            "    return [{'name': row['name'], 'quantity': VALUE}\n"
            "            for row in csv.DictReader(io.StringIO(text))]\n"
        )
        for value, expected in (
            ("parse_quantity(row['quantity'])", True),
            ("parse_quantity(row['quantity'].strip())", True),
            ("(parse_quantity(row['quantity']), int(row['quantity']))[1]", False),
        ):
            with self.subTest(value=value), make_workspace(SOURCE, case) as workspace:
                workspace.file("src/importer.py").write_text(
                    source.replace("VALUE", value)
                )
                self.assertEqual(
                    check_result(check, Observation(), workspace, "thread", [])[0],
                    expected,
                )

    def test_amendment_fixture_establishes_its_test_framework(self) -> None:
        case = self.cases()["amend-preserves-earlier-edit"]
        with make_workspace(SOURCE, case) as workspace:
            tests = workspace.root / "tests"
            self.assertTrue(tests.is_dir(), "No project test convention is supplied.")
            result = subprocess.run(
                ["python3", "-B", "-m", "unittest", "discover", "-s", "tests"],
                cwd=workspace.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Ran 2 tests", result.stderr)
            app = workspace.file("src/app.py")
            app.write_text(
                app.read_text().replace(
                    'sum(item["quantity"] for item in items)',
                    'sum(max(0, item["quantity"]) for item in items)',
                )
            )
            checks = [
                check
                for step in case.steps
                for check in step.checks
                if check.kind == "regression_test"
            ]
            self.assertFalse(
                check_result(checks[0], Observation(), workspace, "thread", [])[0],
                "The supplied positive-only tests cannot establish the repair.",
            )
            (tests / "test_negative.py").write_text(
                "import unittest, runpy\nfrom pathlib import Path\n"
                "class NegativeTests(unittest.TestCase):\n"
                "    def test_negative_quantity(self):\n"
                "        app=runpy.run_path(str(Path(__file__).resolve().parents[1]"
                "/'src/app.py'))\n"
                "        self.assertEqual(app['stock_total']"
                "([{'quantity':-3},{'quantity':5}]),5)\n"
            )
            self.assertTrue(
                check_result(checks[0], Observation(), workspace, "thread", [])[0]
            )
            contracts = [
                check
                for step in case.steps
                for check in step.checks
                if check.kind == "python_check"
                and check.path
                in {"checks/check_result.py", "checks/check_second_amendment.py"}
            ]
            self.assertTrue(
                check_result(contracts[0], Observation(), workspace, "thread", [])[0]
            )
            for step in case.steps:
                if step.kind == "edit":
                    for relative, content in step.files.items():
                        workspace.file(relative).write_text(content)
            self.assertTrue(
                check_result(contracts[1], Observation(), workspace, "thread", [])[0]
            )
            self.assertTrue(
                check_result(checks[1], Observation(), workspace, "thread", [])[0]
            )


if __name__ == "__main__":
    unittest.main()
