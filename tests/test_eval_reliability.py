from __future__ import annotations

import contextlib
import io
import json
import unittest

from evals.assessment_models import AssessmentResult


class CalibrationEnforcementTests(unittest.TestCase):
    def test_disagreement_fails_calibration_command(self) -> None:
        from evals.calibrate import main
        from evals.fixtures import Workspace
        from evals.runner import Observation
        from tests.test_eval_runner import FakeDriver

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                packet = json.loads(prompt.split("\n\n", 1)[1])
                criterion = packet["criteria"][0]["id"]
                return Observation(
                    json.dumps(
                        {
                            output["label"]: {
                                criterion: {
                                    "verdict": "met",
                                    "reason": "observed",
                                    "channel": "artifacts",
                                    "evidence": [
                                        "The guide contains the required content."
                                    ],
                                }
                            }
                            for output in packet["outputs"]
                        }
                    ),
                    10,
                )

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> Judge:
            return Judge()

        with contextlib.redirect_stdout(io.StringIO()):
            code = main(
                [
                    "--model",
                    "fake",
                    "--examples",
                    "evals/calibration/prose-boundaries.json",
                ],
                driver_factory=factory,
            )
        self.assertEqual(code, 1)

        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as raw:
            example = Path(raw) / "clear.json"
            example.write_text(
                json.dumps(
                    {
                        "rubric": [
                            {
                                "id": "content",
                                "description": "The guide contains the content.",
                            }
                        ],
                        "examples": [
                            {
                                "id": "clear",
                                "request": "Write the guide.",
                                "files": {"guide.md": "Guide."},
                                "reply": "Done.",
                                "recording": {
                                    "actions": "complete",
                                    "problems": ["A capture is unavailable."],
                                },
                                "expected": "met",
                                "reason": "The content is supplied.",
                            }
                        ],
                    }
                )
            )
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(
                    ["--model", "fake", "--examples", str(example)],
                    driver_factory=factory,
                )
            self.assertEqual(code, 1)

        from evals.__main__ import main as run

        candidates = []

        def candidate(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            candidates.append(workspace.root)
            return FakeDriver()

        with tempfile.TemporaryDirectory() as raw:
            report = Path(raw) / "report.json"
            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                code = run(
                    [
                        "run",
                        "--case",
                        "interactive-prototype-comparison",
                        "--model",
                        "fake",
                        "--judge-model",
                        "fake",
                        "--calibration",
                        "evals/calibration/prose-boundaries.json",
                        "--report",
                        str(report),
                    ],
                    driver_factory=candidate,
                    judge_factory=factory,
                )
            self.assertEqual(code, 1)
            self.assertEqual(candidates, [])
            self.assertEqual(json.loads(report.read_text())["results"], [])


class ReliabilityRoutingTests(unittest.TestCase):
    def result(
        self, *, complete: bool, reason: str, verdict: str, required: bool = True
    ) -> AssessmentResult:
        from evals.assessment import assess
        from evals.evidence import EvidenceFrame, EvidenceRun
        from evals.fixtures import Workspace
        from evals.models import RubricCriterion
        from evals.recording import Recording
        from evals.runner import Observation
        from tests.test_eval_runner import FakeDriver

        run = EvidenceRun("case", "fake", "source")
        run.frames = [
            EvidenceFrame(
                0,
                "main",
                "Repair the dialog.",
                "Done.",
                {},
                [],
                None,
                {},
                recording=Recording(actions="complete" if complete else "unknown"),
            )
        ]

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                packet = json.loads(prompt.split("\n\n", 1)[1])
                return Observation(
                    json.dumps(
                        {
                            output["label"]: {
                                "operation": {
                                    "verdict": verdict,
                                    "reason": reason,
                                    "channel": "actions",
                                    "evidence": ["Only open and cancel are recorded."],
                                }
                            }
                            for output in packet["outputs"]
                        }
                    ),
                    10,
                )

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> Judge:
            return Judge()

        return assess(
            [
                RubricCriterion(
                    id="operation",
                    description="Operate the required dialog flows.",
                    required=required,
                )
            ],
            [run],
            "fake",
            driver_factory=factory,
        )[0]

    def test_absent_operation_fails_only_with_complete_recording(self) -> None:
        observed = self.result(
            complete=True, reason="omitted_action", verdict="not_met"
        )
        unavailable = self.result(
            complete=False, reason="omitted_action", verdict="not_met"
        )
        self.assertEqual(observed.status, "fail")
        self.assertEqual(unavailable.status, "inconclusive")
        self.assertEqual(unavailable.criteria[0]["verdict"], "uncertain")
        self.assertEqual(unavailable.issues[0].kind, "capture")

    def test_ambiguity_needs_criterion_review(self) -> None:
        result = self.result(
            complete=True, reason="ambiguous_requirement", verdict="uncertain"
        )
        self.assertEqual(result.issues[0].kind, "criterion")
        self.assertEqual(result.status, "inconclusive")

    def test_optional_uncertainty_does_not_change_behavior_verdict(self) -> None:
        result = self.result(
            complete=True,
            reason="ambiguous_requirement",
            verdict="uncertain",
            required=False,
        )
        self.assertEqual(result.status, "pass")
        self.assertTrue(result.issues)

    def test_positive_failure_is_not_erased_by_missing_observations(self) -> None:
        result = self.result(complete=False, reason="observed", verdict="not_met")
        self.assertEqual(result.status, "fail")


class RecordingIntegrityTests(unittest.TestCase):
    def test_bad_browser_line_preserves_valid_operations_and_reports_problem(
        self,
    ) -> None:
        from evals.evidence import EvidenceRun
        from evals.fixtures import make_workspace
        from evals.models import CaseSpec
        from evals.recording import Recording
        from evals.runner import Observation
        from tests.test_eval_runner import SOURCE

        case = CaseSpec.model_validate(
            {
                "id": "recording",
                "tags": [],
                "files": {},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        run = EvidenceRun("recording", "fake", "source")
        with make_workspace(SOURCE, case) as workspace:
            (workspace.home / "work-system/browser-journal.jsonl").write_text(
                json.dumps(
                    {
                        "steps": [{"action": "click", "selector": "#save"}],
                        "status": "completed",
                    }
                )
                + "\n{broken\n"
                + json.dumps({"request_id": []})
                + "\n"
                + json.dumps({"images": [{"data_url": "bad"}]})
                + "\n"
            )
            run.observe(
                workspace,
                0,
                "thread",
                "Continue.",
                Observation("Done.", 10, recording=Recording(actions="complete")),
            )
        self.assertEqual(
            run.frames[0].browser[0]["steps"],
            [{"action": "click", "selector": "#save"}],
        )
        self.assertEqual(run.frames[0].recording.channels["browser"], "partial")
        self.assertTrue(run.frames[0].recording.problems)
        self.assertEqual(run.frames[0].reply, "Done.")

    def test_browser_request_without_receipt_is_not_complete(self) -> None:
        from evals.fixtures import make_workspace
        from evals.gui import candidate_browser
        from evals.models import CaseSpec
        from tests.test_eval_runner import SOURCE

        case = CaseSpec.model_validate(
            {
                "id": "recording",
                "tags": [],
                "files": {},
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
            queue = workspace.home / "work-system/browser-queue"
            queue.mkdir(exist_ok=True)
            (queue / "request.response.json").write_text('{"returncode":1}')
            problems: list[str] = []
            self.assertEqual(candidate_browser(workspace, problems), [])
            self.assertTrue(problems)


class RepairCommandTests(unittest.TestCase):
    def test_reassessment_preserves_original_and_rejects_changed_task(self) -> None:
        import tempfile
        from pathlib import Path

        from evals.assessment import assess
        from evals.evidence import EvidenceFrame, EvidenceRun
        from evals.fixtures import Workspace
        from evals.models import CaseSpec
        from evals.recording import Recording
        from evals.repair import main
        from evals.runner import Observation
        from tests.test_eval_runner import FakeDriver

        insufficient_recording = False
        bad_expectations = False
        diagnosis_calls = 0

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                nonlocal diagnosis_calls
                packet = json.loads(prompt.split("\n\n", 1)[1])
                if any(c["id"] == "recording" for c in packet["criteria"]):
                    diagnosis_calls += 1
                return Observation(
                    json.dumps(
                        {
                            out["label"]: {
                                criterion["id"]: {
                                    "verdict": "not_met"
                                    if (
                                        insufficient_recording
                                        and criterion["id"] == "recording"
                                    )
                                    or (
                                        bad_expectations
                                        and criterion["id"] == "expectations"
                                    )
                                    else "met",
                                    "reason": "observed",
                                    "channel": "artifacts",
                                    "evidence": [
                                        "guide.md contains the requested guide."
                                    ],
                                }
                                for criterion in packet["criteria"]
                            }
                            for out in packet["outputs"]
                        }
                    ),
                    10,
                )

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> Judge:
            return Judge()

        case = CaseSpec.model_validate(
            {
                "id": "sample",
                "tags": [],
                "files": {"guide.md": "Guide."},
                "rubric": [
                    {"id": "guide", "description": "Deliver the requested guide."}
                ],
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Write the guide.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        run = EvidenceRun(
            "sample", "fake", "source", definition=case.model_dump(mode="json")
        )
        run.frames = [
            EvidenceFrame(
                0,
                "main",
                "Write the guide.",
                "Done.",
                {"guide.md": "Guide."},
                [],
                None,
                {},
                recording=Recording(actions="complete"),
            )
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "original"
            assess(
                case.rubric, [run], "fake", driver_factory=factory, review_dir=archive
            )
            self.assertTrue((archive / "assessment-results.json").is_file())
            before = {
                p.relative_to(archive): p.read_bytes()
                for p in archive.rglob("*")
                if p.is_file()
            }
            cases = root / "cases"
            cases.mkdir()
            definition = cases / "sample.json"
            definition.write_text(case.model_dump_json())

            def invoke(operation: str, name: str) -> int:
                with (
                    contextlib.redirect_stdout(io.StringIO()),
                    contextlib.redirect_stderr(io.StringIO()),
                ):
                    return main(
                        [
                            operation,
                            "--evidence",
                            str(archive),
                            "--model",
                            "fake",
                            "--cases",
                            str(cases),
                            "--report",
                            str(root / (name + ".json")),
                            "--review-dir",
                            str(root / name),
                        ],
                        driver_factory=factory,
                    )

            self.assertEqual(invoke("reassess", "revised"), 0)
            revised = json.loads((root / "revised.json").read_text())
            self.assertTrue(revised["results"][0]["original_criteria"])
            self.assertEqual(
                before,
                {
                    p.relative_to(archive): p.read_bytes()
                    for p in archive.rglob("*")
                    if p.is_file()
                },
            )
            self.assertEqual(invoke("reassess", "revised"), 2)
            original_archive = archive
            run.execution = {
                "status": "error",
                "detail": "Runtime failed after the last observation.",
            }
            archive = root / "execution-error"
            assess(
                case.rubric, [run], "fake", driver_factory=factory, review_dir=archive
            )
            self.assertNotEqual(invoke("reassess", "execution-error-reassessment"), 0)
            archive = original_archive
            run.execution = {}

            changed = case.model_dump(mode="json")
            changed["steps"][0]["prompt"] = "Write a different guide."
            definition.write_text(json.dumps(changed))
            self.assertEqual(invoke("reassess", "changed"), 2)
            self.assertEqual(invoke("diagnose", "diagnosis"), 0)
            # A diagnosis evaluates the warning rather than inheriting it.
            run.frames[0].recording.problems = [
                "A quiet command was reported as missing output."
            ]
            archive = root / "warning-original"
            assess(
                case.rubric, [run], "fake", driver_factory=factory, review_dir=archive
            )
            self.assertEqual(invoke("diagnose", "warning-diagnosis"), 0)
            definition.write_text(case.model_dump_json())
            self.assertEqual(invoke("reassess", "warning-reassessment"), 0)
            bad_expectations = True
            self.assertEqual(invoke("reassess", "invalid-expectation"), 1)
            self.assertEqual(
                json.loads((root / "invalid-expectation.json").read_text())["results"],
                [],
            )
            bad_expectations = False

            insufficient_recording = True
            self.assertEqual(invoke("reassess", "needs-fresh-capture"), 1)
            self.assertEqual(
                json.loads((root / "needs-fresh-capture.json").read_text())["results"],
                [],
            )
            insufficient_recording = False
            run.frames[0].recording.problems = []
            archive = root / "failed-judge"

            class BrokenJudge(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    return Observation("{", 10)

            assess(
                case.rubric,
                [run],
                "fake",
                driver_factory=lambda *args: BrokenJudge(),
                review_dir=archive,
            )
            self.assertEqual(invoke("reassess", "recovered-judge"), 0)
            recovered = json.loads((root / "recovered-judge.json").read_text())
            self.assertTrue(recovered["results"][0]["original_assessment_error"])
            self.assertEqual(recovered["results"][0]["behavior"], "correct")

            class InterruptedJudge(Judge):
                def message(self, thread: str, prompt: str) -> Observation:
                    observed = super().message(thread, prompt)
                    observed.completed = False
                    return observed

            archive = root / "valid-json-invalid-assessment"
            assess(
                case.rubric,
                [run],
                "fake",
                driver_factory=lambda *args: InterruptedJudge(),
                review_dir=archive,
            )
            before_audits = diagnosis_calls
            self.assertEqual(invoke("reassess", "review-interrupted-judge"), 0)
            self.assertEqual(diagnosis_calls, before_audits + 1)

            class UncertainJudge(FakeDriver):
                def message(self, thread: str, prompt: str) -> Observation:
                    packet = json.loads(prompt.split("\n\n", 1)[1])
                    return Observation(
                        json.dumps(
                            {
                                out["label"]: {
                                    "guide": {
                                        "verdict": "uncertain",
                                        "reason": "ambiguous_requirement",
                                        "channel": "artifacts",
                                        "evidence": [
                                            "The requested detail is unclear."
                                        ],
                                    }
                                }
                                for out in packet["outputs"]
                            }
                        ),
                        10,
                    )

            archive = root / "uncertain-assessment"
            assess(
                case.rubric,
                [run],
                "fake",
                driver_factory=lambda *args: UncertainJudge(),
                review_dir=archive,
            )
            before_audits = diagnosis_calls
            self.assertEqual(invoke("reassess", "review-uncertain-judge"), 1)
            self.assertEqual(diagnosis_calls, before_audits + 1)


class AutomaticDiagnosisTests(unittest.TestCase):
    def test_run_investigates_uncertainty_without_replacing_it(self) -> None:
        import tempfile
        from pathlib import Path

        from evals.__main__ import main
        from evals.fixtures import Workspace
        from evals.runner import Observation
        from tests.test_eval_runner import FakeDriver

        class Judge(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                packet = json.loads(prompt.split("\n\n", 1)[1])
                decisions = {}
                for item in packet["outputs"]:
                    decisions[item["label"]] = {
                        criterion["id"]: {
                            "verdict": "uncertain"
                            if criterion["id"] == "useful"
                            else "met",
                            "reason": "ambiguous_requirement"
                            if criterion["id"] == "useful"
                            else "observed",
                            "channel": "artifacts",
                            "evidence": ["A requested detail is unspecified."],
                        }
                        for criterion in packet["criteria"]
                    }
                return Observation(json.dumps(decisions), 10)

        def judge(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> Judge:
            return Judge()

        def candidate(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            return FakeDriver()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            cases = root / "cases"
            cases.mkdir()
            (cases / "one.json").write_text(
                json.dumps(
                    {
                        "id": "one",
                        "tags": [],
                        "files": {},
                        "rubric": [{"id": "useful", "description": "Useful answer."}],
                        "steps": [
                            {
                                "kind": "message",
                                "prompt": "Ready?",
                                "checks": [{"kind": "no_publish"}],
                            }
                        ],
                    }
                )
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
                        str(cases),
                        "--model",
                        "fake",
                        "--judge-model",
                        "fake",
                        "--review-dir",
                        str(root / "review"),
                        "--diagnose",
                    ],
                    driver_factory=candidate,
                    judge_factory=judge,
                )
            self.assertEqual(code, 4)
            result = json.loads(output.getvalue())
            self.assertEqual(result["results"][0]["behavior"], "unknown")
            self.assertEqual(len(result["diagnoses"]), 1)
            self.assertTrue(Path(result["diagnoses"][0]["report"]).is_file())


class CalibrationEvidenceTests(unittest.TestCase):
    def test_action_calibration_keeps_expected_labels_and_reasons_private(self) -> None:
        from pathlib import Path

        from evals.assessment import blind_packet
        from evals.calibration import Calibration, load_calibration

        for name in ("dialog-operation", "transaction-structure"):
            path = Path("evals/calibration") / (name + ".json")
            definition = Calibration.model_validate_json(path.read_text())
            rubric, runs, _ = load_calibration(path)
            packet, _ = blind_packet(rubric, runs)
            encoded = json.dumps(packet)
            for example in definition.examples:
                self.assertNotIn(example.id, encoded)
                self.assertNotIn(example.reason, encoded)
            self.assertTrue(any(frame.commands for run in runs for frame in run.frames))
            self.assertEqual(
                {run.frames[0].recording.channels["browser"] for run in runs},
                {"complete", "partial"},
            )


class RawOutputBoundaryTests(unittest.TestCase):
    def test_assessment_rejects_review_output_inside_any_git_checkout(self) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.assessment import assess
        from evals.evidence import EvidenceRun
        from evals.models import RubricCriterion
        from tests.test_eval_runner import FakeDriver

        with tempfile.TemporaryDirectory() as temporary:
            checkout = Path(temporary) / "another-checkout"
            subprocess.run(["git", "init", "-q", str(checkout)], check=True)
            review = checkout / "ignored-evidence"
            result = assess(
                [RubricCriterion(id="content", description="Useful content.")],
                [EvidenceRun("case", "fake", "source")],
                "fake",
                review_dir=review,
                driver_factory=lambda *args: FakeDriver(),
            )
            self.assertEqual(result[0].status, "error")
            self.assertFalse(review.exists())
            from evals.calibrate import main as calibrate

            with (
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                code = calibrate(
                    ["--model", "fake", "--review-dir", str(review)],
                    driver_factory=lambda *args: FakeDriver(),
                )
            self.assertEqual(code, 2)
            self.assertFalse(review.exists())
