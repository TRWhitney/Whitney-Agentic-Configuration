from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from scripts.deploy import STATE_FILENAME, DeploymentError, deploy, main, purge_skills
from scripts.sync_navigators import sync_navigators

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


def run_git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "protocol.file.allow=always",
            "-c",
            "user.name=Deploy Tests",
            "-c",
            "user.email=deploy-tests@example.com",
            *arguments,
        ],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
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

    def configure_external_unslop(self, body: str = "external initial") -> Path:
        upstream = Path(self.temporary_directory.name) / "pstack"
        upstream.mkdir()
        run_git(upstream, "init", "--initial-branch=main")
        skill = upstream / "skills" / "unslop"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\n"
            "name: unslop\n"
            "description: Remove AI tells from writing.\n"
            "---\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Initial external skill")

        (self.source_root / "config" / "external-skills.json").write_text(
            json.dumps(
                {
                    "unslop": {
                        "path": "skills/unslop",
                        "submodule": "external/pstack",
                    }
                }
            ),
            encoding="utf-8",
        )
        run_git(self.source_root, "init", "--initial-branch=main")
        run_git(self.source_root, "add", ".")
        run_git(self.source_root, "commit", "-m", "Initial sources")
        run_git(
            self.source_root,
            "submodule",
            "add",
            "--branch",
            "main",
            str(upstream),
            "external/pstack",
        )
        run_git(self.source_root, "add", ".gitmodules", "external/pstack")
        run_git(self.source_root, "commit", "-m", "Reference external skills")
        return upstream

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

    def test_deploy_installs_a_skill_from_a_git_submodule(self) -> None:
        self.configure_external_unslop()

        actions = deploy(self.source_root, self.codex_home)

        self.assertIn("INSTALL skill unslop", actions)
        installed = self.codex_home / "skills" / "unslop" / "SKILL.md"
        self.assertIn("external initial", installed.read_text(encoding="utf-8"))
        state = json.loads(
            (self.codex_home / STATE_FILENAME).read_text(encoding="utf-8")
        )
        self.assertIn("unslop", state["managed_skills"])

    def test_purge_removes_an_installed_external_skill(self) -> None:
        self.configure_external_unslop()
        deploy(self.source_root, self.codex_home)

        actions = purge_skills(self.source_root, self.codex_home)

        self.assertIn("REMOVE managed skill unslop", actions)
        self.assertFalse((self.codex_home / "skills" / "unslop").exists())

    def test_update_external_skills_advances_and_deploys_the_submodule(self) -> None:
        upstream = self.configure_external_unslop()
        deploy(self.source_root, self.codex_home)
        upstream_skill = upstream / "skills" / "unslop" / "SKILL.md"
        upstream_skill.write_text(
            upstream_skill.read_text(encoding="utf-8").replace(
                "external initial", "external updated"
            ),
            encoding="utf-8",
        )
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Update external skill")

        actions = deploy(
            self.source_root,
            self.codex_home,
            update_external_skills=True,
        )

        self.assertIn("UPDATE external source external/pstack", actions)
        self.assertIn("UPDATE skill unslop", actions)
        installed = self.codex_home / "skills" / "unslop" / "SKILL.md"
        self.assertIn("external updated", installed.read_text(encoding="utf-8"))
        self.assertEqual(
            run_git(
                self.source_root / "external" / "pstack", "rev-parse", "HEAD"
            ).stdout,
            run_git(upstream, "rev-parse", "HEAD").stdout,
        )

    def test_external_update_dry_run_does_not_move_the_submodule(self) -> None:
        upstream = self.configure_external_unslop()
        deploy(self.source_root, self.codex_home)
        submodule = self.source_root / "external" / "pstack"
        original_revision = run_git(submodule, "rev-parse", "HEAD").stdout
        upstream_skill = upstream / "skills" / "unslop" / "SKILL.md"
        upstream_skill.write_text(
            upstream_skill.read_text(encoding="utf-8").replace(
                "external initial", "external updated"
            ),
            encoding="utf-8",
        )
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Update external skill")

        actions = deploy(
            self.source_root,
            self.codex_home,
            dry_run=True,
            update_external_skills=True,
        )

        self.assertIn("UPDATE skill unslop", actions)
        self.assertEqual(
            run_git(submodule, "rev-parse", "HEAD").stdout, original_revision
        )
        installed = self.codex_home / "skills" / "unslop" / "SKILL.md"
        self.assertIn("external initial", installed.read_text(encoding="utf-8"))

    def test_normal_dry_run_uses_the_pinned_submodule_revision(self) -> None:
        upstream = self.configure_external_unslop()
        deploy(self.source_root, self.codex_home)
        pinned_revision = run_git(
            self.source_root / "external" / "pstack", "rev-parse", "HEAD"
        ).stdout
        upstream_skill = upstream / "skills" / "unslop" / "SKILL.md"
        upstream_skill.write_text(
            upstream_skill.read_text(encoding="utf-8").replace(
                "external initial", "external updated"
            ),
            encoding="utf-8",
        )
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Update external skill")
        run_git(
            self.source_root,
            "submodule",
            "update",
            "--remote",
            "--checkout",
            "--",
            "external/pstack",
        )

        actions = deploy(self.source_root, self.codex_home, dry_run=True)

        self.assertNotIn("UPDATE skill unslop", actions)
        self.assertEqual(
            run_git(
                self.source_root / "external" / "pstack", "rev-parse", "HEAD"
            ).stdout,
            run_git(upstream, "rev-parse", "HEAD").stdout,
        )
        self.assertNotEqual(
            run_git(upstream, "rev-parse", "HEAD").stdout,
            pinned_revision,
        )

    def test_external_update_reports_a_submodule_only_change(self) -> None:
        upstream = self.configure_external_unslop()
        deploy(self.source_root, self.codex_home)
        (upstream / "unrelated.txt").write_text("updated\n", encoding="utf-8")
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Update unrelated content")

        actions = deploy(
            self.source_root,
            self.codex_home,
            dry_run=True,
            update_external_skills=True,
        )

        self.assertIn("UPDATE external source external/pstack", actions)
        self.assertNotIn("UPDATE skill unslop", actions)

    def test_external_skill_cannot_escape_through_an_ancestor_symlink(self) -> None:
        upstream = self.configure_external_unslop()
        outside = Path(self.temporary_directory.name) / "outside"
        outside_skill = outside / "unslop"
        outside_skill.mkdir(parents=True)
        (outside_skill / "SKILL.md").write_text(
            "---\nname: unslop\ndescription: Escaped test skill.\n---\n\nescaped\n",
            encoding="utf-8",
        )
        (upstream / "escape").symlink_to(outside, target_is_directory=True)
        run_git(upstream, "add", ".")
        run_git(upstream, "commit", "-m", "Add escaping skill path")
        manifest = self.source_root / "config" / "external-skills.json"
        manifest.write_text(
            json.dumps(
                {
                    "unslop": {
                        "path": "escape/unslop",
                        "submodule": "external/pstack",
                    }
                }
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(DeploymentError, "symlinked external skill path"):
            deploy(
                self.source_root,
                self.codex_home,
                dry_run=True,
                update_external_skills=True,
            )

    def test_dry_run_reads_an_uninitialized_submodule_without_initializing_it(
        self,
    ) -> None:
        self.configure_external_unslop()
        run_git(self.source_root, "submodule", "deinit", "--force", "external/pstack")
        submodule_skill = self.source_root / "external" / "pstack" / "skills" / "unslop"
        self.assertFalse(submodule_skill.exists())

        actions = deploy(self.source_root, self.codex_home, dry_run=True)

        self.assertIn("INSTALL skill unslop", actions)
        self.assertFalse(submodule_skill.exists())
        self.assertFalse(self.codex_home.exists())

    def test_purge_removes_only_managed_skills_and_preserves_instructions(
        self,
    ) -> None:
        deploy(self.source_root, self.codex_home)
        instructions = self.codex_home / "AGENTS.md"
        instructions.write_text("locally edited instructions\n", encoding="utf-8")
        unrelated = self.codex_home / "skills" / "unrelated"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("keep\n", encoding="utf-8")
        system_skill = self.codex_home / "skills" / ".system" / "built-in"
        system_skill.mkdir(parents=True)
        (system_skill / "keep.txt").write_text("keep\n", encoding="utf-8")

        actions = purge_skills(self.source_root, self.codex_home)

        self.assertEqual(
            actions,
            ("REMOVE managed skill alpha", "REMOVE managed skill beta"),
        )
        self.assertFalse((self.codex_home / "skills" / "alpha").exists())
        self.assertFalse((self.codex_home / "skills" / "beta").exists())
        self.assertTrue((unrelated / "keep.txt").is_file())
        self.assertTrue((system_skill / "keep.txt").is_file())
        self.assertEqual(
            instructions.read_text(encoding="utf-8"), "locally edited instructions\n"
        )
        state = json.loads(
            (self.codex_home / STATE_FILENAME).read_text(encoding="utf-8")
        )
        self.assertEqual(state["managed_skills"], {})
        self.assertIsInstance(state["instructions_hash"], str)

    def test_purge_dry_run_reports_removals_without_writing(self) -> None:
        deploy(self.source_root, self.codex_home)
        state_before = (self.codex_home / STATE_FILENAME).read_text(encoding="utf-8")

        actions = purge_skills(self.source_root, self.codex_home, dry_run=True)

        self.assertEqual(
            actions,
            ("REMOVE managed skill alpha", "REMOVE managed skill beta"),
        )
        self.assertTrue((self.codex_home / "skills" / "alpha").is_dir())
        self.assertTrue((self.codex_home / "skills" / "beta").is_dir())
        self.assertEqual(
            (self.codex_home / STATE_FILENAME).read_text(encoding="utf-8"),
            state_before,
        )

    def test_purge_requires_force_for_a_locally_modified_managed_skill(
        self,
    ) -> None:
        deploy(self.source_root, self.codex_home)
        first_skill = self.codex_home / "skills" / "alpha"
        modified_skill = self.codex_home / "skills" / "beta"
        (modified_skill / "SKILL.md").write_text("locally modified\n", encoding="utf-8")

        with self.assertRaisesRegex(
            DeploymentError, "locally modified managed skill beta"
        ):
            purge_skills(self.source_root, self.codex_home)

        self.assertTrue(first_skill.is_dir())
        self.assertTrue(modified_skill.is_dir())
        actions = purge_skills(self.source_root, self.codex_home, force=True)
        self.assertIn("REMOVE managed skill beta", actions)
        self.assertFalse(first_skill.exists())
        self.assertFalse(modified_skill.exists())

    def test_purge_rejects_the_repository_as_a_codex_home(self) -> None:
        with self.assertRaisesRegex(DeploymentError, "Unsafe Codex home"):
            purge_skills(self.source_root, self.source_root, dry_run=True)

    def test_purge_rejects_symlinked_managed_skill_content(self) -> None:
        deploy(self.source_root, self.codex_home)
        external = Path(self.temporary_directory.name) / "external"
        external.mkdir()
        (self.codex_home / "skills" / "alpha" / "linked").symlink_to(
            external, target_is_directory=True
        )

        with self.assertRaisesRegex(DeploymentError, "symlinked source or target"):
            purge_skills(self.source_root, self.codex_home, force=True)

        self.assertTrue((self.codex_home / "skills" / "alpha").is_dir())
        self.assertTrue((self.codex_home / "skills" / "beta").is_dir())

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

    def test_main_deploys_an_isolated_repository_to_an_isolated_home(self) -> None:
        self.configure_external_unslop()
        output = StringIO()

        with redirect_stdout(output):
            return_code = main(
                ["--codex-home", str(self.codex_home)],
                repository_root=self.source_root,
            )

        self.assertEqual(return_code, 0, output.getvalue())
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())
        self.assertEqual(
            {
                path.name
                for path in (self.codex_home / "skills").iterdir()
                if path.is_dir()
            },
            {"alpha", "beta", "unslop"},
        )

    def test_deploy_rejects_stale_navigators_before_writing_even_with_force(
        self,
    ) -> None:
        scripts = self.source_root / "scripts"
        scripts.mkdir()
        shutil.copy2(REPO_ROOT / "scripts" / "navigator_source.py", scripts)
        write_skill(self.source_root, "work-system")
        targets = sync_navigators(self.source_root)
        deploy(self.source_root, self.codex_home)
        before = {
            path.relative_to(self.codex_home): path.read_bytes()
            for path in self.codex_home.rglob("*")
            if path.is_file()
        }
        (self.source_root / "config" / "global-agents.md").write_text(
            "new instructions\n"
        )
        targets[0].write_text("stale navigator\n")
        for dry_run in (False, True):
            for force in (False, True):
                with (
                    self.subTest(dry_run=dry_run, force=force),
                    self.assertRaisesRegex(DeploymentError, "sync_navigators.py"),
                ):
                    deploy(
                        self.source_root,
                        self.codex_home,
                        dry_run=dry_run,
                        force=force,
                    )
        self.assertEqual(
            before,
            {
                path.relative_to(self.codex_home): path.read_bytes()
                for path in self.codex_home.rglob("*")
                if path.is_file()
            },
        )
        self.assertEqual(targets[0].read_text(), "stale navigator\n")

    def test_deploy_requires_navigator_source_and_copy_but_purge_does_not(self) -> None:
        write_skill(self.source_root, "note-system")
        with self.assertRaisesRegex(DeploymentError, "navigator source"):
            deploy(self.source_root, self.codex_home)
        self.assertFalse(self.codex_home.exists())
        scripts = self.source_root / "scripts"
        scripts.mkdir()
        shutil.copy2(REPO_ROOT / "scripts" / "navigator_source.py", scripts)
        with self.assertRaisesRegex(DeploymentError, "Missing or stale"):
            deploy(self.source_root, self.codex_home)
        self.assertFalse(self.codex_home.exists())
        sync_navigators(self.source_root)
        deploy(self.source_root, self.codex_home)
        shutil.rmtree(scripts)
        actions = purge_skills(self.source_root, self.codex_home)
        self.assertIn("REMOVE managed skill note-system", actions)

    def test_cli_purges_repository_skills_without_removing_agents_file(self) -> None:
        deploy(self.source_root, self.codex_home)

        result = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "deploy.py"),
                "--codex-home",
                str(self.codex_home),
                "--purge-skills",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REMOVE managed skill alpha", result.stdout)
        self.assertIn("REMOVE managed skill beta", result.stdout)
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())
        self.assertFalse((self.codex_home / "skills" / "alpha").exists())
        self.assertFalse((self.codex_home / "skills" / "beta").exists())


if __name__ == "__main__":
    unittest.main()
