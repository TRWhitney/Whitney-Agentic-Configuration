from __future__ import annotations

import unittest

from evals.assessment import blind_packet
from evals.evidence import EvidenceRun
from evals.models import CaseSpec, load_cases
from evals.runner import CommandResult
from tests.test_eval_runner import SOURCE, capture_case

RECORD = ".work/export/status.md"
DESIGN = "docs/planning/export/design.md"
MAP = "docs/planning/export/map.md"
SPEC = ".work/export/spec.md"
IMPLEMENTATION = ".work/export/tickets/01-export-text.md"
TESTS = ".work/export/tickets/02-export-tests.md"
UNRELATED = ".work/totals/tickets/01-stock-total.md"


class PlanningCaseChecksTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def assert_unassessed(
        self,
        case: CaseSpec,
        changes: dict[str, str],
        reply: str,
        *,
        progress: tuple[str, str | None] | None = None,
    ) -> EvidenceRun:
        result, evidence = capture_case(case, changes, reply, progress=progress)
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        self.assertIsNone(result.assessment)
        packet, _ = blind_packet(case.rubric, [evidence])
        self.assertEqual(
            packet["criteria"], [c.model_dump(mode="json") for c in case.rubric]
        )
        for path, text in changes.items():
            self.assertEqual(evidence.frames[-1].files[path], text)
        return evidence

    def test_wayfinding_completion_checks_state_and_captures_saved_answers(
        self,
    ) -> None:
        case = self.case("wayfinding-complete")
        resolved = case.files[DESIGN].replace("claimed", "resolved")
        start, end = (
            resolved.index("## Questions"),
            resolved.index("## Accepted answers"),
        )
        resolved = resolved[:start] + "## Questions\n\nNone.\n\n" + resolved[end:]
        resolved += "\nInclude the name,quantity header row.\n"
        changes = {
            DESIGN: resolved,
            MAP: "## Decisions so far\n\nInclude name,quantity headings.\n",
            RECORD: (
                "Planning continues. Specification and implementation tickets remain.\n"
            ),
        }
        reply = "The specification and implementation tickets remain."
        for updates in (changes, {}, {**changes, MAP: case.files[MAP]}):
            with self.subTest(updates=updates):
                self.assert_unassessed(
                    case, updates, reply, progress=("planning", None)
                )
        for updates, progress in (
            (changes, ("planning", "wayfinding")),
            (changes, ("implementation", None)),
            (
                {**changes, "src/export.py": "def export_rows(items): pass\n"},
                ("planning", None),
            ),
        ):
            with self.subTest(progress=progress, updates=updates):
                result, _ = capture_case(case, updates, reply, progress=progress)
                self.assertEqual(result.mechanical_status, "fail")
                self.assertEqual(result.status, "fail")

    def test_changed_answers_and_stale_tickets_enter_hidden_assessment(self) -> None:
        case = self.case("changed-decision-tickets")
        changes = {
            path: case.files[path]
            .replace(
                'raises ValueError("Inventory is empty.") without returning CSV text.',
                'returns a header-only CSV, exactly "name,quantity\\n".',
            )
            .replace(
                'raise ValueError("Inventory is empty.").',
                'return a header-only CSV, exactly "name,quantity\\n".',
            )
            .replace("refuses empty input", "returns a header-only CSV for empty input")
            for path in (RECORD, DESIGN, MAP, SPEC, IMPLEMENTATION, TESTS)
        }
        reply = 'Empty input returns exactly "name,quantity\\n", with no data rows.'
        self.assert_unassessed(case, changes, reply)
        for stale in changes:
            with self.subTest(stale=stale):
                updates = {p: text for p, text in changes.items() if p != stale}
                evidence = self.assert_unassessed(case, updates, reply)
                self.assertEqual(evidence.frames[-1].files[stale], case.files[stale])
        conflicting = {
            **changes,
            TESTS: changes[TESTS] + '\nExpect ValueError("Inventory is empty.").\n',
        }
        self.assert_unassessed(case, conflicting, reply)
        for path, text in (
            (UNRELATED, "Changed the unrelated totals ticket.\n"),
            ("src/export.py", "def export_rows(items): pass\n"),
        ):
            with self.subTest(path=path):
                result, _ = capture_case(case, {**changes, path: text}, reply)
                self.assertEqual(result.mechanical_status, "fail")

    def test_outdated_recap_evidence_retains_the_conflict_and_each_reply(self) -> None:
        case = self.case("outdated-recap")
        answers = (
            "The recap is outdated. Empty input raises ValueError; "
            "headings remain open.",
            "Empty input returns header-only CSV. Headings are agreed.",
            "Empty input raises ValueError. Whether to include headings remains open.",
        )
        for answer in answers:
            with self.subTest(answer=answer):
                evidence = self.assert_unassessed(case, {}, answer)
                self.assertIn("previous assistant recap", evidence.frames[0].prompt)
                self.assertEqual(evidence.frames[-1].reply, answer)
                self.assertEqual(evidence.frames[-1].files[DESIGN], case.files[DESIGN])
        for path in (DESIGN, MAP, RECORD):
            result, _ = capture_case(
                case, {path: "Use the old recap instead.\n"}, answers[0]
            )
            self.assertEqual(result.mechanical_status, "fail")
        result, _ = capture_case(case, {}, answers[0], progress=("planning", None))
        self.assertEqual(result.mechanical_status, "fail")

    def test_prototype_can_keep_the_sample_as_csv(self) -> None:
        case = self.case("prototype-returns-to-planning")
        source = case.files["prototypes/export_csv_probe.py"]
        changes = {
            "prototypes/export_csv_probe.py": source.replace(
                'Path(__file__).with_suffix(".result.json").write_text(',
                'Path(__file__).with_suffix(".sample.csv").write_text(',
            ),
            "prototypes/export_csv_probe.sample.csv": '"Tea, loose",2\n',
        }
        result, evidence = capture_case(case, changes, "Sample retained.")
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        packet, _ = blind_packet(case.rubric, [evidence])
        self.assertIn(".sample.csv", str(packet))

    def test_prototype_records_observed_commands_without_inferring_execution(
        self,
    ) -> None:
        case = self.case("prototype-returns-to-planning")
        output = "prototypes/export_csv_probe.result.json"
        notes = "docs/prototypes/export-csv.md"
        changes = {
            output: '{"preserved": true, "rows": 3}\n',
            notes: "Three names survived the CSV round trip.\n",
            DESIGN: case.files[DESIGN] + "\nCSV round-trip probe passed.\n",
        }
        reply = "Names survived; whether to include headings remains open."
        observations = (
            (),
            (
                CommandResult(
                    "python3 prototypes/export_csv_probe.py",
                    0,
                    "All three names survived CSV writing and reading unchanged.",
                ),
            ),
            (
                CommandResult(
                    "rg 'python3 prototypes/export_csv_probe.py'",
                    0,
                    "Run python3 prototypes/export_csv_probe.py.",
                ),
            ),
            (
                CommandResult(
                    "python3 prototypes/export_csv_probe.py",
                    1,
                    "AssertionError: CSV round trip failed",
                ),
            ),
        )
        for observed in observations:
            with self.subTest(observed=observed):
                result, evidence = capture_case(
                    case, changes, reply, command_results=observed
                )
                self.assertEqual(result.status, "inconclusive")
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(evidence.frames[-1].files[output], changes[output])
                self.assertIsNone(result.assessment)
                self.assertEqual(
                    evidence.frames[-1].commands,
                    [
                        {
                            "command": c.command,
                            "exit_code": c.exit_code,
                            "output": c.output,
                        }
                        for c in observed
                    ],
                )
        missing_output = {p: text for p, text in changes.items() if p != output}
        result, _ = capture_case(case, missing_output, reply)
        self.assertEqual(result.status, "inconclusive")
        for updates, progress in (
            ({**changes, "src/export.py": "def export_rows(items): pass\n"}, None),
            (changes, ("planning", None)),
        ):
            result, _ = capture_case(case, updates, reply, progress=progress)
            self.assertEqual(result.mechanical_status, "fail")

    def test_related_question_records_are_available_without_semantic_regexes(
        self,
    ) -> None:
        case = self.case("related-feature-questions")
        changes = {
            DESIGN: case.files[DESIGN]
            + "\nOpen: zero quantities and alphabetical order.\n",
            MAP: case.files[MAP] + "\nZero quantities and ordering are unresolved.\n",
        }
        reply = (
            "Empty inventory, existing files, zero quantities, "
            "and ordering remain open."
        )
        self.assert_unassessed(case, changes, reply)
        for updates in (
            {},
            {**changes, ".work/export/decisions/02-zero-quantity.md": "New ticket.\n"},
            {
                **changes,
                DESIGN: changes[DESIGN] + "\nSort alphabetically is accepted.\n",
            },
        ):
            with self.subTest(updates=updates):
                self.assert_unassessed(case, updates, reply)
        result, _ = capture_case(
            case, {**changes, "src/export.py": "def export_rows(items): pass\n"}, reply
        )
        self.assertEqual(result.mechanical_status, "fail")

    def test_partial_completion_claims_remain_unjudged_but_source_stays_protected(
        self,
    ) -> None:
        case = self.case("partial-completion")
        for answer in (
            "Search is done. Export remains unimplemented.",
            "Yes, search and export are complete.",
            "Search is done.",
        ):
            with self.subTest(answer=answer):
                evidence = self.assert_unassessed(case, {}, answer)
                self.assertEqual(evidence.frames[-1].reply, answer)
                self.assertIn(
                    "export",
                    evidence.frames[-1].files[".work/inventory/status.md"].lower(),
                )
        for changes, progress in (
            ({}, ("complete", None)),
            ({"src/export.py": "def export_rows(items): pass\n"}, None),
        ):
            result, _ = capture_case(
                case, changes, "Export remains.", progress=progress
            )
            self.assertEqual(result.mechanical_status, "fail")


if __name__ == "__main__":
    unittest.main()
