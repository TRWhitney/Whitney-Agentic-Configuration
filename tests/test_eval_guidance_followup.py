from __future__ import annotations

import unittest

from evals.assessment import blind_packet
from evals.fixtures import Workspace, make_workspace
from evals.models import CaseSpec, MessageStep, SeedStep, load_cases
from evals.runner import Observation, check_result
from tests.evidence_support import evidence_text
from tests.test_eval_prose import record_case
from tests.test_eval_runner import SOURCE


class GuidanceFollowupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}

    def mechanically_passed(
        self, case: CaseSpec, workspace: Workspace, answer: str = ""
    ) -> bool:
        return all(
            check_result(check, Observation(answer), workspace, "thread", [])[0]
            for check in case.steps[-1].checks
        )

    def test_export_contract_rejects_wrong_output_and_exposes_obsolete_code(
        self,
    ) -> None:
        case = self.cases["remove-obsolete-export-paths"]
        with make_workspace(SOURCE, case) as w:
            self.assertFalse(self.mechanically_passed(case, w))
            w.file("src/cli.py").write_text(
                "import argparse,json\n"
                "from export import export_items\n"
                "p=argparse.ArgumentParser()\n"
                'p.add_argument("--format",choices=["json"],default="json")\n'
                "p.parse_args()\n"
                'print(export_items([{"name":"Tea","quantity":2}]))\n'
            )
            w.file("src/export.py").write_text(
                "import json\ndef export_items(items): return json.dumps(items)\n"
            )
            w.file("docs/export.md").write_text("# Export\n\nJSON only.\n")
            self.assertTrue(self.mechanically_passed(case, w))
            w.file("src/legacy.py").write_text(
                'def export_csv(items): return "unused"\n'
            )
            # Unused compatibility code needs assessment beyond runtime contracts.
            self.assertTrue(self.mechanically_passed(case, w))
            from evals.evidence import EvidenceRun

            run = EvidenceRun(case.id, "candidate", "authored-output")
            message = case.steps[-1]
            assert isinstance(message, MessageStep)
            run.observe(w, 1, "thread", message.prompt, Observation("Done.", 10))
            packet, _ = blind_packet(case.rubric, [run])
            self.assertIn(
                w.file("src/legacy.py").read_text(),
                evidence_text(packet),
            )
            w.file("src/legacy.py").unlink()
            w.file("src/export.py").write_text(
                "import json\ndef export_items(items): "
                'return json.dumps([{"name":"Tea","quantity":2}])\n'
            )
            self.assertFalse(self.mechanically_passed(case, w))

    def test_parser_reuse_rejects_equivalent_duplicate_implementation(self) -> None:
        case = self.cases["reuse-existing-quantity-parser"]
        with make_workspace(SOURCE, case) as w:
            prefix = "import csv,io\n"
            body = (
                "def import_items(text):\n"
                '    return [{"name":r["name"],"quantity":parse_quantity('
                'r["quantity"])} for r in csv.DictReader(io.StringIO(text))]\n'
            )
            w.file("src/importer.py").write_text(
                prefix + "from src.quantities import parse_quantity\n" + body
            )
            self.assertTrue(self.mechanically_passed(case, w))
            w.file("src/importer.py").write_text(
                prefix + w.file("src/quantities.py").read_text() + "\n" + body
            )
            self.assertFalse(self.mechanically_passed(case, w))
            w.file("src/importer.py").write_text(
                prefix
                + "from src.quantities import parse_quantity\n"
                + "def import_items(text):\n"
                + "    result=[]\n"
                + "    for r in csv.DictReader(io.StringIO(text)):\n"
                + '        parse_quantity(r["quantity"])\n'
                + '        result.append({"name":r["name"],'
                + '"quantity":int(r["quantity"])})\n'
                + "    return result\n"
            )
            self.assertFalse(self.mechanically_passed(case, w))

    def test_term_acceptance_needs_assessment_but_premature_glossary_edits_fail(
        self,
    ) -> None:
        case = self.cases["proposed-domain-term-stays-proposed"]
        for status, answer in [
            (
                "# Receiving\n\nProposed term: batch.\n",
                "Batch fits a received group. Shall we use it?",
            ),
            ("# Receiving\n\nAccepted term: batch.\n", "Batch is now accepted."),
        ]:
            with self.subTest(status=status):
                result, run = record_case(
                    case, {".work/receiving/status.md": status}, answer
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(status, evidence_text(packet))
                self.assertIn(answer, evidence_text(packet))
        with make_workspace(SOURCE, case) as w:
            seed = case.steps[0]
            assert isinstance(seed, SeedStep)
            w.seed("thread", seed)
            w.file("docs/glossary.md").write_text(
                w.file("docs/glossary.md").read_text()
                + "\n## Batch\n\nItems received together.\n"
            )
            self.assertFalse(self.mechanically_passed(case, w))

    def test_definition_links_and_duplicate_meaning_reach_assessment(self) -> None:
        case = self.cases["link-shared-domain-definition"]
        definition = "A counted item is one individual object held in stock."
        glossary = "# Inventory terms\n\n## Counted item\n\n" + definition + "\n"
        link = "# Stock\n\n[Terms](../../docs/glossary.md#counted-item).\n"
        for status in (link, link + definition, "# Stock\n\nSee the glossary.\n"):
            with self.subTest(status=status):
                result, run = record_case(
                    case,
                    {
                        "docs/glossary.md": glossary,
                        ".work/stock/status.md": status,
                    },
                )
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(glossary, evidence_text(packet))
                self.assertIn(status, evidence_text(packet))
        result, run = record_case(
            case,
            {
                "docs/glossary.md": glossary,
                ".work/stock/status.md": link,
                "docs/copy.md": definition,
            },
        )
        self.assertEqual(result.status, "inconclusive")
        packet, _ = blind_packet(case.rubric, [run])
        self.assertIn("docs/copy.md", run.frames[0].files)
        self.assertIn(definition, evidence_text(packet))

    def test_blocker_reasons_need_assessment_and_implementation_edits_fail(
        self,
    ) -> None:
        case = self.cases["unsupported-review-does-not-block"]
        for answer in (
            "Neither should block review. The loop is stylistic; "
            "string inputs are unsupported.",
            "Both should fail review.",
        ):
            with self.subTest(answer=answer):
                result, run = record_case(case, {}, answer, complete=True)
                self.assertEqual(result.mechanical_status, "pass")
                self.assertEqual(result.status, "inconclusive")
                packet, _ = blind_packet(case.rubric, [run])
                self.assertIn(answer, evidence_text(packet))
                self.assertIn(
                    case.files["docs/review.md"],
                    evidence_text(packet),
                )
        with make_workspace(SOURCE, case) as w:
            w.file("src/app.py").write_text(
                "# Expanded to support speculative input.\n"
            )
            self.assertFalse(self.mechanically_passed(case, w))

    def test_research_conclusions_and_full_source_packet_need_assessment(self) -> None:
        examples = {
            "copied-claims-need-original-source": [
                "Basic accounts get 20 labels; Pro accounts get 50. These reports copy "
                "one manual, sources/manual.md, "
                "rather than independently confirming it.",
                "Basic accounts get 50 labels; Pro accounts get 20. "
                "See sources/manual.md.",
                "Three independent reports confirm 50 labels for Basic accounts.",
                "The Basic limit is 20, but no original source was consulted.",
            ],
            "conflicting-sources-need-version-and-conditions": [
                "Production Basic 2.0 creation allows 20 labels. "
                "Version 1.0 allowed 10; "
                "50 is Pro, 100 is status lookup, "
                "and the sandbox trial differs from production. "
                "See sources/manual-v2.md, sources/manual-v1.md, "
                "sources/status-endpoint.md "
                "and sources/sandbox-trial.md.",
                "The newest newsletter confirms 50 labels for Basic accounts.",
                "The status endpoint allows 100 IDs, "
                "so production can create 100 labels.",
            ],
        }
        for name, answers in examples.items():
            case = self.cases[name]
            for answer in answers:
                with self.subTest(case=name, answer=answer):
                    result, run = record_case(case, {}, answer)
                    self.assertEqual(result.mechanical_status, "pass")
                    self.assertEqual(result.status, "inconclusive")
                    packet, _ = blind_packet(case.rubric, [run])
                    self.assertIn(answer, evidence_text(packet))
                    for path, text in case.files.items():
                        if path.startswith("sources/"):
                            self.assertEqual(run.initial_files[path], text)
                            self.assertIn(text, evidence_text(packet))
            source = (
                "sources/manual.md"
                if name.startswith("copied")
                else "sources/manual-v2.md"
            )
            result, _ = record_case(case, {source: "Changed source.\n"}, answers[0])
            self.assertEqual(result.mechanical_status, "fail")
            self.assertEqual(result.status, "fail")


if __name__ == "__main__":
    unittest.main()
