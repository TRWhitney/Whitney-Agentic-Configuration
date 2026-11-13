"""Browser evidence must distinguish correct layouts and independent verification."""

from __future__ import annotations

import json
import re
import unittest

from pydantic import JsonValue, TypeAdapter

from evals.evidence import EvidenceRun
from evals.fixtures import Workspace, make_workspace
from evals.models import load_cases
from evals.runner import Observation
from tests.test_eval_runner import SOURCE


class GuiTests(unittest.TestCase):
    @staticmethod
    def measurements(result: dict[str, JsonValue]) -> list[dict[str, JsonValue]]:
        return TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            result["measurements"]
        )

    def install_finished_application(self, workspace: Workspace) -> None:
        files = json.loads(
            (SOURCE / "evals/cases/fixtures/gui-finished.json").read_text()
        )
        for path, content in files.items():
            destination = workspace.file(path)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content)

    def rename_internal_markup(self, workspace: Workspace) -> None:
        for path in (workspace.root / "app").rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text()
            for name in (
                "preference-row",
                "dialog-heading",
                "document-mark",
                "search-panel",
                "document-pane",
                "document-footer",
                "code-editor",
                "dialog-frame",
            ):
                text = text.replace(name, "alternate-" + name)
            for name in (
                "new",
                "rename",
                "name",
                "confirm",
                "cancel",
                "name-error",
                "modal-actions",
                "search",
                "clear",
                "results",
                "split",
                "save",
                "document-title",
                "retry",
                "global-status",
                "save-notice",
                "save-label",
                "save-detail",
            ):
                text = re.sub(
                    r"#" + re.escape(name) + r"(?![\w-])", "#alternate-" + name, text
                )
                for prefix in ('id="', 'for="'):
                    text = text.replace(
                        prefix + name + '"', prefix + "alternate-" + name + '"'
                    )
            text = text.replace("<article", "<section").replace(
                "</article>", "</section>"
            )
            text = text.replace(
                '<section id="alternate-save-notice"', '<div id="alternate-save-notice"'
            ).replace("</section>\n<textarea", "</div>\n<textarea")
            path.write_text(text)

    def test_copying_the_prototype_cannot_complete_the_application(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        with make_workspace(SOURCE, case) as workspace:
            for name in ("index.html", "app.css", "app.js"):
                workspace.file("app/" + name).write_bytes(
                    workspace.file("design/" + name).read_bytes()
                )
            result = collect_browser(workspace, "clean")
            self.assertFalse(
                result["matched"],
                "A display prototype lacks production document storage.",
            )
            failures = [
                str(measurement["name"])
                for measurement in self.measurements(result)
                if not measurement["matched"]
            ]
            self.assertIn("notebook/reload-current-text", failures)
            self.assertTrue(
                all(name.startswith("notebook/") for name in failures), failures
            )

    def test_real_browser_rejects_defects_and_accepts_reference(self) -> None:
        from evals.gui import collect_browser

        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        for name in [
            "gui-accepted-design",
            "gui-browser-rendering",
            "gui-state-changes",
            "gui-combined-conditions",
            "gui-layout-and-wrapping",
            "gui-incomplete-audit",
        ]:
            case = cases[name]
            with self.subTest(case=name), make_workspace(SOURCE, case) as w:
                check = next(
                    c for s in case.steps for c in s.checks if c.kind == "browser"
                )
                bad = collect_browser(w, check.scenario)
                self.assertFalse(bad["matched"], bad)
                self.assertTrue(
                    all(
                        measurement["matched"]
                        for measurement in self.measurements(bad)
                        if str(measurement["name"]).startswith("notebook/")
                    ),
                    "Presentation defects must preserve notebook behavior.",
                )
                self.install_finished_application(w)
                if name == "gui-browser-rendering":
                    css = w.file("app/app.css")
                    css.write_text(css.read_text() + case.files["design/display.css"])
                self.rename_internal_markup(w)
                good = collect_browser(w, check.scenario)
                self.assertTrue(good["matched"], good)
                self.assertEqual(good["origin"], "private_grader")
                images = good["images"]
                assert isinstance(images, list)
                self.assertGreaterEqual(len(images), 2)
                measurements = {
                    str(item["name"]): item for item in self.measurements(good)
                }
                self.assertTrue(measurements["notebook/reload-current-text"]["matched"])
                self.assertTrue(measurements["notebook/reload-other-text"]["matched"])

    def test_search_height_check_covers_added_documents_at_narrow_width(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-state-changes"
        )
        with make_workspace(SOURCE, case) as workspace:
            self.install_finished_application(workspace)
            css = workspace.file("app/app.css")
            original = css.read_text()
            css.write_text(original + "\n#results {flex-wrap:wrap;}\n")
            bad = collect_browser(workspace, "transitions")
            failures = {
                str(item["name"])
                for item in self.measurements(bad)
                if not item["matched"]
            }
            self.assertEqual(failures, {"search/narrow-empty-height"})
            css.write_text(original)
            good = collect_browser(workspace, "transitions")
            self.assertTrue(good["matched"], good)

    def test_design_check_allows_footer_to_follow_the_applied_format(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "gui-accepted-design"
        )
        with make_workspace(SOURCE, case) as workspace:
            self.install_finished_application(workspace)
            component = workspace.file("app/components/workspace.js")
            component.write_text(
                component.read_text().replace(
                    "notebook.current.title;",
                    "notebook.current.title;"
                    " root.querySelector('.document-footer span:last-child')"
                    ".textContent"
                    " = notebook.current.preferences.format;",
                )
            )
            good = collect_browser(workspace, "design")
            self.assertTrue(good["matched"], self.measurements(good))

            naming = workspace.file("app/components/naming.js")
            naming.write_text(
                naming.read_text().replace('class="dialog-frame"', 'class="unframed"')
            )
            bad = collect_browser(workspace, "design")
            self.assertFalse(bad["matched"], self.measurements(bad))

    def test_storage_regression_fails_even_when_presentation_matches(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        with make_workspace(SOURCE, case) as workspace:
            state = workspace.file("app/state.js")
            state.write_text(
                state.read_text().replace(
                    "storage.setItem(storageKey, JSON.stringify(state))", "undefined"
                )
            )
            result = collect_browser(workspace, "clean")
            failures = [
                str(item["name"])
                for item in self.measurements(result)
                if not item["matched"]
            ]
            self.assertIn("notebook/reload-current-text", failures)
            self.assertTrue(
                all(name.startswith("notebook/") for name in failures), failures
            )

    def test_internal_markup_names_are_not_product_requirements(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        with make_workspace(SOURCE, case) as workspace:
            self.install_finished_application(workspace)
            self.rename_internal_markup(workspace)
            result = collect_browser(workspace, "clean")
            self.assertTrue(result["matched"])

    def test_retry_rejects_a_visible_explanation_split_into_paragraphs(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        for stale in (False, True):
            with self.subTest(stale=stale), make_workspace(SOURCE, case) as workspace:
                self.install_finished_application(workspace)
                path = workspace.file("app/components/workspace.js")
                path.write_text(
                    path.read_text().replace(
                        '<p id="save-detail"></p>', '<div id="save-detail"></div>'
                    )
                )
                path = workspace.file("app/components/save-status.js")
                hidden = "false" if stale else "status !== 'failed'"
                path.write_text(
                    path.read_text().replace(
                        "detail.hidden = status !== 'failed'; "
                        "detail.textContent = failureDetail;",
                        f"detail.hidden = {hidden}; detail.innerHTML = '<p>' + "
                        "failureDetail.replace('. ', '.</p><p>') + '</p>';",
                    )
                )
                result = collect_browser(workspace, "composition")
                failures = [
                    str(item["name"])
                    for item in self.measurements(result)
                    if not item["matched"]
                ]
                self.assertEqual(
                    failures, ["retry/previous-detail-visible"] if stale else []
                )

    def test_fieldnotes_cases_preserve_requests_and_product_data_flow(self) -> None:
        cases = [
            c for c in load_cases(SOURCE / "evals/cases") if "gui-project" in c.fixtures
        ]
        self.assertEqual(len(cases), 9)
        for case in cases:
            with self.subTest(case=case.id):
                self.assertNotIn("docs/visual-review.md", case.artifacts)
                self.assertNotEqual(
                    case.files["app/app.js"], case.files["design/app.js"]
                )
                self.assertIn("app/state.js", case.files)
                self.assertNotIn("previous-checks", "\n".join(case.files))
                for step in case.steps:
                    if step.kind != "message":
                        continue
                    self.assertNotRegex(
                        step.prompt.lower(),
                        r"\b(audit|review|verify|verification|report)\b",
                    )
                    browser = next(
                        check for check in step.checks if check.kind == "browser"
                    )
                    self.assertTrue(browser.require_match)
                    for check in step.checks:
                        if check.kind == "unchanged":
                            self.assertNotIn("app", check.paths)

    def test_clean_control_keeps_columns_aligned_after_applying_one_row(self) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.gui import install_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            install_browser(w)
            for page in ("app/index.html", "design/index.html"):
                scenario = Path(raw) / "scenario.json"
                scenario.write_text(
                    json.dumps(
                        {
                            "page": page,
                            "steps": [
                                {
                                    "action": "click",
                                    "selector": ".preference-row:first-of-type .apply",
                                },
                                {
                                    "action": "evaluate",
                                    "script": """
                                [...document.querySelectorAll('.preference-row')]
                                .map(row => {
                                  const select=row.querySelector('select')
                                    .getBoundingClientRect();
                                  const action=row.querySelector('button')
                                    .getBoundingClientRect();
                                  return {selectRight:select.right,
                                          actionLeft:action.left}
                                })""",
                                },
                            ],
                        }
                    )
                )
                result = subprocess.run(
                    [str(w.home / "bin/browser-run"), str(scenario), raw],
                    cwd=w.root,
                    env=w.environment(),
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                rows = json.loads(result.stdout)["observations"][0]
                self.assertAlmostEqual(
                    rows[0]["selectRight"], rows[1]["selectRight"], delta=1
                )
                self.assertAlmostEqual(
                    rows[0]["actionLeft"], rows[1]["actionLeft"], delta=1
                )

    def test_equivalent_monospace_font_is_allowed(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        with make_workspace(SOURCE, case) as w:
            with w.file("app/app.css").open("a") as css:
                css.write("\n.code-editor { font-family: 'Courier New'; }\n")
            result = collect_browser(w, "rendering")
            self.assertTrue(result["matched"], result["measurements"])

    def test_clean_audit_control_and_private_capture_never_prove_candidate_checks(
        self,
    ) -> None:
        from evals.assessment import blind_packet
        from evals.gui import collect_browser

        case = next(
            c for c in load_cases(SOURCE / "evals/cases") if c.id == "gui-clean-audit"
        )
        run = EvidenceRun(case.id, "hidden-model", "hidden-condition")
        with make_workspace(SOURCE, case) as w:
            check = next(c for s in case.steps for c in s.checks if c.kind == "browser")
            result = collect_browser(w, check.scenario)
            self.assertTrue(result["matched"])
            observation = Observation("Everything is verified.", 10)
            observation.browser_evidence.append(result)
            message = case.steps[-1]
            assert message.kind == "message"
            run.observe(w, 0, "main", message.prompt, observation)
        packet, _ = blind_packet(case.rubric, [run])
        self.assertTrue(packet["images"])
        self.assertIn("private_grader", json.dumps(packet))
        self.assertNotIn("hidden-model", json.dumps(packet))
        self.assertIn("cannot establish", str(packet["evidence_format"]))


class BrowserEvidenceTests(unittest.TestCase):
    def test_document_load_receipts_distinguish_navigation_from_keys_and_urls(
        self,
    ) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.gui import candidate_browser, install_browser
        from evals.models import CaseSpec

        page = (
            '<!doctype html><a id="next" href="page.html?again">Open again</a>'
            "<script>sessionStorage.loads=Number(sessionStorage.loads||0)+1;</script>"
        )
        case = CaseSpec.model_validate(
            {
                "id": "document-load-receipts",
                "tags": [],
                "files": {"page.html": page},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Inspect the page.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        steps = [
            {
                "action": "evaluate",
                "script": "window.marker='original'; Number(sessionStorage.loads)",
            },
            {"action": "press", "key": "Control+r"},
            {
                "action": "evaluate",
                "script": (
                    "({marker:window.marker, loads:Number(sessionStorage.loads)})"
                ),
            },
            {
                "action": "evaluate",
                "script": (
                    "location.hash='section'; history.pushState({}, '', '#other'); "
                    "Number(sessionStorage.loads)"
                ),
            },
            {
                "action": "evaluate",
                "script": (
                    "(async()=>{await new Promise(resolve=>{"
                    "const f=document.createElement('iframe');f.srcdoc='<p>Child</p>';"
                    "f.onload=resolve;document.body.append(f)});"
                    "return Number(sessionStorage.loads)})()"
                ),
            },
            {"action": "click", "selector": "#next"},
            {
                "action": "evaluate",
                "script": (
                    "({marker:window.marker||null, loads:Number(sessionStorage.loads)})"
                ),
            },
        ]
        for fail in (False, True):
            with (
                self.subTest(fail=fail),
                make_workspace(SOURCE, case) as workspace,
                tempfile.TemporaryDirectory() as raw,
            ):
                install_browser(workspace)
                scenario = Path(raw) / "scenario.json"
                scenario.write_text(
                    json.dumps(
                        {
                            "page": "page.html",
                            "steps": steps
                            + (
                                [
                                    {
                                        "action": "evaluate",
                                        "script": (
                                            "throw Error('receipt probe failure')"
                                        ),
                                    }
                                ]
                                if fail
                                else []
                            ),
                        }
                    )
                )
                result = subprocess.run(
                    [str(workspace.home / "bin/browser-run"), str(scenario), raw],
                    cwd=workspace.root,
                    env=workspace.environment(),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, int(fail), result.stderr)
                records = candidate_browser(workspace)
                self.assertEqual(len(records), 1)
                record = records[0]
                self.assertEqual(record["status"], "failed" if fail else "completed")
                self.assertEqual(
                    record["observations"],
                    [
                        1,
                        {"marker": "original", "loads": 1},
                        1,
                        1,
                        {"marker": None, "loads": 2},
                    ],
                )
                self.assertIn("navigation", record)
                navigation = TypeAdapter(dict[str, JsonValue]).validate_python(
                    record["navigation"]
                )
                self.assertEqual(navigation["status"], "complete")
                events = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                    navigation["events"]
                )
                commits = [e for e in events if e["kind"] == "main_document_commit"]
                loads = [e for e in events if e["kind"] == "main_document_load"]
                self.assertEqual([e["document_sequence"] for e in commits], [1, 2])
                self.assertEqual([e["document_sequence"] for e in loads], [1, 2])
                self.assertEqual(
                    [e["committed_during_action_index"] for e in loads], [None, 5]
                )
                self.assertTrue(str(commits[0]["url"]).endswith("/page.html"))
                self.assertTrue(str(commits[1]["url"]).endswith("/page.html?again"))
                same_document = [
                    e for e in events if e["kind"] == "same_document_navigation"
                ]
                self.assertEqual(len(same_document), 2)
                self.assertTrue(all(e["document_sequence"] == 1 for e in same_document))
                if not fail:
                    self.assertEqual(
                        json.loads(result.stdout)["navigation"], navigation
                    )
                run = EvidenceRun(case.id, "candidate", "condition")
                run.observe(
                    workspace,
                    0,
                    "opaque-navigation-thread-0190a624",
                    "Inspect.",
                    Observation(browser_evidence=records),
                )
                self.assertEqual(run.frames[0].browser[0]["navigation"], navigation)

    def test_rejected_browser_request_does_not_lose_recording(self) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.gui import candidate_browser, install_browser
        from evals.models import CaseSpec

        case = CaseSpec.model_validate(
            {
                "id": "rejected-browser-request",
                "tags": [],
                "files": {"page.html": "<button>Preview</button>"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Open the supplied preview.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with (
            make_workspace(SOURCE, case) as workspace,
            tempfile.TemporaryDirectory() as raw,
        ):
            install_browser(workspace)
            scenario = Path(raw) / "scenario.json"
            scenario.write_text(json.dumps({"url": "file:///project/page.html"}))
            result = subprocess.run(
                [str(workspace.home / "bin/browser-run"), str(scenario), raw],
                cwd=workspace.root,
                env=workspace.environment(),
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            problems: list[str] = []
            records = candidate_browser(workspace, problems)
            self.assertEqual(problems, [])
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["status"], "failed")
            self.assertEqual(records[0]["steps"], [])
            self.assertTrue(records[0]["error"])

    def test_candidate_capture_is_kept_after_candidate_deletes_its_raw_files(
        self,
    ) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.gui import candidate_browser, install_browser
        from evals.models import CaseSpec

        case = CaseSpec.model_validate(
            {
                "id": "browser-tool",
                "tags": [],
                "files": {"page.html": "<label>Name <input></label>"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Inspect the page.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            install_browser(w)
            script = Path(raw) / "steps.json"
            script.write_text(
                json.dumps(
                    {
                        "page": "page.html",
                        "steps": [{"action": "capture", "name": "initial"}],
                    }
                )
            )
            environment = w.environment()
            subprocess.run(
                [str(w.home / "bin/browser-run"), str(script), raw],
                cwd=w.root,
                env=environment,
                check=True,
                capture_output=True,
            )
            for path in Path(raw).glob("*.png"):
                path.unlink()
            record = candidate_browser(w)[0]
            self.assertEqual(record["origin"], "candidate_browser")
            self.assertTrue(record["images"])
            run = EvidenceRun(case.id, "model", "current")
            run.observe(w, 0, "main", "Inspect.", Observation("Done.", 10))
            self.assertEqual(len(run.frames[0].browser), 1)
            self.assertTrue(w.raw_temporary_contents)
            self.assertFalse(any(p.endswith(".png") for p in w.project_files()))
            self.assertNotIn(str(w.root), json.dumps(run.frames[0].browser))

    def test_failed_browser_sequence_keeps_completed_captures(self) -> None:
        import subprocess
        import tempfile
        from pathlib import Path

        from evals.gui import candidate_browser, install_browser
        from evals.models import CaseSpec

        case = CaseSpec.model_validate(
            {
                "id": "browser-failure",
                "tags": [],
                "files": {"page.html": "<button>Save</button>"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Inspect the page.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            install_browser(w)
            scenario = Path(raw) / "steps.json"
            scenario.write_text(
                json.dumps(
                    {
                        "page": "page.html",
                        "steps": [
                            {"action": "capture", "name": "before"},
                            {"action": "unsupported"},
                        ],
                    }
                )
            )
            result = subprocess.run(
                [str(w.home / "bin/browser-run"), str(scenario), raw],
                cwd=w.root,
                env=w.environment(),
                capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            records = candidate_browser(w)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["status"], "failed")
            self.assertTrue(records[0]["images"])

    def test_browser_observations_are_readable_without_custom_decoding(self) -> None:
        from evals.assessment import blind_packet
        from evals.evidence import EvidenceFrame
        from evals.models import RubricCriterion

        observation: dict[str, JsonValue] = {
            "html": "<main>Useful content</main>",
            "elements": {"x": {"top": 4}},
        }
        run = EvidenceRun("case", "model", "condition")
        run.frames.append(
            EvidenceFrame(
                0,
                "main",
                "Inspect.",
                "Done.",
                {},
                [],
                None,
                {},
                browser=[
                    {
                        "origin": "candidate_browser",
                        "observations": [observation, observation],
                    }
                ],
            )
        )
        packet, _ = blind_packet(
            [RubricCriterion(id="layout", description="Inspect layout.")], [run]
        )
        output = json.loads(json.dumps(packet))["outputs"][0]
        self.assertEqual(
            output["frames"][0]["browser"][0]["observations"],
            [observation, observation],
        )

    def test_browser_worker_keeps_requests_inside_the_project(self) -> None:
        import http.server
        import subprocess
        import tempfile
        import threading
        from pathlib import Path

        from evals.gui import install_browser
        from evals.models import CaseSpec

        requests: list[str] = []

        class Canary(http.server.BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                requests.append(self.path)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"outside response")

            def log_message(self, format: str, *args: object) -> None:
                pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Canary)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        case = CaseSpec.model_validate(
            {
                "id": "browser-boundary",
                "tags": [],
                "files": {"page.html": "<h1>Local page</h1>"},
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Inspect.",
                        "checks": [{"kind": "no_publish"}],
                    }
                ],
            }
        )
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            install_browser(w)
            outside = Path(raw) / "outside.txt"
            outside.write_text("PRIVATE_CANARY_OUTSIDE_PROJECT")
            w.file("linked.txt").symlink_to(outside)
            external = f"http://127.0.0.1:{server.server_port}"
            script = """(async () => {
                const read = async u => {
                  try {return await (await fetch(u)).text()}
                  catch {return 'blocked'}
                };
                const socket = await new Promise(resolve => {
                  const ws = new WebSocket(EXTERNAL.replace('http:', 'ws:'));
                  ws.onerror = () => resolve('blocked');
                  ws.onclose = () => resolve('closed');
                  setTimeout(() => {ws.close();resolve('timeout')}, 1000);
                });
                return [await read(EXTERNAL), await read(FILE),
                        await read('/linked.txt'), socket];
            })()""".replace("EXTERNAL", json.dumps(external)).replace(
                "FILE", json.dumps(outside.as_uri())
            )
            scenario = Path(raw) / "steps.json"
            scenario.write_text(
                json.dumps(
                    {
                        "page": "page.html",
                        "steps": [
                            {"action": "evaluate", "script": "null"},
                            {"action": "evaluate", "script": script},
                        ],
                    }
                )
            )
            result = subprocess.run(
                [str(w.home / "bin/browser-run"), str(scenario), raw],
                cwd=w.root,
                env=w.environment(),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("PRIVATE_CANARY_OUTSIDE_PROJECT", result.stdout)
            self.assertFalse(requests)
            worker = w.browser_worker
            assert worker is not None
            worker.close()
            queued = worker.queue / "after-close.request.json"
            queued.write_text(json.dumps({"page": "page.html", "steps": []}))
            with self.assertRaisesRegex(ValueError, "stopped"):
                worker._execute(queued)
            self.assertFalse(worker.thread.is_alive())
