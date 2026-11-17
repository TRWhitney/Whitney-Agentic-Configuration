"""Offline contracts for the performance tasks; no candidate or judge model calls."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from typing import ClassVar, TypedDict, cast

from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, load_cases
from evals.runner import Observation, check_result
from tests.eval_support import observe_case
from tests.test_eval_runner import SOURCE


class ReportResult(TypedDict):
    items: list[dict[str, str | int]]
    quantity: int


class Receipt(TypedDict, total=False):
    elapsed_ms: float
    completed: int
    errors: int
    submitted: int
    labels_per_second: float
    labels: list[dict[str, str]]
    result: ReportResult
    csv: str
    items: list[dict[str, str | int | bool]]


SNAPSHOT_REPORT = """\ndef build_report(rows, catalog_path):
    catalog = load_catalog(catalog_path) if rows else {}
    items = [{"order": row["order"], "sku": row["sku"],
              "name": catalog.get(row["sku"], "Unknown"),
              "quantity": row["quantity"]} for row in rows]
    return {"items": items, "quantity": sum(row["quantity"] for row in rows)}
"""

PER_SKU_REPORT = """\ndef build_report(rows, catalog_path):
    names = {}
    items = []
    for row in rows:
        sku = row["sku"]
        if sku not in names:
            names[sku] = load_catalog(catalog_path).get(sku, "Unknown")
        items.append(dict(order=row["order"], sku=sku,
                          name=names[sku], quantity=row["quantity"]))
    return dict(items=items, quantity=sum(row["quantity"] for row in rows))
"""

STALE_REPORT = """\n_cached = {}
def build_report(rows, catalog_path):
    key = str(catalog_path)
    if key not in _cached:
        _cached[key] = load_catalog(catalog_path)
    catalog = _cached[key]
    items = [{"order": row["order"], "sku": row["sku"],
              "name": catalog.get(row["sku"], "Unknown"),
              "quantity": row["quantity"]} for row in rows]
    return {"items": items, "quantity": sum(row["quantity"] for row in rows)}
"""


class PerformanceCaseTests(unittest.TestCase):
    cases: ClassVar[dict[str, CaseSpec]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = {
            c.id: c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id.startswith("performance-")
        }

    def case(self, name: str) -> CaseSpec:
        return self.cases["performance-" + name]

    def run_python(self, workspace: Workspace, *args: str) -> str:
        result = subprocess.run(
            [sys.executable, "-B", *args],
            cwd=workspace.root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def receipt(self, workspace: Workspace, *args: str) -> Receipt:
        return cast(Receipt, json.loads(self.run_python(workspace, *args)))

    def report_source(self, case: CaseSpec, implementation: str) -> str:
        return (
            case.files["src/report.py"].split("def build_report", 1)[0] + implementation
        )

    def grader_passes(self, case: CaseSpec, workspace: Workspace) -> bool:
        check = next(c for c in case.steps[-1].checks if c.kind == "python_check")
        return check_result(check, Observation(), workspace, "thread", [])[0]

    def test_corpus_is_four_tasks_and_a_bounded_single_run_control(self) -> None:
        self.assertEqual(len(self.cases), 5)
        for case in self.cases.values():
            with self.subTest(case=case.id):
                self.assertIn("performance", case.tags)
                self.assertIn(case.purpose, {"task", "control"})
                self.assertGreaterEqual(len(case.rubric), 3)
                self.assertLessEqual(len(case.rubric), 6)
                # Public inputs do not prescribe the hidden measurement process.
                public = "\n".join(
                    [*case.files.values()]
                    + [s.prompt for s in case.steps if s.kind == "message"]
                )
                self.assertNotIn("at least five", public)
                self.assertNotIn("alternating A/B", public)
                self.assertNotIn("statistical test", public)
                self.assertNotIn("grading/", public)
        control = self.case("rough-single-run-control")
        self.assertEqual(control.purpose, "control")
        self.assertFalse(any(step.kind == "seed" for step in control.steps))
        self.assertFalse(
            any(
                c.kind in {"command_sequence", "action_sequence", "command_regex"}
                for c in control.steps[-1].checks
            )
        )

    def test_label_cli_rate_counts_submitted_instead_of_completed_work(self) -> None:
        case = self.case("completed-work-discovery")
        with make_workspace(SOURCE, case) as w:
            receipt = self.receipt(w, "tools/label_rate.py")
            orders = json.loads(w.file("data/orders.json").read_text())
            self.assertEqual(receipt["submitted"], 120)
            self.assertEqual(receipt["completed"], 12)
            self.assertEqual(len(receipt["labels"]), 12)
            self.assertEqual(
                [label["order"] for label in receipt["labels"]],
                [row["order"] for row in orders[:12]],
            )
            elapsed_seconds = receipt["elapsed_ms"] / 1000
            completed_rate = receipt["completed"] / elapsed_seconds
            self.assertAlmostEqual(receipt["labels_per_second"] / completed_rate, 10)
            self.assertNotEqual(receipt["completed"], len(orders))
            # The source bound independently settles the accepted throughput target.
            self.assertLess(120 / (120 * 0.001), 5000)

    def test_report_cli_accepts_original_and_two_real_optimizations(self) -> None:
        case = self.case("repeated-catalog-implementation")
        baseline = case.files["src/report.py"]
        for source, expected_wait in (
            (baseline, 0.192),
            (self.report_source(case, SNAPSHOT_REPORT), 0.003),
            (self.report_source(case, PER_SKU_REPORT), 0.009),
        ):
            with (
                self.subTest(expected_wait=expected_wait),
                make_workspace(SOURCE, case) as w,
            ):
                w.file("src/report.py").write_text(source)
                self.assertIn(
                    "Report CLI contract passed",
                    self.run_python(w, "checks/report_contract.py"),
                )
                self.assertTrue(self.grader_passes(case, w))
                # Sum modeled waits deterministically, outside reported timing runs.
                output = self.run_python(
                    w,
                    "-c",
                    """import json
from unittest.mock import patch
from src import report
rows=json.load(open('data/orders.json'))
waits=[]
with patch.object(report.time,'sleep',side_effect=waits.append):
    result=report.build_report(rows,'data/catalog.json')
assert len(result['items'])==64
assert result['quantity']==sum(r['quantity'] for r in rows)
print(sum(waits))
""",
                )
                self.assertAlmostEqual(float(output), expected_wait)

    def test_report_checker_accepts_an_imported_sleep_alias(self) -> None:
        case = self.case("repeated-catalog-implementation")
        source = (
            self.report_source(case, SNAPSHOT_REPORT)
            .replace("import time", "from time import sleep")
            .replace("time.sleep(0.003)", "sleep(0.003)")
        )
        with make_workspace(SOURCE, case) as w:
            w.file("src/report.py").write_text(source)
            self.assertTrue(self.grader_passes(case, w))

    def test_report_checker_accepts_renaming_a_private_adapter_helper(self) -> None:
        case = self.case("repeated-catalog-implementation")
        source = self.report_source(case, SNAPSHOT_REPORT).replace(
            "load_catalog", "read_catalog"
        )
        with make_workspace(SOURCE, case) as w:
            w.file("src/report.py").write_text(source)
            self.assertTrue(self.grader_passes(case, w))

    def test_seeded_cases_resume_through_the_real_navigator(self) -> None:
        for case in self.cases.values():
            for step in case.steps:
                if step.kind == "seed":
                    with self.subTest(case=case.id), make_workspace(SOURCE, case) as w:
                        w.seed("performance-offline", step)
                        progress = w.progress("performance-offline")
                        assert progress is not None
                        self.assertEqual(progress["state"], step.state)
                        self.assertIn(
                            "performance",
                            w.navigate("performance-offline", ["resume"]).lower(),
                        )

    def test_report_checker_rejects_skipped_rows_stale_cache_and_fabricated_totals(
        self,
    ) -> None:
        case = self.case("repeated-catalog-implementation")
        valid = self.report_source(case, SNAPSHOT_REPORT)
        for source in (
            self.report_source(case, STALE_REPORT),
            valid.replace("for row in rows]", "for row in rows[:1]]"),
            valid.replace('sum(row["quantity"] for row in rows)', "64"),
            valid.replace('catalog.get(row["sku"], "Unknown")', '"Unknown"'),
        ):
            with self.subTest(source=source), make_workspace(SOURCE, case) as w:
                w.file("src/report.py").write_text(source)
                self.assertFalse(self.grader_passes(case, w))

    def test_report_checker_rejects_removing_the_accepted_adapter_wait(self) -> None:
        case = self.case("repeated-catalog-implementation")
        source = self.report_source(case, SNAPSHOT_REPORT)
        source = source.replace("    time.sleep(0.003)\n", "")
        with make_workspace(SOURCE, case) as w:
            w.file("src/report.py").write_text(source)
            self.assertFalse(self.grader_passes(case, w))

    def test_report_checker_rejects_bypassing_the_storage_adapter(self) -> None:
        case = self.case("repeated-catalog-implementation")
        source = self.report_source(case, SNAPSHOT_REPORT).replace(
            "catalog = load_catalog(catalog_path) if rows else {}",
            "catalog = json.loads(Path(catalog_path).read_text()) if rows else {}",
        )
        with make_workspace(SOURCE, case) as w:
            w.file("src/report.py").write_text(source)
            self.assertFalse(self.grader_passes(case, w))

    def test_report_checker_rejects_false_cli_completion_and_missing_payload(
        self,
    ) -> None:
        case = self.case("repeated-catalog-implementation")
        for bad_cli in (
            case.files["tools/report.py"].replace("len(result['items'])", "999"),
            case.files["tools/report.py"].replace("'result':result", "'result':{}"),
        ):
            with self.subTest(cli=bad_cli), make_workspace(SOURCE, case) as w:
                w.file("src/report.py").write_text(
                    self.report_source(case, SNAPSHOT_REPORT)
                )
                w.file("tools/report.py").write_text(bad_cli)
                self.assertFalse(self.grader_passes(case, w))

    def test_export_helper_and_complete_cli_preserve_results_but_differ_in_scope(
        self,
    ) -> None:
        case = self.case("completed-change-validation")
        with make_workspace(SOURCE, case) as w:
            receipts = [
                self.receipt(
                    w, "tools/measure.py", "--variant", variant, "--scope", scope
                )
                for variant in ("before", "after")
                for scope in ("render", "export")
            ]
            self.assertEqual(len({r["csv"] for r in receipts}), 1)
            self.assertTrue(all(r["completed"] == 80 for r in receipts))
            self.assertTrue(all(r["errors"] == 0 for r in receipts))
            # Deterministic source observations demonstrate a sufficient lower bound.
            self.run_python(
                w,
                "-c",
                """from unittest.mock import patch
from src import export
rows=[{'order':'Comma, quote "','quantity':0}]
waits=[]
with patch.object(export.time,'sleep',side_effect=waits.append):
    a=export.export(rows,'before')
    assert waits==[0.090,0.001]
    waits.clear()
    b=export.export(rows,'after')
    assert waits==[0.090]
assert a==b
import csv,io
parsed=list(csv.reader(io.StringIO(a['csv'])))
assert parsed==[['order','quantity'],['Comma, quote "','0']]
assert a['completed']==1 and a['errors']==0
""",
            )
            self.assertGreater(0.090 * 1000, 50)

    def test_lookup_public_engines_consume_same_complete_work(self) -> None:
        case = self.case("close-engine-comparison")
        with make_workspace(SOURCE, case) as w:
            rows = json.loads(w.file("data/locations.json").read_text())
            expected = [row for row in rows if row["enabled"]]
            for engine in ("direct", "buffered"):
                receipt = self.receipt(w, "tools/lookup.py", "--engine", engine)
                self.assertEqual(receipt["items"], expected)
                self.assertEqual(receipt["completed"], 60)
                self.assertEqual(receipt["errors"], 0)
                self.assertGreater(receipt["elapsed_ms"], 0)
            # Filtering output is not permission to omit input work from accounting.
            self.assertEqual(len(expected), 40)
            self.assertNotEqual(len(expected), len(rows))
            self.run_python(
                w,
                "-c",
                """import json
from unittest.mock import patch
from src import lookup
encoded=open('data/locations.json').read()
with patch.object(lookup.random,'uniform',return_value=0.021), \\
     patch.object(lookup.time,'sleep') as sleep:
    direct=lookup.lookup(encoded,'direct')
    buffered=lookup.lookup(encoded,'buffered')
assert direct==buffered
assert [c.args for c in sleep.call_args_list]==[(0.021,),(0.021,)]
""",
            )

    def test_single_run_control_checks_the_whole_report_without_a_comparison(
        self,
    ) -> None:
        case = self.case("rough-single-run-control")
        with make_workspace(SOURCE, case) as w:
            receipt = self.receipt(w, "tools/report.py")
            rows = json.loads(w.file("data/orders.json").read_text())
            catalog = json.loads(w.file("data/catalog.json").read_text())
            expected = [
                {**row, "name": catalog.get(row["sku"], "Unknown")} for row in rows
            ]
            self.assertEqual(receipt["result"]["items"], expected)
            self.assertEqual(
                receipt["result"]["quantity"], sum(r["quantity"] for r in rows)
            )
            self.assertEqual(receipt["completed"], 64)
            self.assertEqual(receipt["errors"], 0)
            self.assertGreater(receipt["elapsed_ms"], 0)
        # This only calibrates mechanical scope; the rubric requires observed execution.
        result = observe_case(
            case, {}, "Single-run local modeled estimate: 200ms for 64 correct rows."
        )
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        changed = dict(case.files)
        changed["src/report.py"] = self.report_source(case, SNAPSHOT_REPORT)
        result = observe_case(
            case, {"src/report.py": changed["src/report.py"]}, "Faster."
        )
        self.assertEqual(result.mechanical_status, "fail")


if __name__ == "__main__":
    unittest.main()
