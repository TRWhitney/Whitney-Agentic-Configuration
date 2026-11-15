# Project operating documentation trials

## Scope and method

Check ordinary operating-document creation, fresh-conversation use, maintenance, adequate existing
docs, unavailable prerequisites, and upkeep during a CLI feature change. Creation explicitly asks
for a guide and its consumer is directed to it; the adequate-doc case tests ordinary discovery.
Supplied states test continuation. No comparison with earlier instruction versions is claimed.

Candidates and separate blinded judges use `gpt-6.1-sol`, SDK/runtime `0.163.0`, 1,800 seconds per
candidate turn, 1,200 seconds per assessment, and no token cutoff. Same-family judging and small
CLI projects limit conclusions. Design inputs were pstack's [creator](https://github.com/backnotprop/pstack/blob/main/skills/create-verification-skill/SKILL.md)
and [maintainer](https://github.com/backnotprop/pstack/blob/main/skills/maintain-verification-skill/SKILL.md), adapted to existing documentation and validation.

## Results

| Case | Valid attempts 1 / 2 / 3 | Observed outcome |
| --- | --- | --- |
| Author and reuse | Correct / correct / correct | Usable linked guides; separate native conversations import/list through the real CLI. |
| Maintain and diagnose | Correct / correct / correct | Separate stale commands from data loss; repair both and exercise corrected behavior. |
| Adequate docs | Correct / correct / correct | Existing guide unchanged; requested rehearsal created; working inventory preserved. |
| Unavailable prerequisite | Correct / correct / correct | Real missing-client failure observed; useful local guidance and live-operation limits retained. |
| Feature upkeep, fresh after correction | Correct / correct / correct | Accepted filter, useful guide maintenance, observed CLI red/green and regression checks. |

All fifteen valid outputs were inspected. Initial independent investigation covered twelve valid
outputs and the three superseded feature outputs. Fresh feature outputs were directly inspected.
Independent intent and engineering delivery reviews passed with no findings. Isolation, completed recording, source instructions,
case definitions, and independent native consumer threads were verified.

## Evaluation corrections

Initial grading rejected three feature attempts for legitimate test/contract updates, missing
literal examples, and no extra rehearsal beyond acceptance scripts. A separate source-based audit
confirmed those requirements exceeded the task. Actual tests invoked the public CLI, inspected
JSON and nonmutation, and cleaned temporary data. Concise parameterized references were usable.

Regressions reproduced unjustified byte-preservation checks before repair. Audited all corpus
cases protecting test paths; the maintenance case had the same restriction. Its task and semantic
criteria stayed fixed, so all three saved outputs were rechecked against the corrected protection
scope. Other matching cases were documentation-only, cleanup, validation, or explicit worker-scope
controls. Changed feature criteria required three fresh attempts; the original three are
superseded. Approved subject instructions stayed unchanged.

Calibration initially matched 8/8 examples, then 10/10 after independent option-reference
controls were added, including an uncertain incomplete-recording example. Offline checks cover
valid alternatives and plausible violations.

## Limits and repository checks

Some executions used Python 3.10 despite documented 3.11+, with that difference disclosed;
blanket unavailability claims were insufficiently established. These trials do not certify
supported Python versions. Service lifecycle appears only in authored calibration controls.

Navigator loading, structural validation, all 115 selected repository tests, 179 definitions,
lint, formatting and strict typing pass. Validation's state text
and reference access remain unchanged.

[Authoring standards](../eval-authoring.md). [Commands](../agent-evaluations.md#project-operating-documentation).
