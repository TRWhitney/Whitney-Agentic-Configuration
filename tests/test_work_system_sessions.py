from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

NAVIGATOR = (
    Path(__file__).resolve().parents[1] / "skills/work-system/scripts/navigate.py"
)


class WorkflowSessionTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.root = self.directory / "project"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.codex_home = self.directory / "codex-home"
        self.environment = {
            **os.environ,
            "CODEX_HOME": str(self.codex_home),
            "CODEX_THREAD_ID": "conversation-one",
            "CODEX_SESSION_ID": "shared-session",
        }

    def run_nav(self, *arguments: str, success: bool = True) -> str:
        result = subprocess.run(
            [sys.executable, str(NAVIGATOR), *arguments],
            cwd=self.root,
            env=self.environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return result.stdout if success else result.stderr

    def path(self, conversation: str = "conversation-one") -> Path:
        filename = hashlib.sha256(conversation.encode("utf-8")).hexdigest()
        return self.codex_home / "work-system/state" / f"{filename}.json"

    def progress(self, conversation: str = "conversation-one") -> dict[str, object]:
        value: dict[str, object] = json.loads(self.path(conversation).read_text())
        return value

    def make_commit(self, text: str) -> str:
        (self.root / "item.txt").write_text(text)
        self.git("add", "item.txt")
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-qm",
            text,
        )
        return self.git("rev-parse", "HEAD").strip()

    def git(self, *arguments: str) -> str:
        return subprocess.check_output(["git", *arguments], cwd=self.root, text=True)

    def test_commits_survive_completed_and_cancelled_workflows(self) -> None:
        commit = self.make_commit("first")
        self.run_nav("commit", "add", "HEAD")
        self.run_nav("start", "question")
        self.run_nav("move", "question", "discovery", "answer")
        self.run_nav("move", "question", "answer", "complete")
        self.assertIn(commit, self.run_nav("commit", "list"))
        self.assertNotIn("workflow", self.progress())
        self.assertIn("No active workflow", self.run_nav("resume"))
        self.run_nav("start", "tweak")
        self.run_nav("cancel")
        self.assertIn(commit, self.run_nav("commit", "list"))
        self.assertNotIn("workflow", self.progress())

    def test_amendment_replaces_saved_id_and_rejects_unknown_targets(self) -> None:
        before = self.make_commit("first")
        self.run_nav("commit", "add", before)
        self.run_nav("commit", "add", before)
        self.git(
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "--amend",
            "--allow-empty",
            "-qm",
            "amended",
        )
        after = self.git("rev-parse", "HEAD").strip()
        self.make_commit("later")
        self.run_nav("commit", "add", after, "--replaces", before)
        self.assertEqual(self.progress()["commits"], {str(self.root / ".git"): [after]})
        saved = self.path().read_bytes()
        self.run_nav("commit", "add", "missing", success=False)
        self.run_nav("commit", "add", "HEAD", "--replaces", "", success=False)
        self.run_nav("commit", "add", "HEAD", "--replaces", before, success=False)
        self.assertEqual(self.path().read_bytes(), saved)

    def test_commits_are_separate_by_repository_and_conversation(self) -> None:
        first = self.make_commit("first")
        self.run_nav("commit", "add", first)
        original = self.path().read_bytes()
        self.environment["CODEX_THREAD_ID"] = "conversation-two"
        self.assertNotIn(first, self.run_nav("commit", "list"))
        self.assertEqual(self.path().read_bytes(), original)
        self.environment["CODEX_THREAD_ID"] = "conversation-one"
        self.root = self.directory / "other"
        self.root.mkdir()
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        second = self.make_commit("second")
        self.assertNotIn(first, self.run_nav("commit", "list"))
        self.run_nav("commit", "add", second)
        listing = self.run_nav("commit", "list")
        self.assertIn(second, listing)
        self.assertNotIn(first, listing)
        self.assertFalse((self.root / ".work").exists())

    def test_damaged_commit_state_is_not_overwritten(self) -> None:
        self.make_commit("first")
        self.run_nav("start", "question")
        damaged = '{"commits": {"repo": ["not-a-hash"]}}'
        self.path().write_text(damaged)
        self.run_nav("commit", "list", success=False)
        self.run_nav("commit", "add", "HEAD", success=False)
        self.assertEqual(self.path().read_text(), damaged)

    def test_worktrees_share_commits_and_explicit_conversation_works(self) -> None:
        commit = self.make_commit("first")
        self.run_nav("commit", "add", "HEAD", "--conversation", "explicit")
        worktree = self.directory / "worktree"
        self.git("worktree", "add", "--detach", str(worktree))
        self.root = worktree
        self.assertIn(
            commit, self.run_nav("commit", "list", "--conversation", "explicit")
        )
        self.assertNotIn(commit, self.run_nav("commit", "list"))

    def test_failed_commit_replacement_preserves_existing_state(self) -> None:
        commit = self.make_commit("first")
        self.run_nav("start", "question")
        original = self.path().read_bytes()
        script = """
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import navigate
sys.argv = ['navigate.py', *sys.argv[2:]]
with patch('os.replace', side_effect=OSError('Cannot replace file')):
    raise SystemExit(navigate.main())
"""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                script,
                str(NAVIGATOR.parent),
                "commit",
                "add",
                commit,
            ],
            cwd=self.root,
            env=self.environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.path().read_bytes(), original)
        self.assertEqual(list(self.path().parent.glob("*.tmp")), [])

    def test_concurrent_commit_additions_keep_both_ids(self) -> None:
        first = self.make_commit("first")
        second = self.make_commit("second")
        processes = [
            subprocess.Popen(
                [sys.executable, str(NAVIGATOR), "commit", "add", commit],
                cwd=self.root,
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for commit in (first, second)
        ]
        for process in processes:
            _, error = process.communicate()
            self.assertEqual(process.returncode, 0, error)
        listing = self.run_nav("commit", "list")
        self.assertEqual(set(listing.splitlines()[1:]), {first, second})

    def test_squash_replaces_multiple_ids_and_keeps_other_commits(self) -> None:
        first = self.make_commit("first")
        second = self.make_commit("second")
        third = self.make_commit("third")
        for commit in (first, second, third):
            self.run_nav("commit", "add", commit)
        self.git("reset", "--soft", first)
        combined = self.make_commit("combined")
        self.run_nav(
            "commit", "add", combined, "--replaces", second, "--replaces", third
        )
        self.assertEqual(
            self.progress()["commits"], {str(self.root / ".git"): [first, combined]}
        )

    def test_reset_removes_discarded_ids_even_after_objects_are_pruned(self) -> None:
        first = self.make_commit("first")
        second = self.make_commit("second")
        third = self.make_commit("third")
        for commit in (first, second, third):
            self.run_nav("commit", "add", commit)
        self.git("reset", "--hard", first)
        self.git("reflog", "expire", "--expire=now", "--all")
        self.git("gc", "--prune=now")
        missing = subprocess.run(
            ["git", "cat-file", "-e", second], cwd=self.root, capture_output=True
        )
        self.assertNotEqual(missing.returncode, 0)
        self.run_nav("commit", "remove", second, third)
        self.assertEqual(self.progress()["commits"], {str(self.root / ".git"): [first]})

    def test_unknown_removal_keeps_the_complete_record_unchanged(self) -> None:
        first = self.make_commit("first")
        self.run_nav("commit", "add", first)
        self.run_nav("start", "question")
        original = self.path().read_bytes()
        self.run_nav("commit", "remove", first, "0" * 40, success=False)
        self.assertEqual(self.path().read_bytes(), original)

    def test_removing_all_ids_preserves_an_active_workflow(self) -> None:
        commit = self.make_commit("first")
        self.run_nav("commit", "add", commit)
        self.run_nav("start", "question")
        self.run_nav("commit", "remove", commit)
        self.assertEqual(
            self.progress(), {"workflow": "question", "state": "discovery"}
        )
        self.run_nav("cancel")
        self.run_nav("commit", "add", commit)
        self.run_nav("commit", "remove", commit)
        self.assertFalse(self.path().exists())

    def test_commit_commands_keep_an_explicit_conversation(self) -> None:
        self.make_commit("first")
        self.environment.pop("CODEX_THREAD_ID")
        self.run_nav("start", "tweak", "--conversation", "explicit")
        self.run_nav(
            "move", "tweak", "discovery", "implementation", "--conversation", "explicit"
        )
        self.run_nav(
            "move",
            "tweak",
            "implementation",
            "validation",
            "--conversation",
            "explicit",
        )
        output = self.run_nav(
            "move", "tweak", "validation", "delivery", "--conversation", "explicit"
        )
        self.assertIn("commit list --conversation explicit", output)
        self.assertIn("commit add '<commit>' --conversation explicit", output)
        self.assertIn("commit remove '<commit>' ... --conversation explicit", output)

    def test_minimal_progress_is_saved_outside_the_repository(self) -> None:
        self.run_nav("start", "novel-work")
        self.assertEqual(
            self.progress(), {"workflow": "novel-work", "state": "planning"}
        )
        self.assertFalse((self.root / ".git/work-system").exists())
        self.assertFalse((self.root / ".work").exists())

    def test_default_home_uses_the_same_location_without_configuration(self) -> None:
        self.environment.pop("CODEX_HOME")
        self.environment["HOME"] = str(self.directory)
        self.environment["USERPROFILE"] = str(self.directory)
        self.run_nav("start", "question")
        expected = self.directory / ".codex" / self.path().relative_to(self.codex_home)
        self.assertEqual(
            json.loads(expected.read_text()),
            {"workflow": "question", "state": "discovery"},
        )

    def test_restore_across_processes_and_read_named_guidance(self) -> None:
        self.run_nav("resume")
        self.run_nav("start", "novel-work", "--record", ".work/design/status.md")
        progress = self.progress()
        self.assertEqual(progress["record"], str(self.root / ".work/design/status.md"))
        restored = self.run_nav("resume")
        self.assertIn(str(progress["record"]), restored)
        self.run_nav("resume", "novel-work", "delivery")
        self.assertEqual(self.progress(), progress)
        self.run_nav("start", "novel-work", "--record", "https://example.com/issues/1")
        self.assertEqual(self.progress()["record"], "https://example.com/issues/1")
        self.assertIn("https://example.com/issues/1", self.run_nav("resume"))

    def test_substate_survives_research_and_restores_its_format(self) -> None:
        self.run_nav("start", "novel-work")
        self.run_nav("substate", "enter", "wayfinding")
        self.run_nav("procedure", "novel-work", "planning", "research")
        self.assertEqual(self.progress()["substate"], "wayfinding")
        restored = self.run_nav("resume")
        skill = NAVIGATOR.parent.parent
        guidance = skill / "references/substates/wayfinding.md"
        format_path = skill / "references/formats/wayfinding.md"
        self.assertIn(guidance.read_text().strip(), restored)
        self.assertIn(format_path.read_text().strip(), restored)
        self.run_nav("move", "novel-work", "planning", "implementation", success=False)
        self.run_nav("substate", "leave")
        self.assertNotIn("substate", self.progress())
        self.run_nav("move", "novel-work", "planning", "implementation")
        self.assertEqual(self.progress()["state"], "implementation")

    def test_invalid_commands_preserve_progress(self) -> None:
        self.run_nav("start", "novel-work")
        original = self.progress()
        self.run_nav("substate", "enter", "research", success=False)
        self.run_nav("move", "novel-work", "planning", "delivery", success=False)
        self.run_nav(
            "move", "novel-work", "implementation", "validation", success=False
        )
        self.run_nav("start", "question", success=False)
        self.assertEqual(self.progress(), original)

    def test_failed_file_replacement_keeps_progress_and_removes_temporary_data(
        self,
    ) -> None:
        self.run_nav("start", "novel-work")
        original = self.path().read_bytes()
        script = """
import sys
from unittest.mock import patch
sys.path.insert(0, sys.argv[1])
import navigate
sys.argv = ['navigate.py', 'move', 'novel-work', 'planning', 'implementation']
with patch('os.replace', side_effect=OSError('Cannot replace file')):
    raise SystemExit(navigate.main())
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(NAVIGATOR.parent)],
            cwd=self.root,
            env=self.environment,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(self.path().read_bytes(), original)
        self.assertEqual(list(self.path().parent.glob("*.tmp")), [])

    def test_conversations_in_the_same_directory_restore_independently(self) -> None:
        self.run_nav("start", "novel-work")
        self.run_nav("substate", "enter", "wayfinding")
        original = self.progress()
        self.environment["CODEX_THREAD_ID"] = "conversation-two"
        self.run_nav("start", "question")
        self.run_nav("move", "question", "discovery", "answer")
        self.assertEqual(self.progress("conversation-two")["state"], "answer")
        self.assertEqual(self.progress(), original)
        self.environment["CODEX_THREAD_ID"] = "conversation-one"
        self.assertIn("Planning:", self.run_nav("resume"))
        self.assertEqual(self.progress(), original)

    def test_conversation_files_stay_distinct_when_case_is_ignored(self) -> None:
        self.environment["CODEX_THREAD_ID"] = "Review"
        self.run_nav("start", "novel-work")
        self.environment["CODEX_THREAD_ID"] = "review"
        self.run_nav("start", "question")
        paths = list(self.path().parent.glob("*.json"))
        self.assertEqual(len({path.name.casefold() for path in paths}), 2)
        self.run_nav("cancel")
        self.environment["CODEX_THREAD_ID"] = "Review"
        self.run_nav("resume")
        self.run_nav("substate", "enter", "wayfinding")
        paths = list(self.path().parent.glob("*.json"))
        self.assertEqual(len(paths), 1)
        self.assertEqual(json.loads(paths[0].read_text())["substate"], "wayfinding")

    def test_completion_and_cancellation_remove_only_the_current_progress(self) -> None:
        self.run_nav("start", "question")
        self.environment["CODEX_THREAD_ID"] = "conversation-two"
        self.run_nav("start", "novel-work")
        other = self.progress("conversation-two")
        self.environment["CODEX_THREAD_ID"] = "conversation-one"
        self.run_nav("move", "question", "discovery", "answer")
        self.run_nav("move", "question", "answer", "complete")
        self.assertFalse(self.path().exists())
        self.run_nav("resume")
        self.assertFalse(self.path().exists())
        record = self.root / "status.md"
        record.write_text("Work in progress\n")
        self.run_nav("start", "novel-work", "--record", str(record))
        self.run_nav("cancel")
        self.assertFalse(self.path().exists())
        self.assertEqual(record.read_text(), "Work in progress\n")
        self.assertEqual(self.progress("conversation-two"), other)

    def test_missing_thread_id_never_selects_shared_or_other_progress(self) -> None:
        self.run_nav("start", "novel-work")
        original = self.progress()
        self.environment.pop("CODEX_THREAD_ID")
        self.assertIn("--conversation", self.run_nav("resume", success=False))
        self.run_nav("start", "question", success=False)
        self.assertEqual(self.progress(), original)
        self.assertFalse(self.path("shared-session").exists())

    def test_explicit_conversation_id_is_kept_in_continuation_commands(self) -> None:
        self.environment.pop("CODEX_THREAD_ID")
        output = self.run_nav("start", "novel-work", "--conversation", "explicit")
        self.assertIn("resume --conversation explicit", output)
        self.assertIn("substate enter wayfinding --conversation explicit", output)
        self.run_nav("substate", "enter", "wayfinding", "--conversation", "explicit")
        restored = self.run_nav("resume", "--conversation", "explicit")
        self.assertIn("Planning:", restored)

    def test_conversation_id_cannot_escape_the_state_directory(self) -> None:
        for identifier in ("../elsewhere", "", "nested/file", ".."):
            with self.subTest(identifier=identifier):
                self.run_nav(
                    "start", "question", "--conversation", identifier, success=False
                )
        self.assertFalse(self.path().exists())

    def test_invalid_progress_is_preserved_and_other_conversations_can_resume(
        self,
    ) -> None:
        self.run_nav("start", "novel-work")
        self.path().write_text("{")
        output = self.run_nav("resume", success=False)
        guidance = NAVIGATOR.parent.parent / "references/providers/local/record.md"
        self.assertIn(str(guidance), output)
        self.run_nav("start", "novel-work", success=False)
        self.assertEqual(self.path().read_text(), "{")
        self.environment["CODEX_THREAD_ID"] = "conversation-two"
        self.run_nav("start", "question")
        self.run_nav("resume")
        self.assertEqual(self.progress("conversation-two")["state"], "discovery")

    def test_invalid_fields_or_states_preserve_the_file(self) -> None:
        self.run_nav("start", "novel-work")
        for change in (
            {"version": 99},
            {"state": "missing"},
            {"workflow": "missing"},
            {"substate": "missing"},
            {"record": 1},
        ):
            with self.subTest(change=change):
                value = {"workflow": "novel-work", "state": "planning", **change}
                self.path().write_text(json.dumps(value))
                before = self.path().read_bytes()
                output = self.run_nav("resume", success=False)
                guidance = (
                    NAVIGATOR.parent.parent / "references/providers/local/record.md"
                )
                self.assertIn(str(guidance), output)
                self.assertEqual(self.path().read_bytes(), before)

    def test_failed_restore_uses_the_selected_tracker_record_guidance(self) -> None:
        settings = self.root / ".git/work-system.json"
        settings.write_text(
            json.dumps({"tracker": "github", "repository": "example/inventory"})
        )
        original_settings = settings.read_bytes()
        self.run_nav("start", "novel-work")
        damaged = '{"workflow": "missing", "state": "planning"}'
        self.path().write_text(damaged)
        output = self.run_nav("resume", success=False)
        guidance = NAVIGATOR.parent.parent / "references/providers/github/record.md"
        self.assertEqual(output.count(str(guidance)), 1)
        self.assertNotIn("references/providers/local/record.md", output)
        self.assertEqual(settings.read_bytes(), original_settings)
        self.assertEqual(self.path().read_text(), damaged)
        self.assertFalse((self.root / ".work").exists())

    def test_unreadable_state_returns_guidance_without_changing_its_bytes(self) -> None:
        self.run_nav("start", "novel-work")
        self.path().write_bytes(b"\xff")
        output = self.run_nav("resume", success=False)
        guidance = NAVIGATOR.parent.parent / "references/providers/local/record.md"
        self.assertIn(str(guidance), output)
        self.assertIn(str(self.path()), output)
        self.assertEqual(self.path().read_bytes(), b"\xff")

    def test_concurrent_conversations_do_not_overwrite_progress(self) -> None:
        processes = [
            subprocess.Popen(
                [sys.executable, str(NAVIGATOR), "start", "question"],
                cwd=self.root,
                env={**self.environment, "CODEX_THREAD_ID": f"conversation-{number}"},
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for number in range(4)
        ]
        for process in processes:
            _, errors = process.communicate(timeout=15)
            self.assertEqual(process.returncode, 0, errors)
        for number in range(4):
            self.assertEqual(
                self.progress(f"conversation-{number}")["state"], "discovery"
            )

    def test_concurrent_starts_in_one_conversation_preserve_one_workflow(self) -> None:
        processes = [
            subprocess.Popen(
                [sys.executable, str(NAVIGATOR), "start", workflow],
                cwd=self.root,
                env=self.environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for workflow in ("question", "novel-work")
        ]
        for process in processes:
            process.communicate(timeout=15)
        self.assertEqual(sorted(process.returncode for process in processes), [0, 2])
        self.assertIn(self.progress()["workflow"], {"question", "novel-work"})

    def test_subdirectories_and_worktrees_keep_conversation_progress(self) -> None:
        self.run_nav("start", "novel-work", "--record", "status.md")
        original = self.progress()
        primary = self.root
        self.root = primary / "child"
        self.root.mkdir()
        self.assertIn(str(primary / "status.md"), self.run_nav("resume"))
        self.assertEqual(self.progress(), original)
        subprocess.run(
            [
                "git",
                "-C",
                str(primary),
                "-c",
                "user.name=Test",
                "-c",
                "user.email=test@example.com",
                "commit",
                "--allow-empty",
                "-qm",
                "Initial",
            ],
            check=True,
        )
        self.root = self.directory / "other"
        subprocess.run(
            [
                "git",
                "-C",
                str(primary),
                "worktree",
                "add",
                "-qb",
                "other",
                str(self.root),
            ],
            check=True,
            capture_output=True,
        )
        self.run_nav("resume")
        self.environment["CODEX_THREAD_ID"] = "conversation-two"
        self.run_nav("start", "question")
        self.assertEqual(self.progress(), original)
        self.assertFalse((primary / ".git/work-system").exists())

    def test_non_git_progress_is_external_and_uses_ancestor_settings(self) -> None:
        self.root = self.directory / "without-git"
        self.root.mkdir()
        self.run_nav("start", "novel-work")
        self.assertFalse((self.root / ".work").exists())
        settings = self.root / ".work/project.json"
        settings.parent.mkdir()
        settings.write_text(json.dumps({"tracker": "local"}))
        self.root = self.root / "child"
        self.root.mkdir()
        self.assertIn(str(settings), self.run_nav("resume"))
        self.assertEqual(self.progress()["state"], "planning")
        settings.write_text("{")
        self.run_nav("resume", success=False)

    def test_inspecting_github_does_not_select_it(self) -> None:
        self.run_nav("start", "novel-work")
        self.run_nav("provider", "novel-work", "planning", "github")
        self.assertFalse((self.root / ".git/work-system.json").exists())
        self.assertIn("Tracker: `local`", self.run_nav("resume"))
        self.run_nav("procedure", "novel-work", "planning", "publish", success=False)
        (self.root / ".git/work-system.json").write_text(
            json.dumps({"tracker": "github", "repository": "owner/repo"})
        )
        self.run_nav("procedure", "novel-work", "planning", "publish")
        self.assertIn("Tracker: `github`", self.run_nav("resume"))

    def test_local_planning_does_not_require_document_delivery(self) -> None:
        self.run_nav("start", "novel-work")
        for procedure in ("review", "commit", "publish"):
            self.run_nav(
                "procedure", "novel-work", "planning", procedure, success=False
            )
        self.run_nav("move", "novel-work", "planning", "implementation")
        self.assertEqual(self.progress()["state"], "implementation")

    def _start_wayfinding_for_reply(self) -> bytes:
        self.run_nav("start", "novel-work")
        self.run_nav("substate", "enter", "wayfinding")
        return self.path().read_bytes()

    def _reply_arguments(self, ready: str = "1") -> tuple[str, ...]:
        return (
            "reply",
            "--decided",
            "2",
            "--ready",
            ready,
            "--unspecified",
            "destination",
            "--body",
            "Refusal protects saved files.",
        )

    def test_reply_preserves_navigation_and_contains_question(self) -> None:
        before = self._start_wayfinding_for_reply()
        out = self.run_nav(
            *self._reply_arguments(), "--question", "Should export refuse?"
        )
        self.assertTrue(
            out.startswith("Planning: 2 decided, 1 ready, unspecified: destination")
        )
        self.assertIn("Refusal protects saved files.", out)
        self.assertTrue(out.rstrip().endswith("Should export refuse?"))
        self.assertEqual(self.path().read_bytes(), before)

    def test_reply_requires_an_ending_mode(self) -> None:
        before = self._start_wayfinding_for_reply()
        self.run_nav(*self._reply_arguments(), success=False)
        self.assertEqual(self.path().read_bytes(), before)

    def test_blocked_reply_has_no_invented_question(self) -> None:
        before = self._start_wayfinding_for_reply()
        out = self.run_nav(
            *self._reply_arguments("0"), "--blocked-by", "The source is unavailable."
        )
        self.assertIn("0 ready", out)
        self.assertTrue(out.rstrip().endswith("The source is unavailable."))
        self.assertEqual(self.path().read_bytes(), before)

    def test_contradictory_and_blank_fields_are_rejected(self) -> None:
        before = self._start_wayfinding_for_reply()
        self.run_nav(
            *self._reply_arguments("0"),
            "--question",
            "Should export refuse?",
            success=False,
        )
        self.run_nav(
            *self._reply_arguments(), "--blocked-by", "Unavailable.", success=False
        )
        self.run_nav(
            *self._reply_arguments("-1"),
            "--question",
            "Should export refuse?",
            success=False,
        )
        self.run_nav(*self._reply_arguments(), "--question", "   ", success=False)
        self.assertEqual(self.path().read_bytes(), before)

    def test_reply_rejects_unavailable_saved_substate(self) -> None:
        self.run_nav("start", "question")
        state = self.progress()
        state["substate"] = "wayfinding"
        self.path().write_text(json.dumps(state))
        before = self.path().read_bytes()
        self.run_nav(
            *self._reply_arguments(),
            "--question",
            "Should export refuse?",
            success=False,
        )
        self.assertEqual(self.path().read_bytes(), before)

    def test_requested_recap_preserves_progress_without_another_question(self) -> None:
        before = self._start_wayfinding_for_reply()
        out = self.run_nav(*self._reply_arguments(), "--recap")
        self.assertTrue(out.startswith("Planning: 2 decided, 1 ready,"))
        self.assertTrue(out.rstrip().endswith("Refusal protects saved files."))
        self.assertEqual(self.path().read_bytes(), before)

    def test_reply_requires_wayfinding(self) -> None:
        self.run_nav(
            *self._reply_arguments(),
            "--question",
            "Should export refuse?",
            success=False,
        )
        self.run_nav("start", "novel-work")
        before = self.path().read_bytes()
        self.run_nav(
            *self._reply_arguments(),
            "--question",
            "Should export refuse?",
            success=False,
        )
        self.assertEqual(self.path().read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
