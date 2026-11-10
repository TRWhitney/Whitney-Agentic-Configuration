"""Native filesystem permission profiles and preflight isolation checks."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


class RuntimeIsolation:
    def __init__(
        self,
        base: Path,
        *,
        workspace: Path | None = None,
        home: Path | None = None,
        read_only: bool = False,
    ) -> None:
        from openai_codex.client import _installed_codex_path

        self.base = base.resolve()
        self.workspace = workspace or self.base
        self.home = home or self.base / "runtime"
        self.scratch = self.base / "scratch"
        self.scratch.mkdir(exist_ok=True)
        self.native = _installed_codex_path()
        self.read_only = read_only
        filesystem = {
            ":minimal": "read",
            ":workspace_roots": "read" if read_only else "write",
            str(self.native): "read",
            sys.prefix: "read",
            sys.base_prefix: "read",
            str(self.home / "AGENTS.md"): "read",
            str(self.home / "skills"): "read",
            str(self.home / "bin"): "read",
            str(self.home / "work-system"): "write",
            str(self.base / "account"): "write",
            str(self.base / "evidence"): "read" if read_only else "write",
            str(self.scratch): "write",
        }
        if (self.workspace / ".git").is_dir():
            filesystem[str(self.workspace / ".git")] = "read" if read_only else "write"
        if (self.base / "origin.git").exists():
            filesystem[str(self.base / "origin.git")] = "read" if read_only else "write"
        filesystem = {
            path: mode
            for path, mode in filesystem.items()
            if path.startswith(":") or Path(path).exists()
        }
        table = (
            "{"
            + ",".join(
                json.dumps(path) + "=" + json.dumps(mode)
                for path, mode in filesystem.items()
            )
            + "}"
        )
        self.overrides = (
            'default_permissions="eval"',
            "permissions.eval.filesystem=" + table,
            "permissions.eval.network.enabled=false",
        )

    def command(self, arguments: list[str], *, cwd: Path) -> list[str]:
        command = [str(self.native)]
        for override in self.overrides:
            command.extend(["--config", override])
        return [*command, "sandbox", "-P", "eval", "-C", str(cwd), "--", *arguments]

    def verify(self, environment: dict[str, str] | None = None) -> None:
        private_case = (
            Path(__file__).resolve().parent
            / "cases/interactive-prototype-comparison.json"
        )
        with (
            tempfile.TemporaryDirectory(prefix="outside-attempt-") as foreign,
            socket.socket() as listener,
        ):
            sentinel = Path(foreign) / "input.txt"
            sentinel.write_text("another attempt")
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            script = """from pathlib import Path
import socket
import sys
assert not Path(sys.argv[1]).exists()
assert not Path(sys.argv[2]).exists()
Path(sys.argv[3]).write_text("isolated")
if sys.argv[5]:
    Path(sys.argv[5]).write_text("git metadata probe")
    Path(sys.argv[5]).unlink()
try:
    connection = socket.socket()
    connection.connect(("127.0.0.1", int(sys.argv[4])))
except OSError:
    pass
else:
    raise AssertionError("tool network accessible")
"""
            result = subprocess.run(
                self.command(
                    [
                        sys.executable,
                        "-c",
                        script,
                        str(sentinel),
                        str(private_case),
                        str(self.scratch / "runtime-probe"),
                        str(listener.getsockname()[1]),
                        str(self.workspace / ".git/isolation-probe")
                        if not self.read_only and (self.workspace / ".git").is_dir()
                        else "",
                    ],
                    cwd=self.workspace,
                ),
                env={**(environment or os.environ), "TMPDIR": str(self.scratch)},
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode:
                raise ValueError(
                    "Native isolation probe failed: " + result.stderr[-1000:]
                )
            if (self.scratch / "runtime-probe").read_text() != "isolated":
                raise ValueError(
                    "Native isolation probe did not write its private scratch file."
                )
            (self.scratch / "runtime-probe").unlink()
