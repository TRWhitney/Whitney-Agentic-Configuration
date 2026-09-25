from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parents[1]
CHECKER_PATH = (
    REPO_ROOT / "skills" / "note-system" / "scripts" / "check_markdown_tables.py"
)


class MarkdownTableCheckerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write_note(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(textwrap.dedent(content).lstrip("\n"), encoding="utf-8")
        return path

    def run_checker(self, *paths: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER_PATH), *(str(path) for path in paths)],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_reports_unescaped_wikilinks_and_embeds_in_table_rows(self) -> None:
        note = self.write_note(
            "broken table.md",
            r"""
            [[Topic|Display]] | Preview
            -- | --
            Topic | ![[diagram.png|200]]
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertIn(f"{note}:1:", result.stdout)
        self.assertIn("[[Topic|Display]]", result.stdout)
        self.assertIn(f"{note}:3:", result.stdout)
        self.assertIn("![[diagram.png|200]]", result.stdout)

    def test_accepts_escaped_pipes_and_ignores_links_outside_tables(self) -> None:
        note = self.write_note(
            "valid.md",
            r"""
            Outside [[Topic|Display]] and ![[diagram.png|200]].

            | Topic | Preview |
            | :-- | --: |
            | [[Topic\|Display]] | ![[diagram.png\|200]] |

            This | is not followed by a delimiter row.
            Another [[Topic|Display]] | prose line.
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_ignores_backtick_and_tilde_fenced_examples(self) -> None:
        note = self.write_note(
            "examples.md",
            r"""
            ```markdown
            | Topic | Meaning |
            | -- | -- |
            | [[Topic|Display]] | Example |
            ```

            ~~~~md
            Topic | Meaning
            -- | --
            [[Topic|Display]] | Example
            ~~~~
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_ignores_fences_in_lists_and_quoted_markers_inside_a_fence(self) -> None:
        note = self.write_note(
            "nested examples.md",
            r"""
            - Outer example:
              - Inner example:

                ```markdown
                Topic | Meaning
                -- | --
                [[Topic|Display]] | Example
                ```

            ````markdown
            > ````
            Topic | Meaning
            -- | --
            [[Topic|Display]] | Example
            ````
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_four_space_indentation_is_not_a_top_level_fence(self) -> None:
        note = self.write_note(
            "indented code.md",
            r"""
                ```markdown

            Topic | Meaning
            -- | --
            [[Topic|Display]] | Broken
            """,
        )
        fenced = self.write_note(
            "fence content.md",
            r"""
            ````markdown
                ````
            Topic | Meaning
            -- | --
            [[Topic|Display]] | Example
            ````
            """,
        )

        violation = self.run_checker(note)
        ignored = self.run_checker(fenced)

        self.assertEqual(violation.returncode, 1)
        self.assertIn(f"{note}:5:", violation.stdout)
        self.assertEqual(ignored.returncode, 0, ignored.stdout + ignored.stderr)

    def test_unclosed_blockquote_fence_ends_with_the_blockquote(self) -> None:
        note = self.write_note(
            "quoted example.md",
            r"""
            > ```markdown
            > Topic | Meaning
            > -- | --
            > [[Topic|Display]] | Example

            Topic | Meaning
            -- | --
            [[Topic|Display]] | Broken
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 1)
        self.assertNotIn(f"{note}:4:", result.stdout)
        self.assertIn(f"{note}:8:", result.stdout)

    def test_ignores_rows_below_a_mismatched_table_header(self) -> None:
        note = self.write_note(
            "not a table.md",
            r"""
            First | Second | Third
            -- | --
            [[Topic|Display]] | Prose
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_even_backslashes_do_not_escape_a_table_pipe(self) -> None:
        note = self.write_note(
            "backslashes.md",
            r"""
            Topic | Meaning
            -- | --
            [[Topic\\|Display]] | Example
            """,
        )

        result = self.run_checker(note)

        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{note}:3:", result.stdout)

    def test_checks_each_explicit_path_and_reports_input_errors_separately(
        self,
    ) -> None:
        valid = self.write_note(
            "valid note.md",
            r"""
            Topic | Meaning
            -- | --
            [[Topic\|Display]] | Example
            """,
        )
        broken = self.write_note(
            "broken note.md",
            r"""
            Topic | Meaning
            -- | --
            [[Topic|Display]] | Example
            """,
        )

        violation = self.run_checker(valid, broken)
        missing = self.run_checker(self.root / "missing.md")

        self.assertEqual(violation.returncode, 1)
        self.assertNotIn(str(valid), violation.stdout)
        self.assertIn(f"{broken}:3:", violation.stdout)
        self.assertEqual(missing.returncode, 2)
        self.assertIn("missing.md", missing.stderr)


if __name__ == "__main__":
    unittest.main()
