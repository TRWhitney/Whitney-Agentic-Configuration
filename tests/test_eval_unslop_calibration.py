from __future__ import annotations

import json
import unittest
from dataclasses import asdict
from pathlib import Path

from evals.calibration import Calibration, load_calibration

CALIBRATION_PATH = Path("evals/calibration/unslop-writing.json")


class UnslopCalibrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calibration = Calibration.model_validate_json(
            CALIBRATION_PATH.read_text(encoding="utf-8")
        )
        self.examples = {example.id: example for example in self.calibration.examples}
        self.rubric, self.runs, self.expected = load_calibration(CALIBRATION_PATH)

    def test_calibration_loads_twelve_complete_independent_examples(self) -> None:
        self.assertEqual(len(self.rubric), 1)
        self.assertEqual(len(self.examples), 12)
        self.assertEqual(len(self.runs), 12)
        self.assertEqual(set(self.examples), set(self.expected))
        sources = []
        for example in self.examples.values():
            with self.subTest(example=example.id):
                self.assertTrue(example.completed)
                self.assertTrue(example.request.strip())
                self.assertTrue(example.reply.strip())
                self.assertTrue(example.reason.strip())
                self.assertTrue(example.files["sources/context.md"].strip())
                self.assertIsNone(example.artifact)
                sources.append(example.files["sources/context.md"])
        self.assertEqual(len(sources), len(set(sources)))

    def test_private_labels_and_reasons_do_not_enter_evidence(self) -> None:
        for run in self.runs:
            with self.subTest(example=run.case):
                example = self.examples[run.case]
                self.assertEqual(run.initial_files, example.files)
                self.assertEqual(len(run.frames), 1)
                frame = run.frames[0]
                self.assertEqual(frame.prompt, example.request)
                self.assertEqual(frame.reply, example.reply)
                self.assertEqual(frame.files, example.files)
                visible = json.dumps(asdict(run))
                self.assertNotIn(example.reason, visible)
                self.assertNotIn('"expected":', visible)
                self.assertNotIn('"reason":', visible)

    def test_positive_controls_and_semantic_failures_have_distinct_labels(self) -> None:
        positives = {
            "reservation-fix-final-reply",
            "api-rate-limit-useful-terms",
            "cloakroom-clear-draft-unchanged",
            "market-revision-preserves-decisions",
            "community-event-recommendation-with-tradeoff",
        }
        negatives = {
            "parcel-update-familiar-labels",
            "membership-note-shortened-away-limit",
            "database-upgrade-disconnected-commands",
            "support-search-dense-correct-terms",
            "workshop-update-invented-support",
            "reading-room-uncertainty-promised-away",
            "rental-revision-loses-accepted-condition",
        }
        self.assertEqual(positives | negatives, set(self.examples))
        self.assertFalse(positives & negatives)
        for example_id in positives:
            with self.subTest(example=example_id):
                self.assertEqual(self.expected[example_id], "met")
        for example_id in negatives:
            with self.subTest(example=example_id):
                self.assertEqual(self.expected[example_id], "not_met")

    def test_clear_draft_control_preserves_the_entire_source_draft(self) -> None:
        example = self.examples["cloakroom-clear-draft-unchanged"]
        self.assertEqual(example.reply, example.files["draft.md"])
        self.assertEqual(example.expected, "met")

    def test_revision_examples_supply_ordered_prior_decisions_to_the_judge(
        self,
    ) -> None:
        for example_id in (
            "rental-revision-loses-accepted-condition",
            "market-revision-preserves-decisions",
        ):
            with self.subTest(example=example_id):
                example = self.examples[example_id]
                history = example.files["conversation.md"]
                roles = [line.split(":", 1)[0] for line in history.splitlines()]
                self.assertEqual(
                    roles, ["User", "Assistant", "User", "Assistant", "User"]
                )
                run = next(run for run in self.runs if run.case == example_id)
                self.assertEqual(run.frames[0].files["conversation.md"], history)
                self.assertNotEqual(example.reply, history.splitlines()[-2])

    def test_skill_read_is_observed_separately_from_quality(self) -> None:
        loaded_but_unclear = self.examples["parcel-update-familiar-labels"]
        clear_without_action_record = self.examples["reservation-fix-final-reply"]
        self.assertTrue(loaded_but_unclear.commands)
        self.assertEqual(loaded_but_unclear.expected, "not_met")
        self.assertEqual(clear_without_action_record.commands, [])
        self.assertEqual(clear_without_action_record.expected, "met")
        run = next(run for run in self.runs if run.case == loaded_but_unclear.id)
        self.assertEqual(run.frames[0].commands, loaded_but_unclear.commands)


if __name__ == "__main__":
    unittest.main()
