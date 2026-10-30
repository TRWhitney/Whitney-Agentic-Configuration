from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from evals.models import CaseSpec, CompactStep, load_cases, select_cases


class CaseDefinitionTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def write_case(self, name: str, **updates: object) -> None:
        case: dict[str, object] = {
            "id": name,
            "tags": ["workflow"],
            "files": {"src/app.py": "def value():\n    return 1\n"},
            "steps": [
                {
                    "kind": "message",
                    "prompt": "Explain the current behavior.",
                    "checks": [{"kind": "unchanged", "paths": ["src/app.py"]}],
                }
            ],
            **updates,
        }
        (self.root / f"{name}.json").write_text(json.dumps(case))

    def test_selects_cases_without_running_a_model(self) -> None:
        self.write_case("planning")
        self.write_case(
            "compaction",
            integration=True,
            steps=[
                {"kind": "compact", "checks": [{"kind": "tracker", "name": "local"}]}
            ],
        )
        cases = load_cases(self.root)
        self.assertEqual(
            [
                case.id
                for case in select_cases(
                    cases, ids=set(), tags=set(), integration=False
                )
            ],
            ["planning"],
        )
        self.assertEqual(
            len(select_cases(cases, ids=set(), tags=set(), integration=True)), 2
        )

    def test_rejects_invalid_cases_before_execution(self) -> None:
        for updates in (
            {"files": {"../outside": "text"}},
            {"unexpected": True},
            {"steps": [{"kind": "compact"}]},
            {
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue",
                        "checks": [{"kind": "reply_regex", "pattern": "["}],
                    }
                ]
            },
            {
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue",
                        "checks": [{"kind": "command_regex", "pattern": "["}],
                    }
                ]
            },
            {
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue",
                        "checks": [
                            {
                                "kind": "file_regex",
                                "path": "src/app.py",
                                "pattern": "[",
                            }
                        ],
                    }
                ]
            },
        ):
            with self.subTest(updates=updates):
                self.write_case("invalid", **updates)
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_rejects_a_case_without_any_checks(self) -> None:
        self.write_case("unchecked", steps=[{"kind": "message", "prompt": "Continue"}])
        with self.assertRaises(ValueError):
            load_cases(self.root)

    def test_shared_fixtures_are_reused_and_case_files_can_override_them(self) -> None:
        directory = self.root / "fixtures"
        directory.mkdir()
        (directory / "inventory.json").write_text(
            json.dumps({"src/app.py": "original\n", "docs/inventory.md": "Inventory\n"})
        )
        self.write_case(
            "first", fixtures=["inventory"], files={"src/app.py": "override\n"}
        )
        self.write_case("second", fixtures=["inventory"], files={})
        cases = {case.id: case for case in load_cases(self.root)}
        self.assertEqual(cases["first"].files["src/app.py"], "override\n")
        self.assertEqual(cases["second"].files["src/app.py"], "original\n")
        self.assertEqual(cases["first"].files["docs/inventory.md"], "Inventory\n")

    def test_rejects_unsafe_paths_in_setup_steps_and_checks(self) -> None:
        for path in (
            "/outside",
            "../outside",
            "a/../b",
            "a\\b",
            "C:/outside",
            "./a",
            "a\x00b",
        ):
            for updates in (
                {"files": {"src/app.py": "text", path: "text"}},
                {"uncommitted_files": {path: "text"}},
                {
                    "steps": [
                        {
                            "kind": "seed",
                            "workflow": "novel-work",
                            "state": "planning",
                            "record": path,
                        }
                    ]
                },
                {
                    "steps": [
                        {
                            "kind": "message",
                            "prompt": "Continue",
                            "checks": [
                                {"kind": "file_equals", "path": path, "text": "text"}
                            ],
                        }
                    ]
                },
            ):
                with self.subTest(path=path, updates=updates):
                    self.write_case("unsafe", **updates)
                    with self.assertRaises(ValueError):
                        load_cases(self.root)

    def test_rejects_git_setup_and_conflicting_file_paths(self) -> None:
        for files in (
            {".git/config": "text"},
            {".GIT": "text"},
            {"a": "text", "a/b": "text"},
        ):
            with self.subTest(files=files):
                self.write_case("unsafe", files={"src/app.py": "text", **files})
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_uncommitted_files_cannot_change_git_metadata_or_conflict_with_paths(
        self,
    ) -> None:
        for files, edits in (
            ({"src/app.py": "text"}, {".git/config": "text"}),
            ({"src/app.py": "text"}, {".GIT": "text"}),
            ({"a": "text"}, {"a/b": "text"}),
            ({"a/b": "text"}, {"a": "text"}),
            ({"src/app.py": "text"}, {"a": "text", "a/b": "text"}),
        ):
            with self.subTest(files=files, edits=edits):
                self.write_case("unsafe", files=files, uncommitted_files=edits)
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_rejects_unknown_check_kinds_and_bad_references(self) -> None:
        for steps in (
            [{"kind": "message", "prompt": "Continue", "checks": [{"kind": "shell"}]}],
            [
                {
                    "kind": "message",
                    "prompt": "Continue",
                    "checks": [{"kind": "unchanged", "paths": ["missing.py"]}],
                }
            ],
            [
                {
                    "kind": "seed",
                    "workflow": "novel-work",
                    "state": "planning",
                    "record": "missing.md",
                }
            ],
            [{"kind": "message", "conversation": "../other", "prompt": "Continue"}],
        ):
            with self.subTest(steps=steps):
                self.write_case("invalid", steps=steps)
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_rejects_coercion_and_unknown_nested_fields(self) -> None:
        for updates in (
            {"integration": "false"},
            {"tags": "workflow"},
            {"files": {"src/app.py": 42}},
            {"steps": [{"kind": "message", "prompt": 42}]},
            {
                "steps": [{"kind": "compact", "setup_code": "run()"}],
                "integration": True,
            },
            {
                "steps": [
                    {
                        "kind": "message",
                        "prompt": "Continue",
                        "checks": [{"kind": "commit_count", "count": True}],
                    }
                ]
            },
        ):
            with self.subTest(updates=updates):
                self.write_case("invalid", **updates)
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_rejects_empty_corpus_empty_steps_and_duplicate_ids(self) -> None:
        with self.assertRaises(ValueError):
            load_cases(self.root)
        self.write_case("empty", steps=[])
        with self.assertRaises(ValueError):
            load_cases(self.root)
        (self.root / "empty.json").unlink()
        self.write_case("one", id="same")
        self.write_case("two", id="same")
        with self.assertRaisesRegex(ValueError, "duplicate case ID"):
            load_cases(self.root)

    def test_verification_checks_reject_bad_patterns_codes_and_script_references(
        self,
    ) -> None:
        for check in (
            {"kind": "command_sequence", "commands": []},
            {
                "kind": "command_sequence",
                "commands": [{"pattern": "[", "exit_code": 0}],
            },
            {
                "kind": "command_sequence",
                "commands": [{"pattern": "run", "exit_code": True}],
            },
            {
                "kind": "command_sequence",
                "commands": [{"pattern": "run", "exit_code": 0, "output_pattern": "["}],
            },
            {"kind": "python_check", "path": "missing.py"},
            {"kind": "python_check", "path": "../outside.py"},
        ):
            with self.subTest(check=check):
                self.write_case(
                    "invalid",
                    steps=[
                        {"kind": "message", "prompt": "Run checks.", "checks": [check]}
                    ],
                )
                with self.assertRaises(ValueError):
                    load_cases(self.root)

    def test_selection_combines_ids_tags_and_integration_opt_in(self) -> None:
        self.write_case("alpha", tags=["planning", "recovery"])
        self.write_case("beta", tags=["planning"])
        self.write_case("gamma", tags=["recovery"], integration=True)
        cases = load_cases(self.root)
        selected = select_cases(
            cases, ids={"alpha", "beta"}, tags={"recovery"}, integration=False
        )
        self.assertEqual([case.id for case in selected], ["alpha"])
        selectors: list[tuple[set[str], set[str], bool]] = [
            ({"missing"}, set(), True),
            ({"gamma"}, set(), False),
            (set(), {"missing"}, True),
        ]
        for ids, tags, integration in selectors:
            with self.subTest(ids=ids, tags=tags), self.assertRaises(ValueError):
                select_cases(cases, ids=ids, tags=tags, integration=integration)

    def test_starter_cases_remain_covered_and_compaction_requires_opt_in(self) -> None:
        cases = load_cases(Path(__file__).resolve().parents[1] / "evals/cases")
        self.assertGreaterEqual(
            {case.id for case in cases},
            {
                "incomplete-design",
                "planning-pr-unmerged",
                "local-tracking",
                "seeded-wayfinding-recovery",
                "narrow-correction",
                "separate-conversations",
                "explicit-compaction",
                "wayfinding-follow-up",
                "wayfinding-short-replies",
                "wayfinding-counts",
                "wayfinding-stop",
                "wayfinding-revised-answer",
                "wayfinding-blocked-question",
                "wayfinding-code-question",
                "question-before-change",
                "amend-preserves-earlier-edit",
                "missing-implementation-ticket",
                "planning-continue-discussion",
                "tracker-separate-conversations",
                "wayfinding-complete",
                "changed-decision-tickets",
                "outdated-recap",
                "prototype-returns-to-planning",
                "related-feature-questions",
                "partial-completion",
                "ready-implementation",
                "preserve-uncommitted-work",
                "replace-workflow",
                "failed-verification",
                "unavailable-verification",
                "reproducible-bug",
            },
        )
        compaction_cases = [
            case
            for case in cases
            if any(isinstance(step, CompactStep) for step in case.steps)
        ]
        self.assertIn("explicit-compaction", {case.id for case in compaction_cases})
        self.assertTrue(all(case.integration for case in compaction_cases))
        routine = select_cases(cases, ids=set(), tags=set(), integration=False)
        self.assertTrue(
            all(
                not isinstance(step, CompactStep)
                for case in routine
                for step in case.steps
            )
        )
        json.dumps(CaseSpec.model_json_schema())


if __name__ == "__main__":
    unittest.main()
