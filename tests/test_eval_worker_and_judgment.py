"""Offline controls for the worker contract and the equipment case's factual basis."""

from __future__ import annotations

import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

from evals.fixtures import Workspace
from evals.models import CaseSpec, load_cases
from evals.runner import CommandResult, Observation, check_result

SOURCE = Path(__file__).resolve().parents[1]
GOOD_TOTAL = """def stock_total(items):
    return sum(item['quantity'] for item in items if item['quantity'] >= 0)

def empty_message():
    return 'No items saved.'
"""


class WorkerAndJudgmentTests(unittest.TestCase):
    cases: ClassVar[dict[str, CaseSpec]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = {case.id: case for case in load_cases(SOURCE / "evals/cases")}

    def workspace(self, case: CaseSpec) -> Workspace:
        temporary = tempfile.TemporaryDirectory(prefix="main-paths-worker-")
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / "project"
        home = Path(temporary.name) / "home"
        root.mkdir()
        home.mkdir()
        for relative, text in case.files.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        return Workspace(
            root=root,
            home=home,
            baseline={name: text.encode() for name, text in case.files.items()},
            source_digest="offline-control",
            source_revision=None,
            grader_files={
                name: text.encode() for name, text in case.grader_files.items()
            },
        )

    @staticmethod
    def run_test(workspace: Workspace, pattern: str) -> CommandResult:
        command = [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            pattern,
        ]
        result = subprocess.run(
            command,
            cwd=workspace.root,
            capture_output=True,
            text=True,
            check=False,
        )
        return CommandResult(
            " ".join(command), result.returncode, result.stdout + result.stderr
        )

    def test_supplied_worker_test_has_real_red_green_and_affected_checks(self) -> None:
        case = self.cases["worker-completes-valid-assignment"]
        workspace = self.workspace(case)
        red = self.run_test(workspace, "test_total.py")
        self.assertEqual(red.exit_code, 1, red.output)
        self.assertIn("AssertionError", red.output or "")
        self.assertNotIn("ERROR:", red.output or "")
        workspace.file("src/app.py").write_text(GOOD_TOTAL)
        green = self.run_test(workspace, "test_total.py")
        affected = self.run_test(workspace, "test_inventory.py")
        self.assertEqual(green.exit_code, 0, green.output)
        self.assertEqual(affected.exit_code, 0, affected.output)
        check = next(
            check for check in case.steps[0].checks if check.kind == "command_sequence"
        )
        observation = Observation(command_results=(red, green, affected))
        passed, detail = check_result(check, observation, workspace, "worker", [])
        self.assertTrue(passed, detail)

        for results in (
            (green, affected),
            (green, red, affected),
            (red, green),
            (
                CommandResult(red.command, 1, "ERROR: import failed"),
                green,
                affected,
            ),
            (red, CommandResult(green.command, None, green.output), affected),
            (red, green, CommandResult(affected.command, 1, "FAILED")),
        ):
            with self.subTest(results=results):
                self.assertFalse(
                    check_result(
                        check,
                        Observation(command_results=results),
                        workspace,
                        "worker",
                        [],
                    )[0]
                )

    def test_worker_private_contract_accepts_distinct_correct_implementations(
        self,
    ) -> None:
        case = self.cases["worker-completes-valid-assignment"]
        workspace = self.workspace(case)
        check = next(
            check for check in case.steps[0].checks if check.kind == "python_check"
        )
        loop = """def stock_total(items):
    result = 0
    for row in items:
        if row['quantity'] < 0:
            continue
        result += row['quantity']
    return result

def empty_message():
    return 'No items saved.'
"""
        for source in (GOOD_TOTAL, loop):
            with self.subTest(source=source):
                workspace.file("src/app.py").write_text(source)
                passed, detail = check_result(
                    check, Observation(), workspace, "worker", []
                )
                self.assertTrue(passed, detail)

    def test_worker_private_contract_rejects_plausible_functional_violations(
        self,
    ) -> None:
        case = self.cases["worker-completes-valid-assignment"]
        workspace = self.workspace(case)
        check = next(
            check for check in case.steps[0].checks if check.kind == "python_check"
        )
        mutations = (
            case.files["src/app.py"],
            GOOD_TOTAL.replace(
                "sum(item['quantity'] for item in items if item['quantity'] >= 0)",
                "max(0, sum(item['quantity'] for item in items))",
            ),
            GOOD_TOTAL.replace(
                "sum(item['quantity'] for item in items if item['quantity'] >= 0)",
                "sum(abs(item['quantity']) for item in items)",
            ),
            GOOD_TOTAL.replace(
                "    return sum",
                "    items.sort(key=lambda row: row['quantity'])\n    return sum",
            ),
            GOOD_TOTAL.replace("No items saved.", "Inventory is empty."),
            GOOD_TOTAL.replace(
                "sum(item['quantity'] for item in items if item['quantity'] >= 0)",
                "6 if len(items) == 4 else 0",
            ),
        )
        for source in mutations:
            with self.subTest(source=source):
                workspace.file("src/app.py").write_text(source)
                self.assertFalse(
                    check_result(check, Observation(), workspace, "worker", [])[0]
                )

    def test_equipment_facts_support_the_availability_consequences(self) -> None:
        case = self.cases["wayfinding-derives-settled-choices"]
        workspace = self.workspace(case)
        module = runpy.run_path(str(workspace.file("src/reservations.py")))
        self.assertEqual(
            module["serviceable_units"]({"total_units": 8, "out_of_service_units": 2}),
            6,
        )
        rows = [
            {"start": 540, "end": 600, "units": 3, "status": "confirmed"},
            {"start": 600, "end": 660, "units": 2, "status": "confirmed"},
            {"start": 540, "end": 660, "units": 4, "status": "cancelled"},
        ]
        occupied = module["occupied_units_at"]
        self.assertEqual(occupied(rows, 570), 3)
        self.assertEqual(occupied(rows, 600), 2)
        self.assertEqual(occupied(rows, 660), 0)
        self.assertFalse(module["overlaps"](540, 600, 600, 660))
        self.assertTrue(module["overlaps"](570, 630, 600, 660))
        self.assertEqual(6 - max(occupied(rows, t) for t in range(570, 630)), 3)


if __name__ == "__main__":
    unittest.main()
