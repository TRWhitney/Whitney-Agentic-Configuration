"""Disposable projects and instruction bundles used by every case."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Iterator, Sequence
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from pydantic import JsonValue, TypeAdapter

from evals.models import BrowserCheck, CaseSpec, SeedStep

if TYPE_CHECKING:
    from evals.gui import BrowserWorker


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout.strip()


@dataclass
class Workspace:
    root: Path
    home: Path
    baseline: dict[str, bytes]
    source_digest: str
    source_revision: str | None
    initial_commit: str = ""
    grader_files: dict[str, bytes] = field(default_factory=dict)
    initial_service_state: dict[str, JsonValue] | None = None
    temporary_baseline: dict[str, bytes] = field(default_factory=dict)
    raw_temporary_contents: set[bytes] = field(default_factory=set)
    initial_objects: set[str] = field(default_factory=set)
    browser_worker: BrowserWorker | None = field(default=None, repr=False)
    candidate_role: Literal["primary", "implementation-worker"] = "primary"

    def publish(self) -> None:
        remote = self.root.parent / "origin.git"
        if (
            not remote.is_dir()
            or git(self.root, "remote", "get-url", "origin") != str(remote)
            or git(self.root, "remote", "get-url", "--push", "--all", "origin")
            != str(remote)
        ):
            raise ValueError("publication may use only the disposable remote")
        git(
            self.root,
            "-c",
            "protocol.file.allow=always",
            "push",
            "--force",
            "-u",
            "origin",
            "HEAD:main",
        )

    @property
    def temporary_root(self) -> Path:
        return self.home.parent / "evidence"

    def expand(self, text: str) -> str:
        return text.replace("{temporary}", self.temporary_root.as_posix())

    def temporary_file(self, relative: str) -> Path:
        path = (self.temporary_root / relative).resolve()
        if not path.is_relative_to(self.temporary_root.resolve()):
            raise ValueError(f"Path leaves temporary evidence storage: {relative}")
        return path

    def temporary_files(self) -> dict[str, bytes]:
        return {
            path.relative_to(self.temporary_root).as_posix(): path.read_bytes()
            for path in self.temporary_root.rglob("*")
            if path.is_file()
        }

    def write_temporary(self, relative: str, content: str) -> bytes:
        path = self.temporary_file(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.expand(content), encoding="utf-8")
        raw = path.read_bytes()
        self.raw_temporary_contents.add(raw)
        return raw

    def file(self, relative: str) -> Path:
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError(f"Path leaves the project: {relative}")
        return path

    def project_files(self) -> dict[str, bytes]:
        names = set(
            git(
                self.root,
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ).split("\0")
        ) - {""}
        names.update(self.baseline)
        return {
            name: self.file(name).read_bytes()
            for name in names
            if self.file(name).is_file()
        }

    def service_state(self) -> dict[str, JsonValue] | None:
        adapter = TypeAdapter(dict[str, JsonValue])
        settings = adapter.validate_json(
            (self.root / ".git/work-system.json").read_text()
        )
        if settings.get("tracker") != "github" and not self.service_calls():
            return None
        state = adapter.validate_json(
            (self.home / "work-system/github.json").read_text()
        )
        return {key: state[key] for key in ("issues", "prs")}

    def progress_path(self, thread: str) -> Path:
        name = hashlib.sha256(thread.encode()).hexdigest()
        return self.home / "work-system/state" / f"{name}.json"

    def progress(self, thread: str) -> dict[str, object] | None:
        path = self.progress_path(thread)
        if not path.exists():
            return None
        value: dict[str, object] = json.loads(path.read_text())
        return value

    def seed(self, thread: str, step: SeedStep) -> None:
        arguments = ["start", step.workflow]
        if step.record:
            arguments.extend(["--record", str(self.file(step.record))])
        self.navigate(thread, arguments)
        progress = self.progress(thread)
        if progress is None:
            raise ValueError("Navigator did not save progress.")
        if progress["state"] != step.state:
            progress["state"] = step.state
            self.progress_path(thread).write_text(json.dumps(progress))
        if step.substate:
            self.navigate(thread, ["substate", "enter", step.substate])
        self.navigate(thread, ["resume"])

    def navigate(self, thread: str, arguments: Sequence[str]) -> str:
        navigator = self.home / "skills/work-system/scripts/navigate.py"
        result = subprocess.run(
            [sys.executable, str(navigator), *arguments],
            cwd=self.root,
            env={**self.environment(), "CODEX_THREAD_ID": thread},
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode:
            raise ValueError(
                f"Cannot prepare navigation state: {result.stderr.strip()}"
            )
        return result.stdout

    def environment(self) -> dict[str, str]:
        account_home = self.home.parent / "account"
        account_home.mkdir(exist_ok=True)
        return {
            **os.environ,
            "HOME": str(account_home),
            "USERPROFILE": str(account_home),
            "CODEX_HOME": str(self.home),
            "PATH": str(self.home / "bin") + os.pathsep + os.environ.get("PATH", ""),
        }

    def copy_credentials(self) -> None:
        home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
        auth = home / "auth.json"
        if not auth.is_file():
            raise ValueError(
                "Native runs require existing file-based Codex credentials."
            )
        destination = self.home / "auth.json"
        shutil.copyfile(auth, destination)
        destination.chmod(0o600)

    def service_calls(self) -> list[list[str]]:
        path = self.home / "work-system/service-calls.jsonl"
        if not path.exists():
            return []
        calls: list[list[str]] = [
            json.loads(line) for line in path.read_text().splitlines()
        ]
        return calls


def install_subject(source: Path, home: Path) -> str:
    instructions = source / "config/global-agents.md"
    shutil.copyfile(instructions, home / "AGENTS.md")
    skills = home / "skills"
    shutil.copytree(
        source / "skills", skills, ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    manifest = source / "config/external-skills.json"
    if manifest.exists():
        declarations: dict[str, dict[str, str]] = json.loads(manifest.read_text())
        for name, declaration in declarations.items():
            origin = (source / declaration["submodule"] / declaration["path"]).resolve()
            if not origin.is_relative_to(source.resolve()) or not origin.is_dir():
                raise ValueError(f"External skill source is unavailable: {name}")
            destination = (skills / name).resolve()
            if not destination.is_relative_to(skills.resolve()) or destination.exists():
                raise ValueError(f"Invalid external skill destination: {name}")
            shutil.copytree(
                origin,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
    digest = hashlib.sha256()
    for path in [
        home / "AGENTS.md",
        *sorted(path for path in skills.rglob("*") if path.is_file()),
    ]:
        digest.update(str(path.relative_to(home)).encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def install_service_fixture(home: Path, case: CaseSpec) -> None:
    directory = home / "bin"
    directory.mkdir()
    script = directory / "github.py"
    response = {
        "number": 12,
        "title": "Planning documents",
        "body": "Planning PR is open and unmerged.",
        "state": case.github_pr_state,
        "isDraft": case.github_pr_state == "OPEN",
        "mergedAt": "2026-10-01T00:00:00Z"
        if case.github_pr_state == "MERGED"
        else None,
        "mergeStateStatus": "DRAFT" if case.github_pr_state == "OPEN" else "CLEAN",
        "url": "https://github.com/example/inventory/pull/12",
        "labels": [],
        "comments": [],
        "statusCheckRollup": [],
    }
    if case.github_pr_state != "OPEN":
        response["body"] = "Planning PR: " + str(case.github_pr_state)
    bodies = case.github_issues or (
        {"10": case.github_issue_body, "11": case.github_issue_body}
        if case.github_issue_body is not None
        else {}
    )
    issues = {
        number: {
            "number": int(number),
            "title": "Name search",
            "body": body,
            "state": "OPEN",
            "labels": [
                {"name": label} for label in case.github_issue_labels.get(number, [])
            ],
            "comments": [],
            "url": f"https://github.com/example/inventory/issues/{number}",
        }
        for number, body in bodies.items()
    }
    (home / "work-system/github.json").write_text(
        json.dumps(
            {
                "issues": issues,
                "prs": {"12": response} if case.github_pr_state is not None else {},
                "read_error": case.github_read_error,
                "write_timeout": case.github_write_timeout,
            }
        )
    )
    shutil.copyfile(Path(__file__).with_name("github_fixture.py"), script)
    launcher = directory / "gh"
    launcher.write_text(
        f"#!{sys.executable}\n"
        f"exec(compile(open({str(script)!r}).read(), {str(script)!r}, 'exec'))\n"
    )
    launcher.chmod(0o755)
    (directory / "gh.cmd").write_text(f'@"{sys.executable}" "{script}" %*\n')


@contextmanager
def make_workspace(source: Path, case: CaseSpec) -> Iterator[Workspace]:
    with tempfile.TemporaryDirectory(prefix="project-") as temporary:
        directory = Path(temporary).resolve()
        root, home = directory / case.project_name, directory / "runtime"
        root.mkdir()
        home.mkdir()
        (home / "work-system").mkdir()
        digest = install_subject(source, home)
        install_service_fixture(home, case)
        git(root, "init", "-q")
        git(root, "config", "user.name", "Example Engineer")
        git(root, "config", "user.email", "dev@example.com")
        workspace = Workspace(root, home, {}, digest, None)
        workspace.candidate_role = case.candidate_role
        workspace.temporary_root.mkdir()
        for name, content in case.temporary_files.items():
            workspace.temporary_baseline[name] = workspace.write_temporary(
                name, content
            )
        workspace.grader_files = {
            p: text.encode("utf-8") for p, text in case.grader_files.items()
        }
        if case.delegation is not None:
            shutil.copyfile(
                Path(__file__).with_name("delegate_fixture.py"),
                home / "bin/delegate-fixture.py",
            )
            (home / "work-system/delegate.json").write_text(
                json.dumps({"root": str(root), "scenario": case.delegation})
            )

        def write_files(files: dict[str, str]) -> None:
            for relative, content in files.items():
                path = workspace.file(relative)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(workspace.expand(content), encoding="utf-8")
                workspace.baseline[relative] = path.read_bytes()

        write_files(
            {
                ".gitignore": "__pycache__/\n*.py[cod]\n",
                **case.files,
            }
        )
        settings: dict[str, str] = {"tracker": case.tracker}
        if case.tracker == "github":
            settings["repository"] = "example/inventory"
        (root / ".git/work-system.json").write_text(json.dumps(settings))
        workspace.initial_service_state = workspace.service_state()
        git(root, "add", ".")
        git(root, "commit", "-qm", "Define inventory behavior", "--allow-empty")
        workspace.initial_commit = git(root, "rev-parse", "HEAD")
        if case.local_remote:
            remote = directory / "origin.git"
            git(root, "init", "--bare", "-q", str(remote))
            git(root, "branch", "-M", "main")
            git(root, "remote", "add", "origin", str(remote))
            workspace.publish()
        workspace.initial_objects = set(
            git(
                root, "cat-file", "--batch-all-objects", "--batch-check=%(objectname)"
            ).splitlines()
        )
        write_files(case.uncommitted_files)
        if case.commit_hook is not None:
            hook = root / ".git/hooks/pre-commit"
            shutil.copyfile(workspace.file(case.commit_hook), hook)
            hook.chmod(0o755)
        with suppress(subprocess.CalledProcessError):
            workspace.source_revision = git(source, "rev-parse", "HEAD")
        try:
            if case.browser_tools or any(
                isinstance(check, BrowserCheck)
                for step in case.steps
                for check in step.checks
            ):
                from evals.gui import install_browser

                install_browser(workspace)
            yield workspace
        finally:
            if workspace.browser_worker is not None:
                workspace.browser_worker.close()
