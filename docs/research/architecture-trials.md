# Architecture behavior trials

## Scope and method

Three Python tasks test calling examples, interfaces, coordinated updates, and a result type
that loses required information. Two existing cases provide controls. Seeded states test
continuation, not initial workflow selection. Criteria are private.

Each case runs three times with `gpt-6.1-sol` candidates and separate blinded judges,
1,800 seconds per candidate turn, 1,200 seconds per assessment, and no token cutoff.
SDK/runtime: `0.163.0`. Baseline instructions: `90204f5`. Same-family judging and small
projects limit broader conclusions. Definitions, authoring audit, and twenty existing case
tests pass.

## Results

C = correct; I = incorrect. Each cell lists attempts 1 / 2 / 3.

| Case | Corrected baseline | Iteration 1 | Iteration 2 | Iteration 3, inspected | Iteration 4 |
| --- | --- | --- | --- | --- | --- |
| `architecture-export-interface` | C / C / I | C / I / I | I / C / C | I / C / I | C / C / C |
| `architecture-shared-records` | C / C / C, fresh after grading correction | C / C / C | C / C / C | C / C / C | C / C / C |
| `architecture-result-design-conflict` | I / I / C | C / C / I | C / C / C | C / C / C | C / C / C |
| `choose-reversible-implementation-detail` | C / C / C | C / C / C | C / C / C | C / C / C | C / C / C |
| `incomplete-design` | C / C / C | C / C / C | C / C / C | C / C / C | C / C / C |
| Total | 12/15 | 12/15 | 14/15 | 13/15 | 15/15 |

Initial baseline judging reported 11/15. Independent review disputed a shared-record failure
that demanded formal declaration blocks and literal records despite a usable interface and
correct coordination. Clarified criteria accept precise prose and assess coordination separately.
Three fresh shared-record attempts superseded the original three.

Baseline result-redesign failures omitted calling examples. Its export failure requested weaker
partial-file protection without establishing that alternatives could not satisfy the requirement.

Iteration 1 requires calls and declarations before interface agreement, and alternatives before
requesting changed requirements. One redesign skipped architecture; two exports dismissed
staging without checking the partial-destination requirement.

Iteration 2 explicitly loads architecture for redesign and checks alternatives against the
requirement. One export still dismissed staging as unrequested work. Iteration 3 prohibits
rejecting compliant designs solely for providing an additional guarantee. Inputs, grading,
model, and allowances stayed fixed between these instruction iterations.

## Grading defect and final iteration

Iteration 3's automated 15/15 contradicted inspection: two exports allow partial destinations
when deletion fails. Independent review confirmed both failures; the third export stages
complete output before publication. Other cases passed.

A calibration example marked correct had the same deletion assumption. Earlier 10/10 agreement
therefore did not establish sound grading. Corrected that example and its paired interface
negative, added independent valid/invalid cleanup-failure examples, and clarified private export
grading. Corrected calibration: 12/12. Ordinary secondary cleanup failure counts; process
termination and hardware corruption do not. No publication primitive is mandatory. Original
false passes remain distinguished from inspected outcomes.

All completed outputs were inspected; independent review covered all architecture outputs.
Isolation, completion, recording, instruction bytes, and definitions were verified. Iteration 4
adds a check for cleanup failure and the files or records left changed. With corrected grading
and calibration, all 15 attempts passed inspection; independent review agreed on all nine
architecture outputs. All three exports stage complete files before exclusive publication and
distinguish temporary leftovers from partial destinations. Every calibration run matched all
12 examples, including one correctly uncertain judgment. Lint and strict typing pass.

[Authoring standards](../eval-authoring.md). [Runner and command](../agent-evaluations.md#code-architecture).
