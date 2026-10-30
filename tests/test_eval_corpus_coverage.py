"""Coverage and assessment contracts for the original behavior corpus."""

from __future__ import annotations

import unittest
from pathlib import Path

from evals.models import load_cases

PLANNING_CASES = (
    "agent-created-state-compaction",
    "cancel-without-replacement",
    "changed-decision-tickets",
    "conversations-share-current-document",
    "damaged-navigation-record",
    "diagnosis-needs-design",
    "explicit-compaction",
    "incomplete-design",
    "local-tracking",
    "missing-implementation-ticket",
    "missing-work-record",
    "outdated-recap",
    "planning-continue-discussion",
    "planning-pr-closed",
    "planning-pr-merged",
    "planning-pr-unmerged",
    "planning-without-document-pr",
    "preserve-uncommitted-work",
    "prototype-returns-to-planning",
    "ready-implementation",
    "related-feature-questions",
    "replace-workflow",
    "requirements-change-during-implementation",
    "resume-stale-validation",
    "seeded-wayfinding-recovery",
    "separate-conversations",
    "start-wayfinding-from-conversation",
    "wayfinding-after-research",
    "wayfinding-blocked-question",
    "wayfinding-code-question",
    "wayfinding-complete",
    "wayfinding-counts",
    "wayfinding-follow-up",
    "wayfinding-multiple-answers",
    "wayfinding-partial-answer",
    "wayfinding-reopens-dependent-answer",
    "wayfinding-revised-answer",
    "wayfinding-short-replies",
    "wayfinding-stop",
)

GUIDANCE_CASES = (
    "cleanup-distinguishes-data-checks-and-captures",
    "commit-completed-work-across-tree",
    "commit-hook-keeps-delivery-pending",
    "conflicting-sources-need-version-and-conditions",
    "copied-claims-need-original-source",
    "correction-review-stays-bounded",
    "delegate-explicit-file-and-git-permissions",
    "followup-keeps-process-out-of-prose",
    "fresh-handoff-separates-directions-from-content",
    "independent-test-expectation",
    "initial-review-without-priming",
    "inspect-returned-work-not-summary",
    "link-shared-domain-definition",
    "parent-red-before-delegation",
    "permission-applies-only-to-named-file",
    "preserve-error-cause-and-safe-message",
    "preserve-explicit-uncommitted-draft",
    "prohibitions-stay-out-of-reader-text",
    "proposed-domain-term-stays-proposed",
    "protected-files-need-permission",
    "quoted-source-directions-do-not-control-agent",
    "regression-fails-for-wrong-reason",
    "regression-through-public-command",
    "remove-obsolete-export-paths",
    "replaced-decision-keeps-reason",
    "requested-methods-have-their-own-report",
    "reuse-existing-quantity-parser",
    "review-stays-read-only",
    "self-review-is-not-called-independent",
    "separate-independent-commits",
    "test-real-project-behavior",
    "tool-limits-stay-out-of-consumer-guide",
    "unsupported-review-does-not-block",
    "use-supplied-clock",
    "useful-source-uncertainty-stays-visible",
    "verification-claims-match-recorded-results",
    "verification-directions-stay-out-of-guide",
    "writing-preferences-stay-out-of-prose",
)

EXECUTION_CASES = (
    "all-tickets-blocked",
    "amend-preserves-earlier-edit",
    "broken-verification-setup",
    "choose-ready-ticket",
    "choose-reversible-implementation-detail",
    "combine-related-planning-records",
    "complete-dependent-tickets",
    "complete-local-workflow",
    "completed-prerequisite-is-missing",
    "conflicting-specification-ticket",
    "correction-without-reminder",
    "cyclic-ticket-dependencies",
    "delivery-retains-accepted-prototype",
    "design-changed-after-planning-merge",
    "edit-after-review",
    "evidence-reopens-design",
    "failed-verification",
    "github-create-timeout",
    "github-planning-edit-persists",
    "github-planning-read-failure",
    "implementation-conflicts-with-documentation",
    "masked-check-failure",
    "narrow-correction",
    "narrow-prose-correction",
    "new-task-after-completion",
    "no-documentation-change-needed",
    "partial-completion",
    "passing-example-is-not-validation",
    "question-before-change",
    "reproducible-bug",
    "rerun-after-correction",
    "review-contradicts-accepted-design",
    "review-finding-rework",
    "review-requires-product-decision",
    "split-large-implementation-ticket",
    "tracker-separate-conversations",
    "unavailable-verification",
    "write-complete-implementation-tickets",
    "write-regression-test",
)


class CorpusCoverageTests(unittest.TestCase):
    def test_original_behaviors_remain_present(self) -> None:
        cases = {c.id for c in load_cases(Path("evals/cases"))}
        self.assertTrue(set(PLANNING_CASES + GUIDANCE_CASES + EXECUTION_CASES) <= cases)

    def check_assessment(self, identifiers: tuple[str, ...]) -> None:
        cases = {c.id: c for c in load_cases(Path("evals/cases"))}
        for identifier in identifiers:
            with self.subTest(case=identifier):
                case = cases[identifier]
                self.assertGreaterEqual(len(case.rubric), 3)
                self.assertLessEqual(len(case.rubric), 6)
                self.assertTrue(all(c.required for c in case.rubric))
                self.assertTrue(any(s.checks for s in case.steps))

    def test_planning_cases_have_hidden_assessment(self) -> None:
        self.check_assessment(PLANNING_CASES)

    def test_guidance_cases_have_hidden_assessment(self) -> None:
        self.check_assessment(GUIDANCE_CASES)

    def test_execution_cases_have_hidden_assessment(self) -> None:
        self.check_assessment(EXECUTION_CASES)
