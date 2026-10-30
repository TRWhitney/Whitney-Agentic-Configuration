from __future__ import annotations

import unittest

from pydantic import TypeAdapter

from evals.audit import CaseAudit, audit
from evals.models import CaseSpec


class InstructionAuditTests(unittest.TestCase):
    def test_reports_process_requests_in_prompts_and_later_context(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "coached",
                "tags": [],
                "files": {
                    ".work/search/spec.md": (
                        "Run python3 checks/search.py before delivery.\n"
                    )
                },
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Audit the implementation and amend the commit.",
                        "checks": [{"kind": "no_publish"}],
                    },
                    {
                        "kind": "edit",
                        "files": {
                            ".work/search/status.md": (
                                "Delegate the repair to a worker.\n"
                            )
                        },
                    },
                ],
            }
        )
        data = TypeAdapter(list[CaseAudit]).validate_python(
            audit([case])["case_details"]
        )[0]
        cues = data.process_cues
        self.assertTrue(any(cue["cue"].lower() == "amend" for cue in cues))
        self.assertEqual(
            {cue["source"] for cue in cues},
            {
                "message:0",
                "file:.work/search/spec.md",
                "edit:1:.work/search/status.md",
            },
        )

    def test_does_not_treat_product_requirements_as_process_requests(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "ordinary",
                "tags": [],
                "files": {
                    ".work/search/spec.md": (
                        "An empty query returns all items.\n"
                        "Project checks: checks/search.py.\n"
                    )
                },
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Finish the accepted search change.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        self.assertEqual(
            TypeAdapter(list[CaseAudit])
            .validate_python(audit([case])["case_details"])[0]
            .process_cues,
            [],
        )
