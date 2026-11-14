from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipapp
from pathlib import Path

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "evals/cases/fixtures/inventory-cli.json"
)


class ProjectEvalFixtureTests(unittest.TestCase):
    def test_inventory_workflow_survives_packaging_and_failed_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, text in json.loads(FIXTURE.read_text()).items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
            inventory = root / "inventory.json"
            archive = root / "field-shelf.pyz"
            zipapp.create_archive(root / "src", archive)

            def invoke(
                program: Path, *arguments: str
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [sys.executable, str(program), str(inventory), *arguments],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            added = invoke(root / "src", "add", "Hämmer", "2")
            self.assertEqual(added.returncode, 0, added.stderr)
            stock = root / "stock.csv"
            stock.write_text('name,quantity\n"Nails, steel",5\n')
            imported = invoke(archive, "import", str(stock))
            self.assertEqual(imported.returncode, 0, imported.stderr)
            listed = invoke(archive, "list")
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertEqual(
                json.loads(listed.stdout),
                [
                    {"name": "Hämmer", "quantity": 2},
                    {"name": "Nails, steel", "quantity": 5},
                ],
            )
            before = inventory.read_bytes()
            stock.write_text("name,quantity\nScrew,3\nBolt,-1\n")
            self.assertNotEqual(invoke(archive, "import", str(stock)).returncode, 0)
            self.assertEqual(inventory.read_bytes(), before)
