from __future__ import annotations

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
    "testing",
    "wayfinding",
}
EXPECTED_FORMATS = {"domain-modeling", "planning-artifacts", "wayfinding"}
EXPECTED_WORKFLOWS = {"fix", "novel-work", "question", "tweak"}
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
    def test_only_the_work_system_is_discoverable(self) -> None:
        skill_files = set(SKILLS_ROOT.glob("*/SKILL.md"))

        self.assertEqual(skill_files, {WORK_SYSTEM_ROOT / "SKILL.md"})
        self.assertEqual(
            {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()},
            {"work-system"},
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
        self.assertEqual(
            metadata["description"],
            "Use when working in a code repository and I ask a question or "
            "request work.",
        )

        openai_metadata = load_yaml_mapping(WORK_SYSTEM_ROOT / "agents" / "openai.yaml")
        interface = cast(dict[str, object], openai_metadata["interface"])
        self.assertEqual(
            interface["short_description"], "Handle repository questions and work"
        )
        self.assertEqual(
            interface["default_prompt"],
            "Use $work-system to handle this repository prompt.",
        )
        policy = openai_metadata["policy"]
        self.assertIsInstance(policy, dict)
        self.assertIs(
            cast(dict[str, object], policy)["allow_implicit_invocation"], True
        )

    def test_root_delegates_navigation_without_exposing_manifests(self) -> None:
        skill_body = (WORK_SYSTEM_ROOT / "SKILL.md").read_text(encoding="utf-8")
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
        self.assertIn("scripts/navigate.py", skill_body)
        self.assertIn("start <workflow>", skill_body)
        self.assertIn("resume <workflow> <state>", skill_body)
        self.assertNotIn("procedure <workflow> <state> <procedure>", skill_body)
        self.assertNotIn("format <workflow> <state> <format>", skill_body)
        self.assertIn("move <workflow> <state> <destination>", skill_body)
        self.assertIn(
            "Load an allowed or triggered procedure only through an exact command",
            skill_body,
        )
        self.assertIn("Do not construct a procedure command independently", skill_body)
        self.assertNotIn("**Effort**", skill_body)
        self.assertNotIn("**Ticket**", skill_body)
        self.assertNotIn("effort and ticket convention", skill_body.casefold())
        self.assertIn(
            "Follow any workflow-record guidance returned by the navigator",
            skill_body,
        )
        self.assertIn("Keep question, tweak, and fix state in conversation", skill_body)
        self.assertIn("exact resume command", skill_body)
        self.assertIn("Do not create a repository record", skill_body)
        self.assertNotIn("--variant", skill_body)
        for workflow_name in EXPECTED_WORKFLOWS:
            self.assertNotIn(f"references/workflows/{workflow_name}.json", skill_body)
        for state_name in EXPECTED_STATES:
            self.assertNotIn(f"references/states/{state_name}.md", skill_body)
        for procedure_name in EXPECTED_PROCEDURES:
            self.assertNotIn(f"references/procedures/{procedure_name}.md", skill_body)

    def test_navigator_uses_only_standard_library_manifest_loading(self) -> None:
        navigator = NAVIGATOR_PATH.read_text(encoding="utf-8")

        self.assertIn("import json", navigator)
        self.assertNotIn("import yaml", navigator)
        self.assertNotIn(".yaml", navigator)

    def test_states_and_procedures_do_not_resolve_format_paths(self) -> None:
        for path in [*STATES_ROOT.glob("*.md"), *PROCEDURES_ROOT.glob("*.md")]:
            guidance = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotIn("../formats/", guidance)
                self.assertNotRegex(guidance, r"references/formats/[^\s)]+")

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

    def test_instructions_do_not_repeat_ambient_or_cross_state_rules(self) -> None:
        paths = [WORK_SYSTEM_ROOT / "SKILL.md", *REFERENCES_ROOT.rglob("*.md")]
        instructions = "\n".join(
            path.read_text(encoding="utf-8") for path in paths
        ).casefold()
        forbidden_phrases = {
            "read applicable agents.md",
            "load applicable agents.md",
            "apply policy",
            "ceremonial confirmation",
            "does not authorize",
            "incompatible states",
            "do not load implementation, testing",
            "do not load or invoke the testing",
            "never apply production testing instructions to a prototype",
        }

        for phrase in forbidden_phrases:
            self.assertNotIn(phrase, instructions)

    def test_glossary_preserves_standing_terms_and_defines_skill_terms(self) -> None:
        skill_body = (WORK_SYSTEM_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(
            "I, me, my, you, your, user, and agent retain their established meanings",
            skill_body,
        )
        for term in {
            "Prompt",
            "Workflow",
            "State",
            "Procedure",
            "Procedure result",
            "Transition",
            "Continuation criteria",
            "Null state",
        }:
            self.assertIn(f"**{term}**", skill_body)

        paths = [
            WORK_SYSTEM_ROOT / "SKILL.md",
            *(
                path
                for path in REFERENCES_ROOT.rglob("*.md")
                if path != FORMATS_ROOT / "planning-artifacts.md"
            ),
        ]
        instructions = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertEqual(len(re.findall(r"\buser\b", instructions, re.IGNORECASE)), 1)
        planning_format = (FORMATS_ROOT / "planning-artifacts.md").read_text(
            encoding="utf-8"
        )
        self.assertEqual(
            re.findall(r"\buser\b", planning_format, re.IGNORECASE), ["User"]
        )

    def test_procedure_results_are_reported_at_the_right_time(self) -> None:
        skill_body = (WORK_SYSTEM_ROOT / "SKILL.md").read_text(encoding="utf-8")
        normalized_skill = " ".join(skill_body.split())

        for guidance in {
            "A procedure result belongs to the active state",
            "does not select another state or require a standalone completion response",
            "Record results needed for continuation in the durable work record",
            "Tell me immediately when a result requires my decision",
            "When the workflow completes, give me one final response",
            "documentation impact, commits, and unresolved issues",
            "Link durable artifacts instead of copying them",
        }:
            self.assertIn(guidance, normalized_skill)

        for procedure_path in PROCEDURES_ROOT.glob("*.md"):
            procedure = procedure_path.read_text(encoding="utf-8")
            with self.subTest(procedure=procedure_path.name):
                self.assertIn("## Result", procedure)
                self.assertNotRegex(
                    procedure,
                    r"Return .* to "
                    r"(?:delivery|planning|implementation|validation|discovery)",
                )

    def test_audited_ambiguous_language_is_absent(self) -> None:
        paths = [WORK_SYSTEM_ROOT / "SKILL.md", *REFERENCES_ROOT.rglob("*.md")]
        instructions = "\n".join(
            path.read_text(encoding="utf-8") for path in paths
        ).casefold()
        for phrase in {
            "workflow map",
            "core question",
            "focused effort",
            "focused question",
            "focused-tweak",
            "context boundary",
            "gate fails",
            "downstream gate",
            "owns the problem",
            "manifest reaches",
        }:
            self.assertNotIn(phrase, instructions)

    def test_shared_states_do_not_name_workflow_specific_context(self) -> None:
        forbidden_by_state = {
            "discovery": {"prototype", "research"},
            "implementation": {"planning", "wayfinding", "discovery"},
            "validation": {
                "plan gap",
                "decision gap",
                "misunderstood requirement",
            },
            "delivery": {
                "implementation for",
                "planning",
                "wayfinding",
                "discovery",
            },
        }

        for state_name, forbidden_phrases in forbidden_by_state.items():
            state = (
                (STATES_ROOT / f"{state_name}.md")
                .read_text(encoding="utf-8")
                .casefold()
            )
            for phrase in forbidden_phrases:
                with self.subTest(state=state_name, phrase=phrase):
                    self.assertNotIn(phrase, state)

    def test_answer_state_resolves_questions_without_authorizing_work(self) -> None:
        answer = (STATES_ROOT / "answer.md").read_text(encoding="utf-8")
        normalized_answer = " ".join(answer.split())

        for heading in {"## Compose the answer", "## Continue"}:
            self.assertIn(heading, answer)

        self.assertNotIn("### ", answer)
        self.assertNotIn("evidence accepted during discovery", answer.casefold())
        self.assertNotIn("delivery reporting", answer.casefold())
        self.assertNotIn("documentation impact", answer.casefold())
        self.assertLess(len(answer.split()), 400)

        for guidance in {
            "evidence established during discovery",
            "The answer is the work",
            "Keep repository state unchanged",
            "do not begin a separate task",
            "Lead with the direct answer, recommendation, or conclusion",
            "For a factual question",
            "For an evaluative question",
            "established facts, supported inferences, and unresolved uncertainty",
            "assumptions that affect the conclusion",
            "conflicting evidence directly",
            "Keep the response proportional to the question",
            "judgment that remains mine",
            "ask the smallest question needed",
            "do not perform it or present it as underway",
            "workflow's completion response",
            "every material part of my question has been answered",
            "remain in answer for discussion or return to discovery for evidence",
        }:
            self.assertIn(guidance, normalized_answer)

    def test_delivery_state_coordinates_complete_durable_work(self) -> None:
        delivery = (STATES_ROOT / "delivery.md").read_text(encoding="utf-8")
        normalized_delivery = " ".join(delivery.split())

        for heading in {
            "## Assemble the complete work",
            "## Adjudicate delivery results",
            "## Preserve the result",
            "## Continue",
        }:
            self.assertIn(heading, delivery)

        self.assertNotIn("### ", delivery)
        self.assertNotIn("navigator presents", delivery.casefold())
        self.assertLess(len(delivery.split()), 500)

        for guidance in {
            "complete, durable repository outcome",
            "does not own corrections to accepted intent, implementation, or "
            "validation evidence",
            "Include every task-owned change",
            "before the complete work is reviewed",
            "Do not use documentation, review, or commit work to conceal",
            "Classify every failed procedure or validated finding",
            "problem remains in delivery",
            "belongs to validation",
            "belongs to implementation",
            "earliest available state that can correct it",
            "Preserve results that remain valid",
            "repeat validation and delivery work",
            "Commit only after documentation is resolved",
            "A commit blocker leaves the work in delivery",
            "When more accepted work remains",
            "Complete the workflow only when no accepted work remains",
            "review passes without an unresolved finding",
            "no decision or correction belongs to an earlier state",
        }:
            self.assertIn(guidance, normalized_delivery)

    def test_discovery_state_orients_without_becoming_research(self) -> None:
        discovery = (STATES_ROOT / "discovery.md").read_text(encoding="utf-8")
        normalized_discovery = " ".join(discovery.split())

        for heading in {
            "## Frame the uncertainty",
            "## Establish the facts",
            "## Continue",
        }:
            self.assertIn(heading, discovery)

        self.assertNotIn("### ", discovery)
        self.assertLess(len(discovery.split()), 500)
        for research_detail in {
            "authoritative sources",
            "multi-source",
            "citation methodology",
            "bounded experiment",
            "adjudicate conflicting sources",
        }:
            self.assertNotIn(research_detail, discovery.casefold())

        for guidance in {
            "facts needed to answer my question or safely begin clear, bounded work",
            "does not choose desired behavior, design a solution, or change the "
            "repository",
            "intent I have stated",
            "assumptions that still require inspection",
            "choices that depend on my judgment",
            "For a question, define the uncertainty",
            "For requested work, state the observable outcome, concrete acceptance "
            "checks",
            "source of intent",
            "current behavior or structure",
            "Inspect the relevant code, configuration, documentation, history, and "
            "observable behavior directly",
            "Reading a small set of repository files is ordinary discovery",
            "only far enough to establish the facts needed by the prompt",
            "decisive evidence and its location",
            "authorized procedure whose cue applies",
            "Do not accumulate unrelated repository orientation",
            "turn a question into repository work",
            "implementation can proceed without inventing consequential intent",
            "Remain in discovery while a material fact is unsupported",
            "cannot remain bounded",
        }:
            self.assertIn(guidance, normalized_discovery)

    def test_implementation_state_builds_maintainable_accepted_work(self) -> None:
        implementation = (STATES_ROOT / "implementation.md").read_text(encoding="utf-8")
        normalized_implementation = " ".join(implementation.split())

        for heading in {
            "## Establish the change",
            "## Build the outcome",
            "## Continue",
        }:
            self.assertIn(heading, implementation)

        self.assertNotIn("### ", implementation)
        self.assertLess(len(implementation.split()), 650)

        for guidance in {
            "coherent, maintainable repository change",
            "does not own new product intent or completion evidence",
            "accepted outcome, concrete acceptance checks, and source artifacts",
            "Do not measure implementation quality by diff size",
            "code and relationships involved in the accepted outcome",
            "directly coupled code whose structure prevents a clean implementation",
            "Follow a refactoring across files, layers, and interfaces",
            "Do not search unrelated parts of the repository",
            "Keep behavior outside the accepted change stable",
            "focused and affected tests green",
            "Refactor the involved code",
            "domain and application behavior independent of GUI rendering",
            "Use dependency injection",
            "Preserve precise types",
            "Handle failures at the boundary",
            "Reuse established dependencies",
            "Add abstractions for accepted behavior or demonstrated variation",
            "Treat removal as removal",
            "Do not stop at an internal mechanism",
            "authorized specialized procedures when their cues apply",
            "do not establish completion evidence",
            "every accepted behavior is implemented",
            "no known implementation defect or unresolved consequential decision",
            "earliest state that can resolve it",
        }:
            self.assertIn(guidance, normalized_implementation)

    def test_pocock_style_artifact_schemas_are_preserved(self) -> None:
        expected_phrases = {
            "domain-modeling.md": {
                "CONTEXT.md",
                "CONTEXT-MAP.md",
                "docs/adr/",
                "_Avoid_",
                "Considered Options",
            },
            "wayfinding.md": {
                "## Destination",
                "## Decisions so far",
                "## Not yet specified",
                "## Out of scope",
                "**Type:** research | prototype | discussion | task",
            },
            "planning-artifacts.md": {
                "## Problem Statement",
                "## Solution",
                "## User Stories",
                "## Implementation Decisions",
                "## Testing Decisions",
                "**What to build:**",
                "**Blocked by:**",
                "**Status:** ready-for-agent",
            },
        }

        for filename, phrases in expected_phrases.items():
            guidance = (FORMATS_ROOT / filename).read_text(encoding="utf-8")
            for phrase in phrases:
                with self.subTest(reference=filename, phrase=phrase):
                    self.assertIn(phrase, guidance)

    def test_efforts_and_tickets_are_introduced_only_when_relevant(self) -> None:
        root = (WORK_SYSTEM_ROOT / "SKILL.md").read_text(encoding="utf-8")
        planning = (STATES_ROOT / "planning.md").read_text(encoding="utf-8")
        planning_format = (FORMATS_ROOT / "planning-artifacts.md").read_text(
            encoding="utf-8"
        )
        work_store = (STORAGE_ROOT / "local-work-store.md").read_text(encoding="utf-8")
        wayfinding = (PROCEDURES_ROOT / "wayfinding.md").read_text(encoding="utf-8")
        normalized_planning = " ".join(planning.split())

        self.assertNotRegex(root, r"\b[Ee]ffort\b")
        self.assertNotRegex(root, r"\b[Tt]icket\b")
        self.assertIn(
            "turn novel work into an accepted specification",
            normalized_planning,
        )
        self.assertIn(
            "implementation tickets sized for one fresh implementation context",
            normalized_planning,
        )
        self.assertIn("It does not own production implementation", normalized_planning)
        self.assertIn(
            "free of unresolved decisions that would require the implementing agent",
            normalized_planning,
        )
        self.assertIn(
            "implementation ticket is a self-contained unit of accepted work",
            planning_format,
        )
        self.assertIn(
            "effort is the durable parent record for one novel-work outcome",
            work_store,
        )
        self.assertIn(
            "Decision tickets resolve intent and must not become production "
            "implementation tickets",
            " ".join(wayfinding.split()),
        )

    def test_wayfinding_handoffs_keep_one_canonical_source(self) -> None:
        planning = (FORMATS_ROOT / "planning-artifacts.md").read_text(encoding="utf-8")
        storage = (STORAGE_ROOT / "local-work-store.md").read_text(encoding="utf-8")
        normalized_planning = " ".join(planning.split())
        normalized_storage = " ".join(storage.split())

        for guidance in {
            "link each wayfinding decision and canonical domain or architecture record",
            "without copying its rationale or evidence",
            "implementation ticket's `Accepted sources`",
            "decisions, research, prototypes, or canonical records",
        }:
            self.assertIn(guidance, normalized_planning)

        for guidance in {
            "When `map.md` exists",
            "use `Frontier` to link the map",
            "rather than copying its decision list",
            "full decision frontier canonical in the map",
            "exact next action under `Continuation`",
        }:
            self.assertIn(guidance, normalized_storage)

    def test_retention_preserves_sources_in_their_intended_history(self) -> None:
        prototype = (PROCEDURES_ROOT / "prototype.md").read_text(encoding="utf-8")
        research = (PROCEDURES_ROOT / "research.md").read_text(encoding="utf-8")

        normalized_prototype = " ".join(prototype.split())
        normalized_research = " ".join(research.split())
        self.assertIn("normal repository history", normalized_prototype)
        self.assertIn(
            "committed with the completed outcome during delivery", normalized_prototype
        )
        self.assertIn("do not create a dedicated branch", normalized_prototype)
        self.assertNotIn("out of the main line", normalized_prototype)
        self.assertIn("normal repository history", normalized_research)
        self.assertIn(
            "commit it with the completed outcome during delivery", normalized_research
        )
        self.assertNotIn("out of the main line", normalized_research)
        self.assertNotIn("research/<name>", normalized_research)


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
        self.assertEqual(
            workflows["novel-work"]["work-record"],
            "storage/local-work-store.md",
        )
        record_path = REFERENCES_ROOT / cast(
            str, workflows["novel-work"]["work-record"]
        )
        self.assertTrue(record_path.is_file())

        record = record_path.read_text(encoding="utf-8")
        for phrase in {
            ".work/<effort-slug>/",
            "uncommitted continuation record",
            "Commit the current effort record with the completed outcome "
            "during delivery",
            "Do not commit planning artifacts",
            "status.md",
            "map.md",
            "decisions/",
            "tickets/",
            "research/",
            "prototypes/",
        }:
            self.assertIn(phrase, record)

    def test_local_work_guidance_does_not_expose_external_trackers(self) -> None:
        paths = [
            STORAGE_ROOT / "local-work-store.md",
            FORMATS_ROOT / "wayfinding.md",
            FORMATS_ROOT / "planning-artifacts.md",
        ]
        guidance = "\n".join(
            path.read_text(encoding="utf-8") for path in paths
        ).casefold()

        for term in {"github", "linear", "external tracker"}:
            self.assertNotIn(term, guidance)

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

    def test_planning_procedures_do_not_control_state(self) -> None:
        for procedure_name in {"prototype", "wayfinding"}:
            procedure = (PROCEDURES_ROOT / f"{procedure_name}.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("## Result", procedure)
            self.assertNotIn("return", procedure.casefold())


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

        self.assertIn("# Discovery State", output)
        self.assertIn("`research` (allowed)", output)
        self.assertIn("procedure question discovery research", output)
        self.assertIn("move question discovery answer", output)
        self.assertIn("## Resume", output)
        self.assertIn("resume question discovery", output)
        for unrelated in {
            "# Planning State",
            "# Implementation State",
            "# Validation State",
            "# Delivery State",
            "# Research Procedure",
            "# Testing Procedure",
            "# Verification Procedure",
        }:
            self.assertNotIn(unrelated, output)

    def test_triggered_procedures_are_discoverable_but_not_preloaded(self) -> None:
        output = self.run_navigator("start", "novel-work").stdout

        for procedure_name in {
            "domain-modeling",
            "interface-design",
            "prototype",
            "wayfinding",
        }:
            self.assertIn(f"`{procedure_name}` (triggered)", output)
            self.assertIn(f"procedure novel-work planning {procedure_name}", output)
        for heading in {
            "# Domain Modeling Procedure",
            "# Interface Design Procedure",
            "# Prototype Procedure",
            "# Wayfinding Procedure",
        }:
            self.assertNotIn(heading, output)
        self.assertIn("format novel-work planning planning-artifacts", output)
        self.assertNotIn("# Planning Artifact Formats", output)

    def test_required_procedures_are_preloaded_in_manifest_order(self) -> None:
        output = self.run_navigator("resume", "tweak", "delivery").stdout

        review = output.index("# Review Procedure")
        documentation = output.index("# Documentation Procedure")
        commit = output.index("# Commit Procedure")
        self.assertLess(documentation, review)
        self.assertLess(review, commit)
        for procedure_name in {"review", "documentation", "commit"}:
            self.assertIn(f"`{procedure_name}` (required)", output)

    def test_fix_workflow_preloads_diagnosis_during_discovery(self) -> None:
        output = self.run_navigator("start", "fix").stdout

        self.assertIn("`diagnose` (required)", output)
        self.assertIn("# Diagnose Procedure", output)
        self.assertIn("resume fix discovery", output)
        self.assertNotIn("--variant", output)

    def test_every_active_state_exposes_an_exact_resume_command(self) -> None:
        for workflow_name, workflow in load_workflows().items():
            states = cast(dict[str, object], workflow["states"])
            for state_name in states:
                with self.subTest(workflow=workflow_name, state=state_name):
                    output = self.run_navigator(
                        "resume", workflow_name, state_name
                    ).stdout
                    self.assertIn("## Resume", output)
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

        self.assertIn("Procedure status: triggered", available.stdout)
        self.assertIn("# Prototype Procedure", available.stdout)
        self.assertEqual(unavailable.stdout, "")
        self.assertIn("is unavailable", unavailable.stderr)

    def test_procedure_exposes_only_its_associated_formats(self) -> None:
        output = self.run_navigator(
            "procedure", "novel-work", "planning", "domain-modeling"
        ).stdout

        self.assertIn(
            "format novel-work planning domain-modeling --procedure domain-modeling",
            output,
        )
        self.assertNotIn("format novel-work planning wayfinding", output)
        self.assertNotIn("# Domain Documentation Formats", output)

    def test_procedure_exposes_only_declared_related_procedure_cues(self) -> None:
        output = self.run_navigator(
            "procedure", "novel-work", "planning", "wayfinding"
        ).stdout

        self.assertIn("## Related procedures", output)
        for procedure_name in {
            "research",
            "prototype",
            "domain-modeling",
            "interface-design",
        }:
            self.assertIn(f"`{procedure_name}`", output)
            self.assertIn(f"procedure novel-work planning {procedure_name}", output)
        self.assertNotIn("`testing`", output)
        self.assertNotIn("# Research Procedure", output)
        self.assertNotIn("# Prototype Procedure", output)
        self.assertNotIn("# Domain Modeling Procedure", output)
        self.assertNotIn("# Interface Design Procedure", output)

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

        self.assertIn("Procedure status: triggered", planning)
        self.assertIn("# Interface Design Procedure", planning)
        self.assertIn("## Related procedures", planning)
        self.assertIn("`prototype`", planning)
        self.assertIn("# Interface Design Procedure", implementation)
        self.assertNotIn("## Related procedures", implementation)
        self.assertIn("is unavailable", unavailable.stderr)

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

        self.assertIn("# Planning Artifact Formats", state_format)
        self.assertIn("# Wayfinding Formats", procedure_format)
        self.assertIn("[<Decision title>](decisions/<NN>-<slug>.md)", procedure_format)
        self.assertIn("is unavailable", unavailable.stderr)

    def test_move_requires_an_available_destination(self) -> None:
        valid = self.run_navigator("move", "tweak", "validation", "delivery").stdout
        invalid = self.run_navigator(
            "move",
            "tweak",
            "discovery",
            "delivery",
            expected_returncode=2,
        )

        self.assertIn("# Delivery State", valid)
        self.assertIn("# Commit Procedure", valid)
        self.assertIn("Cannot move", invalid.stderr)

    def test_cross_workflow_move_loads_the_new_workflow_context(self) -> None:
        output = self.run_navigator(
            "move", "fix", "discovery", "novel-work.planning"
        ).stdout

        self.assertIn("# Planning State", output)
        self.assertIn("# Local Work Store", output)
        self.assertIn("procedure novel-work planning prototype", output)
        self.assertIn("resume novel-work planning", output)

    def test_complete_move_returns_to_the_null_state(self) -> None:
        output = self.run_navigator("move", "question", "answer", "complete").stdout

        self.assertEqual(output, "Workflow complete: question\n")


class ProcedureQualityTests(unittest.TestCase):
    def test_commit_procedure_preserves_commit_policy(self) -> None:
        commit = (PROCEDURES_ROOT / "commit.md").read_text(encoding="utf-8")

        for heading in {
            "## Decide whether to commit",
            "## Compose the commits",
            "## Write the subject",
            "## Result",
        }:
            self.assertIn(heading, commit)

        self.assertNotIn("## Stage deliberately", commit)
        self.assertNotIn("### ", commit)
        self.assertNotIn("delivery", commit.casefold())
        self.assertLess(len(commit.split()), 500)

        for slug in {
            "[Feature]",
            "[Fix]",
            "[Tweak]",
            "[Refactor]",
            "[Optimization]",
            "[Documentation]",
            "[Design]",
            "[Cleanup]",
            "[Chore]",
        }:
            self.assertIn(f"`{slug}`", commit)

        for guidance in {
            "one concrete outcome",
            "under 50 characters",
            "imperative verb",
            "recent commits",
            "Group changes by completed outcome",
            "Squash local commits that describe the same outcome",
            "Include my changes with yours",
            "Draft a subject for each proposed commit",
            "Preserve unrelated and unfinished changes exactly as found",
            "any intentionally uncommitted changes",
        }:
            self.assertIn(guidance, commit)

    def test_delegate_procedure_preserves_delegation_policy(self) -> None:
        delegate = (PROCEDURES_ROOT / "delegate.md").read_text(encoding="utf-8")
        normalized_delegate = " ".join(delegate.split())

        for heading in {
            "## Define the assignment",
            "## Protect ownership",
            "## Integrate the result",
            "## Result",
        }:
            self.assertIn(heading, delegate)

        self.assertNotIn("### ", delegate)
        self.assertNotIn("to implementation", delegate.casefold())
        self.assertNotIn("whether it may commit", delegate.casefold())
        self.assertNotIn("changed paths or commits", delegate.casefold())
        self.assertNotIn("keep the work local", delegate.casefold())
        self.assertNotIn("verification evidence", delegate.casefold())
        self.assertNotIn("focused regression coverage", delegate.casefold())
        self.assertNotIn(
            "focused tests and applicable lint or type checks", delegate.casefold()
        )
        self.assertLess(len(delegate.split()), 350)

        for guidance in {
            "one independently completable outcome",
            "observable result and its acceptance checks",
            "Accepted decisions and source artifacts",
            "accepted ticket, relevant artifact paths",
            "Exclude unrelated history and unresolved reasoning",
            "outcome, authority, or writable scope cannot be bounded",
            "Explicit writable file scope",
            "one owner at a time",
            "Do not delegate overlapping scopes in parallel",
            "Restrict the subagent to read-only Git inspection",
            "must not stage, commit, change branches",
            "otherwise mutate repository state through Git",
            "existing tests or other checks the subagent must make pass",
            "focused test has failed for the expected reason",
            "does not establish the test-first boundary",
            "run the named assignment checks until they pass",
            "Do not ask it to add broader coverage",
            "does not validate the integrated outcome",
            "Do not accept a completion summary as proof",
            "new bounded outcome",
            "named check results",
        }:
            self.assertIn(guidance, normalized_delegate)

    def test_diagnose_procedure_preserves_diagnostic_policy(self) -> None:
        diagnose = (PROCEDURES_ROOT / "diagnose.md").read_text(encoding="utf-8")
        normalized_diagnose = " ".join(diagnose.split())

        for heading in {
            "## Reproduce the symptom",
            "## Establish the cause and boundary",
            "## Result",
        }:
            self.assertIn(heading, diagnose)

        self.assertNotIn("### ", diagnose)
        self.assertNotIn("fix variant", diagnose.casefold())
        self.assertNotIn("to discovery", diagnose.casefold())
        self.assertLess(len(diagnose.split()), 350)

        for guidance in {
            "same action, interface, data, and relevant environment",
            "implementation proxy for direct evidence",
            "exact triggering action and target element",
            "exact post-action state",
            "cannot replace visual inspection",
            "Report the unresolved reproduction instead of inventing a cause",
            "first incorrect state, value, transition, or violated contract",
            "Distinguish confirmed facts from remaining hypotheses",
            "smallest observable behavior and conditions a focused test must cover",
            "concrete acceptance check",
            "Do not change production or test code",
            "next bounded investigation",
        }:
            self.assertIn(guidance, normalized_diagnose)

    def test_documentation_procedure_preserves_documentation_policy(self) -> None:
        documentation = (PROCEDURES_ROOT / "documentation.md").read_text(
            encoding="utf-8"
        )
        normalized_documentation = " ".join(documentation.split())

        for heading in {
            "## Decide the impact",
            "## Update canonical knowledge",
            "## Result",
        }:
            self.assertIn(heading, documentation)

        self.assertNotIn("### ", documentation)
        self.assertNotIn("to delivery", documentation.casefold())
        self.assertLess(len(documentation.split()), 350)

        for guidance in {
            "may conclude that no documentation change is needed",
            "future developer, operator, or consumer must know",
            "Do not document temporary process, narrate the diff, restate code",
            "report the gap instead of rewriting durable knowledge",
            "existing canonical source",
            "Keep each meaning in one place",
            "work record exists",
            "Keep it an index",
            "does not repeat implementation validation",
            "documentation-impact decision",
            "why existing knowledge remains sufficient",
        }:
            self.assertIn(guidance, normalized_documentation)

    def test_domain_modeling_procedure_preserves_domain_policy(self) -> None:
        domain_modeling = (PROCEDURES_ROOT / "domain-modeling.md").read_text(
            encoding="utf-8"
        )
        normalized_domain_modeling = " ".join(domain_modeling.split())

        for heading in {
            "## Decide what is durable",
            "## Record it once",
            "## Result",
        }:
            self.assertIn(heading, domain_modeling)

        self.assertNotIn("### ", domain_modeling)
        self.assertNotIn("during planning", domain_modeling.casefold())
        self.assertNotIn("to planning", domain_modeling.casefold())
        self.assertLess(len(domain_modeling.split()), 300)

        for guidance in {
            "Record accepted decisions; do not make them through documentation",
            "project-specific concept used across a meaningful boundary",
            "costly to reverse, surprising without context",
            "Leave proposed terminology, open choices, implementation plans",
            "ordinary programming vocabulary",
            "one canonical term",
            "free of implementation detail",
            "Do not turn it into a specification, ticket, or progress log",
            "Supersede an obsolete decision",
            "Link specifications, work records, and related decisions",
            "working artifact because it remains unsettled",
        }:
            self.assertIn(guidance, normalized_domain_modeling)

    def test_prototype_procedure_preserves_prototyping_policy(self) -> None:
        prototype = (PROCEDURES_ROOT / "prototype.md").read_text(encoding="utf-8")
        normalized_prototype = " ".join(prototype.split())

        for heading in {
            "## Frame the decision",
            "## Build and iterate",
            "## Settle and preserve",
            "## Result",
        }:
            self.assertIn(heading, prototype)

        self.assertNotIn("### ", prototype)
        self.assertNotIn("during planning", prototype.casefold())
        self.assertNotIn("to planning", prototype.casefold())
        self.assertLess(len(prototype.split()), 650)

        for guidance in {
            "one unresolved decision",
            "observable evidence",
            "cheapest form with enough fidelity",
            "one answerable question",
            "meaningfully different structures",
            "relevant state",
            "Reuse the repository's established stack",
            "separation of purpose and execution path",
            "Build only what affects the decision",
            "Exercise the decision-bearing behavior directly",
            "Do not add production regression coverage",
            "preference export only when",
            "Let me react and iterate",
            "If the same effect fails twice",
            "supporting a possibility, rejecting it, or remaining inconclusive",
            "Do not turn an inconclusive result into an accepted decision",
            "binding primary source",
            "Binding qualities",
            "Flexible qualities",
            "obtain my explicit confirmation",
            "effort's `prototypes/` directory",
            "normal repository history",
            "committed with the completed outcome during delivery",
            "do not create a dedicated branch",
            "Production implementation remains separate work",
            "Prototype acceptance does not make prototype code production-ready",
        }:
            self.assertIn(guidance, normalized_prototype)

    def test_interface_design_procedure_preserves_design_policy(self) -> None:
        design = (PROCEDURES_ROOT / "interface-design.md").read_text(encoding="utf-8")
        normalized_design = " ".join(design.split())

        for heading in {
            "## Ground the direction",
            "## Plan a specific design",
            "## Build and critique",
            "## Result",
        }:
            self.assertIn(heading, design)

        self.assertNotIn("### ", design)
        self.assertNotIn("during planning", design.casefold())
        self.assertNotIn("during implementation", design.casefold())
        self.assertNotIn("to validation", design.casefold())
        self.assertLess(len(design.split()), 1100)

        for guidance in {
            "accepted intent",
            "established design system",
            "accepted prototype",
            "consumer's primary task",
            "real content",
            "consequential visual choice",
            "do not invent it",
            "subject's own materials",
            "design lead",
            "distinctive point of view",
            "one real aesthetic risk",
            "primary surface is a thesis",
            "Typography carries personality",
            "Structural devices",
            "Motion must serve the subject",
            "generic model defaults",
            "warm cream",
            "near-black",
            "broadsheet",
            "legitimate when the subject calls for them",
            "compact design plan",
            "four to six named colors",
            "two or more type roles",
            "ASCII wireframes",
            "one signature element",
            "could belong unchanged to an unrelated product",
            "Match complexity to the direction",
            "Structure must communicate",
            "Cards must represent genuine grouping",
            "dark and light themes",
            "adaptive units",
            "reactive as data changes",
            "reduced motion",
            "keyboard operation",
            "consumer's side of the interface",
            "sales pitch",
            "active voice",
            "same way through the interaction",
            "Errors explain what happened and how to recover",
            "Each element does one job",
            "Render and inspect the interface",
            "structural representation",
            "does not establish completion evidence",
            "accepted or applied direction",
            "unresolved design decision",
        }:
            self.assertIn(guidance, normalized_design)

    def test_research_procedure_preserves_research_policy(self) -> None:
        research = (PROCEDURES_ROOT / "research.md").read_text(encoding="utf-8")
        normalized_research = " ".join(research.split())

        for heading in {
            "## Frame the question",
            "## Investigate",
            "## Assess and preserve",
            "## Result",
        }:
            self.assertIn(heading, research)

        self.assertNotIn("### ", research)
        self.assertNotIn("to discovery", research.casefold())
        self.assertNotIn("to planning", research.casefold())
        self.assertNotIn("substantial", research.casefold())
        self.assertLess(len(research.split()), 500)

        for guidance in {
            "one bounded factual question",
            "return the remaining judgment to me",
            "Inspect the current repository directly",
            "ordinary context gathering and must not be replaced by delegation",
            "fresh-context subagent when available for external multi-source "
            "investigation",
            "Do not delegate repository orientation or reading a handful of "
            "relevant files",
            "only after you have inspected its decision-bearing sources directly",
            "Do not supply a preferred conclusion",
            "subagent's Git access read-only",
            "must not stage, commit, alter repository history",
            "Search through more than one approach and source",
            "alternate terminology and search paths",
            "original, authoritative, and current sources",
            "repeated copies of one claim",
            "Investigate conflicts",
            "commands and experiments bounded to the question",
            "confirm that each citation supports the claim",
            "established facts, supported inferences, recommendations",
            "evidence is insufficient",
            "dedicated report only when future work will need to revisit",
            "`.work/<effort-slug>/research/<research-slug>.md`",
            "commit it with the completed outcome during delivery",
            "Link external and repository sources",
            "Otherwise keep the finding in its owning answer",
            "remains mine to resolve",
        }:
            self.assertIn(guidance, normalized_research)

    def test_review_procedure_preserves_review_policy(self) -> None:
        review = (PROCEDURES_ROOT / "review.md").read_text(encoding="utf-8")
        normalized_review = " ".join(review.split())

        for heading in {
            "## Establish the review scope",
            "## Dispatch independent review",
            "## Adjudicate findings",
            "## Result",
        }:
            self.assertIn(heading, review)

        self.assertNotIn("### ", review)
        self.assertNotIn("state responsible", review.casefold())
        self.assertNotIn("to delivery", review.casefold())
        self.assertNotIn("comparison base", review.casefold())
        self.assertNotIn("staged", review.casefold())
        self.assertNotIn("pinned", review.casefold())
        self.assertNotIn("completion suites", review.casefold())
        self.assertNotIn("workflow can route", review.casefold())
        self.assertLess(len(review.split()), 500)

        for guidance in {
            "accepted intent and engineering risk",
            "complete work for the accepted outcome",
            "including every task-owned change",
            "task scope cannot be identified, do not dispatch review",
            "my request, acceptance checks, specification or ticket",
            "without prior conclusions, suspected defects",
            "separate fresh-context subagents for the intent and engineering axes",
            "genuinely small, low-risk change",
            "do not claim independent review",
            "exact file and Git boundaries",
            "must not edit or format files, stage or commit changes",
            "must not rerun validation checks",
            "Intent axis",
            "Engineering axis",
            "violated source or observable consequence",
            "objective defects, judgment calls, and missing evidence",
            "state `no findings` when an axis is clean",
            "Validate every finding against the complete work",
            "reviewer agreement does not replace direct evidence",
            "Do not modify the work while reviewing it",
            "validated problem makes the review fail",
            "After remediation and renewed validation",
            "whether they were independent",
        }:
            self.assertIn(guidance, normalized_review)

    def test_testing_procedure_preserves_test_first_policy(self) -> None:
        testing = (PROCEDURES_ROOT / "testing.md").read_text(encoding="utf-8")
        normalized_testing = " ".join(testing.split())

        for heading in {
            "## Choose the test boundary",
            "## Run the loop",
            "## Preserve durable coverage",
            "## Result",
        }:
            self.assertIn(heading, testing)

        self.assertNotIn("### ", testing)
        self.assertNotIn("during implementation", testing.casefold())
        self.assertNotIn("validation", testing.casefold())
        self.assertLess(len(testing.split()), 450)

        for guidance in {
            "focused red-green-refactor loop",
            "highest stable public seam",
            "derive expected values independently",
            "focused failing regression test established by diagnosis",
            "write the focused test before changing production code",
            "fails for the wrong reason",
            "Add only enough production behavior",
            "dependency injection",
            "Correct every red or flaky test",
            "observable capabilities in domain language",
            "focused integration coverage",
            "Do not mock owned collaborators",
            "removed behavior remains absent",
            "observed red and green results",
        }:
            self.assertIn(guidance, normalized_testing)

    def test_validation_state_preserves_completion_policy(self) -> None:
        validation = (STATES_ROOT / "validation.md").read_text(encoding="utf-8")
        normalized_validation = " ".join(validation.split())

        for heading in {
            "## Define the evidence",
            "## Run and inspect",
            "## Adjudicate failures",
            "## Record current evidence",
            "## Continue",
        }:
            self.assertIn(heading, validation)

        self.assertNotIn("### ", validation)
        self.assertLess(len(validation.split()), 800)

        for guidance in {
            "current, direct evidence",
            "sufficiency of completion evidence",
            "Map each acceptance check",
            "repository's configured commands rather than guessing",
            "changed surface, affected dependencies, and risk",
            "formatting with no remaining drift",
            "every configured linter with no outstanding finding",
            "every configured type checker passing",
            "no use of `Any` unless no sensible typed alternative exists",
            "affected regression suites",
            "direct execution of the accepted behavior",
            "Every selected check must pass",
            "Treat a red or flaky test as an implementation failure",
            "unavailable evidence is not a pass",
            "same action through the same interface",
            "operate the rendered interface yourself",
            "exact triggering action on the exact target",
            "observe the post-action state in the interface",
            "Take screenshots while exercising each relevant visual state",
            "inspect every screenshot yourself",
            "available structural representation, such as a DOM",
            "accessibility tree, or component hierarchy",
            "element identity, state, semantics, and layout relationships",
            "actual rendered appearance",
            "Neither substitutes for the other",
            "Automated assertions, unattended scripts, and artifact generation",
            "do not substitute for direct operation and inspection",
            "accepted prototype exists",
            "Screenshots are temporary inspection aids",
            "remove them after visual validation",
            "do not commit or link them as durable artifacts",
            "Classify each failure",
            "remains in validation",
            "belongs to implementation",
            "earliest available state that can resolve it",
            "Do not modify production code, tests, or repository tooling",
            "Record exact commands",
            "Invalidate any evidence affected by later changes",
            "Continue to delivery when every accepted check",
        }:
            self.assertIn(guidance, normalized_validation)

    def test_wayfinding_procedure_preserves_wayfinding_policy(self) -> None:
        wayfinding = (PROCEDURES_ROOT / "wayfinding.md").read_text(encoding="utf-8")
        normalized_wayfinding = " ".join(wayfinding.split())
        wayfinding_format = (FORMATS_ROOT / "wayfinding.md").read_text(encoding="utf-8")
        normalized_format = " ".join(wayfinding_format.split())

        for heading in {
            "## Establish the destination",
            "## Work the frontier",
            "## Update the record",
            "## Result",
        }:
            self.assertIn(heading, wayfinding)

        self.assertNotIn("### ", wayfinding)
        self.assertNotIn("use during planning", wayfinding.casefold())
        self.assertNotIn("planning owns", wayfinding.casefold())
        self.assertNotIn("state transition", wayfinding.casefold())
        self.assertLess(len(wayfinding.split()), 550)

        for guidance in {
            "visible decision map",
            "Plan decisions, not production work",
            "one or two observable sentences",
            "uncertain but potentially relevant terrain",
            "questions that can be stated precisely",
            "Do not enumerate speculative questions",
            "precise, open, unblocked, and unclaimed decision tickets",
            "Claim one before working it",
            "Wayfinding · <n> resolved · <n> visible",
            "recommend an answer with the decisive reason",
            "ask one primary question",
            "two or three tightly coupled questions",
            "Do not serialize questions",
            "Do not paste the decision map into conversation",
            "completion percentage or fixed question count",
            "factual uncertainty through research",
            "concrete reaction through a prototype",
            "never production implementation",
            "requires my judgment",
            "advance an unrelated frontier decision",
            "record the resolution and supporting evidence once",
            "Recompute the frontier and remaining fog",
            "domain modeling to record the canonical knowledge",
            "Keep the map an index rather than a transcript or specification",
            "must not become production implementation tickets",
            "without inventing intent",
            "zero visible decisions and no remaining in-scope fog",
        }:
            self.assertIn(guidance, normalized_wayfinding)

        for guidance in {
            "Use `Type` to identify how the question will be settled",
            "`discussion` requires my judgment",
            "`research` requires factual investigation",
            "`prototype` requires concrete exploration",
            "`task` requires a prerequisite action",
            "without implementing the destination",
            "resolution, rationale, and consequences",
            "canonical domain or architecture records",
        }:
            self.assertIn(guidance, normalized_format)


if __name__ == "__main__":
    unittest.main()
