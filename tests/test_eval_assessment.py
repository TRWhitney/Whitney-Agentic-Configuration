from __future__ import annotations

import json
import unittest

from evals.fixtures import make_workspace
from evals.models import CaseSpec
from evals.runner import Observation, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


class TaskDefinitionTests(unittest.TestCase):
    def definition(self) -> dict[str, object]:
        return {
            "id": "sample",
            "tags": [],
            "files": {"docs/guide.md": "draft\n"},
            "purpose": "task",
            "artifacts": ["docs/guide.md"],
            "rubric": [
                {"id": f"criterion-{i}", "description": f"Observable outcome {i}."}
                for i in range(3)
            ],
            "grader_files": {
                "checks/private.py": (
                    "from pathlib import Path\n"
                    'assert not Path("checks/private.py").exists()\n'
                )
            },
            "steps": [
                {
                    "kind": "message",
                    "prompt": "Write the guide.",
                    "checks": [{"kind": "python_check", "path": "checks/private.py"}],
                }
            ],
        }

    def test_private_assertions_run_without_entering_candidate_project(self) -> None:
        case = CaseSpec.model_validate(self.definition())
        with make_workspace(SOURCE, case) as w:
            self.assertFalse(w.file("checks/private.py").exists())
        result = run_case(
            case, SOURCE, "fake", driver_factory=lambda *args: FakeDriver()
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")

    def test_task_requires_hidden_criteria_and_private_file_isolation(self) -> None:
        data = self.definition()
        data["rubric"] = []
        with self.assertRaises(ValueError):
            CaseSpec.model_validate(data)
        data = self.definition()
        data["grader_files"] = {"docs/guide.md": "private"}
        with self.assertRaises(ValueError):
            CaseSpec.model_validate(data)


class BlindAssessmentTests(unittest.TestCase):
    def test_response_contract_matches_the_outputs_and_criteria_to_assess(self) -> None:
        from evals.assessment import blind_packet
        from evals.evidence import EvidenceRun
        from evals.models import RubricCriterion

        rubric = [RubricCriterion(id="answer", description="Answer the question.")]
        packet, _ = blind_packet(rubric, [EvidenceRun("case", "model", "source")])
        schema = packet["response_schema"]
        assert isinstance(schema, dict)
        self.assertEqual(schema["required"], ["A"])
        output = schema["properties"]["A"]
        self.assertEqual(output["required"], ["answer"])
        self.assertEqual(set(output["properties"]), {"answer"})
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(output["additionalProperties"])

    def test_label_and_criterion_keys_produce_a_complete_verdict(self) -> None:
        from evals.assessment import validate_judgment
        from evals.models import RubricCriterion

        rubric = [RubricCriterion(id="answer", description="Answer the question.")]
        result = validate_judgment(
            '{"A":{"answer":{"verdict":"met","evidence":["reply.txt"]}}}',
            {"A"},
            rubric,
        )
        self.assertEqual(result.candidates[0].criteria[0].verdict, "met")

    def test_packet_keeps_artifacts_and_hides_run_metadata(self) -> None:
        from evals.assessment import blind_packet
        from evals.evidence import EvidenceFrame, EvidenceRun
        from evals.models import RubricCriterion

        run = EvidenceRun(
            "private-case", "private-model", "private-variant", {"source.md": "facts"}
        )
        run.frames.append(
            EvidenceFrame(
                0,
                "main",
                "Write a guide.",
                "Done.",
                {"docs/guide.md": "Source validation: complete."},
                [],
                None,
                {},
            )
        )
        packet, labels = blind_packet(
            [RubricCriterion(id="purpose", description="Reader content stays useful.")],
            [run],
        )
        rendered = json.dumps(packet)
        for secret in ["private-case", "private-model", "private-variant"]:
            self.assertNotIn(secret, rendered)
        self.assertIn("Source validation: complete.", rendered)
        self.assertEqual(set(labels), {"A"})

    def test_missing_candidate_or_criterion_is_rejected(self) -> None:
        from evals.assessment import validate_judgment
        from evals.models import RubricCriterion

        rubric = [
            RubricCriterion(id="purpose", description="Reader content stays useful.")
        ]
        with self.assertRaises(ValueError):
            validate_judgment("{}", {"A"}, rubric)

    def test_duplicate_unknown_and_missing_criteria_are_rejected(self) -> None:
        from evals.assessment import validate_judgment
        from evals.models import RubricCriterion

        rubric = [RubricCriterion(id="purpose", description="Useful content.")]
        decision = '{"verdict":"met","evidence":["guide.md"]}'
        candidates = (
            '{"A":{"purpose":' + decision + '},"A":{"purpose":' + decision + "}}",
            '{"B":{"purpose":' + decision + "}}",
            '{"A":{"purpose":' + decision + ',"purpose":' + decision + "}}",
            '{"A":{"unknown":' + decision + "}}",
            '{"A":{}}',
            '{"A":{"purpose":{"verdict":"maybe","evidence":["guide.md"]}}}',
            '{"A":{"purpose":{"verdict":"met","evidence":[]}}}',
            '{"A":{"purpose":' + decision,
        )
        for value in candidates:
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_judgment(value, {"A"}, rubric)

    def test_unobserved_assignment_is_not_a_failed_agent_action(self) -> None:
        from evals.evidence import EvidenceRun
        from evals.runner import ObservedAction

        case = CaseSpec.model_validate(
            {
                "id": "observations",
                "tags": [],
                "files": {},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        run = EvidenceRun("private", "candidate", "condition")
        with make_workspace(SOURCE, case) as workspace:
            run.observe(
                workspace,
                0,
                "actual-thread",
                "Continue.",
                Observation(
                    actions=(
                        ObservedAction(
                            "agent", "", tool="spawnAgent", status="unavailable"
                        ),
                    )
                ),
            )
        action = run.frames[0].commands[0]
        self.assertEqual(action["assignment_visibility"], "unavailable")
        self.assertIsNone(action["status"])
        self.assertIsNone(action["assignment"])
