from __future__ import annotations

import json
import unittest

from evals.assessment import apply_assessment, blind_packet
from evals.assessment_models import AssessmentResult
from evals.evidence import EvidenceRun
from evals.fixtures import make_workspace
from evals.models import CaseSpec, OnlyChangedCheck, PythonCheck, UnchangedCheck
from evals.runner import Observation, check_result, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


def assessed_case(**updates: object) -> CaseSpec:
    return CaseSpec.model_validate(
        {
            "id": "question",
            "tags": [],
            "purpose": "task",
            "files": {"src/app.py": "answer = 42\n"},
            "rubric": [
                {"id": "answer", "description": "Explain the current return value."},
                {"id": "evidence", "description": "Use the existing implementation."},
                {"id": "boundaries", "description": "Preserve the reviewed source."},
            ],
            "steps": [
                {
                    "kind": "message",
                    "prompt": "What is the answer?",
                    "checks": [{"kind": "no_publish"}],
                }
            ],
            **updates,
        }
    )


class CorpusAssessmentTests(unittest.TestCase):
    def test_damaged_navigation_is_evidence_rather_than_a_capture_error(self) -> None:
        case = assessed_case(
            steps=[
                {"kind": "seed", "workflow": "novel-work", "state": "planning"},
                {"kind": "edit", "navigation_text": "{broken"},
                {
                    "kind": "message",
                    "prompt": "Resume the current work.",
                    "checks": [{"kind": "no_publish"}],
                },
            ]
        )
        evidence = EvidenceRun("private", "model", "source")
        result = run_case(
            case,
            SOURCE,
            "fake",
            driver_factory=lambda *a: FakeDriver(),
            on_observation=evidence.observe,
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(evidence.frames[0].progress, {"invalid_json": "{broken"})

    def test_supplied_file_changes_are_distinguished_from_candidate_edits(self) -> None:
        case = assessed_case(
            steps=[
                {"kind": "edit", "files": {"src/app.py": "answer = 7\n"}},
                {
                    "kind": "message",
                    "prompt": "What is the answer now?",
                    "checks": [{"kind": "no_publish"}],
                },
            ]
        )
        evidence = EvidenceRun("private", "model", "source")
        run_case(
            case,
            SOURCE,
            "fake",
            driver_factory=lambda *a: FakeDriver(),
            on_observation=evidence.observe,
        )
        self.assertEqual(
            [f.event for f in evidence.frames], ["fixture_edit", "message"]
        )
        self.assertEqual(evidence.frames[0].files["src/app.py"], "answer = 7\n")
        self.assertEqual(evidence.frames[0].commands, [])

    def test_issue_edits_preserve_the_starting_tracker_context_for_assessment(
        self,
    ) -> None:
        case = assessed_case(tracker="github", github_issues={"10": "CSV accepted."})
        with make_workspace(SOURCE, case) as workspace:
            path = workspace.home / "work-system/github.json"
            state = json.loads(path.read_text())
            state["issues"]["10"]["body"] = "CSV accepted. Empty input refuses export."
            path.write_text(json.dumps(state))
            evidence = EvidenceRun("private", "model", "source")
            evidence.observe(
                workspace,
                0,
                "actual-thread-id",
                "Record the empty-input answer.",
                Observation(),
            )
            self.assertIn("CSV accepted.", str(evidence.initial_service_state))
            self.assertNotIn("refuses", str(evidence.initial_service_state))
            packet, _ = blind_packet(case.rubric, [evidence])
            self.assertIn("initial_service_state", json.dumps(packet))
            self.assertIn("Empty input refuses export.", json.dumps(packet))

    def test_public_project_check_keeps_its_file_location(self) -> None:
        case = assessed_case(
            files={
                "src/value.txt": "42",
                "checks/check_value.py": (
                    "from pathlib import Path\n"
                    "assert (Path(__file__).resolve().parents[1] / "
                    "'src/value.txt').read_text() == '42'\n"
                ),
            }
        )
        with make_workspace(SOURCE, case) as workspace:
            check = PythonCheck(path="checks/check_value.py")
            self.assertTrue(check_result(check, Observation(), workspace, "t", [])[0])
            workspace.file("src/value.txt").write_text("7")
            self.assertFalse(check_result(check, Observation(), workspace, "t", [])[0])

    def test_reply_only_tasks_support_hidden_assessment(self) -> None:
        case = assessed_case()
        result = run_case(case, SOURCE, "fake", driver_factory=lambda *a: FakeDriver())
        self.assertEqual(result.status, "inconclusive")
        self.assertEqual(result.mechanical_status, "pass")
        apply_assessment(result, AssessmentResult("pass", "judge"))
        self.assertEqual(result.status, "pass")

    def test_project_observation_ignores_cache_but_detects_real_source_changes(
        self,
    ) -> None:
        case = assessed_case()
        with make_workspace(SOURCE, case) as w:
            cache = w.file("src/__pycache__/app.pyc")
            cache.parent.mkdir()
            cache.write_bytes(b"\x00\xffbinary")
            run = EvidenceRun("private", "model", "source")
            run.observe(w, 0, "thread", "Question", Observation())
            self.assertNotIn("src/__pycache__/app.pyc", run.frames[0].files)
            check = UnchangedCheck(paths=["src"])
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            w.file("src/added.py").write_text("new = True\n")
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            w.file("src/added.py").unlink()
            w.file("src/app.py").write_text("answer = 7\n")
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_change_permissions_allow_files_inside_an_allowed_directory(self) -> None:
        with make_workspace(SOURCE, assessed_case()) as w:
            path = w.file("tests/test_answer.py")
            path.parent.mkdir()
            path.write_text("pass\n")
            check = OnlyChangedCheck(paths=["tests"])
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            w.file("src/app.py").write_text("answer = 7\n")
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_compaction_and_tracker_records_enter_the_judging_evidence(self) -> None:
        case = assessed_case(
            integration=True,
            tracker="github",
            github_issues={"10": "Accepted search."},
            steps=[
                {
                    "kind": "message",
                    "prompt": "What remains?",
                    "checks": [{"kind": "no_publish"}],
                },
                {"kind": "compact"},
            ],
        )
        evidence = EvidenceRun("private", "model", "source")
        result = run_case(
            case,
            SOURCE,
            "fake",
            driver_factory=lambda *a: FakeDriver(),
            on_observation=evidence.observe,
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual([f.event for f in evidence.frames], ["message", "compaction"])
        self.assertIn("Accepted search.", str(evidence.frames[0].service_state))
