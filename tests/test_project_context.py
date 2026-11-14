from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

NAVIGATOR = (
    Path(__file__).resolve().parents[1] / "skills/work-system/scripts/navigate.py"
)


class ProjectContextTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / "application"
        self.root.mkdir()
        self.cwd = self.root
        self.home = self.directory / "agent-home"
        self.environment = {
            **os.environ,
            "CODEX_HOME": str(self.home),
            "CODEX_THREAD_ID": "project-context",
        }
        self.git("init", "-q")

    def git(self, *arguments: str) -> str:
        return subprocess.check_output(
            ["git", *arguments], cwd=self.root, text=True, stderr=subprocess.PIPE
        )

    def write(self, name: str, text: str) -> Path:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def nav(self, *arguments: str, success: bool = True) -> str:
        result = subprocess.run(
            [sys.executable, str(NAVIGATOR), *arguments],
            cwd=self.cwd,
            env=self.environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return result.stdout if success else result.stderr

    def test_default_record_is_found_from_nested_directory_without_writes(self) -> None:
        record = self.write("docs/project.md", "# Agreed project\n")
        self.cwd = self.root / "src/deeper"
        self.cwd.mkdir(parents=True)
        self.assertIn(str(record), self.nav("project"))
        self.assertFalse(self.home.exists())
        self.assertIn(str(record), self.nav("resume"))
        self.assertFalse((self.root / ".work").exists())
        self.assertEqual(list(self.home.rglob("*.json")), [])

    def test_absent_record_allows_work_without_creating_documents(self) -> None:
        self.assertIn(str(self.root / "docs/project.md"), self.nav("project"))
        output = self.nav("start", "fix")
        self.assertIn(str(self.root / "docs/project.md"), output)
        self.assertFalse((self.root / "docs").exists())
        self.assertFalse((self.root / ".work").exists())

    def test_lookup_preserves_document_tracker_and_active_workflow(self) -> None:
        record = self.write("docs/project.md", "# Agreed Linux application\n")
        settings = self.write(
            ".git/work-system.json", '{"tracker": "local", "extra": 7}\n'
        )
        self.nav("start", "novel-work", "--record", ".work/change/status.md")
        states = self.home / "work-system/state"
        before = {path.name: path.read_bytes() for path in states.iterdir()}
        original_settings = settings.read_bytes()
        self.assertIn(str(record), self.nav("project"))
        self.assertEqual(settings.read_bytes(), original_settings)
        self.assertEqual(record.read_text(), "# Agreed Linux application\n")
        self.assertEqual(
            {path.name: path.read_bytes() for path in states.iterdir()}, before
        )
        self.assertFalse((self.root / ".work").exists())

    def test_github_lookup_preserves_tracking_without_local_metadata(self) -> None:
        record = self.write("docs/project.md", "# Shared project agreements\n")
        settings = self.write(
            ".git/work-system.json",
            '{"tracker":"github","repository":"example/application"}\n',
        )
        before = settings.read_bytes()
        self.environment.pop("CODEX_THREAD_ID", None)
        self.environment.pop("CODEX_SESSION_ID", None)
        self.assertIn(str(record), self.nav("project"))
        self.assertFalse(self.home.exists())
        output = self.nav("start", "novel-work", "--conversation", "github-project")
        self.assertIn(str(record), output)
        self.assertIn("Tracker: `github`", output)
        self.assertEqual(settings.read_bytes(), before)
        self.assertFalse((self.root / ".work").exists())

    def test_worktree_uses_its_own_record_and_shared_tracker_settings(self) -> None:
        self.write("docs/project.md", "# Agreed application\n")
        settings = self.write(".git/work-system.json", '{"tracker":"local"}\n')
        self.git("add", "docs/project.md")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            "Project agreements",
        )
        worktree = self.directory / "worktree"
        self.git("worktree", "add", "-q", "-b", "other", str(worktree), "HEAD")
        self.cwd = worktree
        output = self.nav("start", "tweak")
        self.assertIn(str(worktree / "docs/project.md"), output)
        self.assertIn(str(settings), output)

    def test_non_git_project_uses_ancestor_settings_without_changing_them(self) -> None:
        shutil.rmtree(self.root / ".git")
        record = self.write("docs/project.md", "# Standalone application\n")
        settings = self.write(".work/project.json", '{"tracker":"local","extra":9}')
        before = settings.read_bytes()
        self.cwd = self.root / "src/nested"
        self.cwd.mkdir(parents=True)
        self.assertIn(str(record), self.nav("project"))
        self.assertIn(str(record), self.nav("start", "question"))
        self.assertEqual(settings.read_bytes(), before)

    def test_subagent_workflow_receives_the_same_project_reference(self) -> None:
        record = self.write("docs/project.md", "# Shared requirements\n")
        self.assertIn(str(record), self.nav("start", "subagent-implementation"))
        self.assertIn(str(record), self.nav("resume"))

    def test_non_git_default_record_and_settings_use_the_same_root(self) -> None:
        shutil.rmtree(self.root / ".git")
        record = self.write("docs/project.md", "# Standalone application\n")
        self.cwd = self.root / "src/nested"
        self.cwd.mkdir(parents=True)
        output = self.nav("start", "tweak")
        self.assertIn(str(record), output)
        self.assertIn(str(self.root / ".work/project.json"), output)

    def test_hooks_restore_project_and_work_references_without_state_changes(
        self,
    ) -> None:
        record = self.write("docs/project.md", "# Shared requirements\n")
        work = self.write(".work/change/status.md", "# Current change\n")
        self.nav("start", "novel-work", "--record", str(work))
        states = self.home / "work-system/state"
        before = {path.name: path.read_bytes() for path in states.iterdir()}
        for application in ("codex", "claude"):
            with self.subTest(application=application):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(NAVIGATOR.with_name("compaction.py")),
                        "resume",
                        "--application",
                        application,
                        "--config-home",
                        str(self.home),
                    ],
                    cwd=self.root,
                    env=self.environment,
                    input=json.dumps(
                        {
                            "hook_event_name": "SessionStart",
                            "source": "compact",
                            "session_id": "project-context",
                            "cwd": str(self.root),
                        }
                    ),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                context = json.loads(result.stdout)["hookSpecificOutput"][
                    "additionalContext"
                ]
                self.assertIn(str(record), context)
                self.assertIn(str(work), context)
                self.assertEqual(
                    {path.name: path.read_bytes() for path in states.iterdir()}, before
                )

    def test_project_planning_is_exposed_through_the_procedure_list(self) -> None:
        output = self.nav("start", "novel-work")
        self.assertIn("procedure novel-work planning project-planning", output)
        self.nav("procedure", "novel-work", "planning", "project-planning")
        self.nav(
            "format",
            "novel-work",
            "planning",
            "project-records",
            "--procedure",
            "project-planning",
        )
        self.assertIn(
            "procedure novel-work planning project-planning",
            self.nav("substate", "enter", "wayfinding"),
        )
