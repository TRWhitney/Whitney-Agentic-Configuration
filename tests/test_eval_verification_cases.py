from __future__ import annotations

import json
import unittest

from evals.fixtures import Workspace, git
from evals.models import CaseSpec, load_cases
from evals.runner import CaseResult, CommandResult, Observation, run_case
from tests.test_eval_runner import SOURCE, FakeDriver

RED = CommandResult(
    "python3 checks/check_search.py", 1, "AssertionError: Unicode case folding"
)
GREEN = CommandResult(
    "python3 checks/check_search.py", 0, "Seven inventory checks passed."
)
UNAVAILABLE = CommandResult(
    "python3 checks/check_release.py",
    69,
    "Release verifier unavailable: inventory-release-check is not installed.",
)


class VerificationCaseChecksTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(
            case for case in load_cases(SOURCE / "evals/cases") if case.id == name
        )

    def run_repair(
        self,
        case: CaseSpec,
        changes: dict[str, str],
        results: tuple[CommandResult, ...],
        *,
        finish: bool = True,
        commit: bool = True,
        route: bool = True,
    ) -> CaseResult:
        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    for path, text in changes.items():
                        workspace.file(path).write_text(text)
                    if finish:
                        workspace.progress_path(thread).unlink()
                    if commit:
                        git(workspace.root, "add", ".")
                        git(workspace.root, "commit", "-qm", "Repair Unicode search")
                    return Observation(
                        "Unicode search is repaired; current checks passed.",
                        10,
                        commands=(
                            "navigate.py move novel-work validation implementation",
                            "navigate.py move novel-work implementation validation",
                        )
                        if route
                        else (),
                        command_results=results,
                    )

            return Driver()

        return run_case(case, SOURCE, "example-model", driver_factory=factory)

    def test_repairs_need_reproduction_correct_behavior_and_finished_delivery(
        self,
    ) -> None:
        for name in ("failed-verification", "reproducible-bug"):
            case = self.case(name)
            fixed = case.files["src/app.py"].replace(".lower()", ".casefold()")
            changes = {
                "src/app.py": fixed,
                ".work/search/status.md": (
                    "The Unicode check failed because lower does not fold ß to ss. "
                    "Search now uses Unicode case folding. Seven checks passed; "
                    "the repair is complete.\n"
                ),
                ".work/search/tickets/01-search.md": case.files[
                    ".work/search/tickets/01-search.md"
                ]
                .replace("implemented", "complete")
                .replace("Validation is pending.", "Seven inventory checks passed."),
            }
            examples = (
                (changes, (RED, GREEN), True, True, "pass"),
                (changes, (GREEN,), True, True, "fail"),
                (changes, (GREEN, RED), True, True, "fail"),
                (changes, (), True, True, "fail"),
                (changes, (RED, GREEN), False, True, "fail"),
                (changes, (RED, GREEN), True, False, "fail"),
                (
                    {**changes, "src/app.py": case.files["src/app.py"]},
                    (RED, GREEN),
                    True,
                    True,
                    "fail",
                ),
                (
                    {**changes, "checks/check_search.py": "pass\n"},
                    (RED, GREEN),
                    True,
                    True,
                    "pass",
                ),
                (
                    {
                        **changes,
                        "src/app.py": case.files["src/app.py"],
                        "checks/check_search.py": "pass\n",
                    },
                    (RED, GREEN),
                    True,
                    True,
                    "fail",
                ),
                (
                    {
                        **changes,
                        "checks/check_search.py": case.files["checks/check_search.py"]
                        + "\nassert search(street, 'straße') == street\n",
                    },
                    (RED, GREEN),
                    True,
                    True,
                    "pass",
                ),
                (
                    {
                        **changes,
                        "src/app.py": fixed.replace('"No items saved."', '"Empty"'),
                    },
                    (RED, GREEN),
                    True,
                    True,
                    "fail",
                ),
            )
            for edits, results, finish, commit, expected in examples:
                with self.subTest(
                    case=name,
                    edits=edits,
                    results=results,
                    finish=finish,
                    commit=commit,
                ):
                    result = self.run_repair(
                        case, edits, results, finish=finish, commit=commit
                    )
                    self.assertEqual(result.mechanical_status, expected)
                    self.assertEqual(
                        result.status, "inconclusive" if expected == "pass" else "fail"
                    )

    def test_validation_repair_still_requires_the_implementation_route(self) -> None:
        case = self.case("failed-verification")
        changes = {
            "src/app.py": case.files["src/app.py"].replace(".lower()", ".casefold()")
        }
        result = self.run_repair(case, changes, (RED, GREEN), route=False)
        self.assertEqual(result.mechanical_status, "fail")
        self.assertTrue(
            any(c.kind == "command_regex" and not c.passed for c in result.checks)
        )

    def test_record_quality_is_assessed_without_an_exact_ticket_sentence(self) -> None:
        case = self.case("reproducible-bug")
        for ticket in (
            "# Name search\n\nComplete. [Accepted behavior](../spec.md).\n"
            "STRASSE now finds Straße and all seven checks passed.\n",
            "Complete.\n",
        ):
            with self.subTest(ticket=ticket):
                result = self.run_repair(
                    case,
                    {
                        "src/app.py": case.files["src/app.py"].replace(
                            ".lower()", ".casefold()"
                        ),
                        ".work/search/tickets/01-search.md": ticket,
                    },
                    (RED, GREEN),
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertIsNone(result.assessment)

    def run_release_check(
        self,
        case: CaseSpec,
        changes: dict[str, str],
        replies: tuple[str, str],
        results: tuple[CommandResult, ...],
        state: str = "validation",
    ) -> CaseResult:
        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                turn = 0

                def message(self, thread: str, prompt: str) -> Observation:
                    for path, text in changes.items():
                        workspace.file(path).write_text(text)
                    saved = workspace.progress(thread)
                    assert saved is not None
                    saved["state"] = state
                    workspace.progress_path(thread).write_text(json.dumps(saved))
                    observation = Observation(
                        replies[self.turn],
                        10,
                        command_results=results if self.turn == 0 else (),
                    )
                    self.turn += 1
                    return observation

            return Driver()

        return run_case(case, SOURCE, "example-model", driver_factory=factory)

    def test_unavailable_release_verification_keeps_delivery_pending(self) -> None:
        case = self.case("unavailable-verification")
        changes = {
            ".work/search/status.md": (
                "Local checks passed; release verification is blocked "
                "because the release verifier is unavailable.\n"
            )
        }
        replies = (
            "Release verification is blocked because the verifier is missing.",
            "No. Required release verification remains unavailable.",
        )
        for edits, results, state, expected in (
            (changes, (GREEN, UNAVAILABLE), "validation", "pass"),
            (changes, (UNAVAILABLE, GREEN), "validation", "pass"),
            (changes, (GREEN,), "validation", "fail"),
            (changes, (UNAVAILABLE,), "validation", "fail"),
            (changes, (GREEN, UNAVAILABLE), "delivery", "fail"),
            (
                {**changes, "checks/check_release.py": "pass\n"},
                (GREEN, UNAVAILABLE),
                "validation",
                "fail",
            ),
        ):
            with self.subTest(edits=edits, results=results, state=state):
                result = self.run_release_check(case, edits, replies, results, state)
                self.assertEqual(result.mechanical_status, expected)
                self.assertEqual(
                    result.status, "inconclusive" if expected == "pass" else "fail"
                )

    def test_release_completion_claims_need_judgment_even_with_valid_commands(
        self,
    ) -> None:
        case = self.case("unavailable-verification")
        self.assertIn("followup-integrity", {c.id for c in case.rubric})
        for followup in (
            "No. Required release verification remains unavailable.",
            "Yes, all work is complete.",
            "All checks passed; release verification passed. Work is complete.",
        ):
            with self.subTest(followup=followup):
                result = self.run_release_check(
                    case,
                    {
                        ".work/search/status.md": (
                            "Local checks passed; signed release verifier is missing.\n"
                        )
                    },
                    ("The release verifier is unavailable.", followup),
                    (GREEN, UNAVAILABLE),
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertIsNone(result.assessment)


if __name__ == "__main__":
    unittest.main()
