# Assessing the existing corpus

These results use earlier case definitions. See the [current corpus revision](workflow-eval-realism.md)
for changed inputs, grading corrections, and new outcomes.

## Method

Poteto's [playbook](https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/eval.md)
uses ordinary tasks, hidden criteria, isolated environments, a blinded judge, and artifact
inspection. The [guide](https://github.com/cursor/plugins/blob/main/pstack/docs/guide/09-make-it-yours.md)
warns against changing a skill around one bad session. These sources describe a method; the
research found no completed first-party public corpus with tasks, outputs, and scores.

All 116 original cases were revised in place, preserving their identifiers and behavior coverage.
Requests give ordinary intent and necessary context. Process coaching was removed from prompts
and supplied records. The cases have 468 hidden criteria. Genuine constraints remain, including
exact edits, a requested self-review, and named-file permission. The separate six-case addition
and prompt-reminder comparison were removed.

Code checks cover functional contracts, observed actions, permissions, navigation, and history.
Private criteria assess meaning and completeness. Unassessed criteria remain inconclusive.
Evidence includes complete artifacts, supplied context changes, starting and changed tracker
records, confirmed compaction, and observed actions. Judge turns supply a response schema;
responses still undergo label and criterion validation.

## Validation

All candidates and judges used `gpt-6.1-sol` in separate contexts. Candidate allowances were
360 seconds and 600,000 reported tokens; judges had 240 seconds and 200,000 tokens. The two
compaction cases requested actual compaction in short conversations. Subject instructions stayed
unchanged. All finished artifacts, replies, and relevant actions were inspected.

| Existing cases | Cases | Pass | Fail | Inconclusive | Limit |
| --- | ---: | ---: | ---: | ---: | ---: |
| Planning and recovery | 39 | 26 | 8 | 0 | 5 |
| Guidance and prose | 38 | 25 | 1 | 8 | 4 |
| Implementation and delivery | 39 | 23 | 2 | 10 | 4 |
| Total | 116 | 74 | 11 | 18 | 13 |

An additional valid ticket-writing attempt passed and was inspected separately. Invalid fixture
attempts were replaced. Corrected graders were reapplied to saved outputs; changed criteria
received fresh blind assessments. Corrections allow stronger tests and related guide updates,
separate supplied edits from agent actions, and remove irrelevant caveats and prescribed reading
or explanation steps. Review also removed a remaining regression reminder and refreshed that case. Malformed
responses and exhausted allowances remain visible.

Nine failures have clear behavioral evidence. Two fail verdicts remain disputed: asking to waive
a closed planning PR's merge requirement, and whether a broad rename grants protected-file
permission. Their recorded fail verdicts remain in the table.

| Confirmed failures | Observed behavior |
| --- | --- |
| `agent-created-state-compaction`, `start-wayfinding-from-conversation` | No linked planning map or feature record created |
| `damaged-navigation-record` | Guessed replacement state and implemented both features |
| `diagnosis-needs-design`, `implementation-conflicts-with-documentation` | Stayed in the wrong workflow state |
| `requirements-change-during-implementation` | Returned to planning but left conflicting specification and ready ticket |
| `wayfinding-revised-answer` | Omitted the first reply's progress line |
| `wayfinding-multiple-answers` | Saved answers but asked no next decision question |
| `tracker-separate-conversations` | Omitted GitHub planning-document delivery from its explanation |

Eighteen cases remain inconclusive, mainly from unavailable review findings. Eleven limits
occurred in assessment; two candidates exhausted their token allowance before a follow-up.
One invalid assessment also remains attached to a case with an independently observed phase
failure. Calibration matched seven clear labels; its ambiguous example remains disputed.
Infrastructure validation passed 340 tests, lint, typing, definition validation, and private-grader
compilation.

## Limits and next work

These short projects and one primary attempt per case do not establish normal-use reliability.
The same-family judge may share candidate blind spots. Calibration covers prose, not every
workflow criterion. The amendment case also exposed missing retained regression coverage that
its frozen criteria did not score. Next, calibrate disputed workflow judgments and improve review
evidence before comparing skill changes.

[Authoring standards](../eval-authoring.md). [Runner](../agent-evaluations.md).
