#!/usr/bin/env python3
"""Expose only the workflow guidance relevant to an agent's requested location."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

Status = Literal["allowed", "triggered", "required"]
STATUSES: frozenset[str] = frozenset({"allowed", "triggered", "required"})
SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_ROOT = SKILL_ROOT / "references"
WORKFLOWS_ROOT = REFERENCES_ROOT / "workflows"
STATES_ROOT = REFERENCES_ROOT / "states"
PROCEDURES_ROOT = REFERENCES_ROOT / "procedures"
FORMATS_ROOT = REFERENCES_ROOT / "formats"


class NavigationError(Exception):
    """Report an invalid navigation request without a traceback."""


@dataclass(frozen=True)
class FormatAccess:
    name: str
    cue: str


@dataclass(frozen=True)
class ProcedureAccess:
    name: str
    status: Status
    cue: str
    related_procedures: tuple[str, ...]
    formats: tuple[FormatAccess, ...]


def mapping(value: object, label: str) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise NavigationError(f"Invalid {label} in workflow configuration.")
    return cast(dict[str, object], value)


def text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise NavigationError(f"Invalid {label} in workflow configuration.")
    return value


def names(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise NavigationError(f"Invalid {label} in workflow configuration.")
    if len(value) != len(set(value)):
        raise NavigationError(f"Duplicate {label} in workflow configuration.")
    return tuple(cast(list[str], value))


def load_workflow(workflow_name: str) -> dict[str, object]:
    path = WORKFLOWS_ROOT / f"{workflow_name}.json"
    if not path.is_file():
        raise NavigationError(f"Unknown workflow: {workflow_name}")
    try:
        loaded: object = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise NavigationError(f"Invalid workflow JSON for {workflow_name}.") from error
    workflow = mapping(loaded, f"{workflow_name} workflow")
    if workflow.get("name") != workflow_name:
        raise NavigationError(f"Workflow name does not match {workflow_name}.")
    return workflow


def states_for(workflow: dict[str, object]) -> dict[str, object]:
    return mapping(workflow.get("states"), "states")


def state_for(workflow: dict[str, object], state_name: str) -> dict[str, object]:
    state = states_for(workflow).get(state_name)
    if state is None:
        raise NavigationError(f"Unknown state for this workflow: {state_name}")
    return mapping(state, f"{state_name} state")


def parse_formats(value: object, label: str) -> tuple[FormatAccess, ...]:
    configured = mapping(value, label)
    return tuple(
        FormatAccess(
            name=name,
            cue=text(mapping(raw, f"{name} format access").get("cue"), f"{name} cue"),
        )
        for name, raw in configured.items()
    )


def parse_access(name: str, value: object) -> ProcedureAccess:
    access = mapping(value, f"{name} procedure access")
    raw_status = text(access.get("status"), f"{name} procedure status")
    if raw_status not in STATUSES:
        raise NavigationError(f"Invalid status for {name}: {raw_status}")
    return ProcedureAccess(
        name=name,
        status=cast(Status, raw_status),
        cue=text(access.get("cue"), f"{name} procedure cue"),
        related_procedures=names(
            access.get("related-procedures", []), f"{name} related procedures"
        ),
        formats=parse_formats(access.get("formats", {}), f"{name} formats"),
    )


def procedures_for(
    workflow: dict[str, object], state_name: str
) -> list[ProcedureAccess]:
    state = state_for(workflow, state_name)
    configured = mapping(state.get("procedures"), f"{state_name} procedures")
    return [parse_access(name, value) for name, value in configured.items()]


def formats_for_state(
    workflow: dict[str, object], state_name: str
) -> tuple[FormatAccess, ...]:
    state = state_for(workflow, state_name)
    return parse_formats(state.get("formats", {}), f"{state_name} formats")


def procedure_for(
    workflow: dict[str, object],
    state_name: str,
    procedure_name: str,
) -> ProcedureAccess:
    access = next(
        (
            procedure
            for procedure in procedures_for(workflow, state_name)
            if procedure.name == procedure_name
        ),
        None,
    )
    if access is None:
        workflow_name = text(workflow.get("name"), "workflow name")
        location = f"{workflow_name}.{state_name}"
        raise NavigationError(
            f"Procedure {procedure_name} is unavailable in {location}."
        )
    return access


def read_markdown(path: Path, label: str) -> str:
    if not path.is_file():
        raise NavigationError(f"Missing {label} guidance.")
    return path.read_text(encoding="utf-8").strip()


def procedure_command(
    workflow_name: str,
    state_name: str,
    procedure_name: str,
) -> str:
    arguments = [
        "python3",
        str(Path(__file__).resolve()),
        "procedure",
        workflow_name,
        state_name,
        procedure_name,
    ]
    return " ".join(shlex.quote(argument) for argument in arguments)


def format_command(
    workflow_name: str,
    state_name: str,
    format_name: str,
    procedure_name: str | None,
) -> str:
    arguments = [
        "python3",
        str(Path(__file__).resolve()),
        "format",
        workflow_name,
        state_name,
        format_name,
    ]
    if procedure_name is not None:
        arguments.extend(("--procedure", procedure_name))
    return " ".join(shlex.quote(argument) for argument in arguments)


def destination_command(
    workflow_name: str,
    state_name: str,
    destination: str,
) -> str:
    arguments = [
        "python3",
        str(Path(__file__).resolve()),
        "move",
        workflow_name,
        state_name,
        destination,
    ]
    return " ".join(shlex.quote(argument) for argument in arguments)


def resume_command(workflow_name: str, state_name: str) -> str:
    arguments = [
        "python3",
        str(Path(__file__).resolve()),
        "resume",
        workflow_name,
        state_name,
    ]
    return " ".join(shlex.quote(argument) for argument in arguments)


def render_routes(
    workflow_name: str,
    state_name: str,
    state: dict[str, object],
) -> str:
    transitions = mapping(state.get("transitions"), f"{state_name} transitions")
    lines = ["## Available routes"]
    for reason, raw_destination in transitions.items():
        destination = text(raw_destination, f"{reason} destination")
        command = destination_command(workflow_name, state_name, destination)
        lines.extend((f"- `{destination}` when `{reason}` applies.", f"  `{command}`"))
    return "\n".join(lines)


def render_formats(
    workflow_name: str,
    state_name: str,
    formats: tuple[FormatAccess, ...],
    procedure_name: str | None,
) -> str | None:
    if not formats:
        return None
    lines = ["## Formats"]
    for format_access in formats:
        command = format_command(
            workflow_name,
            state_name,
            format_access.name,
            procedure_name,
        )
        lines.extend(
            (
                f"- `{format_access.name}`: {format_access.cue}",
                f"  Load with `{command}`",
            )
        )
    return "\n".join(lines)


def render_related_procedures(
    workflow_name: str,
    state_name: str,
    procedures: list[ProcedureAccess],
    access: ProcedureAccess,
) -> str | None:
    if not access.related_procedures:
        return None
    by_name = {procedure.name: procedure for procedure in procedures}
    lines = ["## Related procedures"]
    for related_name in access.related_procedures:
        if related_name == access.name:
            raise NavigationError(f"Procedure {access.name} cannot relate to itself.")
        related = by_name.get(related_name)
        if related is None:
            raise NavigationError(
                f"Related procedure {related_name} is unavailable in "
                f"{workflow_name}.{state_name}."
            )
        lines.append(f"- `{related.name}` ({related.status}): {related.cue}")
        if related.status == "required":
            lines.append("  Already loaded with the active state.")
            continue
        command = procedure_command(workflow_name, state_name, related.name)
        lines.append(f"  Load with `{command}`")
    return "\n".join(lines)


def render_state(
    workflow_name: str,
    workflow: dict[str, object],
    state_name: str,
    *,
    include_work_record: bool,
) -> str:
    state = state_for(workflow, state_name)
    state_guidance = read_markdown(STATES_ROOT / f"{state_name}.md", state_name)
    procedures = procedures_for(workflow, state_name)
    sections = [state_guidance, "## Procedures"]

    for procedure in procedures:
        sections.append(f"- `{procedure.name}` ({procedure.status}): {procedure.cue}")
        if procedure.status != "required":
            command = procedure_command(workflow_name, state_name, procedure.name)
            sections.append(f"  Load with `{command}`")

    state_formats = render_formats(
        workflow_name,
        state_name,
        formats_for_state(workflow, state_name),
        None,
    )
    if state_formats is not None:
        sections.append(state_formats)

    required = [procedure for procedure in procedures if procedure.status == "required"]
    if required:
        sections.append("## Required procedure guidance")
        for procedure in required:
            sections.append(
                read_markdown(PROCEDURES_ROOT / f"{procedure.name}.md", procedure.name)
            )
            procedure_formats = render_formats(
                workflow_name,
                state_name,
                procedure.formats,
                procedure.name,
            )
            if procedure_formats is not None:
                sections.append(procedure_formats)

    if include_work_record and "work-record" in workflow:
        relative_path = text(workflow["work-record"], "work record")
        sections.extend(
            (
                "## Workflow record",
                read_markdown(REFERENCES_ROOT / relative_path, "work record"),
            )
        )

    sections.extend(
        (
            "## Resume",
            "Continue this state in a fresh context with "
            f"`{resume_command(workflow_name, state_name)}`",
            render_routes(workflow_name, state_name, state),
        )
    )
    return "\n\n".join(sections)


def render_procedure(
    workflow_name: str,
    state_name: str,
    procedure_name: str,
) -> str:
    workflow = load_workflow(workflow_name)
    procedures = procedures_for(workflow, state_name)
    access = procedure_for(workflow, state_name, procedure_name)
    guidance = read_markdown(PROCEDURES_ROOT / f"{procedure_name}.md", procedure_name)
    sections = [f"Procedure status: {access.status}", guidance]
    related = render_related_procedures(workflow_name, state_name, procedures, access)
    if related is not None:
        sections.append(related)
    formats = render_formats(
        workflow_name,
        state_name,
        access.formats,
        procedure_name,
    )
    if formats is not None:
        sections.append(formats)
    return "\n\n".join(sections)


def render_format(
    workflow_name: str,
    state_name: str,
    format_name: str,
    procedure_name: str | None,
) -> str:
    workflow = load_workflow(workflow_name)
    if procedure_name is None:
        formats = formats_for_state(workflow, state_name)
    else:
        procedure = procedure_for(workflow, state_name, procedure_name)
        formats = procedure.formats
    if format_name not in {format_access.name for format_access in formats}:
        source = procedure_name or state_name
        raise NavigationError(f"Format {format_name} is unavailable through {source}.")
    return read_markdown(FORMATS_ROOT / f"{format_name}.md", format_name)


def resolve_destination(
    workflow_name: str,
    workflow: dict[str, object],
    state_name: str,
    destination: str,
) -> tuple[str, dict[str, object], str]:
    state = state_for(workflow, state_name)
    transitions = mapping(state.get("transitions"), f"{state_name} transitions")
    destinations = {
        text(value, f"{reason} destination") for reason, value in transitions.items()
    }
    if destination not in destinations:
        permitted = ", ".join(sorted(destinations))
        raise NavigationError(
            f"Cannot move from {workflow_name}.{state_name} to {destination}. "
            f"Available destinations: {permitted}"
        )
    if destination == "complete":
        return workflow_name, workflow, destination
    if "." not in destination:
        state_for(workflow, destination)
        return workflow_name, workflow, destination
    next_workflow_name, next_state_name = destination.split(".", maxsplit=1)
    next_workflow = load_workflow(next_workflow_name)
    state_for(next_workflow, next_state_name)
    return next_workflow_name, next_workflow, next_state_name


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Navigate note-system states and procedures."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("workflow")

    resume = subparsers.add_parser("resume")
    resume.add_argument("workflow")
    resume.add_argument("state")

    procedure = subparsers.add_parser("procedure")
    procedure.add_argument("workflow")
    procedure.add_argument("state")
    procedure.add_argument("procedure")

    format_parser = subparsers.add_parser("format")
    format_parser.add_argument("workflow")
    format_parser.add_argument("state")
    format_parser.add_argument("format")
    format_parser.add_argument("--procedure")

    move = subparsers.add_parser("move")
    move.add_argument("workflow")
    move.add_argument("state")
    move.add_argument("destination")
    return parser


def run(args: argparse.Namespace) -> str:
    command = cast(str, args.command)
    workflow_name = cast(str, args.workflow)
    workflow = load_workflow(workflow_name)

    if command == "start":
        entry_state = text(workflow.get("entry-state"), "entry state")
        return render_state(
            workflow_name,
            workflow,
            entry_state,
            include_work_record=True,
        )
    if command == "resume":
        return render_state(
            workflow_name,
            workflow,
            cast(str, args.state),
            include_work_record=True,
        )
    if command == "procedure":
        return render_procedure(
            workflow_name,
            cast(str, args.state),
            cast(str, args.procedure),
        )
    if command == "format":
        return render_format(
            workflow_name,
            cast(str, args.state),
            cast(str, args.format),
            cast(str | None, args.procedure),
        )
    if command == "move":
        current_state = cast(str, args.state)
        destination = cast(str, args.destination)
        next_workflow_name, next_workflow, next_state = resolve_destination(
            workflow_name, workflow, current_state, destination
        )
        if next_state == "complete":
            return f"Workflow complete: {workflow_name}"
        return render_state(
            next_workflow_name,
            next_workflow,
            next_state,
            include_work_record=next_workflow_name != workflow_name,
        )
    raise NavigationError(f"Unknown command: {command}")


def main() -> int:
    try:
        print(run(build_parser().parse_args()))
    except NavigationError as error:
        print(f"Navigation error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
