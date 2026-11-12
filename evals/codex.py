"""Native Codex execution through the pinned official SDK."""

from __future__ import annotations

import base64
import json
import queue
import re
import subprocess
import sys
import threading
from pathlib import Path
from time import perf_counter
from typing import cast

from openai_codex import LocalImageInput, TextInput
from openai_codex._inputs import InputItem
from openai_codex.api import Thread
from openai_codex.client import CodexClient, CodexConfig
from openai_codex.generated.v2_all import (
    ActivePermissionProfile,
    HooksListResponse,
    ThreadStartResponse,
)
from openai_codex.models import JsonObject, Notification
from pydantic import BaseModel, Field, JsonValue, TypeAdapter

from evals.fixtures import Workspace
from evals.isolation import RuntimeIsolation
from evals.recording import Recording
from evals.runner import (
    CommandResult,
    ExecutionFailed,
    LimitReached,
    Observation,
    ObservedAction,
    TimeLimitReached,
)


class ProfiledThreadStartResponse(ThreadStartResponse):
    active_permission_profile: ActivePermissionProfile | None = Field(
        default=None, alias="activePermissionProfile"
    )


def mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Expected a structured Codex event.")
    return cast(dict[str, object], value)


def event_data(payload: object) -> dict[str, object]:
    if not isinstance(payload, BaseModel):
        raise ValueError("Unrecognized Codex event payload.")
    return mapping(payload.model_dump(mode="json", by_alias=True))


class ObservableClient(CodexClient):
    """Observe compaction events before SDK turn routing consumes them.

    This protected SDK hook is covered against the pinned runtime in adapter tests.
    """

    def __init__(self, config: CodexConfig) -> None:
        self.watched_thread: str | None = None
        self.compaction_events: queue.Queue[Notification | None] = queue.Queue()
        self.hook_events: dict[str, queue.Queue[dict[str, object]]] = {}
        super().__init__(config)

    def watch(self, thread: str) -> None:
        while not self.compaction_events.empty():
            self.compaction_events.get_nowait()
        self.watched_thread = thread

    def _coerce_notification(self, method: str, params: object) -> Notification:
        event = super()._coerce_notification(method, params)
        if method == "hook/completed":
            data = event_data(event.payload)
            identifier = str(data["threadId"])
            self.hook_events.setdefault(identifier, queue.Queue()).put(
                mapping(data["run"])
            )
        if (
            self.watched_thread is not None
            and getattr(event.payload, "thread_id", None) == self.watched_thread
            and method
            in {
                "thread/tokenUsage/updated",
                "item/completed",
                "error",
                "turn/completed",
            }
        ):
            self.compaction_events.put(event)
        return event

    def hook_runs(self, thread: str) -> list[dict[str, object]]:
        events = self.hook_events.setdefault(thread, queue.Queue())
        runs = []
        while not events.empty():
            runs.append(events.get_nowait())
        return runs

    def next_compaction_notification(self) -> Notification:
        event = self.compaction_events.get()
        if event is None:
            raise ValueError("Codex closed before compaction completed.")
        return event

    def close(self) -> None:
        self.compaction_events.put(None)
        super().close()


class CodexDriver:
    def __init__(
        self,
        workspace: Workspace,
        model: str,
        timeout: float,
        max_tokens: int,
        *,
        read_only: bool = False,
        instructions: str | None = None,
        output_schema: JsonObject | None = None,
        image_paths: list[str] | None = None,
    ) -> None:
        started = perf_counter()
        self.metrics: dict[str, float | int] = {
            "startup_seconds": 0.0,
            "thread_start_seconds": 0.0,
            "message_seconds": 0.0,
            "compaction_seconds": 0.0,
        }
        self.usage_by_thread: dict[str, dict[str, int]] = {}
        hook_script = workspace.home / "skills/work-system/scripts/compaction.py"
        hook_command: str | None = None
        if not read_only and hook_script.is_file():
            subprocess.run(
                [
                    sys.executable,
                    str(hook_script),
                    "configure",
                    "--application",
                    "codex",
                    "--config-home",
                    str(workspace.home),
                ],
                cwd=workspace.root,
                env=workspace.environment(),
                check=True,
                capture_output=True,
                text=True,
                timeout=20,
            )
            configured = mapping(
                json.loads((workspace.home / "hooks.json").read_text())
            )
            groups = mapping(configured["hooks"])["SessionStart"]
            assert isinstance(groups, list)
            handlers = mapping(groups[0])["hooks"]
            assert isinstance(handlers, list)
            hook_command = str(mapping(handlers[0])["command"])
        workspace.copy_credentials()
        self.subject_hooks = hook_command is not None
        self.workspace, self.model = workspace, model
        self.max_tokens = max_tokens
        self.read_only, self.instructions = read_only, instructions
        if instructions is None and workspace.candidate_role == "implementation-worker":
            self.instructions = (
                "You are a spawned implementation subagent. "
                "The message is your parent's assignment."
            )
        self.output_schema = output_schema
        self.image_paths = image_paths or []
        self.tokens: dict[str, int] = {}
        self.expired = threading.Event()
        environment = workspace.environment()
        config = CodexConfig(
            cwd=str(workspace.root),
            env=environment,
            experimental_api=False,
            config_overrides=(
                'web_search="disabled"',
                "features.apps=false",
                "mcp_servers={}",
                "shell_environment_policy.set.PATH=" + json.dumps(environment["PATH"]),
            ),
        )
        self.isolation = RuntimeIsolation(
            workspace.home.parent,
            workspace=workspace.root,
            home=workspace.home,
            read_only=read_only,
        )
        environment["TMPDIR"] = str(self.isolation.scratch)
        config.config_overrides = (*config.config_overrides, *self.isolation.overrides)
        if read_only:
            config.config_overrides = (*config.config_overrides, "features.hooks=false")
        self.isolation.verify(environment)
        self.client = ObservableClient(config)
        self.isolation_verified = False
        self.timer = threading.Timer(timeout, self._expire)
        self.timer.daemon = True
        self.timer.start()
        try:
            self.client.start()
            self.client.initialize()
            if hook_command is not None:
                inventory = event_data(
                    self.client.request(
                        "hooks/list",
                        {"cwds": [str(workspace.root)]},
                        response_model=HooksListResponse,
                    )
                )
                entries = inventory.get("data")
                if not isinstance(entries, list):
                    raise ValueError("Missing native hook inventory.")
                hooks: list[dict[str, object]] = []
                for entry in entries:
                    group = mapping(entry)
                    if group.get("errors"):
                        raise ValueError("Native hook configuration has errors.")
                    values = group.get("hooks")
                    if not isinstance(values, list):
                        raise ValueError("Missing native hooks.")
                    hooks.extend(mapping(value) for value in values)
                if len(hooks) != 1 or (
                    hooks[0].get("command") != hook_command
                    or hooks[0].get("sourcePath") != str(workspace.home / "hooks.json")
                    or hooks[0].get("eventName") != "sessionStart"
                    or hooks[0].get("matcher") != "^compact$"
                    or hooks[0].get("enabled") is not True
                ):
                    raise ValueError(
                        "Native hooks differ from the isolated subject hook."
                    )
        except Exception as error:
            self.close()
            if self.expired.is_set() or isinstance(error, TimeoutError):
                raise TimeLimitReached(
                    "Time allowance exhausted during runtime startup.",
                    metrics=self.metrics,
                ) from error
            raise
        finally:
            self.metrics["startup_seconds"] = perf_counter() - started

    def _expire(self) -> None:
        self.expired.set()
        self.client.close()

    def close(self) -> None:
        self.timer.cancel()
        self.client.close()

    def start(self) -> str:
        started = perf_counter()
        try:
            self.isolation_verified = False
            response = self.client.request(
                "thread/start",
                {
                    "cwd": str(self.workspace.root),
                    "model": self.model,
                    "developerInstructions": self.instructions,
                    "approvalPolicy": "never",
                    "ephemeral": self.read_only,
                    **(
                        {"config": {"bypass_hook_trust": True}}
                        if self.subject_hooks
                        else {}
                    ),
                },
                response_model=ProfiledThreadStartResponse,
            )
            if (
                response.active_permission_profile is None
                or response.active_permission_profile.id != "eval"
            ):
                raise ValueError(
                    "Runtime did not confirm the evaluation permission profile."
                )
            self.isolation_verified = True
            return response.thread.id
        except Exception as error:
            if self.expired.is_set() or isinstance(error, TimeoutError):
                raise TimeLimitReached(
                    "Time allowance exhausted during conversation startup.",
                    sum(self.tokens.values()) or None,
                    metrics=self.metrics,
                ) from error
            raise
        finally:
            self.metrics["thread_start_seconds"] += perf_counter() - started

    def _usage(
        self, data: dict[str, object], thread: str, *, enforce: bool = True
    ) -> None:
        token_usage = mapping(data["tokenUsage"])
        usage = mapping(token_usage["total"])
        total = usage["totalTokens"]
        if type(total) is not int or total < 0:
            raise ValueError("Invalid token usage from Codex.")
        self.tokens[thread] = total
        fields = {
            "totalTokens": "tokens",
            "inputTokens": "input_tokens",
            "outputTokens": "output_tokens",
            "reasoningOutputTokens": "reasoning_output_tokens",
            "cachedInputTokens": "cached_input_tokens",
            "cacheWriteInputTokens": "cache_write_input_tokens",
        }
        totals: dict[str, int] = {}
        for key, label in fields.items():
            value = usage.get(key)
            if value is not None:
                if type(value) is not int or value < 0:
                    raise ValueError("Invalid token usage from Codex.")
                totals[label] = value
        self.usage_by_thread[thread] = totals
        for label in fields.values():
            values = [u[label] for u in self.usage_by_thread.values() if label in u]
            if values:
                self.metrics["usage_total_" + label] = sum(values)
        last = token_usage.get("last")
        if last is not None:
            last_usage = mapping(last)
            for key, label in fields.items():
                value = last_usage.get(key)
                if value is not None:
                    if type(value) is not int or value < 0:
                        raise ValueError("Invalid token usage from Codex.")
                    self.metrics["usage_last_" + label] = value
        context_window = token_usage.get("modelContextWindow")
        if context_window is not None:
            if type(context_window) is not int or context_window < 0:
                raise ValueError("Invalid model context window from Codex.")
            self.metrics["model_context_window"] = context_window
        if (
            enforce
            and self.max_tokens > 0
            and sum(self.tokens.values()) > self.max_tokens
        ):
            raise LimitReached(
                "Observed token allowance exhausted.",
                sum(self.tokens.values()),
                metrics=self.metrics,
            )

    def _native_child_results(self, identifier: str) -> dict[str, JsonValue]:
        try:
            data = event_data(self.client.thread_read(identifier, include_turns=True))
            turns = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                mapping(data["thread"])["turns"]
            )
            for turn in turns:
                items = turn.get("items")
                if not isinstance(items, list) or any(
                    not isinstance(item, dict) for item in items
                ):
                    raise ValueError("Invalid native child turn items.")
                for item in items:
                    if isinstance(item, dict) and item.get("type") in {
                        "subAgentActivity",
                        "collabAgentToolCall",
                    }:
                        item.pop("model", None)
                        item.pop("reasoningEffort", None)
                turn["items"] = [
                    item
                    for item in items
                    if isinstance(item, dict) and item.get("type") != "reasoning"
                ]
            observed_turns: list[JsonValue] = list(turns)
            return {identifier: {"turns": observed_turns}}
        except Exception as error:
            return {identifier: {"unavailable": str(error)}}

    def _hook_actions(self, thread: str) -> list[ObservedAction]:
        return [
            ObservedAction(
                "hook",
                json.dumps(run),
                tool=str(run["eventName"]),
                status=str(run["status"]),
            )
            for run in self.client.hook_runs(thread)
        ]

    def message(self, thread: str, prompt: str) -> Observation:
        started = perf_counter()
        replies: list[str] = []
        commentary: list[str] = []
        pending: dict[str, list[str]] = {}
        commands: list[str] = []
        command_results: list[CommandResult] = []
        actions: list[ObservedAction] = []
        native_children: dict[str, ObservedAction] = {}
        collab_children: dict[str, list[ObservedAction]] = {}
        browser_evidence: list[dict[str, JsonValue]] = []
        reported = False
        turn_completed = False
        recording = Recording()

        def observation(*, completed: bool) -> Observation:
            actions.extend(self._hook_actions(thread))
            return Observation(
                "\n".join(replies),
                self.tokens.get(thread) if reported else None,
                tuple(commands),
                command_results=tuple(command_results),
                actions=tuple(actions),
                browser_evidence=browser_evidence,
                completed=completed,
                partial_reply="\n".join("".join(parts) for parts in pending.values()),
                commentary=list(commentary),
                recording=Recording(
                    "complete"
                    if completed and recording.actions != "partial"
                    else "partial",
                    list(recording.problems),
                    dict(recording.channels),
                ),
            )

        try:
            if self.max_tokens > 0 and sum(self.tokens.values()) > self.max_tokens:
                raise LimitReached(
                    "Observed token allowance exhausted.",
                    sum(self.tokens.values()),
                    metrics=self.metrics,
                )
            native_thread = Thread(self.client, thread)
            content: str | list[InputItem] = (
                [
                    TextInput(prompt),
                    *[LocalImageInput(path) for path in self.image_paths],
                ]
                if self.image_paths
                else prompt
            )
            handle = (
                native_thread.turn(content, output_schema=self.output_schema)
                if self.output_schema is not None
                else native_thread.turn(content)
            )
            for event in handle.stream():
                actions.extend(self._hook_actions(thread))
                if event.method not in {
                    "thread/tokenUsage/updated",
                    "item/completed",
                    "item/agentMessage/delta",
                    "turn/completed",
                }:
                    continue
                data = event_data(event.payload)
                if event.method == "item/agentMessage/delta":
                    if data.get("threadId") == thread:
                        identifier, delta = data.get("itemId"), data.get("delta")
                        if not isinstance(identifier, str) or not isinstance(
                            delta, str
                        ):
                            raise ValueError("Invalid message delta from Codex.")
                        pending.setdefault(identifier, []).append(delta)
                elif (
                    event.method == "thread/tokenUsage/updated"
                    and data.get("threadId") == thread
                ):
                    reported = True
                    self._usage(data, thread, enforce=not replies)
                elif event.method == "item/completed":
                    item = mapping(data["item"])
                    if item.get("type") not in {
                        "agentMessage",
                        "reasoning",
                        "userMessage",
                        "commandExecution",
                        "imageView",
                        "subAgentActivity",
                        "fileChange",
                        "collabAgentToolCall",
                        "mcpToolCall",
                        "plan",
                        "contextCompaction",
                        "hookPrompt",
                    }:
                        recording.actions = "partial"
                        recording.problems.append(
                            f"Unrecorded native item type: {item.get('type')}"
                        )
                    identifier = item.get("id")
                    if isinstance(identifier, str):
                        pending.pop(identifier, None)
                    if item.get("type") == "hookPrompt":
                        fragments = item.get("fragments")
                        if not isinstance(fragments, list):
                            raise ValueError("Missing hook context fragments.")
                        for fragment in fragments:
                            value = mapping(fragment)
                            actions.append(
                                ObservedAction(
                                    "hook",
                                    str(value["text"]),
                                    tool=str(value["hookRunId"]),
                                    status="delivered",
                                )
                            )
                    if self.read_only and item.get("type") not in {
                        "agentMessage",
                        "reasoning",
                        "userMessage",
                        "commandExecution",
                        "imageView",
                    }:
                        raise ValueError("Judge used a tool or changed its context.")
                    if item.get("type") == "subAgentActivity" and item.get("kind") in {
                        "started",
                        "completed",
                    }:
                        complete = item.get("kind") == "completed"
                        action = ObservedAction(
                            "agent",
                            "",
                            tool="agentCompleted" if complete else "spawnAgent",
                            status="completed" if complete else "unavailable",
                        )
                        actions.append(action)
                        identifier = item.get("agentThreadId")
                        if isinstance(identifier, str):
                            native_children[identifier] = action
                    if item.get("type") == "fileChange":
                        changes, status = item.get("changes"), item.get("status")
                        if (
                            not isinstance(changes, list)
                            or any(not isinstance(change, dict) for change in changes)
                            or not isinstance(status, str)
                        ):
                            raise ValueError("Invalid native file-change event.")
                        actions.append(
                            ObservedAction(
                                "file",
                                json.dumps(changes, ensure_ascii=False),
                                tool="fileChange",
                                status=status,
                            )
                        )
                    if item.get("type") == "collabAgentToolCall":
                        agent_prompt = item.get("prompt")
                        tool, status = item.get("tool"), item.get("status")
                        if (
                            not isinstance(tool, str)
                            or not isinstance(status, str)
                            or (
                                agent_prompt is not None
                                and not isinstance(agent_prompt, str)
                            )
                        ):
                            raise ValueError("Invalid agent call from Codex.")
                        actions.append(
                            ObservedAction(
                                "agent",
                                agent_prompt or "",
                                tool=tool,
                                status=status,
                                agent_results=TypeAdapter(
                                    dict[str, JsonValue]
                                ).validate_python(item["agentsStates"])
                                if item.get("agentsStates") is not None
                                else None,
                            )
                        )
                        identifiers = item.get("receiverThreadIds")
                        if not isinstance(identifiers, list):
                            states = item.get("agentsStates")
                            identifiers = (
                                list(states) if isinstance(states, dict) else []
                            )
                        if not identifiers and tool != "wait":
                            recording.channels["children"] = "partial"
                            recording.problems.append(
                                "Native child identifiers unavailable."
                            )
                        for child in identifiers:
                            if isinstance(child, str):
                                collab_children.setdefault(child, []).append(
                                    actions[-1]
                                )
                    if item.get("type") == "imageView":
                        path = item.get("path")
                        if not isinstance(path, str):
                            raise ValueError("Invalid native image-view path.")
                        actions.append(ObservedAction("image", path, tool="imageView"))
                        image_path = Path(path)
                        if not image_path.is_absolute():
                            image_path = self.workspace.root / image_path
                        images: list[JsonValue] = []
                        if image_path.is_file():
                            raw = image_path.read_bytes()
                            if raw.startswith(b"\x89PNG\r\n\x1a\n"):
                                images.append(
                                    {
                                        "name": path,
                                        "data_url": "data:image/png;base64,"
                                        + base64.b64encode(raw).decode("ascii"),
                                    }
                                )
                        if not images:
                            recording.channels["images"] = "partial"
                            recording.problems.append(
                                f"Viewed image bytes unavailable: {path}"
                            )
                        browser_evidence.append(
                            {
                                "origin": "candidate_image_view",
                                "path": path,
                                "images": images,
                            }
                        )
                    if item.get("type") == "mcpToolCall":
                        raise ValueError(
                            "External service tool used in isolated evaluation: "
                            f"{item.get('server')}/{item.get('tool')}"
                        )
                    if item.get("type") == "agentMessage" and isinstance(
                        item.get("text"), str
                    ):
                        target = (
                            commentary if item.get("phase") == "commentary" else replies
                        )
                        target.append(str(item["text"]))
                    if item.get("type") == "commandExecution":
                        command = str(item.get("command", ""))
                        commands.append(command)
                        exit_code = item.get("exitCode")
                        output = item.get("aggregatedOutput")
                        if exit_code is not None and type(exit_code) is not int:
                            raise ValueError("Invalid command exit code from Codex.")
                        if output is not None and not isinstance(output, str):
                            raise ValueError("Invalid command output from Codex.")
                        if exit_code is None:
                            recording.channels["commands"] = "partial"
                            recording.problems.append(
                                "Completed command has no exit code."
                            )
                        command_results.append(
                            CommandResult(command, exit_code, output)
                        )
                        actions.append(
                            ObservedAction(
                                "command", command + "\n" + (output or ""), exit_code
                            )
                        )
                        for identifier in re.findall(
                            r"^DELEGATION_FIXTURE_ID:([a-f0-9]{32})$",
                            output or "",
                            re.MULTILINE,
                        ):
                            path = self.workspace.home / "work-system/delegations.jsonl"
                            records = [
                                json.loads(line)
                                for line in path.read_text().splitlines()
                            ]
                            prompts = [
                                r["prompt"] for r in records if r["id"] == identifier
                            ]
                            if len(prompts) != 1 or not isinstance(prompts[0], str):
                                raise ValueError("Invalid delegation fixture record.")
                            actions.append(
                                ObservedAction(
                                    "agent",
                                    prompts[0],
                                    tool="delegateFixture",
                                    status="completed" if exit_code == 0 else "failed",
                                )
                            )
                elif event.method == "turn/completed":
                    turn = mapping(data["turn"])
                    if turn.get("status") != "completed":
                        error = turn.get("error")
                        reason = (
                            error.get("message") if isinstance(error, dict) else None
                        )
                        detail = f": {reason}" if reason else ""
                        raise ValueError(
                            f"Codex turn status: {turn.get('status')}{detail}"
                        )
                    turn_completed = True
            if self.expired.is_set():
                raise TimeLimitReached("Time allowance exhausted during message.")
            if not turn_completed:
                raise ValueError("Codex stream ended without a completed turn.")
            for identifier in native_children.keys() | collab_children.keys():
                findings = self._native_child_results(identifier)
                if identifier in native_children:
                    native_children[identifier].agent_results = findings
                for action in collab_children.get(identifier, []):
                    action.agent_findings = findings
                if any(
                    isinstance(v, dict) and "unavailable" in v
                    for v in findings.values()
                ):
                    recording.channels["children"] = "partial"
                    recording.problems.append("Native child findings unavailable.")
            if self.expired.is_set():
                raise TimeLimitReached(
                    "Time allowance exhausted collecting child work."
                )
            for channel in ("commands", "images", "children"):
                recording.channels.setdefault(channel, "complete")
            return observation(completed=True)
        except Exception as error:
            partial = observation(completed=False)
            if self.expired.is_set():
                raise TimeLimitReached(
                    "Time allowance exhausted during message.",
                    sum(self.tokens.values()) or None,
                    partial,
                    self.metrics,
                ) from None
            if isinstance(error, TimeoutError):
                raise TimeLimitReached(
                    str(error), sum(self.tokens.values()) or None, partial, self.metrics
                ) from error
            if isinstance(error, LimitReached):
                error.observation = partial
                error.metrics = self.metrics
                raise
            raise ExecutionFailed(
                f"{type(error).__name__}: {error}", partial
            ) from error
        finally:
            self.metrics["message_seconds"] += perf_counter() - started

    def compact(self, thread: str) -> Observation:
        started = perf_counter()
        try:
            self.client.watch(thread)
            self.client.thread_compact(thread)
            compacted_turn: str | None = None
            completed_turns: set[str] = set()
            while True:
                event = self.client.next_compaction_notification()
                if event.method not in {
                    "thread/tokenUsage/updated",
                    "item/completed",
                    "error",
                    "turn/completed",
                }:
                    continue
                data = event_data(event.payload)
                if data.get("threadId") != thread:
                    continue
                if event.method == "thread/tokenUsage/updated":
                    self._usage(data, thread)
                if (
                    event.method == "item/completed"
                    and mapping(data["item"]).get("type") == "contextCompaction"
                ):
                    compacted_turn = str(data["turnId"])
                if event.method == "error":
                    if data.get("willRetry"):
                        continue
                    raise ValueError("Codex compaction failed.")
                if event.method == "turn/completed":
                    turn = mapping(data["turn"])
                    if turn.get("status") != "completed":
                        raise ValueError("Codex compaction did not complete.")
                    if compacted_turn is None:
                        raise ValueError("No completed compaction item was reported.")
                    completed_turns.add(str(turn["id"]))
                if compacted_turn in completed_turns:
                    return Observation(
                        tokens=self.tokens.get(thread),
                        compacted=True,
                        actions=tuple(self._hook_actions(thread)),
                    )
        except Exception as error:
            partial = Observation(tokens=self.tokens.get(thread), completed=False)
            if self.expired.is_set():
                raise TimeLimitReached(
                    "Time allowance exhausted during compaction.",
                    sum(self.tokens.values()) or None,
                    partial,
                    self.metrics,
                ) from None
            if isinstance(error, TimeoutError):
                raise TimeLimitReached(
                    str(error), sum(self.tokens.values()) or None, partial, self.metrics
                ) from error
            if isinstance(error, LimitReached):
                error.observation = partial
                error.metrics = self.metrics
            raise
        finally:
            self.metrics["compaction_seconds"] += perf_counter() - started
            self.client.watched_thread = None
