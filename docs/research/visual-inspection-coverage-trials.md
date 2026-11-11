# Visual inspection coverage trials

## Method and conclusion

The [original proposal](visual-inspection-coverage-proposal.diff) was rejected. The
[V16 follow-up](visual-inspection-coverage-followup-proposal.diff) passed but put the method in
generic implementation. The [placement correction](visual-verification-placement-proposal.diff)
is applied inside visual verification. Ticket-60 source and captures are unavailable;
these tasks reconstruct the cause.

Candidates and separate blinded judges use gpt-6.1-sol, isolated repository sources,
1800/1200-second allowances and disabled token guards. Inputs and settings stay fixed within
comparisons. Earlier baselines `ef9d83b`/`dbf75cb` have identical
instructions. Same-family judging limits generalization. No full-corpus rerun.

## Original evaluation corrections

[Agenda](../../evals/cases/gui-state-selection.json) attempt 3 hides stored notes despite both
judges passing it. A supplied saved visit starts a fresh comparison. Private checks accept
compatible keys, migration, fallback and accessible labels; eleven earlier outputs reveal no
further loss.

Per-output artifact paths repair wrong-output citations. Initial visual selection and retention
judgments are 5/5 and 2/4; isolated/applied repairs are 12/12 and 9/9. All 30 complete.
A 14px narrow-search collapse after document growth triggers rechecking 21 earlier outputs.
Private replays prove product behavior, never candidate inspection.

## Original attempts

C/F/U mean correct, incorrect and unknown. No original exclusions.

| Case | Baseline | First wording | Saved-visit baseline / first wording | Second wording | Third wording | Fourth wording | Failure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gui-clean-audit | C | C/C/C | Not changed | C/C/C | C/C/C | C/F/C | Fourth attempt 2 retains narrow-search collapse. |
| gui-combined-conditions | C | C/C/C | Not changed | C/C/C | C/C/C | F/C/C | Fourth attempt 1 retains that collapse despite passing focused composition criteria. |
| gui-state-changes | F | F/F/C | Not changed | F/C/F | F/F/F | C/F/F | Corrected-input inspection omitted. Version 1 attempt 2, version 2 attempts 1/3 and version 3 attempt 2 also retain narrow-search collapse. |
| gui-state-selection | C | C/C/F | C / C/C/C | C/C/C | C/C/C | C/C/C | Original version 1 attempt 3 hides old notes. |

All 56 candidate and 48 joint assessments complete. Inspection corrects V3 attempt 3's false
pass and attempt 2's observation credit. Some restoration rationales overstate screenshots.
V4 product uncertainty resolves from private replays; inspection omissions still fail. No U
remains. Changed guidance was loaded. Reviews passed; original raw evidence was deleted.

## Follow-up trials

Four excluded setup slots lack an external skill; no candidates run. Copies are corrected.
V5 skips correction; V6 loads guidance earlier; V7 uses numbered steps; V8 adds automated
observations. V9 moves them into implementation; V10 adds content variation; V11 traces review
evidence; V12 varies each affected part; V13 derives checks from requirements. All retain
omissions or collapse.

| Case | Fresh baseline | Fifth | Sixth | Seventh | Eighth | Ninth to twelfth | Thirteenth |
| --- | --- | --- | --- | --- | --- | --- | --- |
| gui-clean-audit | C | C | C | C | C/C/C | Not run | C/C/C |
| gui-combined-conditions | C | Not run | Not run | Not run | C/C/C | Not run | C/C/C |
| gui-state-changes | F | F | F | F | C/F/F | F/F/F/F | C/F/F |
| gui-state-selection | C | Not run | Not run | Not run | C/C/C | Not run | C/C/C |

All 38 assessments complete. Omissions fail flow-observation/completion-evidence; collapse fails
the browser check. Inspection corrects V5/V7/V8 false passes and V6 product/observation judgments.
Baseline transitions miss restoration. The control's sleep warning leaves relevant channels
complete; C. V5 control overstates correction despite meeting criteria.

## Clarified requirement

The [shared fixture](../../evals/cases/fixtures/gui-project.json) now says filtering preserves
height for the same documents. Reviews mistook "reserves" for a minimum. Intent and criteria remain unchanged. Changed Fieldnotes inputs
start fresh comparisons. Agenda definitions and instructions are identical, permitting reuse.

| Case | Baseline | Unchanged V13 | V14 | V15 | V16 |
| --- | --- | --- | --- | --- | --- |
| gui-clean-audit | C | C/C/C | C/C/C | C/C/C | C/C/C |
| gui-combined-conditions | C | C/C/C | C/C/C | C/C/C | C/C/C |
| gui-state-changes | F | C/F/C | C/F/F | C/F/C | C/C/C |
| gui-state-selection | C, reused | C/C/C, reused | C/C/C | C/C/C | C/C/C |

Clarified baseline/V14 omit correction; V13 omits restoration; V15 omits both.
Inspection corrects a false pass.
Through V16, all 86 candidates and 28 joint judgments complete; twelve final attempts are correct.
Existing Retry races and incomplete literal-reload probes limit these fixtures.

## Visual verification placement

| Case | Baseline 0b8074d | V17 | V18 | V19 | V20 |
| --- | --- | --- | --- | --- | --- |
| gui-state-changes | C | C/F/F | F/U/Excluded | F/C/F | C/C/C |
| gui-clean-audit | C | C/C/C | C/U/Excluded | Not run | C/C/C |
| gui-combined-conditions | C | C/C/C | C/U/Excluded | Not run | C/C/C |
| gui-state-selection | C | C/C/C | C/U/Excluded | Not run | C/C/C |

V17 relocates the method; V18 traces observations after passing checks; V19 emphasizes feedback
while editing. Their failures still omit corrected-input inspection. Extra restoration and
matching-search omission rationales are unsupported. V20 maps each affected control's display
changes before inspecting; all twelve final attempts are correct. Its exact diff is applied.

V18 quota interruption leaves four second attempts U and four third slots unstarted/excluded.
Four original judge calls fail. Recovery completes eight paired judgments without overwriting errors.
Sixteen final joint judgments complete. Both reviews pass; raw evidence deleted.
