from __future__ import annotations

import importlib.util
import json
import unittest
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

from pydantic import RootModel

from evals.fixtures import make_workspace
from evals.models import CaseSpec
from evals.runner import ExecutionFailed, LimitReached

if TYPE_CHECKING:
    from evals.codex import CodexDriver

SOURCE = Path(__file__).resolve().parents[1]


def event(method: str, **data: object) -> SimpleNamespace:
    return SimpleNamespace(method=method, payload=RootModel[dict[str, object]](data))


class FakeClient:
    def __init__(self) -> None:
        self.notifications: list[SimpleNamespace] = []
        self.compactions: list[str] = []
        self.closed = False
        self.starts: list[dict[str, object]] = []
        self.hook_path: Path | None = None

    def thread_start(self, arguments: dict[str, object]) -> SimpleNamespace:
        self.starts.append(arguments)
        return SimpleNamespace(
            thread=SimpleNamespace(id="runtime-thread"),
            active_permission_profile=SimpleNamespace(id="eval"),
        )

    def request(
        self, method: str, params: dict[str, object], *, response_model: object
    ) -> SimpleNamespace | RootModel[dict[str, object]]:
        if method == "hooks/list":
            assert self.hook_path is not None
            configured = json.loads(self.hook_path.read_text())
            handler = configured["hooks"]["SessionStart"][0]["hooks"][0]
            return RootModel[dict[str, object]](
                {
                    "data": [
                        {
                            "errors": [],
                            "hooks": [
                                {
                                    "command": handler["command"],
                                    "sourcePath": str(self.hook_path),
                                    "eventName": "sessionStart",
                                    "matcher": "^compact$",
                                    "enabled": True,
                                }
                            ],
                        }
                    ]
                }
            )
        assert method == "thread/start"
        return self.thread_start(params)

    def start(self) -> None:
        pass

    def initialize(self) -> None:
        pass

    def close(self) -> None:
        self.closed = True

    def thread_compact(self, thread: str) -> None:
        self.compactions.append(thread)

    def watch(self, thread: str) -> None:
        pass

    def hook_runs(self, thread: str) -> list[dict[str, object]]:
        return []

    def next_compaction_notification(self) -> SimpleNamespace:
        if not self.notifications:
            raise TimeoutError("No completion notification.")
        return self.notifications.pop(0)


@unittest.skipUnless(
    importlib.util.find_spec("openai_codex"), "Optional Codex SDK is not installed."
)
class CodexAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        from evals.codex import ObservableClient

        self.real_client_type = ObservableClient
        case = CaseSpec.model_validate(
            {
                "id": "adapter",
                "tags": [],
                "files": {},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Ready?",
                        "checks": [{"kind": "reply_regex", "pattern": "Ready"}],
                    }
                ],
            }
        )
        context = make_workspace(SOURCE, case)
        self.workspace = context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
        self.client = FakeClient()
        self.client.hook_path = self.workspace.home / "hooks.json"
        for replacement in (
            patch("evals.codex.ObservableClient", return_value=self.client),
            patch.object(self.workspace, "copy_credentials"),
        ):
            replacement.start()
            self.addCleanup(replacement.stop)

    def driver(self, *, max_tokens: int = 100) -> CodexDriver:
        from evals.codex import CodexDriver

        driver = CodexDriver(self.workspace, "example-model", 10, max_tokens)
        self.addCleanup(driver.close)
        return driver

    def test_worker_runtime_role_does_not_supply_the_test_decision(self) -> None:
        from evals.codex import CodexDriver

        self.workspace.candidate_role = "implementation-worker"
        worker = self.driver()
        worker.start()
        instructions = self.client.starts[-1]["developerInstructions"]
        self.assertEqual(self.client.starts[-1]["config"], {"bypass_hook_trust": True})
        self.assertIsInstance(instructions, str)
        assert isinstance(instructions, str)
        self.assertIn("spawned implementation subagent", instructions)
        judge = CodexDriver(
            self.workspace,
            "example-model",
            10,
            0,
            read_only=True,
            instructions="Assess the evidence.",
        )
        self.addCleanup(judge.close)
        judge.start()
        self.assertEqual(
            self.client.starts[-1]["developerInstructions"], "Assess the evidence."
        )
        self.assertNotIn("config", self.client.starts[-1])

    def stream(self, events: list[SimpleNamespace]) -> None:
        handle = SimpleNamespace(stream=lambda: iter(events))
        replacement = patch(
            "evals.codex.Thread",
            return_value=SimpleNamespace(turn=lambda prompt: handle),
        )
        replacement.start()
        self.addCleanup(replacement.stop)

    def test_wait_without_targets_does_not_hide_available_child_findings(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "subAgentActivity",
                        "kind": "completed",
                        "agentThreadId": "child",
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "collabAgentToolCall",
                        "tool": "wait",
                        "status": "completed",
                        "receiverThreadIds": [],
                        "agentsStates": {},
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        snapshot = RootModel[dict[str, object]](
            {
                "thread": {
                    "turns": [
                        {
                            "items": [
                                {
                                    "type": "agentMessage",
                                    "text": "Reviewed source; no findings.",
                                }
                            ]
                        }
                    ]
                }
            }
        )
        with patch.object(
            self.client, "thread_read", return_value=snapshot, create=True
        ):
            result = self.driver().message("thread", "Finish.")
        self.assertEqual(result.recording.channels["children"], "complete")
        self.assertEqual(result.recording.problems, [])

    def test_collaboration_status_does_not_establish_available_findings(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "collabAgentToolCall",
                        "tool": "wait",
                        "status": "completed",
                        "receiverThreadIds": ["child"],
                        "agentsStates": {"child": {"status": "completed"}},
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("thread", "Continue.")
        self.assertEqual(result.recording.channels["children"], "partial")
        self.assertTrue(result.recording.problems)

    def test_unknown_native_action_is_reported_as_partial_recording(self) -> None:
        self.stream(
            [
                event("item/completed", item={"type": "unhandledTool", "id": "new"}),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("thread", "Continue.")
        self.assertTrue(result.completed)
        self.assertEqual(result.recording.actions, "partial")
        self.assertTrue(result.recording.problems)
        self.assertEqual(len(result.actions), 1)
        self.assertEqual(
            json.loads(result.actions[0].text), {"type": "unhandledTool", "id": "new"}
        )

    def test_sleep_event_is_retained_without_losing_next_command_result(self) -> None:
        from evals.evidence import EvidenceRun

        native = {"type": "sleep", "id": "pause", "durationMs": 25}
        self.stream(
            [
                event("item/completed", item=native),
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "read status",
                        "exitCode": 0,
                        "aggregatedOutput": "Review complete",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        observation = self.driver().message("thread", "Continue.")
        self.assertEqual(observation.recording.actions, "complete")
        self.assertEqual(observation.recording.problems, [])
        run = EvidenceRun("adapter", "candidate", "condition")
        run.observe(self.workspace, 0, "thread", "Continue.", observation)
        self.assertEqual(run.frames[0].commands[0], {"native_item": native})
        self.assertEqual(run.frames[0].commands[1]["output"], "Review complete")

    def test_hook_context_is_recorded_separately_from_agent_commands(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "hookPrompt",
                        "fragments": [
                            {
                                "hookRunId": "recovery",
                                "text": "Restored planning from the existing record.",
                            }
                        ],
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "read status",
                        "exitCode": 0,
                        "aggregatedOutput": "Pending overwrite decision",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("thread", "Continue.")
        self.assertEqual(result.recording.actions, "complete")
        self.assertEqual(result.actions[0].kind, "hook")
        self.assertIn("Restored planning", result.actions[0].text)
        self.assertEqual(result.command_results[0].output, "Pending overwrite decision")

    def test_native_hook_notifications_keep_conversation_identity(self) -> None:
        from openai_codex.client import CodexConfig

        client = self.real_client_type(CodexConfig())
        self.addCleanup(client.close)
        for identifier in ("one", "two"):
            client._coerce_notification(
                "hook/completed",
                {
                    "threadId": identifier,
                    "turnId": "compact",
                    "run": {
                        "id": identifier + "-hook",
                        "eventName": "sessionStart",
                        "handlerType": "command",
                        "executionMode": "sync",
                        "scope": "thread",
                        "sourcePath": "/home/hooks.json",
                        "status": "completed",
                        "source": "user",
                        "startedAt": 1,
                        "displayOrder": 0,
                        "entries": [
                            {
                                "kind": "context",
                                "text": "Saved record for " + identifier,
                            }
                        ],
                    },
                },
            )
        one = client.hook_runs("one")
        self.assertEqual(one[0]["id"], "one-hook")
        self.assertEqual(client.hook_runs("one"), [])
        self.assertEqual(client.hook_runs("two")[0]["id"], "two-hook")

    def test_missing_viewed_image_is_a_capture_problem(self) -> None:
        self.stream(
            [
                event(
                    "item/completed", item={"type": "imageView", "path": "/missing.png"}
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("thread", "Inspect.")
        self.assertTrue(result.completed)
        self.assertEqual(result.recording.channels["images"], "partial")
        self.assertTrue(result.recording.problems)

    def test_native_image_views_are_observed_separately_from_capture_generation(
        self,
    ) -> None:
        image = self.workspace.temporary_root / "view.png"
        image.write_bytes(b"\x89PNG\r\n\x1a\n")
        self.stream(
            [
                event("item/completed", item={"type": "imageView", "path": str(image)}),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("thread", "Inspect the image.")
        self.assertEqual(
            [(a.kind, a.text) for a in result.actions], [("image", str(image))]
        )
        self.assertEqual(result.browser_evidence[0]["origin"], "candidate_image_view")
        self.assertTrue(result.browser_evidence[0]["images"])

    def test_images_are_sent_as_image_inputs_alongside_the_packet(self) -> None:
        from openai_codex import LocalImageInput, TextInput

        driver = self.driver()
        driver.image_paths = ["/outside/image-1.png", "/outside/image-2.png"]
        seen: list[object] = []

        def turn(content: object) -> SimpleNamespace:
            seen.append(content)
            return SimpleNamespace(
                stream=lambda: iter(
                    [
                        event(
                            "thread/tokenUsage/updated",
                            threadId="thread",
                            tokenUsage={"total": {"totalTokens": 7}},
                        ),
                        event("turn/completed", turn={"status": "completed"}),
                    ]
                )
            )

        with patch("evals.codex.Thread", return_value=SimpleNamespace(turn=turn)):
            observation = driver.message("thread", "The complete blinded packet.")
        self.assertEqual(observation.tokens, 7)
        self.assertEqual(
            seen,
            [
                [
                    TextInput("The complete blinded packet."),
                    LocalImageInput("/outside/image-1.png"),
                    LocalImageInput("/outside/image-2.png"),
                ]
            ],
        )

    def test_assessor_rejects_non_command_tools(self) -> None:
        from evals.codex import CodexDriver

        self.stream(
            [event("item/completed", item={"type": "fileChange", "changes": []})]
        )
        driver = CodexDriver(
            self.workspace,
            "judge",
            10,
            100,
            read_only=True,
            instructions="Assess only.",
        )
        self.addCleanup(driver.close)
        with self.assertRaisesRegex(ValueError, "Judge used"):
            driver.message("one", "Assess this output.")

    def test_judge_turn_supplies_its_structured_response_contract(self) -> None:
        from evals.assessment_models import JudgeResponse
        from evals.codex import CodexDriver

        schema = JudgeResponse.model_json_schema()
        driver = CodexDriver(
            self.workspace, "judge", 10, 100, read_only=True, output_schema=schema
        )
        self.addCleanup(driver.close)
        events = [
            event(
                "thread/tokenUsage/updated",
                threadId="one",
                tokenUsage={"total": {"totalTokens": 10}},
            ),
            event("turn/completed", turn={"status": "completed"}),
        ]
        with patch("evals.codex.Thread") as thread:
            thread.return_value.turn.return_value.stream.return_value = iter(events)
            driver.message("one", "Assess this output.")
            thread.return_value.turn.assert_called_once_with(
                "Assess this output.", output_schema=schema
            )

    def test_native_runs_disable_apps(self) -> None:
        with patch(
            "evals.codex.ObservableClient", return_value=self.client
        ) as constructor:
            self.driver()
        self.assertIn(
            "features.apps=false", constructor.call_args.args[0].config_overrides
        )

    def test_agent_assignments_and_commands_keep_parent_event_order(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "python test.py",
                        "exitCode": 1,
                        "aggregatedOutput": "FAIL: total",
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "collabAgentToolCall",
                        "tool": "spawnAgent",
                        "status": "completed",
                        "prompt": "Implement src/app.py",
                        "agentsStates": {
                            "child": {
                                "status": "completed",
                                "message": "Child completion is not an assignment.",
                            }
                        },
                    },
                ),
                event(
                    "item/completed",
                    item={"type": "agentMessage", "text": "Parent answer."},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("one", "Proceed.")
        self.assertEqual([a.kind for a in result.actions], ["command", "agent"])
        self.assertIn("FAIL: total", result.actions[0].text)
        self.assertEqual(result.actions[1].text, "Implement src/app.py")
        self.assertEqual(result.actions[1].tool, "spawnAgent")
        self.assertEqual(result.reply, "Parent answer.")

    def test_native_wait_preserves_reviewer_messages_separately_from_assignment(
        self,
    ) -> None:
        from openai_codex.client import CodexConfig

        states = {
            "reviewer": {
                "status": "completed",
                "message": "Correction review of Unicode search: no findings.",
            }
        }
        client = self.real_client_type(CodexConfig())
        self.addCleanup(client.close)
        native = client._coerce_notification(
            "item/completed",
            {
                "completedAtMs": 1,
                "threadId": "one",
                "turnId": "turn",
                "item": {
                    "id": "wait",
                    "type": "collabAgentToolCall",
                    "tool": "wait",
                    "status": "completed",
                    "senderThreadId": "one",
                    "receiverThreadIds": ["reviewer"],
                    "agentsStates": states,
                },
            },
        )
        self.stream(
            [
                SimpleNamespace(method=native.method, payload=native.payload),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        action = self.driver().message("one", "Continue.").actions[0]
        self.assertEqual(action.text, "")
        self.assertEqual(action.tool, "wait")
        self.assertEqual(action.agent_results, states)

    def test_completed_native_child_work_is_captured_before_runtime_cleanup(
        self,
    ) -> None:
        commands = {
            "type": "commandExecution",
            "command": "git diff -- src/app.py",
            "exitCode": 0,
            "aggregatedOutput": "Both search comparisons use casefold.",
        }
        finding = {
            "type": "agentMessage",
            "phase": "final_answer",
            "text": "Correction review: Unicode search is repaired. No findings.",
        }
        nested_activity = {
            "type": "subAgentActivity",
            "kind": "started",
            "id": "nested-start",
            "agentPath": "/reviewer/worker",
            "agentThreadId": "nested-worker",
        }
        snapshot = RootModel[dict[str, object]](
            {
                "thread": {
                    "turns": [
                        {
                            "id": "review-turn",
                            "status": "completed",
                            "items": [
                                {
                                    "type": "reasoning",
                                    "summary": ["Not review evidence."],
                                },
                                {
                                    **nested_activity,
                                    "model": "candidate-model",
                                    "reasoningEffort": "high",
                                },
                                commands,
                                finding,
                            ],
                        }
                    ]
                }
            }
        )
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "subAgentActivity",
                        "kind": "started",
                        "agentThreadId": "reviewer",
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "git commit --amend --no-edit",
                        "exitCode": 0,
                        "aggregatedOutput": "Committed before child completion.",
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "subAgentActivity",
                        "kind": "completed",
                        "agentThreadId": "reviewer",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        with patch.object(
            self.client, "thread_read", return_value=snapshot, create=True
        ) as read:
            driver = self.driver()
            driver.start()
            self.assertFalse(self.client.starts[-1]["ephemeral"])
            result = driver.message("one", "Fix the review finding.")
        read.assert_called_once_with("reviewer", include_turns=True)
        self.assertEqual(
            [a.kind for a in result.actions], ["agent", "command", "agent"]
        )
        self.assertEqual(result.actions[-1].tool, "agentCompleted")
        self.assertIsNone(result.actions[0].agent_results)
        self.assertEqual(
            result.actions[-1].agent_results,
            {
                "reviewer": {
                    "turns": [
                        {
                            "id": "review-turn",
                            "status": "completed",
                            "items": [nested_activity, commands, finding],
                        }
                    ]
                }
            },
        )
        self.assertEqual(result.actions[0].text, "")
        self.assertTrue(result.completed)

    def test_unavailable_child_work_stays_missing_evidence(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "subAgentActivity",
                        "kind": "started",
                        "agentThreadId": "reviewer",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        with patch.object(
            self.client,
            "thread_read",
            side_effect=ValueError("Missing review"),
            create=True,
        ):
            result = self.driver().message("one", "Continue.")
        self.assertEqual(
            result.actions[0].agent_results,
            {"reviewer": {"unavailable": "Missing review"}},
        )
        self.assertTrue(result.completed)

    def test_invalid_agent_assignments_are_errors(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "collabAgentToolCall",
                        "tool": "spawnAgent",
                        "status": "completed",
                        "prompt": 42,
                    },
                )
            ]
        )
        with self.assertRaisesRegex(ValueError, "Invalid agent call"):
            self.driver().message("one", "Proceed.")

    def test_native_file_changes_preserve_patches_and_event_order(self) -> None:
        from openai_codex.client import CodexConfig

        changes = [
            {
                "path": str(self.workspace.root / "old.md"),
                "kind": {
                    "type": "update",
                    "move_path": str(self.workspace.root / "new.md"),
                },
                "diff": "@@ -1 +1 @@\n-old\n+accepted\n",
            }
        ]
        client = self.real_client_type(CodexConfig())
        self.addCleanup(client.close)
        for status in ("completed", "failed"):
            with self.subTest(status=status):
                patch_event = client._coerce_notification(
                    "item/completed",
                    {
                        "completedAtMs": 1,
                        "threadId": "one",
                        "turnId": "turn",
                        "item": {
                            "id": "patch",
                            "type": "fileChange",
                            "status": status,
                            "changes": changes,
                        },
                    },
                )
                self.stream(
                    [
                        SimpleNamespace(
                            method=patch_event.method, payload=patch_event.payload
                        ),
                        event(
                            "item/completed",
                            item={
                                "type": "commandExecution",
                                "command": "python checks.py",
                                "exitCode": 0,
                                "aggregatedOutput": "PASS",
                            },
                        ),
                        event("turn/completed", turn={"status": "completed"}),
                    ]
                )
                result = self.driver().message("one", "Proceed.")
                self.assertEqual([a.kind for a in result.actions], ["file", "command"])
                self.assertEqual(json.loads(result.actions[0].text), changes)
                self.assertEqual(result.actions[0].status, status)
                self.assertEqual(result.command_results[0].output, "PASS")

    def test_fixture_submission_uses_recorded_text_at_command_position(self) -> None:
        identifier = "a" * 32
        path = self.workspace.home / "work-system/delegations.jsonl"
        path.write_text(
            '{"id":"' + identifier + '","prompt":"Review spec.md read-only."}\n'
        )
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "python delegate-fixture.py assignment.md",
                        "exitCode": 0,
                        "aggregatedOutput": "DELEGATION_FIXTURE_ID:"
                        + identifier
                        + "\nNo findings.",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("one", "Delegate review.")
        self.assertEqual([a.kind for a in result.actions], ["command", "agent"])
        self.assertEqual(result.actions[1].text, "Review spec.md read-only.")
        self.assertEqual(result.actions[1].tool, "delegateFixture")

    def test_pinned_sdk_preserves_agent_prompt_fields(self) -> None:
        from openai_codex.client import CodexConfig

        client = self.real_client_type(CodexConfig())
        self.addCleanup(client.close)
        notification = client._coerce_notification(
            "item/completed",
            {
                "completedAtMs": 1,
                "threadId": "parent",
                "turnId": "turn",
                "item": {
                    "id": "spawn",
                    "type": "collabAgentToolCall",
                    "senderThreadId": "parent",
                    "receiverThreadIds": ["child"],
                    "tool": "spawnAgent",
                    "status": "completed",
                    "prompt": "Implement src/app.py",
                    "agentsStates": {},
                },
            },
        )
        from evals.codex import event_data, mapping

        item = mapping(event_data(notification.payload)["item"])
        self.assertEqual(item["tool"], "spawnAgent")
        self.assertEqual(item["prompt"], "Implement src/app.py")

    def test_unexpected_external_tool_invalidates_the_run(self) -> None:
        self.stream([event("item/completed", item={"type": "mcpToolCall"})])
        with self.assertRaisesRegex(ValueError, "External service tool"):
            self.driver().message("one", "Check planning.")

    def test_compaction_waits_for_the_matching_conversation(self) -> None:
        driver = self.driver()
        driver.tokens["one"] = 10
        self.client.notifications = [
            event(
                "item/completed",
                threadId="other",
                turnId="unrelated",
                item={"type": "contextCompaction", "id": "other-item"},
            ),
            event(
                "item/completed",
                threadId="one",
                turnId="compact-one",
                item={"type": "contextCompaction", "id": "context-one"},
            ),
            event(
                "turn/completed",
                threadId="one",
                turn={"id": "compact-one", "status": "completed"},
            ),
        ]
        result = driver.compact("one")
        self.assertTrue(result.compacted)
        self.assertEqual(self.client.compactions, ["one"])
        self.assertEqual(self.client.notifications, [])

    def test_compaction_acknowledgement_without_event_cannot_pass(self) -> None:
        with self.assertRaises(TimeoutError):
            self.driver().compact("one")

    def test_documented_compaction_item_confirms_the_operation(self) -> None:
        driver = self.driver()
        driver.tokens["one"] = 10
        self.client.notifications = [
            event(
                "item/completed",
                threadId="one",
                turnId="compact-one",
                item={"type": "contextCompaction", "id": "context-one"},
            ),
            event(
                "turn/completed",
                threadId="one",
                turn={"id": "compact-one", "status": "completed"},
            ),
        ]
        self.assertTrue(driver.compact("one").compacted)

    def test_compacted_event_alone_does_not_make_the_next_turn_ready(self) -> None:
        driver = self.driver()
        self.client.notifications = [
            event(
                "item/completed",
                threadId="one",
                turnId="compact-one",
                item={"type": "contextCompaction", "id": "context-one"},
            )
        ]
        with self.assertRaises(TimeoutError):
            driver.compact("one")

    def test_native_items_are_normalized_and_unknown_noise_is_ignored(self) -> None:
        self.stream(
            [
                SimpleNamespace(method="runtime/noise", payload=object()),
                event(
                    "item/completed", item={"type": "agentMessage", "text": "Ready."}
                ),
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={"total": {"totalTokens": 11}},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("one", "Ready?")
        self.assertEqual(result.reply, "Ready.")
        self.assertEqual(result.tokens, 11)

    def test_completed_commentary_survives_an_interruption(self) -> None:
        def stream() -> Iterator[SimpleNamespace]:
            yield event(
                "item/agentMessage/delta",
                threadId="one",
                itemId="progress",
                delta="Checking the layout.",
            )
            yield event(
                "item/completed",
                item={
                    "id": "progress",
                    "type": "agentMessage",
                    "phase": "commentary",
                    "text": "Checking the layout.",
                },
            )
            raise TimeoutError("Stream stopped.")

        with (
            patch(
                "evals.codex.Thread",
                return_value=SimpleNamespace(
                    turn=lambda prompt: SimpleNamespace(stream=stream)
                ),
            ),
            self.assertRaises(TimeoutError) as raised,
        ):
            self.driver().message("one", "Assess.")
        observation = getattr(raised.exception, "observation", None)
        assert observation is not None
        self.assertEqual(observation.commentary, ["Checking the layout."])
        self.assertEqual(observation.reply, "")

    def test_interrupted_verdict_keeps_unfinished_message_text(self) -> None:
        from evals.runner import TimeLimitReached

        def stream() -> Iterator[SimpleNamespace]:
            yield event(
                "item/agentMessage/delta",
                threadId="one",
                itemId="verdict",
                delta='{"candidates":[',
            )
            raise TimeoutError("Stream stopped.")

        with (
            patch(
                "evals.codex.Thread",
                return_value=SimpleNamespace(
                    turn=lambda prompt: SimpleNamespace(stream=stream)
                ),
            ),
            self.assertRaises(TimeLimitReached) as raised,
        ):
            self.driver().message("one", "Assess.")
        observation = raised.exception.observation
        assert observation is not None
        self.assertEqual(observation.partial_reply, '{"candidates":[')
        self.assertFalse(observation.completed)

    def test_failed_turn_retains_completed_actions_for_diagnosis(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "cat source.py",
                        "exitCode": 0,
                        "aggregatedOutput": "source contents",
                    },
                ),
                event("turn/completed", turn={"status": "failed"}),
            ]
        )
        with self.assertRaises(ExecutionFailed) as raised:
            self.driver().message("one", "Inspect.")
        observation = raised.exception.observation
        self.assertIsNotNone(observation)
        assert observation is not None
        self.assertFalse(observation.completed)
        self.assertEqual(observation.command_results[0].output, "source contents")

    def test_failed_native_turn_cannot_pass(self) -> None:
        self.stream([event("turn/completed", turn={"status": "failed"})])
        with self.assertRaises(ValueError):
            self.driver().message("one", "Ready?")

    def test_completed_commands_keep_exit_codes_and_combined_output(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "python check.py",
                        "exitCode": 1,
                        "aggregatedOutput": "AssertionError: Unicode",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        observation = self.driver().message("one", "Run checks.")
        self.assertEqual(observation.commands, ("python check.py",))
        result = observation.command_results[0]
        self.assertEqual(result.command, "python check.py")
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output, "AssertionError: Unicode")

    def test_quiet_successful_command_is_not_a_recording_fault(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "git diff --check",
                        "exitCode": 0,
                        "aggregatedOutput": None,
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("one", "Check the edit.")
        self.assertEqual(result.recording.channels["commands"], "complete")
        self.assertEqual(result.recording.problems, [])

    def test_missing_command_result_fields_remain_unknown(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={"type": "commandExecution", "command": "python check.py"},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        result = self.driver().message("one", "Run checks.").command_results[0]
        self.assertIsNone(result.exit_code)
        self.assertIsNone(result.output)

    def test_bad_command_result_types_are_runtime_errors(self) -> None:
        for fields in ({"exitCode": True}, {"aggregatedOutput": 42}):
            with self.subTest(fields=fields):
                self.stream(
                    [
                        event(
                            "item/completed",
                            item={"type": "commandExecution", **fields},
                        )
                    ]
                )
                with self.assertRaisesRegex(ValueError, "Invalid command"):
                    self.driver().message("one", "Run checks.")

    def test_reply_checks_use_the_final_answer_instead_of_progress_updates(
        self,
    ) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "agentMessage",
                        "phase": "commentary",
                        "text": "Ready.",
                    },
                ),
                event(
                    "item/completed",
                    item={
                        "type": "agentMessage",
                        "phase": "final_answer",
                        "text": "Waiting.",
                    },
                ),
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={"total": {"totalTokens": 11}},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        self.assertEqual(self.driver().message("one", "Ready?").reply, "Waiting.")

    def test_failed_native_turn_reports_the_runtime_reason(self) -> None:
        self.stream(
            [
                event(
                    "turn/completed",
                    turn={
                        "status": "failed",
                        "error": {"message": "Service unavailable."},
                    },
                )
            ]
        )
        with self.assertRaisesRegex(ValueError, "Service unavailable"):
            self.driver().message("one", "Ready?")

    def test_completed_answer_survives_a_late_token_notification(self) -> None:
        self.stream(
            [
                event(
                    "item/completed", item={"type": "agentMessage", "text": "Ready."}
                ),
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={"total": {"totalTokens": 11}},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        observation = self.driver(max_tokens=10).message("one", "Ready?")
        self.assertEqual(observation.reply, "Ready.")
        self.assertEqual(observation.tokens, 11)
        self.assertTrue(observation.completed)

    def test_interrupted_turn_retains_completed_actions(self) -> None:
        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "cat source.py",
                        "exitCode": 0,
                        "aggregatedOutput": "value = 1",
                    },
                ),
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={"total": {"totalTokens": 11}},
                ),
            ]
        )
        with self.assertRaises(LimitReached) as raised:
            self.driver(max_tokens=10).message("one", "Inspect.")
        observation = raised.exception.observation
        self.assertIsNotNone(observation)
        assert observation is not None
        self.assertFalse(observation.completed)
        self.assertEqual(observation.command_results[0].output, "value = 1")

    def test_read_only_judge_can_read_evidence(self) -> None:
        from evals.codex import CodexDriver

        self.stream(
            [
                event(
                    "item/completed",
                    item={
                        "type": "commandExecution",
                        "command": "cat evidence.txt",
                        "exitCode": 0,
                        "aggregatedOutput": "complete evidence",
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        driver = CodexDriver(self.workspace, "judge", 10, 100, read_only=True)
        self.addCleanup(driver.close)
        observation = driver.message("one", "Assess.")
        self.assertEqual(observation.command_results[0].output, "complete evidence")
        self.assertGreaterEqual(driver.metrics["message_seconds"], 0)

    def test_transport_timeout_retains_partial_actions(self) -> None:
        from evals.runner import TimeLimitReached

        def interrupted_stream() -> Iterator[SimpleNamespace]:
            yield event(
                "item/completed",
                item={
                    "type": "commandExecution",
                    "command": "cat source.py",
                    "exitCode": 0,
                    "aggregatedOutput": "source text",
                },
            )
            raise TimeoutError("Runtime stream stopped.")

        driver = self.driver()
        with patch("evals.codex.Thread") as thread:
            thread.return_value.turn.return_value.stream.side_effect = (
                interrupted_stream
            )
            with self.assertRaises(TimeLimitReached) as raised:
                driver.message("one", "Inspect.")
        observation = raised.exception.observation
        self.assertIsNotNone(observation)
        assert observation is not None
        self.assertFalse(observation.completed)
        self.assertEqual(observation.command_results[0].output, "source text")
        self.assertGreaterEqual(driver.metrics["message_seconds"], 0)

    def test_disabled_token_guard_still_records_usage_and_context_window(self) -> None:
        driver = self.driver(max_tokens=0)
        self.stream(
            [
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={
                        "total": {
                            "totalTokens": 111,
                            "inputTokens": 100,
                            "outputTokens": 11,
                            "reasoningOutputTokens": 7,
                            "cachedInputTokens": 40,
                            "cacheWriteInputTokens": 3,
                        },
                        "last": {
                            "totalTokens": 21,
                            "inputTokens": 10,
                            "outputTokens": 11,
                        },
                        "modelContextWindow": 1000,
                    },
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        observation = driver.message("one", "Inspect.")
        self.assertEqual(observation.tokens, 111)
        self.assertEqual(driver.metrics["usage_total_input_tokens"], 100)
        self.assertEqual(driver.metrics["usage_total_reasoning_output_tokens"], 7)
        self.assertEqual(driver.metrics["usage_total_cached_input_tokens"], 40)
        self.assertEqual(driver.metrics["usage_total_cache_write_input_tokens"], 3)
        self.assertEqual(driver.metrics["usage_last_input_tokens"], 10)
        self.assertEqual(driver.metrics["model_context_window"], 1000)

    def test_total_usage_sums_latest_totals_without_double_counting_updates(
        self,
    ) -> None:
        driver = self.driver(max_tokens=0)
        for thread_name, total, inputs in [
            ("one", 10, 8),
            ("two", 20, 15),
            ("one", 14, 11),
        ]:
            self.stream(
                [
                    event(
                        "thread/tokenUsage/updated",
                        threadId=thread_name,
                        tokenUsage={
                            "total": {"totalTokens": total, "inputTokens": inputs}
                        },
                    ),
                    event("turn/completed", turn={"status": "completed"}),
                ]
            )
            driver.message(thread_name, "Inspect.")
        self.assertEqual(driver.metrics["usage_total_tokens"], 34)
        self.assertEqual(driver.metrics["usage_total_input_tokens"], 26)

    def test_startup_timeout_retains_phase_time(self) -> None:
        from evals.codex import CodexDriver
        from evals.runner import TimeLimitReached

        with (
            patch.object(
                self.client, "initialize", side_effect=TimeoutError("startup")
            ),
            self.assertRaises(TimeLimitReached) as raised,
        ):
            CodexDriver(self.workspace, "model", 10, 100)
        self.assertGreaterEqual(raised.exception.metrics["startup_seconds"], 0)
        self.assertTrue(self.client.closed)

    def test_token_allowance_stops_native_event_consumption(self) -> None:
        self.stream(
            [
                event(
                    "thread/tokenUsage/updated",
                    threadId="one",
                    tokenUsage={"total": {"totalTokens": 11}},
                ),
                event("turn/completed", turn={"status": "completed"}),
            ]
        )
        with self.assertRaises(LimitReached):
            self.driver(max_tokens=10).message("one", "Ready?")

    def test_deadline_closes_the_runtime_and_is_reported_as_a_limit(self) -> None:
        driver = self.driver()
        self.stream([event("turn/completed", turn={"status": "completed"})])
        driver._expire()
        self.assertTrue(self.client.closed)
        with self.assertRaises(TimeoutError):
            driver.message("one", "Ready?")

    def test_pinned_sdk_compaction_notification_is_captured_before_turn_routing(
        self,
    ) -> None:
        from openai_codex.client import CodexConfig

        client = self.real_client_type(CodexConfig())
        self.addCleanup(client.close)
        client.watch("one")
        notification = client._coerce_notification(
            "item/completed",
            {
                "completedAtMs": 1,
                "threadId": "one",
                "turnId": "internal-turn",
                "item": {"type": "contextCompaction", "id": "context-one"},
            },
        )
        self.assertEqual(client.compaction_events.get(timeout=1), notification)


if __name__ == "__main__":
    unittest.main()
