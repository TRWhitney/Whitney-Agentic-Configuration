from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import cast

import yaml

REPO_ROOT = Path(__file__).parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
EXPECTED_SKILLS = {
    "diagnose-fix",
    "document-change",
    "handoff-work",
    "implement-work",
    "manage-work",
    "plan-work",
    "prototype-decision",
    "review-change",
    "test-first",
    "verify-change",
    "wayfind-work",
}
FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<yaml>.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^]]*]\(([^)]+)\)")
SKILL_REFERENCE_PATTERN = re.compile(r"\$([a-z0-9-]+)")


def load_yaml_mapping(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise AssertionError(f"{path} must contain a YAML mapping")
    return cast(dict[str, object], loaded)


def load_skill(skill_name: str) -> tuple[dict[str, object], str]:
    path = SKILLS_ROOT / skill_name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(text)
    if match is None:
        raise AssertionError(f"{path} must start with YAML frontmatter")
    metadata = yaml.safe_load(match.group("yaml"))
    if not isinstance(metadata, dict):
        raise AssertionError(f"{path} frontmatter must be a YAML mapping")
    return cast(dict[str, object], metadata), text[match.end() :]


class SkillStructureTests(unittest.TestCase):
    def test_repository_global_instructions_are_not_auto_discovered(self) -> None:
        instruction_path = REPO_ROOT / "config" / "global-agents.md"
        self.assertTrue(instruction_path.is_file())
        self.assertNotEqual(instruction_path.name, "AGENTS.md")
        self.assertGreater(instruction_path.stat().st_size, 0)

    def test_gitignore_covers_generated_python_artifacts(self) -> None:
        ignored = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", ignored)
        self.assertIn("*.py[cod]", ignored)
        self.assertIn(".mypy_cache/", ignored)
        self.assertIn(".ruff_cache/", ignored)

    def test_expected_skill_set_is_exact(self) -> None:
        actual = {path.name for path in SKILLS_ROOT.iterdir() if path.is_dir()}
        self.assertEqual(actual, EXPECTED_SKILLS)

    def test_frontmatter_is_minimal_and_trigger_focused(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            with self.subTest(skill=skill_name):
                metadata, body = load_skill(skill_name)
                self.assertEqual(set(metadata), {"name", "description"})
                self.assertEqual(metadata["name"], skill_name)
                description = metadata["description"]
                self.assertIsInstance(description, str)
                self.assertTrue(
                    cast(str, description).startswith("Use when "),
                    f"{skill_name} description must be a usage statement",
                )
                self.assertNotIn("TODO", body)
                self.assertLessEqual(len(body.splitlines()), 500)
                self.assertIn("## Completion", body)

    def test_openai_metadata_is_explicit_and_complete(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            with self.subTest(skill=skill_name):
                path = SKILLS_ROOT / skill_name / "agents" / "openai.yaml"
                metadata = load_yaml_mapping(path)
                self.assertEqual(set(metadata), {"interface", "policy"})
                interface = metadata.get("interface")
                policy = metadata.get("policy")
                self.assertIsInstance(interface, dict)
                self.assertIsInstance(policy, dict)
                interface_mapping = cast(dict[str, object], interface)
                policy_mapping = cast(dict[str, object], policy)
                self.assertEqual(
                    set(interface_mapping),
                    {"display_name", "short_description", "default_prompt"},
                )
                prompt = interface_mapping["default_prompt"]
                self.assertIsInstance(prompt, str)
                self.assertIn(f"${skill_name}", cast(str, prompt))
                short_description = interface_mapping["short_description"]
                self.assertIsInstance(short_description, str)
                self.assertGreaterEqual(len(cast(str, short_description)), 25)
                self.assertLessEqual(len(cast(str, short_description)), 64)
                expected_implicit_invocation = skill_name == "manage-work"
                self.assertIs(
                    policy_mapping.get("allow_implicit_invocation"),
                    expected_implicit_invocation,
                )

    def test_local_markdown_links_resolve(self) -> None:
        for skill_name in EXPECTED_SKILLS:
            skill_path = SKILLS_ROOT / skill_name / "SKILL.md"
            paths = [skill_path, *(skill_path.parent / "references").glob("*.md")]
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

    def test_reference_directories_are_not_empty(self) -> None:
        for references in SKILLS_ROOT.glob("*/references"):
            with self.subTest(skill=references.parent.name):
                self.assertTrue(any(references.iterdir()))

    def test_every_bundled_reference_is_discoverable_from_skill(self) -> None:
        for references in SKILLS_ROOT.glob("*/references"):
            skill_path = references.parent / "SKILL.md"
            skill_body = skill_path.read_text(encoding="utf-8")
            for reference in references.glob("*.md"):
                with self.subTest(
                    skill=references.parent.name, reference=reference.name
                ):
                    self.assertIn(
                        f"references/{reference.name}",
                        skill_body,
                        f"{reference} is not discoverable from {skill_path}",
                    )

    def test_cross_skill_references_resolve(self) -> None:
        for skill_path in SKILLS_ROOT.glob("*/SKILL.md"):
            body = skill_path.read_text(encoding="utf-8")
            for skill_name in SKILL_REFERENCE_PATTERN.findall(body):
                with self.subTest(source=skill_path.parent.name, target=skill_name):
                    self.assertIn(skill_name, EXPECTED_SKILLS)


class WorkflowContractTests(unittest.TestCase):
    def assert_skill_contains(self, skill_name: str, phrases: set[str]) -> None:
        _, body = load_skill(skill_name)
        for phrase in phrases:
            self.assertIn(phrase, body, f"{skill_name} is missing {phrase!r}")

    def assert_skill_contains_case_insensitive(
        self, skill_name: str, phrases: set[str]
    ) -> None:
        _, body = load_skill(skill_name)
        lowered_body = body.casefold()
        for phrase in phrases:
            self.assertIn(
                phrase.casefold(),
                lowered_body,
                f"{skill_name} is missing {phrase!r}",
            )

    def test_manage_work_routes_every_classification(self) -> None:
        self.assert_skill_contains(
            "manage-work",
            {
                "Fix route",
                "Tweak route",
                "Significant-feature route",
                "$diagnose-fix",
                "$wayfind-work",
                "$plan-work",
                "$implement-work",
                "$handoff-work",
            },
        )

    def test_implementation_composes_completion_disciplines(self) -> None:
        self.assert_skill_contains(
            "implement-work",
            {
                "$test-first",
                "$document-change",
                "$verify-change",
                "$review-change",
                "objective defect",
                "commit",
            },
        )
        _, body = load_skill("implement-work")
        record_position = body.index("Record completion evidence")
        commit_position = body.index("Commit only")
        self.assertLess(record_position, commit_position)

    def test_wayfinding_has_progress_and_interaction_contracts(self) -> None:
        self.assert_skill_contains(
            "wayfind-work",
            {
                "one primary question",
                "tightly coupled questions",
                "decisions settled",
                "visible frontier",
                "remaining fog",
                "Never estimate a percentage",
                "$plan-work",
            },
        )

    def test_prototype_settlement_is_a_hard_gate(self) -> None:
        self.assert_skill_contains(
            "prototype-decision",
            {
                "acceptance contract",
                "binding",
                "flexible",
                "explicit confirmation",
                "Export preferences",
                "permanent",
                "blocks planning",
                "light and dark",
                "tweak controls",
            },
        )

    def test_prototype_feedback_can_reference_named_elements(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "element identification",
                "hover labels",
                "stable names",
                "same names",
            },
        )

    def test_prototype_uses_the_repository_host_without_rebuilding_it(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "minimum shared host scaffold",
                "normal repository locations",
                "do not recreate the dependency tree",
                "decision-bearing prototype behavior",
                "source links",
            },
        )

    def test_prototype_iteration_resists_process_and_scope_expansion(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "smallest decision-bearing revision",
                "scope, infrastructure, controls, instrumentation, or process",
                "do not route prototype iteration through",
                "$diagnose-fix",
                "$implement-work",
                "$test-first",
                "$verify-change",
                "$review-change",
                "$document-change",
            },
        )
        self.assert_skill_contains_case_insensitive(
            "manage-work",
            {
                "active prototype",
                "return feedback to `$prototype-decision`",
                "do not reclassify",
            },
        )
        _, diagnosis_body = load_skill("diagnose-fix")
        diagnosis_metadata, _ = load_skill("diagnose-fix")
        diagnosis_description = diagnosis_metadata["description"]
        self.assertIsInstance(diagnosis_description, str)
        self.assertIn("production behavior", cast(str, diagnosis_description))
        self.assertIn("prototype feedback", diagnosis_body.casefold())
        self.assert_skill_contains_case_insensitive(
            "test-first",
            {
                "even when the prototype uses shared repository host scaffolding",
                "direct verification belongs to `$prototype-decision`",
            },
        )

    def test_prototype_iteration_has_a_repeated_failure_circuit_breaker(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "invalidate the previous verification",
                "same requested effect fails twice",
                "do not make another edit",
                "causal explanation",
                "do not claim that the instructions were sufficient",
            },
        )

    def test_prototype_iteration_proves_the_latest_requested_delta(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "latest explicit feedback",
                "observable delta",
                "before and after",
                "unaffected qualities",
                "only the states, themes, and viewports",
            },
        )
        prototype_forms = (
            SKILLS_ROOT / "prototype-decision" / "references" / "prototype-forms.md"
        ).read_text(encoding="utf-8")
        self.assertIn("initial alternatives", prototype_forms.casefold())
        self.assertIn("applying explicit feedback", prototype_forms.casefold())

    def test_workflow_profiles_keep_prototype_and_focused_work_proportionate(
        self,
    ) -> None:
        self.assert_skill_contains_case_insensitive(
            "manage-work",
            {
                "prototype-iteration profile",
                "focused-production profile",
                "full-production profile",
                "current explicit feedback",
                "standing production quality rules do not apply",
            },
        )
        self.assert_skill_contains_case_insensitive(
            "implement-work",
            {
                "completion profile",
                "focused-production",
                "full-production",
                "risk-based",
            },
        )
        self.assert_skill_contains_case_insensitive(
            "verify-change",
            {
                "focused-production",
                "full-production",
                "unrelated pre-existing failures",
            },
        )

    def test_prototype_support_apparatus_is_optional(self) -> None:
        self.assert_skill_contains_case_insensitive(
            "prototype-decision",
            {
                "only when it directly improves the named decision",
                "do not build it preemptively",
                "outside the prototype UI",
            },
        )

    def test_review_is_risk_based_and_respects_subagent_authority(self) -> None:
        self.assert_skill_contains(
            "review-change",
            {
                "Intent reviewer",
                "Engineering reviewer",
                "must not edit",
                "objective defects",
                "focused-production",
                "full-production",
                "user permits subagents",
                "do not claim clean-context independence",
            },
        )

    def test_production_completion_skills_exclude_active_prototypes(self) -> None:
        for skill_name in {"document-change", "review-change", "verify-change"}:
            with self.subTest(skill=skill_name):
                metadata, _ = load_skill(skill_name)
                description = metadata["description"]
                self.assertIsInstance(description, str)
                self.assertIn(
                    "do not use for active prototype",
                    cast(str, description).casefold(),
                )

    def test_testing_and_verification_have_distinct_gates(self) -> None:
        self.assert_skill_contains(
            "test-first",
            {"red", "green", "refactor", "public seam", "vertical slice"},
        )
        self.assert_skill_contains(
            "verify-change",
            {
                "formatter",
                "linter",
                "type checker",
                "full regression suite",
                "exact triggering action",
                "exact target element",
                "exact post-action state",
            },
        )

    def test_documentation_owns_only_durable_knowledge(self) -> None:
        self.assert_skill_contains(
            "document-change",
            {
                "documentation-impact",
                "ADR",
                "domain glossary",
                "README",
                "progress diary",
            },
        )

    def test_frontier_excludes_externally_blocked_items(self) -> None:
        for skill_name, path in {
            "manage-work": SKILLS_ROOT
            / "manage-work"
            / "references"
            / "local-work-store.md",
            "plan-work": SKILLS_ROOT / "plan-work" / "references" / "spec-and-items.md",
        }.items():
            with self.subTest(skill=skill_name):
                body = path.read_text(encoding="utf-8")
                self.assertIn("ready items whose dependencies are complete", body)

    def test_durable_evidence_requires_redaction(self) -> None:
        self.assert_skill_contains(
            "verify-change",
            {"Redact secrets", "commands", "screenshots", "traces"},
        )
        local_store = (
            SKILLS_ROOT / "manage-work" / "references" / "local-work-store.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Redact secrets", local_store)

    def test_transition_and_storage_ownership_are_explicit(self) -> None:
        for skill_name in {"diagnose-fix", "plan-work", "wayfind-work"}:
            self.assert_skill_contains_case_insensitive(
                skill_name, {"return control to `$manage-work`"}
            )
        _, plan_body = load_skill("plan-work")
        self.assertNotIn(
            "return that decision to `$wayfind-work`", plan_body.casefold()
        )
        for skill_name in {
            "handoff-work",
            "plan-work",
            "prototype-decision",
            "wayfind-work",
        }:
            self.assert_skill_contains(skill_name, {"active work adapter"})
        decision_map = (
            SKILLS_ROOT / "wayfind-work" / "references" / "decision-map.md"
        ).read_text(encoding="utf-8")
        self.assertIn("active work adapter", decision_map)
        self.assertIn("For the local adapter", decision_map)


if __name__ == "__main__":
    unittest.main()
