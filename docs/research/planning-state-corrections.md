# Planning records and workflow state corrections

Three skill files now require current planning records before replies, creation and reuse of
wayfinding records, and preservation of damaged workflow state. The state fields are defined
before use. Tracker questions can read another provider's rules without selecting it.
The proposed diagnosis instruction was withdrawn. The corpus remains at 151 cases.

The diagnosis eval now expects the small clarification to remain in fix discovery. Its retained
control accepts that state and rejects the former planning jump. Source preservation is unchanged.
This case does not establish that substantial design can stay in a fix.

## Previous proposal trials

These 18 completed assessments used the earlier forced-transition criterion. The table preserves
the original verdicts. No old diagnosis result is reused under the corrected criterion.

| Case | Original | First proposal | Revised proposal |
| --- | --- | --- | --- |
| agent-created-state-compaction | incorrect: criterion-2, python_check | incorrect: python_check | incorrect: criterion-1, python_check |
| damaged-navigation-record | correct | incorrect: criterion-1, criterion-2, criterion-3, criterion-4, unchanged, navigation_text | incorrect: criterion-4 |
| diagnosis-needs-design | incorrect: criterion-3, progress | correct | correct |
| requirements-change-during-implementation | incorrect: criterion-2 | incorrect: criterion-1 | correct |
| start-wayfinding-from-conversation | incorrect: criterion-1, criterion-2, python_check | correct | correct |
| tracker-separate-conversations | incorrect: planning-explanation | correct | correct |

The first proposal's requirements case corrected the records but failed criterion-1. The judge
identified an unrecorded selection contract and also objected to asking only about the format.
Requiring both questions in one reply is disputed. No instruction to ask both was added.
The first compaction proposal created a duplicate work index; its damaged-state attempt guessed
state and changed production. The revised compaction proposal created and linked records, but
omitted alternatives/tradeoffs and hit the map-filename defect. Its damaged-state attempt stopped
safely but failed the recovery-explanation criterion.

## Approved version

Candidates and blinded judges used gpt-6.1-sol. All six assessments completed. Four behaviors
were correct and two were incorrect under the retained checks and criteria.

| Case | Behavior | Evidence |
| --- | --- | --- |
| diagnosis-needs-design | Correct | Reproduced the sum, asked the negative-quantity clarification and stayed in fix discovery. No implementation. |
| requirements-change-during-implementation | Correct | Updated the specification, blocked the export ticket and preserved accepted CSV and completed search. |
| start-wayfinding-from-conversation | Correct | Reused the existing work record and linked the created map and feature requirements before asking. |
| agent-created-state-compaction | Incorrect | Created a second work index and left the existing one stale, failing the saved-link check. The model judge marked every criterion met; parent inspection identifies the missed record-reuse failure. Useful requirements and actual compaction recovery passed. |
| damaged-navigation-record | Incorrect | All source and state checks passed. Criterion-4 failed because the response did not distinguish the damaged conversation state from available project documents that could help recovery. The other conversation remained intact. |
| tracker-separate-conversations | Correct | Explained planning-document delivery and implementation tracking while keeping the local tracker selected. |

## Remaining findings

Reuse of the existing work record still needs attention.
[Recovery from damaged workflow state](damaged-state-recovery.md) records the later correction and results.
The compaction case's earlier alternatives/tradeoffs failure did not recur in this attempt.
The map check separately requires the leaf name map.md. It rejected a useful decision-map.md in
the revised proposal. The approved run used map.md, so that defect did not cause its failure.
The model judge also missed the approved run's duplicate work index; semantic review needs that
case covered. These assessment issues remain open rather than adding file-naming instructions.

These are small samples from the same model family. Earlier raw evidence had already been
removed; its table comes from retained findings. Approved-run replies, records and actions were
inspected before cleanup. No production failure rate or lasting fix is established.

## Verification

432 framework tests, skill validation, lint, formatting, strict typing across 70 files and all
151 definitions pass. An older framework control still required planning; it was updated to the
new expectation. Independent intent and engineering reviews pass. Raw run evidence was removed
after inspection and review.
