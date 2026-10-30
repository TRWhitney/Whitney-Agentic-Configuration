"""Procedure cases distinguish supported corrections from shortcuts."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from evals.evidence import EvidenceRun
from evals.fixtures import make_workspace
from evals.models import CaseSpec, MessageStep, load_cases
from evals.runner import Observation, check_result
from tests.test_eval_runner import SOURCE


class ProcedureFollowupTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_display_oracle_rejects_light_only_and_preserves_notebook_checks(
        self,
    ) -> None:
        from evals.gui import collect_browser

        case = self.case("gui-browser-rendering")
        with make_workspace(SOURCE, case) as w:
            finished = json.loads(
                (SOURCE / "evals/cases/fixtures/gui-finished.json").read_text()
            )
            for name, text in finished.items():
                w.file(name).write_text(text)
            bad = collect_browser(w, "display-settings")
            measurements = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                bad["measurements"]
            )
            failures = [m["name"] for m in measurements if not m["matched"]]
            self.assertTrue(failures)
            self.assertTrue(
                all(str(name).startswith("appearance/dark/") for name in failures),
                failures,
            )
            css = w.file("app/app.css")
            css.write_text(css.read_text() + "\n" + case.files["design/display.css"])
            good = collect_browser(w, "display-settings")
            self.assertTrue(good["matched"], good["measurements"])
            css.write_text(
                css.read_text() + "\nhtml,[role=alert]{border-color:transparent;}\n"
            )
            equivalent = collect_browser(w, "display-settings")
            self.assertTrue(equivalent["matched"], equivalent["measurements"])
            css.write_text(
                css.read_text().replace(
                    " .preference-row select,.preference-row .preference-select "
                    "{background-image:",
                    " .preference-select {background-image:",
                )
            )
            bad_arrow = collect_browser(w, "display-settings")
            measured = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                bad_arrow["measurements"]
            )
            self.assertTrue(
                any(
                    m["name"] == "appearance/dark/select/image" and not m["matched"]
                    for m in measured
                )
            )
            css.write_text(
                finished["app/app.css"]
                + case.files["design/display.css"].replace(
                    "background:#121d2b", "background:#edf2f7"
                )
            )
            bad_canvas = collect_browser(w, "display-settings")
            measured = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                bad_canvas["measurements"]
            )
            self.assertTrue(
                any(
                    m["name"] == "appearance/dark/page/background" and not m["matched"]
                    for m in measured
                )
            )

    def test_heading_failure_is_order_dependent_and_test_isolation_repairs_it(
        self,
    ) -> None:
        case = self.case("order-dependent-test-failure")
        with make_workspace(SOURCE, case) as w:

            def run(*names: str) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [
                        "python3",
                        "-B",
                        "-c",
                        'import sys,unittest;sys.path.insert(0,"tests");'
                        "suite=unittest.TestLoader().loadTestsFromNames(sys.argv[1:]);"
                        "result=unittest.TextTestRunner().run(suite);"
                        "sys.exit(not result.wasSuccessful())",
                        *names,
                    ],
                    cwd=w.root,
                    capture_output=True,
                    text=True,
                )

            default = "test_export.ExportTests.test_default_heading"
            custom = "test_export.ExportTests.test_custom_heading"
            self.assertEqual(run(default).returncode, 0)
            self.assertNotEqual(run(custom, default).returncode, 0)
            self.assertEqual(run(default, custom).returncode, 0)
            p = w.file("tests/test_export.py")
            p.write_text(
                p.read_text().replace(
                    "class ExportTests(unittest.TestCase):",
                    "class ExportTests(unittest.TestCase):\n"
                    "    def setUp(self):\n"
                    "        heading = export.get_heading()\n"
                    "        self.addCleanup(export.set_heading, *heading)\n",
                )
            )
            self.assertEqual(run(custom, default).returncode, 0)
            self.assertEqual(run(default, custom).returncode, 0)
            source = w.file("src/export.py")
            source.write_text(
                source.read_text() + "\n"
                "def export_selected(items, selected):\n"
                '    rows = [i for i in items if i["name"] in selected]\n'
                "    return export_inventory(rows)\n"
            )
            check = case.steps[-1].checks[0]
            self.assertTrue(check_result(check, Observation(), w, "t", [])[0])
            source.write_text(
                source.read_text().replace(
                    "    return export_inventory(rows)",
                    '    set_heading("name", "quantity")\n'
                    "    return export_inventory(rows)",
                )
            )
            self.assertFalse(check_result(check, Observation(), w, "t", [])[0])

    def test_worker_has_passing_supplied_test_but_missing_assigned_behavior(
        self,
    ) -> None:
        case = self.case("worker-invalid-supplied-test")
        evidence = EvidenceRun(case.id, "example", "example")
        with make_workspace(SOURCE, case) as w:
            self.assertEqual(w.candidate_role, "implementation-worker")
            baseline = subprocess.run(
                ["python3", "-B", "-m", "unittest", "discover", "-s", "tests"],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    "from src.app import stock_total;"
                    'assert stock_total([{"quantity":-3},{"quantity":5}])==5',
                ],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            step = case.steps[0]
            assert isinstance(step, MessageStep)
            evidence.observe(
                w, 0, "worker-thread-id", step.prompt, Observation("Blocked.")
            )
            self.assertIn("spawned implementation subagent", evidence.frames[0].prompt)

    def test_deletion_risk_is_real_and_unchanged_guard_accepts_only_search_scope(
        self,
    ) -> None:
        case = self.case("review-reports-outside-data-loss")
        with make_workspace(SOURCE, case) as w:
            result = subprocess.run(
                [
                    "python3",
                    "-c",
                    """from src.delete import delete_selected
class Store:
    def __init__(self): self.items=[{'id':'cup','name':'Cup','quantity':2}]
    def load(self): return self.items
    def save(self,items): self.items=items
s=Store()
delete_selected(s,set())
assert s.items==[]
""",
                ],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            checks = case.steps[-1].checks
            self.assertTrue(check_result(checks[0], Observation(), w, "t", [])[0])
            self.assertTrue(check_result(checks[1], Observation(), w, "t", [])[0])
            p = w.file("src/delete.py")
            p.write_text(
                p.read_text().replace(
                    "    items = store.load()",
                    "    if not selected: return\n    items = store.load()",
                )
            )
            self.assertFalse(check_result(checks[1], Observation(), w, "t", [])[0])

    def test_browser_can_switch_system_appearance_during_editing(self) -> None:
        case = self.case("interactive-prototype-comparison")
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            page = w.file("appearance.html")
            page.write_text(
                "<style>body{background:white}@media(prefers-color-scheme:dark)"
                '{body{background:black}}</style><input aria-label="Name">'
            )
            scenario = Path(raw) / "steps.json"
            observation = (
                '({dark:matchMedia("(prefers-color-scheme:dark)").matches,'
                'text:document.querySelector("input").value})'
            )
            scenario.write_text(
                json.dumps(
                    {
                        "page": "appearance.html",
                        "media": {"colorScheme": "light"},
                        "steps": [
                            {"action": "fill", "selector": "input", "value": "Unsaved"},
                            {"action": "media", "colorScheme": "dark"},
                            {
                                "action": "evaluate",
                                "script": observation,
                            },
                            {"action": "capture", "name": "dark"},
                        ],
                    }
                )
            )
            run = subprocess.run(
                [str(w.home / "bin/browser-run"), str(scenario), raw],
                cwd=w.root,
                env=w.environment(),
                capture_output=True,
                text=True,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(run.stdout)["observations"][0]
            self.assertEqual(result, {"dark": True, "text": "Unsaved"})

    def test_prototype_history_has_a_reproducible_cause_and_equivalent_repairs(
        self,
    ) -> None:
        case = self.case("interactive-prototype-comparison")
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:

            def visible() -> bool:
                scenario = Path(raw) / "steps.json"
                scenario.write_text(
                    json.dumps(
                        {
                            "page": "prototypes/names/index.html",
                            "steps": [
                                {
                                    "action": "click",
                                    "selector": "#dialog-items > div:first-child "
                                    "button",
                                },
                                {
                                    "action": "evaluate",
                                    "script": "getComputedStyle(document.querySelector("
                                    '".item-summary")).display !== "none"',
                                },
                            ],
                        }
                    )
                )
                run = subprocess.run(
                    [str(w.home / "bin/browser-run"), str(scenario), raw],
                    cwd=w.root,
                    env=w.environment(),
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(run.returncode, 0, run.stderr)
                return json.loads(run.stdout)["observations"][-1] is True

            self.assertFalse(visible())
            base = w.file("prototypes/names/base.css")
            base.write_text(
                base.read_text().replace("display:none!important", "display:block")
            )
            self.assertTrue(visible())
            base.write_text(case.files["prototypes/names/base.css"])
            preview = w.file("prototypes/names/preview.css")
            preview.write_text(
                preview.read_text()
                + "\nbody.dialog-open .item-summary{display:block!important}\n"
            )
            self.assertTrue(visible())
