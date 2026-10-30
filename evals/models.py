"""Validated case definitions shared by offline tools and live execution."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    model_validator,
)


def _relative_path(value: str) -> str:
    parts = value.split("/")
    if (
        not value
        or "\\" in value
        or "\x00" in value
        or PurePosixPath(value).is_absolute()
        or PureWindowsPath(value).drive
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise ValueError("expected a safe relative project path")
    return value


RelativePath = Annotated[str, AfterValidator(_relative_path)]
Identifier = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")]
NonemptyText = Annotated[str, StringConstraints(min_length=1)]


def _regex_pattern(value: str) -> str:
    try:
        re.compile(value)
    except re.error as error:
        raise ValueError(f"invalid regex: {error}") from error
    return value


RegexPattern = Annotated[str, AfterValidator(_regex_pattern)]


class Definition(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class UnchangedCheck(Definition):
    exclude: list[RelativePath] = Field(default_factory=list)
    kind: Literal["unchanged"] = "unchanged"
    paths: Annotated[list[RelativePath], Field(min_length=1)]


class OnlyChangedCheck(Definition):
    kind: Literal["only_changed"] = "only_changed"
    paths: Annotated[list[RelativePath], Field(min_length=1)]


class FileEqualsCheck(Definition):
    kind: Literal["file_equals"] = "file_equals"
    path: RelativePath
    text: str


class ReplyRegexCheck(Definition):
    kind: Literal["reply_regex"] = "reply_regex"
    pattern: RegexPattern
    absent: bool = False


class CommandRegexCheck(Definition):
    kind: Literal["command_regex"] = "command_regex"
    pattern: RegexPattern
    absent: bool = False


class CommandExpectation(Definition):
    pattern: RegexPattern
    exit_code: int | None
    output_pattern: RegexPattern | None = None


class CommandSequenceCheck(Definition):
    kind: Literal["command_sequence"] = "command_sequence"
    commands: Annotated[list[CommandExpectation], Field(min_length=1)]


class ActionExpectation(Definition):
    kind: Literal["command", "agent"]
    pattern: RegexPattern
    exit_code: int | None = None
    tool: Identifier | None = None


class ActionSequenceCheck(Definition):
    kind: Literal["action_sequence"] = "action_sequence"
    actions: Annotated[list[ActionExpectation], Field(min_length=1)]


class AgentAssignmentsCheck(Definition):
    kind: Literal["agent_assignments"] = "agent_assignments"
    tools: Annotated[list[Identifier], Field(min_length=1)] = Field(
        default_factory=lambda: ["spawnAgent"]
    )
    min_count: Annotated[int, Field(ge=0)] = 1
    max_count: Annotated[int, Field(ge=0)] | None = None
    required_patterns: list[RegexPattern] = Field(default_factory=list)
    forbidden_patterns: list[RegexPattern] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_count(self) -> AgentAssignmentsCheck:
        if self.max_count is not None and self.max_count < self.min_count:
            raise ValueError("max_count is less than min_count")
        return self


class PythonCheck(Definition):
    kind: Literal["python_check"] = "python_check"
    path: RelativePath


class TemporaryFilesCheck(Definition):
    kind: Literal["temporary_files"] = "temporary_files"
    paths: Annotated[list[RelativePath], Field(min_length=1)]
    state: Literal["present", "absent", "unchanged"]


class NoRawEvidenceCheck(Definition):
    kind: Literal["no_raw_evidence"] = "no_raw_evidence"
    paths: list[RelativePath] = Field(default_factory=list)


class RegressionTestCheck(Definition):
    kind: Literal["regression_test"] = "regression_test"
    tests: RelativePath
    source: RelativePath
    faulty_text: NonemptyText | None = None


class BrowserCheck(Definition):
    kind: Literal["browser"] = "browser"
    scenario: Literal[
        "design",
        "rendering",
        "transitions",
        "composition",
        "layout",
        "audit",
        "clean",
        "shared-views",
        "keyboard",
        "display-settings",
    ]
    require_match: bool = True


class SessionCommitsCheck(Definition):
    kind: Literal["session_commits"] = "session_commits"
    include_initial: bool = False


class CompletedCheck(Definition):
    kind: Literal["completed"] = "completed"


class FileRegexCheck(Definition):
    kind: Literal["file_regex"] = "file_regex"
    path: RelativePath
    pattern: RegexPattern
    absent: bool = False


class ProseCheck(Definition):
    kind: Literal["prose"] = "prose"
    paths: Annotated[list[RelativePath], Field(min_length=1)]
    required_patterns: Annotated[list[RegexPattern], Field(min_length=1)]
    forbidden_patterns: list[RegexPattern] = Field(default_factory=list)


class ProgressCheck(Definition):
    kind: Literal["progress"] = "progress"
    workflow: Identifier
    state: Identifier
    substate: Identifier | None = None
    ignore_substate: bool = False


class CommitCountCheck(Definition):
    kind: Literal["commit_count"] = "commit_count"
    count: Annotated[int, Field(ge=0)]


class CommitGroupsCheck(Definition):
    kind: Literal["commit_groups"] = "commit_groups"
    groups: list[Annotated[list[RelativePath], Field(min_length=1)]]
    uncommitted: list[RelativePath] = Field(default_factory=list)


class NoPublishCheck(Definition):
    kind: Literal["no_publish"] = "no_publish"
    target: Literal["all", "pull_requests"] = "all"


class TrackerCheck(Definition):
    kind: Literal["tracker"] = "tracker"
    name: Literal["local", "github"]


class NavigationTextCheck(Definition):
    kind: Literal["navigation_text"] = "navigation_text"
    text: str


class GitHubStateCheck(Definition):
    kind: Literal["github_state"] = "github_state"
    resource: Literal["issues", "prs"] = "issues"
    count: Annotated[int, Field(ge=0)] | None = None
    number: Annotated[int, Field(ge=1)] | None = None
    body_pattern: RegexPattern | None = None

    @model_validator(mode="after")
    def has_expectation(self) -> GitHubStateCheck:
        if self.count is None and self.body_pattern is None:
            raise ValueError("service state needs a count or body pattern")
        return self


Check = Annotated[
    UnchangedCheck
    | OnlyChangedCheck
    | FileEqualsCheck
    | FileRegexCheck
    | ProseCheck
    | ReplyRegexCheck
    | CommandRegexCheck
    | CommandSequenceCheck
    | ActionSequenceCheck
    | AgentAssignmentsCheck
    | PythonCheck
    | TemporaryFilesCheck
    | NoRawEvidenceCheck
    | RegressionTestCheck
    | CompletedCheck
    | SessionCommitsCheck
    | BrowserCheck
    | ProgressCheck
    | CommitCountCheck
    | CommitGroupsCheck
    | NoPublishCheck
    | TrackerCheck
    | NavigationTextCheck
    | GitHubStateCheck,
    Field(discriminator="kind"),
]


class ConversationStep(Definition):
    conversation: Identifier = "main"
    checks: list[Check] = Field(default_factory=list)


class MessageStep(ConversationStep):
    kind: Literal["message"] = "message"
    prompt: NonemptyText


class SeedStep(ConversationStep):
    kind: Literal["seed"] = "seed"
    workflow: Identifier
    state: Identifier
    substate: Identifier | None = None
    record: RelativePath | None = None


class CompactStep(ConversationStep):
    kind: Literal["compact"] = "compact"


class EditStep(ConversationStep):
    kind: Literal["edit"] = "edit"
    files: dict[RelativePath, str] = Field(default_factory=dict)
    remove: list[RelativePath] = Field(default_factory=list)
    temporary_files: dict[RelativePath, str] = Field(default_factory=dict)
    remove_temporary: list[RelativePath] = Field(default_factory=list)
    navigation_text: str | None = None
    publish: bool = False
    record_commit: bool = False

    @model_validator(mode="after")
    def safe_edits(self) -> EditStep:
        for path in [*self.files, *self.remove]:
            if any(part.casefold() == ".git" for part in path.split("/")):
                raise ValueError("edit steps cannot write .git")
        if set(self.files).intersection(self.remove):
            raise ValueError("an edit cannot write and remove the same file")
        if set(self.temporary_files).intersection(self.remove_temporary):
            raise ValueError("an edit cannot write and remove the same temporary file")
        return self


Step = Annotated[
    MessageStep | SeedStep | CompactStep | EditStep, Field(discriminator="kind")
]


class RubricCriterion(Definition):
    id: Identifier
    description: NonemptyText
    required: bool = True


class CaseSpec(Definition):
    id: Identifier
    tags: list[Identifier]
    purpose: Literal["focused", "task", "control"] = "focused"
    project_name: Identifier = "inventory"
    artifacts: list[RelativePath] = Field(default_factory=list)
    rubric: list[RubricCriterion] = Field(default_factory=list)
    grader_files: dict[RelativePath, str] = Field(default_factory=dict)
    integration: bool = False
    browser_tools: bool = False
    candidate_role: Literal["primary", "implementation-worker"] = "primary"
    local_remote: bool = False
    tracker: Literal["local", "github"] = "local"
    github_pr_state: Literal["OPEN", "CLOSED", "MERGED"] | None = "OPEN"
    github_issue_body: str | None = None
    github_issues: dict[
        Annotated[str, StringConstraints(pattern=r"^[1-9][0-9]*$")], str
    ] = Field(default_factory=dict)
    github_issue_labels: dict[
        Annotated[str, StringConstraints(pattern=r"^[1-9][0-9]*$")], list[NonemptyText]
    ] = Field(default_factory=dict)
    github_read_error: bool = False
    github_write_timeout: bool = False
    fixtures: list[Identifier] = Field(default_factory=list)
    files: dict[RelativePath, str]
    uncommitted_files: dict[RelativePath, str] = Field(default_factory=dict)
    temporary_files: dict[RelativePath, str] = Field(default_factory=dict)
    commit_hook: RelativePath | None = None
    delegation: Literal["review", "label", "total"] | None = None
    steps: Annotated[list[Step], Field(min_length=1)]

    @model_validator(mode="after")
    def valid_references(self) -> CaseSpec:
        if not any(step.checks for step in self.steps):
            raise ValueError("a case must include at least one check")
        setup_files = {**self.files, **self.uncommitted_files}
        if self.purpose == "task" and not 3 <= len(self.rubric) <= 6:
            raise ValueError("task cases need three to six criteria")
        if len({c.id for c in self.rubric}) != len(self.rubric):
            raise ValueError("rubric criterion IDs must be unique")
        if self.rubric and not any(c.required for c in self.rubric):
            raise ValueError("a rubric needs at least one required criterion")
        if self.grader_files.keys() & setup_files.keys():
            raise ValueError("private grading files overlap project files")
        if self.commit_hook is not None and self.commit_hook not in setup_files:
            raise ValueError("commit hook is not a setup file")
        for path in setup_files:
            if any(part.casefold() == ".git" for part in path.split("/")):
                raise ValueError("setup files cannot write .git")
        paths = sorted(setup_files)
        for index, path in enumerate(paths):
            if any(other.startswith(path + "/") for other in paths[index + 1 :]):
                raise ValueError(f"setup file is also a directory: {path}")
        for step in self.steps:
            if isinstance(step, EditStep) and step.publish and not self.local_remote:
                raise ValueError("publication needs a disposable local remote")
            if isinstance(step, CompactStep) and not self.integration:
                raise ValueError("compact steps require an integration case")
            if (
                isinstance(step, SeedStep)
                and step.record is not None
                and step.record not in setup_files
            ):
                raise ValueError(f"seed record is not a setup file: {step.record}")
            for check in step.checks:
                if isinstance(check, NoRawEvidenceCheck) and any(
                    path not in setup_files for path in check.paths
                ):
                    raise ValueError("raw evidence path is not a setup file")
                if (
                    isinstance(check, TemporaryFilesCheck)
                    and check.state == "unchanged"
                    and any(path not in self.temporary_files for path in check.paths)
                ):
                    raise ValueError("unchanged temporary evidence needs a baseline")
                if (
                    isinstance(check, RegressionTestCheck)
                    and check.source not in setup_files
                ):
                    raise ValueError("regression source is not a setup file")
                if (
                    isinstance(check, PythonCheck)
                    and check.path not in setup_files
                    and check.path not in self.grader_files
                ):
                    raise ValueError(f"python check is not a setup file: {check.path}")
                if isinstance(check, UnchangedCheck):
                    missing = {
                        path
                        for path in check.paths
                        if path not in setup_files
                        and not any(name.startswith(path + "/") for name in setup_files)
                    }
                    if missing:
                        raise ValueError(
                            f"unchanged check has no setup file: {sorted(missing)}"
                        )
        return self


def load_cases(directory: Path) -> list[CaseSpec]:
    """Load a nonempty JSON corpus in filename order, rejecting duplicate IDs."""
    paths = sorted(directory.glob("*.json"))
    if not paths:
        raise ValueError(f"no case definitions in {directory}")
    cases: list[CaseSpec] = []
    identifiers: set[str] = set()
    fixtures: dict[str, dict[str, str]] = {}
    for path in paths:
        try:
            raw = TypeAdapter(dict[str, object]).validate_json(
                path.read_text(encoding="utf-8")
            )
            names = TypeAdapter(list[Identifier]).validate_python(
                raw.get("fixtures", []), strict=True
            )
            files: dict[str, str] = {}
            for name in names:
                if name not in fixtures:
                    fixture = (directory / "fixtures" / f"{name}.json").resolve()
                    if not fixture.is_relative_to(directory.resolve()):
                        raise ValueError("fixture leaves the case directory")
                    fixtures[name] = TypeAdapter(dict[RelativePath, str]).validate_json(
                        fixture.read_text(encoding="utf-8"), strict=True
                    )
                files.update(fixtures[name])
            files.update(
                TypeAdapter(dict[RelativePath, str]).validate_python(
                    raw.get("files", {}), strict=True
                )
            )
            raw["files"] = files
            case = CaseSpec.model_validate(raw)
        except (OSError, ValueError) as error:
            raise ValueError(f"invalid case definition {path}: {error}") from error
        if case.id in identifiers:
            raise ValueError(f"duplicate case ID: {case.id}")
        identifiers.add(case.id)
        cases.append(case)
    return cases


def select_cases(
    cases: list[CaseSpec],
    *,
    ids: set[str],
    tags: set[str],
    integration: bool,
    purposes: set[str] | None = None,
) -> list[CaseSpec]:
    """Filter IDs and any matching tag; integration cases require opt-in."""
    missing = ids.difference(case.id for case in cases)
    if missing:
        raise ValueError(f"unknown case IDs: {sorted(missing)}")
    selected = [
        case
        for case in cases
        if (not ids or case.id in ids)
        and (not tags or tags.intersection(case.tags))
        and (integration or not case.integration)
        and (not purposes or case.purpose in purposes)
    ]
    if not selected:
        raise ValueError("no cases match the selection")
    return selected
