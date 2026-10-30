from __future__ import annotations

import json
import unittest

from evals.fixtures import Workspace
from evals.models import CaseSpec, load_cases
from evals.runner import Observation, run_case
from tests.eval_support import observe_case
from tests.test_eval_runner import SOURCE, FakeDriver

SEARCH = (
    "def search_items(items, query):\n"
    "    needle = query.casefold()\n"
    '    return [item for item in items if needle in item["name"].casefold()]\n'
)
INLINE_SEARCH = (
    "def search_items(items, query):\n"
    "    return [item for item in items "
    'if query.casefold() in item["name"].casefold()]\n'
)


class ImplementationCaseChecksTests(unittest.TestCase):
    def case(self, name: str) -> CaseSpec:
        return next(c for c in load_cases(SOURCE / "evals/cases") if c.id == name)

    def test_ready_search_checks_behavior_without_forcing_syntax_or_final_stage(
        self,
    ) -> None:
        case = self.case("ready-implementation")
        code = case.files["src/app.py"] + "\n\n" + SEARCH
        inline = case.files["src/app.py"] + "\n\n" + INLINE_SEARCH
        reply = "Search is implemented. CSV export remains pending."
        for changes, state, expected in (
            ({"src/app.py": code}, "implementation", "pass"),
            ({"src/app.py": inline}, "validation", "pass"),
            ({"src/app.py": code}, "delivery", "pass"),
            ({}, "implementation", "fail"),
            (
                {"src/app.py": code.replace(".casefold()", ".lower()")},
                "implementation",
                "fail",
            ),
            (
                {"src/app.py": code + "\ndef export_rows(items): pass\n"},
                "implementation",
                "fail",
            ),
        ):
            with self.subTest(changes=changes, state=state):
                result = observe_case(case, changes, reply, progress=(state, None))
                self.assertEqual(result.mechanical_status, expected)
                self.assertEqual(
                    result.status, "inconclusive" if expected == "pass" else "fail"
                )

    def test_existing_tracked_and_untracked_edits_survive_the_search_change(
        self,
    ) -> None:
        case = self.case("preserve-uncommitted-work")
        code = case.uncommitted_files["src/app.py"] + "\n\n" + SEARCH
        reply = "Search is implemented. CSV export remains pending."
        result = observe_case(case, {"src/app.py": code}, reply)
        self.assertEqual(result.mechanical_status, "pass")
        self.assertEqual(result.status, "inconclusive")
        for changes in (
            {"src/app.py": case.files["src/app.py"] + "\n\n" + SEARCH},
            {"src/app.py": code, ".work/drafts/notes.md": "Replaced draft.\n"},
            {},
        ):
            with self.subTest(changes=changes):
                result = observe_case(case, changes, reply)
                self.assertEqual(result.mechanical_status, "fail")
                self.assertEqual(result.status, "fail")

    def test_replacing_a_workflow_keeps_the_other_conversation_and_replacement(
        self,
    ) -> None:
        case = self.case("replace-workflow")
        for replace, disturb_other, expected in (
            (True, False, "pass"),
            (False, False, "fail"),
            (True, True, "fail"),
        ):
            with self.subTest(replace=replace, disturb_other=disturb_other):

                def factory(
                    workspace: Workspace,
                    model: str,
                    timeout: float,
                    max_tokens: int,
                    *,
                    change: bool = replace,
                    disturb: bool = disturb_other,
                ) -> FakeDriver:
                    class ReplacementDriver(FakeDriver):
                        def message(self, thread: str, prompt: str) -> Observation:
                            if thread == "thread-1":
                                if change:
                                    saved = {
                                        "workflow": "fix",
                                        "state": "discovery",
                                        "record": str(
                                            workspace.file(".work/import/status.md")
                                        ),
                                    }
                                    workspace.progress_path(thread).write_text(
                                        json.dumps(saved)
                                    )
                                if disturb:
                                    workspace.progress_path("thread-2").unlink(
                                        missing_ok=True
                                    )
                                return Observation(
                                    "Please supply the failing CSV and error.", 10
                                )
                            return Observation(
                                "Should totals accept or reject negative quantities?",
                                10,
                            )

                    return ReplacementDriver()

                result = run_case(case, SOURCE, "example-model", driver_factory=factory)
                self.assertEqual(result.mechanical_status, expected)
                self.assertEqual(
                    result.status, "inconclusive" if expected == "pass" else "fail"
                )


if __name__ == "__main__":
    unittest.main()
