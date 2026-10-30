from __future__ import annotations

import unittest
from pathlib import Path


class CalibrationTests(unittest.TestCase):
    def test_expected_labels_do_not_enter_assessment_evidence(self) -> None:
        from evals.calibration import load_calibration

        rubric, runs, expected = load_calibration(
            Path("evals/calibration/prose-boundaries.json")
        )
        self.assertEqual(len(runs), 8)
        self.assertEqual(len(rubric), 1)
        self.assertEqual(sorted(expected.values()).count("met"), 4)
        for run in runs:
            self.assertNotIn("expected", run.initial_files)
            self.assertNotIn("reason", run.initial_files)
