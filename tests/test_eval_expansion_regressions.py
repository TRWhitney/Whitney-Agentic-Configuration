from __future__ import annotations

import json
import unittest

from evals.fixtures import make_workspace
from evals.models import (
    CaseSpec,
    CommandSequenceCheck,
    ProgressCheck,
    PythonCheck,
    load_cases,
)
from evals.runner import CommandResult, Observation, check_result
from tests.test_eval_runner import SOURCE, capture_case


class ExpansionRegressionTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_map_check_follows_the_saved_link_and_rejects_a_missing_map(self) -> None:
        case = self.case("start-wayfinding-from-conversation")
        check = next(c for c in case.steps[1].checks if isinstance(c, PythonCheck))
        with make_workspace(SOURCE, case) as w:
            w.file(".work/export/status.md").write_text(
                "[Map](../../docs/planning/chosen-name/map.md).\n"
            )
            path = w.file("docs/planning/chosen-name/map.md")
            path.parent.mkdir(parents=True)
            path.write_text(
                "CSV uses name and quantity. Empty inventory and "
                "existing destination are open.\n"
            )
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            path.unlink()
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_optional_wayfinding_is_allowed_without_ignoring_the_workflow_state(
        self,
    ) -> None:
        case = self.case("conversations-share-current-document")
        check = ProgressCheck(
            workflow="novel-work", state="planning", ignore_substate=True
        )
        with make_workspace(SOURCE, case) as w:
            path = w.progress_path("thread")
            path.parent.mkdir(parents=True)
            path.write_text(
                '{"workflow":"novel-work","state":"planning","substate":"wayfinding"}'
            )
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            strict = check.model_copy(update={"ignore_substate": False})
            self.assertFalse(check_result(strict, Observation(), w, "thread", [])[0])
            wrong = check.model_copy(update={"state": "implementation"})
            self.assertFalse(check_result(wrong, Observation(), w, "thread", [])[0])

    def test_progress_alternatives_preserve_record_and_substate_requirements(
        self,
    ) -> None:
        case = self.case("diagnosis-needs-design")
        check = ProgressCheck.model_validate(
            {
                "workflow": "fix",
                "state": "discovery",
                "alternatives": [{"workflow": "novel-work", "state": "planning"}],
                "record": ".work/totals/status.md",
            }
        )
        with make_workspace(SOURCE, case) as workspace:
            path = workspace.progress_path("thread")
            path.parent.mkdir(parents=True, exist_ok=True)
            record = str(workspace.file(".work/totals/status.md"))
            for workflow, state, substate, saved_record, expected in (
                ("fix", "discovery", None, record, True),
                ("novel-work", "planning", None, record, True),
                ("novel-work", "implementation", None, record, False),
                ("fix", "planning", None, record, False),
                ("novel-work", "planning", "wayfinding", record, False),
                ("novel-work", "planning", None, "/project/other.md", False),
            ):
                with self.subTest(workflow=workflow, state=state, record=saved_record):
                    path.write_text(
                        json.dumps(
                            {
                                "workflow": workflow,
                                "state": state,
                                "substate": substate,
                                "record": saved_record,
                            }
                        )
                    )
                    passed, detail = check_result(
                        check, Observation(), workspace, "thread", []
                    )
                    self.assertEqual(passed, expected)
                    self.assertIn(f"{workflow}.{state}", detail)
            path.unlink()
            self.assertFalse(
                check_result(check, Observation(), workspace, "thread", [])[0]
            )

    def test_service_error_output_can_be_checked_inside_a_successful_shell_call(
        self,
    ) -> None:
        case = self.case("github-planning-read-failure")
        check = next(
            c for c in case.steps[-1].checks if isinstance(c, CommandSequenceCheck)
        )
        with make_workspace(SOURCE, case) as w:
            command = "gh issue view 10; cat docs/inventory.md"
            for code, output, expected in (
                (0, "temporary read failure", True),
                (1, "temporary read failure", True),
                (0, "Successful read", False),
            ):
                observation = Observation(
                    command_results=(CommandResult(command, code, output),)
                )
                self.assertEqual(
                    check_result(check, observation, w, "thread", [])[0], expected
                )

    def test_search_failure_remains_observable_in_compound_shell(self) -> None:
        case = self.case("reproducible-bug")
        check = next(
            c for c in case.steps[-1].checks if isinstance(c, CommandSequenceCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            for initial_code, output, expected in (
                (0, "AssertionError: Unicode case folding", True),
                (1, "AssertionError: Unicode case folding", True),
                (0, "No failure", False),
                (1, "ModuleNotFoundError", False),
            ):
                results = (
                    CommandResult(
                        "python3 checks/check_search.py; echo done",
                        initial_code,
                        output,
                    ),
                    CommandResult("python3 checks/check_search.py", 0, "Checks passed"),
                )
                with self.subTest(initial_code=initial_code, output=output):
                    observation = Observation(command_results=results)
                    self.assertEqual(
                        check_result(check, observation, workspace, "thread", [])[0],
                        expected,
                    )

    def test_cycle_explanations_are_preserved_for_hidden_assessment(self) -> None:
        case = self.case("cyclic-ticket-dependencies")
        for answer in (
            "Search and export block each other; "
            "neither can create the snapshot first.",
            "Search is ready; export follows.",
        ):
            with self.subTest(answer=answer):
                result, evidence = capture_case(case, {}, answer)
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertEqual(evidence.frames[-1].reply, answer)
                self.assertIn("explain-cycle", {c.id for c in case.rubric})
                self.assertIn(
                    "Neither snapshot creation",
                    evidence.initial_files[".work/inventory/spec.md"],
                )

    def test_wayfinding_acknowledgement_needs_semantic_assessment(
        self,
    ) -> None:
        examples = (
            (
                "wayfinding-multiple-answers",
                "Planning: 3 decided, 1 ready, unspecified: zero-quantity inclusion.\n",
                "Should export include zero-quantity items?",
                "Please choose whether zero-quantity items are included.",
                "Zero-quantity inclusion remains open. Planning remains active.",
            ),
            (
                "wayfinding-partial-answer",
                "Planning: 2 decided, 2 ready, "
                "unspecified: headings and existing file.\n",
                "Should the CSV contain column headings?",
                "Please choose whether to include column headings.",
                "Column headings remain undecided. Planning remains active.",
            ),
        )
        for name, line, question, request, acknowledgement in examples:
            case = self.case(name)
            for answer in (question, request, acknowledgement):
                with self.subTest(case=name, answer=answer):
                    result, evidence = capture_case(case, {}, line + answer)
                    self.assertEqual(result.mechanical_status, "pass")
                    self.assertEqual(result.status, "inconclusive")
                    self.assertEqual(evidence.frames[-1].reply, line + answer)
                    self.assertTrue(
                        any("question" in c.description for c in case.rubric)
                    )


if __name__ == "__main__":
    unittest.main()
