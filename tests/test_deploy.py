from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.deploy import STATE_FILENAME, DeploymentError, deploy

REPO_ROOT = Path(__file__).parents[1]


def write_skill(source_root: Path, name: str, body: str = "initial") -> None:
    skill_dir = source_root / "skills" / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {name}\n"
        "description: Use when testing deployment.\n"
        "---\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    metadata_dir = skill_dir / "agents"
    metadata_dir.mkdir()
    (metadata_dir / "openai.yaml").write_text(
        "interface:\n"
        f'  display_name: "{name.title()}"\n'
        '  short_description: "Deploy test skill metadata"\n'
        f'  default_prompt: "Use ${name} for deployment testing."\n'
        "policy:\n"
        "  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )


class DeployTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        temporary_root = Path(self.temporary_directory.name)
        self.source_root = temporary_root / "source"
        self.codex_home = temporary_root / "codex-home"
        (self.source_root / "config").mkdir(parents=True)
        (self.source_root / "config" / "global-agents.md").write_text(
            "global instructions\n",
            encoding="utf-8",
        )
        write_skill(self.source_root, "alpha")
        write_skill(self.source_root, "beta")

    def test_dry_run_reports_changes_without_writing(self) -> None:
        actions = deploy(self.source_root, self.codex_home, dry_run=True)

        self.assertIn("CREATE global AGENTS.md", actions)
        self.assertIn("INSTALL skill alpha", actions)
        self.assertIn("INSTALL skill beta", actions)
        self.assertFalse(self.codex_home.exists())

    def test_deploy_installs_instructions_skills_and_state(self) -> None:
        deploy(self.source_root, self.codex_home)

        self.assertEqual(
            (self.codex_home / "AGENTS.md").read_text(encoding="utf-8"),
            "global instructions\n",
        )
        self.assertTrue((self.codex_home / "skills" / "alpha" / "SKILL.md").is_file())
        state = json.loads(
            (self.codex_home / STATE_FILENAME).read_text(encoding="utf-8")
        )
        self.assertEqual(set(state), {"instructions_hash", "managed_skills", "version"})
        self.assertEqual(set(state["managed_skills"]), {"alpha", "beta"})
        self.assertEqual(state["version"], 1)

    def test_redeploy_updates_sources_and_removes_only_managed_skills(self) -> None:
        deploy(self.source_root, self.codex_home)
        unrelated = self.codex_home / "skills" / "unrelated"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep\n", encoding="utf-8")
        system_skill = self.codex_home / "skills" / ".system" / "built-in"
        system_skill.mkdir(parents=True)
        (system_skill / "keep.txt").write_text("keep\n", encoding="utf-8")

        (self.source_root / "config" / "global-agents.md").write_text(
            "updated instructions\n",
            encoding="utf-8",
        )
        shutil.rmtree(self.source_root / "skills" / "beta")
        (self.source_root / "skills" / "alpha" / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Use when testing deployment.\n"
            "---\n\n"
            "updated\n",
            encoding="utf-8",
        )

        actions = deploy(self.source_root, self.codex_home)

        self.assertIn("UPDATE global AGENTS.md", actions)
        self.assertIn("UPDATE skill alpha", actions)
        self.assertIn("REMOVE managed skill beta", actions)
        self.assertFalse((self.codex_home / "skills" / "beta").exists())
        self.assertTrue((unrelated / "keep.txt").is_file())
        self.assertTrue((system_skill / "keep.txt").is_file())

    def test_identical_redeploy_is_a_no_op(self) -> None:
        deploy(self.source_root, self.codex_home)

        self.assertEqual(deploy(self.source_root, self.codex_home), ())

    def test_invalid_skill_fails_before_writing(self) -> None:
        (self.source_root / "skills" / "alpha" / "SKILL.md").write_text(
            "---\nname: wrong-name\ndescription: Use when invalid.\n---\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(DeploymentError, "must match directory name"):
            deploy(self.source_root, self.codex_home)

        self.assertFalse(self.codex_home.exists())

    def test_corrupted_state_cannot_escape_skills_directory(self) -> None:
        self.codex_home.mkdir()
        (self.codex_home / STATE_FILENAME).write_text(
            json.dumps(
                {
                    "instructions_hash": None,
                    "managed_skills": {"../../outside": "hash"},
                    "version": 1,
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(DeploymentError, "Invalid managed skill name"):
            deploy(self.source_root, self.codex_home, dry_run=True)

    def test_symlinked_destinations_are_rejected(self) -> None:
        external = Path(self.temporary_directory.name) / "external"
        external.mkdir()
        self.codex_home.mkdir()
        (self.codex_home / "skills").symlink_to(external, target_is_directory=True)

        with self.assertRaisesRegex(DeploymentError, "symlinked skills destination"):
            deploy(self.source_root, self.codex_home, dry_run=True)

        (self.codex_home / "skills").unlink()
        (self.codex_home / "AGENTS.md").symlink_to(external / "missing")
        with self.assertRaisesRegex(DeploymentError, "instruction destination"):
            deploy(self.source_root, self.codex_home, dry_run=True)

    def test_unsafe_codex_home_targets_are_rejected(self) -> None:
        for unsafe_target in {
            Path("/"),
            Path.home(),
            self.source_root,
            self.source_root / "nested-codex-home",
        }:
            with (
                self.subTest(target=unsafe_target),
                self.assertRaisesRegex(DeploymentError, "Unsafe Codex home"),
            ):
                deploy(self.source_root, unsafe_target, dry_run=True)

    def test_unowned_skill_collision_requires_force(self) -> None:
        collision = self.codex_home / "skills" / "alpha"
        collision.mkdir(parents=True)
        (collision / "SKILL.md").write_text("unowned\n", encoding="utf-8")

        with self.assertRaisesRegex(DeploymentError, "unowned skill alpha"):
            deploy(self.source_root, self.codex_home)

        self.assertEqual(
            (collision / "SKILL.md").read_text(encoding="utf-8"), "unowned\n"
        )

    def test_unowned_instructions_require_force(self) -> None:
        self.codex_home.mkdir()
        destination = self.codex_home / "AGENTS.md"
        destination.write_text("unowned instructions\n", encoding="utf-8")

        with self.assertRaisesRegex(DeploymentError, "unowned AGENTS.md"):
            deploy(self.source_root, self.codex_home)

        self.assertEqual(
            destination.read_text(encoding="utf-8"), "unowned instructions\n"
        )
        actions = deploy(self.source_root, self.codex_home, force=True)
        self.assertIn("UPDATE global AGENTS.md", actions)

    def test_identical_unowned_instructions_are_adopted(self) -> None:
        self.codex_home.mkdir()
        destination = self.codex_home / "AGENTS.md"
        destination.write_text("global instructions\n", encoding="utf-8")

        actions = deploy(self.source_root, self.codex_home, dry_run=True)

        self.assertIn("ADOPT identical global AGENTS.md", actions)
        self.assertFalse((self.codex_home / STATE_FILENAME).exists())

    def test_locally_modified_managed_skill_requires_force(self) -> None:
        deploy(self.source_root, self.codex_home)
        destination = self.codex_home / "skills" / "alpha" / "SKILL.md"
        destination.write_text("locally modified\n", encoding="utf-8")
        (self.source_root / "skills" / "alpha" / "SKILL.md").write_text(
            "---\n"
            "name: alpha\n"
            "description: Use when testing deployment.\n"
            "---\n\n"
            "source changed\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(DeploymentError, "locally modified skill alpha"):
            deploy(self.source_root, self.codex_home)

        actions = deploy(self.source_root, self.codex_home, force=True)
        self.assertIn("UPDATE skill alpha", actions)
        self.assertIn("source changed", destination.read_text(encoding="utf-8"))

    def test_locally_modified_instructions_require_force(self) -> None:
        deploy(self.source_root, self.codex_home)
        destination = self.codex_home / "AGENTS.md"
        destination.write_text("local instructions\n", encoding="utf-8")
        (self.source_root / "config" / "global-agents.md").write_text(
            "source instructions\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(DeploymentError, "locally modified AGENTS.md"):
            deploy(self.source_root, self.codex_home)

        actions = deploy(self.source_root, self.codex_home, force=True)
        self.assertIn("UPDATE global AGENTS.md", actions)
        self.assertEqual(
            destination.read_text(encoding="utf-8"), "source instructions\n"
        )

    def test_cli_deploys_this_repository_to_an_isolated_home(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "deploy.py"),
                "--codex-home",
                str(self.codex_home),
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())
        self.assertEqual(
            {
                path.name
                for path in (self.codex_home / "skills").iterdir()
                if path.is_dir()
            },
            {path.name for path in (REPO_ROOT / "skills").iterdir() if path.is_dir()},
        )


if __name__ == "__main__":
    unittest.main()
