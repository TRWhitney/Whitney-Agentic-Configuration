# 05 Assess the existing corpus

**What to build:** Apply shared assessment to ordinary repository tasks, including reply-only
questions, without treating unassessed criteria as a pass.

**Blocked by:** none.

**Status:** complete

- [x] Keep isolated blind judging, private grading, calibration, source comparison, audits, and reporting.
- [x] Support criteria for reply-only tasks and preserve code-check outcomes separately.
- [x] Report passing code checks with unassessed required criteria as inconclusive.
- [x] Include confirmed compaction and relevant service-fixture state in blind evidence.
- [x] Use one prompt sequence per case; remove prompt-reminder comparison support.
- [x] Share project-file observation across capture and preservation checks, excluding ordinary generated caches.
- [x] Cover missing evidence, hard failures, source changes, private graders, and existing interfaces with focused tests.

## Accepted sources

[Specification](../spec.md#corpus-assessment).
[Authoring standards](../../../docs/eval-authoring.md).

## Completion evidence

The full infrastructure suite passes 340 tests, lint, and strict typing. All 116 definitions
validate and private graders compile. Focused regressions cover reply-only assessment, cache
handling, file permissions, supplied edits, damaged navigation capture, tracker context, public
check paths, judge response contracts, and retained hard failures. Corpus results are recorded
in the [assessment study](../../../docs/research/evaluation-methods.md#validation).
