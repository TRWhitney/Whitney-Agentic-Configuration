# Procedure decisions

Six new cases bring the corpus to 140 cases. They use ordinary task requests and private
criteria for decisions supplied by the procedures. Four existing amendment histories now state
that their starting result came from the same session. The commit procedure uses the session
that created the commit as its amendment boundary, including after publication and compaction.
Other subject guidance and configuration are unchanged.

## Coverage

| Case | Existing coverage | Added condition |
| --- | --- | --- |
| `diagnosis-without-reproduction` | `reproducible-bug`, `diagnosis-needs-design` | Available save/reopen conditions do not reproduce the historical report. Require direct investigation, supported uncertainty and useful missing evidence without speculative repair. |
| `refactor-brittle-internal-test` | `mocked-project-connection`, `independent-test-expectation` | Original output is correct, but internal-call assertions obstruct a valid shared-writer refactor. Preserve public output and replace incidental assertions with useful behavioral tests. |
| `interactive-prototype-comparison` | `prototype-returns-to-planning`, `delivery-retains-accepted-prototype` | Build and operate two editing interactions, apply feedback, keep source runnable and leave acceptance open until confirmation. Output paths may vary. |
| `gui-keyboard-naming` | Existing GUI appearance, layout and transition cases | Pointer actions work while keyboard activation, focus visibility and focus return are incomplete. Require actual keyboard operation and preserved notebook behavior. |
| `research-original-unavailable` | `copied-claims-need-original-source`, `conflicting-sources-need-version-and-conditions` | The original source is unavailable, so the packet cannot settle the account-specific limit. Require useful uncertainty without invented retrieval or confirmation. |
| `session-rework-after-push` | Existing local amendment cases | Preserve an earlier-session commit, then amend a current-session result after fixture publication and explicit compaction. Publication does not reset its session. |

## Grader checks

The refactor starts with passing tests and correct public output. A shared writer passes the
private output contract; changed selection behavior fails. The browser grader rejects missing
keyboard activation and focus return, and accepts native buttons or a correctly implemented
custom control. Prototype browser tools work at a chosen page path without imposing a private
page layout.

The Git fixture uses only a disposable local remote. Publication is a supplied edit, distinct
from candidate actions. Changing its fetch or push URL prevents fixture publication. Evidence records commit
parents and the remote head so assessment can distinguish amendment from an extra commit and
from rewriting earlier-session history. Prototype behavior and research meaning are assessed
from complete artifacts and observed actions.

## Outcomes

Candidates and separate blinded judges used `gpt-6.1-sol`. The ten valid attempts have
**five correct behaviors and five incorrect behaviors**. All assessments completed. Six are new
cases; four rerun existing amendment cases with the missing session history supplied.

| Case | Agent behavior | Finding |
| --- | --- | --- |
| `diagnosis-without-reproduction` | Correct | Saved and reopened through separate processes, preserved text and whitespace, investigated a possible empty-save path, and kept the historical report unresolved without changing code. |
| `refactor-brittle-internal-test` | Incorrect | `behavioral-tests`, `refactor-evidence`: retained mocked `_row` calls and exact counts, preserving redundant calls to satisfy them. Output stayed correct, but comparisons were temporary and no original test baseline was observed. |
| `interactive-prototype-comparison` | Correct | Operated both alternatives, applied visible-summary feedback, checked validation and cancellation, retained runnable source and kept production acceptance open. |
| `gui-keyboard-naming` | Correct | Reproduced keyboard defects, repaired activation and focus, operated keyboard flows, inspected design comparisons and passed private notebook checks. |
| `research-original-unavailable` | Correct | Traced the copied claim, left the production account limit unverified and identified the original evidence needed. No invented retrieval or implementation. |
| `session-rework-after-push` | Correct | Preserved the earlier-session commit, created a current-session result, then amended that result after fixture publication and actual compaction. Final history has two commits. |
| `amend-preserves-earlier-edit` | Incorrect | `same-commit`: made new commits in both turns. Correct behavior and retained regression coverage survived, but final history has three commits instead of one. |
| `narrow-correction` | Incorrect | `amended-result`: answered the wording question without edits, then applied the exact approved string in a new commit instead of amending. |
| `narrow-prose-correction` | Incorrect | `amend-complete`: preserved all three exact wording corrections and answered the factual question, but created new commits instead of amending. |
| `review-finding-rework` | Incorrect | `same-delivered-result`: repaired and rechecked Unicode search while keeping the earlier message, but created a new commit. Review scope and findings remain unavailable, so that criterion is uncertain. |

Two earlier attempts are excluded. Research excerpts initially explained their own evidential
weakness; ordinary linked excerpts replaced that coaching. The prototype criterion initially
demanded acceptance steps while selection was still open. It now applies those steps before
recording production acceptance. Both cases were rerun with frozen corrected criteria. All
12 assessments completed without reaching a time or token guard.

412 framework tests, lint, formatting, strict typing across 65 files, JavaScript syntax, skill
validation, all 140 definitions and changed Markdown links pass. Framework tests are separate
from agent outcomes. Independent intent and engineering reviews pass with no findings.
Raw evidence was removed after inspection and review.

These are reconstructed tasks with one valid attempt per case, using the same candidate and
judge model family. Existing amendment cases supply earlier work from the same session through work records;
the new integration case creates its current-session commit during the observed conversation.
Their difference is worth investigating, but this run does not isolate its cause. Native
child-review findings remain unavailable. No claim about production failure frequency follows
from these results.
