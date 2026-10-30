# Rework commit trials

**27 final attempts were correct**, three per case or control. Assessments completed.
The [tested diff](rework-commit-proposal.diff) is applied. No context-clearing steps ran.

## Final confirmation

| Case or control | Correct | Incorrect | Assessment |
| --- | --- | --- | --- |
| Code correction | 3 | 0 | Complete |
| Prose corrections | 3 | 0 | Complete |
| Retain the fix and additional regression tests | 3 | 0 | Complete |
| Repair a review finding | 3 | 0 | Complete |
| Separate independent work, then requested squash and reset | 3 | 0 | Complete |
| Pushed, no rewrite request | 3 | 0 | Complete |
| Pushed, explicit rewrite request | 3 | 0 | Complete |
| Another conversation, pushed | 3 | 0 | Complete |
| Another conversation, unpushed | 3 | 0 | Complete |

The accepted conditions remain unchanged. One lookup sentence changed:

```diff
-Run `scripts/navigate.py commit list` to find commits made in this session.
+Before creating a new commit, run `scripts/navigate.py commit list` and check these conditions.
```

Navigator operations store, list, replace and remove commit IDs in external conversation state.
They make no amendment or publication decision. The documentation procedure is unchanged.
All three coverage reassessments passed after a stale rubric phrase was corrected.

## Case corrections

The code and prose cases now begin with ordinary work performed by the agent, followed by
corrections. The earlier-edit case adds regression coverage for the same stock-total fix.
Its former stock and message edits did not establish one logical unit. A tested missing-quantity
variant also changed the input contract, so it was replaced. No forced amendment of unrelated
work remains. Existing case count stays 151.

Private checks compare saved IDs with Git history. Review setup registers its conversation
commit through the navigator. Markdown ownership claims and their preservation criterion and
calibration were removed. Explicit squash and reset requests test record updates separately
from automatic folding.

## Current comparisons

C means correct, F incorrect, U unknown. All assessments completed. Four `screen` attempts ran
no candidate because the frozen source lacked its existing unslop dependency. Initial independent
work omitted the item format and is excluded. Earlier-edit variants described above are superseded.

| Trial | Outcomes in order |
| --- | --- |
| amend-code | F, F, F |
| check-earlier | F, F, F |
| command-code | F, F, F |
| command-earlier | F, F, F |
| command-prose | C, C, F |
| control-older-pushed | C |
| control-older-unpushed | C |
| control-permission | C |
| control-published | C |
| decision-code | F, F, F |
| lookup-code | F, F, F |
| lookup-earlier | F, F, F |
| lookup-independent | C |
| qualified-code | C, C, F |
| qualified-prose | C, C, C |
| real-code | F |
| real-earlier | C |
| real-prose | C |
| rework-code | C, F, C |
| screen-code | U |
| screen-independent | U |
| screen-prose | U |
| screen-repair | U |
| trial-code | F |
| trial-independent | F |
| trial-prose | F |
| trial-repair | C |

These 49 other attempts are retained above. Failed correction attempts generally
created new commits. Lookup timing, amendment commands, command paths and rework-wording trials
were insufficient. Only the final lookup sentence was retained.

Inspection covered replies, exact edits, executable regression tests, child-review findings,
Git history and saved IDs. 465 framework tests pass, including 41 navigator tests. Candidate and
blind judge used gpt-6.1-sol. Three repeats support the tested cases, not a production failure rate.
Publication used disposable local remotes. Native compaction, live hosting and correction of
older non-HEAD session commits remain untested.

## Withdrawn documentation proposal

Its 217 assessments completed, including 45 confirmation passes. These tested a withdrawn
requirement to retain session and publication facts in documents. Four false file-check rejections
are superseded; all 22 saved checks passed after correction. Two four-example calibrations each
had complete 4/4 agreement but tested the withdrawn requirement.

| Case or control | Correct | Incorrect |
| --- | --- | --- |
| Code correction | 5 | 0 |
| Prose corrections | 5 | 0 |
| Preserve the earlier edit and tests | 5 | 0 |
| Repair a review finding | 5 | 0 |
| Separate independent commits | 5 | 0 |
| Earlier-session, pushed commit | 5 | 0 |
| Earlier-session, unpushed commit | 5 | 0 |
| Pushed, no rewrite request | 5 | 0 |
| Pushed, explicit rewrite request | 5 | 0 |

| Wording or comparison | Correct | Incorrect | Superseded |
| --- | --- | --- | --- |
| Preserve commit facts, initial screen | 6 | 0 | 0 |
| Choose before staging, initial screen | 6 | 0 | 0 |
| Shorter preservation rule, full set | 35 | 1 | 4 |
| Corrected earlier-edit grader | 5 | 0 | 0 |
| Choose before staging, review repairs | 5 | 0 | 0 |
| Choose before staging, full set | 39 | 1 | 0 |
| Identify target first, repair screen | 10 | 0 | 0 |
| Identify target first, full set | 37 | 3 | 0 |
| Explicit remote check, repair and publication screen | 10 | 0 | 0 |
| Preserve facts in skill entry, earlier-edit screen | 5 | 0 | 0 |
| Preserve facts in documentation, earlier-edit screen | 5 | 0 | 0 |
| Final confirmation above | 45 | 0 | 0 |

The shorter and before-staging sets created new review-repair commits on attempt 1.
Identify-first amended pushed commits on attempts 3 and 4 and lost recorded facts on earlier-edit
attempt 5.

## Previous publication revision

All 24 assessments completed. Review repair created a new commit; earlier-edit lost recorded facts.

| Case or control | Attempt 1 | Attempt 2 | Attempt 3 |
| --- | --- | --- | --- |
| Code correction | Correct | Correct | Correct |
| Prose corrections | Correct | Correct | Correct |
| Preserve the earlier edit | Correct | Incorrect | Correct |
| Repair a review finding | Incorrect | Correct | Correct |
| Independent commits | Correct | Correct | Correct |
| Earlier-session prefix | Correct | Correct | Correct |
| Pushed, no rewrite request | Correct | Correct | Correct |
| Pushed, explicit rewrite request | Correct | Correct | Correct |

## Earlier comparisons

All 154 assessments completed under the superseded pushed-amendment policy. Six U outcomes lacked
child-review findings. F outcomes failed amendment history; one also changed unrelated history.
Two passing drafts could amend the wrong commit.

| Draft | Code correction | Prose correction | Earlier edit | Review repair | Independent results | Earlier-session prefix |
| --- | --- | --- | --- | --- | --- | --- |
| Original skill | F, F, F, F, F | F, F, F, F, F | F, F, F, C, F | F, F, F, F, F | C, C, C, C | C, C, C, C |
| explicit-amend | F | F | F | U | Not run | Not run |
| check-history | F | F | F | U | Not run | Not run |
| amend-first | F | F | F | U | Not run | Not run |
| history-first | F | F | F | U | Not run | Not run |
| record-path | F | F | F | U | Not run | Not run |
| record-path-first | F | F | F | U | Not run | Not run |
| session-before-request | F | F | C | Not run | Not run | Not run |
| read-records | C, C, C, C | C, C, C, C | C, C, C, C | C, C, C | C, C, C | C, C, C |
| record-files | C, C, C | C, C, C | C, C, C | C, C, C | C, C, C | C, C, C |
| lookup-only | F | C | C | F | Not run | Not run |
| lookup-first | C | C | C | F | Not run | Not run |
| lookup-amend | C | C | C | F | Not run | Not run |
| lookup-command | F | C | C | F | Not run | Not run |
| target-commit | C, C, C, C | C, C, C, C | C, C, C, C | C, C, C, C | C, C, C | C, C, C |
| target-no-command | C | C | C | C | Not run | Not run |
| record-lookup | C, C, C | C, C, C | C, F, C | F, C, C | C, C, C | C, C, C |

Eight setup failures and one control-validation failure ran no candidate. Three observation probes
yielded two unknown and one incorrect amendment with missing review findings.
