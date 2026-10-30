from __future__ import annotations

import unittest

from evals.assessment import blind_packet
from evals.models import CaseSpec, EditStep, MessageStep, SeedStep, load_cases
from tests.evidence_support import evidence_text
from tests.test_eval_prose import record_case
from tests.test_eval_runner import SOURCE


class ProseRealWorkTests(unittest.TestCase):
    def cases(self) -> dict[str, CaseSpec]:
        return {case.id: case for case in load_cases(SOURCE / "evals/cases")}

    def test_known_compliance_report_cannot_pass_reader_content_checks(self) -> None:
        case = self.cases()["verification-directions-stay-out-of-guide"]
        body = (
            "# Camera controls\n\n"
            "Aperture is the lens opening. A wider opening admits more light.\n"
            "Shutter speed is exposure duration; a shorter exposure reduces motion "
            "blur in the toy train.\nISO affects brightness and noise.\n"
        )
        claim = "All three source cards were checked for this guide."
        for report in (
            claim,
            "## " + claim,
            "| Preparation | " + claim + " |",
            "<!-- " + claim + " -->",
        ):
            with self.subTest(report=report):
                result, run = record_case(
                    case, {"docs/camera-guide.md": body + "\n" + report}
                )
                self.assertEqual(result.mechanical_status, "fail", result.detail)
                self.assertIn(report, run.frames[0].files["docs/camera-guide.md"])

    def test_unknown_paraphrase_still_reaches_complete_semantic_assessment(
        self,
    ) -> None:
        case = self.cases()["verification-directions-stay-out-of-guide"]
        guide = (
            "# Camera controls\n\n"
            "Aperture is the lens opening; widening it admits more light in the "
            "window portrait. Shutter speed is exposure duration; shortening it "
            "makes the toy-train wheels clearer but admits less light. ISO changes "
            "recorded brightness through camera response; the evening-room image "
            "gets brighter but its dark areas have more visible noise.\n\n"
            "<!-- The handout has been reconciled with its lesson references. -->\n"
        )
        result, run = record_case(case, {"docs/camera-guide.md": guide})
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertIsNone(result.assessment)
        packet, _ = blind_packet(case.rubric, [run])
        self.assertIn(guide, evidence_text(packet))
        self.assertEqual(len(run.frames), len(case.steps))
        self.assertEqual(
            [f.files["docs/camera-guide.md"] for f in run.frames],
            [guide] * len(case.steps),
        )
        self.assertIn("cyclist", run.initial_files["sources/cards/shutter.md"])
        self.assertIn("toy train", run.frames[-1].files["sources/cards/shutter.md"])

    def test_real_work_starts_from_existing_documents_and_requires_followups(
        self,
    ) -> None:
        cases = self.cases()
        paths = {
            "verification-directions-stay-out-of-guide": "docs/camera-guide.md",
            "writing-preferences-stay-out-of-prose": "docs/assistant-guide.md",
            "followup-keeps-process-out-of-prose": "docs/transfer-guide.md",
            "fresh-handoff-separates-directions-from-content": "docs/plant-guide.md",
        }
        for name, path in paths.items():
            with self.subTest(case=name):
                case = cases[name]
                draft = case.files[path]
                self.assertTrue(draft.strip())
                self.assertGreaterEqual(
                    sum(isinstance(step, MessageStep) for step in case.steps), 2
                )
                self.assertEqual(case.artifacts, [path])
                self.assertGreaterEqual(len(case.rubric), 3)
                self.assertLessEqual(len(case.rubric), 6)
        camera = cases["verification-directions-stay-out-of-guide"]
        first_step = camera.steps[0]
        assert isinstance(first_step, MessageStep)
        handoff = cases["fresh-handoff-separates-directions-from-content"]
        self.assertIsInstance(handoff.steps[0], SeedStep)
        self.assertIn(".work/plant/status.md", handoff.files)
        transfer = cases["followup-keeps-process-out-of-prose"]
        self.assertNotIn("platform 4", transfer.files["sources/transfer.md"])
        self.assertTrue(
            any(
                "platform 4" in step.files.get("sources/transfer.md", "")
                for step in transfer.steps
                if isinstance(step, EditStep)
            )
        )

    def test_workflow_documentation_and_author_directions_share_vocabulary(
        self,
    ) -> None:
        case = self.cases()["writing-preferences-stay-out-of-prose"]
        source = case.files["sources/shelf-assistant.md"]
        self.assertIn("pending proposal", source)
        self.assertIn("Resuming a session does not accept or save", source)
        self.assertNotIn("familiar words", source)
        self.assertNotIn("short explanations", source)
        path = "docs/assistant-guide.md"
        first = (
            "Review the proposal before accepting it. Accept saves name and quantity "
            "together; Cancel leaves inventory unchanged. The assistant asks for a "
            "missing quantity. Zero is valid. Deletion requires acceptance too. "
            "Resuming shows a pending proposal and waits for your decision. A failed "
            "save leaves the inventory unchanged and the proposal pending. "
            "For Blue mug, accept a proposal setting its quantity to zero; it remains "
            "in the inventory."
        )
        second = first + (
            " For a new Red bowl, omit the quantity, then give zero when asked. "
            "Cancel the proposal; Red bowl is not saved."
        )
        final = (
            "# How do I save a change?\n\n"
            + second
            + ("\n<!-- The prose now observes your preferred direct wording. -->")
        )
        result, run = record_case(case, ({path: first}, {path: second}, {path: final}))
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertIsNone(result.assessment)
        packet, _ = blind_packet(case.rubric, [run])
        for text, frame in zip((first, second, final), run.frames, strict=True):
            self.assertEqual(frame.files[path], text)
            self.assertIn(text, evidence_text(packet))
        self.assertEqual(run.initial_files[path], case.files[path])
        self.assertEqual(run.frames[-1].files["sources/shelf-assistant.md"], source)
