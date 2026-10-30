"""New graders distinguish real connections and changes outside the requested view."""

from __future__ import annotations

import re
import shlex
import subprocess
import unittest

from pydantic import JsonValue, TypeAdapter

from evals.fixtures import make_workspace
from evals.models import load_cases
from evals.runner import Observation, check_result
from tests.test_eval_runner import SOURCE


class AcceptedExpansionTests(unittest.TestCase):
    @staticmethod
    def measurements(result: dict[str, JsonValue]) -> list[dict[str, JsonValue]]:
        return TypeAdapter(list[dict[str, JsonValue]]).validate_python(
            result["measurements"]
        )

    def test_working_export_has_broken_guide_examples(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "documentation-examples-run"
        )
        with make_workspace(SOURCE, case) as w:
            check = case.steps[0].checks[0]
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            spec = w.file(".work/export/spec.md")
            spec.write_text(
                spec.read_text() + "\nThe output path may name another CSV file.\n"
            )
            for check in case.steps[0].checks:
                self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            guide = w.file("docs/export.md").read_text()
            for text, expected in (
                (guide, False),
                (guide.replace("--destination", "--output"), True),
            ):
                commands = re.findall(r"```sh\n(.*?)\n```", text, re.DOTALL)
                self.assertEqual(len(commands), 2)
                for command in commands:
                    result = subprocess.run(
                        shlex.split(command), cwd=w.root, capture_output=True, text=True
                    )
                    self.assertEqual(result.returncode == 0, expected, result.stderr)

    def test_storage_requires_real_roundtrip_and_retained_regression(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "mocked-project-connection"
        )
        with make_workspace(SOURCE, case) as w:
            checks = [
                c
                for c in case.steps[0].checks
                if c.kind in {"python_check", "regression_test"}
            ]
            self.assertFalse(check_result(checks[0], Observation(), w, "thread", [])[0])
            store = w.file("src/store.py")
            store.write_text(store.read_text().replace("'count':", "'quantity':"))
            self.assertTrue(check_result(checks[0], Observation(), w, "thread", [])[0])
            self.assertFalse(
                check_result(checks[1], Observation(), w, "thread", [])[0],
                "Mocked project components cannot establish this regression.",
            )
            w.file("tests/test_service.py").write_text("""import tempfile, unittest
from pathlib import Path
from src.service import replace_inventory
class RoundtripTests(unittest.TestCase):
    def test_roundtrip(self):
        rows=[{'name':'Blue mug','quantity':3}]
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(replace_inventory(Path(directory)/'items.json',rows),rows)
""")
            self.assertTrue(check_result(checks[1], Observation(), w, "thread", [])[0])
            doc = w.file("docs/storage.md")
            doc.write_text(
                doc.read_text()
                + "\nAn empty inventory is stored as an empty JSON list.\n"
            )
            for check in case.steps[0].checks:
                self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])

    def test_shared_view_check_rejects_archive_only_regression(self) -> None:
        from evals.gui import collect_browser

        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "gui-shared-change-other-view"
        )
        with make_workspace(SOURCE, case) as w:
            bad = collect_browser(w, "shared-views")
            self.assertFalse(bad["matched"])
            failures = [m["name"] for m in self.measurements(bad) if not m["matched"]]
            self.assertTrue(failures)
            self.assertTrue(
                all(str(name).startswith("archive/") for name in failures), failures
            )
            css = w.file("app/app.css")
            original = css.read_text()
            css.write_text(original.replace("300px minmax", "220px minmax"))
            rollback = collect_browser(w, "shared-views")
            self.assertFalse(
                rollback["matched"],
                "Global rollback loses the requested workspace change.",
            )
            self.assertTrue(
                any(
                    str(m["name"]).startswith("workspace/") and not m["matched"]
                    for m in self.measurements(rollback)
                )
            )
            css.write_text(original)
            css.write_text(
                css.read_text() + "\n.archive .preference-row {"
                "grid-template-columns:220px minmax(0,1fr) auto;}\n"
                "@media(max-width:700px){.archive .preference-row {"
                "grid-template-columns:minmax(0,1fr) auto;}}\n"
            )
            good = collect_browser(w, "shared-views")
            self.assertTrue(
                good["matched"],
                [m for m in self.measurements(good) if not m["matched"]],
            )
            # Alternate scoping and markup must also work.
            archive = w.file("app/archive.html")
            archive.write_text(
                archive.read_text().replace(
                    'class="shell archive"', 'class="shell records"'
                )
            )
            css.write_text(css.read_text().replace(".archive ", ".records "))
            self.assertTrue(collect_browser(w, "shared-views")["matched"])
