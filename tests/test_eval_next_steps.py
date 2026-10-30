from __future__ import annotations

import unittest

from evals.models import CaseSpec, load_cases
from evals.runner import CommandResult
from tests.eval_support import observe_case
from tests.test_eval_runner import SOURCE, capture_case


class NextStepCasesTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_stale_validation_requires_a_new_failure_and_successful_repair(
        self,
    ) -> None:
        case = self.case("resume-stale-validation")
        fixed = case.files["src/app.py"]
        red = CommandResult(
            "python3 checks/check_search.py", 1, "AssertionError: Unicode case folding"
        )
        green = CommandResult(
            "python3 checks/check_search.py", 0, "Seven inventory checks passed."
        )
        for changes, results, expected in (
            ({"src/app.py": fixed}, (red, green), "pass"),
            ({"src/app.py": fixed}, (), "fail"),
            ({}, (red, green), "fail"),
            ({"src/app.py": fixed}, (green,), "fail"),
        ):
            with self.subTest(changes=changes, results=results):
                self.assertEqual(
                    observe_case(
                        case, changes, "", command_results=results
                    ).mechanical_status,
                    expected,
                )

    def test_ticket_selection_needs_the_ready_search_and_leaves_export_unimplemented(
        self,
    ) -> None:
        case = self.case("choose-ready-ticket")
        correct = case.files["src/app.py"] + (
            "\n\ndef search_items(items, query):\n"
            "    return [row for row in items "
            'if query.casefold() in row["name"].casefold()]\n'
        )
        result = CommandResult(
            "python3 checks/check_search.py", 0, "Four search checks passed."
        )
        for code, results, expected in (
            (correct, (result,), "pass"),
            (
                correct + "\n\ndef export_matches(items, query): pass\n",
                (result,),
                "fail",
            ),
            (case.files["src/app.py"], (result,), "fail"),
            (correct, (), "fail"),
        ):
            with self.subTest(code=code, results=results):
                self.assertEqual(
                    observe_case(
                        case, {"src/app.py": code}, "", command_results=results
                    ).mechanical_status,
                    expected,
                )

        extra_source = {
            "src/app.py": correct,
            "src/export.py": "def export_matches(items, query): return ''\n",
        }
        self.assertEqual(
            observe_case(
                case, extra_source, "", command_results=(result,)
            ).mechanical_status,
            "fail",
        )

    def test_search_can_update_its_documentation(self) -> None:
        case = self.case("choose-ready-ticket")
        edits = {
            "src/app.py": case.files["src/app.py"]
            + (
                "\n\ndef search_items(items, query):\n"
                "    return [row for row in items "
                'if query.casefold() in row["name"].casefold()]\n'
            ),
            "docs/inventory.md": case.files["docs/inventory.md"]
            + "\nName search ignores case.\n",
        }
        result = CommandResult(
            "python3 checks/check_search.py", 0, "Four search checks passed."
        )
        self.assertEqual(
            observe_case(case, edits, "", command_results=(result,)).mechanical_status,
            "pass",
        )

    def test_unimplemented_export_completion_claim_requires_assessment(self) -> None:
        case = self.case("choose-ready-ticket")
        edits = {
            "src/app.py": case.files["src/app.py"]
            + (
                "\n\ndef search_items(items, query):\n"
                "    return [row for row in items "
                'if query.casefold() in row["name"].casefold()]\n'
            ),
            ".work/inventory/tickets/01-export.md": case.files[
                ".work/inventory/tickets/01-export.md"
            ].replace("ready-for-agent", "done"),
        }
        result = CommandResult(
            "python3 checks/check_search.py", 0, "Four search checks passed."
        )
        outcome, evidence = capture_case(
            case, edits, "Export is complete.", command_results=(result,)
        )
        self.assertEqual(outcome.mechanical_status, "pass")
        self.assertEqual(outcome.status, "inconclusive")
        self.assertEqual(
            evidence.frames[-1].files[".work/inventory/tickets/01-export.md"],
            edits[".work/inventory/tickets/01-export.md"],
        )
        self.assertIn("one-ticket-boundary", {c.id for c in case.rubric})

    def test_requirement_change_blocks_work_and_preserves_finished_search(
        self,
    ) -> None:
        case = self.case("requirements-change-during-implementation")
        reply = "Which second export format should the caller select?"
        changes = {
            ".work/inventory/status.md": (
                "Current state: novel-work planning. "
                "Second export format is undecided.\n"
            ),
            ".work/inventory/spec.md": case.files[".work/inventory/spec.md"].replace(
                "All product and architecture decisions are settled.",
                "The second export format is undecided.",
            )
            + "\nA second export format is required, but not yet chosen.\n",
            ".work/inventory/tickets/02-export.md": (
                "# CSV and additional export\n\n**Status:** blocked\n"
                "**Blocked by:** export format decision\n\n"
                "CSV stays accepted. Additional format design is pending.\n"
            ),
        }
        result, evidence = capture_case(
            case, changes, reply, progress=("planning", None)
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        for path, text in changes.items():
            self.assertEqual(evidence.frames[-1].files[path], text)
        for missing in changes:
            edits = {path: text for path, text in changes.items() if path != missing}
            with self.subTest(missing=missing):
                self.assertEqual(
                    observe_case(
                        case, edits, reply, progress=("planning", None)
                    ).status,
                    "inconclusive",
                )
        conflicting = dict(changes)
        conflicting[".work/inventory/spec.md"] += (
            "\nAll product and architecture decisions are settled.\n"
        )
        self.assertEqual(
            observe_case(case, conflicting, reply, progress=("planning", None)).status,
            "inconclusive",
        )
        for edits, progress in (
            (changes, ("implementation", None)),
            (
                {**changes, "src/new_export.py": "def export_json(items): pass\n"},
                ("planning", None),
            ),
            (
                {
                    **changes,
                    ".work/inventory/tickets/01-search.md": "Search reopened.\n",
                },
                ("planning", None),
            ),
        ):
            with self.subTest(edits=edits, progress=progress):
                self.assertEqual(
                    observe_case(
                        case, edits, reply, progress=progress
                    ).mechanical_status,
                    "fail",
                )


if __name__ == "__main__":
    unittest.main()
