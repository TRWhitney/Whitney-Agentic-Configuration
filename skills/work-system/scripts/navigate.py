#!/usr/bin/env python3
"""Load repository workflow guidance for the project's selected provider."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path

# Keep standalone installation working with Python's isolated mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import navigation as core
import project
import sessions


def nav_command(*arguments: str) -> str:
    return " ".join(
        shlex.quote(value)
        for value in ("python3", str(Path(__file__).resolve()), *arguments)
    )


def bind_commands(output: str, conversation: str | None) -> str:
    if conversation is None:
        return output

    def bind(match: re.Match[str]) -> str:
        value = match.group(1)
        parts = shlex.split(value)
        if parts and parts[0] == "scripts/navigate.py":
            value = nav_command(*parts[1:])
            parts = shlex.split(value)
        if (
            len(parts) > 2
            and parts[1]
            in {str(Path(__file__).resolve()), str(Path(core.__file__).resolve())}
            and parts[2] != "provider"
            and "--conversation" not in parts
        ):
            value += " --conversation " + shlex.quote(conversation)
        return f"`{value}`"

    return re.sub(r"`((?:python3 |scripts/navigate.py )[^`\n]+)`", bind, output)


def substates_for(
    workflow: dict[str, object], state: str
) -> list[core.ProcedureAccess]:
    configured = core.mapping(
        core.state_for(workflow, state).get("substates", {}), "substates"
    )
    return [
        core.parse_access(name, {"status": "allowed", **core.mapping(raw, name)})
        for name, raw in configured.items()
    ]


def substate_for(
    workflow: dict[str, object], state: str, name: str
) -> core.ProcedureAccess:
    for access in substates_for(workflow, state):
        if access.name == name:
            return access
    raise core.NavigationError(f"Substate {name} is unavailable in {state}.")


def render_substate(
    provider: project.Provider, workflow: dict[str, object], state: str, name: str
) -> str:
    access = substate_for(workflow, state, name)
    sections = [
        core.read_markdown(core.REFERENCES_ROOT / "substates" / f"{name}.md", name)
    ]
    related = core.render_related_procedures(
        core.text(workflow["name"], "workflow"),
        state,
        core.procedures_for(workflow, state),
        access,
    )
    if related:
        sections.append(related)
    for format_access in access.formats:
        sections.append(
            provider.resource("formats", format_access.name)
            or core.read_markdown(
                core.FORMATS_ROOT / f"{format_access.name}.md", format_access.name
            )
        )
    if name == "wayfinding":
        command = nav_command(
            "reply",
            "--decided",
            "<n>",
            "--ready",
            "<n>",
            "--unspecified",
            "<topics or none>",
            "--body",
            "<facts and recommendation>",
            "--question",
            "<next decision question>",
        )
        sections.append(
            f"Build the final reply with `{command}`. Send its output unchanged."
        )
    sections.append(f"Leave this substate with `{nav_command('substate', 'leave')}`.")
    return "\n\n".join(sections)


def render_reply(
    decided: int,
    ready: int,
    unspecified: str,
    body: str,
    question: str | None,
    blocked_by: str | None,
    recap: bool = False,
) -> str:
    if decided < 0 or ready < 0:
        raise core.NavigationError("Decision counts cannot be negative.")
    if recap:
        if question is not None or blocked_by is not None:
            raise core.NavigationError("A recap uses its body without a next question.")
        ending = ""
    elif ready:
        if not question or blocked_by:
            raise core.NavigationError("Ask the next ready question with --question.")
        ending = question.strip()
    else:
        if not blocked_by or question:
            raise core.NavigationError(
                "Use --blocked-by when no question is ready, "
                "or leave finished wayfinding."
            )
        ending = blocked_by.strip()
    topics = unspecified.strip()
    discussion = body.strip()
    if not topics or not discussion or (not recap and not ending):
        raise core.NavigationError("Reply fields cannot be blank.")
    result = (
        f"Planning: {decided} decided, {ready} ready, unspecified: {topics}\n\n"
        f"{discussion}"
    )
    return result + f"\n\n{ending}" if ending else result


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
    session: sessions.Session | None = None,
    conversation: str | None = None,
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
    sections.append(f"Tracker: `{provider.directory.name}`")
    substates = substates_for(workflow, state_name)
    if substates:
        sections.append("## Optional substates")
        for substate in substates:
            sections.append(
                f"- `{substate.name}`: {substate.cue}\n"
                f"  Enter with `{nav_command('substate', 'enter', substate.name)}`"
            )
    if session:
        if session.record:
            sections.append(f"Read the work record before continuing: {session.record}")
        if session.substate:
            sections.append(
                render_substate(provider, workflow, state_name, session.substate)
            )
    resume = (
        core.resume_command(name, state_name)
        if session is None
        else nav_command("resume")
    )
    sections.extend(
        (
            "## Resume",
            f"Continue this state with `{resume}`",
            core.render_routes(name, state_name, state),
        )
    )
    return bind_commands("\n\n".join(sections), conversation)


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Navigate work-system states and procedures."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name in (
        "start",
        "resume",
        "move",
        "procedure",
        "format",
        "cancel",
        "substate",
        "reply",
        "commit",
    ):
        item = commands.add_parser(name)
        item.add_argument("--conversation")
        if name == "commit":
            actions = item.add_subparsers(dest="action", required=True)
            add = actions.add_parser("add")
            add.add_argument("revision")
            add.add_argument("--replaces", action="append", default=[])
            listing = actions.add_parser("list")
            remove = actions.add_parser("remove")
            remove.add_argument("commits", nargs="+")
            for action in (add, listing, remove):
                action.add_argument("--conversation", default=argparse.SUPPRESS)
        elif name == "start":
            item.add_argument("workflow")
            item.add_argument("--record")
        elif name == "resume":
            item.add_argument("workflow", nargs="?")
            item.add_argument("state", nargs="?")
        elif name == "reply":
            item.add_argument("--decided", type=int, required=True)
            item.add_argument("--ready", type=int, required=True)
            item.add_argument("--unspecified", required=True)
            item.add_argument("--body", required=True)
            ending = item.add_mutually_exclusive_group(required=True)
            ending.add_argument("--question")
            ending.add_argument("--blocked-by")
            ending.add_argument("--recap", action="store_true")
        elif name == "substate":
            item.add_argument("action", choices=("enter", "leave"))
            item.add_argument("name", nargs="?")
        elif name != "cancel":
            item.add_argument("workflow")
            item.add_argument("state")
            if name == "move":
                item.add_argument("destination")
            elif name == "procedure":
                item.add_argument("procedure")
            else:
                item.add_argument("format")
                sources = item.add_mutually_exclusive_group()
                sources.add_argument("--procedure")
                sources.add_argument("--substate")
    return parser


def recovery_guidance(provider: project.Provider) -> str:
    records = core.mapping(provider.manifest.get("records", {}), "records")
    paths = dict.fromkeys(
        provider.resource_path(core.text(value, "work-record guidance"))
        for value in records.values()
    )
    sections = [f"Tracker: {provider.directory.name}"]
    sections.extend(f"Work-record guidance: {path}" for path in paths)
    if paths:
        sections.append(
            "Read this guidance to find the work record and explain how it can help "
            "recovery. "
            "Leave the damaged state unchanged."
        )
    return "\n".join(sections)


def git_value(*arguments: str) -> str:
    result = subprocess.run(["git", *arguments], capture_output=True, text=True)
    if result.returncode:
        raise core.NavigationError(result.stderr.strip() or "Git command failed.")
    return result.stdout.strip()


def commit_hash(revision: str) -> str:
    if not revision:
        raise core.NavigationError("Supply a commit revision.")
    return git_value(
        "rev-parse", "--verify", "--end-of-options", revision + "^{commit}"
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

    args = build_parser().parse_args(arguments)
    if args.command == "commit":
        repository = str(Path(git_value("rev-parse", "--git-common-dir")).resolve())
        with sessions.locked_store(args.conversation) as store:
            if args.action == "add":
                commit = commit_hash(args.revision)
                store.update_commits(repository, [commit], args.replaces)
                return f"Recorded commit: {commit}"
            if args.action == "remove":
                store.update_commits(repository, [], args.commits)
                return "Removed recorded commits:\n" + "\n".join(args.commits)
            commits = store.commits(repository)
            return "Commits made in this session for this repository:\n" + (
                "\n".join(commits) if commits else "None."
            )
    provider, settings = project.selected()
    if args.command == "resume" and bool(args.workflow) != bool(args.state):
        raise core.NavigationError("Supply both workflow and state, or neither.")
    if args.command == "resume" and args.workflow:
        output = render_state(
            provider,
            settings,
            args.workflow,
            provider.workflow(args.workflow),
            args.state,
            include_record=True,
            conversation=args.conversation,
        )
        return bind_commands(
            output + "\n\nNamed-location guidance does not move the saved workflow. "
            f"Restore it with `{nav_command('resume')}`.",
            args.conversation,
        )
    try:
        return run_saved(args, provider, settings)
    except (core.NavigationError, OSError) as error:
        if args.command != "resume":
            raise
        raise core.NavigationError(
            f"{error}\n\n{recovery_guidance(provider)}"
        ) from error


def run_saved(
    args: argparse.Namespace, provider: project.Provider, settings: Path
) -> str:
    left_substate: str | None = None
    with sessions.locked_store(args.conversation) as store:
        session = store.load()
        if args.command == "start":
            workflow = provider.workflow(args.workflow)
            if session and session.workflow != args.workflow:
                raise core.NavigationError(
                    "A workflow is active in this conversation. Restore, complete, "
                    "or cancel it before starting another."
                )
            if session is None:
                session = sessions.Session(
                    args.workflow,
                    core.text(workflow["entry-state"], "entry state"),
                )
            if args.record is not None:
                session.record = sessions.record_location(args.record)
        elif args.command in {"procedure", "format", "move"}:
            workflow = provider.workflow(args.workflow)
            if session and (session.workflow, session.state) != (
                args.workflow,
                args.state,
            ):
                raise core.NavigationError(
                    f"The saved state is {session.workflow}.{session.state}. "
                    "Restore it before continuing."
                )
            if args.command == "procedure":
                output = render_procedure(
                    provider, workflow, args.state, args.procedure
                )
                resume = (
                    nav_command("resume")
                    if session
                    else core.resume_command(args.workflow, args.state)
                )
                return bind_commands(
                    output + f"\n\nReturn with `{resume}`.", args.conversation
                )
            if args.command == "format":
                if args.substate:
                    access = substate_for(workflow, args.state, args.substate)
                    if args.format not in {item.name for item in access.formats}:
                        raise core.NavigationError(
                            "Format unavailable through this substate."
                        )
                    return provider.resource(
                        "formats", args.format
                    ) or core.read_markdown(
                        core.FORMATS_ROOT / f"{args.format}.md", args.format
                    )
                return render_format(
                    provider, workflow, args.state, args.format, args.procedure
                )
            if session is None:
                session = sessions.Session(args.workflow, args.state)
            if session.substate:
                raise core.NavigationError(
                    "Leave the active substate before moving to another state."
                )
            source = core.state_for(workflow, args.state)
            destination = args.destination
            if (
                destination
                not in core.mapping(source.get("transitions"), "transitions").values()
            ):
                raise core.NavigationError(
                    f"Cannot move from {args.workflow}.{args.state} to {destination}."
                )
            if destination == "complete":
                if store.path.exists():
                    store.clear()
                return f"Workflow complete: {session.workflow}"
            session.workflow, session.state = (
                destination.split(".", 1)
                if "." in destination
                else (args.workflow, destination)
            )
        elif session is None:
            if args.command == "resume":
                return (
                    "No active workflow. "
                    "Use the work-system skill to choose a workflow."
                )
            raise core.NavigationError("No active workflow. Start one first.")
        if args.command == "reply":
            if session.substate != "wayfinding":
                raise core.NavigationError("Reply building requires active wayfinding.")
            substate_for(
                provider.workflow(session.workflow), session.state, "wayfinding"
            )
            return render_reply(
                args.decided,
                args.ready,
                args.unspecified,
                args.body,
                args.question,
                args.blocked_by,
                args.recap,
            )
        if args.command == "cancel":
            store.clear()
            return (
                f"Workflow cancelled: {session.workflow}. Its work record is unchanged."
            )
        workflow = provider.workflow(session.workflow)
        if args.command == "substate":
            if args.action == "enter":
                if not args.name:
                    raise core.NavigationError("Name the substate to enter.")
                substate_for(workflow, session.state, args.name)
                if session.substate and session.substate != args.name:
                    raise core.NavigationError(
                        "Leave the current substate before entering another."
                    )
                session.substate = args.name
            else:
                if args.name or not session.substate:
                    raise core.NavigationError(
                        "Use substate leave with an active substate and no name."
                    )
                left_substate = session.substate
                session.substate = None
        output = render_state(
            provider,
            settings,
            session.workflow,
            workflow,
            session.state,
            include_record=True,
            session=session,
            conversation=args.conversation,
        )
        if args.command != "resume":
            store.save(session)
        if left_substate and session.record:
            output += (
                f"\n\n{left_substate} has ended. Update {session.record} with the "
                "current workflow state and next step."
            )
        return output


def main() -> int:
    try:
        output = run(sys.argv[1:])
        # Route commands emitted by the shared engine back through this wrapper.
        print(
            output.replace(
                str(Path(core.__file__).resolve()), str(Path(__file__).resolve())
            )
        )
    except (core.NavigationError, OSError) as error:
        print(f"Navigation error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
