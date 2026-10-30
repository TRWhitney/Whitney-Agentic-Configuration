from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, EditStep, GitHubStateCheck
from evals.runner import Observation, check_result, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


class SetupTests(unittest.TestCase):
    def case(self, **updates: object) -> CaseSpec:
        return CaseSpec.model_validate(
            {
                "id": "setup",
                "tags": [],
                "files": {"record.md": "Initial record.\n"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Read the record.",
                        "checks": [{"kind": "tracker", "name": "local"}],
                    }
                ],
                **updates,
            }
        )

    def test_commit_setup_belongs_only_to_its_conversation(self) -> None:
        case = self.case(
            steps=[
                {"kind": "edit", "record_commit": True},
                {
                    "kind": "message",
                    "prompt": "Read the record.",
                    "checks": [{"kind": "tracker", "name": "local"}],
                },
                {"kind": "message", "conversation": "other", "prompt": "Read it too."},
            ]
        )
        seen: list[bool] = []

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    state = workspace.progress(thread) or {}
                    commits = state.get("commits", {})
                    seen.append(workspace.initial_commit in str(commits))
                    return Observation("Read.", 10)

            return Driver()

        result = run_case(case, SOURCE, "example", driver_factory=factory)
        self.assertEqual(result.status, "pass", result.detail)
        self.assertEqual(seen, [True, False])

    def test_edits_apply_between_messages_without_resetting_baselines(self) -> None:
        case = self.case(
            steps=[
                {
                    "kind": "message",
                    "prompt": "First.",
                    "checks": [
                        {
                            "kind": "file_equals",
                            "path": "record.md",
                            "text": "Initial record.\n",
                        }
                    ],
                },
                {
                    "kind": "edit",
                    "files": {"new.md": "New.\n"},
                    "remove": ["record.md"],
                },
                {
                    "kind": "message",
                    "prompt": "Second.",
                    "checks": [
                        {"kind": "file_equals", "path": "new.md", "text": "New.\n"},
                        {"kind": "unchanged", "paths": ["record.md"]},
                    ],
                },
            ]
        )
        seen: list[bool] = []

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    seen.append(workspace.file("record.md").exists())
                    return Observation("Read.", 10)

            return Driver()

        result = run_case(case, SOURCE, "example", driver_factory=factory)
        self.assertEqual(result.status, "fail")
        self.assertEqual([c.passed for c in result.checks], [True, True, False])
        self.assertEqual(seen, [True, False])

    def test_damaged_navigation_can_be_checked_without_parsing_it(self) -> None:
        case = self.case(
            steps=[
                {"kind": "edit", "navigation_text": "{broken"},
                {
                    "kind": "message",
                    "prompt": "Resume.",
                    "checks": [{"kind": "navigation_text", "text": "{broken"}],
                },
            ]
        )
        driver = FakeDriver()
        self.assertEqual(
            run_case(case, SOURCE, "example", driver_factory=lambda *a: driver).status,
            "pass",
        )
        case.steps[-1].checks[0].text = "different"  # type: ignore[union-attr]
        self.assertEqual(
            run_case(case, SOURCE, "example", driver_factory=lambda *a: driver).status,
            "fail",
        )

    def test_edit_paths_and_service_expectations_are_validated(self) -> None:
        for data in (
            {"files": {"../escape": ""}},
            {"remove": [".git/config"]},
            {"files": {"a": ""}, "remove": ["a"]},
        ):
            with self.subTest(data=data), self.assertRaises(ValueError):
                EditStep.model_validate({"kind": "edit", **data})
        with self.assertRaises(ValueError):
            GitHubStateCheck.model_validate({"kind": "github_state"})
        with self.assertRaises(ValueError):
            self.case(github_issues={"../10": "Invalid"})

    def query(
        self, workspace: Workspace, *args: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(workspace.home / "bin/github.py"), *args],
            capture_output=True,
            text=True,
            timeout=10,
        )

    def test_issue_edit_body_file_is_visible_to_later_reads(self) -> None:
        with make_workspace(
            SOURCE, self.case(github_issues={"10": "Old answer."})
        ) as w:
            body = w.file("answer.md")
            body.write_text("Accepted: header-only CSV.\n")
            self.assertEqual(
                self.query(
                    w, "issue", "edit", "10", "--body-file", str(body)
                ).returncode,
                0,
            )
            result = self.query(w, "issue", "view", "10")
            self.assertEqual(json.loads(result.stdout)["body"], body.read_text())
            for pattern, count, expected in [
                ("header-only", 1, True),
                ("old", 1, False),
                ("header-only", 2, False),
            ]:
                check = GitHubStateCheck(count=count, number=10, body_pattern=pattern)
                self.assertEqual(
                    check_result(check, Observation(), w, "thread", [])[0], expected
                )

    def test_rest_patch_updates_only_the_selected_issue(self) -> None:
        with make_workspace(
            SOURCE, self.case(github_issues={"10": "First.", "11": "Second."})
        ) as w:
            result = self.query(
                w,
                "api",
                "repos/example/inventory/issues/11",
                "-X",
                "PATCH",
                "-f",
                "body=Revised.",
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(
                json.loads(self.query(w, "issue", "view", "11").stdout)["body"],
                "Revised.",
            )
            self.assertEqual(
                json.loads(self.query(w, "issue", "view", "10").stdout)["body"],
                "First.",
            )

    def test_create_timeout_saves_exactly_one_issue_and_can_be_read_back(self) -> None:
        with make_workspace(
            SOURCE,
            self.case(github_issues={"10": "Original."}, github_write_timeout=True),
        ) as w:
            result = self.query(
                w,
                "issue",
                "create",
                "--title",
                "Export",
                "--body",
                "Pending empty-input decision.",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("timed out", result.stderr)
            listed = json.loads(self.query(w, "issue", "list").stdout)
            self.assertEqual([item["number"] for item in listed], [10, 11])
            self.assertEqual(listed[1]["body"], "Pending empty-input decision.")
            self.assertEqual(
                self.query(w, "issue", "create", "--title", "Another").returncode, 0
            )

    def test_unavailable_reads_do_not_return_success_or_change_state(self) -> None:
        with make_workspace(
            SOURCE, self.case(github_issues={"10": "Original."}, github_read_error=True)
        ) as w:
            before = (w.home / "work-system/github.json").read_bytes()
            result = self.query(w, "issue", "view", "10")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertEqual((w.home / "work-system/github.json").read_bytes(), before)
            self.assertEqual(w.service_calls(), [["issue", "view", "10"]])

    def test_comments_preserve_issue_bodies_and_edits_do_not_consume_create_timeout(
        self,
    ) -> None:
        case = self.case(
            github_issues={"10": "Accepted design."}, github_write_timeout=True
        )
        with make_workspace(SOURCE, case) as w:
            self.assertEqual(
                self.query(
                    w, "issue", "comment", "10", "--body", "Continuation."
                ).returncode,
                0,
            )
            issue = json.loads(self.query(w, "issue", "view", "10").stdout)
            self.assertEqual(issue["body"], "Accepted design.")
            self.assertEqual(issue["comments"], [{"body": "Continuation."}])
            result = self.query(w, "issue", "create", "--title", "Export")
            self.assertEqual(result.returncode, 1)
            self.assertIn("timed out", result.stderr)

    def test_a_different_repository_cannot_read_or_write_fixture_issues(self) -> None:
        with make_workspace(SOURCE, self.case(github_issues={"10": "Original."})) as w:
            result = self.query(
                w, "issue", "edit", "10", "--repo", "other/repo", "--body", "Wrong."
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                json.loads(self.query(w, "issue", "view", "10").stdout)["body"],
                "Original.",
            )

    def test_rest_calls_cannot_read_or_write_a_different_repository(self) -> None:
        for method in ("GET", "PATCH"):
            with (
                self.subTest(method=method),
                make_workspace(
                    SOURCE, self.case(github_issues={"10": "Original."})
                ) as w,
            ):
                path = w.home / "work-system/github.json"
                before = path.read_bytes()
                arguments = ["api", "repos/other/repo/issues/10", "-X", method]
                if method == "PATCH":
                    arguments.extend(["-f", "body=Wrong."])
                result = self.query(w, *arguments)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
