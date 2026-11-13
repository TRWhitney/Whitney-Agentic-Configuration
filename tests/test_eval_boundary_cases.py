from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.fixtures import Workspace, git, make_workspace
from evals.models import load_cases
from evals.runner import CommandResult, Observation, check_result, run_case
from tests.eval_support import observe_case
from tests.test_eval_runner import SOURCE, FakeDriver


class BoundaryCasesTests(unittest.TestCase):
    def test_planning_discussion_allows_comments_but_rejects_new_prs(self) -> None:
        from evals.models import GitHubStateCheck, NoPublishCheck

        cases = {case.id: case for case in load_cases(SOURCE / "evals/cases")}
        for name in ("github-create-timeout", "github-planning-edit-persists"):
            case = cases[name]
            checks = [
                check
                for step in case.steps
                for check in step.checks
                if (
                    isinstance(check, NoPublishCheck)
                    and check.target == "pull_requests"
                )
                or (isinstance(check, GitHubStateCheck) and check.resource == "prs")
            ]
            self.assertTrue(checks)
            with self.subTest(case=name), make_workspace(SOURCE, case) as workspace:
                command = [sys.executable, str(workspace.home / "bin/github.py")]
                subprocess.run(
                    [*command, "pr", "comment", "12", "--body", "Decision still open."],
                    check=True,
                    capture_output=True,
                )
                for check in checks:
                    self.assertTrue(
                        check_result(check, Observation(), workspace, "main", [])[0]
                    )
                subprocess.run(
                    [*command, "pr", "create", "--title", "Redundant planning PR"],
                    check=False,
                    capture_output=True,
                )
                for check in checks:
                    self.assertFalse(
                        check_result(check, Observation(), workspace, "main", [])[0]
                    )

    def test_github_readiness_requires_code_and_closed_pr_blocks_it(self) -> None:
        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        for name in ("planning-pr-merged", "planning-without-document-pr"):
            case = cases[name]
            code = (
                case.files["src/app.py"]
                + "\n\ndef search_items(items, query):\n"
                + "    needle = query.casefold()\n"
                + "    return [item for item in items\n"
                + '            if needle in item["name"].casefold()]\n'
            )
            results = (
                CommandResult(
                    "python3 checks/check_search.py",
                    0,
                    "Seven inventory checks passed.",
                ),
            )
            for state in ("implementation", "validation", "delivery"):
                with self.subTest(case=name, state=state):
                    result = observe_case(
                        case,
                        {"src/app.py": code},
                        "Search is implemented and its current checks passed.",
                        progress=(state, None),
                        command_results=results,
                    )
                    self.assertEqual(result.mechanical_status, "pass")
                    self.assertEqual(result.status, "inconclusive")
            self.assertEqual(
                observe_case(
                    case,
                    {},
                    "Ready.",
                    progress=("implementation", None),
                    command_results=results,
                ).mechanical_status,
                "fail",
            )
        case = cases["planning-pr-closed"]
        blocked = observe_case(case, {}, "The planning PR is closed and unmerged.")
        self.assertEqual(blocked.mechanical_status, "pass")
        self.assertEqual(blocked.status, "inconclusive")
        self.assertEqual(
            observe_case(
                case, {}, "Closed.", progress=("implementation", None)
            ).mechanical_status,
            "fail",
        )

    def test_unprompted_correction_still_needs_current_execution(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "correction-without-reminder"
        )
        case.steps = [case.steps[0], case.steps[-1]]
        changes = {
            "src/app.py": case.files["src/app.py"].replace(
                "No items saved.", "Your shelf is empty."
            ),
            "checks/check_message.py": case.files["checks/check_message.py"].replace(
                "No items saved.", "Your shelf is empty."
            ),
            ".work/message/spec.md": "Return Your shelf is empty.\n",
        }
        result = CommandResult(
            "python3 checks/check_message.py",
            0,
            "Message check passed: Your shelf is empty.",
        )
        for commands, expected in (((result,), "pass"), ((), "fail")):

            def factory(
                workspace: Workspace,
                model: str,
                timeout: float,
                max_tokens: int,
                *,
                observations: tuple[CommandResult, ...] = commands,
            ) -> FakeDriver:
                class Driver(FakeDriver):
                    def message(self, thread: str, prompt: str) -> Observation:
                        for path, text in changes.items():
                            workspace.file(path).write_text(text)
                        workspace.progress_path(thread).unlink()
                        git(workspace.root, "add", ".")
                        git(workspace.root, "commit", "-qm", "Correct empty message")
                        return Observation(
                            "The corrected message is ready.",
                            10,
                            command_results=observations,
                        )

                return Driver()

            with self.subTest(commands=commands):
                observed = run_case(
                    case, SOURCE, "example-model", driver_factory=factory
                )
                self.assertEqual(observed.mechanical_status, expected)
                self.assertEqual(
                    observed.status, "inconclusive" if expected == "pass" else "fail"
                )

    def test_source_preservation_allows_cache_but_rejects_new_production_code(
        self,
    ) -> None:
        from evals.models import UnchangedCheck

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "diagnosis-needs-design"
        )
        check = UnchangedCheck.model_validate(
            {"kind": "unchanged", "paths": ["src"], "exclude": ["src/__pycache__"]}
        )
        with make_workspace(SOURCE, case) as workspace:
            cache = workspace.file("src/__pycache__/app.pyc")
            cache.parent.mkdir()
            cache.write_bytes(b"generated bytecode")
            self.assertTrue(
                check_result(check, Observation(), workspace, "main", [])[0]
            )
            workspace.file("src/negative_policy.py").write_text("def reject(): pass\n")
            self.assertFalse(
                check_result(check, Observation(), workspace, "main", [])[0]
            )

    def test_pr_publication_check_covers_cli_and_api_but_allows_issue_updates(
        self,
    ) -> None:
        from evals.models import NoPublishCheck

        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        for name in (
            "planning-pr-closed",
            "planning-pr-unmerged",
            "github-planning-read-failure",
        ):
            case = cases[name]
            publication_check = next(
                check
                for step in case.steps
                for check in step.checks
                if isinstance(check, NoPublishCheck)
            )
            with make_workspace(SOURCE, case) as workspace:
                for call, passed in (
                    (["pr", "create"], False),
                    (["pr", "comment", "12", "--body", "Decision is still open"], True),
                    (["pr", "merge", "12"], False),
                    (["pr", "reopen", "12"], False),
                    (["pr", "edit", "12", "--title", "Replacement"], False),
                    (
                        [
                            "api",
                            "repos/example/inventory/pulls",
                            "-f",
                            "title=Planning",
                        ],
                        False,
                    ),
                    (
                        [
                            "api",
                            "-XPOST",
                            "repos/example/inventory/pulls",
                            "--input",
                            "body.json",
                        ],
                        False,
                    ),
                    (["api", "repos/example/inventory/pulls"], True),
                    (["issue", "edit", "11", "--add-label", "active"], True),
                    (
                        [
                            "api",
                            "repos/example/inventory/issues/11",
                            "-f",
                            "body=Updated",
                        ],
                        True,
                    ),
                ):
                    with self.subTest(call=call):
                        (workspace.home / "work-system/service-calls.jsonl").write_text(
                            json.dumps(call) + "\n"
                        )
                        self.assertEqual(
                            check_result(
                                publication_check,
                                Observation(),
                                workspace,
                                "main",
                                [],
                            )[0],
                            passed,
                        )

                strict = publication_check.model_copy(
                    update={"allow_pr_comments": False}
                )
                (workspace.home / "work-system/service-calls.jsonl").write_text(
                    json.dumps(["pr", "comment", "12", "--body", "Still open"]) + "\n"
                )
                self.assertFalse(
                    check_result(strict, Observation(), workspace, "main", [])[0]
                )

    def test_review_allows_correcting_summary_but_protects_accepted_docs(self) -> None:
        from evals.models import UnchangedCheck

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "initial-review-without-priming"
        )
        check = next(
            check
            for step in case.steps
            for check in step.checks
            if isinstance(check, UnchangedCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            workspace.file("docs/previous-summary.md").write_text(
                "# Label change summary\n\nThe title is Shelf inventory.\n"
            )
            self.assertTrue(
                check_result(check, Observation(), workspace, "main", [])[0]
            )
            workspace.file("docs/label-spec.md").write_text(
                "# A different requirement\n"
            )
            self.assertFalse(
                check_result(check, Observation(), workspace, "main", [])[0]
            )

    def test_product_policy_question_allows_discovery_or_planning(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "diagnosis-needs-design"
        )

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    workspace.progress_path(thread).write_text(
                        json.dumps({"workflow": "novel-work", "state": "planning"})
                    )
                    return Observation(
                        "Should negative quantities be accepted or rejected?", 10
                    )

            return Driver()

        result = run_case(case, SOURCE, "example-model", driver_factory=factory)
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertEqual(
            observe_case(
                case, {}, "Should negative quantities be accepted or rejected?"
            ).mechanical_status,
            "pass",
        )

    def test_review_rework_requires_fresh_checks_amendment_and_preserved_edit(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "review-finding-rework"
        )
        for missing in (None, "amend", "earlier-edit", "checks", "route"):

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
                        code = case.files["src/app.py"].replace(
                            ".lower()", ".casefold()"
                        )
                        if omit == "earlier-edit":
                            code = code.replace(
                                "Your shelf is empty.", "No items saved."
                            )
                        workspace.file("src/app.py").write_text(code)
                        before = git(workspace.root, "rev-parse", "HEAD")
                        workspace.navigate(thread, ["cancel"])
                        git(workspace.root, "add", ".")
                        if omit == "amend":
                            git(workspace.root, "commit", "-qm", "Fix search")
                        else:
                            git(workspace.root, "commit", "--amend", "--no-edit", "-q")
                        workspace.navigate(
                            thread,
                            ["commit", "add", "HEAD"]
                            + ([] if omit == "amend" else ["--replaces", before]),
                        )
                        results = (
                            ()
                            if omit == "checks"
                            else (
                                CommandResult(
                                    "python3 checks/check_search.py",
                                    1,
                                    "AssertionError: Unicode case folding",
                                ),
                                CommandResult(
                                    "python3 checks/check_search.py",
                                    0,
                                    "Seven inventory checks passed.",
                                ),
                            )
                        )
                        return Observation(
                            "Complete.",
                            10,
                            ()
                            if omit == "route"
                            else (
                                "move novel-work delivery implementation",
                                "move novel-work implementation validation",
                                "move novel-work validation delivery",
                                "move novel-work delivery complete",
                            ),
                            command_results=results,
                        )

                return Driver()

            with self.subTest(missing=missing):
                result = run_case(case, SOURCE, "example-model", driver_factory=factory)
                self.assertEqual(
                    result.mechanical_status,
                    "pass" if missing is None else "fail",
                    result.detail,
                )
                self.assertEqual(
                    result.status, "inconclusive" if missing is None else "fail"
                )


if __name__ == "__main__":
    unittest.main()
