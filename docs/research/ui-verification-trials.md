# UI verification wording trials

The pending [test-quality patch](test-quality-proposal.diff) is applied unchanged in `b1268c2`.
This study covers 77 candidate attempts across three existing cases. Three setup slots lacked
the declared unslop source and are excluded; no candidate work occurred. No cases were added.

## Findings

The [tested skill diff](ui-verification-proposal.diff) is applied unchanged. It clarifies complete
flows in each alternative, successful completion and recovery, substantive structural inspection,
browser opening of both prototype and app, and confirmation before recording acceptance.

Two rubric errors needed clarification. Linked notes can present an interpretation; selection
is not final acceptance. Comparison-only wording can reject an alternative without a literal
rejection word. A fresh corrected-rubric comparison is F/C. Lost confirmed flexibility still fails.

Structural inspection accepts rendered text, DOM content and equivalent targeted queries. Extra
geometry, a cancelled-state screenshot and repeated cancellation exercises are unnecessary.
Independent inspection corrected false passes and false failures. Initial final review found
one additional omission despite a passing judge: headings and control heights did not expose
return/volunteer relationships. That version remains F/C/C. Adding values and excluding headings
alone produces three fresh design passes, alongside three prototype and three GUI passes.
Independent intent and engineering correction reviews pass.

A matched assessor comparison reuses six frozen outputs three times. The original prompt gets
9/18 inspection judgments right; the actual-read clarification gets 18/18. Both prompts produce
one disputed presentation failure. Extending to seven outputs reveals another false pass in
both repeats. An extra partial-read sentence still misses it twice and additionally disputes
one previously accepted inspection. All 28 extension assessments complete; that sentence is rejected.

Two prototype verdicts were unknown despite all criteria being met. Rejected URL-only requests
never reached the browser receipt writer. Failure receipts fix the regression; genuine missing
receipts still warn. Read-only diagnosis and recording review establish sufficient observations;
reassessment passes all three, retaining original warnings and unknowns.

## Attempts

C/F/U mean correct, incorrect and unknown, in attempt order. Arrows preserve original judgments
followed by inspected or repaired conclusions. Every formal assessment completed. Reassessment
rows reuse work. Initial review found the omitted inspection; both correction reviews pass.

| Stage | Prototype | Design | GUI control | Failed criteria and reason |
| --- | --- | --- | --- | --- |
| Excluded setup | U | U | U | Missing unslop; no candidate execution |
| Fresh baseline | F | C → F | C | Prototype acceptance before interpretation; design rendered-inspection-and-critique lacks transaction structure |
| First wording | F/C/C | C/C/C → C/C/F | C/C/C | Prototype 1 direct-operation misses recovery; design 3 rendered-inspection-and-critique misses transaction structure |
| First joint assessment, same work | Baseline F; F/C/C | Baseline C → F; C/C/F | Baseline C; C/C/C | Same inspected conclusions; twelve assessments complete |
| Recovery wording in prototype | F/C/C | Not run | C/C/C | Prototype 1 acceptance omits confirmed flexibility; production work and semantic rejection are permitted |
| Main-task content | Not run | C/C/C → C/C/F | C/C/C | Design 3 rendered-inspection-and-critique lacks transaction structure |
| Recovery in GUI validation | F/C/C → C/C/C | C/C/C → C/F/C | C/F/C | Design 2 rendered-inspection-and-critique; GUI 2 observed-comparison/honest-completion, prototype unopened |
| Second joint assessment, same work | Baseline F; F/C/C → C/C/C | Baseline C → F; C/C/C → C/F/C | Baseline C; C/F/C | Same inspected conclusions; twelve assessments complete |
| Open both in browser | Not run | C/C/F → F/F/F | C/C/C | Designs 1/2 rendered-inspection-and-critique; design 3 also runnable-choice, no equipment-first return |
| Grouping screen | Not run | F | Not run | rendered-inspection-and-critique, checkout image and transaction structure omitted |
| Each-state screen | Not run | C → F | Not run | rendered-inspection-and-critique, volunteer loan/available grouping omitted |
| Revised-rubric comparison | Current F; trial C | Not run | Not run | Current direct-operation lacks editing, saving and recovery |
| Each-alternative flow screen | Not run | C → F | Not run | rendered-inspection-and-critique, heading presence/counts only |
| Each-alternative repeats | C/C/F | Not run | C/C/C | Prototype 3 direct-operation checks summaries only |
| Read-content screen | Not run | F | Not run | rendered-inspection-and-critique, headers/keys/lengths only |
| Successful-flow completion | C/C/C | Not run | C/C/C | None |
| Read-complete screen | Not run | F | Not run | rendered-inspection-and-critique, checkout/volunteer structures omitted; cancellation did pass |
| Read-each screen | Not run | C → F | Not run | rendered-inspection-and-critique, main text omits active transaction relationships |
| Relationships wording | U/U/C → C/C/C | C/C/C → F/C/C | C/C/C | Prototype capture warnings were false alarms; design 1 omitted return/volunteer structure |
| Relationships joint comparison, same work | Baseline F; C/C/C | Baseline C → F; C/C/C → F/C/C | Baseline C; C/C/C | Baseline design and trial 1 inspection disagreements retained |
| Values and headings, final version | C/C/C | C/C/C | C/C/C | All criteria met; both correction reviews pass |
| Final joint comparison, same work | Baseline F; C/C/C | Baseline F; C/C/C | Baseline C; C/C/C | Twelve assessments complete |

## Checks and limits

All 81 authored calibration judgments match, including intentional missing-observation controls:
15 on the initial five acceptance examples, 18 on six examples, then 18 acceptance, 18 dialog
and 12 structural judgments with the assessor clarification. All 36 matched reassessments
completed. All 490 framework tests, affected checks, quality checks and 151 definitions pass.

Candidates and separate blinded judges use gpt-6.1-sol, 1800/1200-second allowances and disabled
token guards. Tasks, resolved fixtures, settings and private criteria remain fixed within each
comparison; rubric correction receives fresh work. Valid attempts use verified isolation.
Same-family judging and reconstructed tasks limit generalization. Native compaction and a
full-corpus rerun remain deferred. Raw evidence was inspected and reviewed outside the checkout, then deleted before delivery.
