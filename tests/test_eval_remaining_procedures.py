"""Accepted contracts distinguish useful tests and complete measurements."""

from __future__ import annotations

import subprocess
import unittest

from evals.fixtures import make_workspace
from evals.models import CaseSpec, load_cases
from evals.runner import Observation, check_result
from tests.test_eval_runner import SOURCE


class RemainingProcedureTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_individual_worker_checks_do_not_prove_the_command(self) -> None:
        case = self.case("delegated-parts-fail-together")
        with make_workspace(SOURCE, case) as w:
            for name in ["check_reader.py", "check_totals.py"]:
                result = subprocess.run(
                    ["python3", "-B", "checks/" + name],
                    cwd=w.root,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
            check = case.steps[-1].checks[0]
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            source = w.file("src/import_summary.py")
            source.write_text(
                source.read_text().replace(
                    "    print(summarize(rows))",
                    '    rows=[{**row,"quantity":int(row["quantity"])} '
                    "for row in rows]\n"
                    "    print(summarize(rows))",
                )
            )
            self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            source.write_text(source.read_text().replace('int(row["quantity"])', "1"))
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_service_oracle_accepts_alternative_encoders_and_rejects_fake_delivery(
        self,
    ) -> None:
        case = self.case("contractual-service-interaction")
        check = case.steps[-1].checks[0]
        with make_workspace(SOURCE, case) as w:
            self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])
            source = w.file("src/publisher.py")
            for writer in [
                "writer.writerows((r['name'],r['quantity']) for r in items)",
                "\n    for row in items: "
                "writer.writerow([row['name'],row['quantity']])",
            ]:
                source.write_text(
                    """import csv,io
def publish_inventory(items,client):
    out=io.StringIO(newline='')
    writer=csv.writer(out,lineterminator='\\n')
    writer.writerow(['name','quantity'])
    """
                    + writer
                    + """
    ticket=client.start()
    client.write(ticket,out.getvalue().encode('utf-8'))
    return client.finish(ticket)
"""
                )
                self.assertTrue(check_result(check, Observation(), w, "thread", [])[0])
            correct = source.read_text()
            for bad in [
                correct.replace(
                    "client.write(ticket,out.getvalue().encode('utf-8'))",
                    'client.write(ticket,b"name,quantity\\n")',
                ),
                correct.replace("return client.finish(ticket)", 'return "Uploaded"'),
                correct.replace(
                    "return client.finish(ticket)", "return client.finish(object())"
                ),
            ]:
                source.write_text(bad)
                self.assertFalse(check_result(check, Observation(), w, "thread", [])[0])

    def test_existing_measurement_excludes_snapshot_wait(self) -> None:
        case = self.case("experiment-measures-partial-operation")
        with make_workspace(SOURCE, case) as w:
            # Count elapsed waits deterministically instead of timing this unit test.
            result = subprocess.run(
                [
                    "python3",
                    "-B",
                    "-c",
                    """from unittest.mock import patch
from src import export
waits=[]
with patch.object(export.time,'sleep',side_effect=waits.append):
    rows=export.load_snapshot()
    assert waits==[0.150]
    waits.clear()
    export.render_csv(rows)
    assert waits==[]
    assert export.export_inventory()=='name,quantity\\nCup,2\\nPlate,0\\n'
    assert waits==[0.150]
""",
                ],
                cwd=w.root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
