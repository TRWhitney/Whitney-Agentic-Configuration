# Interface and prototype trials

Trials investigate [prototype comparison](integration-and-acceptance-evals.md#outcomes) and
[interface design](main-procedure-path-evals.md#outcomes). The
[reviewed diff](interface-prototype-proposal.diff) is applied unchanged.

## Historical outcomes

All 59 candidate assessments and five joint comparisons completed. The last set was 13 correct
and two unknown. These verdicts used the earlier deletion expectation and production ban.
Raw evidence was deleted after review; the revised criteria do not relabel these attempts.

C means correct, F incorrect, U unknown. Entries follow execution order. Plan means
`specific-design-plan`, inspection `rendered-inspection-and-critique`, and operation
`runnable-choice`. Tags identify every failed or uncertain criterion; other criteria are met.

| Instruction condition | interactive-prototype-comparison | new-interface-design | prototype-returns-to-planning | delivery-retains-accepted-prototype | gui-accepted-design |
| --- | --- | --- | --- | --- | --- |
| Baseline | F acceptance: early recording, inline kept | F plan: built first; U inspection: focus/critique | C | C | C |
| First screen | F acceptance: early recording, inline kept, production built | F plan: built first; U inspection: structure/states | Not run | Not run | Not run |
| Plan instruction first | Not run | U inspection: structure/states/focus | Not run | Not run | Not run |
| Extend existing prototype cue | F acceptance: inline kept | Not run | Not run | Not run | Not run |
| Explicit focus inspection | Not run | U inspection: structure/states | Not run | Not run | Not run |
| Cleanup deadline screen | C | Not run | Not run | Not run | Not run |
| Visual inspection beside operation | Not run | U operation: volunteer checkout; U inspection: checkout/states | Not run | Not run | Not run |
| Complete flows in each alternative | Not run | C | Not run | Not run | Not run |
| Visual-inspection repeats | F acceptance: inline kept<br>F acceptance: inline kept; U direct-operation: save/recovery<br>F acceptance: inline kept | U inspection: structure/states<br>U inspection: structure/states<br>U inspection: structure/states | C/C/C | C/C/C | C/C/C |
| Cleanup beside confirmation screen | C | Not run | Not run | Not run | Not run |
| Cleanup beside confirmation repeats | C<br>C<br>F acceptance: unanswered production decisions | U inspection: structure/states<br>C<br>U inspection: structure/states/focus | C/C/C | C/C/C | C/C/C |
| Inspect each state; use keyboard | C/C/C | U inspection: structure/error view<br>U operation: volunteer checkout; U inspection: checkout/structure<br>C | C/C/C | C/C/C | C/C/C |

The first prototype screen never loaded the procedure; extending the cue exposed acceptance
guidance. Deadline changes varied across attempts. Deletion-based and blanket-production
failures remain historical; they do not assess revised retention. Visual repeat 2 lacks direct
save/recovery operation.

Moving the instruction first met planning. Inspection uncertainties remain; the visual screen
omitted completed volunteer-first checkout. Judges passed several outcomes retained as U, including visual
repeats, adjacent repeat 1, the plan-order screen and final repeat 1. Introductory HTML or
lengths and incomplete state inspection were insufficient. Final repeat 2 lacked checkout.
Final repeat 3 is C despite its original U: rendered relationships, keyboard destination and
an inspected focus ring suffice together. Duplicate cancellation subtypes and per-state structural
copies are unnecessary. Criticism of blocked production planning and demands for invented
rejection reasons exceed the rubric.

One visual GUI repeat originally errored because its grader located the pane through permanent
"Plain text" footer content. Editor and Save anchors fix that unsupported assumption. The
regression failed before correction, passed after, and rejects a missing dialog frame. All
four saved baseline/visual outputs passed 30 corrected checks.

## Reviewed wording

The comparison now retains both runnable alternatives with inline clearly marked rejected.
Production may follow settled necessary decisions. Candidate requests, fixtures and checks did
not change.

| Case | Fresh baseline | Reviewed repeats |
| --- | --- | --- |
| interactive-prototype-comparison | F operable-comparison: no rejected label; F acceptance: early recording/no label | U direct-operation: editing/save/recovery<br>C<br>C |
| new-interface-design | F plan: built first; U inspection: focus/transaction structure | U inspection: transaction structure<br>C<br>U inspection: transaction structure |
| prototype-returns-to-planning | C | C/C/C |
| delivery-retains-accepted-prototype | C | C/C/C |
| gui-accepted-design | C | C/C/C |

All 20 fresh assessments and five joint comparisons completed. Reviewed repeats reconcile to
12 C and three U. All three prototype repeats marked and kept rejected alternatives; all three design repeats
planned before building. Unknown criteria are tagged above. The joint judge passes design
repeat 1, which remains U.
Repeat 2 is C despite its original U: full runtime relationship text supports inspection, and
the joint judge agrees. An explicit no-refinement-needed statement is unnecessary.
GUI repeat 2 deleted captures before independent review, an observed violation outside its
four frozen criteria. Its passing case verdict does not establish retention compliance.

## Method and limits

Historical baseline is `ba604f4`; the fresh baseline is `705d93d`. Source copies include
repository skills, global instructions and declared unslop. Candidate and separate blinded
judge use gpt-6.1-sol, 1800/1200-second allowances and disabled token guards. Inputs and private
criteria stay fixed within each comparison. Browser and service fixtures are local. Related
cases establish requested experiments and accepted-source handling, not autonomous prototyping.
469 framework tests, quality checks and 151 definitions pass. Both independent reviews pass.
Raw evidence was deleted afterward.
Native compaction remains deferred. Same-family judges and these fixtures do not establish
production reliability or full-corpus rates.
