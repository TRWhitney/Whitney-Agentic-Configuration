from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.fixtures import Workspace, git, make_workspace
from evals.models import CommitCountCheck, GitHubStateCheck, load_cases
from evals.runner import Observation, check_result
from tests.test_eval_runner import SOURCE


class PRDescriptionTests(unittest.TestCase):
    def filed_body_passes(
        self, workspace: Workspace, check: GitHubStateCheck, description: str
    ) -> bool:
        state_path = workspace.home / "work-system/github.json"
        state = json.loads(state_path.read_text())
        state["prs"] = {"12": {"number": 12, "body": description}}
        state_path.write_text(json.dumps(state))
        return check_result(check, Observation(), workspace, "main", [])[0]

    def test_format_check_reads_filed_body_and_rejects_missing_sections(self) -> None:
        cases = {
            case.id: case
            for case in load_cases(SOURCE / "evals/cases")
            if "pr-description" in case.tags
        }
        headings = [
            "Problem",
            "What changed",
            "Code example",
            "Why this was needed",
            "Why this approach",
            "Setup and limits",
            "Validation",
        ]

        def body(sections: list[str]) -> str:
            return "\n\n".join(f"## {name}\n\nExplanation." for name in sections) + (
                "\n\nCloses #11.\n"
            )

        valid = body(headings)
        for case in cases.values():
            check = next(
                check
                for check in case.steps[-1].checks
                if isinstance(check, GitHubStateCheck)
            )
            with self.subTest(case=case.id), make_workspace(SOURCE, case) as workspace:
                workspace.file("draft.md").write_text(valid)
                self.assertFalse(self.filed_body_passes(workspace, check, "Old body."))
                self.assertTrue(self.filed_body_passes(workspace, check, valid))
                self.assertTrue(self.filed_body_passes(workspace, check, "\n" + valid))
                self.assertTrue(
                    self.filed_body_passes(
                        workspace, check, valid.replace("\n", "\r\n")
                    )
                )
                for missing in headings:
                    with self.subTest(missing=missing):
                        self.assertFalse(
                            self.filed_body_passes(
                                workspace,
                                check,
                                body([h for h in headings if h != missing]),
                            )
                        )
                swapped = headings.copy()
                swapped[3], swapped[4] = swapped[4], swapped[3]
                for description in (
                    body(swapped),
                    valid.replace("Closes #11.", ""),
                    valid.replace("Closes #11.", "Closes #99."),
                ):
                    self.assertFalse(
                        self.filed_body_passes(workspace, check, description)
                    )
                self.assertTrue(
                    self.filed_body_passes(
                        workspace, check, valid.replace("Closes #11.", "Fixes #11")
                    )
                )
                self.assertTrue(
                    self.filed_body_passes(
                        workspace,
                        check,
                        valid.replace("Closes #11.", "Closes #11. Related to #10."),
                    )
                )
                for reference in (
                    "CLOSES: #11.",
                    "Fixed #11.",
                    "Resolve example/inventory#11.",
                ):
                    self.assertTrue(
                        self.filed_body_passes(
                            workspace, check, valid.replace("Closes #11.", reference)
                        )
                    )

    def test_description_only_control_accepts_initial_commit_but_no_new_commit(
        self,
    ) -> None:
        case = next(
            case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id == "github-pr-description-small"
        )
        check = next(
            check
            for check in case.steps[-1].checks
            if isinstance(check, CommitCountCheck)
        )
        with make_workspace(SOURCE, case) as workspace:
            self.assertTrue(
                check_result(check, Observation(), workspace, "main", [])[0]
            )
            git(workspace.root, "commit", "--allow-empty", "-qm", "Unrequested commit")
            self.assertFalse(
                check_result(check, Observation(), workspace, "main", [])[0]
            )

    def test_evidence_links_need_a_fixed_revision(self) -> None:
        case = next(
            case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id == "github-pr-description-small"
        )
        check = case.steps[-1].checks[1]
        assert isinstance(check, GitHubStateCheck)
        with make_workspace(SOURCE, case) as workspace:
            revision = git(workspace.root, "rev-parse", "HEAD")
            body = "Validation: checked the help command."
            self.assertFalse(self.filed_body_passes(workspace, check, body))
            link = "https://github.com/example/inventory/blob/"
            self.assertFalse(
                self.filed_body_passes(
                    workspace, check, body + link + "main/docs/notes.md"
                )
            )
            self.assertTrue(
                self.filed_body_passes(
                    workspace, check, body + link + revision + "/docs/notes.md"
                )
            )

    def test_export_fixture_demonstrates_stop_and_retained_earlier_files(self) -> None:
        case = next(
            case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id == "github-pr-description"
        )
        with make_workspace(SOURCE, case) as workspace:
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                cwd=workspace.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            workspace.file("src/exporter.py").write_text(case.files["src/exporter.py"])
            original = subprocess.run(
                [sys.executable, "-m", "src.exporter", "examples/missing-folder.json"],
                cwd=workspace.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(original.returncode, 0)
            self.assertIn("missing-output-folder", original.stderr)


if __name__ == "__main__":
    unittest.main()
