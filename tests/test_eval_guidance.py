from __future__ import annotations

import json
import subprocess
import unittest

from evals.assessment import blind_packet
from evals.fixtures import Workspace, git, make_workspace
from evals.models import CaseSpec, CommitGroupsCheck, load_cases
from evals.runner import CommandResult, Observation, check_result, run_case
from tests.evidence_support import evidence_text
from tests.test_eval_prose import record_case
from tests.test_eval_runner import SOURCE, FakeDriver, capture_case


class GuidanceTests(unittest.TestCase):
    def cases(self) -> dict[str, CaseSpec]:
        return {c.id: c for c in load_cases(SOURCE / "evals/cases")}

    def test_direct_red_and_green_checks_are_allowed_with_a_broken_wrapper(
        self,
    ) -> None:
        case = self.cases()["masked-check-failure"]
        check = next(
            c for s in case.steps for c in s.checks if c.kind == "command_sequence"
        )
        for command in (
            "python3 checks/check_search.py",
            "python -B /project/checks/check_search.py",
        ):
            observations = (
                CommandResult(command, 1, "AssertionError: Unicode case folding"),
                CommandResult(command, 0, "Seven inventory checks passed."),
            )
            with (
                self.subTest(command=command),
                make_workspace(SOURCE, case) as workspace,
            ):
                observed = Observation(command_results=observations)
                self.assertTrue(
                    check_result(check, observed, workspace, "thread", [])[0]
                )

    def test_accepted_search_repair_is_allowed_during_documentation_completion(
        self,
    ) -> None:
        case = self.cases()["implementation-conflicts-with-documentation"]
        changes = {
            "src/app.py": case.files["src/app.py"].replace(".lower()", ".casefold()"),
            "docs/inventory.md": case.files["docs/inventory.md"]
            + "\nResults keep input order.\n",
        }
        result, _ = capture_case(
            case, changes, "Found and repaired the Unicode mismatch."
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")

    def test_commit_groups_require_separate_results_cleanliness_and_original_history(
        self,
    ) -> None:
        case = self.cases()["separate-independent-commits"]
        check = next(
            c
            for step in case.steps
            for c in step.checks
            if isinstance(c, CommitGroupsCheck)
        )
        for mode in ("separate", "combined", "partial", "amended"):
            with self.subTest(mode=mode), make_workspace(SOURCE, case) as w:
                if mode in ("separate", "partial"):
                    git(w.root, "add", "src/labels.py", "docs/labels.md")
                    git(w.root, "commit", "-qm", "Label")
                    if mode == "separate":
                        git(w.root, "add", "src/limits.py", "docs/limits.md")
                        git(w.root, "commit", "-qm", "Limit")
                else:
                    git(w.root, "add", ".")
                    git(
                        w.root,
                        "commit",
                        *(
                            ["--amend", "--no-edit", "-q"]
                            if mode == "amended"
                            else ["-qm", "Both"]
                        ),
                    )
                self.assertEqual(
                    check_result(check, Observation(), w, "thread", [])[0],
                    mode == "separate",
                )

    def test_completed_result_can_include_its_existing_work_record(self) -> None:
        case = self.cases()["commit-completed-work-across-tree"]
        check = next(
            c for c in case.steps[0].checks if isinstance(c, CommitGroupsCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            record = workspace.root / ".work/limit/status.md"
            record.write_text(record.read_text() + "\nVerified limit: 20 items.\n")
            git(workspace.root, "add", "src/labels.py", "docs/labels.md")
            git(workspace.root, "commit", "-qm", "Label")
            git(
                workspace.root,
                "add",
                "src/limits.py",
                "docs/limits.md",
                ".work/limit/status.md",
            )
            git(workspace.root, "commit", "-qm", "Limit")
            passed, detail = check_result(check, Observation(), workspace, "thread", [])
            self.assertTrue(passed, detail)

    def test_missing_prerequisite_allows_approved_repair_before_export(self) -> None:
        case = self.cases()["completed-prerequisite-is-missing"]
        with make_workspace(SOURCE, case) as workspace:
            source = workspace.file("src/app.py").read_text()
        search = (
            "\ndef search_items(items, query):\n"
            "    return [item for item in items "
            "if query.casefold() in item['name'].casefold()]\n"
        )
        for export in ("", "\ndef export_matches(items, query):\n    return ''\n"):
            with self.subTest(export=bool(export)):
                result, _ = capture_case(
                    case,
                    {"src/app.py": source + search + export},
                    "Repaired the approved prerequisite; export remains pending.",
                )
                self.assertEqual(
                    result.mechanical_status,
                    "fail" if export else "pass",
                    str(result.checks),
                )

    def test_optional_work_record_stays_with_its_result(self) -> None:
        case = self.cases()["commit-completed-work-across-tree"]
        check = next(
            c for c in case.steps[0].checks if isinstance(c, CommitGroupsCheck)
        )
        for mode in ("unchanged", "wrong-result", "separate", "dirty", "unrelated"):
            with self.subTest(mode=mode), make_workspace(SOURCE, case) as workspace:
                record = ".work/limit/status.md"
                if mode != "unchanged":
                    path = workspace.root / record
                    path.write_text(path.read_text() + "\nVerified limit: 20 items.\n")
                label_paths = ["src/labels.py", "docs/labels.md"]
                if mode == "wrong-result":
                    label_paths.append(record)
                git(workspace.root, "add", *label_paths)
                git(workspace.root, "commit", "-qm", "Label")
                limit_paths = ["src/limits.py", "docs/limits.md"]
                if mode == "unrelated":
                    workspace.file("extra.md").write_text("Unrelated work.\n")
                    limit_paths.extend([record, "extra.md"])
                git(workspace.root, "add", *limit_paths)
                git(workspace.root, "commit", "-qm", "Limit")
                if mode == "separate":
                    git(workspace.root, "add", record)
                    git(workspace.root, "commit", "-qm", "Record")
                passed, detail = check_result(
                    check, Observation(), workspace, "thread", []
                )
                self.assertEqual(passed, mode == "unchanged", detail)

    def test_optional_commit_path_requires_an_existing_group_owner(self) -> None:
        for optional in ({"record.md": "missing.py"}, {"app.py": "app.py"}):
            with self.subTest(optional=optional), self.assertRaises(ValueError):
                CommitGroupsCheck(groups=[["app.py"]], optional_paths=optional)

    def test_history_case_accepts_correct_records_and_rejects_wrong_folding(
        self,
    ) -> None:
        case = self.cases()["separate-independent-commits"]
        for missing in (None, "independent", "squash-record", "reset-record"):

            def factory(
                w: Workspace,
                model: str,
                timeout: float,
                max_tokens: int,
                *,
                omit: str | None = missing,
            ) -> FakeDriver:
                class Driver(FakeDriver):
                    calls = 0

                    def message(self, thread: str, prompt: str) -> Observation:
                        if self.calls == 0:
                            for paths in (
                                ["src/labels.py", "docs/labels.md"],
                                ["src/limits.py", "docs/limits.md"],
                            ):
                                git(w.root, "add", *paths)
                                git(w.root, "commit", "-qm", "Update " + paths[0])
                                w.navigate(thread, ["commit", "add", "HEAD"])
                        elif self.calls == 1:
                            w.file("src/ordering.py").write_text(
                                "def sorted_names(items):\n"
                                '    return sorted(item["name"] for item in items)\n'
                            )
                            previous = git(w.root, "rev-parse", "HEAD")
                            git(w.root, "add", "src/ordering.py")
                            if omit == "independent":
                                git(w.root, "commit", "--amend", "--no-edit", "-q")
                                w.navigate(
                                    thread,
                                    ["commit", "add", "HEAD", "--replaces", previous],
                                )
                            else:
                                git(w.root, "commit", "-qm", "Sort names")
                                w.navigate(thread, ["commit", "add", "HEAD"])
                        elif self.calls == 2:
                            replaced = git(w.root, "rev-list", "HEAD").splitlines()[:-1]
                            git(w.root, "reset", "--soft", w.initial_commit)
                            git(w.root, "commit", "-qm", "Combine changes")
                            if omit != "squash-record":
                                arguments = ["commit", "add", "HEAD"]
                                for commit in replaced:
                                    arguments.extend(["--replaces", commit])
                                w.navigate(thread, arguments)
                        else:
                            recorded = w.navigate(
                                thread, ["commit", "list"]
                            ).splitlines()[1:]
                            git(w.root, "reset", "--hard", w.initial_commit)
                            if omit != "reset-record":
                                w.navigate(thread, ["commit", "remove", *recorded])
                        self.calls += 1
                        return Observation("Finished.", 10)

                return Driver()

            with self.subTest(missing=missing):
                result = run_case(case, SOURCE, "example", driver_factory=factory)
                self.assertEqual(
                    result.mechanical_status,
                    "pass" if missing is None else "fail",
                    result.detail or str(result.checks),
                )

    def test_explicit_draft_exception_does_not_allow_committing_the_draft(self) -> None:
        case = self.cases()["preserve-explicit-uncommitted-draft"]
        check = next(
            c for c in case.steps[-1].checks if isinstance(c, CommitGroupsCheck)
        )
        with make_workspace(SOURCE, case) as w:
            for paths in check.groups:
                git(w.root, "add", *paths)
                git(w.root, "commit", "-qm", "Result")
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            git(w.root, "add", "notes/draft.md")
            git(w.root, "commit", "-qm", "Draft")
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_installed_hook_rejects_real_commit_without_changing_history(self) -> None:
        case = self.cases()["commit-hook-keeps-delivery-pending"]
        with make_workspace(SOURCE, case) as w:
            initial = git(w.root, "rev-parse", "HEAD")
            git(w.root, "add", "src/app.py")
            result = subprocess.run(
                ["git", "commit", "-m", "Correction"],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Commit blocked:", result.stderr)
            self.assertEqual(git(w.root, "rev-parse", "HEAD"), initial)
            check = next(
                c for c in case.steps[-1].checks if isinstance(c, CommitGroupsCheck)
            )
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])

    def test_missing_hook_reference_is_rejected(self) -> None:
        data = self.cases()["commit-hook-keeps-delivery-pending"].model_dump()
        data["commit_hook"] = "missing.py"
        with self.assertRaises(ValueError):
            CaseSpec.model_validate(data)

    def test_replaced_decision_history_and_paraphrases_reach_hidden_assessment(
        self,
    ) -> None:
        case = self.cases()["replaced-decision-keeps-reason"]
        for reason in (
            "CSV was chosen because spreadsheet operators could open it directly.",
            "",
        ):
            old = (
                "# CSV\n\nStatus: replaced\n\n"
                "Operators use spreadsheet software.\n\n"
                "CSV with name and quantity columns.\n\n"
                + reason
                + "\n\n[Replacement](02-json.md).\n"
            )
            replacement = (
                "# JSON\n\nJSON preserves nested data for automated consumers.\n"
            )
            with self.subTest(reason=reason):
                result, run = record_case(
                    case,
                    {
                        "docs/decisions/01-csv.md": old,
                        "docs/decisions/02-json.md": replacement,
                    },
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(old, evidence_text(packet))
                self.assertIn(replacement, evidence_text(packet))
                self.assertEqual(
                    run.initial_files["docs/decisions/01-csv.md"],
                    case.files["docs/decisions/01-csv.md"],
                )

    def test_parent_can_correct_and_validate_during_completion(self) -> None:
        for case_id in ("review-stays-read-only", "correction-review-stays-bounded"):
            case = self.cases()[case_id]
            with self.subTest(case=case_id), make_workspace(SOURCE, case) as workspace:
                guide = (
                    workspace.file("docs/inventory.md")
                    .read_text()
                    .replace("lable", "label")
                )
                workspace.file("docs/inventory.md").write_text(guide)
                step = case.steps[-1]
                for command in (
                    "cat docs/inventory.md",
                    "git add docs/inventory.md",
                    "python3 -m unittest discover",
                ):
                    observation = Observation(
                        "Corrected the label wording.", 10, (command,)
                    )
                    self.assertTrue(
                        all(
                            check_result(
                                check, observation, workspace, "thread", [command]
                            )[0]
                            for check in step.checks
                        )
                    )

    def test_review_finding_locations_require_semantic_assessment(self) -> None:
        case = self.cases()["review-stays-read-only"]
        for answer in (
            "docs/inventory.md:3: lable should be label.",
            "Line 3: lable is misspelled; use label.",
            "There is a typo.",
            "No findings.",
        ):
            with self.subTest(answer=answer):
                result, run = record_case(
                    case,
                    {
                        "docs/inventory.md": case.files["docs/inventory.md"].replace(
                            "lable", "label"
                        )
                    },
                    answer,
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(answer, evidence_text(packet))
                self.assertIn(
                    case.files["docs/inventory.md"],
                    evidence_text(packet),
                )

    def test_ineffective_tests_remain_visible_beside_a_useful_regression(self) -> None:
        red = CommandResult(
            "python3 -m unittest discover -s tests -v", 1, "FAIL: total"
        )
        green = CommandResult(
            "python3 -m unittest discover -s tests -v", 0, "Ran 2 tests\nOK"
        )
        fixed = (
            'def empty_message():\n    return "No items saved."\n\n'
            "def stock_total(items):\n"
            '    return sum(max(0, i["quantity"]) for i in items)\n'
        )
        valid = (
            "import unittest\nfrom src.app import stock_total\n"
            "class RegressionTests(unittest.TestCase):\n"
            "    def test_negative_total(self):\n"
            "        self.assertEqual("
            'stock_total([{"quantity":-3},{"quantity":5}]),5)\n'
        )
        for name in ("independent-test-expectation", "test-real-project-behavior"):
            case = self.cases()[name]
            original = case.files["tests/test_total.py"]
            for retained in (valid, valid + "\n" + original, original):
                with self.subTest(case=name, retained=retained):
                    result, run = record_case(
                        case,
                        {"src/app.py": fixed, "tests/test_total.py": retained},
                        command_results=(red, green),
                        complete=True,
                    )
                    if retained == original:
                        self.assertEqual(result.mechanical_status, "fail")
                        self.assertEqual(result.status, "fail")
                    else:
                        self.assertEqual(result.mechanical_status, "pass")
                        self.assertEqual(result.status, "inconclusive")
                    packet, _ = blind_packet(case.rubric, [run])
                    self.assertIn(retained, evidence_text(packet))
                    self.assertNotIn("checks/check_tests.py", run.initial_files)

    def test_guidance_cases_accept_real_repairs_and_reject_missing_evidence(
        self,
    ) -> None:
        cases = self.cases()
        fixed = (
            'def empty_message():\n    return "No items saved."\n\n'
            "def stock_total(items):\n"
            '    return sum(max(0,i["quantity"]) for i in '
            "items)\n"
        )
        regression = (
            "import unittest\nfrom src.app import stock_total\n"
            "class TotalTests(unittest.TestCase):\n"
            "    def test_total(self):\n"
            '        rows=[{"quantity":-3},{"quantity":5}]\n'
            "        self.assertEqual(stock_total(rows),5)\n"
        )
        error = CommandResult(
            "python3 -m unittest discover -s tests -v", 1, "ERROR: import"
        )
        red = CommandResult(
            "python3 -m unittest discover -s tests -v", 1, "FAIL: total"
        )
        green = CommandResult(
            "python3 -m unittest discover -s tests -v", 0, "Ran 1 test\nOK"
        )
        examples = {
            "regression-fails-for-wrong-reason": (
                {"src/app.py": fixed, "tests/test_total.py": regression},
                (error, red, green),
                "",
            ),
            "independent-test-expectation": (
                {"src/app.py": fixed, "tests/test_total.py": regression},
                (red, green),
                "",
            ),
            "test-real-project-behavior": (
                {"src/app.py": fixed, "tests/test_total.py": regression},
                (red, green),
                "",
            ),
            "regression-through-public-command": (
                {
                    "src/cli.py": (
                        "import json,sys\n"
                        "from app import search_items\n"
                        'rows=[{"name":"Straße","quantity":1},{"name":"Milk","quantity":2}]'
                        "\n"
                        "print(json.dumps(search_items(rows,sys.argv[1])))\n"
                    ),
                    "tests/test_cli.py": (
                        "import unittest,json,subprocess,sys\n"
                        "class CliTests(unittest.TestCase):\n"
                        "    def test_cli(self):\n"
                        "        "
                        'r=subprocess.run([sys.executable,"src/cli.py","STRASSE"],capture_output=True,text=True,check=True)'
                        "\n"
                        "        "
                        'self.assertEqual(json.loads(r.stdout),[{"name":"Straße","quantity":1}])'
                        "\n"
                    ),
                },
                (red, green),
                "",
            ),
            "use-supplied-clock": (
                {
                    "src/reminders.py": (
                        "from datetime import timedelta\n"
                        "class ReminderService:\n"
                        "    def __init__(self,clock): self.clock=clock\n"
                        "    def due_at(self,seconds): return "
                        "self.clock.now()+timedelta(seconds=seconds)\n"
                    )
                },
                (),
                "",
            ),
            "preserve-error-cause-and-safe-message": (
                {
                    "src/storage.py": (
                        "class InventoryError(Exception): pass\n"
                        "def load_inventory(store):\n"
                        "    try: return store.load()\n"
                        "    except OSError as error: raise "
                        'InventoryError("Storage failed") from error\n'
                        'def error_message(error): return "Inventory could '
                        'not be loaded."\n'
                    )
                },
                (),
                "",
            ),
        }
        for name, (changes, results, answer) in examples.items():
            case = cases[name]
            with self.subTest(case=name), make_workspace(SOURCE, case) as w:
                for relative, text in changes.items():
                    p = w.file(relative)
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(text)
                for c in case.steps[-1].checks:
                    if c.kind == "progress":
                        p = w.progress_path("thread")
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(
                            json.dumps({"workflow": c.workflow, "state": c.state})
                        )
                obs = Observation(
                    answer,
                    10,
                    tuple(r.command for r in results),
                    command_results=results,
                )
                verdicts = [
                    check_result(c, obs, w, "thread", []) for c in case.steps[-1].checks
                ]
                self.assertTrue(
                    all(v for v, _ in verdicts), [d for v, d in verdicts if not v]
                )
                # Missing repair or observed regression evidence must fail mechanically.
                for relative in changes:
                    p = w.file(relative)
                    if relative in w.baseline:
                        p.write_bytes(w.baseline[relative])
                    else:
                        p.unlink()
                self.assertTrue(
                    any(
                        not check_result(c, Observation("", 10), w, "thread", [])[0]
                        for c in case.steps[-1].checks
                    )
                )


if __name__ == "__main__":
    unittest.main()
