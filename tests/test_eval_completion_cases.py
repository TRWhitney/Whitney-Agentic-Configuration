from __future__ import annotations

import unittest

from evals.fixtures import Workspace, git
from evals.models import load_cases
from evals.runner import CommandResult, Observation, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


class CompletionCaseTests(unittest.TestCase):
    def test_correction_needs_fresh_success_with_the_updated_message(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "rerun-after-correction"
        )
        case.steps = [case.steps[0], case.steps[-1]]
        updated = {
            "src/app.py": case.files["src/app.py"].replace(
                "No items saved.", "Your shelf is empty."
            ),
            ".work/message/spec.md": "Return Your shelf is empty.\n",
            "checks/check_message.py": case.files["checks/check_message.py"].replace(
                "No items saved.", "Your shelf is empty."
            ),
        }
        for results, expected in (
            (
                (
                    CommandResult(
                        "python3 checks/check_message.py",
                        0,
                        "Message check passed: Your shelf is empty.",
                    ),
                ),
                "pass",
            ),
            ((), "fail"),
            (
                (
                    CommandResult(
                        "python3 checks/check_message.py",
                        0,
                        "Message check passed: No items saved.",
                    ),
                ),
                "fail",
            ),
            (
                (
                    CommandResult(
                        "python3 checks/check_message.py",
                        1,
                        "Message check passed: Your shelf is empty.",
                    ),
                ),
                "fail",
            ),
        ):

            def factory(
                workspace: Workspace,
                model: str,
                timeout: float,
                max_tokens: int,
                *,
                observations: tuple[CommandResult, ...] = results,
            ) -> FakeDriver:
                class Driver(FakeDriver):
                    def message(self, thread: str, prompt: str) -> Observation:
                        for path, text in updated.items():
                            workspace.file(path).write_text(text)
                        workspace.progress_path(thread).unlink()
                        git(workspace.root, "add", ".")
                        git(workspace.root, "commit", "-qm", "Correct empty message")
                        return Observation(
                            "The message is corrected.",
                            10,
                            command_results=observations,
                        )

                return Driver()

            with self.subTest(results=results):
                result = run_case(case, SOURCE, "example-model", driver_factory=factory)
                self.assertEqual(result.mechanical_status, expected)
                self.assertEqual(
                    result.status, "inconclusive" if expected == "pass" else "fail"
                )

    def test_local_delivery_requires_code_commit_cleared_progress_and_execution(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "complete-local-workflow"
        )
        for missing in (None, "code", "commit", "clear", "execution", "untracked"):

            def factory(
                workspace: Workspace,
                model: str,
                timeout: float,
                max_tokens: int,
                *,
                omit: str | None = missing,
            ) -> FakeDriver:
                class Driver(FakeDriver):
                    def message(self, thread: str, prompt: str) -> Observation:
                        if omit != "code":
                            workspace.file("src/app.py").write_text(
                                case.files["src/app.py"].replace(
                                    "No items saved.", "Your shelf is empty."
                                )
                            )
                        workspace.file("docs/inventory.md").write_text(
                            "# Shelf inventory\n\n"
                            "An empty shelf shows Your shelf is empty.\n"
                        )
                        workspace.file(".work/message/status.md").write_text(
                            "The accepted message is applied. "
                            "The message check passed.\n"
                        )
                        if omit != "clear":
                            workspace.progress_path(thread).unlink()
                        if omit != "commit":
                            git(workspace.root, "add", ".")
                            git(workspace.root, "commit", "-qm", "Update empty message")
                        if omit == "untracked":
                            workspace.file("unfinished.txt").write_text(
                                "Still pending.\n"
                            )
                        return Observation(
                            "The new message is applied.",
                            10,
                            command_results=()
                            if omit == "execution"
                            else (
                                CommandResult(
                                    "python3 checks/check_message.py",
                                    0,
                                    "Message check passed: Your shelf is empty.",
                                ),
                            ),
                        )

                return Driver()

            with self.subTest(missing=missing):
                result = run_case(case, SOURCE, "example-model", driver_factory=factory)
                self.assertEqual(
                    result.mechanical_status, "pass" if missing is None else "fail"
                )
                self.assertEqual(
                    result.status, "inconclusive" if missing is None else "fail"
                )

    def test_documentation_and_review_claims_cannot_replace_hidden_assessment(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "complete-local-workflow"
        )
        self.assertIn("reader-docs", {c.id for c in case.rubric})
        self.assertIn("delivered-result", {c.id for c in case.rubric})
        for update_guide, claim_review in ((True, False), (False, True)):

            def factory(
                workspace: Workspace,
                model: str,
                timeout: float,
                max_tokens: int,
                *,
                write_guide: bool = update_guide,
                review_claim: bool = claim_review,
            ) -> FakeDriver:
                class Driver(FakeDriver):
                    def message(self, thread: str, prompt: str) -> Observation:
                        workspace.file("src/app.py").write_text(
                            case.files["src/app.py"].replace(
                                "No items saved.", "Your shelf is empty."
                            )
                        )
                        if write_guide:
                            workspace.file("docs/inventory.md").write_text(
                                "An empty shelf shows Your shelf is empty.\n"
                            )
                        workspace.file(".work/message/status.md").write_text(
                            "Complete. Review passed.\n"
                            if review_claim
                            else "Complete.\n"
                        )
                        workspace.progress_path(thread).unlink()
                        git(workspace.root, "add", ".")
                        git(workspace.root, "commit", "-qm", "Update empty message")
                        return Observation(
                            "Complete.",
                            10,
                            command_results=(
                                CommandResult(
                                    "python3 checks/check_message.py",
                                    0,
                                    "Message check passed: Your shelf is empty.",
                                ),
                            ),
                        )

                return Driver()

            with self.subTest(update_guide=update_guide, claim_review=claim_review):
                result = run_case(case, SOURCE, "example-model", driver_factory=factory)
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertIsNone(result.assessment)


if __name__ == "__main__":
    unittest.main()
