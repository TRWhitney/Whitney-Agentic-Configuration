from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections.abc import Mapping
from pathlib import Path

from evals.evidence import EvidenceRun
from evals.fixtures import Workspace, git, make_workspace
from evals.models import CaseSpec
from evals.runner import CaseResult, CommandResult, Observation, run_case
from tests.evidence_support import evidence_text

SOURCE = Path(__file__).resolve().parents[1]


class FakeDriver:
    def __init__(self, reply: str = "Ready.", *, tokens: int | None = 10) -> None:
        self.reply = reply
        self.tokens = tokens
        self.closed = False
        self.compactions = 0
        self.created = 0

    def start(self) -> str:
        self.created += 1
        return f"thread-{self.created}"

    def message(self, thread: str, prompt: str) -> Observation:
        return Observation(self.reply, self.tokens)

    def compact(self, thread: str) -> Observation:
        self.compactions += 1
        return Observation("", self.tokens, compacted=True)

    def close(self) -> None:
        self.closed = True


def capture_case(
    case: CaseSpec,
    changes: Mapping[str, str | None],
    reply: str | tuple[str, ...],
    *,
    progress: tuple[str, str | None] | None = None,
    commands: tuple[str, ...] = (),
    command_results: tuple[CommandResult, ...] = (),
) -> tuple[CaseResult, EvidenceRun]:
    evidence = EvidenceRun(case.id, "example-model", "source")

    def factory(
        workspace: Workspace, model: str, timeout: float, max_tokens: int
    ) -> FakeDriver:
        replies = iter([reply] * len(case.steps) if isinstance(reply, str) else reply)

        class CaptureDriver(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                for name, text in changes.items():
                    path = workspace.file(name)
                    if text is None:
                        path.unlink(missing_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(text)
                if progress is not None:
                    path = workspace.progress_path(thread)
                    saved = json.loads(path.read_text())
                    saved["state"] = progress[0]
                    if progress[1] is None:
                        saved.pop("substate", None)
                    else:
                        saved["substate"] = progress[1]
                    path.write_text(json.dumps(saved))
                return Observation(
                    next(replies), 10, commands, command_results=command_results
                )

        return CaptureDriver()

    result = run_case(
        case,
        SOURCE,
        "example-model",
        driver_factory=factory,
        on_observation=evidence.observe,
    )
    return result, evidence


class EvaluationRunnerTests(unittest.TestCase):
    def case(self, checks: list[dict[str, object]]) -> CaseSpec:
        return CaseSpec.model_validate(
            {
                "id": "check-behavior",
                "tags": ["workflow"],
                "files": {"src/app.py": "value = 1\n"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Explain the value.",
                        "checks": checks
                        or [{"kind": "reply_regex", "pattern": "Ready"}],
                    }
                ],
            }
        )

    def run_with(
        self,
        case: CaseSpec,
        driver: FakeDriver,
        *,
        max_tokens: int = 100_000,
        evidence: EvidenceRun | None = None,
    ) -> CaseResult:
        return run_case(
            case,
            SOURCE,
            "example-model",
            driver_factory=lambda workspace, model, timeout, max_tokens: driver,
            max_tokens=max_tokens,
            on_observation=evidence.observe if evidence is not None else None,
        )

    def test_required_failure_cannot_be_averaged_into_a_pass(self) -> None:
        case = self.case(
            [
                {"kind": "unchanged", "paths": ["src/app.py"]},
                {"kind": "reply_regex", "pattern": "Never present"},
            ]
        )
        driver = FakeDriver()
        result = self.run_with(case, driver)
        self.assertEqual(result.status, "fail")
        self.assertEqual([check.passed for check in result.checks], [True, False])
        self.assertTrue(driver.closed)

    def test_empty_inventory_descriptions_remain_unjudged_evidence(self) -> None:
        from evals.assessment import blind_packet
        from evals.models import load_cases

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "seeded-wayfinding-recovery"
        )
        descriptions = [
            "Create a header-only CSV, or refuse export without creating a file.",
            "Create a CSV containing only the name,quantity header, "
            "or refuse export without creating a file.",
            "Refuse export, or create a CSV containing only the name,quantity header.",
            "Create a CSV with headers and inventory rows, or refuse export.",
            "Create a header-only CSV.",
        ]
        for description in descriptions:
            with self.subTest(description=description):
                reply = (
                    "Planning: 1 decided, 1 ready, unspecified: empty inventory.\n"
                    + description
                )
                evidence = EvidenceRun(case.id, "candidate", "source")
                result = self.run_with(case, FakeDriver(reply), evidence=evidence)
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertIsNone(result.assessment)
                self.assertEqual(evidence.frames[-1].reply, reply)
                packet, _ = blind_packet(case.rubric, [evidence])
                self.assertEqual(
                    packet["criteria"], [c.model_dump(mode="json") for c in case.rubric]
                )
                strings = evidence_text(packet)
                self.assertIn(reply, strings)

    def test_missing_usage_is_an_error(self) -> None:
        result = self.run_with(self.case([]), FakeDriver(tokens=None))
        self.assertEqual(result.status, "error")

    def test_uncommitted_setup_keeps_history_and_checks_the_starting_edits(
        self,
    ) -> None:
        raw = self.case([]).model_dump()
        raw["uncommitted_files"] = {
            "src/app.py": "value = 2\n",
            "draft.txt": "Existing draft.\n",
        }
        raw["steps"] = [
            {
                "kind": "message",
                "prompt": "Explain the current work without editing it.",
                "checks": [{"kind": "unchanged", "paths": ["src/app.py", "draft.txt"]}],
            }
        ]
        case = CaseSpec.model_validate(raw)
        with make_workspace(SOURCE, case) as workspace:
            self.assertEqual(
                git(workspace.root, "show", "HEAD:src/app.py"), "value = 1"
            )
            self.assertEqual(workspace.file("src/app.py").read_text(), "value = 2\n")
            self.assertEqual(git(workspace.root, "ls-files", "draft.txt"), "")
            self.assertEqual(workspace.baseline["src/app.py"], b"value = 2\n")
            self.assertEqual(workspace.baseline["draft.txt"], b"Existing draft.\n")
        self.assertEqual(self.run_with(case, FakeDriver()).status, "pass")

    def test_command_patterns_check_the_current_step_in_recorded_order(self) -> None:
        class CommandsDriver(FakeDriver):
            calls = 0

            def message(self, thread: str, prompt: str) -> Observation:
                self.calls += 1
                commands = ("load prototype", "run probe", "resume planning")
                return Observation("Ready.", 10, commands if self.calls == 1 else ())

        check: dict[str, object] = {
            "kind": "command_regex",
            "pattern": "(?s)load.*run.*resume",
        }
        case = self.case([check])
        self.assertEqual(self.run_with(case, CommandsDriver()).status, "pass")
        case.steps.append(case.steps[0].model_copy())
        result = self.run_with(case, CommandsDriver())
        self.assertEqual([item.passed for item in result.checks], [True, False])
        absent = self.case([{**check, "absent": True}])
        self.assertEqual(self.run_with(absent, FakeDriver()).status, "pass")
        self.assertEqual(self.run_with(absent, CommandsDriver()).status, "fail")

    def test_file_patterns_check_saved_content_and_require_the_file(self) -> None:
        for path, pattern, absent, expected in (
            ("src/app.py", r"(?m)^value = 1$", False, "pass"),
            ("src/app.py", r"value = 2", False, "fail"),
            ("src/app.py", r"value = 2", True, "pass"),
            ("src/app.py", r"value = 1", True, "fail"),
            ("missing.md", r"old answer", True, "fail"),
            ("src", r"old answer", True, "fail"),
        ):
            with self.subTest(path=path, pattern=pattern, absent=absent):
                case = self.case(
                    [
                        {
                            "kind": "file_regex",
                            "path": path,
                            "pattern": pattern,
                            "absent": absent,
                        }
                    ]
                )
                self.assertEqual(self.run_with(case, FakeDriver()).status, expected)

    def test_revised_answers_capture_both_records_for_hidden_assessment(self) -> None:
        from evals.models import load_cases

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "wayfinding-revised-answer"
        )
        design = "docs/planning/export/design.md"
        decision_map = "docs/planning/export/map.md"
        accepted = "Empty inventory: refuse export without creating a file.\n"
        for design_text, map_text in (
            (accepted, accepted),
            (case.files[design], accepted),
            (accepted, case.files[decision_map]),
            (accepted + "Empty inventory creates a header-only CSV.\n", accepted),
        ):
            with self.subTest(design=design_text, decision_map=map_text):

                def factory(
                    workspace: Workspace,
                    model: str,
                    timeout: float,
                    max_tokens: int,
                    *,
                    design_content: str = design_text,
                    map_content: str = map_text,
                ) -> FakeDriver:
                    workspace.file(design).write_text(design_content)
                    workspace.file(decision_map).write_text(map_content)
                    return FakeDriver(
                        "Planning: 2 decided, 1 ready, unspecified: existing file.\n"
                        "Refuse empty export."
                    )

                evidence = EvidenceRun(case.id, "candidate", "source")
                result = run_case(
                    case,
                    SOURCE,
                    "example-model",
                    driver_factory=factory,
                    on_observation=evidence.observe,
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertEqual(evidence.frames[-1].files[design], design_text)
                self.assertEqual(evidence.frames[-1].files[decision_map], map_text)
                self.assertTrue(case.rubric)

    def test_continue_discussion_captures_unchosen_options_for_assessment(self) -> None:
        from evals.models import load_cases

        case = next(
            case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id == "planning-continue-discussion"
        )
        design = "docs/planning/inventory/design.md"
        original = case.files[design]
        accepted = (
            "Export format is accepted: CSV. Empty inventory uses header-only CSV."
        )
        recommendation = (
            "I recommend CSV and a header-only file when empty. "
            "Should we agree on those export choices?"
        )
        for saved, reply in (
            (accepted, accepted),
            (original + "\n" + accepted, accepted),
            (original, accepted),
            (accepted, recommendation),
            (original + "\n" + accepted, recommendation),
            (
                original + "\nResearch: CSV supports tabular data.\n",
                recommendation,
            ),
        ):
            with self.subTest(saved=saved, reply=reply):

                def factory(
                    workspace: Workspace,
                    model: str,
                    timeout: float,
                    max_tokens: int,
                    *,
                    saved_text: str = saved,
                    answer: str = reply,
                ) -> FakeDriver:
                    class DiscussionDriver(FakeDriver):
                        messages = 0

                        def message(self, thread: str, prompt: str) -> Observation:
                            self.messages += 1
                            if self.messages == 1:
                                return Observation(
                                    "Export format and empty-inventory "
                                    "behavior remain open.",
                                    10,
                                )
                            workspace.file(design).write_text(saved_text)
                            return Observation(answer, 20)

                    return DiscussionDriver()

                evidence = EvidenceRun(case.id, "candidate", "source")
                result = run_case(
                    case,
                    SOURCE,
                    "example-model",
                    driver_factory=factory,
                    on_observation=evidence.observe,
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                self.assertEqual(evidence.frames[-1].files[design], saved)
                self.assertEqual(evidence.frames[-1].reply, reply)
                self.assertEqual(len(evidence.frames), 2)
                self.assertTrue(case.rubric)

    def test_wayfinding_progress_starts_the_final_reply(self) -> None:
        from evals.models import load_cases

        case = next(
            case
            for case in load_cases(SOURCE / "evals/cases")
            if case.id == "seeded-wayfinding-recovery"
        )
        reply = (
            "I read the saved record.\n\n"
            "Planning: 1 decided, 1 ready, unspecified: empty inventory.\n\n"
            "Create a header-only CSV, or refuse export without creating a file."
        )
        self.assertEqual(self.run_with(case, FakeDriver(reply)).status, "fail")

    def test_unchanged_directory_rejects_new_production_files(self) -> None:
        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            (workspace.root / "src/search.py").write_text("def search(): pass\n")
            return FakeDriver()

        result = run_case(
            self.case([{"kind": "unchanged", "paths": ["src"]}]),
            SOURCE,
            "example-model",
            driver_factory=factory,
        )
        self.assertEqual(result.status, "fail")

    def test_completed_task_is_checked_after_late_usage_crosses_the_guard(self) -> None:
        result = self.run_with(self.case([]), FakeDriver(tokens=11), max_tokens=10)
        self.assertEqual(result.status, "pass")
        self.assertIn("exceeded", result.detail)

    def test_agent_files_are_removed_after_failure(self) -> None:
        observed: list[Path] = []
        driver = FakeDriver()

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            observed.append(workspace.root)
            (workspace.root / "src/app.py").write_text("value = 2\n")
            return driver

        result = run_case(
            self.case([{"kind": "unchanged", "paths": ["src/app.py"]}]),
            SOURCE,
            "example-model",
            driver_factory=factory,
        )
        self.assertEqual(result.status, "fail")
        self.assertTrue(observed)
        self.assertFalse(observed[0].exists())

    def test_no_model_or_context_filling_is_needed_to_validate_checks(self) -> None:
        result = self.run_with(
            self.case(
                [
                    {"kind": "reply_regex", "pattern": "^Ready\\."},
                    {
                        "kind": "file_equals",
                        "path": "src/app.py",
                        "text": "value = 1\n",
                    },
                    {"kind": "commit_count", "count": 1},
                    {"kind": "tracker", "name": "local"},
                    {"kind": "no_publish"},
                ]
            ),
            FakeDriver(),
        )
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.tokens, 10)

    def test_incorrect_files_progress_tracker_and_dirty_commit_fail(self) -> None:
        checks: list[dict[str, object]] = [
            {"kind": "file_equals", "path": "src/app.py", "text": "wrong\n"},
            {"kind": "progress", "workflow": "fix", "state": "discovery"},
            {"kind": "tracker", "name": "github"},
            {"kind": "commit_count", "count": 1},
        ]

        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            (workspace.root / "src/app.py").write_text("uncommitted = True\n")
            return FakeDriver()

        result = run_case(
            self.case(checks), SOURCE, "example-model", driver_factory=factory
        )
        self.assertEqual(result.status, "fail")
        self.assertEqual([check.passed for check in result.checks], [False] * 4)

    def test_a_compaction_acknowledgement_is_not_completion(self) -> None:
        class AcknowledgementOnly(FakeDriver):
            def compact(self, thread: str) -> Observation:
                return Observation("", 10, compacted=False)

        case = CaseSpec.model_validate(
            {
                "id": "explicit-compaction",
                "integration": True,
                "tags": ["recovery"],
                "files": {},
                "steps": [
                    {
                        "kind": "compact",
                        "checks": [{"kind": "tracker", "name": "local"}],
                    }
                ],
            }
        )
        result = self.run_with(case, AcknowledgementOnly())
        self.assertEqual(result.status, "error")

    def test_searching_for_a_command_is_not_a_publication_attempt(self) -> None:
        class SearchDriver(FakeDriver):
            def message(self, thread: str, prompt: str) -> Observation:
                return Observation("Ready.", 10, ("rg 'gh pr create' docs",))

        result = self.run_with(self.case([{"kind": "no_publish"}]), SearchDriver())
        self.assertEqual(result.status, "pass")

    def test_service_fixture_detects_implicit_post_without_publishing(self) -> None:
        def factory(
            workspace: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            subprocess.run(
                [
                    sys.executable,
                    str(workspace.home / "bin/github.py"),
                    "api",
                    "repos/example/inventory/issues",
                    "-f",
                    "title=New issue",
                ],
                check=True,
                capture_output=True,
            )
            return FakeDriver()

        result = run_case(
            self.case([{"kind": "no_publish"}]),
            SOURCE,
            "example-model",
            driver_factory=factory,
        )
        self.assertEqual(result.status, "fail")

    def test_publication_checks_use_the_action_instead_of_argument_words(self) -> None:
        examples = [
            ("gh pr view 12 --json body --jq 'contains(\"create\")'", "pass"),
            ("gh issue list --search create", "pass"),
            ("gh issue delete 12 --yes", "fail"),
            ("gh --repo example/inventory pr create --title Example", "fail"),
            ("gh pr --repo example/inventory create --title Example", "fail"),
            ("gh api -XPOST repos/example/inventory/issues", "fail"),
        ]
        for command, expected in examples:
            with self.subTest(command=command):

                class CommandDriver(FakeDriver):
                    def __init__(self, command: str) -> None:
                        super().__init__()
                        self.command = command

                    def message(self, thread: str, prompt: str) -> Observation:
                        return Observation("Ready.", 10, (self.command,))

                result = self.run_with(
                    self.case([{"kind": "no_publish"}]), CommandDriver(command)
                )
                self.assertEqual(result.status, expected)

    def test_only_approved_paths_can_change_even_in_an_amended_commit(self) -> None:
        for unrelated in (False, True):
            with self.subTest(unrelated=unrelated):

                def factory(
                    workspace: Workspace,
                    model: str,
                    timeout: float,
                    max_tokens: int,
                    *,
                    create_unrelated: bool = unrelated,
                ) -> FakeDriver:
                    from evals.fixtures import git

                    (workspace.root / "src/app.py").write_text("value = 2\n")
                    if create_unrelated:
                        (workspace.root / "other.py").write_text("value = 3\n")
                    git(workspace.root, "add", ".")
                    git(workspace.root, "commit", "--amend", "--no-edit", "-q")
                    return FakeDriver()

                result = run_case(
                    self.case([{"kind": "only_changed", "paths": ["src/app.py"]}]),
                    SOURCE,
                    "example-model",
                    driver_factory=factory,
                )
                self.assertEqual(result.status, "fail" if unrelated else "pass")

    def test_conversations_share_a_project_without_sharing_progress(self) -> None:
        first = {
            "kind": "progress",
            "workflow": "novel-work",
            "state": "planning",
            "substate": "wayfinding",
        }
        second = {"kind": "progress", "workflow": "question", "state": "discovery"}
        case = CaseSpec.model_validate(
            {
                "id": "conversation-state",
                "tags": [],
                "files": {},
                "steps": [
                    {
                        "kind": "seed",
                        "conversation": "first",
                        "workflow": "novel-work",
                        "state": "planning",
                        "substate": "wayfinding",
                    },
                    {
                        "kind": "seed",
                        "conversation": "second",
                        "workflow": "question",
                        "state": "discovery",
                    },
                    {
                        "kind": "message",
                        "conversation": "first",
                        "prompt": "Continue",
                        "checks": [first],
                    },
                    {
                        "kind": "message",
                        "conversation": "second",
                        "prompt": "Continue",
                        "checks": [second],
                    },
                ],
            }
        )
        result = self.run_with(case, FakeDriver())
        self.assertEqual(result.status, "pass")
        self.assertEqual(result.tokens, 20)


if __name__ == "__main__":
    unittest.main()
