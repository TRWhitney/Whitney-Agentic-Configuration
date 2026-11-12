from __future__ import annotations

import unittest
from pathlib import Path

from evals.fixtures import make_workspace
from evals.models import CaseSpec, ProgressCheck, PythonCheck, load_cases
from evals.runner import Observation, check_result

SOURCE = Path(__file__).resolve().parents[1]


class CompactionAssessmentTests(unittest.TestCase):
    def test_decision_map_check_accepts_other_names_and_rejects_empty_maps(
        self,
    ) -> None:
        original = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "agent-created-state-compaction"
        )
        case = CaseSpec.model_validate(
            {
                "id": "map-name",
                "tags": [],
                "files": {
                    ".work/export/status.md": (
                        "[Decision map](../../docs/planning/export/decision-map.md)\n"
                        "[Feature planning](decisions/export.md)\n"
                    ),
                    "docs/planning/export/decision-map.md": (
                        "# Export choices\n\nCSV accepted. "
                        "Existing destination is open.\n"
                    ),
                    ".work/export/decisions/export.md": (
                        "# Export requirements\n\n"
                        "Name and quantity columns are accepted.\n"
                    ),
                },
                "grader_files": original.grader_files,
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        check = PythonCheck(path="checks/check_wayfinding_map.py")
        with make_workspace(SOURCE, case) as workspace:
            self.assertTrue(check_result(check, Observation(), workspace, "one", [])[0])
            workspace.file("docs/planning/export/decision-map.md").write_text("")
            self.assertFalse(
                check_result(check, Observation(), workspace, "one", [])[0]
            )

    def test_record_check_rejects_missing_and_wrong_links(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "record-link",
                "tags": [],
                "files": {"status.md": "Pending choice."},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        check = ProgressCheck(
            workflow="novel-work", state="planning", record="status.md"
        )
        with make_workspace(SOURCE, case) as workspace:
            workspace.navigate("one", ["start", "novel-work"])
            self.assertFalse(
                check_result(check, Observation(), workspace, "one", [])[0]
            )
            workspace.navigate(
                "one",
                ["start", "novel-work", "--record", str(workspace.root / "other.md")],
            )
            self.assertFalse(
                check_result(check, Observation(), workspace, "one", [])[0]
            )
            workspace.navigate(
                "one",
                ["start", "novel-work", "--record", str(workspace.root / "status.md")],
            )
            self.assertTrue(check_result(check, Observation(), workspace, "one", [])[0])


if __name__ == "__main__":
    unittest.main()
