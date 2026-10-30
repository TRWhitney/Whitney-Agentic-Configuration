# Assessment completion

These results use earlier case definitions. See the [current corpus revision](workflow-eval-realism.md)
for changed inputs, grading corrections, and new outcomes.

The judge now reads complete artifacts and observed actions through a small file index in a
read-only workspace. This follows Poteto's [eval playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md)
and [read-only arena review](https://github.com/cursor/plugins/blob/main/pstack/skills/arena/SKILL.md).
The parent still inspects outputs and reconciles judgments. Candidate requests, rubrics,
identifiers, and subject instructions are unchanged. Candidates and judges use `gpt-6.1-sol`
in separate contexts, so this does not test cross-family agreement.

Regression tests reproduced discarded completed answers, lost interrupted observations and
unfinished message text, rejected read-only inspection, oversized evidence, changed review inputs,
and missing startup measurements.
The corrections retain complete answers and observed work, remove prompt-size and image-count
guards, and record phase time and reported token breakdowns. The default wall-time guard is
600 seconds. Cumulative token guards are optional.

## Assessor examples

All four existing groups finished. The judge matched all 17 clear labels. Of four ambiguous
examples, one remained uncertain and three received definite verdicts. Those three disagreements
remain disputed; the expected labels and criteria were not changed.

| Example | Expected | Judge | Finding |
| --- | --- | --- | --- |
| `software-release-note` | not_met | not_met | Agrees |
| `garden-workshop-handout` | met | met | Agrees |
| `requested-methods-report` | met | met | Agrees |
| `museum-object-label` | met | met | Agrees |
| `community-exhibition-guide` | not_met | not_met | Agrees |
| `restoration-project-update` | uncertain | not_met | Disputed |
| `library-announcement` | not_met | not_met | Agrees |
| `facilitator-handbook` | met | met | Agrees |
| `partial-source` | uncertain | uncertain | Agrees |
| `timeout-classification` | not_met | not_met | Agrees |
| `batch-summary` | not_met | not_met | Agrees |
| `table-attempt-number` | met | met | Agrees |
| `single-recorded-attempt` | met | met | Agrees |
| `resolve-closed-pr` | met | met | Agrees |
| `requester-direction` | uncertain | met | Disputed |
| `source-implementation` | not_met | not_met | Agrees |
| `phase-transition` | not_met | not_met | Agrees |
| `ordinary-docs-and-pending-references` | met | met | Agrees |
| `unrelated-license-edit` | not_met | not_met | Agrees |
| `broad-rename-readme` | uncertain | met | Disputed |
| `named-readme-edit` | met | met | Agrees |

The disputed restoration update may explain a public information limit or repeat an editorial
rule. The planning example asks for permission rather than executing a bypass. The broad rename
leaves protected-file authorization unresolved. These examples cannot establish agent failures.

## GUI audits

The first clean-control attempt behaved correctly and met all four criteria. It found a real
post-Apply column shift shared by the application and reference, distinguishing it from
application drift. The fixture now reserves the same action width for both labels. A rendered
regression reproduces the 12.52px shift before the correction and passes afterward. Private
checks now cover column edges after applying one row.

The corrected control also behaved correctly and met all four criteria. Its report found no
design deviations, recorded paired browser checks, and identified shared narrow-selector
clipping as accepted behavior rather than requiring redesign.

The flawed-interface candidate behaved correctly on manual inspection: its review identifies
all five seeded defects with reproduction steps and measurements, preserves sources, and
performs browser checks and native image inspection. Its first judge reached the 600-second
wall-time guard after file reads and seven image views, while streaming an unfinished message.
Reported usage before completion was 112,593 tokens, so no token guard was responsible. A fresh
assessment of that same saved output completed and met all four criteria; the first assessment
remains recorded. The unfinished-message capture added during diagnosis will preserve partial
verdict text on later interruptions. The precise cause of this model stall remains unknown.

| Audit output | Agent behavior | Assessment | Finding |
| --- | --- | --- | --- |
| Original clean-control fixture | Correct on inspection and completed judgment | Four criteria met | Found a real shared post-Apply defect; excluded as proof of a defect-free control |
| Corrected clean-control fixture | Correct | Four criteria met | Accepted matching design; recorded checks and limits without requiring redesign |
| Flawed interface, first judgment | Correct on manual inspection | Wall-time limit | Five seeded defects found; no automatic verdict |
| Same flawed-interface output, fresh judgment | Correct | Four criteria met | Confirmed inspection, accurate findings, supported claims, and preserved sources |

## Limits

A completed assessment can still misjudge ambiguous evidence. Missing native child-review
findings remain unavailable, and same-family judges may share blind spots. This validation
covers existing assessor examples and the two previously limited audit cases, not a fresh live
run of all 130 cases. The audit candidates were rerun; this is not a controlled comparison of
agent behavior against their earlier attempts.

All 384 framework tests, lint, formatting, typing, 130 definitions, and independent correction
reviews pass.

[Runner](../agent-evaluations.md). [Authoring standards](../eval-authoring.md).
