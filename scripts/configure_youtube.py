#!/usr/bin/env python3
"""Check and interactively configure yt-dlp for native and Flatpak acquisition."""

from __future__ import annotations

import argparse
import ast
import codecs
import json
import locale
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]
Resolver = Callable[[str], str | None]
CONFIG_LINE = re.compile(r'^\[debug\] (.*?)[Cc]onfig(?: "(.*?)")?: (.*)$')
VERSION = re.compile(r"\b(?:v)?(\d+)\.(\d+)\.(\d+)")
MINIMUM_RUNTIME = {"deno": (2, 3, 0), "node": (22, 0, 0)}
BROWSER_READERS = {
    "brave",
    "chrome",
    "chromium",
    "edge",
    "firefox",
    "opera",
    "safari",
    "vivaldi",
    "whale",
}


class SetupError(Exception):
    """An actionable configuration or command failure."""


@dataclass(frozen=True)
class Context:
    home: Path
    platform: str
    environ: Mapping[str, str]
    run: Runner
    resolve: Resolver
    ask: Callable[[str], str]
    emit: Callable[[str], None]


@dataclass(frozen=True)
class Profile:
    label: str
    browser: str
    path: Path
    database: Path

    @property
    def spec(self) -> str:
        reader = "firefox" if self.browser == "zen" else self.browser
        return f"{reader}:{self.database if reader == 'safari' else self.path}"


@dataclass(frozen=True)
class Diagnostic:
    arguments: tuple[str, ...]
    config: Path
    runtimes: str
    libraries: str

    @property
    def browser(self) -> str | None:
        return setting(
            self.arguments, "--cookies-from-browser", "--no-cookies-from-browser"
        )

    @property
    def cookies(self) -> str | None:
        return setting(self.arguments, "--cookies", "--no-cookies")

    @property
    def runtime_ready(self) -> bool:
        for kind, major, minor, patch in re.findall(
            r"(deno|node)-(\d+)\.(\d+)\.(\d+)", self.runtimes
        ):
            if (int(major), int(minor), int(patch)) >= MINIMUM_RUNTIME[kind]:
                return True
        return bool(re.search(r"quickjs-\d", self.runtimes))

    @property
    def solver_ready(self) -> bool:
        remote = values(self.arguments, "--remote-components", "--no-remote-components")
        return (
            "yt_dlp_ejs-" in self.libraries
            or "yt-dlp-ejs-" in self.libraries
            or (
                "ejs:github" in remote
                or ("ejs:npm" in remote and "deno-" in self.runtimes)
            )
        )


def values(arguments: Sequence[str], option: str, disable: str = "") -> list[str]:
    result: list[str] = []
    for index, argument in enumerate(arguments):
        if disable and argument == disable:
            result.clear()
        elif argument == option and index + 1 < len(arguments):
            result.append(arguments[index + 1])
        elif argument.startswith(option + "="):
            result.append(argument[len(option) + 1 :])
    return result


def setting(arguments: Sequence[str], option: str, disable: str = "") -> str | None:
    found = values(arguments, option, disable)
    return found[-1] if found else None


def expand_path(value: str, context: Context) -> Path:
    value = re.sub(
        r"\$(?:\{(\w+)\}|(\w+))|%(\w+)%",
        lambda m: context.environ.get(next(g for g in m.groups() if g), m[0]),
        value,
    )
    if value == "~" or value.startswith(("~/", "~\\")):
        value = str(context.home) + value[1:]
    return Path(value)


def user_config(context: Context) -> Path:
    if context.platform == "win32":
        root = context.environ.get("APPDATA", str(context.home / "AppData/Roaming"))
    else:
        root = context.environ.get("XDG_CONFIG_HOME", str(context.home / ".config"))
    return Path(root) / "yt-dlp/config"


def executable(context: Context, name: str) -> str | None:
    resolved = context.resolve(name)
    if resolved:
        return resolved
    for folder in (context.home / ".local/bin", context.home / "bin"):
        path = folder / (name + ".exe" if context.platform == "win32" else name)
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def parse_diagnostic(
    result: subprocess.CompletedProcess[str],
    default: Path,
    *,
    require_runtime: bool = True,
) -> Diagnostic:
    groups: list[list[str]] = []
    config = default
    runtime = ""
    libraries = ""
    chosen = False
    for line in result.stderr.splitlines():
        match = CONFIG_LINE.match(line)
        if match:
            try:
                parsed: object = ast.literal_eval(match[3])
            except (ValueError, SyntaxError) as error:
                raise SetupError(
                    "Cannot read yt-dlp configuration diagnostics."
                ) from error
            if not isinstance(parsed, list) or not all(
                isinstance(arg, str) for arg in parsed
            ):
                raise SetupError("Unexpected yt-dlp configuration diagnostics.")
            groups.append([str(arg) for arg in parsed])
            if (
                not chosen
                and match[1].strip() in ("Portable", "Home", "User")
                and match[2]
            ):
                config = Path(match[2])
                chosen = True
        elif line.startswith("[debug] JS runtimes: "):
            runtime = line.removeprefix("[debug] JS runtimes: ")
        elif line.startswith("[debug] Optional libraries: "):
            libraries = line.removeprefix("[debug] Optional libraries: ")
    if not groups or (require_runtime and not runtime):
        raise SetupError(
            "yt-dlp could not report configuration and runtimes. "
            "Check its executable and update to a release with EJS support."
        )
    arguments = tuple(arg for group in reversed(groups) for arg in group)
    return Diagnostic(arguments, config, runtime, libraries)


def flatpak_command(flatpak: str, app: str, command: Sequence[str]) -> list[str]:
    return [
        flatpak,
        "run",
        "--env=PYTHONDONTWRITEBYTECODE=1",
        "--command=" + command[0],
        app,
        *command[1:],
    ]


def inspect(
    context: Context,
    yt_dlp: str,
    *,
    flatpak: str | None = None,
    app: str | None = None,
    config: Path | None = None,
) -> Diagnostic:
    help_command = [yt_dlp, "--verbose", "--help"]
    if flatpak and app:
        help_command = flatpak_command(flatpak, app, help_command)
    configuration = context.run(help_command)
    if configuration.returncode:
        raise SetupError(
            "yt-dlp cannot parse its saved configuration. Repair it and rerun setup."
        )
    saved = parse_diagnostic(
        configuration, config or user_config(context), require_runtime=False
    )
    arguments = saved.arguments
    destination = saved.config
    if "--alias" in arguments or "-" in values(arguments, "--config-locations"):
        raise SetupError(
            "Aliases and stdin-based settings need manual setup. Use direct options."
        )
    command = [yt_dlp, "--ignore-config", "--verbose", "--no-cache-dir", "--no-update"]
    if "--no-js-runtimes" in arguments:
        command.append("--no-js-runtimes")
    for option, disable in (
        ("--js-runtimes", "--no-js-runtimes"),
        ("--remote-components", "--no-remote-components"),
    ):
        for value in values(arguments, option, disable):
            command.extend((option, value))
    if flatpak and app:
        command = flatpak_command(flatpak, app, command)
    details = parse_diagnostic(context.run(command), destination)
    return Diagnostic(
        tuple(arguments), destination, details.runtimes, details.libraries
    )


def decode_config(data: bytes) -> tuple[str, str]:
    for prefix, decoder, encoder in (
        (codecs.BOM_UTF32_LE, "utf-32", "utf-32-le"),
        (codecs.BOM_UTF32_BE, "utf-32", "utf-32-be"),
        (codecs.BOM_UTF16_LE, "utf-16", "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16", "utf-16-be"),
        (codecs.BOM_UTF8, "utf-8-sig", "utf-8"),
    ):
        if data.startswith(prefix):
            return data.decode(decoder), encoder
    encoding = locale.getpreferredencoding(False)
    declared = re.match(rb"# coding:\s*([\w.-]+)", data)
    if declared:
        encoding = declared[1].decode("ascii")
    try:
        return data.decode(encoding), encoding
    except (UnicodeError, LookupError) as error:
        raise SetupError("Cannot decode a yt-dlp configuration file.") from error


def discover_profiles(context: Context) -> list[Profile]:
    home = context.home
    config = user_config(context).parent.parent
    if context.platform == "win32":
        roaming = Path(context.environ.get("APPDATA", str(home / "AppData/Roaming")))
        local = Path(context.environ.get("LOCALAPPDATA", str(home / "AppData/Local")))
        firefox = [
            ("Firefox", "firefox", roaming / "Mozilla/Firefox"),
            ("Zen", "zen", roaming / "zen"),
        ]
        chromium = [
            ("Chrome", "chrome", local / "Google/Chrome/User Data"),
            ("Edge", "edge", local / "Microsoft/Edge/User Data"),
            ("Brave", "brave", local / "BraveSoftware/Brave-Browser/User Data"),
        ]
    elif context.platform == "darwin":
        support = home / "Library/Application Support"
        firefox = [
            ("Firefox", "firefox", support / "Firefox"),
            ("Zen", "zen", support / "zen"),
        ]
        chromium = [
            ("Chrome", "chrome", support / "Google/Chrome"),
            ("Edge", "edge", support / "Microsoft Edge"),
            ("Brave", "brave", support / "BraveSoftware/Brave-Browser"),
        ]
    else:
        firefox = [
            ("Firefox", "firefox", home / ".mozilla/firefox"),
            (
                "Firefox Flatpak",
                "firefox",
                home / ".var/app/org.mozilla.firefox/.mozilla/firefox",
            ),
            ("Zen", "zen", home / ".zen"),
            ("Zen", "zen", config / "zen"),
            ("Zen Flatpak", "zen", home / ".var/app/app.zen_browser.zen/.zen"),
        ]
        chromium = [
            ("Chrome", "chrome", config / "google-chrome"),
            ("Chromium", "chromium", config / "chromium"),
            ("Edge", "edge", config / "microsoft-edge"),
            ("Brave", "brave", config / "BraveSoftware/Brave-Browser"),
            ("Vivaldi", "vivaldi", config / "vivaldi"),
        ]
    profiles: dict[Path, Profile] = {}
    for label, browser, root in firefox:
        for pattern in ("*/cookies.sqlite", "Profiles/*/cookies.sqlite"):
            for database in sorted(root.glob(pattern)):
                profiles[database] = Profile(
                    f"{label}: {database.parent.name}",
                    browser,
                    database.parent,
                    database,
                )
    for label, browser, root in chromium:
        for pattern in ("*/Cookies", "*/Network/Cookies"):
            for database in sorted(root.glob(pattern)):
                profile = (
                    database.parent.parent
                    if database.parent.name == "Network"
                    else database.parent
                )
                profiles[database] = Profile(
                    f"{label}: {profile.name}", browser, profile, database
                )
    for relative in (
        "Library/Cookies/Cookies.binarycookies",
        "Library/Containers/com.apple.Safari/Data/Library/Cookies/Cookies.binarycookies",
    ):
        safari = home / relative
        if context.platform == "darwin" and safari.is_file():
            profiles[safari] = Profile("Safari", "safari", safari.parent, safari)
    return list(profiles.values())


def cookie_locations(
    context: Context, diagnostic: Diagnostic
) -> list[tuple[Path, Path]]:
    locations: list[tuple[Path, Path]] = []
    if diagnostic.cookies:
        path = expand_path(diagnostic.cookies, context)
        locations.append((path, path))
    if diagnostic.browser:
        name, separator, profile = diagnostic.browser.partition(":")
        name = name.split("+", 1)[0]
        profile = profile.split("::", 1)[0]
        if separator and ("/" in profile or "\\" in profile or profile.startswith("~")):
            path = expand_path(profile, context)
            if name == "safari":
                locations.append((path, path))
                return locations
            database = path / ("cookies.sqlite" if name == "firefox" else "Cookies")
            if name != "firefox" and (path / "Network/Cookies").is_file():
                database = path / "Network/Cookies"
            locations.append((path, database))
        else:
            for candidate in discover_profiles(context):
                if candidate.browser == name and (
                    not profile or candidate.path.name == profile
                ):
                    locations.append((candidate.path, candidate.database))
    return locations


def runtime_candidates(context: Context) -> list[str]:
    candidates: list[tuple[str, Path]] = []
    for kind in ("deno", "node"):
        found = executable(context, kind)
        if found:
            candidates.append((kind, Path(found)))
    for kind, patterns in (
        ("deno", (".deno/bin/deno", ".local/share/mise/installs/deno/*/bin/deno")),
        (
            "node",
            (
                ".local/share/mise/installs/node/*/bin/node",
                ".nvm/versions/node/*/bin/node",
                ".volta/bin/node",
            ),
        ),
    ):
        for pattern in patterns:
            if context.platform == "win32":
                pattern += ".exe"
            candidates.extend((kind, p) for p in sorted(context.home.glob(pattern)))
    valid: list[str] = []
    seen: set[Path] = set()
    for kind, path in candidates:
        if not path.is_file() or not os.access(path, os.X_OK):
            continue
        real = path.resolve()
        if real in seen:
            continue
        seen.add(real)
        try:
            result = context.run([str(path), "--version"])
        except (OSError, subprocess.TimeoutExpired):
            continue
        version = VERSION.search(result.stdout)
        minimum = MINIMUM_RUNTIME[kind]
        if (
            result.returncode == 0
            and version
            and tuple(int(v) for v in version.groups()) >= minimum
        ):
            valid.append(f"{kind}:{path}")
    return valid


def choose(
    context: Context, title: str, choices: Sequence[tuple[str, str]]
) -> str | None:
    context.emit(title)
    for index, (label, _) in enumerate(choices, 1):
        context.emit(f"  {index}. {label}")
    answer = context.ask(
        "Choose a number, enter a specification, or press Enter to skip: "
    ).strip()
    if not answer:
        return None
    if answer.isdigit():
        index = int(answer) - 1
        if 0 <= index < len(choices):
            return choices[index][1]
        context.emit("Selection was outside the available choices.")
        return None
    return answer


def confirm(context: Context, description: str) -> bool:
    context.emit(description)
    return context.ask("Apply this remedy? [y/N] ").strip().lower() in ("y", "yes")


def append_config(
    context: Context, path: Path, additions: Sequence[tuple[str, str | None]]
) -> bool:
    original_data = path.read_bytes() if path.exists() else b""
    original, encoding = decode_config(original_data)
    tokens = shlex.split(original, comments=True)
    disables = {
        "--cookies-from-browser": "--no-cookies-from-browser",
        "--js-runtimes": "--no-js-runtimes",
        "--remote-components": "--no-remote-components",
    }
    additions = [
        (option, value)
        for option, value in additions
        if value is None
        or (
            value not in values(tokens, option, disables.get(option, ""))
            if option in ("--remote-components", "--config-locations")
            else value != setting(tokens, option, disables.get(option, ""))
        )
    ]
    if not additions:
        return False
    lines = [
        option + (" " + shlex.quote(value) if value is not None else "")
        for option, value in additions
    ]
    if not confirm(context, f"Update {path}:\n" + "\n".join(lines)):
        return False
    current = path.read_bytes() if path.exists() else b""
    if current != original_data:
        raise SetupError(f"{path} changed during configuration; rerun setup.")
    path.parent.mkdir(parents=True, exist_ok=True)
    addition = "\n" if original and not original.endswith("\n") else ""
    addition += "\n".join(lines) + "\n"
    try:
        encoded = addition.encode(encoding)
    except UnicodeError as error:
        raise SetupError(
            f"Cannot represent the change in {encoding}; update {path} encoding first."
        ) from error
    with path.open("ab") as output:
        output.write(encoded)
    return True


def host_problems(context: Context, state: Diagnostic) -> list[str]:
    problems: list[str] = []
    if not state.browser and not state.cookies:
        problems.append("No browser cookie source is configured.")
    else:
        locations = cookie_locations(context, state)
        if not locations or not all(
            p.is_file() and os.access(p, os.R_OK) for _, p in locations
        ):
            problems.append(
                "Cannot read the cookie source. Check its profile or file path."
            )
    if not state.runtime_ready:
        problems.append("No JavaScript runtime is enabled and available to yt-dlp.")
    if not state.solver_ready:
        problems.append("EJS solver scripts are not installed or enabled for download.")
    return problems


def configure_host(
    context: Context,
    yt_dlp: str,
    state: Diagnostic,
    *,
    browser: str | None,
    runtime: str | None,
) -> tuple[Diagnostic, list[str]]:
    problems: list[str] = []
    locations = cookie_locations(context, state)
    if (
        browser
        or not (state.browser or state.cookies)
        or not locations
        or not all(p.is_file() for _, p in locations)
    ):
        selected = browser or choose(
            context,
            "Select the browser profile containing your login:",
            [(p.label, p.spec) for p in discover_profiles(context)],
        )
        if selected:
            proposed = Diagnostic(
                ("--cookies-from-browser", selected),
                state.config,
                state.runtimes,
                state.libraries,
            )
            found = cookie_locations(context, proposed)
            reader = selected.split(":", 1)[0].split("+", 1)[0]
            if (
                reader not in BROWSER_READERS
                or not found
                or not all(p.is_file() and os.access(p, os.R_OK) for _, p in found)
            ):
                problems.append("Selected browser has no readable database; not saved.")
                selected = None
        if selected:
            additions: list[tuple[str, str | None]] = []
            if state.cookies:
                additions.append(("--no-cookies", None))
            additions.append(("--cookies-from-browser", selected))
            append_config(context, state.config, additions)
    if runtime or not state.runtime_ready:
        selected = runtime or choose(
            context,
            "Select a supported installed Deno or Node runtime:",
            [(value, value) for value in runtime_candidates(context)],
        )
        if selected:
            kind, _, value = selected.partition(":")
            path = (
                expand_path(value, context)
                if value
                else Path(executable(context, kind) or "/missing-runtime")
            )
            if (
                kind not in MINIMUM_RUNTIME
                or not path.is_file()
                or not os.access(path, os.X_OK)
            ):
                problems.append(
                    "Selected runtime is not a supported executable; not saved."
                )
            else:
                result = context.run([str(path), "--version"])
                version = VERSION.search(result.stdout)
                if (
                    result.returncode
                    or not version
                    or tuple(int(v) for v in version.groups()) < MINIMUM_RUNTIME[kind]
                ):
                    problems.append(
                        "Selected runtime version is unsupported; not saved."
                    )
                else:
                    append_config(
                        context, state.config, [("--js-runtimes", f"{kind}:{path}")]
                    )
    if not state.solver_ready:
        context.emit(
            "Allow yt-dlp to fetch its official EJS solver scripts from GitHub."
        )
        append_config(context, state.config, [("--remote-components", "ejs:github")])
    return inspect(context, yt_dlp), problems


def app_shell(
    context: Context, flatpak: str, app: str, script: str, value: str = ""
) -> subprocess.CompletedProcess[str]:
    return context.run(flatpak_command(flatpak, app, ["sh", "-c", script, "--", value]))


def configure_flatpak(
    context: Context,
    flatpak: str,
    app: str,
    yt_dlp: str,
    host: Diagnostic,
    tools: Mapping[str, str],
    check_only: bool,
) -> list[str]:
    environment = app_shell(
        context, flatpak, app, 'printf "%s\\n" "$XDG_CONFIG_HOME" "$PATH"'
    )
    values = environment.stdout.splitlines()
    if environment.returncode or len(values) < 2 or not values[0]:
        return [f"Cannot inspect the {app} Flatpak environment."]
    app_config = Path(values[0]) / "yt-dlp/config"
    app_path = values[1]
    state = inspect(context, yt_dlp, flatpak=flatpak, app=app, config=app_config)
    changed_permissions = False
    if (
        (
            (not state.browser and not state.cookies)
            or not state.runtime_ready
            or not state.solver_ready
        )
        and not check_only
        and app_config != host.config
    ):
        append_config(context, app_config, [("--config-locations", str(host.config))])
        state = inspect(context, yt_dlp, flatpak=flatpak, app=app, config=app_config)
    problems: list[str] = []
    if not state.browser and not state.cookies:
        problems.append(f"{app}: yt-dlp cannot discover a configured cookie source.")
    if not state.runtime_ready:
        problems.append(f"{app}: no enabled JavaScript runtime is accessible.")
    if not state.solver_ready:
        problems.append(f"{app}: EJS solver scripts are unavailable.")
    locations = cookie_locations(context, state)
    if (state.browser or state.cookies) and not locations:
        problems.append(f"{app}: cannot identify the configured cookie database.")
    for location, database in locations:
        readable = app_shell(context, flatpak, app, 'test -r "$1"', str(database))
        if readable.returncode:
            command = [
                flatpak,
                "override",
                "--user",
                f"--filesystem={location}:ro",
                app,
            ]
            if not check_only and confirm(
                context, "Grant read-only cookie-source access:\n" + shlex.join(command)
            ):
                result = context.run(command)
                if result.returncode:
                    raise SetupError(f"Flatpak could not grant access to {location}.")
                changed_permissions = True
                readable = app_shell(
                    context, flatpak, app, 'test -r "$1"', str(database)
                )
            if readable.returncode:
                problems.append(f"{app}: cookie source is inaccessible at {database}.")
    missing: list[str] = []
    directories: list[str] = []
    for name, path in tools.items():
        found = app_shell(context, flatpak, app, 'command -v "$1"', name)
        if not found.returncode and name != "yt-dlp":
            command = flatpak_command(flatpak, app, [found.stdout.strip(), "-version"])
            if context.run(command).returncode:
                problems.append(
                    f"{app}: {name} cannot execute; repair its installation."
                )
        if found.returncode:
            accessible = app_shell(context, flatpak, app, 'test -x "$1"', path)
            if accessible.returncode:
                problems.append(f"{app}: install {name} in an accessible location.")
            else:
                missing.append(name)
                directory = str(Path(path).parent)
                if (
                    directory not in app_path.split(":")
                    and directory not in directories
                ):
                    directories.append(directory)
    if directories:
        updated_path = ":".join([*directories, app_path])
        command = [flatpak, "override", "--user", f"--env=PATH={updated_path}", app]
        if not check_only and confirm(
            context,
            "Add existing tool directories to the Flatpak PATH:\n"
            + shlex.join(command),
        ):
            if context.run(command).returncode:
                raise SetupError(f"Flatpak could not update PATH for {app}.")
            changed_permissions = True
    for name in missing:
        if app_shell(context, flatpak, app, 'command -v "$1"', name).returncode:
            problems.append(f"{app}: {name} is not on PATH.")
    if changed_permissions:
        context.emit(
            f"Restart {app} to apply changed permissions or PATH to existing processes."
        )
    return problems


def probe(
    context: Context,
    yt_dlp: str,
    url: str,
    *,
    flatpak: str | None,
    app: str | None,
    state: Diagnostic,
) -> bool:
    command = [
        yt_dlp,
        "--ignore-config",
        "--simulate",
        "--dump-single-json",
        "--skip-download",
        "--no-playlist",
        "--no-progress",
        "--no-cache-dir",
    ]
    read_options = {
        "--cookies-from-browser": "--no-cookies-from-browser",
        "--js-runtimes": "--no-js-runtimes",
        "--remote-components": "--no-remote-components",
        "--proxy": "",
        "--socket-timeout": "",
        "--user-agent": "",
        "--referer": "",
        "--add-headers": "",
        "--extractor-args": "",
        "--source-address": "",
        "--impersonate": "",
        "--format": "",
        "--format-sort": "",
        "--match-filters": "",
    }
    if "--no-js-runtimes" in state.arguments:
        command.append("--no-js-runtimes")
    for option, disable in read_options.items():
        for value in values(state.arguments, option, disable):
            command.extend((option, value))
    for flag in ("--force-ipv4", "--force-ipv6", "--legacy-server-connect"):
        if flag in state.arguments:
            command.append(flag)
    directory = context.home / ".var/app" / app / "cache" if app else context.home
    with tempfile.TemporaryDirectory(
        prefix="yt-dlp-check-", dir=directory
    ) as workspace:
        if state.cookies:
            source = expand_path(state.cookies, context)
            copy = Path(workspace) / "cookies.txt"
            if flatpak and app:
                result = context.run(
                    flatpak_command(flatpak, app, ["cp", "--", str(source), str(copy)])
                )
                if result.returncode:
                    raise SetupError(
                        "Cannot isolate the cookie file for a read-only check."
                    )
            else:
                shutil.copyfile(source, copy)
            copy.chmod(0o600)
            command.extend(("--cookies", str(copy)))
        command.extend(("--", url))
        if flatpak and app:
            command = flatpak_command(flatpak, app, command)
        result = context.run(command)
    if result.returncode:
        context.emit(
            "YouTube access failed. Check the browser login and source availability."
        )
        for line in result.stderr.splitlines():
            if line.startswith("ERROR:"):
                context.emit(re.sub(r"https?://\S+", "<URL>", line))
        return False
    try:
        parsed: object = json.loads(result.stdout)
    except ValueError as error:
        raise SetupError("YouTube access check returned invalid metadata.") from error
    if (
        not isinstance(parsed, dict)
        or not isinstance(parsed.get("formats"), list)
        or not parsed["formats"]
    ):
        context.emit("YouTube access check returned no usable media formats.")
        return False
    context.emit("YouTube access passed. No media downloaded or metadata retained.")
    return True


def configure(
    context: Context,
    *,
    check_only: bool = False,
    url: str | None = None,
    flatpak_app: str | None = None,
    browser: str | None = None,
    runtime: str | None = None,
    native_only: bool = False,
) -> int:
    tools: dict[str, str] = {}
    problems: list[str] = []
    for name in ("yt-dlp", "ffmpeg", "ffprobe"):
        path = executable(context, name)
        if not path:
            problems.append(
                f"Install {name} or add its directory to PATH, then rerun setup."
            )
        else:
            tools[name] = path
            if name != "yt-dlp" and context.run([path, "-version"]).returncode:
                problems.append(
                    f"{name} cannot execute. Repair its installation and rerun setup."
                )
    if "yt-dlp" not in tools:
        for problem in problems:
            context.emit(problem)
        return 1
    state = inspect(context, tools["yt-dlp"])
    context.emit(f"yt-dlp configuration: {state.config}")
    if not check_only:
        state, selection_problems = configure_host(
            context, tools["yt-dlp"], state, browser=browser, runtime=runtime
        )
        problems.extend(selection_problems)
    problems.extend(host_problems(context, state))
    flatpak = executable(context, "flatpak")
    app = flatpak_app
    probe_executable = tools["yt-dlp"]
    if flatpak and not native_only:
        candidate = app or "md.obsidian.Obsidian"
        if context.run([flatpak, "info", candidate]).returncode == 0:
            app = candidate
            found = app_shell(context, flatpak, app, 'command -v "$1"', "yt-dlp")
            probe_executable = (
                found.stdout.strip() if not found.returncode else tools["yt-dlp"]
            )
            if app_shell(
                context, flatpak, app, 'test -x "$1"', probe_executable
            ).returncode:
                problems.append(
                    f"{app}: yt-dlp is not installed in an accessible location."
                )
            else:
                problems.extend(
                    configure_flatpak(
                        context,
                        flatpak,
                        app,
                        probe_executable,
                        state,
                        tools,
                        check_only,
                    )
                )
        elif app:
            problems.append(f"Flatpak application {app} is not installed.")
    elif app:
        problems.append(
            "The requested Flatpak target cannot be checked without flatpak."
        )
    for problem in problems:
        context.emit(problem)
    if problems:
        context.emit("Setup is incomplete. Resolve the reported issues and rerun.")
        return 1
    if url:
        probe_state = (
            inspect(context, probe_executable, flatpak=flatpak, app=app)
            if app
            else state
        )
        if not probe(
            context, probe_executable, url, flatpak=flatpak, app=app, state=probe_state
        ):
            return 1
    context.emit(
        "Configuration checks passed."
        + ("" if url else " YouTube access was not tested; use --url to test a video.")
    )
    return 0


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report problems without prompts or configuration changes.",
    )
    parser.add_argument(
        "--url", help="Test access to one YouTube video without downloading media."
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "--flatpak-app",
        help="Check a Flatpak app; installed Obsidian is detected by default.",
    )
    target.add_argument(
        "--native-only", action="store_true", help="Check only the host environment."
    )
    parser.add_argument(
        "--browser", help="Propose a yt-dlp browser/profile specification."
    )
    parser.add_argument(
        "--runtime",
        help="Propose a JavaScript runtime, such as node:/absolute/path/to/node.",
    )
    options = parser.parse_args(arguments)
    if not options.check and not sys.stdin.isatty():
        parser.error("Run in an interactive terminal, or use --check for diagnostics.")
    if Path("/.flatpak-info").exists() and not options.check:
        parser.error("Run configuration from a host terminal, outside Flatpak.")
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    def run(command: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            env=environment,
            timeout=120,
            check=False,
        )

    context = Context(
        Path.home(), sys.platform, environment, run, shutil.which, input, print
    )
    try:
        return configure(
            context,
            check_only=options.check,
            url=options.url,
            flatpak_app=options.flatpak_app,
            native_only=options.native_only,
            browser=options.browser,
            runtime=options.runtime,
        )
    except subprocess.TimeoutExpired:
        print("A setup command timed out; rerun the check.", file=sys.stderr)
        return 1
    except (SetupError, OSError, EOFError) as error:
        print(f"Setup could not finish: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(
            "\nSetup interrupted. Previously approved changes remain applied.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
