from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.sync_navigators import (
    NAVIGATOR_SKILLS,
    NavigatorSyncError,
    sync_navigators,
)

REPO_ROOT = Path(__file__).parents[1]


class SkillPackagingTests(unittest.TestCase):
    def test_only_root_system_skills_are_discoverable(self) -> None:
        skills_root = REPO_ROOT / "skills"
        self.assertEqual(
            {
                path.relative_to(skills_root).as_posix()
                for path in skills_root.rglob("SKILL.md")
            },
            {"note-system/SKILL.md", "work-system/SKILL.md"},
        )
        self.assertEqual(
            {path.name for path in skills_root.iterdir() if path.is_dir()},
            {"note-system", "work-system"},
        )

    def test_each_skill_navigates_when_installed_alone(self) -> None:
        scenarios = {
            "work-system": [
                ("start", "question"),
                ("resume", "question", "discovery"),
                ("move", "question", "discovery", "answer"),
                ("procedure", "tweak", "implementation", "testing"),
                ("format", "novel-work", "planning", "planning-artifacts"),
            ],
            "note-system": [
                ("start", "curate"),
                ("resume", "curate", "integration"),
                ("move", "curate", "integration", "ingest.acquisition"),
                ("procedure", "curate", "visual-preparation", "visual-sourcing"),
                ("format", "curate", "review", "completion-report"),
            ],
        }
        for name, commands in scenarios.items():
            with (
                self.subTest(skill=name),
                tempfile.TemporaryDirectory(prefix="standalone skill ") as temporary,
            ):
                root = Path(temporary)
                installed = root / name
                shutil.copytree(REPO_ROOT / "skills" / name, installed)
                self.assertFalse(
                    any(path.is_symlink() for path in installed.rglob("*"))
                )
                navigator = installed / "scripts" / "navigate.py"
                for arguments in [("--help",), *commands]:
                    result = subprocess.run(
                        [sys.executable, "-I", str(navigator), *arguments],
                        cwd=root,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertNotIn(str(REPO_ROOT), result.stdout)
                    if arguments == ("--help",):
                        self.assertIn(f"Navigate {name}", result.stdout)
                    elif arguments[0] in {"start", "resume", "move"}:
                        self.assertIn(str(navigator), result.stdout)
                    else:
                        self.assertTrue(result.stdout.strip())


class NavigatorGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        scripts = self.root / "scripts"
        scripts.mkdir()
        for filename in ("navigator_source.py", "sync_navigators.py"):
            shutil.copy2(REPO_ROOT / "scripts" / filename, scripts / filename)
        for name in NAVIGATOR_SKILLS:
            (self.root / "skills" / name).mkdir(parents=True)

    def test_generation_is_deterministic_and_repository_copies_are_current(
        self,
    ) -> None:
        changed = sync_navigators(self.root)
        self.assertEqual(len(changed), 2)
        self.assertEqual(changed[0].read_bytes(), changed[1].read_bytes())
        self.assertFalse(any(path.is_symlink() for path in changed))
        before = {path: path.stat().st_mtime_ns for path in changed}
        self.assertEqual(sync_navigators(self.root), ())
        self.assertEqual(sync_navigators(self.root, check=True), ())
        self.assertEqual(before, {path: path.stat().st_mtime_ns for path in changed})
        self.assertEqual(sync_navigators(REPO_ROOT, check=True), ())

    def test_check_reports_missing_or_stale_copies_without_writing(self) -> None:
        with self.assertRaisesRegex(NavigatorSyncError, "sync_navigators.py"):
            sync_navigators(self.root, check=True)
        self.assertFalse((self.root / "skills" / "work-system" / "scripts").exists())
        changed = sync_navigators(self.root)
        changed[0].write_text("stale\n", encoding="utf-8")
        changed[1].unlink()
        with self.assertRaisesRegex(NavigatorSyncError, "note-system.*work-system"):
            sync_navigators(self.root, check=True)
        self.assertEqual(changed[0].read_text(encoding="utf-8"), "stale\n")
        self.assertFalse(changed[1].exists())

    def test_source_changes_require_regeneration(self) -> None:
        targets = sync_navigators(self.root)
        source = self.root / "scripts" / "navigator_source.py"
        original = targets[0].read_bytes()
        source.write_bytes(source.read_bytes() + b"\n# Changed source.\n")
        with self.assertRaisesRegex(NavigatorSyncError, "stale"):
            sync_navigators(self.root, check=True)
        self.assertEqual(targets[0].read_bytes(), original)
        self.assertEqual(sync_navigators(self.root), targets)
        self.assertTrue(targets[0].read_bytes().endswith(b"# Changed source.\n"))

    def test_missing_source_and_symlink_targets_are_rejected(self) -> None:
        targets = sync_navigators(self.root)
        original = targets[0].read_bytes()
        source = self.root / "scripts" / "navigator_source.py"
        source.unlink()
        with self.assertRaisesRegex(NavigatorSyncError, "navigator source"):
            sync_navigators(self.root)
        self.assertEqual(targets[0].read_bytes(), original)
        shutil.copy2(REPO_ROOT / "scripts" / "navigator_source.py", source)
        targets[0].unlink()
        targets[0].symlink_to(targets[1])
        with self.assertRaisesRegex(NavigatorSyncError, "symlinked navigator"):
            sync_navigators(self.root)
        self.assertEqual(targets[1].read_bytes(), original)

    def test_cli_check_fails_without_writes_and_regeneration_repairs_it(self) -> None:
        command = [sys.executable, str(self.root / "scripts" / "sync_navigators.py")]
        result = subprocess.run([*command, "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("sync_navigators.py", result.stderr)
        self.assertFalse((self.root / "skills" / "work-system" / "scripts").exists())
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([*command, "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
