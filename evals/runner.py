"""Execute case steps and apply the same checks to every instruction variant."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Protocol

from pydantic import JsonValue

from evals.assessment_models import AssessmentResult, Outcome
from evals.fixtures import Workspace, git, make_workspace
from evals.models import (
    ActionSequenceCheck,
    AgentAssignmentsCheck,
    BrowserCheck,
    CaseSpec,
    CommandRegexCheck,
    CommandSequenceCheck,
    CommitCountCheck,
    CommitGroupsCheck,
    CompactStep,
    CompletedCheck,
    EditStep,
    FileEqualsCheck,
    FileRegexCheck,
    GitHubStateCheck,
    MessageStep,
    NavigationTextCheck,
    NoPublishCheck,
    NoRawEvidenceCheck,
    OnlyChangedCheck,
    ProgressCheck,
    ProseCheck,
    PythonCheck,
    RegressionTestCheck,
    ReplyRegexCheck,
    SeedStep,
    SessionCommitsCheck,
    TemporaryFilesCheck,
    TrackerCheck,
    UnchangedCheck,
)
from evals.recording import Recording
from evals.retention import no_raw_evidence, temporary_check


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int | None
    output: str | None


@dataclass
class ObservedAction:
    kind: Literal["command", "agent", "image", "file", "hook"]
    text: str
    exit_code: int | None = None
    tool: str | None = None
    status: str | None = None
    agent_results: dict[str, JsonValue] | None = None
    agent_findings: dict[str, JsonValue] | None = None


@dataclass
class Observation:
    reply: str = ""
    tokens: int | None = None
    commands: tuple[str, ...] = ()
    compacted: bool = False
    command_results: tuple[CommandResult, ...] = ()
    actions: tuple[ObservedAction, ...] = ()
    fixture_edit: bool = False
    browser_evidence: list[dict[str, JsonValue]] = field(default_factory=list)
    completed: bool = True
    partial_reply: str = ""
    commentary: list[str] = field(default_factory=list)
    recording: Recording = field(default_factory=Recording)


class Driver(Protocol):
    def start(self) -> str: ...
    def message(self, thread: str, prompt: str) -> Observation: ...
    def compact(self, thread: str) -> Observation: ...
    def close(self) -> None: ...


class ExecutionFailed(ValueError):
    def __init__(self, message: str, observation: Observation) -> None:
        super().__init__(message)
        self.observation = observation


class LimitReached(RuntimeError):
    def __init__(
        self,
        message: str,
        tokens: int | None = None,
        observation: Observation | None = None,
        metrics: dict[str, float | int] | None = None,
    ) -> None:
        super().__init__(message)
        self.tokens = tokens
        self.observation = observation
        self.metrics = metrics if metrics is not None else {}


class TimeLimitReached(TimeoutError):
    def __init__(
        self,
        message: str,
        tokens: int | None = None,
        observation: Observation | None = None,
        metrics: dict[str, float | int] | None = None,
    ) -> None:
        super().__init__(message)
        self.tokens = tokens
        self.observation = observation
        self.metrics = metrics if metrics is not None else {}


@dataclass
class CheckResult:
    step: int
    conversation: str
    kind: str
    passed: bool
    detail: str


@dataclass
class CaseResult:
    case: str
    model: str
    status: Outcome = "error"
    checks: list[CheckResult] = field(default_factory=list)
    tokens: int | None = None
    source_digest: str = ""
    source_revision: str | None = None
    detail: str = ""
    purpose: str = "focused"
    isolation_status: str = "unverified"
    assessment: AssessmentResult | None = None
    mechanical_status: Outcome | None = None
    metrics: dict[str, float | int] = field(default_factory=dict)

    @property
    def behavior(self) -> Literal["correct", "incorrect", "unknown"]:
        if any(not check.passed for check in self.checks) or (
            self.assessment is not None and self.assessment.status == "fail"
        ):
            return "incorrect"
        if self.status == "pass":
            return "correct"
        return "unknown"

    @property
    def assessment_execution(self) -> Literal["complete", "failed", "not_requested"]:
        if self.assessment is None:
            return "not_requested"
        return "failed" if self.assessment.status in {"error", "limit"} else "complete"


DriverFactory = Callable[[Workspace, str, float, int], Driver]


def _positionals(values: list[str]) -> list[str]:
    remaining = list(values)
    while remaining and remaining[0].startswith("-"):
        flag = remaining.pop(0)
        if flag in {"-R", "--repo", "--hostname"} and remaining:
            remaining.pop(0)
    return remaining


def publication_request(arguments: list[str]) -> bool:
    arguments = _positionals(arguments)
    if not arguments:
        return False
    if arguments[0] == "api":
        for index, argument in enumerate(arguments):
            if argument in {"-X", "--method"} and index + 1 < len(arguments):
                return arguments[index + 1].upper() not in {"GET", "HEAD"}
            if argument.startswith("--method="):
                return argument.partition("=")[2].upper() not in {"GET", "HEAD"}
            if argument.startswith("-X") and len(argument) > 2:
                return argument[2:].upper() not in {"GET", "HEAD"}
        return any(
            argument in {"-f", "-F", "--field", "--raw-field", "--input"}
            or argument.startswith(("-f", "-F", "--field=", "--raw-field=", "--input="))
            for argument in arguments[1:]
        )
    mutations = {
        "pr": {
            "close",
            "comment",
            "create",
            "edit",
            "lock",
            "merge",
            "ready",
            "reopen",
            "review",
            "unlock",
        },
        "issue": {
            "close",
            "comment",
            "create",
            "delete",
            "edit",
            "lock",
            "pin",
            "reopen",
            "transfer",
            "unlock",
            "unpin",
        },
    }
    action = _positionals(arguments[1:])
    return bool(action and action[0] in mutations.get(arguments[0], set()))


def pull_request_target(arguments: list[str]) -> bool:
    parts = _positionals(arguments)
    return bool(
        parts
        and (
            parts[0] == "pr"
            or (
                parts[0] == "api"
                and any(
                    re.fullmatch(r"/?repos/[^/]+/[^/]+/pulls(?:/.*)?", arg)
                    for arg in parts[1:]
                )
            )
        )
    )


def check_result(
    check: BrowserCheck
    | ActionSequenceCheck
    | AgentAssignmentsCheck
    | UnchangedCheck
    | OnlyChangedCheck
    | FileEqualsCheck
    | FileRegexCheck
    | ReplyRegexCheck
    | CommandRegexCheck
    | CommandSequenceCheck
    | PythonCheck
    | TemporaryFilesCheck
    | NoRawEvidenceCheck
    | RegressionTestCheck
    | CompletedCheck
    | SessionCommitsCheck
    | ProgressCheck
    | ProseCheck
    | CommitCountCheck
    | CommitGroupsCheck
    | NoPublishCheck
    | NavigationTextCheck
    | GitHubStateCheck
    | TrackerCheck,
    observation: Observation,
    workspace: Workspace,
    thread: str,
    commands: list[str],
) -> tuple[bool, str]:
    if isinstance(check, TemporaryFilesCheck):
        return temporary_check(check, workspace)
    if isinstance(check, NoRawEvidenceCheck):
        return no_raw_evidence(check, workspace)
    if isinstance(check, ProseCheck):
        contents: list[str] = []
        for name in check.paths:
            path = workspace.file(name)
            if not path.is_file():
                return False, f"Missing or empty reader content: {name}"
            content = path.read_text(encoding="utf-8")
            if not content.strip():
                return False, f"Missing or empty reader content: {name}"
            contents.append(content)
        text = "\n".join(contents)
        if any(not re.search(p, text, re.MULTILINE) for p in check.required_patterns):
            return False, "Required subject content is missing."
        if any(re.search(p, text, re.MULTILINE) for p in check.forbidden_patterns):
            return False, "Prohibited prose pattern is present."
        return (
            True,
            "Required subject content is present; prohibited patterns are absent.",
        )
    if isinstance(check, AgentAssignmentsCheck):
        assignments = [
            a
            for a in observation.actions
            if a.kind == "agent" and a.tool in check.tools
        ]
        count_ok = len(assignments) >= check.min_count and (
            check.max_count is None or len(assignments) <= check.max_count
        )
        if count_ok and any(a.status == "unavailable" for a in assignments):
            raise ValueError("Runtime did not expose native assignment text.")
        content_ok = all(
            a.status == "completed"
            and all(re.search(p, a.text) for p in check.required_patterns)
            and not any(re.search(p, a.text) for p in check.forbidden_patterns)
            for a in assignments
        )
        return count_ok and content_ok, f"Assignments checked: {len(assignments)}."
    if isinstance(check, ActionSequenceCheck):
        remaining_actions = iter(observation.actions)
        for expected_action in check.actions:
            if not any(
                a.kind == expected_action.kind
                and re.search(expected_action.pattern, a.text)
                and (
                    expected_action.exit_code is None
                    or a.exit_code == expected_action.exit_code
                )
                and (expected_action.tool is None or a.tool == expected_action.tool)
                and (a.kind != "agent" or a.status == "completed")
                for a in remaining_actions
            ):
                if expected_action.kind == "agent" and any(
                    a.kind == "agent"
                    and a.status == "unavailable"
                    and (expected_action.tool is None or a.tool == expected_action.tool)
                    for a in observation.actions
                ):
                    raise ValueError("Runtime did not expose native assignment text.")
                return False, "Required current-step action missing or out of order."
        return True, "Current-step actions match in order."
    if isinstance(check, NavigationTextCheck):
        path = workspace.progress_path(thread)
        return (
            path.is_file() and path.read_text() == check.text,
            "Saved navigation text.",
        )
    if isinstance(check, GitHubStateCheck):
        import json

        state = json.loads((workspace.home / "work-system/github.json").read_text())
        resources = list(state[check.resource].values())
        count_ok = check.count is None or len(resources) == check.count
        if check.number is not None:
            resources = [r for r in resources if r["number"] == check.number]
        body_ok = check.body_pattern is None or any(
            re.search(check.body_pattern, r["body"]) for r in resources
        )
        return count_ok and body_ok, "Saved GitHub fixture state."
    if isinstance(check, SessionCommitsCheck):
        listed = workspace.navigate(thread, ["commit", "list"]).splitlines()[1:]
        actual_commits = {value for value in listed if value != "None."}
        expected_commits = set(git(workspace.root, "rev-list", "HEAD").splitlines())
        if not check.include_initial:
            expected_commits.discard(workspace.initial_commit)
        return actual_commits == expected_commits, (
            f"Expected recorded commits: {sorted(expected_commits)}; "
            f"actual: {sorted(actual_commits)}"
        )
    if isinstance(check, CompletedCheck):
        progress = workspace.progress(thread)
        completed = progress is None or set(progress) == {"commits"}
        return completed, "No active workflow remains."
    if isinstance(check, CommitGroupsCheck):
        history = git(workspace.root, "rev-list", "--reverse", "HEAD").splitlines()
        if not history or history[0] != workspace.initial_commit:
            return False, "The initial commit was rewritten."
        commits = history[1:]
        groups = [
            frozenset(
                git(
                    workspace.root,
                    "diff-tree",
                    "--no-commit-id",
                    "--name-only",
                    "-r",
                    commit,
                ).splitlines()
            )
            for commit in commits
        ]
        expected_groups = [frozenset(paths) for paths in check.groups]
        dirty = set(git(workspace.root, "diff", "HEAD", "--name-only").splitlines())
        dirty.update(
            git(
                workspace.root, "ls-files", "--others", "--exclude-standard"
            ).splitlines()
        )
        return (
            sorted(groups, key=sorted) == sorted(expected_groups, key=sorted)
            and dirty == set(check.uncommitted),
            f"Commit path groups: {[sorted(group) for group in groups]}; "
            f"uncommitted: {sorted(dirty)}",
        )
    if isinstance(check, RegressionTestCheck):
        with tempfile.TemporaryDirectory(prefix="regression-") as temporary:
            root = Path(temporary)
            for name, file_bytes in workspace.project_files().items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(file_bytes)
            for initial in (False, True):
                if initial:
                    faulty = (
                        check.faulty_text.encode("utf-8")
                        if check.faulty_text is not None
                        else workspace.baseline[check.source]
                    )
                    (root / check.source).write_bytes(faulty)
                try:
                    result = subprocess.run(
                        [
                            sys.executable,
                            "-E",
                            "-s",
                            "-B",
                            "-m",
                            "unittest",
                            "discover",
                            "-s",
                            check.tests,
                            "-v",
                        ],
                        cwd=root,
                        env=workspace.environment(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        timeout=10,
                    )
                except subprocess.TimeoutExpired:
                    return False, "Regression test timed out."
                output = result.stdout.decode("utf-8", errors="replace")
                ran = re.search(r"Ran [1-9][0-9]* tests?", output) is not None
                passed = (
                    (
                        result.returncode == 1
                        and "FAIL:" in output
                        and "ERROR:" not in output
                    )
                    if initial
                    else result.returncode == 0
                )
                if not ran or not passed:
                    version = "faulty" if initial else "current"
                    return (
                        False,
                        f"Regression against {version} failed.\n" + output[-1000:],
                    )
        return (
            True,
            "Authored tests pass current code and fail faulty code by assertion.",
        )
    if isinstance(check, UnchangedCheck):
        changed: set[str] = set()

        def included(name: str) -> bool:
            return not any(
                name == path or name.startswith(path + "/") for path in check.exclude
            )

        for prefix in check.paths:
            expected_files = {
                name: content
                for name, content in workspace.baseline.items()
                if (name == prefix or name.startswith(prefix + "/")) and included(name)
            }
            actual = {
                name
                for name in workspace.project_files()
                if (name == prefix or name.startswith(prefix + "/")) and included(name)
            }
            changed.update(actual.symmetric_difference(expected_files))
            changed.update(
                name
                for name in actual.intersection(expected_files)
                if workspace.file(name).read_bytes() != expected_files[name]
            )
        return (
            not changed,
            "Changed files: " + ", ".join(sorted(changed))
            if changed
            else "Files unchanged.",
        )
    if isinstance(check, OnlyChangedCheck):
        current = set(workspace.project_files())
        changed = current.symmetric_difference(workspace.baseline)
        changed.update(
            name
            for name in current.intersection(workspace.baseline)
            if not workspace.file(name).is_file()
            or workspace.file(name).read_bytes() != workspace.baseline[name]
        )
        unexpected = {
            name
            for name in changed
            if not any(name == p or name.startswith(p + "/") for p in check.paths)
        }
        return not unexpected, "Unexpected changes: " + ", ".join(sorted(unexpected))
    if isinstance(check, FileEqualsCheck):
        path = workspace.file(check.path)
        passed = path.is_file() and path.read_text(encoding="utf-8") == check.text
        return passed, f"Expected file content: {check.path}"
    if isinstance(check, ReplyRegexCheck):
        matched = re.search(check.pattern, observation.reply, re.MULTILINE) is not None
        return (
            matched != check.absent,
            "Reply pattern absent." if check.absent else "Reply pattern present.",
        )
    if isinstance(check, CommandRegexCheck):
        matched = (
            re.search(check.pattern, "\n".join(observation.commands), re.MULTILINE)
            is not None
        )
        return matched != check.absent, "Current-step command pattern."
    if isinstance(check, CommandSequenceCheck):
        remaining = iter(observation.command_results)
        for required in check.commands:
            if not any(
                re.search(required.pattern, result.command, re.MULTILINE)
                and (
                    required.exit_code is None or result.exit_code == required.exit_code
                )
                and (
                    required.output_pattern is None
                    or (
                        result.output is not None
                        and re.search(
                            required.output_pattern, result.output, re.MULTILINE
                        )
                    )
                )
                for result in remaining
            ):
                return (
                    False,
                    "Required current-step command result missing or out of order.",
                )
        return True, "Current-step command results match in order."
    if isinstance(check, PythonCheck):
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-B",
                    "-c",
                    "import sys; path = sys.argv[1]; "
                    "exec(compile(sys.stdin.buffer.read(), path, 'exec'), "
                    "{'__name__': '__main__', '__file__': path})",
                    str(workspace.file(check.path)),
                ],
                input=(
                    workspace.grader_files[check.path]
                    if check.path in workspace.grader_files
                    else workspace.baseline[check.path]
                ),
                cwd=workspace.root,
                env=workspace.environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            return False, f"Prepared Python check timed out: {check.path}"
        passed = result.returncode == 0
        detail = f"Prepared Python check: {check.path}; exit code: {result.returncode}"
        if not passed:
            detail += "\n" + result.stdout.decode("utf-8", errors="replace")[-1000:]
        return passed, detail
    if isinstance(check, BrowserCheck):
        browser_result = next(
            (
                r
                for r in observation.browser_evidence
                if r.get("scenario") == check.scenario
                and r.get("origin") == "private_grader"
            ),
            None,
        )
        if browser_result is None:
            return False, "Missing browser observation."
        return (
            not check.require_match or browser_result.get("matched") is True,
            "Browser contract: "
            + check.scenario
            + "; "
            + str(browser_result.get("measurements")),
        )
    if isinstance(check, FileRegexCheck):
        path = workspace.file(check.path)
        if not path.is_file():
            return False, f"Missing file: {check.path}"
        matched = (
            re.search(check.pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
            is not None
        )
        return matched != check.absent, f"File pattern: {check.path}"
    if isinstance(check, ProgressCheck):
        progress = workspace.progress(thread)
        expected: dict[str, str | None] = {
            "workflow": check.workflow,
            "state": check.state,
        }
        if not check.ignore_substate:
            expected["substate"] = check.substate
        if check.record is not None:
            expected["record"] = str(workspace.file(check.record))
        passed = progress is not None and all(
            progress.get(key) == value for key, value in expected.items()
        )
        return (
            passed,
            f"Saved state: {check.workflow}.{check.state}, substate: {check.substate}; "
            f"record: {progress.get('record') if progress else None}",
        )
    if isinstance(check, CommitCountCheck):
        count = int(git(workspace.root, "rev-list", "--count", "HEAD"))
        clean = not git(workspace.root, "diff", "HEAD", "--name-only")
        return (
            count == check.count and clean,
            f"Commits: {count}; tracked files clean: {clean}",
        )
    if isinstance(check, TrackerCheck):
        import json

        settings = json.loads((workspace.root / ".git/work-system.json").read_text())
        return settings.get(
            "tracker"
        ) == check.name, f"Tracker: {settings.get('tracker')}"
    calls = workspace.service_calls()
    for command in commands:
        try:
            arguments = shlex.split(command)
        except ValueError:
            continue
        if arguments and Path(arguments[0]).name in {"gh", "gh.exe", "gh.cmd"}:
            calls.append(arguments[1:])
    mutation = any(
        publication_request(call)
        and (check.target == "all" or pull_request_target(call))
        for call in calls
    )
    return (
        not mutation,
        "Publication request observed."
        if mutation
        else "No publication request observed.",
    )


def run_case(
    case: CaseSpec,
    source: Path,
    model: str,
    *,
    timeout: float = 600,
    max_tokens: int = 0,
    driver_factory: DriverFactory | None = None,
    on_observation: Callable[[Workspace, int, str, str, Observation], None]
    | None = None,
) -> CaseResult:
    if driver_factory is None:
        from evals.codex import CodexDriver

        driver_factory = CodexDriver
    result = CaseResult(case.id, model)
    result.purpose = case.purpose
    started = time.monotonic()
    if timeout <= 0 or max_tokens < 0:
        raise ValueError("Time must be positive; token guard must be nonnegative.")
    try:
        with make_workspace(source, case) as workspace:
            result.source_digest = workspace.source_digest
            result.source_revision = workspace.source_revision
            driver = driver_factory(workspace, model, timeout, max_tokens)
            result.isolation_status = (
                "verified"
                if getattr(driver, "isolation_verified", False)
                else "unverified"
            )
            try:
                threads: dict[str, str] = {}
                tokens: dict[str, int] = {}
                commands: list[str] = []
                for index, step in enumerate(case.steps):
                    if step.conversation not in threads:
                        threads[step.conversation] = driver.start()
                    thread = threads[step.conversation]
                    observation = Observation()
                    if isinstance(step, SeedStep):
                        workspace.seed(thread, step)
                    elif isinstance(step, EditStep):
                        observation.fixture_edit = True
                        if step.record_commit:
                            workspace.navigate(thread, ["commit", "add", "HEAD"])
                        if step.publish:
                            workspace.publish()
                        for relative, text in step.files.items():
                            path = workspace.file(relative)
                            path.parent.mkdir(parents=True, exist_ok=True)
                            path.write_text(workspace.expand(text), encoding="utf-8")
                        for relative, text in step.temporary_files.items():
                            workspace.write_temporary(relative, text)
                        for relative in step.remove_temporary:
                            workspace.temporary_file(relative).unlink()
                        for relative in step.remove:
                            workspace.file(relative).unlink()
                        if step.navigation_text is not None:
                            navigation = workspace.progress_path(thread)
                            navigation.parent.mkdir(parents=True, exist_ok=True)
                            navigation.write_text(step.navigation_text)
                    elif isinstance(step, (MessageStep, CompactStep)):
                        prompt = (
                            workspace.expand(step.prompt)
                            if isinstance(step, MessageStep)
                            else ""
                        )
                        try:
                            observation = (
                                driver.message(thread, prompt)
                                if isinstance(step, MessageStep)
                                else driver.compact(thread)
                            )
                        except (
                            LimitReached,
                            TimeLimitReached,
                            ExecutionFailed,
                        ) as error:
                            if (
                                error.observation is not None
                                and on_observation is not None
                            ):
                                on_observation(
                                    workspace, index, thread, prompt, error.observation
                                )
                            raise
                        if not observation.completed:
                            raise ValueError("Runtime turn did not complete.")
                        if isinstance(step, CompactStep) and not observation.compacted:
                            raise ValueError("Compaction was not confirmed complete.")
                    if (
                        not isinstance(step, (SeedStep, EditStep))
                        and observation.tokens is not None
                    ):
                        tokens[thread] = observation.tokens
                        result.tokens = sum(tokens.values())
                    try:
                        for check in step.checks:
                            if isinstance(check, BrowserCheck):
                                from evals.gui import candidate_browser, collect_browser

                                candidate_browser(workspace)
                                observation.browser_evidence.append(
                                    collect_browser(workspace, check.scenario)
                                )
                    finally:
                        if on_observation is not None and isinstance(
                            step, (MessageStep, CompactStep, EditStep)
                        ):
                            on_observation(
                                workspace,
                                index,
                                thread,
                                workspace.expand(step.prompt)
                                if isinstance(step, MessageStep)
                                else "",
                                observation,
                            )
                    if (
                        not isinstance(step, (SeedStep, EditStep))
                        and observation.tokens is None
                    ):
                        raise ValueError("Runtime did not report token usage.")
                    commands.extend(observation.commands)
                    for check in step.checks:
                        passed, detail = check_result(
                            check, observation, workspace, thread, commands
                        )
                        result.checks.append(
                            CheckResult(
                                index, step.conversation, check.kind, passed, detail
                            )
                        )
                    if (
                        max_tokens
                        and result.tokens is not None
                        and result.tokens > max_tokens
                    ):
                        if index + 1 < len(case.steps):
                            raise LimitReached(
                                "Token guard reached after a completed step.",
                                result.tokens,
                            )
                        result.detail = "Completed task exceeded the token guard."
                result.status = (
                    "pass" if all(check.passed for check in result.checks) else "fail"
                )
            finally:
                result.isolation_status = (
                    "verified"
                    if getattr(driver, "isolation_verified", False)
                    else "unverified"
                )
                result.metrics.update(getattr(driver, "metrics", {}))
                driver.close()
    except (LimitReached, TimeoutError) as error:
        result.status = "limit"
        result.detail = str(error)
        result.tokens = (
            error.tokens
            if isinstance(error, (LimitReached, TimeLimitReached))
            else result.tokens
        )
        result.metrics.update(getattr(error, "metrics", {}))
    except Exception as error:
        if isinstance(error, ExecutionFailed):
            result.tokens = error.observation.tokens
        result.status = "error"
        result.detail = f"{type(error).__name__}: {error}"[:400]
    result.metrics["total_seconds"] = time.monotonic() - started
    result.mechanical_status = result.status
    if case.rubric and result.status == "pass":
        result.status = "inconclusive"
        result.detail = "Required task criteria have not been assessed."
    return result
