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
NOTE_SYSTEM_ROOT = REPO_ROOT / "skills" / "note-system"
REFERENCES_ROOT = NOTE_SYSTEM_ROOT / "references"
WORKFLOWS_ROOT = REFERENCES_ROOT / "workflows"
STATES_ROOT = REFERENCES_ROOT / "states"
PROCEDURES_ROOT = REFERENCES_ROOT / "procedures"
FORMATS_ROOT = REFERENCES_ROOT / "formats"
NAVIGATOR_PATH = NOTE_SYSTEM_ROOT / "scripts" / "navigate.py"
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^]]*]\(([^)]+)\)")

EXPECTED_WORKFLOWS = {"curate", "ingest", "question"}
EXPECTED_STATES = {
    "acquisition",
    "answer",
    "discovery",
    "integration",
    "review",
    "visual-preparation",
}
EXPECTED_PROCEDURES = {
    "concept-integration",
    "research",
    "source-preservation",
    "vault-discovery",
    "verification",
    "visual-assessment",
    "visual-sourcing",
    "youtube",
}
EXPECTED_FORMATS = {"completion-report", "source-note"}


def load_workflows() -> dict[str, dict[str, object]]:
    return {
        name: cast(
            dict[str, object],
            json.loads((WORKFLOWS_ROOT / f"{name}.json").read_text(encoding="utf-8")),
        )
        for name in EXPECTED_WORKFLOWS
    }


class NoteSystemStructureTests(unittest.TestCase):
    def test_metadata_is_minimal_and_implicitly_invokable(self) -> None:
        text = (NOTE_SYSTEM_ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = FRONTMATTER_PATTERN.match(text)
        self.assertIsNotNone(match)
        metadata = yaml.safe_load(cast(re.Match[str], match).group("yaml"))

        self.assertEqual(set(metadata), {"description", "name"})
        self.assertEqual(metadata["name"], "note-system")
        self.assertIn("Obsidian", cast(str, metadata["description"]))

        openai_metadata = yaml.safe_load(
            (NOTE_SYSTEM_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(openai_metadata["interface"]),
            {"default_prompt", "display_name", "short_description"},
        )
        self.assertIn("$note-system", openai_metadata["interface"]["default_prompt"])
        self.assertIs(openai_metadata["policy"]["allow_implicit_invocation"], True)

    def test_internal_modules_are_complete_and_not_discoverable(self) -> None:
        self.assertEqual(
            {path.name for path in REFERENCES_ROOT.iterdir() if path.is_dir()},
            {"formats", "procedures", "states", "workflows"},
        )
        self.assertEqual(
            {path.stem for path in WORKFLOWS_ROOT.glob("*.json")},
            EXPECTED_WORKFLOWS,
        )
        self.assertEqual(
            {path.stem for path in STATES_ROOT.glob("*.md")}, EXPECTED_STATES
        )
        self.assertEqual(
            {path.stem for path in PROCEDURES_ROOT.glob("*.md")},
            EXPECTED_PROCEDURES,
        )
        self.assertEqual(
            {path.stem for path in FORMATS_ROOT.glob("*.md")}, EXPECTED_FORMATS
        )
        self.assertEqual(list(REFERENCES_ROOT.rglob("SKILL.md")), [])
        self.assertTrue(NAVIGATOR_PATH.is_file())

    def test_navigator_has_no_nonstandard_runtime_imports(self) -> None:
        tree = ast.parse(NAVIGATOR_PATH.read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            for alias in node.names
        }

        self.assertIn("json", imports)
        self.assertNotIn("yaml", imports)

    def test_procedure_names_do_not_reuse_state_names(self) -> None:
        self.assertTrue(EXPECTED_PROCEDURES.isdisjoint(EXPECTED_STATES))

    def test_local_markdown_links_resolve(self) -> None:
        paths = [NOTE_SYSTEM_ROOT / "SKILL.md", *REFERENCES_ROOT.rglob("*.md")]
        for path in paths:
            for target in MARKDOWN_LINK_PATTERN.findall(
                path.read_text(encoding="utf-8")
            ):
                if target.startswith(("http://", "https://", "#")):
                    continue
                relative_target = target.split("#", maxsplit=1)[0]
                self.assertTrue(
                    (path.parent / relative_target).exists(),
                    f"Broken link in {path}: {target}",
                )


class NoteSystemWorkflowTests(unittest.TestCase):
    def test_manifests_reference_complete_internal_modules(self) -> None:
        workflows = load_workflows()
        referenced_states: set[str] = set()
        referenced_procedures: set[str] = set()
        referenced_formats: set[str] = set()

        for name, workflow in workflows.items():
            self.assertEqual(
                set(workflow), {"entry-state", "name", "persistence", "states"}
            )
            self.assertEqual(workflow["name"], name)
            self.assertEqual(workflow["persistence"], "conversational")
            states = cast(dict[str, object], workflow["states"])
            self.assertIn(workflow["entry-state"], states)
            referenced_states.update(states)
            for raw_state in states.values():
                state = cast(dict[str, object], raw_state)
                self.assertEqual(
                    set(state).difference({"formats"}), {"procedures", "transitions"}
                )
                procedures = cast(dict[str, object], state["procedures"])
                referenced_procedures.update(procedures)
                referenced_formats.update(
                    cast(dict[str, object], state.get("formats", {}))
                )
                for raw_access in procedures.values():
                    access = cast(dict[str, object], raw_access)
                    self.assertIn(
                        access["status"], {"allowed", "required", "triggered"}
                    )
                    self.assertIsInstance(access["cue"], str)
                    referenced_formats.update(
                        cast(dict[str, object], access.get("formats", {}))
                    )
                for destination in cast(dict[str, str], state["transitions"]).values():
                    if destination != "complete":
                        if "." in destination:
                            target_workflow, target_state = destination.split(".", 1)
                            self.assertIn(target_workflow, workflows)
                            self.assertIn(
                                target_state,
                                cast(
                                    dict[str, object],
                                    workflows[target_workflow]["states"],
                                ),
                            )
                        else:
                            self.assertIn(destination, states)

        self.assertEqual(referenced_states, EXPECTED_STATES)
        self.assertEqual(referenced_procedures, EXPECTED_PROCEDURES)
        self.assertEqual(referenced_formats, EXPECTED_FORMATS)

    def test_workflow_routes_preserve_question_and_approval_boundaries(self) -> None:
        workflows = load_workflows()
        question = cast(dict[str, object], workflows["question"]["states"])
        curate = cast(dict[str, object], workflows["curate"]["states"])
        ingest = cast(dict[str, object], workflows["ingest"]["states"])

        self.assertEqual(set(question), {"answer", "discovery"})
        self.assertNotIn("integration", question)
        self.assertEqual(
            cast(
                dict[str, str], cast(dict[str, object], curate["review"])["transitions"]
            )["decision-resolved"],
            "integration",
        )
        self.assertEqual(
            cast(
                dict[str, str], cast(dict[str, object], ingest["review"])["transitions"]
            )["source-record-defect"],
            "integration",
        )
        self.assertEqual(
            cast(
                dict[str, str], cast(dict[str, object], ingest["review"])["transitions"]
            )["source-evidence-gap"],
            "acquisition",
        )

        self.assertEqual(workflows["ingest"]["entry-state"], "acquisition")
        self.assertEqual(
            cast(
                dict[str, str],
                cast(dict[str, object], ingest["acquisition"])["transitions"],
            ),
            {"source-acquired": "discovery"},
        )
        self.assertEqual(
            cast(
                dict[str, str],
                cast(dict[str, object], ingest["discovery"])["transitions"],
            ),
            {"ready": "integration", "source-mismatch": "acquisition"},
        )


class NoteSystemNavigatorTests(unittest.TestCase):
    def invoke_navigator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(NAVIGATOR_PATH), *arguments],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def run_navigator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = self.invoke_navigator(*arguments)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def reject_navigator(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        result = self.invoke_navigator(*arguments)
        self.assertEqual(result.returncode, 2, result.stdout)
        return result

    def test_each_entry_and_state_has_an_exact_resume_command(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            entry = cast(str, workflow["entry-state"])
            output = self.run_navigator("start", workflow_name).stdout
            self.assertIn(f"resume {workflow_name} {entry}", output)
            for state_name in states:
                with self.subTest(workflow=workflow_name, state=state_name):
                    output = self.run_navigator(
                        "resume", workflow_name, state_name
                    ).stdout
                    self.assertIn(f"resume {workflow_name} {state_name}", output)

    def test_visual_procedures_have_exclusive_state_boundaries(self) -> None:
        acquisition = self.run_navigator("resume", "ingest", "acquisition").stdout

        self.assertIn("procedure ingest acquisition youtube", acquisition)
        self.assertNotIn("# Source Preservation Procedure", acquisition)

        expected = {
            ("ingest", "acquisition", "visual-sourcing"),
            ("curate", "visual-preparation", "visual-sourcing"),
            ("curate", "integration", "visual-assessment"),
            ("ingest", "integration", "visual-assessment"),
        }
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name in states:
                for procedure_name in ("visual-assessment", "visual-sourcing"):
                    arguments = (
                        "procedure",
                        workflow_name,
                        state_name,
                        procedure_name,
                    )
                    if (workflow_name, state_name, procedure_name) in expected:
                        procedure = self.run_navigator(*arguments).stdout
                        self.assertIn("Procedure status: triggered", procedure)
                    else:
                        self.reject_navigator(*arguments)

        integration = self.run_navigator("resume", "ingest", "integration").stdout
        self.assertIn("# Source Preservation Procedure", integration)
        procedure = self.run_navigator(
            "procedure", "ingest", "integration", "source-preservation"
        ).stdout
        self.assertIn(
            "format ingest integration source-note --procedure source-preservation",
            procedure,
        )

    def test_research_is_available_during_investigative_states(self) -> None:
        states = [
            *((workflow_name, "discovery") for workflow_name in EXPECTED_WORKFLOWS),
            ("ingest", "acquisition"),
            ("curate", "integration"),
            ("ingest", "integration"),
        ]
        for workflow_name, state_name in states:
            output = self.run_navigator("resume", workflow_name, state_name).stdout
            self.assertIn(
                f"procedure {workflow_name} {state_name} research",
                output,
            )
            research = self.run_navigator(
                "procedure", workflow_name, state_name, "research"
            ).stdout
            self.assertIn("Procedure status: allowed", research)

        self.reject_navigator("procedure", "question", "discovery", "verification")

    def test_review_can_complete_or_return_to_integration(self) -> None:
        output = self.run_navigator("resume", "curate", "review").stdout

        self.assertIn("move curate review complete", output)
        self.assertIn("move curate review integration", output)

    def test_curation_can_prepare_and_reassess_visuals_without_ingestion(self) -> None:
        for origin in ("integration", "review"):
            with self.subTest(origin=origin):
                output = self.run_navigator("resume", "curate", origin).stdout
                self.assertIn(f"move curate {origin} visual-preparation", output)
                prepared = self.run_navigator(
                    "move", "curate", origin, "visual-preparation"
                ).stdout
                self.assertIn(
                    "procedure curate visual-preparation visual-sourcing", prepared
                )
                self.assertNotIn("youtube", prepared)
                self.assertNotIn("source-preservation", prepared)
                self.assertNotIn("# Visual Sourcing Procedure", prepared)

        integrated = self.run_navigator(
            "move", "curate", "visual-preparation", "integration"
        ).stdout
        self.assertIn("# Concept Integration Procedure", integrated)
        self.assertIn("procedure curate integration visual-assessment", integrated)
        self.assertNotIn("source-preservation", integrated)
        self.reject_navigator(
            "procedure", "curate", "integration", "source-preservation"
        )

    def test_curation_can_route_a_new_source_into_ingestion(self) -> None:
        for origin in ("discovery", "integration", "visual-preparation", "review"):
            with self.subTest(origin=origin):
                output = self.run_navigator("resume", "curate", origin).stdout
                self.assertIn(f"move curate {origin} ingest.acquisition", output)
                acquired = self.run_navigator(
                    "move", "curate", origin, "ingest.acquisition"
                ).stdout
                self.assertIn("resume ingest acquisition", acquired)
                self.assertIn("procedure ingest acquisition youtube", acquired)

        self.run_navigator("move", "ingest", "acquisition", "discovery")
        integrated = self.run_navigator(
            "move", "ingest", "discovery", "integration"
        ).stdout
        self.assertIn("# Source Preservation Procedure", integrated)
        self.assertIn("# Concept Integration Procedure", integrated)

    def test_every_transition_procedure_and_format_is_publicly_reachable(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name, raw_state in states.items():
                state = cast(dict[str, object], raw_state)
                for destination in cast(dict[str, str], state["transitions"]).values():
                    with self.subTest(
                        workflow=workflow_name,
                        state=state_name,
                        destination=destination,
                    ):
                        output = self.run_navigator(
                            "move", workflow_name, state_name, destination
                        ).stdout
                        if destination == "complete":
                            self.assertIn("Workflow complete", output)
                        else:
                            target_workflow, target_state = (
                                destination.split(".", 1)
                                if "." in destination
                                else (workflow_name, destination)
                            )
                            self.assertIn(
                                f"resume {target_workflow} {target_state}", output
                            )

                procedures = cast(dict[str, object], state["procedures"])
                for procedure_name, raw_access in procedures.items():
                    with self.subTest(
                        workflow=workflow_name,
                        state=state_name,
                        procedure=procedure_name,
                    ):
                        output = self.run_navigator(
                            "procedure",
                            workflow_name,
                            state_name,
                            procedure_name,
                        ).stdout
                        self.assertIn("Procedure status:", output)
                    access = cast(dict[str, object], raw_access)
                    for format_name in cast(
                        dict[str, object], access.get("formats", {})
                    ):
                        self.run_navigator(
                            "format",
                            workflow_name,
                            state_name,
                            format_name,
                            "--procedure",
                            procedure_name,
                        )

                for format_name in cast(dict[str, object], state.get("formats", {})):
                    self.run_navigator("format", workflow_name, state_name, format_name)


if __name__ == "__main__":
    unittest.main()
