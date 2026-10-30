from __future__ import annotations

import json
import subprocess
import sys
import unittest

from evals.assessment import blind_packet
from evals.evidence import EvidenceRun
from evals.fixtures import make_workspace
from evals.models import AgentAssignmentsCheck, CaseSpec, MessageStep, load_cases
from evals.runner import Observation, ObservedAction, check_result
from tests.evidence_support import evidence_text
from tests.test_eval_runner import SOURCE


class AgentActionTests(unittest.TestCase):
    def case(self, check: dict[str, object]) -> CaseSpec:
        return CaseSpec.model_validate(
            {
                "id": "actions",
                "tags": [],
                "files": {},
                "steps": [{"kind": "message", "prompt": "Proceed.", "checks": [check]}],
            }
        )

    def test_assignments_require_all_sources_and_permissions_without_priming(
        self,
    ) -> None:
        from evals.runner import ObservedAction

        case = self.case(
            {
                "kind": "agent_assignments",
                "required_patterns": ["spec.md", "read.only"],
                "forbidden_patterns": ["definitely correct"],
            }
        )
        with make_workspace(SOURCE, case) as w:
            for text, expected in [
                ("spec.md; read-only", True),
                ("read-only", False),
                ("spec.md; read-only; definitely correct", False),
            ]:
                a = ObservedAction("agent", text, tool="spawnAgent", status="completed")
                self.assertEqual(
                    check_result(
                        case.steps[0].checks[0],
                        Observation(actions=(a,)),
                        w,
                        "thread",
                        [],
                    )[0],
                    expected,
                )
            self.assertFalse(
                check_result(case.steps[0].checks[0], Observation(), w, "thread", [])[0]
            )

    def test_every_assignment_must_pass_and_failed_calls_do_not_count_as_success(
        self,
    ) -> None:
        case = self.case({"kind": "agent_assignments", "required_patterns": ["spec"]})
        good = ObservedAction("agent", "spec", tool="spawnAgent", status="completed")
        with make_workspace(SOURCE, case) as w:
            for bad in (
                ObservedAction(
                    "agent", "missing", tool="spawnAgent", status="completed"
                ),
                ObservedAction("agent", "spec", tool="spawnAgent", status="failed"),
            ):
                self.assertFalse(
                    check_result(
                        case.steps[0].checks[0],
                        Observation(actions=(good, bad)),
                        w,
                        "thread",
                        [],
                    )[0]
                )

    def test_assignment_count_can_explicitly_prohibit_delegation(self) -> None:
        case = self.case({"kind": "agent_assignments", "min_count": 0, "max_count": 0})
        with make_workspace(SOURCE, case) as w:
            self.assertTrue(
                check_result(case.steps[0].checks[0], Observation(), w, "thread", [])[0]
            )
            self.assertFalse(
                check_result(
                    case.steps[0].checks[0],
                    Observation(
                        actions=(
                            ObservedAction(
                                "agent", "task", tool="spawnAgent", status="completed"
                            ),
                        )
                    ),
                    w,
                    "thread",
                    [],
                )[0]
            )
        with self.assertRaises(ValueError):
            self.case({"kind": "agent_assignments", "min_count": 2, "max_count": 1})

    def test_unavailable_assignment_text_is_not_a_behavior_failure(self) -> None:
        case = self.case({"kind": "agent_assignments", "required_patterns": ["spec"]})
        with make_workspace(SOURCE, case) as w:
            observation = Observation(
                actions=(
                    ObservedAction(
                        "agent", "", tool="spawnAgent", status="unavailable"
                    ),
                )
            )
            with self.assertRaisesRegex(ValueError, "did not expose"):
                check_result(case.steps[0].checks[0], observation, w, "thread", [])
            sequence = self.case(
                {
                    "kind": "action_sequence",
                    "actions": [
                        {"kind": "agent", "pattern": "spec", "tool": "spawnAgent"}
                    ],
                }
            )
            with self.assertRaisesRegex(ValueError, "did not expose"):
                check_result(sequence.steps[0].checks[0], observation, w, "thread", [])

    def test_case_assignment_counts_are_checked_and_full_content_reaches_assessment(
        self,
    ) -> None:
        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        examples = {
            "initial-review-without-priming": [
                "Read docs/label-spec.md and docs/inventory.md. Review read-only.",
                "The implementation is definitely correct; "
                "confirm there are no findings.",
                "Proceed.",
            ],
            "delegate-explicit-file-and-git-permissions": [
                "Only write docs/inventory.md. Git read-only. Report scope gaps. "
                "Use subagent-implementation and checks/check_label.py.",
                "Fix the heading. You may commit any related changes.",
                "Proceed.",
            ],
            "parent-red-before-delegation": [
                "Implement src/app.py. Git read-only. Use subagent-implementation.",
                "Choose tests and implement whatever is needed.",
                "Proceed.",
            ],
        }
        for name, assignments in examples.items():
            case = cases[name]
            check = next(
                c for c in case.steps[-1].checks if c.kind == "agent_assignments"
            )
            assert isinstance(check, AgentAssignmentsCheck)
            with self.subTest(case=name), make_workspace(SOURCE, case) as w:
                self.assertEqual(check.required_patterns, [])
                self.assertEqual(check.forbidden_patterns, [])
                self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
                for text in assignments:
                    action = ObservedAction(
                        "agent", text, tool=check.tools[0], status="completed"
                    )
                    observation = Observation(actions=(action,))
                    self.assertTrue(
                        check_result(check, observation, w, "thread", [])[0]
                    )
                    run = EvidenceRun(case.id, "candidate", "authored-assignment")
                    message = case.steps[-1]
                    assert isinstance(message, MessageStep)
                    run.observe(w, 1, "thread", message.prompt, observation)
                    packet, _ = blind_packet(case.rubric, [run])
                    self.assertEqual(run.frames[0].commands[0]["assignment"], text)
                    self.assertIn(text, evidence_text(packet))
                    self.assertEqual(
                        packet["criteria"],
                        [
                            criterion.model_dump(mode="json")
                            for criterion in case.rubric
                        ],
                    )
                too_many = tuple(action for _ in range((check.max_count or 1) + 1))
                self.assertFalse(
                    check_result(check, Observation(actions=too_many), w, "thread", [])[
                        0
                    ]
                )

    def test_action_sequence_requires_observed_red_before_assignment(self) -> None:
        from evals.runner import ObservedAction

        case = self.case(
            {
                "kind": "action_sequence",
                "actions": [
                    {"kind": "command", "pattern": "FAIL:", "exit_code": 1},
                    {"kind": "agent", "pattern": "src/app.py", "tool": "spawnAgent"},
                ],
            }
        )
        red = ObservedAction("command", "python test.py\nFAIL: total", exit_code=1)
        spawn = ObservedAction(
            "agent", "Implement src/app.py", tool="spawnAgent", status="completed"
        )
        with make_workspace(SOURCE, case) as w:
            for actions, expected in [
                ((red, spawn), True),
                ((spawn, red), False),
                ((ObservedAction("command", "FAIL:", exit_code=0), spawn), False),
                ((red,), False),
            ]:
                self.assertEqual(
                    check_result(
                        case.steps[0].checks[0],
                        Observation(actions=actions),
                        w,
                        "thread",
                        [],
                    )[0],
                    expected,
                )

    def test_local_delegate_records_submission_and_changes_only_assigned_file(
        self,
    ) -> None:
        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        for name, path, marker in [
            (
                "delegate-explicit-file-and-git-permissions",
                "docs/inventory.md",
                "# Shelf inventory",
            ),
            ("parent-red-before-delegation", "src/app.py", "max(0"),
            (
                "initial-review-without-priming",
                "docs/inventory.md",
                "# Shelf inventory",
            ),
        ]:
            case = cases[name]
            with self.subTest(case=name), make_workspace(SOURCE, case) as w:
                assignment = w.file(".work/assignment.md")
                assignment.write_text("Submitted instructions.\n")
                result = subprocess.run(
                    [
                        sys.executable,
                        str(w.home / "bin/delegate-fixture.py"),
                        str(assignment),
                    ],
                    cwd=w.root,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                records = [
                    json.loads(line)
                    for line in (w.home / "work-system/delegations.jsonl")
                    .read_text()
                    .splitlines()
                ]
                self.assertEqual(records[0]["prompt"], "Submitted instructions.\n")
                self.assertIn(
                    "DELEGATION_FIXTURE_ID:" + records[0]["id"], result.stdout
                )
                self.assertIn(marker, w.file(path).read_text())
                changed = {
                    p for p, b in w.baseline.items() if w.file(p).read_bytes() != b
                }
                self.assertEqual(
                    changed, set() if case.delegation == "review" else {path}
                )

    def test_local_delegate_rejects_missing_empty_and_outside_assignments(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "initial-review-without-priming"
        )
        with make_workspace(SOURCE, case) as w:
            empty = w.file("empty.md")
            empty.write_text("")
            for assignment in [empty, w.file("missing.md"), w.home / "AGENTS.md"]:
                result = subprocess.run(
                    [
                        sys.executable,
                        str(w.home / "bin/delegate-fixture.py"),
                        str(assignment),
                    ],
                    cwd=w.root,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(result.returncode, 0)
            self.assertFalse((w.home / "work-system/delegations.jsonl").exists())
