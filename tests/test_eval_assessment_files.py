from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import cast

from evals.assessment import assess, blind_packet
from evals.assessment_files import write_inputs
from evals.evidence import EvidenceFrame, EvidenceRun
from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, RubricCriterion
from evals.runner import CommandResult, Observation, ObservedAction
from tests.test_eval_runner import SOURCE, FakeDriver


class FileAssessmentTests(unittest.TestCase):
    def test_each_output_keeps_its_artifacts_under_its_own_label(self) -> None:
        runs = []
        for code in ("keeps old notes", "loses old notes"):
            run = EvidenceRun(
                "notes", "candidate", "condition", {"notes.py": "old notes"}
            )
            run.frames = [
                EvidenceFrame(
                    0, "main", "Finish.", "Done.", {"notes.py": code}, [], None, {}
                )
            ]
            runs.append(run)
        packet, labels = blind_packet(
            [RubricCriterion(id="retention", description="Keeps existing notes.")],
            runs,
        )
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = write_inputs(root, packet)
            for output in cast(list[dict[str, str]], manifest["outputs"]):
                index = json.loads((root / output["path"]).read_text())
                initial = index["initial_artifacts"]["notes.py"]
                final = index["frames"][0]["artifacts"]["notes.py"]
                for reference in (initial, final):
                    self.assertIn(Path(output["path"]).parent, Path(reference).parents)
                self.assertEqual((root / initial).read_text(), "old notes")
                self.assertEqual(
                    (root / final).read_text(),
                    labels[output["label"]].frames[0].files["notes.py"],
                )

    def test_native_edits_do_not_consume_command_results(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "native-edits",
                "tags": [],
                "files": {"plan.md": "open"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as workspace:
            changes = [
                {
                    "path": str(workspace.root / "plan.md"),
                    "kind": {"type": "update"},
                    "diff": "-open\n+settled\n",
                }
            ]
            run = EvidenceRun(case.id, "candidate", "condition")
            run.observe(
                workspace,
                0,
                "thread",
                "Continue.",
                Observation(
                    command_results=(
                        CommandResult("red", 1, "FAIL"),
                        CommandResult("green", 0, "PASS"),
                    ),
                    actions=(
                        ObservedAction("command", "red", exit_code=1),
                        ObservedAction("file", json.dumps(changes), status="completed"),
                        ObservedAction("command", "green", exit_code=0),
                    ),
                ),
            )
            observed = run.frames[0].commands
            self.assertEqual(observed[0]["output"], "FAIL")
            self.assertEqual(observed[2]["output"], "PASS")
            self.assertEqual(
                observed[1]["file_changes"],
                [{**changes[0], "path": "/project/plan.md"}],
            )
            self.assertEqual(observed[1]["status"], "completed")

    def test_agent_results_reach_judge_files_without_becoming_assignments(self) -> None:
        case = CaseSpec.model_validate(
            {
                "id": "agent-results",
                "tags": [],
                "files": {},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Fix the search finding.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as workspace:
            message = f"Reviewed {workspace.root}/src/app.py: no findings."
            run = EvidenceRun(case.id, "candidate", "condition")
            run.observe(
                workspace,
                0,
                "thread",
                "Fix the search finding.",
                Observation(
                    actions=(
                        ObservedAction(
                            "agent",
                            "",
                            tool="wait",
                            status="completed",
                            agent_results={
                                "reviewer": {"status": "completed", "message": message}
                            },
                        ),
                    )
                ),
            )
            rubric = [
                RubricCriterion(id="review", description="Reviews the correction.")
            ]
            packet, _ = blind_packet(rubric, [run])
            with tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                manifest = write_inputs(root, packet)
                output = cast(list[dict[str, str]], manifest["outputs"])[0]
                index = json.loads((root / output["path"]).read_text())
                action = json.loads(
                    (root / index["frames"][0]["actions"][0]).read_text()
                )
                self.assertIsNone(action["assignment"])
                self.assertEqual(action["assignment_visibility"], "not_supplied")
                self.assertEqual(
                    action["agent_results"],
                    {
                        "reviewer": {
                            "status": "completed",
                            "message": "Reviewed /project/src/app.py: no findings.",
                        }
                    },
                )

    def test_artifact_changes_distinguish_supplied_edits_from_candidate_turns(
        self,
    ) -> None:
        initial = {"plan.md": "open", "gone.md": "old", "keep.md": "unchanged"}
        supplied = {**initial, "plan.md": "supplied"}
        candidate = {
            "plan.md": "settled",
            "new.md": "created",
            "keep.md": "unchanged",
        }
        run = EvidenceRun("edits", "candidate", "condition", initial)
        run.frames = [
            EvidenceFrame(
                0, "main", "", "", supplied, [], None, {}, event="fixture_edit"
            ),
            EvidenceFrame(1, "main", "Continue.", "Done.", candidate, [], None, {}),
            EvidenceFrame(2, "main", "Recap.", "Done.", candidate, [], None, {}),
        ]
        rubric = [
            RubricCriterion(id="records", description="Keeps decisions in records.")
        ]
        packet, _ = blind_packet(rubric, [run])
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            manifest = write_inputs(root, packet)
            output = cast(list[dict[str, str]], manifest["outputs"])[0]
            index = json.loads((root / output["path"]).read_text())
            frames = index["frames"]
            self.assertEqual(frames[0]["event"], "fixture_edit")
            self.assertEqual(
                frames[0]["artifact_changes"],
                {"added": [], "modified": ["plan.md"], "removed": []},
            )
            self.assertEqual(frames[1]["event"], "message")
            self.assertEqual(
                frames[1]["artifact_changes"],
                {
                    "added": ["new.md"],
                    "modified": ["plan.md"],
                    "removed": ["gone.md"],
                },
            )
            self.assertEqual(
                frames[2]["artifact_changes"],
                {"added": [], "modified": [], "removed": []},
            )

    def test_judge_reads_complete_outputs_without_a_large_prompt(self) -> None:
        text = "Useful subject content.\n" * 30_000
        run = EvidenceRun("hidden-case", "hidden-model", "hidden-condition")
        run.frames = [
            EvidenceFrame(
                0,
                "main",
                "Write the guide.",
                "Done.",
                {"guide.md": text},
                [],
                None,
                {},
                commentary=["Checking the guide."],
            )
        ]
        seen: list[Path] = []

        class Judge(FakeDriver):
            def __init__(self, workspace: Workspace) -> None:
                super().__init__()
                self.workspace = workspace

            def message(self, thread: str, prompt: str) -> Observation:
                manifest = json.loads(prompt.split("\n\n", 1)[1])
                self_test.assertLess(len(prompt), 12_000)
                for secret in (run.case, run.model, run.condition):
                    self_test.assertNotIn(secret, prompt)
                output = manifest["outputs"][0]
                index = self.workspace.root / output["path"]
                seen.append(index)
                data = json.loads(index.read_text())
                comments = self.workspace.root / data["frames"][0]["commentary"]
                self_test.assertEqual(
                    json.loads(comments.read_text()), ["Checking the guide."]
                )
                artifact = (
                    self.workspace.root / data["frames"][0]["artifacts"]["guide.md"]
                )
                self_test.assertEqual(artifact.read_text(), text)
                return Observation(
                    json.dumps(
                        {
                            output["label"]: {
                                "content": {
                                    "verdict": "met",
                                    "evidence": [
                                        str(artifact.relative_to(self.workspace.root))
                                    ],
                                }
                            }
                        }
                    ),
                    10,
                    command_results=(CommandResult("cat guide.md", 0, text),),
                )

        self_test = self
        result = assess(
            [RubricCriterion(id="content", description="Useful guide.")],
            [run],
            "judge",
            driver_factory=lambda w, *_: Judge(w),
        )
        self.assertEqual(result[0].status, "pass", result[0].detail)
        self.assertFalse(any(p.exists() for p in seen))

    def test_evidence_mutation_invalidates_a_favorable_judgment(self) -> None:
        run = EvidenceRun("hidden", "candidate", "condition", {"source.md": "facts"})

        class Judge(FakeDriver):
            def __init__(self, workspace: Workspace) -> None:
                super().__init__()
                self.workspace = workspace

            def message(self, thread: str, prompt: str) -> Observation:
                (self.workspace.root / "extra.txt").write_text("changed")
                return Observation(
                    '{"A":{"content":{"verdict":"met","evidence":["source.md"]}}}',
                    10,
                )

        with tempfile.TemporaryDirectory() as raw:
            review = Path(raw) / "review"
            result = assess(
                [RubricCriterion(id="content", description="Read source.")],
                [run],
                "judge",
                driver_factory=lambda w, *_: Judge(w),
                review_dir=review,
            )
            self.assertEqual(result[0].status, "error")
            self.assertIn("changed", result[0].detail)
            self.assertFalse((review / "inputs/extra.txt").exists())

    def test_failed_judge_retains_evidence_and_usage_for_inspection(self) -> None:
        from evals.runner import LimitReached

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                raise LimitReached("Interrupted before verdict.", 123)

        with tempfile.TemporaryDirectory() as raw:
            review = Path(raw) / "review"
            result = assess(
                [RubricCriterion(id="content", description="Read source.")],
                [EvidenceRun("case", "model", "condition", {"source": "facts"})],
                "judge",
                driver_factory=lambda *_: Judge(),
                review_dir=review,
            )
            self.assertEqual(result[0].status, "limit")
            self.assertEqual(result[0].tokens, 123)
            self.assertTrue((review / "evidence.json").is_file())
            self.assertTrue((review / "judge-observation.json").is_file())
            self.assertTrue((review / "inputs/manifest.json").is_file())

    def test_startup_limit_retains_its_phase_measurements(self) -> None:
        from evals.runner import TimeLimitReached

        def factory(*args: object) -> FakeDriver:
            raise TimeLimitReached(
                "Startup timed out.", metrics={"startup_seconds": 3.0}
            )

        with tempfile.TemporaryDirectory() as raw:
            review = Path(raw) / "review"
            result = assess(
                [RubricCriterion(id="content", description="Read source.")],
                [EvidenceRun("case", "model", "condition")],
                "judge",
                driver_factory=factory,
                review_dir=review,
            )
            self.assertEqual(result[0].status, "limit")
            saved = json.loads((review / "judge-observation.json").read_text())
            self.assertEqual(saved["metrics"]["startup_seconds"], 3.0)


class BehaviorReportingTests(unittest.TestCase):
    def test_failed_checks_still_mean_incorrect_when_judge_times_out(self) -> None:
        from evals.assessment import apply_assessment
        from evals.assessment_models import AssessmentResult
        from evals.runner import CaseResult, CheckResult

        result = CaseResult(
            "case",
            "model",
            status="fail",
            mechanical_status="fail",
            checks=[
                CheckResult(0, "main", "completed", False, "Workflow left active.")
            ],
        )
        apply_assessment(result, AssessmentResult("limit", "judge"))
        self.assertEqual(result.behavior, "incorrect")
        self.assertEqual(result.assessment_execution, "failed")

    def test_missing_verdict_never_turns_passed_code_checks_into_correct_behavior(
        self,
    ) -> None:
        from evals.assessment import apply_assessment
        from evals.assessment_models import AssessmentResult
        from evals.runner import CaseResult

        result = CaseResult(
            "case", "model", status="inconclusive", mechanical_status="pass"
        )
        apply_assessment(result, AssessmentResult("limit", "judge"))
        self.assertEqual(result.behavior, "unknown")
        self.assertEqual(result.assessment_execution, "failed")


class EvidenceCaptureTests(unittest.TestCase):
    def test_long_artifact_remains_available_to_assessment(self) -> None:
        from evals.models import CaseSpec
        from evals.runner import run_case
        from tests.test_eval_runner import SOURCE

        text = "Document content.\n" * 50_000
        case = CaseSpec.model_validate(
            {
                "id": "long-artifact",
                "tags": [],
                "files": {"guide.md": text},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Read the guide.",
                        "checks": [{"kind": "unchanged", "paths": ["guide.md"]}],
                    }
                ],
            }
        )
        evidence = EvidenceRun(case.id, "candidate", "condition")
        result = run_case(
            case,
            SOURCE,
            "candidate",
            driver_factory=lambda *_: FakeDriver(),
            on_observation=evidence.observe,
        )
        self.assertEqual(result.status, "pass", result.detail)
        self.assertEqual(evidence.frames[0].files["guide.md"], text)


class PrivateCheckFailureTests(unittest.TestCase):
    def test_candidate_output_survives_a_private_browser_failure(self) -> None:
        from unittest.mock import patch

        from evals.models import load_cases
        from evals.runner import run_case
        from tests.test_eval_runner import SOURCE

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        evidence = EvidenceRun(case.id, "candidate", "condition")

        class CompletedDriver(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                return Observation(
                    "Review complete.",
                    10,
                    command_results=(
                        CommandResult("cat app/index.html", 0, "page content"),
                    ),
                    commentary=["Checking the layout."],
                )

        with patch(
            "evals.gui.collect_browser", side_effect=RuntimeError("Browser stopped.")
        ):
            result = run_case(
                case,
                SOURCE,
                "candidate",
                driver_factory=lambda *_: CompletedDriver(),
                on_observation=evidence.observe,
            )
        self.assertEqual(result.status, "error")
        self.assertIn("Browser stopped.", result.detail)
        self.assertEqual(result.tokens, 10)
        self.assertEqual(len(evidence.frames), 1)
        self.assertEqual(evidence.frames[0].reply, "Review complete.")
        self.assertEqual(evidence.frames[0].commentary, ["Checking the layout."])
        self.assertEqual(evidence.frames[0].commands[0]["output"], "page content")
        self.assertEqual(
            evidence.frames[0].files["app/index.html"], case.files["app/index.html"]
        )
