"""Local GitHub operations needed by tracker conversion preserve service state."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.fixtures import make_workspace
from evals.models import CaseSpec
from tests.test_eval_runner import SOURCE


class TrackerConversionFixtureTests(unittest.TestCase):
    def test_cli_urls_and_labels_preserve_the_selected_issue(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "tracker-cli",
                "tags": [],
                "files": {},
                "github_issues": {"10": "Unrelated", "11": "Feature"},
                "github_write_timeout": True,
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w:

            def query(*args: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [sys.executable, str(w.home / "bin/github.py"), *args],
                    capture_output=True,
                    text=True,
                )

            path = w.home / "work-system/github.json"
            original = json.loads(path.read_text())
            query("label", "create", "ready-for-agent", "--description", "Ready")
            labels = query("label", "list", "--json", "name")
            self.assertEqual(json.loads(labels.stdout), [{"name": "ready-for-agent"}])
            result = query(
                "issue",
                "edit",
                "https://github.com/example/inventory/issues/11",
                "--add-label",
                "ready-for-agent",
                "--body",
                "Updated",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            viewed = json.loads(query("issue", "view", "11").stdout)
            self.assertEqual(viewed["body"], "Updated")
            self.assertEqual(viewed["labels"], [{"name": "ready-for-agent"}])
            self.assertEqual(
                json.loads(query("issue", "view", "10").stdout)["body"], "Unrelated"
            )
            self.assertEqual(json.loads(path.read_text())["prs"], original["prs"])
            self.assertTrue(json.loads(path.read_text())["write_timeout"])
            before = path.read_bytes()
            self.assertNotEqual(query("unknown", "create").returncode, 0)
            self.assertEqual(path.read_bytes(), before)
            query("issue", "create", "--title", "Timed out")
            created = query("issue", "create", "--title", "Next")
            self.assertEqual(
                created.stdout.strip(), "https://github.com/example/inventory/issues/13"
            )

    def test_help_preserves_records_and_pending_timeout(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "tracker-help",
                "tags": [],
                "files": {},
                "github_write_timeout": True,
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w:
            state_path = w.home / "work-system/github.json"
            original = state_path.read_bytes()
            for command in (["issue", "create", "--help"], ["pr", "create", "-h"]):
                result = subprocess.run(
                    [sys.executable, str(w.home / "bin/github.py"), *command],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--body-file", result.stdout)
                self.assertEqual(state_path.read_bytes(), original)
            result = subprocess.run(
                [
                    sys.executable,
                    str(w.home / "bin/github.py"),
                    "issue",
                    "create",
                    "--title",
                    "Actual issue",
                    "--body",
                    "Work",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("timed out", result.stderr)
            saved = json.loads(state_path.read_text())
            self.assertTrue(
                any(r["title"] == "Actual issue" for r in saved["issues"].values())
            )
            created = next(
                r for r in saved["issues"].values() if r["title"] == "Actual issue"
            )
            self.assertNotEqual(created["id"], created["number"])

    def test_access_and_native_parent_links_use_only_fixture_records(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "tracker-access",
                "tags": [],
                "files": {},
                "github_issues": {"10": "Parent", "11": "Child"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "tracker", "name": "local"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w:

            def query(*args: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [sys.executable, str(w.home / "bin/github.py"), *args],
                    capture_output=True,
                    text=True,
                )

            r = query(
                "repo",
                "view",
                "example/inventory",
                "--json",
                "nameWithOwner,hasIssuesEnabled",
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            repo = json.loads(r.stdout)
            self.assertEqual(repo["nameWithOwner"], "example/inventory")
            self.assertTrue(repo["hasIssuesEnabled"])
            r = query("api", "repos/example/inventory")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(json.loads(r.stdout)["has_issues"])
            r = query("auth", "status")
            self.assertEqual(r.returncode, 0, r.stderr)
            child = json.loads(query("issue", "view", "11").stdout)
            self.assertNotEqual(child["id"], child["number"])
            rejected = query(
                "api",
                "repos/example/inventory/issues/10/sub_issues",
                "-X",
                "POST",
                "-F",
                "sub_issue_id=" + str(child["number"]),
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(
                json.loads(
                    query("api", "repos/example/inventory/issues/10/sub_issues").stdout
                ),
                [],
            )
            r = query(
                "api",
                "repos/example/inventory/issues/10/sub_issues",
                "-X",
                "POST",
                "-F",
                "sub_issue_id=" + str(child["id"]),
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            linked = json.loads(
                query("api", "repos/example/inventory/issues/10/sub_issues").stdout
            )
            self.assertEqual([item["number"] for item in linked], [11])
            query(
                "api",
                "repos/example/inventory/issues/10/sub_issues",
                "-X",
                "POST",
                "-F",
                "sub_issue_id=" + str(child["id"]),
            )
            linked = json.loads(
                query("api", "repos/example/inventory/issues/10/sub_issues").stdout
            )
            self.assertEqual(len(linked), 1)
            self.assertNotEqual(
                query("repo", "view", "elsewhere/project").returncode, 0
            )
            self.assertNotEqual(query("api", "repos/elsewhere/project").returncode, 0)
