# Eval reliability trials

The runner distinguishes capture defects, faulty expectations and unsupported judgments before
reassessing saved work. Missing required observations still require a fresh run.

## Native evidence

C/F/U mean correct, incorrect and unknown. Entries follow attempt order. These are original
assessments, not a current corpus failure rate. All completed attempts' outputs, relevant
operations, actual images and available child findings were inspected independently.

| Stage | Prototype comparison | Interface design | GUI control | Assessment | Unmet or uncertain criteria and recording faults |
| --- | --- | --- | --- | --- | --- |
| First capture screen | U/F/U | U/U/U | Not run | All 6 complete | Prototype 2: direct-operation. Design 2/3: rendered-inspection-and-critique uncertain. Quiet-command warnings block other passes. |
| Before enforced isolation | C/C/C | F/C/C | C/C/C | All 9 complete | Design 1: task-and-sources, rendered-inspection-and-critique. All prototype attempts contaminated. |
| Rejected permission profile | U | U | U/U | Not run; batches interrupted | Git writes blocked; no behavioral assessments. |
| Verified isolation | U/C/F | C/F/F | F/U/U | All 9 complete | Prototype 3: direct-operation, acceptance. Design 2/3: rendered-inspection-and-critique. GUI 1: observed-comparison. False wait warnings block prototype 1 and GUI 2/3. |
| Reassessment of verified work | C/C/F | C/F/F | F/C/C | All 9 complete | Prototype 3: acceptance. Design 2/3: rendered-inspection-and-critique. GUI 1: observed-comparison, honest-completion. Criterion disputes remain below. |
| Explicit browser-comparison criterion | Not run | Not run | C/C/C | All 3 complete | None; independent inspection confirms all three. |
| Final inspected conclusions, same work | C/C/F | C/F/F | C/C/C | All 9 complete | Prototype 3: direct-operation. Design 2/3: rendered-inspection-and-critique. No unknown behavior. |

The first screen falsely treated successful quiet commands as lost output. Prototype repeats
1/3 have sufficient evidence; repeat 2 omits post-error editability verification. Initial design
inspection exposes introductory markup rather than transaction relationships; the first
judge's favorable criterion judgment remains disputed.

Every pre-isolation prototype repeat reused an undeclared helper from an earlier attempt.
Their recorded operations occurred, but they are excluded from autonomous-behavior comparisons.
No such reuse was observed in the design or GUI records; their execution boundary was still
unverified. The rejected profile prevented legitimate Git writes. Four started attempts lack
finished assessment evidence and remain unknown, not behavioral failures.

Verified isolation blocks foreign temporary files and private cases while allowing fixture,
Git and scratch operations. Native profile confirmation and network probes pass. Untargeted
waits falsely reported missing child identifiers even when completed findings survived;
a failing regression exposed this, and reassessment independently confirmed data sufficiency.

The interface rubric now explicitly names transaction relationships and distinguishes a
complete-record omission from unavailable observations. No candidate-visible input changed.
The latest design omissions are confirmed; additional filtering judgments remain disputed.

Visual comparison requires opening both the finished application and accepted prototype in a
browser. The private GUI criterion now states this; all three fresh assessments pass. Blank-input
feedback must leave the name editable; no fixed input sequence is required. Independent
inspection confirms verified prototype repeat 3 never checks post-error field editability.
Verified GUI repeat 1 never rendered the reference. Its disputed negative comparison judgment
matches the clarified intent; earlier attempts are not silently rescored under changed wording.
Prototype 3 still fails direct-operation. Reassessment wrongly treats recorded selection as
final acceptance and ordinary saving as post-error editability verification. Original judgments
remain visible separately from these inspected conclusions.

## Calibration

Two added controls exposed overly strict same-dialog-save and typing requirements.
The corrected criterion accepts interaction or runtime editability checks and separate saving.
All 115 classifications completed; 113 matched their labels. Both disagreements and subsequent
checks follow.

M/N/U mean met, not met and uncertain. Multipliers give repeated identical verdicts. Preflight
columns identify their associated native batches, including the rejected permission profile.

| Example | Expected | Early | Added control | Revised | Before isolation | Rejected profile | Verified isolation | Editable feedback |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dialog buttons | M | M×3 | Not run | M×3 | M | M | M×3 | M×3 |
| Dialog keyboard | M | M×3 | Not run | M×3 | M | M | M×3 | M×3 |
| Dialog edit then cancel | M | Not run | N | M×3 | Not run | M | M×3 | M×3 |
| Dialog runtime editability | M | Not run | N | Not run | Not run | Not run | Not run | M×3 |
| Dialog omitted flows | N | N×3 | Not run | N×3 | N | N | N×3 | N×3 |
| Dialog lost observations | U | U×3 | Not run | U×3 | U | U | U×3 | U×3 |
| Transaction DOM and geometry | M | M×3 | Not run | M×3 | M | M | M×3 | Not run |
| Transaction text and geometry | M | M×3 | Not run | M×3 | M | M | M×3 | Not run |
| Transaction header only | N | N×3 | Not run | N×3 | N | N | N×3 | Not run |
| Transaction unavailable observations | U | U×3 | Not run | U×3 | U | U | U×3 | Not run |

Native candidates and separate judges use gpt-6.1-sol, 1800/1200-second allowances and disabled
token guards. Same-family judging remains a limitation. Runtime probes used no model inference;
rejected namespace approaches and browser smoke failures are setup evidence, not case results.
Explicit zero token arguments initially failed CLI validation before inference. A regression
now confirms unlimited zero allowances and rejects negative values.
Independent review is complete; finished raw evidence was deleted. Subject skills are unchanged.
Native compaction and a full-corpus rerun remain deferred.
