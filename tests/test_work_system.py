from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import cast

import yaml

REPO_ROOT = Path(__file__).parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
WORK_SYSTEM_ROOT = SKILLS_ROOT / "work-system"
NOTE_SYSTEM_ROOT = SKILLS_ROOT / "note-system"
REFERENCES_ROOT = WORK_SYSTEM_ROOT / "references"
WORKFLOWS_ROOT = REFERENCES_ROOT / "workflows"
STATES_ROOT = REFERENCES_ROOT / "states"
PROCEDURES_ROOT = REFERENCES_ROOT / "procedures"
FORMATS_ROOT = REFERENCES_ROOT / "formats"
STORAGE_ROOT = REFERENCES_ROOT / "storage"
NAVIGATOR_PATH = WORK_SYSTEM_ROOT / "scripts" / "navigate.py"
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^]]*]\(([^)]+)\)")

EXPECTED_STATES = {
    "answer",
    "delivery",
    "discovery",
    "implementation",
    "planning",
    "subagent-handoff",
    "subagent-implementation",
    "validation",
}
EXPECTED_PROCEDURES = {
    "commit",
    "delegate",
    "diagnose",
    "domain-modeling",
    "documentation",
    "interface-design",
    "prototype",
    "research",
    "review",
    "subagent-testing",
    "testing",
    "wayfinding",
}
EXPECTED_FORMATS = {"domain-modeling", "planning-artifacts", "wayfinding"}
EXPECTED_WORKFLOWS = {
    "fix",
    "novel-work",
    "question",
    "subagent-implementation",
    "tweak",
}
WORKFLOW_MANIFESTS = {
    name: WORKFLOWS_ROOT / f"{name}.json" for name in EXPECTED_WORKFLOWS
}


def load_yaml_mapping(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError(f"{path} must contain a YAML mapping")
    return cast(dict[str, object], loaded)


def load_workflows() -> dict[str, dict[str, object]]:
    return {
        workflow_name: cast(
            dict[str, object], json.loads(path.read_text(encoding="utf-8"))
        )
        for workflow_name, path in WORKFLOW_MANIFESTS.items()
    }


class WorkSystemStructureTests(unittest.TestCase):
    def test_only_root_system_skills_are_discoverable(self) -> None:
        skill_files = set(SKILLS_ROOT.glob("*/SKILL.md"))

        self.assertEqual(
            skill_files,
            {WORK_SYSTEM_ROOT / "SKILL.md", NOTE_SYSTEM_ROOT / "SKILL.md"},
        )
        self.assertEqual(
            {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()},
            {"note-system", "work-system"},
        )
        self.assertEqual(list(REFERENCES_ROOT.rglob("SKILL.md")), [])

    def test_work_system_metadata_is_minimal_and_implicit(self) -> None:
        skill_path = WORK_SYSTEM_ROOT / "SKILL.md"
        text = skill_path.read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(text)
        self.assertIsNotNone(match)
        metadata = yaml.safe_load(cast(re.Match[str], match).group("yaml"))

        self.assertEqual(set(metadata), {"name", "description"})
        self.assertEqual(metadata["name"], "work-system")
        self.assertIsInstance(metadata["description"], str)
        self.assertTrue(cast(str, metadata["description"]).strip())

        openai_metadata = load_yaml_mapping(WORK_SYSTEM_ROOT / "agents" / "openai.yaml")
        interface = cast(dict[str, object], openai_metadata["interface"])
        self.assertEqual(
            set(interface), {"display_name", "short_description", "default_prompt"}
        )
        for value in interface.values():
            self.assertIsInstance(value, str)
            self.assertTrue(cast(str, value).strip())
        policy = openai_metadata["policy"]
        self.assertIsInstance(policy, dict)
        self.assertIs(
            cast(dict[str, object], policy)["allow_implicit_invocation"], True
        )

    def test_root_delegates_navigation_without_exposing_manifests(self) -> None:
        self.assertEqual(
            {path.name for path in REFERENCES_ROOT.iterdir() if path.is_dir()},
            {"formats", "procedures", "states", "storage", "workflows"},
        )
        self.assertEqual(
            {path.name for path in WORKFLOWS_ROOT.iterdir()},
            {f"{name}.json" for name in EXPECTED_WORKFLOWS},
        )
        self.assertEqual(
            {path.name for path in STATES_ROOT.iterdir()},
            {f"{name}.md" for name in EXPECTED_STATES},
        )
        self.assertLessEqual(
            {f"{name}.md" for name in EXPECTED_PROCEDURES},
            {path.name for path in PROCEDURES_ROOT.iterdir()},
        )
        self.assertEqual(
            {path.name for path in FORMATS_ROOT.iterdir()},
            {"domain-modeling.md", "planning-artifacts.md", "wayfinding.md"},
        )
        self.assertEqual(
            {path.name for path in STORAGE_ROOT.iterdir()}, {"local-work-store.md"}
        )
        self.assertEqual(
            [path for path in REFERENCES_ROOT.iterdir() if path.is_file()], []
        )
        self.assertTrue(NAVIGATOR_PATH.is_file())

    def test_navigator_uses_only_standard_library_manifest_loading(self) -> None:
        tree = ast.parse(NAVIGATOR_PATH.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }

        self.assertIn("json", imports)
        self.assertNotIn("yaml", imports)

    def test_local_markdown_links_resolve(self) -> None:
        paths = [WORK_SYSTEM_ROOT / "SKILL.md", *REFERENCES_ROOT.rglob("*.md")]
        for path in paths:
            for target in MARKDOWN_LINK_PATTERN.findall(
                path.read_text(encoding="utf-8")
            ):
                if target.startswith(("http://", "https://", "#")):
                    continue
                relative_target = target.split("#", maxsplit=1)[0]
                if "<" in relative_target:
                    continue
                self.assertTrue(
                    (path.parent / relative_target).exists(),
                    f"Broken link in {path}: {target}",
                )


class WorkflowManifestTests(unittest.TestCase):
    def test_each_manifest_contains_one_workflow(self) -> None:
        workflows = load_workflows()

        for workflow_name, workflow in workflows.items():
            with self.subTest(workflow=workflow_name):
                expected_keys = {"name", "entry-state", "persistence", "states"}
                if workflow_name == "novel-work":
                    expected_keys.add("work-record")
                self.assertEqual(set(workflow), expected_keys)
                self.assertEqual(workflow["name"], workflow_name)
                self.assertNotIn("workflows", workflow)

    def test_manifests_reference_the_expected_internal_modules(self) -> None:
        workflows = load_workflows()
        referenced_states: set[str] = set()
        referenced_procedures: set[str] = set()
        referenced_formats: set[str] = set()

        for workflow in workflows.values():
            states = cast(dict[str, object], workflow["states"])
            referenced_states.update(states)
            for state_value in states.values():
                state = cast(dict[str, object], state_value)
                procedures = cast(dict[str, object], state["procedures"])
                referenced_procedures.update(procedures)
                referenced_formats.update(
                    cast(dict[str, object], state.get("formats", {}))
                )
                for raw_access in procedures.values():
                    access = cast(dict[str, object], raw_access)
                    referenced_formats.update(
                        cast(dict[str, object], access.get("formats", {}))
                    )

        self.assertEqual(referenced_states, EXPECTED_STATES)
        self.assertGreaterEqual(referenced_procedures, EXPECTED_PROCEDURES)
        self.assertEqual(referenced_formats, EXPECTED_FORMATS)
        for state_name in referenced_states:
            self.assertTrue((STATES_ROOT / f"{state_name}.md").is_file())
        for procedure_name in referenced_procedures:
            self.assertTrue((PROCEDURES_ROOT / f"{procedure_name}.md").is_file())
        for format_name in referenced_formats:
            self.assertTrue((FORMATS_ROOT / f"{format_name}.md").is_file())

    def test_every_workflow_state_has_an_explicit_procedure_allowlist(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name, state_value in states.items():
                with self.subTest(workflow=workflow_name, state=state_name):
                    state = cast(dict[str, object], state_value)
                    self.assertIn("procedures", state)
                    authorized = cast(dict[str, object], state["procedures"])
                    for procedure_name, raw_access in authorized.items():
                        self.assertTrue(
                            (PROCEDURES_ROOT / f"{procedure_name}.md").is_file()
                        )
                        access = cast(dict[str, object], raw_access)
                        self.assertLessEqual(
                            set(access),
                            {"status", "cue", "formats", "related-procedures"},
                        )
                        self.assertGreaterEqual(set(access), {"status", "cue"})
                        self.assertIn(
                            access["status"], {"allowed", "triggered", "required"}
                        )
                        self.assertIsInstance(access["cue"], str, procedure_name)
                        related = cast(
                            list[object], access.get("related-procedures", [])
                        )
                        self.assertEqual(len(related), len(set(related)))
                        for related_name in related:
                            self.assertIsInstance(related_name, str)
                            self.assertIn(related_name, authorized)
                            self.assertNotEqual(related_name, procedure_name)
                        formats = cast(dict[str, object], access.get("formats", {}))
                        for format_name, raw_format in formats.items():
                            format_access = cast(dict[str, object], raw_format)
                            self.assertEqual(set(format_access), {"cue"}, format_name)

                    formats = cast(dict[str, object], state.get("formats", {}))
                    for format_name, raw_format in formats.items():
                        format_access = cast(dict[str, object], raw_format)
                        self.assertEqual(set(format_access), {"cue"}, format_name)

    def test_only_novel_work_loads_the_local_record(self) -> None:
        workflows = load_workflows()

        self.assertNotIn("work-record", workflows["question"])
        self.assertNotIn("work-record", workflows["tweak"])
        self.assertNotIn("work-record", workflows["fix"])
        self.assertNotIn("work-record", workflows["subagent-implementation"])
        self.assertEqual(
            workflows["novel-work"]["work-record"],
            "storage/local-work-store.md",
        )
        record_path = REFERENCES_ROOT / cast(
            str, workflows["novel-work"]["work-record"]
        )
        self.assertTrue(record_path.is_file())

    def test_entries_and_transitions_resolve(self) -> None:
        workflows = load_workflows()

        for workflow_name, workflow in workflows.items():
            states = cast(dict[str, object], workflow["states"])
            self.assertIn(workflow["entry-state"], states)
            self.assertLessEqual(set(states), EXPECTED_STATES)

            for state_name, state_value in states.items():
                transitions = cast(
                    dict[str, str], cast(dict[str, object], state_value)["transitions"]
                )
                for outcome, destination in transitions.items():
                    with self.subTest(
                        workflow=workflow_name,
                        state=state_name,
                        outcome=outcome,
                    ):
                        if destination == "complete":
                            continue
                        if "." not in destination:
                            self.assertIn(destination, states)
                            continue
                        target_workflow, target_state = destination.split(
                            ".", maxsplit=1
                        )
                        self.assertIn(target_workflow, workflows)
                        target_states = cast(
                            dict[str, object], workflows[target_workflow]["states"]
                        )
                        self.assertIn(target_state, target_states)

    def test_prototype_and_testing_are_isolated(self) -> None:
        workflows = load_workflows()
        question_states = cast(dict[str, object], workflows["question"]["states"])
        question_discovery = cast(dict[str, object], question_states["discovery"])
        self.assertEqual(
            set(cast(dict[str, object], question_discovery["procedures"])), {"research"}
        )

        tweak_states = cast(dict[str, object], workflows["tweak"]["states"])
        tweak_discovery = cast(dict[str, object], tweak_states["discovery"])
        self.assertEqual(
            set(cast(dict[str, object], tweak_discovery["procedures"])), {"research"}
        )

        fix_states = cast(dict[str, object], workflows["fix"]["states"])
        fix_discovery = cast(dict[str, object], fix_states["discovery"])
        self.assertEqual(
            set(cast(dict[str, object], fix_discovery["procedures"])),
            {"diagnose", "research"},
        )

        novel = workflows["novel-work"]
        self.assertEqual(novel["entry-state"], "planning")
        novel_states = cast(dict[str, object], novel["states"])
        self.assertNotIn("discovery", novel_states)
        self.assertNotIn("wayfinding", novel_states)
        planning = cast(dict[str, object], novel_states["planning"])
        self.assertEqual(
            set(cast(dict[str, object], planning["procedures"])),
            {
                "domain-modeling",
                "interface-design",
                "prototype",
                "research",
                "wayfinding",
            },
        )
        self.assertNotIn("testing", cast(dict[str, object], planning["procedures"]))

        for workflow in workflows.values():
            states = cast(dict[str, object], workflow["states"])
            for state_name, state_value in states.items():
                procedures = cast(
                    dict[str, object],
                    cast(dict[str, object], state_value)["procedures"],
                )
                if "testing" in procedures:
                    self.assertEqual(state_name, "implementation")

    def test_interface_design_is_triggered_only_for_design_work(self) -> None:
        workflows = load_workflows()
        expected_locations = {
            ("fix", "implementation"),
            ("novel-work", "planning"),
            ("novel-work", "implementation"),
            ("tweak", "implementation"),
        }
        actual_locations: set[tuple[str, str]] = set()

        for workflow_name, workflow in workflows.items():
            states = cast(dict[str, object], workflow["states"])
            for state_name, state_value in states.items():
                procedures = cast(
                    dict[str, object],
                    cast(dict[str, object], state_value)["procedures"],
                )
                if "interface-design" not in procedures:
                    continue
                actual_locations.add((workflow_name, state_name))
                access = cast(dict[str, object], procedures["interface-design"])
                self.assertEqual(access["status"], "triggered")

        self.assertEqual(actual_locations, expected_locations)

        novel_states = cast(dict[str, object], workflows["novel-work"]["states"])
        planning = cast(dict[str, object], novel_states["planning"])
        planning_procedures = cast(dict[str, object], planning["procedures"])
        interface_design = cast(
            dict[str, object], planning_procedures["interface-design"]
        )
        prototype = cast(dict[str, object], planning_procedures["prototype"])
        wayfinding = cast(dict[str, object], planning_procedures["wayfinding"])
        self.assertEqual(interface_design["related-procedures"], ["prototype"])
        self.assertEqual(prototype["related-procedures"], ["interface-design"])
        self.assertIn(
            "interface-design",
            cast(list[object], wayfinding["related-procedures"]),
        )

    def test_development_delegation_is_implementation_only(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name, state_value in states.items():
                procedures = cast(
                    dict[str, object],
                    cast(dict[str, object], state_value)["procedures"],
                )
                if (
                    workflow_name in {"fix", "tweak", "novel-work"}
                    and state_name == "implementation"
                ):
                    self.assertIn("delegate", procedures)
                else:
                    self.assertNotIn("delegate", procedures)

    def test_subagent_implementation_is_isolated(self) -> None:
        workflow = load_workflows()["subagent-implementation"]
        states = cast(dict[str, object], workflow["states"])

        self.assertEqual(workflow["entry-state"], "subagent-implementation")
        self.assertEqual(set(states), {"subagent-implementation", "subagent-handoff"})

        implementation = cast(dict[str, object], states["subagent-implementation"])
        procedures = cast(dict[str, object], implementation["procedures"])
        self.assertEqual(set(procedures), {"subagent-testing"})
        self.assertEqual(
            cast(dict[str, object], procedures["subagent-testing"])["status"],
            "required",
        )
        self.assertEqual(
            cast(dict[str, str], implementation["transitions"]),
            {
                "implemented": "subagent-handoff",
                "assignment-blocked": "subagent-handoff",
            },
        )

        handoff = cast(dict[str, object], states["subagent-handoff"])
        self.assertEqual(cast(dict[str, object], handoff["procedures"]), {})
        self.assertEqual(
            cast(dict[str, str], handoff["transitions"]),
            {"reported": "complete"},
        )

    def test_research_is_reusable_but_explicitly_allowlisted(self) -> None:
        authorizing_states: set[str] = set()

        for workflow in load_workflows().values():
            states = cast(dict[str, object], workflow["states"])
            for state_name, state_value in states.items():
                procedures = cast(
                    dict[str, object],
                    cast(dict[str, object], state_value)["procedures"],
                )
                if "research" in procedures:
                    authorizing_states.add(state_name)

        self.assertGreaterEqual(len(authorizing_states), 2)

    def test_fix_is_a_first_class_workflow_with_required_diagnosis(self) -> None:
        fix = load_workflows()["fix"]
        self.assertEqual(fix["entry-state"], "discovery")
        self.assertNotIn("variants", fix)
        states = cast(dict[str, object], fix["states"])
        discovery = cast(dict[str, object], states["discovery"])
        diagnosis = cast(dict[str, object], discovery["procedures"])["diagnose"]
        diagnosis = cast(dict[str, object], diagnosis)
        self.assertEqual(diagnosis["status"], "required")

    def test_validation_and_delivery_can_return_to_owning_states(self) -> None:
        workflows = load_workflows()
        for workflow_name in {"fix", "tweak"}:
            states = cast(dict[str, object], workflows[workflow_name]["states"])
            validation = cast(dict[str, object], states["validation"])
            delivery = cast(dict[str, object], states["delivery"])
            with self.subTest(workflow=workflow_name):
                self.assertGreaterEqual(
                    set(cast(dict[str, str], validation["transitions"]).values()),
                    {"delivery", "implementation", "discovery", "validation"},
                )
                self.assertGreaterEqual(
                    set(cast(dict[str, str], delivery["transitions"]).values()),
                    {
                        "complete",
                        "implementation",
                        "validation",
                        "discovery",
                        "delivery",
                    },
                )

        novel_states = cast(dict[str, object], workflows["novel-work"]["states"])
        novel_validation = cast(dict[str, object], novel_states["validation"])
        novel_delivery = cast(dict[str, object], novel_states["delivery"])
        expected_returns = {"planning", "implementation"}
        self.assertLessEqual(
            expected_returns,
            set(cast(dict[str, str], novel_validation["transitions"]).values()),
        )
        self.assertLessEqual(
            expected_returns | {"validation"},
            set(cast(dict[str, str], novel_delivery["transitions"]).values()),
        )
        self.assertNotIn(
            "discovery",
            set(cast(dict[str, str], novel_validation["transitions"]).values()),
        )
        self.assertNotIn(
            "wayfinding",
            set(cast(dict[str, str], novel_delivery["transitions"]).values()),
        )
        self.assertEqual(
            cast(dict[str, str], novel_delivery["transitions"])["ticket-delivered"],
            "implementation",
        )
        self.assertEqual(
            cast(dict[str, str], novel_delivery["transitions"])["effort-delivered"],
            "complete",
        )


class NavigatorTests(unittest.TestCase):
    def run_navigator(
        self, *arguments: str, expected_returncode: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(NAVIGATOR_PATH), *arguments],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, expected_returncode, result.stderr)
        return result

    def test_start_returns_only_the_entry_state_context(self) -> None:
        output = self.run_navigator("start", "question").stdout

        self.assertIn("procedure question discovery research", output)
        self.assertIn("move question discovery answer", output)
        self.assertIn("resume question discovery", output)
        self.assertNotIn("resume question answer", output)
        self.assertNotIn("procedure question discovery testing", output)

    def test_triggered_procedure_commands_are_discoverable(self) -> None:
        output = self.run_navigator("start", "novel-work").stdout

        for procedure_name in {
            "domain-modeling",
            "interface-design",
            "prototype",
            "wayfinding",
        }:
            self.assertIn(f"procedure novel-work planning {procedure_name}", output)
        self.assertIn("format novel-work planning planning-artifacts", output)

    def test_fix_workflow_navigation_does_not_use_variants(self) -> None:
        output = self.run_navigator("start", "fix").stdout

        self.assertIn("resume fix discovery", output)
        self.assertNotIn("--variant", output)

    def test_tweak_testing_loads_on_demand_while_fix_and_novel_require_it(self) -> None:
        guidance = (PROCEDURES_ROOT / "testing.md").read_text(encoding="utf-8").strip()
        tweak = self.run_navigator("resume", "tweak", "implementation").stdout

        self.assertIn("`testing` (triggered):", tweak)
        self.assertIn("procedure tweak implementation testing", tweak)
        self.assertNotIn(guidance, tweak)
        loaded = self.run_navigator(
            "procedure", "tweak", "implementation", "testing"
        ).stdout
        self.assertIn(guidance, loaded)

        for workflow_name in ("fix", "novel-work"):
            with self.subTest(workflow=workflow_name):
                output = self.run_navigator(
                    "resume", workflow_name, "implementation"
                ).stdout
                self.assertIn(guidance, output)

    def test_every_active_state_exposes_an_exact_resume_command(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name in states:
                with self.subTest(workflow=workflow_name, state=state_name):
                    output = self.run_navigator(
                        "resume", workflow_name, state_name
                    ).stdout
                    self.assertIn(f"resume {workflow_name} {state_name}", output)

    def test_procedure_command_enforces_the_active_state_boundary(self) -> None:
        available = self.run_navigator(
            "procedure", "novel-work", "planning", "prototype"
        )
        unavailable = self.run_navigator(
            "procedure",
            "question",
            "discovery",
            "prototype",
            expected_returncode=2,
        )

        self.assertTrue(available.stdout.strip())
        self.assertEqual(unavailable.stdout, "")
        self.assertTrue(unavailable.stderr.strip())

    def test_procedure_exposes_only_its_associated_formats(self) -> None:
        output = self.run_navigator(
            "procedure", "novel-work", "planning", "domain-modeling"
        ).stdout

        self.assertIn(
            "format novel-work planning domain-modeling --procedure domain-modeling",
            output,
        )
        self.assertNotIn("format novel-work planning wayfinding", output)

    def test_procedure_exposes_only_declared_related_procedure_cues(self) -> None:
        output = self.run_navigator(
            "procedure", "novel-work", "planning", "wayfinding"
        ).stdout

        for procedure_name in {
            "research",
            "prototype",
            "domain-modeling",
            "interface-design",
        }:
            self.assertIn(f"procedure novel-work planning {procedure_name}", output)
        self.assertNotIn("procedure novel-work planning testing", output)

    def test_interface_design_navigation_respects_state_boundaries(self) -> None:
        planning = self.run_navigator(
            "procedure", "novel-work", "planning", "interface-design"
        ).stdout
        implementation = self.run_navigator(
            "procedure", "tweak", "implementation", "interface-design"
        ).stdout
        unavailable = self.run_navigator(
            "procedure",
            "tweak",
            "validation",
            "interface-design",
            expected_returncode=2,
        )

        self.assertIn("procedure novel-work planning prototype", planning)
        self.assertNotIn("procedure tweak implementation prototype", implementation)
        self.assertTrue(implementation.strip())
        self.assertTrue(unavailable.stderr.strip())

    def test_format_command_enforces_its_state_and_procedure_source(self) -> None:
        state_format = self.run_navigator(
            "format", "novel-work", "planning", "planning-artifacts"
        ).stdout
        procedure_format = self.run_navigator(
            "format",
            "novel-work",
            "planning",
            "wayfinding",
            "--procedure",
            "wayfinding",
        ).stdout
        unavailable = self.run_navigator(
            "format",
            "question",
            "discovery",
            "planning-artifacts",
            expected_returncode=2,
        )

        self.assertTrue(state_format.strip())
        self.assertTrue(procedure_format.strip())
        self.assertTrue(unavailable.stderr.strip())

    def test_move_requires_an_available_destination(self) -> None:
        valid = self.run_navigator("move", "tweak", "validation", "delivery").stdout
        invalid = self.run_navigator(
            "move",
            "tweak",
            "discovery",
            "delivery",
            expected_returncode=2,
        )

        self.assertIn("resume tweak delivery", valid)
        self.assertTrue(invalid.stderr.strip())

    def test_subagent_implementation_rejects_primary_destinations(self) -> None:
        for destination in {
            "discovery",
            "implementation",
            "planning",
            "validation",
            "delivery",
        }:
            with self.subTest(destination=destination):
                self.run_navigator(
                    "move",
                    "subagent-implementation",
                    "subagent-implementation",
                    destination,
                    expected_returncode=2,
                )

    def test_cross_workflow_move_loads_the_new_workflow_context(self) -> None:
        output = self.run_navigator(
            "move", "fix", "discovery", "novel-work.planning"
        ).stdout

        self.assertIn("procedure novel-work planning prototype", output)
        self.assertIn("resume novel-work planning", output)

    def test_complete_move_returns_to_the_null_state(self) -> None:
        output = self.run_navigator("move", "question", "answer", "complete").stdout

        self.assertTrue(output.strip())
        self.assertNotIn("resume question", output)


if __name__ == "__main__":
    unittest.main()
