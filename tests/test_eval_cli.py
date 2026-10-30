from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from evals.__main__ import main
from evals.fixtures import Workspace
from tests.test_eval_runner import FakeDriver

SOURCE = Path(__file__).resolve().parents[1]


class EvaluationCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cases = self.root / "cases"
        self.cases.mkdir()
        (self.cases / "one.json").write_text(
            json.dumps(
                {
                    "id": "one",
                    "tags": ["example"],
                    "files": {"src/app.py": "value = 1\n"},
                    "steps": [
                        {
                            "kind": "message",
                            "prompt": "Ready?",
                            "checks": [{"kind": "reply_regex", "pattern": "Ready"}],
                        }
                    ],
                }
            )
        )
        self.workspaces: list[Path] = []

    def factory(
        self, workspace: Workspace, model: str, timeout: float, max_tokens: int
    ) -> FakeDriver:
        self.workspaces.append(workspace.root)
        return FakeDriver()

    def invoke(self, *arguments: str) -> tuple[int, str]:
        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            result = main(list(arguments), driver_factory=self.factory)
        return result, output.getvalue()

    def test_validation_and_listing_make_no_model_calls(self) -> None:
        for operation in ("validate", "list"):
            result, output = self.invoke(operation, "--cases", str(self.cases))
            self.assertEqual(result, 0)
            self.assertTrue(output.strip())
        self.assertEqual(self.workspaces, [])

    def test_variants_and_repeats_use_independent_environments(self) -> None:
        result, output = self.invoke(
            "run",
            "--cases",
            str(self.cases),
            "--model",
            "example-model",
            "--repeat",
            "2",
            "--variant",
            f"before={SOURCE}",
            "--variant",
            f"after={SOURCE}",
        )
        self.assertEqual(result, 0)
        summary = json.loads(output)
        self.assertEqual(summary["counts"]["pass"], 4)
        self.assertEqual(
            {item["variant"] for item in summary["results"]}, {"before", "after"}
        )
        self.assertEqual({item["attempt"] for item in summary["results"]}, {1, 2})
        self.assertEqual(len(set(self.workspaces)), 4)
        self.assertFalse(any(path.exists() for path in self.workspaces))

    def test_reports_remain_outside_checkout_and_existing_files_are_preserved(
        self,
    ) -> None:
        report = self.root / "summary.json"
        arguments = (
            "run",
            "--cases",
            str(self.cases),
            "--model",
            "example-model",
            "--report",
        )
        result, _ = self.invoke(*arguments, str(SOURCE / "summary.json"))
        self.assertEqual(result, 2)
        self.assertEqual(self.workspaces, [])
        result, _ = self.invoke(*arguments, str(report))
        self.assertEqual(result, 0)
        before = report.read_bytes()
        result, _ = self.invoke(*arguments, str(report))
        self.assertEqual(result, 2)
        self.assertEqual(report.read_bytes(), before)
        self.assertEqual(len(self.workspaces), 1)

    def test_unknown_case_fails_before_execution(self) -> None:
        result, _ = self.invoke(
            "run",
            "--cases",
            str(self.cases),
            "--model",
            "example-model",
            "--case",
            "missing",
        )
        self.assertEqual(result, 2)
        self.assertEqual(self.workspaces, [])

    def test_unassessed_task_is_inconclusive(self) -> None:
        definition = json.loads((self.cases / "one.json").read_text())
        definition["purpose"] = "task"
        definition["rubric"] = [
            {"id": f"criterion-{i}", "description": f"Required outcome {i}."}
            for i in range(3)
        ]
        (self.cases / "one.json").write_text(json.dumps(definition))
        code, output = self.invoke("run", "--cases", str(self.cases), "--model", "fake")
        summary = json.loads(output)
        self.assertEqual(code, 4)
        self.assertEqual(summary["results"][0]["mechanical_status"], "pass")
        self.assertEqual(summary["results"][0]["status"], "inconclusive")

    def test_one_blind_judge_receives_both_instruction_variants(self) -> None:
        from evals.runner import Observation

        definition = json.loads((self.cases / "one.json").read_text())
        definition["rubric"] = [{"id": "useful", "description": "Useful answer."}]
        (self.cases / "one.json").write_text(json.dumps(definition))
        packets = []

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                packet = json.loads(prompt.split("\n\n", 1)[1])
                packets.append(packet)
                return Observation(
                    json.dumps(
                        {
                            item["label"]: {
                                "useful": {
                                    "verdict": "uncertain",
                                    "evidence": [
                                        "The answer lacks sufficient evidence."
                                    ],
                                }
                            }
                            for item in packet["outputs"]
                        }
                    ),
                    10,
                )

        output = io.StringIO()
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            code = main(
                [
                    "run",
                    "--cases",
                    str(self.cases),
                    "--model",
                    "candidate",
                    "--variant",
                    f"before={SOURCE}",
                    "--variant",
                    f"after={SOURCE}",
                    "--judge-model",
                    "judge",
                ],
                driver_factory=self.factory,
                judge_factory=lambda *args: Judge(),
            )
        self.assertEqual(code, 4)
        self.assertEqual(len(packets), 1)
        self.assertEqual(len(packets[0]["outputs"]), 2)
        summary = json.loads(output.getvalue())
        self.assertEqual(summary["counts"]["inconclusive"], 2)
        self.assertEqual(summary["assessment_counts"], {"inconclusive": 2})
        self.assertTrue(
            all(r["mechanical_status"] == "pass" for r in summary["results"])
        )

    def test_audit_needs_no_model(self) -> None:
        result, output = self.invoke("audit", "--cases", str(self.cases))
        self.assertEqual(result, 0)
        self.assertEqual(json.loads(output)["purposes"], {"focused": 1})
        self.assertEqual(self.workspaces, [])


if __name__ == "__main__":
    unittest.main()
