#!/usr/bin/env python3
"""Configure compaction recovery or restore work from a SessionStart hook."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import navigation as core
import sessions


def configuration_home(application: str) -> Path:
    variable, directory = (
        ("CODEX_HOME", ".codex")
        if application == "codex"
        else ("CLAUDE_CONFIG_DIR", ".claude")
    )
    return Path(os.environ.get(variable, Path.home() / directory)).expanduser()


def configure(application: str, home: Path, *, dry_run: bool) -> str:
    target = home / ("hooks.json" if application == "codex" else "settings.json")
    if home.is_symlink() or target.is_symlink():
        raise ValueError(f"Refusing symlinked hook configuration: {target}")
    configuration = (
        core.mapping(json.loads(target.read_text()), "application configuration")
        if target.exists()
        else {}
    )
    hooks = core.mapping(configuration.setdefault("hooks", {}), "hooks")
    groups = hooks.setdefault("SessionStart", [])
    if not isinstance(groups, list):
        raise ValueError("SessionStart hooks must be a list.")
    script = str(Path(__file__).resolve())
    command = shlex.join(
        [
            sys.executable,
            script,
            "resume",
            "--application",
            application,
            "--config-home",
            str(home.resolve()),
        ]
    )
    handler: dict[str, object] = {"type": "command", "command": command, "timeout": 20}
    if application == "codex":
        handler["additionalContextLimit"] = 0
    replacement = {"matcher": "^compact$", "hooks": [handler]}
    for index, raw in enumerate(groups):
        group = core.mapping(raw, "SessionStart group")
        handlers = group.get("hooks", [])
        if not isinstance(handlers, list):
            raise ValueError("Hook handlers must be a list.")
        for item in handlers:
            existing = core.mapping(item, "hook handler")
            value = existing.get("command")
            if not isinstance(value, str):
                continue
            parts = shlex.split(value)
            if len(parts) >= 3 and parts[1:3] == [script, "resume"]:
                if len(handlers) != 1 or group.get("matcher") != "^compact$":
                    raise ValueError(
                        "Existing recovery hook was edited; reconcile it first."
                    )
                groups[index] = replacement
                break
        else:
            continue
        break
    else:
        groups.append(replacement)
    configuration["hooks"] = hooks
    content = json.dumps(configuration, indent=2) + "\n"
    if dry_run:
        return content
    if target.exists() and target.read_text() == content:
        return f"Hook already configured: {target}"
    home.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=home, delete=False
        ) as output:
            temporary = output.name
            output.write(content)
        if target.exists():
            os.chmod(temporary, target.stat().st_mode & 0o777)
        os.replace(temporary, target)
    finally:
        if temporary and Path(temporary).exists():
            Path(temporary).unlink()
    return f"Configured compaction recovery: {target}"


def recover(
    application: str, home: Path, event: dict[str, object]
) -> dict[str, object] | None:
    if (
        event.get("hook_event_name") != "SessionStart"
        or event.get("source") != "compact"
    ):
        return None
    identifier = sessions.conversation_id(
        core.text(event.get("session_id"), "session_id")
    )
    cwd = Path(core.text(event.get("cwd"), "cwd"))
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError("Hook cwd must be an existing absolute directory.")
    environment = dict(os.environ)
    environment.pop("CODEX_THREAD_ID", None)
    environment.pop("CLAUDE_CODE_SESSION_ID", None)
    if application == "codex":
        environment.update(CODEX_HOME=str(home), CODEX_THREAD_ID=identifier)
    else:
        environment.update(
            CLAUDE_CONFIG_DIR=str(home), CLAUDE_CODE_SESSION_ID=identifier
        )
    navigator = Path(__file__).resolve().with_name("navigate.py")
    arguments = [sys.executable, str(navigator), "resume", "--conversation", identifier]
    result = subprocess.run(
        arguments, cwd=cwd, env=environment, capture_output=True, text=True, timeout=15
    )
    if result.returncode:
        context = (
            "Work-system recovery failed. Stop work and report this error. "
            "Leave the saved state unchanged.\n\n" + result.stderr
        )
    else:
        context = (
            f"Read {navigator.parent.parent / 'SKILL.md'} before continuing.\n\n"
            f"Recovered with {shlex.join(arguments)}:\n\n{result.stdout}"
        )
    output: dict[str, object] = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    if result.returncode and application == "codex":
        output.update(
            {
                "continue": False,
                "stopReason": result.stderr.strip(),
                "systemMessage": result.stderr.strip(),
            }
        )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("configure", "resume"))
    parser.add_argument("--application", choices=("codex", "claude"), required=True)
    parser.add_argument("--config-home", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    options = parser.parse_args()
    home = (
        (options.config_home or configuration_home(options.application))
        .expanduser()
        .absolute()
    )
    try:
        if options.command == "configure":
            print(configure(options.application, home, dry_run=options.dry_run))
        else:
            output = recover(
                options.application,
                home,
                core.mapping(json.load(sys.stdin), "hook input"),
            )
            if output is not None:
                print(json.dumps(output))
    except (
        ValueError,
        OSError,
        core.NavigationError,
        subprocess.TimeoutExpired,
    ) as error:
        print(f"Compaction recovery error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
