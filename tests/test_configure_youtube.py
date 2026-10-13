from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.configure_youtube import Context, configure, discover_profiles, inspect


class Machine:
    def __init__(self, home: Path, *, flatpak: bool = False) -> None:
        self.home = home
        self.config = home / ".config/yt-dlp/config"
        self.app_config = home / ".var/app/md.obsidian.Obsidian/config/yt-dlp/config"
        self.flatpak = flatpak
        self.profile_readable = not flatpak
        self.app_path = "/usr/bin:/app/bin"
        self.calls: list[list[str]] = []
        self.probe_failure = False
        self.solver_installed = False
        self.node_version = "24.0.0"
        self.app_yt_dlp: str | None = None
        self.app_media_failure = False
        self.write_side_effects = False
        self.tools = {
            name: f"/tools/{name}" for name in ("yt-dlp", "ffmpeg", "ffprobe")
        }
        self.tools["node"] = str(home / ".local/bin/node")
        node = Path(self.tools["node"])
        node.parent.mkdir(parents=True)
        node.write_text("fixture")
        node.chmod(0o755)
        if flatpak:
            self.tools["flatpak"] = "/tools/flatpak"
        self.output: list[str] = []
        self.answers: list[str] = []
        self.prompts: list[str] = []
        self.profile = home / ".var/app/app.zen_browser.zen/.zen/example.default"
        self.profile.mkdir(parents=True)
        (home / ".var/app/md.obsidian.Obsidian/cache").mkdir(parents=True)
        (self.profile / "cookies.sqlite").write_text("fixture")

    def context(self) -> Context:
        return Context(
            self.home,
            "linux",
            {},
            self.run,
            self.tools.get,
            self.ask,
            self.output.append,
        )

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.answers.pop(0) if self.answers else ""

    def write(self, text: str, *, app: bool = False) -> None:
        path = self.app_config if app else self.config
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def ready(self) -> None:
        self.write(
            f'--cookies-from-browser "firefox:{self.profile}"\n'
            f'--js-runtimes "node:{self.tools["node"]}"\n'
            "--remote-components ejs:github\n"
        )

    def run(self, arguments: list[str]) -> subprocess.CompletedProcess[str]:
        self.calls.append(arguments)
        app = "run" in arguments and "md.obsidian.Obsidian" in arguments
        code, out, err = 0, "", ""
        if arguments[0].endswith("flatpak") and "info" in arguments:
            code = 0 if self.flatpak else 1
        elif arguments[0].endswith("flatpak") and "override" in arguments:
            for arg in arguments:
                if arg.startswith("--filesystem="):
                    self.profile_readable = True
                if arg.startswith("--env=PATH="):
                    self.app_path = arg.removeprefix("--env=PATH=")
        elif "--command=cp" in arguments:
            shutil.copyfile(arguments[-2], arguments[-1])
        elif "-c" in arguments:
            script = arguments[arguments.index("-c") + 1]
            value = arguments[-1]
            if "XDG_CONFIG_HOME" in script:
                out = str(self.app_config.parent.parent) + "\n" + self.app_path
            elif "command -v" in script:
                if value in ("ffmpeg", "ffprobe"):
                    out = "/usr/bin/" + value + "\n"
                elif value == "yt-dlp" and "/tools" in self.app_path.split(":"):
                    out = "/tools/yt-dlp\n"
                elif value == "yt-dlp" and self.app_yt_dlp:
                    out = self.app_yt_dlp + "\n"
                else:
                    code = 1
            elif "test -r" in script:
                code = 0 if self.profile_readable else 1
            elif "test -x" in script:
                code = 0
        elif "--dump-single-json" in arguments:
            code = 1 if self.probe_failure else 0
            out = json.dumps({"id": "example", "formats": [{"url": "secret"}]})
            err = "ERROR: test failure https://example.com/?token=secret"
            if self.write_side_effects and "--ignore-config" not in arguments:
                (self.home / "unwanted-info.json").write_text("unwanted")
            if "--cookies" in arguments:
                Path(arguments[arguments.index("--cookies") + 1]).write_text(
                    "rewritten"
                )
        elif "--verbose" in arguments:
            file = self.app_config if app else self.config
            groups = [f"[debug] Command-line config: {arguments!r}"]
            args: list[str] = []
            if file.exists() and "--ignore-config" not in arguments:
                data = file.read_bytes()
                text = data.decode(
                    "utf-16" if data.startswith(b"\xff\xfe") else "utf-8"
                )
                args = shlex.split(text, comments=True)
                if (
                    self.write_side_effects
                    and "--no-cookies" not in arguments
                    and "--ignore-config" not in arguments
                    and "--cookies" in args
                    and "--help" not in arguments
                ):
                    Path(args[args.index("--cookies") + 1]).write_text("rewritten")
                groups.append(f'[debug] User config "{file}": {args!r}')
                if "--config-locations" in args:
                    args = shlex.split(self.config.read_text(), comments=True)
                    groups.append(f'[debug] | Config "{self.config}": {args!r}')
            if "--ignore-config" in arguments:
                args = arguments
                groups = [f"[debug] Command-line config: {arguments!r}"]
            node_enabled = "--js-runtimes" in args
            groups.append(
                "[debug] JS runtimes: "
                + (f"node-{self.node_version}" if node_enabled else "none")
            )
            groups.append(
                "[debug] Optional libraries: "
                + ("yt_dlp_ejs-0.8.0" if self.solver_installed else "sqlite3-3.0")
            )
            err = "\n".join(groups)
            code = 0 if "--help" in arguments else 2
        elif arguments[-1] == "--version":
            out = f"v{self.node_version}\n"
        elif arguments[-1] == "-version":
            out = "ffmpeg version 8.0\n"
            code = 1 if app and self.app_media_failure else 0
        return subprocess.CompletedProcess(arguments, code, out, err)


class ConfigureYoutubeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.machine = Machine(Path(self.temp.name))

    def test_check_reports_missing_setup_without_writes_or_prompts(self) -> None:
        self.assertEqual(configure(self.machine.context(), check_only=True), 1)
        self.assertFalse(self.machine.config.exists())
        self.assertFalse(self.machine.prompts)

    def test_declined_remedies_leave_existing_config_unchanged(self) -> None:
        text = '--output "my videos/%(title)s.%(ext)s"\n'
        self.machine.write(text)
        self.machine.answers = ["1", "n", "1", "n", "n"]
        self.assertEqual(configure(self.machine.context()), 1)
        self.assertEqual(self.machine.config.read_text(), text)

    def test_accepted_configuration_preserves_options_and_repeat_run_is_quiet(
        self,
    ) -> None:
        text = '--output "my videos/%(title)s.%(ext)s"\n'
        self.machine.write(text)
        self.machine.answers = ["1", "y", "1", "y", "y"]
        self.assertEqual(configure(self.machine.context()), 0)
        configured = self.machine.config.read_text()
        self.assertIn(text, configured)
        self.assertIn(str(self.machine.profile), configured)
        self.assertIn("--remote-components ejs:github", configured)
        self.machine.prompts.clear()
        self.assertEqual(configure(self.machine.context()), 0)
        self.assertEqual(self.machine.config.read_text(), configured)
        self.assertFalse(self.machine.prompts)

    def test_existing_credentials_and_installed_solver_need_no_selection(self) -> None:
        self.machine.ready()
        self.machine.solver_installed = True
        self.assertEqual(configure(self.machine.context(), check_only=True), 0)
        self.assertFalse(self.machine.prompts)

    def test_browser_discovery_distinguishes_zen_from_native_firefox(self) -> None:
        native = self.machine.home / ".mozilla/firefox/native.default"
        native.mkdir(parents=True)
        (native / "cookies.sqlite").write_text("fixture")
        profiles = discover_profiles(self.machine.context())
        self.assertEqual({p.path for p in profiles}, {native, self.machine.profile})
        self.assertTrue(all(p.spec.startswith("firefox:") for p in profiles))

    def test_flatpak_accepts_only_configuration_permission_and_path_remedies(
        self,
    ) -> None:
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.machine.profile_readable = False
        self.machine.ready()
        self.machine.answers = ["y", "y", "y"]
        self.assertEqual(configure(self.machine.context()), 0)
        self.assertIn("--config-locations", self.machine.app_config.read_text())
        overrides = [
            a
            for call in self.machine.calls
            for a in call
            if a.startswith("--filesystem=")
        ]
        self.assertEqual(overrides, [f"--filesystem={self.machine.profile}:ro"])
        self.assertIn("/tools", self.machine.app_path.split(":"))
        self.assertTrue(any("Restart" in line for line in self.machine.output))

    def test_flatpak_check_does_not_change_missing_permissions_or_path(self) -> None:
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.machine.profile_readable = False
        self.machine.ready()
        self.assertEqual(configure(self.machine.context(), check_only=True), 1)
        self.assertFalse(self.machine.app_config.exists())
        self.assertFalse(any("override" in call for call in self.machine.calls))

    def test_failed_url_probe_reports_failure_without_exposing_signed_urls(
        self,
    ) -> None:
        self.machine.ready()
        self.machine.probe_failure = True
        self.assertEqual(
            configure(
                self.machine.context(),
                check_only=True,
                url="https://www.youtube.com/watch?v=example",
            ),
            1,
        )
        self.assertNotIn("token=secret", "\n".join(self.machine.output))
        probe = next(
            call for call in self.machine.calls if "--dump-single-json" in call
        )
        self.assertIn("--skip-download", probe)
        self.assertIn("--no-cache-dir", probe)

    def test_missing_media_tool_is_a_blocker(self) -> None:
        self.machine.ready()
        del self.machine.tools["ffprobe"]
        self.assertEqual(configure(self.machine.context(), check_only=True), 1)

    def test_unsupported_configured_node_is_not_reported_as_ready(self) -> None:
        self.machine.ready()
        self.machine.node_version = "18.0.0"
        self.assertEqual(configure(self.machine.context(), check_only=True), 1)

    def test_invalid_explicit_selections_are_not_saved(self) -> None:
        self.machine.ready()
        original = self.machine.config.read_text()
        self.machine.answers = ["y", "y"]
        self.assertEqual(
            configure(
                self.machine.context(),
                browser="unknown:/missing",
                runtime="node:/missing",
            ),
            1,
        )
        self.assertEqual(self.machine.config.read_text(), original)

    def test_multiple_remote_solver_sources_preserve_github_support(self) -> None:
        self.machine.ready()
        with self.machine.config.open("a") as output:
            output.write("--remote-components ejs:npm\n")
        self.assertEqual(configure(self.machine.context(), check_only=True), 0)

    def test_existing_cookie_file_needs_no_browser_prompt(self) -> None:
        cookie_file = self.machine.home / "cookies.txt"
        cookie_file.write_text("fixture")
        self.machine.write(
            f'--cookies "{cookie_file}"\n'
            f'--js-runtimes "node:{self.machine.tools["node"]}"\n'
            "--remote-components ejs:github\n"
        )
        self.assertEqual(configure(self.machine.context()), 0)
        self.assertFalse(self.machine.prompts)

    def test_repeating_explicit_selections_does_not_duplicate_settings(self) -> None:
        self.machine.ready()
        original = self.machine.config.read_text()
        self.machine.answers = ["y", "y"]
        self.assertEqual(
            configure(
                self.machine.context(),
                browser=f"firefox:{self.machine.profile}",
                runtime=f"node:{self.machine.tools['node']}",
            ),
            0,
        )
        self.assertEqual(self.machine.config.read_text(), original)
        self.assertFalse(self.machine.prompts)

    def test_safari_selection_uses_the_cookie_file(self) -> None:
        database = self.machine.home / "Library/Cookies/Cookies.binarycookies"
        database.parent.mkdir(parents=True)
        database.write_text("fixture")
        old = self.machine.context()
        context = Context(
            old.home, "darwin", old.environ, old.run, old.resolve, old.ask, old.emit
        )
        safari = next(p for p in discover_profiles(context) if p.browser == "safari")
        self.assertEqual(safari.spec, f"safari:{database}")

    def test_unknown_browser_reader_is_not_saved_even_if_database_exists(self) -> None:
        self.machine.ready()
        (self.machine.profile / "Cookies").write_text("fixture")
        original = self.machine.config.read_text()
        self.machine.answers = ["y"]
        self.assertEqual(
            configure(
                self.machine.context(), browser=f"unsupported:{self.machine.profile}"
            ),
            1,
        )
        self.assertEqual(self.machine.config.read_text(), original)

    def test_native_only_skips_installed_flatpak(self) -> None:
        self.machine.ready()
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.assertEqual(
            configure(self.machine.context(), check_only=True, native_only=True), 0
        )
        self.assertFalse(any("run" in command for command in self.machine.calls))

    def test_flatpak_probe_uses_its_own_yt_dlp_executable(self) -> None:
        self.machine.ready()
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.machine.app_yt_dlp = "/app/bin/yt-dlp"
        self.machine.write(f'--config-locations "{self.machine.config}"\n', app=True)
        self.assertEqual(
            configure(
                self.machine.context(),
                check_only=True,
                url="https://www.youtube.com/watch?v=example",
            ),
            0,
        )
        probe = next(
            call for call in self.machine.calls if "--dump-single-json" in call
        )
        self.assertIn("--command=/app/bin/yt-dlp", probe)

    def test_flatpak_media_command_execution_failure_is_a_blocker(self) -> None:
        self.machine.ready()
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.machine.app_yt_dlp = "/app/bin/yt-dlp"
        self.machine.app_media_failure = True
        self.machine.write(f'--config-locations "{self.machine.config}"\n', app=True)
        self.assertEqual(configure(self.machine.context(), check_only=True), 1)

    def test_check_does_not_rewrite_a_configured_cookie_file(self) -> None:
        cookie = self.machine.home / "login.txt"
        cookie.write_text("original fixture")
        self.machine.write(
            f'--cookies "{cookie}"\n'
            f'--js-runtimes "node:{self.machine.tools["node"]}"\n'
            "--remote-components ejs:github\n"
        )
        self.machine.write_side_effects = True
        self.assertEqual(
            configure(
                self.machine.context(),
                check_only=True,
                url="https://www.youtube.com/watch?v=example",
            ),
            0,
        )
        self.assertEqual(cookie.read_text(), "original fixture")
        self.assertEqual(list(self.machine.home.glob("yt-dlp-check-*")), [])

    def test_flatpak_cookie_file_probe_preserves_the_source_and_cleans_copy(
        self,
    ) -> None:
        cookie = self.machine.home / "login.txt"
        cookie.write_text("original fixture")
        self.machine.write(
            f'--cookies "{cookie}"\n'
            f'--js-runtimes "node:{self.machine.tools["node"]}"\n'
            "--remote-components ejs:github\n"
        )
        self.machine.flatpak = True
        self.machine.tools["flatpak"] = "/tools/flatpak"
        self.machine.app_yt_dlp = "/app/bin/yt-dlp"
        self.machine.write(f'--config-locations "{self.machine.config}"\n', app=True)
        self.assertEqual(
            configure(
                self.machine.context(),
                check_only=True,
                url="https://www.youtube.com/watch?v=example",
            ),
            0,
        )
        self.assertEqual(cookie.read_text(), "original fixture")
        cache = self.machine.home / ".var/app/md.obsidian.Obsidian/cache"
        self.assertEqual(list(cache.glob("yt-dlp-check-*")), [])

    def test_probe_cannot_inherit_output_hooks_or_disable_simulation(self) -> None:
        self.machine.ready()
        with self.machine.config.open("a") as output:
            output.write('--no-simulate\n--write-info-json\n--exec "touch unwanted"\n')
        self.machine.write_side_effects = True
        self.assertEqual(
            configure(
                self.machine.context(),
                check_only=True,
                url="https://www.youtube.com/watch?v=example",
            ),
            0,
        )
        self.assertFalse((self.machine.home / "unwanted-info.json").exists())

    def test_browser_can_return_to_an_earlier_profile(self) -> None:
        self.machine.ready()
        other = self.machine.home / "other"
        other.mkdir()
        (other / "cookies.sqlite").write_text("fixture")
        with self.machine.config.open("a") as output:
            output.write(f'--cookies-from-browser "firefox:{other}"\n')
        self.machine.answers = ["y"]
        self.assertEqual(
            configure(
                self.machine.context(), browser=f"firefox:{self.machine.profile}"
            ),
            0,
        )
        tokens = shlex.split(self.machine.config.read_text())
        self.assertEqual(tokens[-1], f"firefox:{self.machine.profile}")

    def test_utf16_configuration_keeps_existing_encoding_and_options(self) -> None:
        original = (
            f'--cookies-from-browser "firefox:{self.machine.profile}"\n'
            f'--js-runtimes "node:{self.machine.tools["node"]}"\n'
            '--output "my videos/%(title)s.%(ext)s"\n'
        )
        self.machine.config.parent.mkdir(parents=True)
        self.machine.config.write_bytes(original.encode("utf-16"))
        self.machine.answers = ["y"]
        self.assertEqual(configure(self.machine.context()), 0)
        changed = self.machine.config.read_bytes().decode("utf-16")
        self.assertTrue(changed.startswith(original))
        self.assertIn("--remote-components ejs:github", changed)

    @unittest.skipUnless(shutil.which("yt-dlp"), "yt-dlp is not installed")
    def test_real_diagnostic_cannot_execute_saved_hooks_or_save_cookies(self) -> None:
        cookie = self.machine.home / "login.txt"
        original = (
            "# Netscape HTTP Cookie File\n"
            ".example.com\tTRUE\t/\tFALSE\t0\tfixture\tvalue\n"
        )
        cookie.write_text(original)
        marker = self.machine.home / "unwanted"
        self.machine.write(
            f'--cookies "{cookie}"\n'
            f'--exec "touch {marker}"\n--no-simulate\n'
            f'--print-to-file "%(id)s" "{marker}"\n'
        )
        environment = dict(os.environ)
        environment["XDG_CONFIG_HOME"] = str(self.machine.home / ".config")
        environment["PYTHONDONTWRITEBYTECODE"] = "1"

        def run(command: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                env=environment,
                check=False,
                timeout=30,
            )

        context = Context(
            self.machine.home,
            "linux",
            environment,
            run,
            shutil.which,
            self.machine.ask,
            self.machine.output.append,
        )
        tool = shutil.which("yt-dlp")
        assert tool is not None
        state = inspect(context, tool)
        self.assertEqual(state.cookies, str(cookie))
        self.assertEqual(cookie.read_text(), original)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
