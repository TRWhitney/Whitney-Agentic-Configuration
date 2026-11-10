from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


@unittest.skipUnless(
    shutil.which("bwrap") and importlib.util.find_spec("openai_codex"),
    "Isolation probes require the optional SDK and existing bubblewrap.",
)
class RuntimeIsolationTests(unittest.TestCase):
    def test_attempt_can_use_own_files_but_cannot_read_other_attempt_or_private_cases(
        self,
    ) -> None:
        from evals.isolation import RuntimeIsolation

        with (
            tempfile.TemporaryDirectory(prefix="attempt-") as own,
            tempfile.TemporaryDirectory(prefix="other-attempt-") as other,
        ):
            root = Path(own)
            (root / "own.txt").write_text("own")
            foreign = Path(other) / "helper.py"
            foreign.write_text("other attempt")
            private = Path(__file__).resolve().parents[1] / "evals/cases"
            isolation = RuntimeIsolation(root)
            code = (
                "from pathlib import Path; import sys; "
                'assert Path(sys.argv[1]).read_text()=="own"; '
                "assert not Path(sys.argv[2]).exists(); "
                "assert not Path(sys.argv[3]).exists(); "
                'Path(sys.argv[4]).write_text("private capture")'
            )
            result = subprocess.run(
                isolation.command(
                    [
                        sys.executable,
                        "-c",
                        code,
                        str(root / "own.txt"),
                        str(foreign),
                        str(private),
                        str(isolation.scratch / "capture.png"),
                    ],
                    cwd=root,
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (isolation.scratch / "capture.png").read_text(),
                "private capture",
            )
            self.assertFalse((root / "capture.png").exists())

    def test_candidate_can_commit_to_its_disposable_git_repository(self) -> None:
        from evals.isolation import RuntimeIsolation

        with tempfile.TemporaryDirectory(prefix="attempt-git-") as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            isolation = RuntimeIsolation(root)
            result = subprocess.run(
                isolation.command(
                    [
                        "git",
                        "-c",
                        "user.name=Example",
                        "-c",
                        "user.email=example@example.com",
                        "commit",
                        "--allow-empty",
                        "-m",
                        "Fixture change",
                    ],
                    cwd=root,
                ),
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                subprocess.check_output(
                    ["git", "rev-list", "--count", "HEAD"], cwd=root, text=True
                ).strip(),
                "1",
            )

    def test_judge_can_read_but_cannot_modify_its_evidence(self) -> None:
        from evals.isolation import RuntimeIsolation

        with tempfile.TemporaryDirectory(prefix="judge-evidence-") as temporary:
            root = Path(temporary)
            evidence = root / "source.txt"
            evidence.write_text("original")
            isolation = RuntimeIsolation(root, read_only=True)
            script = (
                "from pathlib import Path; import sys; p=Path(sys.argv[1]); "
                'assert p.read_text()=="original"; p.write_text("changed")'
            )
            result = subprocess.run(
                isolation.command(
                    [sys.executable, "-c", script, str(evidence)], cwd=root
                ),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(evidence.read_text(), "original")
