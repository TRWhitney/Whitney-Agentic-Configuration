"""Procedure graders distinguish behavior through usable tools."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Literal
from unittest.mock import patch

from pydantic import JsonValue, TypeAdapter

from evals.evidence import EvidenceRun
from evals.fixtures import Workspace, git, make_workspace
from evals.models import CaseSpec, load_cases
from evals.runner import Observation, check_result, run_case
from tests.test_eval_runner import SOURCE, FakeDriver


class ProcedureCoverageTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_published_session_correction_preserves_history_after_compaction(
        self,
    ) -> None:
        case = self.case("session-rework-after-push")
        evidence = EvidenceRun(case.id, "example", "example")
        remote_heads = []

        def factory(
            w: Workspace, model: str, timeout: float, max_tokens: int
        ) -> FakeDriver:
            class Driver(FakeDriver):
                calls = 0

                def message(self, thread: str, prompt: str) -> Observation:
                    remote_heads.append(git(w.root, "rev-parse", "origin/main"))
                    before = (
                        "No items saved."
                        if self.calls == 0
                        else "Nothing on the shelf."
                    )
                    after = (
                        "Nothing on the shelf."
                        if self.calls == 0
                        else "Your shelf is empty."
                    )
                    for name in ("src/app.py", "tests/test_message.py"):
                        p = w.file(name)
                        p.write_text(p.read_text().replace(before, after))
                    git(w.root, "add", ".")
                    git(w.root, "commit", "-qm", "Change shelf message")
                    w.navigate(thread, ["commit", "add", "HEAD"])
                    self.calls += 1
                    return Observation("Finished.", 10)

            return Driver()

        result = run_case(
            case,
            SOURCE,
            "example",
            driver_factory=factory,
            on_observation=evidence.observe,
        )
        self.assertEqual(result.mechanical_status, "pass", result.checks)
        self.assertNotEqual(remote_heads[0], remote_heads[1])
        self.assertTrue(all(f.git["initial_commit_present"] for f in evidence.frames))
        edit = next(f for f in evidence.frames if f.event == "fixture_edit")
        self.assertEqual(edit.git["head"], edit.git["remote_head"])
        final = evidence.frames[-1]
        self.assertNotEqual(final.git["head"], final.git["remote_head"])
        self.assertIn(str(final.git["remote_head"]), str(final.git["history"]))
        self.assertEqual(final.git["commit_count"], 3)
        self.assertTrue(any(f.event == "compaction" for f in evidence.frames))

    def test_fixture_publication_cannot_follow_a_changed_remote(self) -> None:
        case = self.case("session-rework-after-push")
        with make_workspace(SOURCE, case) as w:
            git(w.root, "remote", "set-url", "origin", "https://example.invalid/repo")
            with self.assertRaisesRegex(ValueError, "disposable remote"):
                w.publish()

    def test_fixture_publication_rejects_a_separate_external_push_url(self) -> None:
        case = self.case("session-rework-after-push")
        with make_workspace(SOURCE, case) as w:
            git(
                w.root,
                "remote",
                "set-url",
                "--push",
                "origin",
                "https://example.invalid/repo",
            )
            run = subprocess.run

            def guarded(
                args: list[str],
                *,
                check: bool,
                capture_output: bool,
                text: Literal[True],
                timeout: int,
            ) -> subprocess.CompletedProcess[str]:
                if "push" in args:
                    self.fail("Fixture tried to push after its destination changed.")
                return run(
                    args,
                    check=check,
                    capture_output=capture_output,
                    text=text,
                    timeout=timeout,
                )

            with (
                patch("evals.fixtures.subprocess.run", side_effect=guarded),
                self.assertRaisesRegex(ValueError, "disposable remote"),
            ):
                w.publish()

    def test_prototype_can_use_browser_tools_at_a_chosen_path(self) -> None:
        case = self.case("interactive-prototype-comparison")
        with make_workspace(SOURCE, case) as w, tempfile.TemporaryDirectory() as raw:
            page = w.file("experiments/compare.html")
            page.parent.mkdir()
            page.write_text(
                "<button onclick=\"this.textContent='Saved'\">Save</button>"
            )
            scenario = Path(raw) / "steps.json"
            scenario.write_text(
                json.dumps(
                    {
                        "page": "experiments/compare.html",
                        "steps": [
                            {"action": "press", "key": "Tab"},
                            {"action": "press", "key": "Enter"},
                            {
                                "action": "evaluate",
                                "script": "document.querySelector('button')"
                                ".textContent",
                            },
                            {"action": "capture", "name": "result"},
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
            self.assertIn("Saved", run.stdout)

    def test_keyboard_check_rejects_pointer_only_and_lost_focus(self) -> None:
        from evals.gui import collect_browser

        case = self.case("gui-keyboard-naming")

        def failures(result: dict[str, JsonValue]) -> list[str]:
            rows = TypeAdapter(list[dict[str, JsonValue]]).validate_python(
                result["measurements"]
            )
            return [str(row["name"]) for row in rows if not row["matched"]]

        with make_workspace(SOURCE, case) as w:
            bad = collect_browser(w, "keyboard")
            self.assertTrue(any("activate" in n for n in failures(bad)), failures(bad))
            self.assertTrue(
                any("focus-restored" in n for n in failures(bad)), failures(bad)
            )
            files = json.loads(
                (SOURCE / "evals/cases/fixtures/gui-project.json").read_text()
            )
            w.file("app/components/toolbar.js").write_text(
                files["app/components/toolbar.js"]
            )
            naming = w.file("app/components/naming.js")
            naming.write_text(
                naming.read_text()
                .replace(
                    "const render = event => {",
                    "let invoker, wasOpen=false;\n  const render = event => {",
                )
                .replace(
                    "const dialog = notebook.dialog;",
                    "const dialog = notebook.dialog;\n"
                    "    if (dialog && !wasOpen) invoker=document.activeElement;",
                )
                .replace(
                    "if (!dialog) return;",
                    "if (!dialog) { if(wasOpen) invoker?.focus();"
                    " wasOpen=false; return; }\n    wasOpen=true;",
                )
            )
            self.assertEqual(failures(collect_browser(w, "keyboard")), [])
            toolbar = w.file("app/components/toolbar.js")
            toolbar.write_text(
                case.files["app/components/toolbar.js"]
                + "\n// Keyboard semantics for the custom control.\n"
            )
            toolbar.write_text(
                toolbar.read_text().replace(
                    "root.querySelector('#new').onclick",
                    "root.querySelector('#new').onkeydown = event => {"
                    " if(['Enter',' '].includes(event.key)){event.preventDefault();"
                    "event.currentTarget.click();} };\n"
                    "  root.querySelector('#new').onclick",
                )
            )
            css = w.file("app/app.css")
            css.write_text(
                css.read_text() + "\n#new:focus-visible {outline:2px solid #1859a6;"
                "outline-offset:2px;}\n"
            )
            self.assertEqual(failures(collect_browser(w, "keyboard")), [])

    def test_refactor_oracle_accepts_shared_writer_and_rejects_output_drift(
        self,
    ) -> None:
        case = self.case("refactor-brittle-internal-test")
        check = case.steps[0].checks[0]
        with make_workspace(SOURCE, case) as w:
            baseline = subprocess.run(
                ["python3", "-B", "-m", "unittest", "discover", "-s", "tests"],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(baseline.returncode, 0, baseline.stderr)
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            p = w.file("src/export.py")
            p.write_text("""import csv, io
def _write(items):
    out=io.StringIO(newline='')
    writer=csv.writer(out,lineterminator='\\n')
    writer.writerow(['name','quantity'])
    writer.writerows((row['name'],row['quantity']) for row in items)
    return out.getvalue()
def export_inventory(items):
    return _write(items)
def export_selected(items, selected):
    return _write(row for row in items if row['name'] in selected)
""")
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            p.write_text(p.read_text().replace("if row['name'] in selected", "if True"))
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
