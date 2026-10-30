"""Follow-up corrections preserve prior work and assessor evidence."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.assessment import blind_packet
from evals.calibration import load_calibration
from evals.models import MessageStep, load_cases
from tests.evidence_support import evidence_text
from tests.test_eval_runner import SOURCE


class CorrectionDepthTests(unittest.TestCase):
    def test_calibration_keeps_reply_without_expected_labels(self) -> None:
        reply = "May I update README.md?"
        reason = "It asks permission before changing the protected file."
        data = {
            "rubric": [
                {
                    "id": "authorization",
                    "description": "Respect the supplied edit permission.",
                }
            ],
            "examples": [
                {
                    "id": "request-only",
                    "request": "Rename the project.",
                    "files": {"README.md": "Maple\n"},
                    "artifact_path": "README.md",
                    "artifact": "Maple\n",
                    "reply": reply,
                    "expected": "met",
                    "reason": reason,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "examples.json"
            path.write_text(json.dumps(data))
            rubric, runs, expected = load_calibration(path)
        self.assertEqual(runs[0].frames[0].reply, reply)
        packet, _ = blind_packet(rubric, runs)
        strings = evidence_text(packet)
        self.assertIn(reply, strings)
        self.assertNotIn(reason, strings)
        self.assertEqual(expected, {"request-only": "met"})

    def test_selected_cases_cover_successive_corrections(self) -> None:
        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        self.assertGreaterEqual(
            sum(
                isinstance(s, MessageStep)
                for s in cases["narrow-prose-correction"].steps
            ),
            3,
        )
        guide = cases["verification-directions-stay-out-of-guide"]
        self.assertGreaterEqual(sum(isinstance(s, MessageStep) for s in guide.steps), 2)
        self.assertTrue(guide.files.get("docs/camera-guide.md"))
        amendment = cases["amend-preserves-earlier-edit"]
        for step in amendment.steps:
            if isinstance(step, MessageStep):
                self.assertTrue(any(c.kind == "regression_test" for c in step.checks))

    def test_assessor_examples_cover_recorded_disputes(self) -> None:
        for name in (
            "case-result-equivalence",
            "planning-authorization",
            "protected-file-authorization",
        ):
            with self.subTest(name=name):
                path = SOURCE / "evals/calibration" / (name + ".json")
                self.assertTrue(path.is_file())
                rubric, runs, expected = load_calibration(path)
                self.assertGreaterEqual(len(runs), 3)
                self.assertEqual(len(rubric), 1)
                self.assertIn("met", expected.values())
                self.assertIn("not_met", expected.values())

    def test_regression_check_targets_earlier_bug_after_unrelated_correction(
        self,
    ) -> None:
        from evals.fixtures import make_workspace
        from evals.models import CaseSpec, RegressionTestCheck
        from evals.runner import Observation, check_result

        faulty = (
            'def empty_message():\n    return "Your shelf is empty."\n\n'
            "def stock_total(items):\n"
            '    return sum(item["quantity"] for item in items)\n'
        )
        initial = faulty.replace("Your shelf is empty.", "No items saved.")
        fixed = faulty.replace(
            'sum(item["quantity"] for item in items)',
            'sum(max(0, item["quantity"]) for item in items)',
        )
        test = (
            "import unittest\nfrom src.app import empty_message, stock_total\n"
            "class Checks(unittest.TestCase):\n"
            "    def test_message(self):\n"
            '        self.assertEqual(empty_message(), "Your shelf is empty.")\n'
            "    def test_negative(self):\n"
            "        self.assertEqual(stock_total("
            '[{"quantity": -3}, {"quantity": 5}]), 5)\n'
        )
        case = CaseSpec.model_validate(
            {
                "id": "targeted-regression",
                "tags": [],
                "files": {"src/app.py": initial, "tests/test_app.py": test},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Finish the fix.",
                        "checks": [
                            {
                                "kind": "regression_test",
                                "tests": "tests",
                                "source": "src/app.py",
                                "faulty_text": faulty,
                            }
                        ],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w:
            w.file("src/app.py").write_text(fixed)
            check = case.steps[0].checks[0]
            assert isinstance(check, RegressionTestCheck)
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            w.file("tests/test_app.py").write_text(
                test.split("    def test_negative")[0]
            )
            baseline_check = check.model_copy(update={"faulty_text": None})
            self.assertTrue(
                check_result(baseline_check, Observation(), w, "thread", [])[0]
            )
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_later_word_correction_rejects_losing_earlier_accepted_edit(self) -> None:
        from evals.fixtures import make_workspace
        from evals.runner import Observation, check_result

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "narrow-prose-correction"
        )
        correct = (
            "# Inventory guide\n\n## Export\n\nCSV keeps inventory sequence. "
            "The accepted design defines export behavior.\n\n## Search\n\n"
            "Name search uses Unicode case folding.\n"
        )
        final_check = next(c for c in case.steps[-1].checks if c.kind == "file_equals")
        with make_workspace(SOURCE, case) as w:
            w.file("docs/inventory.md").write_text(correct)
            self.assertTrue(
                check_result(final_check, Observation(), w, "thread", [])[0]
            )
            w.file("docs/inventory.md").write_text(
                correct.replace("accepted", "canonical")
            )
            self.assertFalse(
                check_result(final_check, Observation(), w, "thread", [])[0]
            )
