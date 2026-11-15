"""Exercise operating-document task fixtures and their exact checks without models."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import ClassVar

from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, MessageStep, PythonCheck, UnchangedCheck, load_cases
from evals.runner import Observation, check_result

SOURCE = Path(__file__).resolve().parents[1]


class ProjectOperationsCaseTests(unittest.TestCase):
    cases: ClassVar[dict[str, CaseSpec]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = {
            case.id: case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id.startswith("project-operations-")
        }

    def run_script(
        self, workspace: Workspace, relative: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, relative],
            cwd=workspace.root,
            env=workspace.environment(),
            capture_output=True,
            text=True,
            timeout=10,
        )

    def private_result(self, case: CaseSpec, workspace: Workspace) -> tuple[bool, str]:
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if isinstance(check, PythonCheck)
        )
        return check_result(check, Observation(), workspace, "offline", [])

    @staticmethod
    def filtered_source(source: str, *, inline: bool) -> str:
        """Build two valid implementations through the public CLI."""
        source = source.replace(
            '    commands.add_parser("list")',
            '    listing = commands.add_parser("list")\n'
            '    listing.add_argument("--name")',
        )
        if inline:
            return source.replace(
                "            print(json.dumps(items, ensure_ascii=False))",
                "            print(json.dumps([item for item in items\n"
                "                  if args.name is None or args.name.casefold()\n"
                '                  in item["name"].casefold()], ensure_ascii=False))',
            )
        return source.replace(
            '        if args.action == "list":\n',
            '        if args.action == "list":\n'
            "            if args.name is not None:\n"
            "                query = args.name.casefold()\n"
            "                items = [row for row in items\n"
            '                         if query in row["name"].casefold()]\n',
        )

    def test_cases_are_tasks_and_private_checks_are_not_candidate_files(self) -> None:
        self.assertEqual(len(self.cases), 5)
        for case in self.cases.values():
            with self.subTest(case=case.id):
                self.assertEqual(case.purpose, "task")
                self.assertGreaterEqual(len(case.rubric), 3)
                self.assertLessEqual(len(case.rubric), 6)
                self.assertFalse(case.files.keys() & case.grader_files.keys())
                self.assertIn("data/workshop.json", case.files)
                for name, content in case.files.items():
                    if name.endswith(".py"):
                        compile(content, name, "exec")
                for name, content in case.grader_files.items():
                    compile(content, name, "exec")

    def test_fresh_consumer_has_distinct_conversation_and_real_output(self) -> None:
        case = self.cases["project-operations-author-and-reuse"]
        author, consumer = case.steps
        assert isinstance(author, MessageStep)
        assert isinstance(consumer, MessageStep)
        self.assertNotEqual(author.conversation, consumer.conversation)
        with make_workspace(SOURCE, case) as workspace:
            self.assertFalse(self.private_result(case, workspace)[0])
            original = workspace.file("data/workshop.json").read_bytes()
            workspace.file("out").mkdir()
            for arguments in (
                ["import", "samples/rehearsal.csv"],
                ["list"],
            ):
                result = subprocess.run(
                    [sys.executable, "src", "out/rehearsal.json", *arguments],
                    cwd=workspace.root,
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)[0]["name"], "Bolts, brass")
            self.assertTrue(self.private_result(case, workspace)[0])
            output = workspace.file("out/rehearsal.json")
            output.write_text('[{"name": "Bolts, brass", "quantity": 1}]\n')
            self.assertFalse(self.private_result(case, workspace)[0])
            self.assertEqual(
                workspace.file("data/workshop.json").read_bytes(), original
            )

    def test_stale_command_and_product_regression_are_independent(self) -> None:
        case = self.cases["project-operations-maintain-and-diagnose"]
        correct = self.cases["project-operations-author-and-reuse"].files[
            "src/__main__.py"
        ]
        with make_workspace(SOURCE, case) as workspace:
            stale = subprocess.run(
                [sys.executable, "-m", "inventory", "/unused", "list"],
                cwd=workspace.root,
                capture_output=True,
                text=True,
                timeout=3,
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("No module named inventory", stale.stderr)
            failed = self.run_script(workspace, "checks/check_inventory.py")
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("AssertionError", failed.stderr)
            self.assertFalse(self.private_result(case, workspace)[0])
            workspace.file("src/__main__.py").write_text(correct)
            passed = self.run_script(workspace, "checks/check_inventory.py")
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertTrue(self.private_result(case, workspace)[0])
            self.assertIn(
                "python3 -m inventory", workspace.file("docs/cli.md").read_text()
            )

    def test_contract_rejects_invalid_row_mutation_and_negative_quantity(self) -> None:
        case = self.cases["project-operations-maintain-and-diagnose"]
        correct = self.cases["project-operations-author-and-reuse"].files[
            "src/__main__.py"
        ]
        mutations = {
            "negative-accepted": correct.replace('item["quantity"] < 0', "False"),
            "partial-write-before-rejection": correct.replace(
                '        if any(not item["name"]',
                '        if args.action == "import":\n'
                '            args.inventory.write_text("[]\\n")\n'
                '        if any(not item["name"]',
            ),
        }
        with make_workspace(SOURCE, case) as workspace:
            for name, faulty in mutations.items():
                with self.subTest(mutation=name):
                    self.assertNotEqual(faulty, correct)
                    workspace.file("src/__main__.py").write_text(faulty)
                    passed, detail = self.private_result(case, workspace)
                    self.assertFalse(passed, detail)
                    self.assertIn("AssertionError", detail)

    def test_adequate_guide_commands_preserve_docs_and_user_data(self) -> None:
        case = self.cases["project-operations-adequate-docs"]
        with make_workspace(SOURCE, case) as workspace:
            original = workspace.file("data/workshop.json").read_bytes()
            workspace.file("out").mkdir()
            imported = subprocess.run(
                [
                    sys.executable,
                    "src",
                    "out/rehearsal.json",
                    "import",
                    "samples/rehearsal.csv",
                ],
                cwd=workspace.root,
                capture_output=True,
                text=True,
                timeout=3,
            )
            self.assertEqual(imported.returncode, 0, imported.stderr)
            self.assertTrue(self.private_result(case, workspace)[0])
            self.assertEqual(
                workspace.file("docs/cli.md").read_text(), case.files["docs/cli.md"]
            )
            self.assertEqual(
                workspace.file("data/workshop.json").read_bytes(), original
            )

    def test_missing_supplier_fails_without_inventory_mutation(self) -> None:
        case = self.cases["project-operations-unavailable-prerequisite"]
        with make_workspace(SOURCE, case) as workspace:
            original = workspace.file("data/workshop.json").read_bytes()
            result = subprocess.run(
                [sys.executable, "tools/receive_stock.py", "data/workshop.json"],
                cwd=workspace.root,
                env=workspace.environment(),
                capture_output=True,
                text=True,
                timeout=3,
            )
            self.assertEqual(result.returncode, 69, result.stderr)
            self.assertIn("workshop-supplier-feed is not installed", result.stderr)
            self.assertEqual(
                workspace.file("data/workshop.json").read_bytes(), original
            )
            local = self.run_script(workspace, "checks/check_inventory.py")
            self.assertEqual(local.returncode, 0, local.stderr)

    def test_feature_checks_accept_two_forms_and_reject_missing_feature(self) -> None:
        case = self.cases["project-operations-feature-upkeep"]
        with make_workspace(SOURCE, case) as workspace:
            unsupported = self.run_script(workspace, "checks/check_name_filter.py")
            self.assertNotEqual(unsupported.returncode, 0)
            self.assertIn("unrecognized arguments: --name", unsupported.stderr)
            self.assertFalse(self.private_result(case, workspace)[0])
            for inline in (False, True):
                with self.subTest(inline=inline):
                    correct = self.filtered_source(
                        case.files["src/__main__.py"], inline=inline
                    )
                    workspace.file("src/__main__.py").write_text(correct)
                    for script in (
                        "checks/check_name_filter.py",
                        "checks/check_inventory.py",
                    ):
                        result = self.run_script(workspace, script)
                        self.assertEqual(result.returncode, 0, result.stderr)
                    passed, detail = self.private_result(case, workspace)
                    self.assertTrue(passed, detail)

    def test_feature_grader_rejects_plausible_wrong_filters(self) -> None:
        case = self.cases["project-operations-feature-upkeep"]
        correct = self.filtered_source(case.files["src/__main__.py"], inline=False)
        faulty = {
            "ascii-lower": correct.replace(".casefold()", ".lower()"),
            "exact-only": correct.replace(
                'query in row["name"].casefold()', 'query == row["name"].casefold()'
            ),
            "list-mutates": correct.replace(
                "            print(json.dumps(items, ensure_ascii=False))",
                "            args.inventory.write_text(json.dumps(items))\n"
                "            print(json.dumps(items, ensure_ascii=False))",
            ),
        }
        with make_workspace(SOURCE, case) as workspace:
            for name, source in faulty.items():
                with self.subTest(mutation=name):
                    self.assertNotEqual(source, correct)
                    workspace.file("src/__main__.py").write_text(source)
                    passed, detail = self.private_result(case, workspace)
                    self.assertFalse(passed, detail)
                    self.assertIn("AssertionError", detail)

    def test_feature_upkeep_allows_test_and_contract_updates(self) -> None:
        case = self.cases["project-operations-feature-upkeep"]
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if isinstance(check, UnchangedCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            workspace.file("src/__main__.py").write_text(
                self.filtered_source(case.files["src/__main__.py"], inline=False)
            )
            checks = workspace.file("checks/check_name_filter.py")
            checks.write_text(checks.read_text().replace('("strasse",', '("STRASSE",'))
            contract = workspace.file("docs/inventory-contract.md")
            contract.write_text(
                contract.read_text()
                + "\nThe accepted --name option filters without changing stored data.\n"
            )
            passed, detail = check_result(
                check, Observation(), workspace, "offline", []
            )
            self.assertTrue(passed, detail)
            self.assertTrue(self.private_result(case, workspace)[0])
            workspace.file("data/workshop.json").write_text("[]\n")
            self.assertFalse(
                check_result(check, Observation(), workspace, "offline", [])[0]
            )

    def test_maintenance_allows_preserving_regression_checks(self) -> None:
        case = self.cases["project-operations-maintain-and-diagnose"]
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if isinstance(check, UnchangedCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            checks = workspace.file("checks/check_inventory.py")
            checks.write_text(
                checks.read_text().replace(
                    "    before = inventory.read_bytes()",
                    "    assert json.loads(invoke('list').stdout) == expected\n"
                    "    before = inventory.read_bytes()",
                )
            )
            passed, detail = check_result(
                check, Observation(), workspace, "offline", []
            )
            self.assertTrue(passed, detail)


if __name__ == "__main__":
    unittest.main()
