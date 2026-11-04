# Interface and prototype trials

Trials investigate [prototype comparison](integration-and-acceptance-evals.md#outcomes)
and [interface design](main-procedure-path-evals.md#outcomes). The
[proposed skill diff](interface-prototype-proposal.diff) remains unapplied.

## Outcomes

C means correct, F incorrect, U unknown. "Not run" marks an untested pairing. Each entry is one
attempt in execution order. All 59 candidate assessments and five joint comparisons completed.
Final behavior is 13 C and two U. No candidate attempt is excluded.

Plan means `specific-design-plan`, inspection `rendered-inspection-and-critique`, and operation
`runnable-choice`. Tags identify every failed or uncertain criterion; all others are met.

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

The comparison baseline repaired and operated the summary, but acceptance failed through early
recording and retained inline source. Its first screen never loaded the edited procedure and
implemented production after confirmation. Extending the cue reached the procedure and improved
interpretation, but cleanup still failed. An explicit deadline passed once, then all three
visual repeats retained inline source. Moving cleanup beside confirmation removed it in all
three repeats; one implemented production after silently settling an unanswered app/storage
choice. Its F and source-preservation failures used the old production ban. Production
is allowed after necessary decisions are settled; both checks are removed. Historical
verdicts remain; corrected behavior is untested.
Visual repeat 2 also lacks direct-operation proof.

The design baseline and first screen built before the complete plan. Moving the planning
instruction first corrected that criterion. Later U outcomes concern rendered inspection;
the visual screen also lacks a completed volunteer-first checkout trial. Focus and state
inspection remain incomplete in several attempts despite useful observed refinements.

Judges pass several inspection outcomes retained here as U: introductory HTML or lengths and
incomplete state inspection remain insufficient. These include visual repeats, adjacent repeat 1,
the plan-order screen and final repeat 1. Final repeat 2 lacks completed
volunteer-first checkout. Final repeat 3 is C despite its original U: rendered relationship text,
keyboard destination and an inspected focus ring suffice together. Per-state structural copies
and duplicate cancellation subtypes are unnecessary. Criticism of blocked production planning
and demands for invented rejection reasons exceed the rubric.

One visual GUI repeat originally errored because the private grader located its pane through
permanent "Plain text" footer content. Applied format may change that content. Anchoring through
editor and Save fixes it. The regression fails before correction, passes after, and still
rejects a missing dialog frame. All four saved baseline/visual outputs pass 30 corrected checks.

## Method and limits

Baseline `ba604f4` supplies repository skills, global instructions and declared unslop. Candidate
and separate blinded judge use gpt-6.1-sol, 1800/1200-second allowances and disabled token guards.
Tasks, resolved fixtures and private criteria are fixed. Publication and browser services are
local. The related cases cover continuation after a requested experiment, accepted-source
retention and production design adherence. They do not establish autonomous prototype selection.

468 framework tests, 151 definitions, lint, formatting and strict typing pass. Outputs, actions,
images and available child findings were inspected. Independent intent and engineering reviews
pass. Raw evidence was deleted after review. Fixtures and same-family judges do not establish
production reliability or full-corpus rates.
The two final unknowns remain unresolved. Native compaction remains deferred.
