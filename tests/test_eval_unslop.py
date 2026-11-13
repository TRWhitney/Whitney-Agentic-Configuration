from __future__ import annotations

import unittest
from typing import ClassVar

from evals.assessment import blind_packet, judgment_schema
from evals.fixtures import make_workspace
from evals.models import CaseSpec, MessageStep, load_cases, select_cases
from evals.runner import Observation, check_result
from tests.evidence_support import evidence_text
from tests.test_eval_prose import record_case
from tests.test_eval_runner import SOURCE

CASE_IDS = {
    "unslop-final-reply",
    "unslop-vague-explanation",
    "unslop-concise-explanation",
    "unslop-revisions-retain-decisions",
    "unslop-clear-writing",
    "unslop-technical-terms",
}


class UnslopCaseTests(unittest.TestCase):
    corpus: ClassVar[list[CaseSpec]]
    cases: ClassVar[dict[str, CaseSpec]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_cases(SOURCE / "evals/cases")
        cls.cases = {case.id: case for case in cls.corpus if case.id in CASE_IDS}

    def test_valid_cases_are_selectable_with_separate_controls(self) -> None:
        self.assertEqual(set(self.cases), CASE_IDS)
        selected = select_cases(
            self.corpus, ids=set(), tags={"unslop"}, integration=False
        )
        self.assertEqual({case.id for case in selected}, CASE_IDS)
        controls = select_cases(
            selected, ids=set(), tags=set(), integration=False, purposes={"control"}
        )
        self.assertEqual(
            {case.id for case in controls},
            {"unslop-clear-writing", "unslop-technical-terms"},
        )
        for case in selected:
            with self.subTest(case=case.id):
                self.assertTrue(3 <= sum(c.required for c in case.rubric) <= 6)
                self.assertTrue(all(isinstance(s, MessageStep) for s in case.steps))
                self.assertFalse(case.integration)

    def test_optional_use_measurement_is_separate_from_quality(self) -> None:
        self.assertEqual(set(self.cases), CASE_IDS)
        for case in self.cases.values():
            with self.subTest(case=case.id):
                use = [c for c in case.rubric if c.id == "observed-unslop-use"]
                self.assertEqual(len(use), 1)
                self.assertFalse(use[0].required)
                self.assertTrue(all(c.required for c in case.rubric if c not in use))
                schema = judgment_schema(case.rubric, {"A"})
                properties = schema["properties"]
                assert isinstance(properties, dict)
                candidate = properties["A"]
                assert isinstance(candidate, dict)
                required = candidate["required"]
                assert isinstance(required, list)
                self.assertIn("observed-unslop-use", required)

    def test_docs_only_projects_keep_private_assessment_out_of_candidate_files(
        self,
    ) -> None:
        self.assertEqual(set(self.cases), CASE_IDS)
        for case in self.cases.values():
            with self.subTest(case=case.id), make_workspace(SOURCE, case) as workspace:
                self.assertFalse(case.fixtures)
                self.assertTrue(
                    all(p.startswith(("sources/", "docs/")) for p in case.files)
                )
                self.assertFalse(case.grader_files)
                for path, contents in case.files.items():
                    self.assertEqual(workspace.file(path).read_text(), contents)
                candidate_files = "\n".join(
                    contents.decode() for contents in workspace.project_files().values()
                )
                for criterion in case.rubric:
                    self.assertNotIn(criterion.description, candidate_files)
                    for step in case.steps:
                        assert isinstance(step, MessageStep)
                        self.assertNotIn(criterion.description, step.prompt)
                self.assertNotIn("evals/", "\n".join(workspace.project_files()))
                self.assertTrue((workspace.home / "skills/unslop/SKILL.md").is_file())
                self.assertFalse(workspace.home.is_relative_to(workspace.root))

    def test_source_preservation_accepts_outputs_and_rejects_changed_or_missing_sources(
        self,
    ) -> None:
        self.assertEqual(set(self.cases), CASE_IDS)
        for case in self.cases.values():
            with self.subTest(case=case.id), make_workspace(SOURCE, case) as workspace:
                source_path = next(p for p in case.files if p.startswith("sources/"))
                checks = [c for c in case.steps[0].checks if c.kind == "unchanged"]
                self.assertEqual(len(checks), 1)
                check = checks[0]
                self.assertTrue(
                    check_result(check, Observation(), workspace, "thread", [])[0]
                )
                if case.artifacts:
                    workspace.file(case.artifacts[0]).write_text(
                        "A revised document.\n"
                    )
                    self.assertTrue(
                        check_result(check, Observation(), workspace, "thread", [])[0]
                    )
                workspace.file(source_path).write_text("Changed source.\n")
                self.assertFalse(
                    check_result(check, Observation(), workspace, "thread", [])[0]
                )
                workspace.file(source_path).unlink()
                self.assertFalse(
                    check_result(check, Observation(), workspace, "thread", [])[0]
                )

    def test_final_reply_has_no_artifact_and_semantic_errors_reach_assessment(
        self,
    ) -> None:
        case = self.cases["unslop-final-reply"]
        self.assertEqual(case.artifacts, [])
        self.assertEqual(len(case.steps), 1)
        for reply in (
            "No. The hold expired at 14:55 without becoming a booking. "
            "The previous booking ends at 15:00, but that does not reserve Studio B "
            "for Mira. She needs a confirmed booking; the notes do not show "
            "whether anyone else has booked it.",
            "Yes, Mira can enter at 15:00 because an expired hold becomes confirmed.",
        ):
            with self.subTest(reply=reply):
                result, run = record_case(case, {}, reply)
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(reply, evidence_text(packet))
                self.assertEqual(len(run.frames), 1)

    def test_clear_control_accepts_unchanged_document(self) -> None:
        case = self.cases["unslop-clear-writing"]
        path = case.artifacts[0]
        result, run = record_case(case, {}, "The handout is ready to use.")
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertEqual(run.frames[0].files[path], case.files[path])
        packet, _ = blind_packet(case.rubric, [run])
        self.assertIn(case.files[path], evidence_text(packet))

    def test_technical_exact_contract_accepts_layout_variations_and_rejects_mutations(
        self,
    ) -> None:
        case = self.cases["unslop-technical-terms"]
        path = case.artifacts[0]
        exact = [c for c in case.steps[0].checks if c.kind == "file_regex"]
        self.assertEqual(len(exact), 2)
        command = "vaultctl verify --manifest snapshots/latest.json --read-only"
        quotation = "Verification checks stored bytes; it does not test a restore."
        for body in (
            f'Use `{command}`. The manual says, "{quotation}"\n',
            f"## Verify the snapshot\n\n```sh\n{command}\n```\n\n> {quotation}\n",
        ):
            with self.subTest(body=body), make_workspace(SOURCE, case) as workspace:
                workspace.file(path).write_text(body)
                self.assertTrue(
                    all(
                        check_result(c, Observation(), workspace, "t", [])[0]
                        for c in exact
                    )
                )
                for original, changed in (
                    ("--read-only", "--repair"),
                    ("does not test a restore", "proves a restore will work"),
                ):
                    workspace.file(path).write_text(body.replace(original, changed))
                    self.assertFalse(
                        all(
                            check_result(c, Observation(), workspace, "t", [])[0]
                            for c in exact
                        )
                    )
                workspace.file(path).unlink()
                self.assertFalse(
                    any(
                        check_result(c, Observation(), workspace, "t", [])[0]
                        for c in exact
                    )
                )

    def test_all_revisions_and_early_errors_remain_visible_to_the_judge(self) -> None:
        case = self.cases["unslop-revisions-retain-decisions"]
        self.assertEqual(len(case.steps), 3)
        path = case.artifacts[0]
        revisions = (
            "Visitors arrive at 10:00. Registration closes Wednesday at 18:00.\n",
            "Visitors arrive at 10:30. Registration closes Wednesday at 18:00. "
            "The venue emails waitlisted people when a place opens.\n",
            "Register by Wednesday at 18:00. Visitors arrive at 10:30. "
            "The venue emails waitlisted people when a place opens.\n",
        )
        result, run = record_case(case, tuple({path: text} for text in revisions))
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertEqual([frame.files[path] for frame in run.frames], list(revisions))
        packet, _ = blind_packet(case.rubric, [run])
        for text in revisions:
            self.assertIn(text, evidence_text(packet))

    def test_quality_is_not_a_fixed_vocabulary_or_word_count_contract(self) -> None:
        self.assertEqual(set(self.cases), CASE_IDS)
        for case in self.cases.values():
            with self.subTest(case=case.id):
                checks = [check for step in case.steps for check in step.checks]
                self.assertTrue(
                    all(
                        check.kind in {"unchanged", "file_regex", "no_publish"}
                        for check in checks
                    )
                )
                if case.id != "unslop-technical-terms":
                    self.assertFalse(
                        any(check.kind == "file_regex" for check in checks)
                    )


if __name__ == "__main__":
    unittest.main()
