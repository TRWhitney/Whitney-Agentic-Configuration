#!/usr/bin/env python3
"""Generate standalone skill navigators from their shared source."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

NAVIGATOR_SKILLS = ("note-system", "work-system")
NAVIGATOR_FILES = {"note-system": "navigate.py", "work-system": "navigation.py"}
GENERATED_NOTICE = (
    b"# Generated from scripts/navigator_source.py. Do not edit this copy.\n"
    b"# Regenerate with: python3 scripts/sync_navigators.py\n"
)
REGENERATE_COMMAND = "python3 scripts/sync_navigators.py"


class NavigatorSyncError(RuntimeError):
    """A generated navigator is missing, stale, or cannot be safely updated."""


def sync_navigators(source_root: Path, *, check: bool = False) -> tuple[Path, ...]:
    targets = [
        source_root / "skills" / name / "scripts" / NAVIGATOR_FILES[name]
        for name in NAVIGATOR_SKILLS
        if (source_root / "skills" / name).is_dir()
    ]
    if not targets:
        return ()

    source = source_root / "scripts" / "navigator_source.py"
    if source.is_symlink() or not source.is_file():
        raise NavigatorSyncError(f"Missing or symlinked navigator source: {source}")
    try:
        content = source.read_bytes()
        first_line, separator, body = content.partition(b"\n")
        if not first_line.startswith(b"#!") or not separator:
            raise NavigatorSyncError(
                f"Navigator source must start with a shebang: {source}"
            )
        expected = first_line + separator + GENERATED_NOTICE + body
        stale = []
        for target in targets:
            if target.is_symlink() or target.parent.is_symlink():
                raise NavigatorSyncError(f"Refusing symlinked navigator path: {target}")
            if target.exists() and not target.is_file():
                raise NavigatorSyncError(f"Navigator target is not a file: {target}")
            if not target.exists() or target.read_bytes() != expected:
                stale.append(target)
        if check and stale:
            paths = ", ".join(str(path.relative_to(source_root)) for path in stale)
            raise NavigatorSyncError(
                f"Missing or stale generated navigators: {paths}. "
                f"Run {REGENERATE_COMMAND} from the source repository."
            )
        for target in stale:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(expected)
        return tuple(stale)
    except OSError as error:
        raise NavigatorSyncError(f"Cannot synchronize navigators: {error}") from error


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check generated copies without writing."
    )
    options = parser.parse_args(arguments)
    try:
        changed = sync_navigators(
            Path(__file__).resolve().parents[1], check=options.check
        )
    except NavigatorSyncError as error:
        print(str(error), file=sys.stderr)
        return 1
    for path in changed:
        print(f"Updated {path}")
    if not changed:
        print("Generated navigators are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
