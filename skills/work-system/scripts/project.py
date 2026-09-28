"""Load the selected project's provider and its workflow resources."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import navigation as core

PROVIDERS_ROOT = core.REFERENCES_ROOT / "providers"


def settings_path() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise core.NavigationError(f"Cannot locate project: {error}") from error
    if result.returncode:
        return Path.cwd() / ".work" / "project.json"
    return Path(result.stdout.strip()) / "work-system.json"


def read_json(path: Path) -> dict[str, object]:
    try:
        return core.mapping(json.loads(path.read_text(encoding="utf-8")), str(path))
    except (OSError, json.JSONDecodeError) as error:
        raise core.NavigationError(f"Cannot read {path}: {error}") from error


@dataclass(frozen=True)
class Provider:
    directory: Path
    manifest: dict[str, object]

    def resource(self, group: str, name: str) -> str | None:
        resources = core.mapping(self.manifest.get(group, {}), group)
        value = resources.get(name)
        if value is None:
            return None
        return self.read(core.text(value, f"{group}.{name}"))

    def read(self, relative: str) -> str:
        path = (self.directory / relative).resolve()
        if not path.is_relative_to(self.directory.resolve()):
            raise core.NavigationError("Provider resource is outside its directory.")
        return core.read_markdown(path, relative)

    def applies(self, workflow: str) -> bool:
        return workflow in core.names(self.manifest.get("workflows", []), "workflows")

    def workflow(self, name: str) -> dict[str, object]:
        workflow = core.load_workflow(name)
        if not self.applies(name):
            return workflow
        states = core.states_for(workflow)
        for state, raw in core.mapping(
            self.manifest.get("states", {}), "states"
        ).items():
            additions = core.mapping(raw, state)
            target = core.mapping(states[state], state)
            procedures = core.mapping(target["procedures"], "procedures")
            procedures.update(
                core.mapping(additions.get("procedures", {}), "procedures")
            )
        transitions = core.mapping(
            self.manifest.get("workflow-transitions", {}), "transitions"
        )
        for state, raw in core.mapping(transitions.get(name, {}), name).items():
            target = core.mapping(states[state], state)
            core.mapping(target["transitions"], "transitions").update(
                core.mapping(raw, state)
            )
        if name in core.mapping(self.manifest.get("records", {}), "records"):
            workflow["persistence"] = "durable"
        return workflow


def load_named(name: str) -> Provider:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise core.NavigationError("Invalid provider name.")
    directory = PROVIDERS_ROOT / name
    if not (directory / "provider.json").is_file():
        raise core.NavigationError(f"Provider {name} is not installed.")
    return Provider(directory, read_json(directory / "provider.json"))


def selected() -> tuple[Provider, Path]:
    path = settings_path()
    settings = read_json(path) if path.exists() else {"tracker": "local"}
    provider = load_named(core.text(settings.get("tracker"), "project tracker"))
    for key in core.names(
        provider.manifest.get("required-settings", []), "required settings"
    ):
        value = settings.get(key)
        if not isinstance(value, str) or not value.strip():
            raise core.NavigationError(f"Missing project setting {key} in {path}.")
    return provider, path
