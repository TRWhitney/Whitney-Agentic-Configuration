from __future__ import annotations

import json
import unittest
from pathlib import Path

from evals.models import load_cases

ROOT = Path(__file__).resolve().parents[1]


class AcceptedFollowupTests(unittest.TestCase):
    def test_pending_conversations_and_supplied_input_have_distinct_cases(self) -> None:
        cases = {case.id: case for case in load_cases(ROOT / "evals/cases")}
        pending = cases["cleanup-keeps-other-conversation-evidence"]
        self.assertGreaterEqual(len({s.conversation for s in pending.steps}), 2)
        self.assertGreaterEqual(len(pending.temporary_files), 2)
        supplied = cases["cleanup-preserves-supplied-input"]
        self.assertGreaterEqual(len(supplied.temporary_files), 2)
        self.assertTrue(
            any(
                c.kind == "temporary_files" and c.state == "unchanged"
                for s in supplied.steps
                for c in s.checks
            )
        )

    def test_results_include_retry_and_unassessed_later_attempt(self) -> None:
        cases = {case.id: case for case in load_cases(ROOT / "evals/cases")}
        raw = json.loads(cases["results-survive-cleanup"].temporary_files["batch.json"])
        groups: dict[str, list[dict[str, object]]] = {}
        for result in raw["cases"]:
            groups.setdefault(result["id"], []).append(result)
        self.assertTrue(
            any(
                {r["outcome"] for r in rows} >= {"fail", "pass"}
                for rows in groups.values()
            )
        )
        self.assertTrue(
            any(
                len(rows) > 1 and rows[-1]["outcome"] == "limit"
                for rows in groups.values()
            )
        )

    def test_wording_question_follows_accepted_edits_without_a_write_contract(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(ROOT / "evals/cases")
            if c.id == "narrow-prose-correction"
        )
        questions = [s for s in case.steps if s.kind == "message" and "?" in s.prompt]
        self.assertTrue(questions)
        self.assertTrue(any(c.kind == "unchanged" for c in questions[-1].checks))
