"""Real browser observations, kept separate from the candidate's verification."""

from __future__ import annotations

import base64
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from evals.fixtures import Workspace

PNG_PREFIX = "data:image/png;base64,"


def browser_environment() -> dict[str, str]:
    environment = dict(os.environ)
    package = environment.get("EVAL_PLAYWRIGHT_MODULE")
    executable = environment.get("EVAL_BROWSER_EXECUTABLE")
    caches = [
        Path.home() / ".cache/ms-playwright",
        Path.home() / "Library/Caches/ms-playwright",
    ]
    if environment.get("LOCALAPPDATA"):
        caches.append(Path(environment["LOCALAPPDATA"]) / "ms-playwright")
    if not package:
        for cache in caches:
            for link in sorted((cache / ".links").glob("*")):
                target = Path(link.read_text().strip())
                if (target / "package.json").is_file():
                    package = str(target)
                    break
            if package:
                break
    if not executable:
        for cache in caches:
            matches = sorted(
                p
                for pattern in (
                    "chromium-*/chrome-linux*/chrome",
                    "chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
                    "chromium-*/chrome-win*/chrome.exe",
                )
                for p in cache.glob(pattern)
            )
            if matches:
                executable = str(matches[-1])
                break
    if not shutil.which("node") or not package or not executable:
        raise ValueError(
            "GUI evals require existing Node, Playwright, and Chromium. "
            "Nothing was installed."
        )
    environment["EVAL_PLAYWRIGHT_MODULE"] = package
    environment["EVAL_BROWSER_EXECUTABLE"] = executable
    return environment


class ProjectServer:
    """Serve only this disposable project's files to the test browser."""

    def __init__(self, root: Path) -> None:
        class Handler(SimpleHTTPRequestHandler):
            def translate_path(self, path: str) -> str:
                target = Path(super().translate_path(path)).resolve()
                return str(
                    target if target.is_relative_to(root) else root / ".browser-denied"
                )

            def log_message(self, format: str, *args: object) -> None:
                pass

        self.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(Handler, directory=str(root))
        )
        self.origin = f"http://127.0.0.1:{self.server.server_port}/"
        self.thread = threading.Thread(
            target=lambda: self.server.serve_forever(poll_interval=0.05), daemon=True
        )
        self.thread.start()

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


class BrowserWorker:
    """Run the existing browser while the candidate keeps its usual sandbox."""

    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        self.environment = browser_environment()
        self.server = ProjectServer(workspace.root)
        self.environment["EVAL_BROWSER_ORIGIN"] = self.server.origin
        self.environment["EVAL_BROWSER_JOURNAL"] = str(
            workspace.home / "work-system/browser-journal.jsonl"
        )
        self.queue = workspace.home / "work-system/browser-queue"
        self.queue.mkdir(exist_ok=True)
        self.stopped = threading.Event()
        self.process: subprocess.Popen[str] | None = None
        self.process_lock = threading.Lock()
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def _execute(self, request: Path) -> dict[str, JsonValue]:
        try:
            scenario = TypeAdapter(dict[str, JsonValue]).validate_json(
                request.read_text()
            )
            page = scenario.get("page")
            if not isinstance(page, str):
                raise ValueError("Browser requests need a local project page.")
            scenario["page"] = (
                self.workspace.file(page).relative_to(self.workspace.root).as_posix()
            )
        except ValueError as error:
            # Rejected inputs never reach the browser's receipt writer.
            receipt: dict[str, JsonValue] = {
                "request_id": request.name.removesuffix(".request.json"),
                "status": "failed",
                "steps": [],
                "observations": [],
                "images": [],
                "error": str(error),
            }
            with Path(self.environment["EVAL_BROWSER_JOURNAL"]).open("a") as journal:
                journal.write(json.dumps(receipt) + "\n")
            raise
        with tempfile.TemporaryDirectory(prefix="browser-request-") as raw:
            directory = Path(raw)
            path = directory / "scenario.json"
            path.write_text(json.dumps(scenario))
            with self.process_lock:
                if self.stopped.is_set():
                    raise ValueError("Browser worker has stopped.")
                self.process = subprocess.Popen(
                    [
                        "node",
                        str(Path(__file__).with_name("browser.cjs")),
                        str(path),
                        raw,
                    ],
                    cwd=self.workspace.root,
                    env={
                        **self.environment,
                        "EVAL_BROWSER_REQUEST_ID": request.name.removesuffix(
                            ".request.json"
                        ),
                    },
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    start_new_session=True,
                )
            try:
                stdout, stderr = self.process.communicate(timeout=60)
                code = self.process.returncode
            except subprocess.TimeoutExpired:
                self._terminate()
                try:
                    stdout, stderr = self.process.communicate(timeout=3)
                except subprocess.TimeoutExpired:
                    self._terminate(hard=True)
                    stdout, stderr = self.process.communicate(timeout=3)
                code = 1
                stderr += "\nBrowser operation exceeded 60 seconds."
            finally:
                with self.process_lock:
                    self.process = None
            if code:
                return {"returncode": code, "stderr": stderr}
            result = TypeAdapter(dict[str, JsonValue]).validate_json(stdout)
            images: list[JsonValue] = [
                {
                    "name": p.stem,
                    "data_url": PNG_PREFIX
                    + base64.b64encode(p.read_bytes()).decode("ascii"),
                }
                for p in sorted(directory.glob("*.png"))
            ]
            return {
                "returncode": 0,
                "stderr": "",
                "result": result,
                "images": images,
                "structures": [
                    {"name": p.name, "content": p.read_text()}
                    for p in sorted(directory.glob("*.json"))
                    if p.name != "scenario.json"
                ],
            }

    def _serve(self) -> None:
        while not self.stopped.wait(0.05):
            for request in sorted(self.queue.glob("*.request.json")):
                if self.stopped.is_set():
                    break
                identifier = request.name.removesuffix(".request.json")
                try:
                    result = self._execute(request)
                except Exception as error:
                    result = {"returncode": 1, "stderr": str(error)}
                response = self.queue / (identifier + ".response.json")
                pending = response.with_suffix(".pending")
                pending.write_text(json.dumps(result))
                pending.replace(response)
                request.unlink()

    def _terminate(self, *, hard: bool = False) -> None:
        with self.process_lock:
            if self.process is not None and self.process.poll() is None:
                try:
                    if os.name == "posix":
                        os.killpg(
                            self.process.pid, signal.SIGKILL if hard else signal.SIGTERM
                        )
                    else:
                        self.process.kill()
                except ProcessLookupError:
                    pass

    def close(self) -> None:
        self.stopped.set()
        self._terminate()
        self.thread.join(timeout=3)
        if self.thread.is_alive():
            self._terminate(hard=True)
            self.thread.join(timeout=3)
        self.server.close()
        if self.thread.is_alive():
            raise RuntimeError("Browser worker did not stop.")


def install_browser(workspace: Workspace) -> None:
    if workspace.browser_worker is not None:
        return
    browser_environment()
    script = workspace.home / "bin/browser_client.py"
    shutil.copyfile(Path(__file__).with_name("browser_client.py"), script)
    launcher = workspace.home / "bin/browser-run"
    launcher.write_text(
        "#!"
        + sys.executable
        + "\n"
        + "exec(compile(open("
        + repr(str(script))
        + ").read(), "
        + repr(str(script))
        + ", 'exec'))\n"
    )
    launcher.chmod(0o755)
    workspace.browser_worker = BrowserWorker(workspace)


def image_bytes(data_url: str) -> bytes:
    if not data_url.startswith(PNG_PREFIX):
        raise ValueError("Browser evidence must contain PNG image inputs.")
    content = base64.b64decode(data_url[len(PNG_PREFIX) :], validate=True)
    if not content.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG evidence.")
    return content


def collect_browser(workspace: Workspace, scenario: str) -> dict[str, JsonValue]:
    environment = browser_environment()
    server = ProjectServer(workspace.root)
    environment["EVAL_BROWSER_ORIGIN"] = server.origin
    try:
        result = subprocess.run(
            [
                "node",
                str(Path(__file__).with_name("gui_contract.cjs")),
                str(workspace.root),
                scenario,
            ],
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
        )
    finally:
        server.close()
    if result.returncode:
        raise ValueError("Browser observation failed: " + result.stderr[-1500:])
    observed = TypeAdapter(dict[str, JsonValue]).validate_json(result.stdout)
    if type(observed.get("matched")) is not bool or not observed.get("images"):
        raise ValueError("Browser observation lacks a result or images.")
    observed["origin"] = "private_grader"
    observed["scenario"] = scenario
    return observed


def candidate_browser(
    workspace: Workspace, problems: list[str] | None = None
) -> list[dict[str, JsonValue]]:
    journal = workspace.home / "work-system/browser-journal.jsonl"
    records = []
    for number, line in enumerate(
        journal.read_text().splitlines() if journal.exists() else []
    ):
        try:
            record = TypeAdapter(dict[str, JsonValue]).validate_json(line)
            if record.get("request_id") is not None and not isinstance(
                record["request_id"], str
            ):
                raise ValueError("Invalid browser request identifier.")
            records.append(record)
        except ValueError:
            if problems is None:
                raise
            problems.append(f"Unreadable browser receipt at line {number + 1}.")
    if problems is not None:
        identifiers = {r.get("request_id") for r in records}
        queue = workspace.home / "work-system/browser-queue"
        for response in queue.glob("*.response.json"):
            if response.name.removesuffix(".response.json") not in identifiers:
                problems.append(
                    "Browser request has no operation receipt: " + response.stem
                )
        for pending in queue.glob("*.request.json"):
            problems.append("Browser request still pending: " + pending.stem)
    for record in records:
        record["origin"] = "candidate_browser"
        images = record.get("images")
        if isinstance(images, list):
            valid: list[JsonValue] = []
            for item in images:
                try:
                    if not isinstance(item, dict) or not isinstance(
                        item.get("data_url"), str
                    ):
                        raise ValueError("Missing browser image data.")
                    data = item["data_url"]
                    assert isinstance(data, str)
                    workspace.raw_temporary_contents.add(image_bytes(data))
                    valid.append(item)
                except ValueError as error:
                    if problems is None:
                        raise
                    problems.append("Unreadable browser image: " + str(error))
            record["images"] = valid
    return records
