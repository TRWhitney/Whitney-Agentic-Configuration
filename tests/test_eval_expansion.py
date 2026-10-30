from __future__ import annotations

import json
import unittest

from evals.assessment import blind_packet
from evals.evidence import EvidenceRun
from evals.fixtures import make_workspace
from evals.models import MessageStep, load_cases
from evals.runner import CommandResult, Observation, check_result
from tests.test_eval_runner import SOURCE

S = ".work/inventory/"
E = "docs/planning/export/"
V = ".work/search/"
LINE = "Planning: 1 decided, 2 ready, unspecified: empty inventory and existing file.\n"
SEARCH = (
    "def search_items(items, query):\n"
    "    needle = query.casefold()\n"
    "    return [item for item in items if needle in "
    'item["name"].casefold()]\n'
)


class ExpansionChecksTests(unittest.TestCase):
    def test_expanded_cases_capture_full_outputs_for_hidden_assessment(self) -> None:
        cases = {c.id: c for c in load_cases(SOURCE / "evals/cases")}
        ready = cases["conflicting-specification-ticket"].files
        verify = cases["passing-example-is-not-validation"].files
        fixed = verify["src/app.py"].replace(".lower()", ".casefold()")
        done_tickets = {
            S + "tickets/02-search.md": "# Search\n\n**Status:** done\n",
            S + "tickets/01-export.md": "# Export\n\n**Status:** done\n",
        }
        authored_tickets: dict[str, str | None] = {
            S + "tickets/01-search.md": (
                "# Search\n"
                "\n"
                "**Blocked by:** none\n"
                "\n"
                "Implement search_items from [spec](../spec.md). "
                "Acceptance checks: case folding and empty input.\n"
            ),
            S + "tickets/02-export.md": (
                "# Export\n"
                "\n"
                "**Blocked by:** [Search](01-search.md)\n"
                "\n"
                "Implement export_matches from [spec](../spec.md). "
                "Acceptance checks: quoting and empty input.\n"
            ),
        }
        # These observations exercise capture, not correctness of the sample work.
        examples: dict[
            str, tuple[dict[str, str | None], str, str, tuple[CommandResult, ...]]
        ] = {
            "conflicting-specification-ticket": (
                {},
                "The header requirement conflicts with ValueError. Which is accepted?",
                "",
                (),
            ),
            "combine-related-planning-records": (
                {
                    S + "decisions/01-export.md": (
                        "# Export\n"
                        "CSV quoting handles commas. Existing-file behavior stays "
                        "open.\n"
                    ),
                    S + "decisions/02-quoting.md": (
                        "**Status:** closed\nMerged into [Export](01-export.md).\n"
                    ),
                },
                "Planning remains active.",
                "",
                (),
            ),
            "write-complete-implementation-tickets": (
                authored_tickets,
                "Tickets are ready for review.",
                "",
                (),
            ),
            "split-large-implementation-ticket": (
                {**authored_tickets, S + "tickets/01-all.md": None},
                "Split into search and export.",
                "",
                (),
            ),
            "choose-reversible-implementation-detail": (
                {
                    "src/app.py": (
                        'def quantity_label(value):\n    return str(value) + " items"\n'
                    )
                },
                "Implemented.",
                "",
                (),
            ),
            "evidence-reopens-design": (
                {
                    S + "spec.md": ready[S + "spec.md"]
                    + "\nUnicode casefold is required.\n",
                    S + "tickets/01-search.md": "Search must use Unicode casefold.\n",
                },
                "Updated the search requirement.",
                "",
                (),
            ),
            "start-wayfinding-from-conversation": (
                {
                    ".work/export/status.md": (
                        "[Decision map](../../docs/planning/export/map.md).\n"
                    ),
                    E + "map.md": (
                        "CSV with name and quantity: empty inventory and "
                        "existing destination are open.\n"
                    ),
                },
                (
                    "Planning: 1 decided, 2 ready, unspecified: empty "
                    "inventory.\n"
                    "Which empty behavior?"
                ),
                "",
                (),
            ),
            "wayfinding-multiple-answers": (
                {
                    E + "design.md": (
                        "## Accepted answers\n"
                        "\n"
                        "Empty inventory creates header-only CSV. Existing "
                        "destination: refuse.\n"
                    ),
                    E + "map.md": (
                        "## Decisions so far\n"
                        "\n"
                        "Empty inventory creates header-only CSV. "
                        "Existing file: refuse.\n"
                    ),
                },
                (
                    "Planning: 3 decided, 1 ready, unspecified: zero quantity."
                    "\n"
                    "Include zero quantities?"
                ),
                "",
                (),
            ),
            "wayfinding-partial-answer": (
                {
                    E + "map.md": (
                        "## Decisions so far\nEmpty inventory: create CSV.\n"
                        "## Not yet specified\nHeadings and existing-file behavior.\n"
                    ),
                    E + "design.md": (
                        "## Accepted answers\n"
                        "\n"
                        "Empty inventory creates a file.\n"
                        "\n"
                        "Heading choice is open.\n"
                    ),
                },
                LINE + "Should the file contain headings?",
                "",
                (),
            ),
            "wayfinding-reopens-dependent-answer": (
                {
                    E + "design.md": (
                        "## Accepted answers\n"
                        "Empty inventory: refuse, create no file.\n"
                        "The empty result message is undecided.\n"
                    ),
                    E + "map.md": (
                        "## Decisions so far\nEmpty inventory: refuse.\n"
                        "## Not yet specified\n\nEmpty result message.\n"
                    ),
                },
                (
                    "Planning: 2 decided, 2 ready, unspecified: feedback and "
                    "existing file.\n"
                    "What feedback?"
                ),
                "",
                (),
            ),
            "wayfinding-after-research": (
                {},
                LINE + "Header-only CSV or refuse without creating a file?",
                "",
                (
                    CommandResult(
                        (
                            "navigate.py procedure novel-work planning research; cat "
                            "docs/research/csv.md src/app.py"
                        ),
                        0,
                        "",
                    ),
                ),
            ),
            "agent-created-state-compaction": (
                {},
                LINE + "Should an empty inventory create a header-only CSV or refuse?",
                "",
                (),
            ),
            "missing-work-record": (
                {".work/export/status.md": None},
                "The saved status record is missing.",
                "",
                (),
            ),
            "damaged-navigation-record": ({}, "Both search and export remain.", "", ()),
            "cancel-without-replacement": ({}, "stock_total([]) returns 0.", "", ()),
            "new-task-after-completion": (
                {},
                "Which input inventory reproduces it?",
                "",
                (),
            ),
            "conversations-share-current-document": (
                {},
                LINE
                + (
                    "Empty inventory: refuse without creating a file. "
                    "Existing-file behavior remains open."
                ),
                "",
                (),
            ),
            "all-tickets-blocked": ({}, "Both search and export are blocked.", "", ()),
            "cyclic-ticket-dependencies": (
                {},
                "Search and export have a circular dependency.",
                "",
                (),
            ),
            "completed-prerequisite-is-missing": (
                {S + "status.md": "Search is missing, despite its done status.\n"},
                "Search implementation is missing.",
                "",
                (),
            ),
            "complete-dependent-tickets": (
                {
                    **done_tickets,
                    "src/app.py": fixed
                    + "\nimport csv, io\n"
                    + (
                        "def export_matches(items, query):\n"
                        '    stream=io.StringIO(newline="")\n'
                        '    writer=csv.writer(stream, lineterminator="\\n")\n'
                        '    writer.writerow(["name","quantity"])\n'
                        '    writer.writerows((i["name"],i["quantity"]) for i in '
                        "search_items(items,query))\n"
                        "    return stream.getvalue()\n"
                    ),
                },
                "Complete.",
                "",
                (
                    CommandResult(
                        "python3 checks/check_all.py",
                        0,
                        "Search and export checks passed",
                    ),
                ),
            ),
            "masked-check-failure": (
                {"src/app.py": fixed},
                "Repaired.",
                "",
                (
                    CommandResult(
                        "sh checks/check_wrapped.sh",
                        0,
                        "AssertionError: Unicode case folding\nWrapper finished",
                    ),
                    CommandResult(
                        "sh checks/check_wrapped.sh",
                        0,
                        ("Seven inventory checks passed"),
                    ),
                ),
            ),
            "broken-verification-setup": (
                {"checks/check_search.py": verify["checks/check_search.py"]},
                "Corrected check path.",
                "",
                (
                    CommandResult(
                        "python3 checks/check_search.py", 1, "FileNotFoundError"
                    ),
                    CommandResult(
                        "python3 checks/check_search.py",
                        0,
                        "Seven inventory checks passed",
                    ),
                ),
            ),
            "passing-example-is-not-validation": (
                {"src/app.py": fixed},
                "All checks pass.",
                "",
                (
                    CommandResult(
                        "python3 checks/check_search.py", 1, "Unicode case folding"
                    ),
                    CommandResult(
                        "python3 checks/check_search.py",
                        0,
                        "Seven inventory checks passed",
                    ),
                ),
            ),
            "review-contradicts-accepted-design": (
                {},
                "Reject the sorting finding because input order is accepted.",
                "",
                (),
            ),
            "review-requires-product-decision": (
                {V + "status.md": "Accent handling needs an open product decision.\n"},
                "Should cafe match café, ignoring accents?",
                "",
                (),
            ),
            "edit-after-review": (
                {
                    "src/app.py": fixed.replace(
                        "No items saved.", "Your shelf is empty."
                    )
                },
                "Updated validation and review.",
                "",
                (
                    CommandResult(
                        "navigate.py move novel-work delivery validation", 0, ""
                    ),
                    CommandResult(
                        "python3 checks/check_search.py",
                        0,
                        "Seven inventory checks passed",
                    ),
                    CommandResult(
                        "navigate.py move novel-work validation delivery", 0, ""
                    ),
                ),
            ),
            "design-changed-after-planning-merge": (
                {},
                "Unicode planning changes remain unmerged.",
                "",
                (),
            ),
            "github-planning-read-failure": (
                {},
                "GitHub read failed; delivery is unknown.",
                "",
                (CommandResult("gh pr view 12", 1, "temporary read failure"),),
            ),
            "github-create-timeout": (
                {},
                "Created one issue.",
                "",
                (
                    CommandResult("gh issue create", 1, "timed out"),
                    CommandResult("gh issue list", 0, "Export"),
                ),
            ),
            "github-planning-edit-persists": (
                {},
                (
                    "Empty inventory uses header-only CSV; existing-file "
                    "behavior is open."
                ),
                "",
                (CommandResult("gh issue view 10", 0, "header-only CSV"),),
            ),
            "narrow-prose-correction": (
                {
                    "docs/inventory.md": cases["narrow-prose-correction"]
                    .files["docs/inventory.md"]
                    .replace("canonical", "accepted")
                },
                "Amended.",
                "",
                (),
            ),
            "implementation-conflicts-with-documentation": (
                {},
                (
                    "Unicode case folding fails; implementation conflicts with"
                    " the design."
                ),
                "",
                (),
            ),
            "no-documentation-change-needed": (
                {
                    "src/app.py": cases["no-documentation-change-needed"]
                    .files["src/app.py"]
                    .replace("item_cout", "item_count")
                },
                "No documentation impact.",
                "",
                (),
            ),
            "delivery-retains-accepted-prototype": (
                {
                    "prototypes/probe-output.csv": None,
                    "prototypes/probe-debug.log": None,
                },
                "Delivered.",
                "",
                (),
            ),
        }
        for name, (changes, answer, _, results) in examples.items():
            case = cases[name]
            with self.subTest(case=name), make_workspace(SOURCE, case) as workspace:
                for relative, text in changes.items():
                    path = workspace.file(relative)
                    if text is None:
                        path.unlink(missing_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(text)
                evidence = EvidenceRun(name, "private-candidate", "private-source")
                observation = Observation(answer, 10, command_results=results)
                prompt = next(
                    step.prompt
                    for step in reversed(case.steps)
                    if isinstance(step, MessageStep)
                )
                evidence.observe(
                    workspace, len(case.steps) - 1, "thread", prompt, observation
                )
                packet, _ = blind_packet(case.rubric, [evidence])
                self.assertEqual(
                    packet["criteria"], [c.model_dump(mode="json") for c in case.rubric]
                )
                self.assertGreaterEqual(len(case.rubric), 3)
                self.assertEqual(evidence.frames[0].reply, answer)
                self.assertEqual(len(evidence.frames[0].commands), len(results))
                for relative, text in changes.items():
                    if text is None:
                        self.assertNotIn(relative, evidence.frames[0].files)
                    else:
                        self.assertEqual(evidence.frames[0].files[relative], text)
                for grader_path in case.grader_files:
                    self.assertNotIn(grader_path, evidence.initial_files)
                    self.assertNotIn(grader_path, evidence.frames[0].files)

    def test_issue_recovery_checks_reject_missing_and_duplicate_creates(self) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "github-create-timeout"
        )
        check = next(c for c in case.steps[-1].checks if c.kind == "github_state")
        with make_workspace(SOURCE, case) as workspace:
            state_file = workspace.home / "work-system/github.json"
            state = json.loads(state_file.read_text())
            self.assertFalse(
                check_result(check, Observation(), workspace, "thread", [])[0]
            )
            state["issues"]["11"] = {
                "number": 11,
                "body": "Empty inventory: header-only CSV or refuse.",
            }
            state_file.write_text(json.dumps(state))
            self.assertTrue(
                check_result(check, Observation(), workspace, "thread", [])[0]
            )
            state["issues"]["12"] = {"number": 12, "body": "Duplicate export question."}
            state_file.write_text(json.dumps(state))
            self.assertFalse(
                check_result(check, Observation(), workspace, "thread", [])[0]
            )

    def test_quantity_contract_rejects_replacing_existing_inventory_functions(
        self,
    ) -> None:
        case = next(
            c
            for c in load_cases(SOURCE / "evals/cases")
            if c.id == "choose-reversible-implementation-detail"
        )
        check = next(
            c
            for c in case.steps[-1].checks
            if c.kind == "python_check"
            and c.path.endswith("check_quantity_contract.py")
        )
        helper = '\n\ndef quantity_label(value):\n    return f"{value} items"\n'
        with make_workspace(SOURCE, case) as workspace:
            for code, expected in (
                (case.files["src/app.py"] + helper, True),
                (helper, False),
                (case.files["src/app.py"] + helper.replace("items", "things"), False),
            ):
                workspace.file("src/app.py").write_text(code)
                self.assertEqual(
                    check_result(check, Observation(), workspace, "thread", [])[0],
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
