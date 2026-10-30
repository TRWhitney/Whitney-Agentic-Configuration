# Further workflow evaluations

## Question

Does the workflow hold when planning records conflict, dependencies block every ticket,
conversation state is missing or damaged, review changes the next action, or a service fails?

## Method

Use gpt-6.1-sol and Codex SDK/runtime 0.163.0 with unchanged workflow instructions. Each attempt
allows 600,000 reported tokens and 360 seconds. Reported usage includes repeated input across
calls. Cases use disposable projects with Apps and tool network access disabled. One integration
case explicitly compacts a short conversation; routine cases do not request compaction.

Shared edit steps change files or navigation data between turns. The GitHub stand-in saves issue
edits and comments, can reject reads, and can save an issue while returning a creation timeout.
Independent checks inspect source behavior, saved records, service state, and command results.
Review cases supply findings as task input; they do not test reviewer quality.

## Results

The 70 valid attempts produced 63 passes, 6 failures, and 1 allowance limit. There were no
runtime errors or external-service calls. Both integration attempts confirmed one compaction;
no routine attempt compacted. Reported usage ranged from 84,602 to 615,301 tokens.

| # | Case | First attempt | Repeat |
| --- | --- | --- | --- |
| 1 | [Conflicting specification and ticket](../../evals/cases/conflicting-specification-ticket.json) | Pass | Pass |
| 2 | [Combine related planning records](../../evals/cases/combine-related-planning-records.json) | Pass | Pass |
| 3 | [Write complete implementation tickets](../../evals/cases/write-complete-implementation-tickets.json) | Pass | Pass |
| 4 | [Split a large ticket](../../evals/cases/split-large-implementation-ticket.json) | Pass | Pass |
| 5 | [Choose a reversible implementation detail](../../evals/cases/choose-reversible-implementation-detail.json) | Pass | Pass |
| 6 | [Evidence reopens design](../../evals/cases/evidence-reopens-design.json) | Pass | Pass |
| 7 | [Start wayfinding through conversation](../../evals/cases/start-wayfinding-from-conversation.json) | Pass | Pass |
| 8 | [Several answers in one reply](../../evals/cases/wayfinding-multiple-answers.json) | Fail | Fail |
| 9 | [Partly answered question](../../evals/cases/wayfinding-partial-answer.json) | Fail | Fail |
| 10 | [Reopen a dependent answer](../../evals/cases/wayfinding-reopens-dependent-answer.json) | Pass | Fail |
| 11 | [Return from research](../../evals/cases/wayfinding-after-research.json) | Pass | Pass |
| 12 | [Compact agent-created state](../../evals/cases/agent-created-state-compaction.json) | Pass | Pass |
| 13 | [Missing unrecoverable work record](../../evals/cases/missing-work-record.json) | Pass | Pass |
| 14 | [Damaged navigation record](../../evals/cases/damaged-navigation-record.json) | Pass | Limit; violations observed |
| 15 | [Cancel without replacement](../../evals/cases/cancel-without-replacement.json) | Pass | Pass |
| 16 | [New task after completion](../../evals/cases/new-task-after-completion.json) | Pass | Pass |
| 17 | [Shared document across conversations](../../evals/cases/conversations-share-current-document.json) | Pass | Pass |
| 18 | [Every ticket blocked](../../evals/cases/all-tickets-blocked.json) | Pass | Pass |
| 19 | [Circular ticket dependencies](../../evals/cases/cyclic-ticket-dependencies.json) | Pass | Pass |
| 20 | [Missing prerequisite marked done](../../evals/cases/completed-prerequisite-is-missing.json) | Pass | Pass |
| 21 | [Complete dependent tickets](../../evals/cases/complete-dependent-tickets.json) | Pass | Pass |
| 22 | [Shell success hides a failed check](../../evals/cases/masked-check-failure.json) | Pass | Pass |
| 23 | [Broken verification setup](../../evals/cases/broken-verification-setup.json) | Pass | Pass |
| 24 | [Passing example is incomplete evidence](../../evals/cases/passing-example-is-not-validation.json) | Pass | Pass |
| 25 | [Review contradicts accepted design](../../evals/cases/review-contradicts-accepted-design.json) | Pass | Pass |
| 26 | [Review needs a product decision](../../evals/cases/review-requires-product-decision.json) | Pass | Pass |
| 27 | [Edit after review](../../evals/cases/edit-after-review.json) | Pass | Pass |
| 28 | [Design changes after planning merge](../../evals/cases/design-changed-after-planning-merge.json) | Pass | Pass |
| 29 | [Unavailable planning reads](../../evals/cases/github-planning-read-failure.json) | Pass | Pass |
| 30 | [Issue creation returns an uncertain result](../../evals/cases/github-create-timeout.json) | Pass | Pass |
| 31 | [Issue edits persist](../../evals/cases/github-planning-edit-persists.json) | Pass | Pass |
| 32 | [One-word prose correction](../../evals/cases/narrow-prose-correction.json) | Pass | Pass |
| 33 | [Implementation conflicts with documentation](../../evals/cases/implementation-conflicts-with-documentation.json) | Pass | Fail |
| 34 | [No documentation impact](../../evals/cases/no-documentation-change-needed.json) | Pass | Pass |
| 35 | [Retain an accepted prototype](../../evals/cases/delivery-retains-accepted-prototype.json) | Pass | Pass |

Both multiple-answer and partial-answer attempts saved answers but stopped without asking the
next question. Review added continuation checks and corrected those four false passes.

The revised-answer repeat omitted the progress line and accepted new refusal feedback without
asking, leaving that dependent decision out of the open questions. The documentation-conflict
repeat correctly reported the mismatch and preserved code and documentation, but stayed in
delivery instead of returning to implementation.

The damaged-navigation repeat moved the damaged file aside, implemented both features, and
deleted its backup. These violations were observed before the other conversation exhausted
the token allowance; the overall attempt remains a limit, not a completed behavioral verdict.

## Grading corrections

Map checks follow the work record's link instead of requiring an unrequested directory name.
Conversation checks allow optional wayfinding where its presence does not affect the required
state. Planning permits issue updates; service checks account for earlier allowed writes.
Retention checks allow useful documentation updates. Verification permits repairing the shell
wrapper and accepts a request for missing information without requiring a question mark.
A service error can be observed inside a shell call whose final command succeeds.
The fixture rejects wrong-repository reads and writes through both CLI and REST.

Two initial setups did not exercise their intended problem. The supposed dependency cycle had
an accepted specification giving a valid order. The missing work record remained recoverable
from Git with complete accepted design and tickets. These attempts are excluded. Corrected
setups supply an unresolved cycle and an uncommitted, unrecoverable work record.

## Limits

Short conversations and two attempts per case do not establish a failure rate. Explicit
compaction does not test which information would survive an automatically triggered compaction.
Service responses are simulated. Reply patterns remain mechanical checks; final-code and
saved-record checks establish only the behavior they explicitly cover. Earlier recorded workflow
failures remain open.
