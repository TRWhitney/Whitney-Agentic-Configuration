"""Temporary artifact and action observations for complete-task assessment."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from pydantic import JsonValue, TypeAdapter

from evals.fixtures import Workspace, git
from evals.recording import Recording

if TYPE_CHECKING:
    from evals.runner import Observation


@dataclass
class EvidenceFrame:
    step: int
    conversation: str
    prompt: str
    reply: str
    files: dict[str, str]
    commands: list[dict[str, object]]
    progress: dict[str, object] | None
    git: dict[str, object]
    event: Literal["message", "compaction", "fixture_edit"] = "message"
    service_state: dict[str, JsonValue] | None = None
    browser: list[dict[str, JsonValue]] = field(default_factory=list)
    completed: bool = True
    partial_reply: str = ""
    commentary: list[str] = field(default_factory=list)
    recording: Recording = field(default_factory=Recording)


@dataclass
class EvidenceRun:
    case: str
    model: str
    condition: str
    initial_files: dict[str, str] = field(default_factory=dict)
    frames: list[EvidenceFrame] = field(default_factory=list)
    _threads: dict[str, str] = field(default_factory=dict, repr=False)
    initial_service_state: dict[str, JsonValue] | None = None
    _browser_records: int = field(default=0, repr=False)
    instructions: dict[str, str] = field(default_factory=dict)
    definition: dict[str, JsonValue] = field(default_factory=dict)
    framework: dict[str, str] = field(default_factory=dict)
    isolation_status: str = "unverified"
    checks: list[dict[str, JsonValue]] = field(default_factory=list)
    execution: dict[str, JsonValue] = field(default_factory=dict)

    def observe(
        self,
        workspace: Workspace,
        step: int,
        thread: str,
        prompt: str,
        observation: Observation,
    ) -> None:
        self._threads.setdefault(thread, f"conversation-{len(self._threads) + 1}")
        if workspace.candidate_role == "implementation-worker" and prompt:
            prompt = "Runtime role: spawned implementation subagent.\n\n" + prompt

        def clean(text: str) -> str:
            text = text.replace(str(workspace.temporary_root), "/evidence")
            text = text.replace(str(workspace.root), "/project").replace(
                str(workspace.home), "/home"
            )
            for identifier, label in self._threads.items():
                text = text.replace(identifier, label)
            return text

        def clean_value(value: JsonValue) -> JsonValue:
            if isinstance(value, str):
                return clean(value)
            if isinstance(value, list):
                return [clean_value(v) for v in value]
            if isinstance(value, dict):
                return {k: clean_value(v) for k, v in value.items()}
            return value

        if not self.frames:
            self.instructions = {
                path.relative_to(workspace.home).as_posix(): clean(path.read_text())
                for path in [
                    workspace.home / "AGENTS.md",
                    workspace.home / "hooks.json",
                    *sorted((workspace.home / "skills").rglob("*")),
                ]
                if path.is_file() and path.suffix in {".md", ".json", ".py"}
            }
            self.initial_files = {
                p: clean(b.decode("utf-8")) for p, b in workspace.baseline.items()
            }
            self.initial_files.update(
                {
                    "/evidence/" + p: clean(b.decode("utf-8"))
                    for p, b in workspace.temporary_baseline.items()
                }
            )
        files: dict[str, str] = {}
        observed_files = {
            **workspace.project_files(),
            **{"/evidence/" + p: b for p, b in workspace.temporary_files().items()},
        }
        binaries: list[dict[str, JsonValue]] = []
        for name, content in observed_files.items():
            if content.startswith(b"\x89PNG\r\n\x1a\n"):
                binaries.append(
                    {
                        "origin": "artifact",
                        "path": name,
                        "images": [
                            {
                                "name": name,
                                "data_url": "data:image/png;base64,"
                                + base64.b64encode(content).decode("ascii"),
                            }
                        ],
                    }
                )
                files[name] = "PNG image; sha256=" + hashlib.sha256(content).hexdigest()
                continue
            files[name] = clean(content.decode("utf-8"))
        commands: list[dict[str, object]] = []
        results = iter(observation.command_results)
        for action in observation.actions:
            if action.kind == "native":
                commands.append({"native_item": clean_value(json.loads(action.text))})
            elif action.kind == "hook":
                commands.append(
                    {
                        "hook": action.tool,
                        "status": action.status,
                        "context": clean(action.text),
                    }
                )
            elif action.kind == "image":
                commands.append({"image_view": clean(action.text)})
            elif action.kind == "file":
                changes = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                    clean_value(json.loads(action.text))
                )
                commands.append({"file_changes": changes, "status": action.status})
            elif action.kind == "agent":
                commands.append(
                    {
                        "agent_tool": action.tool,
                        "status": None
                        if action.status == "unavailable"
                        else action.status,
                        "assignment": clean(action.text) if action.text else None,
                        **(
                            {"agent_results": clean_value(action.agent_results)}
                            if action.agent_results is not None
                            else {}
                        ),
                        **(
                            {"agent_findings": clean_value(action.agent_findings)}
                            if action.agent_findings is not None
                            else {}
                        ),
                        "assignment_visibility": (
                            "unavailable"
                            if action.status == "unavailable"
                            else "observed"
                            if action.text
                            else "not_supplied"
                        ),
                    }
                )
            else:
                command = next(results, None)
                commands.append(
                    {
                        "command": clean(command.command if command else action.text),
                        "exit_code": action.exit_code,
                        "output": clean(command.output)
                        if command and command.output
                        else None,
                    }
                )
        for command in results:
            commands.append(
                {
                    "command": clean(command.command),
                    "exit_code": command.exit_code,
                    "output": clean(command.output)
                    if command.output is not None
                    else None,
                }
            )
        try:
            progress = workspace.progress(thread)
        except json.JSONDecodeError:
            progress = {"invalid_json": workspace.progress_path(thread).read_text()}
        if progress is not None:
            progress = {
                k: clean(v) if isinstance(v, str) else v for k, v in progress.items()
            }
        state: dict[str, object] = {
            "commit_count": int(git(workspace.root, "rev-list", "--count", "HEAD")),
            "initial_commit_present": workspace.initial_commit
            in git(workspace.root, "rev-list", "HEAD").splitlines(),
            "working_tree": git(
                workspace.root, "status", "--short", "--untracked-files=all"
            ),
        }
        if (workspace.root.parent / "origin.git").is_dir():
            state.update(
                {
                    "head": git(workspace.root, "rev-parse", "HEAD"),
                    "remote_head": git(
                        workspace.root, "rev-parse", "refs/remotes/origin/main"
                    ),
                    "history": git(workspace.root, "log", "--format=%H %P %s"),
                }
            )

        service = workspace.service_state()
        if not self.frames and workspace.initial_service_state is not None:
            self.initial_service_state = {
                k: clean_value(v) for k, v in workspace.initial_service_state.items()
            }
        clean_service = (
            {k: clean_value(v) for k, v in service.items()}
            if service is not None
            else None
        )
        from evals.gui import candidate_browser

        recording = Recording(
            observation.recording.actions,
            [clean(p) for p in observation.recording.problems],
            dict(observation.recording.channels),
        )
        browser_problems: list[str] = []
        records = candidate_browser(workspace, browser_problems)
        recording.problems.extend(clean(p) for p in browser_problems)
        recording.channels["browser"] = "partial" if browser_problems else "complete"
        recording.channels["artifacts"] = "complete"
        browser = records[self._browser_records :]
        self._browser_records = len(records)
        browser.extend(observation.browser_evidence)
        browser.extend(binaries)
        clean_browser = [
            TypeAdapter(dict[str, JsonValue]).validate_python(clean_value(v))
            for v in browser
        ]
        self.frames.append(
            EvidenceFrame(
                step,
                self._threads[thread],
                clean(prompt),
                clean(observation.reply),
                files,
                commands,
                progress,
                state,
                "fixture_edit"
                if observation.fixture_edit
                else "compaction"
                if observation.compacted
                else "message",
                clean_service,
                clean_browser,
                observation.completed,
                clean(observation.partial_reply),
                [clean(message) for message in observation.commentary],
                recording,
            )
        )
