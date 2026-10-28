"""Save navigation progress separately for each conversation."""

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
    value = identifier if identifier is not None else os.environ.get("CODEX_THREAD_ID")
    if value is None:
        raise core.NavigationError(
            "Conversation ID unavailable. Supply --conversation <id>."
        )
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", value):
        raise core.NavigationError("Invalid conversation ID.")
    return value


def location() -> Path:
    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return home.expanduser().resolve() / "work-system" / "state"


def record_location(value: str) -> str:
    return value if "://" in value else str(Path(value).expanduser().resolve())


class Store:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Session | None:
        try:
            value = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None
        try:
            raw = core.mapping(json.loads(value), "saved navigation")
            if not {"workflow", "state"} <= raw.keys() or raw.keys() - {
                "workflow",
                "state",
                "substate",
                "record",
            }:
                raise ValueError("unexpected navigation fields")
            optional = {
                name: None if raw.get(name) is None else core.text(raw[name], name)
                for name in ("substate", "record")
            }
            record = optional["record"]
            if (
                record is not None
                and "://" not in record
                and not Path(record).is_absolute()
            ):
                raise ValueError("work-record path must be absolute")
            return Session(
                workflow=core.text(raw["workflow"], "workflow"),
                state=core.text(raw["state"], "state"),
                substate=optional["substate"],
                record=record,
            )
        except (ValueError, TypeError) as error:
            raise core.NavigationError(
                f"Cannot restore {self.path}: {error}"
            ) from error

    def save(self, session: Session) -> None:
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
                json.dump(
                    {
                        key: value
                        for key, value in asdict(session).items()
                        if value is not None
                    },
                    output,
                    indent=2,
                )
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary and Path(temporary).exists():
                Path(temporary).unlink()

    def clear(self) -> None:
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
