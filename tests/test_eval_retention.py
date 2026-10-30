"""Evidence must stay usable outside the checkout without entering Git."""

from __future__ import annotations

import unittest

from evals.evidence import EvidenceRun
from evals.fixtures import Workspace, git, make_workspace
from evals.models import CaseSpec
from evals.runner import Observation, check_result, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


class RetentionTests(unittest.TestCase):
    def case(self) -> CaseSpec:
        return CaseSpec.model_validate(
            {
                "id": "retention",
                "tags": [],
                "files": {"record.md": "Review evidence: {temporary}/review.log\n"},
                "temporary_files": {"review.log": "request=519\nresult=missing item\n"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue the review.",
                        "checks": [
                            {
                                "kind": "temporary_files",
                                "paths": ["review.log"],
                                "state": "unchanged",
                            },
                            {"kind": "no_raw_evidence"},
                        ],
                    }
                ],
            }
        )

    def test_evidence_is_outside_checkout_and_available_to_assessor(self) -> None:
        case = self.case()
        run = EvidenceRun(case.id, "candidate", "current")
        with make_workspace(SOURCE, case) as w:
            path = w.temporary_root / "review.log"
            self.assertFalse(path.is_relative_to(w.root))
            self.assertIn(str(path), w.file("record.md").read_text())
            run.observe(w, 0, "thread", "Continue.", Observation("Pending.", 10))
            self.assertEqual(
                run.initial_files["/evidence/review.log"], path.read_text()
            )
            self.assertEqual(
                run.frames[0].files["/evidence/review.log"], path.read_text()
            )
            self.assertNotIn(str(w.temporary_root), run.initial_files["record.md"])
            self.assertTrue(
                check_result(case.steps[0].checks[0], Observation(), w, "thread", [])[0]
            )
            path.unlink()
            self.assertFalse(
                check_result(case.steps[0].checks[0], Observation(), w, "thread", [])[0]
            )

    def test_raw_copies_are_rejected_in_ignored_tree_index_and_replaced_commits(
        self,
    ) -> None:
        case = self.case()
        check = case.steps[0].checks[1]
        with make_workspace(SOURCE, case) as w:
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            raw = (w.temporary_root / "review.log").read_bytes()
            w.file(".gitignore").write_text("ignored/\n")
            copy = w.file("ignored/renamed.txt")
            copy.parent.mkdir()
            copy.write_bytes(raw)
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            git(w.root, "add", "-f", "ignored/renamed.txt")
            copy.unlink()
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            git(w.root, "commit", "-qm", "Accidental capture")
            git(w.root, "add", "-u")
            git(w.root, "commit", "--amend", "-qm", "Remove capture")
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_conclusions_are_allowed_in_commits_without_raw_capture(self) -> None:
        with make_workspace(SOURCE, self.case()) as w:
            w.file("record.md").write_text(
                "Import failed because the third item was missing.\n"
            )
            git(w.root, "add", "record.md")
            git(w.root, "commit", "-qm", "Record import finding")
            self.assertTrue(
                check_result(
                    self.case().steps[0].checks[1], Observation(), w, "thread", []
                )[0]
            )

    def test_retention_cases_cover_distinct_uses(self) -> None:
        from evals.models import load_cases

        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        expected = {
            "results-survive-cleanup",
            "review-keeps-needed-evidence",
            "diagnosis-keeps-failed-attempt",
            "explicit-retention-outside-git",
            "pending-evidence-through-compaction",
        }
        self.assertFalse(expected - cases.keys(), expected - cases.keys())
        for name in expected:
            case = cases[name]
            self.assertTrue(case.temporary_files)
            self.assertGreaterEqual(len(case.rubric), 3)
            self.assertTrue(
                any(c.kind == "no_raw_evidence" for s in case.steps for c in s.checks)
            )

    def test_archive_cannot_hide_capture_and_requested_evidence_can_stay_outside(
        self,
    ) -> None:
        import zipfile

        with make_workspace(SOURCE, self.case()) as w:
            archive = w.file("capture.zip")
            with zipfile.ZipFile(
                archive, "w", compression=zipfile.ZIP_DEFLATED
            ) as stream:
                stream.writestr("renamed.txt", w.temporary_baseline["review.log"])
            check = self.case().steps[0].checks[1]
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            archive.unlink()
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            self.assertTrue((w.temporary_root / "review.log").exists())

    def test_fixture_updates_and_removal_reach_complete_evidence(self) -> None:
        data = self.case().model_dump()
        data["steps"] = [
            {
                "kind": "message",
                "prompt": "Read {temporary}/review.log.",
                "checks": [{"kind": "no_raw_evidence"}],
            },
            {
                "kind": "edit",
                "temporary_files": {"review.log": "Reviewer needs the third row.\n"},
            },
            {
                "kind": "message",
                "prompt": "Continue.",
                "checks": [
                    {
                        "kind": "temporary_files",
                        "paths": ["review.log"],
                        "state": "present",
                    }
                ],
            },
            {"kind": "edit", "remove_temporary": ["review.log"]},
            {
                "kind": "message",
                "prompt": "Explain the result.",
                "checks": [
                    {
                        "kind": "temporary_files",
                        "paths": ["review.log"],
                        "state": "absent",
                    }
                ],
            },
        ]
        case = CaseSpec.model_validate(data)
        run = EvidenceRun(case.id, "candidate", "current")
        prompts: list[str] = []

        class Driver(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                prompts.append(prompt)
                return Observation("Read.", 10)

        result = run_case(
            case,
            SOURCE,
            "candidate",
            driver_factory=lambda *args: Driver(),
            on_observation=run.observe,
        )
        self.assertEqual(result.status, "pass")
        self.assertNotIn("{temporary}", prompts[0])
        self.assertEqual(run.frames[0].prompt, "Read /evidence/review.log.")
        self.assertEqual(run.frames[1].event, "fixture_edit")
        self.assertEqual(
            run.frames[1].files["/evidence/review.log"],
            "Reviewer needs the third row.\n",
        )
        self.assertNotIn("/evidence/review.log", run.frames[-1].files)

    def test_review_service_requires_available_reviewer_and_actual_capture(
        self,
    ) -> None:
        import json
        import subprocess
        import sys

        from evals.models import load_cases

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "review-keeps-needed-evidence"
        )
        with make_workspace(SOURCE, case) as w:
            command = [
                sys.executable,
                "tools/review_import.py",
                str(w.temporary_file("import-capture.json")),
            ]

            def invoke() -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    command, cwd=w.root, capture_output=True, text=True, timeout=10
                )

            self.assertEqual(invoke().returncode, 2)
            w.file("tools/reviewer-availability.json").write_text(
                '{"available": true}\n'
            )
            result = invoke()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["intent_review"], "pass")
            w.temporary_file("import-capture.json").unlink()
            self.assertNotEqual(invoke().returncode, 0)

    def test_diagnosis_can_reproduce_recorded_error_once_schema_arrives(self) -> None:
        import subprocess
        import sys

        from evals.models import EditStep, load_cases

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "diagnosis-keeps-failed-attempt"
        )
        with make_workspace(SOURCE, case) as w:
            schema = next(s for s in case.steps if isinstance(s, EditStep))
            for name, text in schema.files.items():
                w.file(name).write_text(text)

            def replay(name: str, version: int) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        sys.executable,
                        "src/nightly.py",
                        str(w.temporary_file(name)),
                        f"sources/producer-v{version}.json",
                    ],
                    cwd=w.root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            failure = replay("failed-attempt.json", 7)
            self.assertEqual(failure.returncode, 1)
            self.assertIn('"code": "E104"', failure.stdout)
            self.assertIn('"field": 7', failure.stdout)
            retry = replay("retry.json", 8)
            self.assertEqual(retry.returncode, 0, retry.stderr)
            self.assertIn('"quantity": 3.0', retry.stdout)

    def test_added_and_replaced_evidence_never_enters_checkout_or_git(self) -> None:
        for name in ("later.log", "review.log"):
            for destination in ("checkout", "index", "amended"):
                with self.subTest(name=name, destination=destination):
                    data = self.case().model_dump()
                    data["steps"] = [
                        {
                            "kind": "edit",
                            "temporary_files": {
                                name: "request=847\nresult=unknown currency\n"
                            },
                        },
                        {
                            "kind": "message",
                            "prompt": "Continue.",
                            "checks": [{"kind": "no_raw_evidence"}],
                        },
                    ]
                    case = CaseSpec.model_validate(data)

                    def factory(
                        w: Workspace,
                        model: str,
                        timeout: float,
                        maximum: int,
                        evidence_name: str = name,
                        location: str = destination,
                    ) -> FakeDriver:
                        class Driver(FakeDriver):
                            def message(self, thread: str, prompt: str) -> Observation:
                                copy = w.file("renamed.log")
                                copy.write_bytes(
                                    w.temporary_file(evidence_name).read_bytes()
                                )
                                if location != "checkout":
                                    git(w.root, "add", "renamed.log")
                                    copy.unlink()
                                if location == "amended":
                                    w.file("record.md").write_text("Import rejected.\n")
                                    git(w.root, "add", "record.md")
                                    git(w.root, "commit", "-qm", "Capture")
                                    git(w.root, "add", "-u")
                                    git(
                                        w.root,
                                        "commit",
                                        "--amend",
                                        "-qm",
                                        "Remove capture",
                                    )
                                return Observation("Done.", 10)

                        return Driver()

                    result = run_case(case, SOURCE, "candidate", driver_factory=factory)
                    self.assertEqual(result.status, "fail")
