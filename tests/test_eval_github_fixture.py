from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.fixtures import make_workspace
from evals.models import CaseSpec
from tests.test_eval_runner import SOURCE


class GitHubFixtureTests(unittest.TestCase):
    def test_planning_and_blocked_implementation_have_distinct_labels(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "issue-labels",
                "tags": [],
                "files": {},
                "tracker": "github",
                "github_issues": {"10": "Export planning.", "11": "Blocked export."},
                "github_issue_labels": {"11": ["blocked"]},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "What is unfinished?",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as workspace:
            state = workspace.service_state()
            assert state is not None
            issues = state["issues"]
            assert isinstance(issues, dict)
            planning, implementation = issues["10"], issues["11"]
            assert isinstance(planning, dict) and isinstance(implementation, dict)
            self.assertEqual(planning["labels"], [])
            self.assertEqual(implementation["labels"], [{"name": "blocked"}])

    def test_pr_states_and_issue_contents_come_from_case_setup(self) -> None:
        for state in ("OPEN", "CLOSED", "MERGED", None):
            case = CaseSpec.model_validate(
                {
                    "id": "github-response",
                    "tags": [],
                    "files": {},
                    "github_pr_state": state,
                    "github_issue_body": "Accepted search design.",
                    "steps": [
                        {
                            "kind": "message",
                            "prompt": "Check planning.",
                            "checks": [{"kind": "tracker", "name": "local"}],
                        }
                    ],
                }
            )
            with self.subTest(state=state), make_workspace(SOURCE, case) as workspace:

                def query(*args: str) -> object:
                    result = subprocess.run(
                        [sys.executable, str(workspace.home / "bin/github.py"), *args],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    return json.loads(result.stdout)

                issues = query("issue", "view", "10")
                assert isinstance(issues, dict)
                self.assertEqual(issues["body"], "Accepted search design.")
                listed = query("pr", "list")
                assert isinstance(listed, list)
                self.assertEqual(len(listed), 0 if state is None else 1)
                if state is not None:
                    pr = query("pr", "view", "12")
                    assert isinstance(pr, dict)
                    self.assertEqual(pr["state"], state)
                    self.assertEqual(pr["mergedAt"] is not None, state == "MERGED")
                    self.assertEqual(pr["isDraft"], state == "OPEN")


if __name__ == "__main__":
    unittest.main()
