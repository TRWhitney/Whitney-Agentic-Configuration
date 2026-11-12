"""Save workflow state and commits separately for each conversation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path

import navigation as core


@dataclass
class Session:
    workflow: str
    state: str
    substate: str | None = None
    record: str | None = None


def conversation_id(identifier: str | None) -> str:
    value = (
        identifier
        if identifier is not None
        else (
            os.environ.get("CODEX_THREAD_ID")
            or os.environ.get("CLAUDE_CODE_SESSION_ID")
        )
    )
    if value is None:
        raise core.NavigationError(
            "Conversation ID unavailable. Supply --conversation <id>."
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", value):
        raise core.NavigationError("Invalid conversation ID.")
    return value


def location() -> Path:
    if os.environ.get("CLAUDE_CODE_SESSION_ID") and not os.environ.get(
        "CODEX_THREAD_ID"
    ):
        home = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude"))
    else:
        home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return home.expanduser().resolve() / "work-system" / "state"


def record_location(value: str) -> str:
    return value if "://" in value else str(Path(value).expanduser().resolve())


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _read(self) -> dict[str, object]:
        try:
            raw = core.mapping(
                json.loads(self.path.read_text(encoding="utf-8")), "conversation state"
            )
            if not raw or raw.keys() - {
                "workflow",
                "state",
                "substate",
                "record",
                "commits",
            }:
                raise ValueError("unexpected navigation fields")
            if ("workflow" in raw) != ("state" in raw):
                raise ValueError("workflow and state must occur together")
            if "workflow" not in raw and raw.keys() - {"commits"}:
                raise ValueError("navigation fields require an active workflow")
            for name in ("workflow", "state", "substate", "record"):
                if name in raw and (
                    name in {"workflow", "state"} or raw[name] is not None
                ):
                    core.text(raw[name], name)
            record = raw.get("record")
            if (
                isinstance(record, str)
                and "://" not in record
                and not Path(record).is_absolute()
            ):
                raise ValueError("work-record path must be absolute")
            commits = core.mapping(raw.get("commits", {}), "conversation commits")
            for repository, hashes in commits.items():
                if not Path(repository).is_absolute() or not isinstance(hashes, list):
                    raise ValueError("invalid repository commit list")
                if any(
                    not isinstance(value, str)
                    or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)
                    for value in hashes
                ):
                    raise ValueError("invalid commit hash")
                if len(hashes) != len(set(hashes)):
                    raise ValueError("duplicate commit hash")
            return raw
        except FileNotFoundError:
            return {}
        except (ValueError, TypeError) as error:
            raise core.NavigationError(
                f"Cannot restore {self.path}: {error}"
            ) from error

    def load(self) -> Session | None:
        raw = self._read()
        if "workflow" not in raw:
            return None
        return Session(
            workflow=core.text(raw["workflow"], "workflow"),
            state=core.text(raw["state"], "state"),
            substate=None
            if raw.get("substate") is None
            else core.text(raw["substate"], "substate"),
            record=None
            if raw.get("record") is None
            else core.text(raw["record"], "record"),
        )

    def commits(self, repository: str) -> list[str]:
        raw = core.mapping(self._read().get("commits", {}), "conversation commits")
        values = raw.get(repository, [])
        assert isinstance(values, list)
        return [core.text(value, "commit hash") for value in values]

    def update_commits(
        self, repository: str, added: list[str], removed: list[str]
    ) -> None:
        raw = self._read()
        commits = core.mapping(raw.get("commits", {}), "conversation commits")
        values = self.commits(repository)
        for commit in removed:
            if commit not in values:
                raise core.NavigationError(
                    f"Commit {commit} is not recorded in this session "
                    "for this repository."
                )
        values = [commit for commit in values if commit not in removed]
        for commit in added:
            if commit not in values:
                values.append(commit)
        if values:
            commits[repository] = values
        else:
            commits.pop(repository, None)
        if commits:
            raw["commits"] = commits
        else:
            raw.pop("commits", None)
        if raw:
            self._write(raw)
        else:
            self.path.unlink()

    def save(self, session: Session) -> None:
        raw: dict[str, object] = {
            key: value for key, value in asdict(session).items() if value is not None
        }
        commits = self._read().get("commits")
        if commits:
            raw["commits"] = commits
        self._write(raw)

    def _write(self, raw: dict[str, object]) -> None:
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                suffix=".tmp",
                delete=False,
            ) as output:
                temporary = output.name
                json.dump(raw, output, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary and Path(temporary).exists():
                Path(temporary).unlink()

    def clear(self) -> None:
        commits = self._read().get("commits")
        if commits:
            self._write({"commits": commits})
        else:
            self.path.unlink()


@contextmanager
def locked_store(identifier: str | None = None) -> Iterator[Store]:
    conversation = conversation_id(identifier)
    filename = hashlib.sha256(conversation.encode("utf-8")).hexdigest()
    directory = location()
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / f"{filename}.lock"
    with lock_path.open("a+b") as lock:
        if sys.platform == "win32":
            import msvcrt

            if lock.tell() == 0:
                lock.write(b"\0")
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield Store(directory / f"{filename}.json")
        finally:
            if sys.platform == "win32":
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)
