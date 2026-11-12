from __future__ import annotations

import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE / "skills/work-system/scripts"


class CompactionRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.project = self.directory / "project"
        self.project.mkdir()
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        self.home = self.directory / "application home"
        self.environment = {
            key: value
            for key, value in os.environ.items()
            if key not in {"CODEX_THREAD_ID", "CLAUDE_CODE_SESSION_ID"}
        }

    def command(
        self, script: str, *arguments: str, payload: object = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *arguments],
            cwd=self.project,
            env=self.environment,
            input=json.dumps(payload) if payload is not None else "",
            capture_output=True,
            text=True,
        )

    def seed(self, application: str, identifier: str, record: Path) -> Path:
        self.environment.update(
            {"CODEX_HOME": str(self.home), "CODEX_THREAD_ID": identifier}
            if application == "codex"
            else {
                "CLAUDE_CONFIG_DIR": str(self.home),
                "CLAUDE_CODE_SESSION_ID": identifier,
            }
        )
        result = self.command(
            "navigate.py", "start", "novel-work", "--record", str(record)
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.command("navigate.py", "substate", "enter", "wayfinding")
        self.assertEqual(result.returncode, 0, result.stderr)
        name = hashlib.sha256(identifier.encode()).hexdigest()
        return self.home / "work-system/state" / f"{name}.json"

    def recover(self, application: str, identifier: str) -> dict[str, object]:
        result = self.command(
            "compaction.py",
            "resume",
            "--application",
            application,
            "--config-home",
            str(self.home),
            payload={
                "hook_event_name": "SessionStart",
                "source": "compact",
                "session_id": identifier,
                "cwd": str(self.project),
            },
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        value: dict[str, object] = json.loads(result.stdout)
        return value

    def test_both_applications_restore_their_own_existing_record(self) -> None:
        for application in ("codex", "claude"):
            with self.subTest(application=application):
                self.environment.pop("CODEX_THREAD_ID", None)
                self.environment.pop("CLAUDE_CODE_SESSION_ID", None)
                record = self.project / f"{application}-status.md"
                record.write_text(
                    "Header-only empty export accepted. "
                    "Existing-file choice remains open.\n"
                )
                path = self.seed(application, application + "-one", record)
                before = path.read_bytes()
                # The event selects recovery despite an inherited conversation ID.
                self.environment["CODEX_THREAD_ID"] = "unrelated-conversation"
                output = self.recover(application, application + "-one")
                context = output["hookSpecificOutput"]
                self.assertIsInstance(context, dict)
                assert isinstance(context, dict)
                text = str(context["additionalContext"])
                self.assertIn(str(record), text)
                self.assertIn("wayfinding", text)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(
                    record.read_text(),
                    "Header-only empty export accepted. "
                    "Existing-file choice remains open.\n",
                )

    def test_damaged_state_reaches_the_agent_without_overwriting_it(self) -> None:
        path = self.seed("codex", "damaged", self.project / "status.md")
        path.write_text("{broken")
        output = self.recover("codex", "damaged")
        self.assertEqual(output["continue"], False)
        self.assertIn(str(path), str(output))
        self.assertEqual(path.read_text(), "{broken")
        self.assertFalse((self.project / "status.md").exists())

    def test_configuring_hooks_preserves_other_settings_and_is_idempotent(self) -> None:
        for application, filename in (
            ("codex", "hooks.json"),
            ("claude", "settings.json"),
        ):
            with self.subTest(application=application):
                self.home.mkdir(exist_ok=True)
                target = self.home / filename
                stop_hooks = [
                    {"hooks": [{"type": "command", "command": "existing-review"}]}
                ]
                existing = {
                    "permissions": {"allow": ["Read"]},
                    "hooks": {"Stop": stop_hooks},
                }
                target.write_text(json.dumps(existing))
                arguments = (
                    "configure",
                    "--application",
                    application,
                    "--config-home",
                    str(self.home),
                )
                result = self.command("compaction.py", *arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                first = target.read_bytes()
                updated = json.loads(first)
                self.assertEqual(updated["permissions"], existing["permissions"])
                self.assertEqual(updated["hooks"]["Stop"], stop_hooks)
                self.assertEqual(len(updated["hooks"]["SessionStart"]), 1)
                result = self.command("compaction.py", *arguments)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(target.read_bytes(), first)

    def test_generated_hooks_execute_with_documented_inputs(self) -> None:
        for application, filename in (
            ("codex", "hooks.json"),
            ("claude", "settings.json"),
        ):
            with self.subTest(application=application):
                self.environment.pop("CODEX_THREAD_ID", None)
                self.environment.pop("CLAUDE_CODE_SESSION_ID", None)
                record = self.project / (application + "-work.md")
                record.write_text("Review remains pending.\n")
                self.seed(application, application + "-session", record)
                result = self.command(
                    "compaction.py",
                    "configure",
                    "--application",
                    application,
                    "--config-home",
                    str(self.home),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                configuration = json.loads((self.home / filename).read_text())
                handler = configuration["hooks"]["SessionStart"][0]["hooks"][0]
                event = {
                    "session_id": application + "-session",
                    "cwd": str(self.project),
                    "source": "compact",
                    "hook_event_name": "SessionStart",
                }
                result = subprocess.run(
                    shlex.split(handler["command"]),
                    input=json.dumps(event),
                    text=True,
                    capture_output=True,
                    env=self.environment,
                    cwd=self.project,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                output = json.loads(result.stdout)
                self.assertIn(
                    str(record), output["hookSpecificOutput"]["additionalContext"]
                )

    def test_missing_state_does_not_create_a_work_record(self) -> None:
        output = self.recover("codex", "not-started")
        self.assertNotIn("continue", output)
        self.assertFalse(list(self.home.rglob("*.json")))
        self.assertEqual(list(self.project.iterdir()), [self.project / ".git"])

    def test_configuration_dry_run_writes_nothing(self) -> None:
        result = self.command(
            "compaction.py",
            "configure",
            "--application",
            "claude",
            "--config-home",
            str(self.home),
            "--dry-run",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SessionStart", json.loads(result.stdout)["hooks"])
        self.assertFalse(self.home.exists())

    def test_invalid_configuration_is_preserved(self) -> None:
        self.home.mkdir()
        target = self.home / "hooks.json"
        target.write_text("{invalid")
        result = self.command(
            "compaction.py",
            "configure",
            "--application",
            "codex",
            "--config-home",
            str(self.home),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(), "{invalid")


if __name__ == "__main__":
    unittest.main()
