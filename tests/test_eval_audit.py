from __future__ import annotations

import unittest

from evals.audit import audit
from evals.models import CaseSpec


class CorpusAuditTests(unittest.TestCase):
    def test_median_includes_the_two_middle_values(self) -> None:
        cases = [
            CaseSpec.model_validate(
                {
                    "id": f"case-{size}",
                    "tags": [],
                    "files": {"context.md": "x" * size},
                    "steps": [
                        {
                            "kind": "message",
                            "prompt": "Continue.",
                            "checks": [{"kind": "no_publish"}],
                        }
                    ],
                }
            )
            for size in (1, 3, 7, 11)
        ]
        self.assertEqual(
            audit(cases)["fixture_characters"], {"min": 1, "median": 5, "max": 11}
        )

    def test_context_size_uses_the_files_the_candidate_starts_with(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "edited",
                "tags": [],
                "files": {"draft.md": "old"},
                "uncommitted_files": {"draft.md": "new text", "note.md": "note"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        self.assertEqual(
            audit([case])["fixture_characters"], {"min": 12, "median": 12, "max": 12}
        )

    def test_each_case_can_be_identified_and_inspected(self) -> None:
        cases = [
            CaseSpec.model_validate(
                {
                    "id": "short",
                    "tags": [],
                    "files": {"context.md": "abc"},
                    "steps": [
                        {
                            "kind": "message",
                            "prompt": "Continue.",
                            "checks": [{"kind": "no_publish"}],
                        }
                    ],
                }
            ),
            CaseSpec.model_validate(
                {
                    "id": "prepared",
                    "tags": [],
                    "purpose": "control",
                    "files": {"context.md": "abcdef", "checks/check.py": "pass"},
                    "steps": [
                        {"kind": "seed", "workflow": "novel-work", "state": "planning"},
                        {
                            "kind": "message",
                            "prompt": "Continue.",
                            "checks": [
                                {"kind": "python_check", "path": "checks/check.py"}
                            ],
                        },
                        {
                            "kind": "message",
                            "prompt": "Continue.",
                            "checks": [{"kind": "no_publish"}],
                        },
                    ],
                }
            ),
        ]
        result = audit(cases)
        self.assertEqual(
            result["case_details"],
            [
                {
                    "id": "short",
                    "purpose": "focused",
                    "message_count": 1,
                    "seed_steps": 0,
                    "fixture_characters": 3,
                    "visible_grading_scripts": [],
                    "process_cues": [],
                },
                {
                    "id": "prepared",
                    "purpose": "control",
                    "message_count": 2,
                    "seed_steps": 1,
                    "fixture_characters": 10,
                    "visible_grading_scripts": ["checks/check.py"],
                    "process_cues": [],
                },
            ],
        )
        self.assertEqual(result["public_python_graders"], 1)
