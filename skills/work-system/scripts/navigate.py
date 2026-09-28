#!/usr/bin/env python3
"""Load repository workflow guidance for the project's selected provider."""

from __future__ import annotations

import argparse
import shlex
import sys
from pathlib import Path
from typing import cast

# Keep standalone installation working with Python's isolated mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import navigation as core
import project


def procedure_guidance(provider: project.Provider, name: str) -> str:
    return provider.resource("procedures", name) or core.read_markdown(
        core.PROCEDURES_ROOT / f"{name}.md", name
    )


def provider_command(workflow: str, state: str) -> str:
    arguments = ["python3", str(Path(__file__).resolve()), "provider", workflow, state]
    return " ".join(shlex.quote(value) for value in arguments) + " <provider>"


def render_state(
    provider: project.Provider,
    settings: Path,
    name: str,
    workflow: dict[str, object],
    state_name: str,
    *,
    include_record: bool,
) -> str:
    state = core.state_for(workflow, state_name)
    procedures = core.procedures_for(workflow, state_name)
    sections = [
        core.read_markdown(core.STATES_ROOT / f"{state_name}.md", state_name),
        "## Procedures",
    ]
    for procedure in procedures:
        sections.append(f"- `{procedure.name}` ({procedure.status}): {procedure.cue}")
        if procedure.status != "required":
            command = core.procedure_command(name, state_name, procedure.name)
            sections.append(f"  Load with `{command}`")
    formats = core.render_formats(
        name, state_name, core.formats_for_state(workflow, state_name), None
    )
    if formats:
        sections.append(formats)
    required = [item for item in procedures if item.status == "required"]
    if required:
        sections.append("## Required procedure guidance")
        for item in required:
            sections.append(procedure_guidance(provider, item.name))
            formats = core.render_formats(name, state_name, item.formats, item.name)
            if formats:
                sections.append(formats)
    if include_record and provider.applies(name):
        sections.extend(("## Project settings", f"`{settings}`"))
        record = provider.resource("records", name)
        if record:
            sections.extend(("## Workflow record", record))
    sections.extend(
        (
            "## Resume",
            f"Continue this state with `{core.resume_command(name, state_name)}`",
            core.render_routes(name, state_name, state),
        )
    )
    return "\n\n".join(sections)


def render_procedure(
    provider: project.Provider, workflow: dict[str, object], state: str, name: str
) -> str:
    workflow_name = core.text(workflow["name"], "workflow name")
    access = core.procedure_for(workflow, state, name)
    sections = [
        f"Procedure status: {access.status}",
        procedure_guidance(provider, name),
    ]
    related = core.render_related_procedures(
        workflow_name, state, core.procedures_for(workflow, state), access
    )
    if related:
        sections.append(related)
    formats = core.render_formats(workflow_name, state, access.formats, name)
    if formats:
        sections.append(formats)
    if name == "tracking":
        sections.append(f"Provider setup: `{provider_command(workflow_name, state)}`")
    return "\n\n".join(sections)


def render_format(
    provider: project.Provider,
    workflow: dict[str, object],
    state: str,
    name: str,
    procedure: str | None,
) -> str:
    formats = (
        core.formats_for_state(workflow, state)
        if procedure is None
        else core.procedure_for(workflow, state, procedure).formats
    )
    if name not in {item.name for item in formats}:
        raise core.NavigationError(
            f"Format {name} is unavailable through {procedure or state}."
        )
    return provider.resource("formats", name) or core.read_markdown(
        core.FORMATS_ROOT / f"{name}.md", name
    )


def run(arguments: list[str]) -> str:
    if arguments and arguments[0] == "provider":
        command = argparse.ArgumentParser(
            description="Read setup for the requested provider."
        )
        command.add_argument("command")
        command.add_argument("workflow")
        command.add_argument("state")
        command.add_argument("provider")
        args = command.parse_args(arguments)
        workflow = core.load_workflow(args.workflow)
        core.procedure_for(workflow, args.state, "tracking")
        provider = project.load_named(args.provider)
        return f"Settings: `{project.settings_path()}`\n\n" + provider.read(
            core.text(provider.manifest.get("setup"), "provider setup")
        )

    args = core.build_parser().parse_args(arguments)
    name = cast(str, args.workflow)
    provider, settings = project.selected()
    workflow = provider.workflow(name)
    command_name = cast(str, args.command)
    if command_name in {"start", "resume"}:
        state = (
            core.text(workflow["entry-state"], "entry state")
            if command_name == "start"
            else cast(str, args.state)
        )
        return render_state(
            provider, settings, name, workflow, state, include_record=True
        )
    if command_name == "procedure":
        return render_procedure(provider, workflow, args.state, args.procedure)
    if command_name == "format":
        return render_format(
            provider, workflow, args.state, args.format, args.procedure
        )
    if command_name == "move":
        current_state = core.state_for(workflow, args.state)
        routes = core.mapping(current_state.get("transitions"), "transitions")
        destination = cast(str, args.destination)
        if destination not in routes.values():
            raise core.NavigationError(
                f"Cannot move from {name}.{args.state} to {destination}."
            )
        if destination == "complete":
            return f"Workflow complete: {name}"
        next_name, next_state = (
            destination.split(".", maxsplit=1)
            if "." in destination
            else (name, destination)
        )
        next_workflow = provider.workflow(next_name)
        return render_state(
            provider,
            settings,
            next_name,
            next_workflow,
            next_state,
            include_record=next_name != name,
        )
    raise core.NavigationError(f"Unknown command: {command_name}")


def main() -> int:
    try:
        output = run(sys.argv[1:])
        # Route commands emitted by the shared engine back through this wrapper.
        print(
            output.replace(
                str(Path(core.__file__).resolve()), str(Path(__file__).resolve())
            )
        )
    except core.NavigationError as error:
        print(f"Navigation error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
