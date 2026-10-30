# Damaged workflow state

The navigator knew the selected tracker before reading conversation state, but a restoration
error prevented it from showing where work records lived. Failed restoration now returns the
path to the tracker's existing work-record guidance and asks the agent to find the work record
and explain recovery. Record locations remain in tracker guidance. The command still fails and preserves
the damaged state; it does not reconstruct a workflow.

The experimental skill instructions to explain recovery and search hidden directories were
removed. Its existing preservation rule remains. The eval request, fixtures, checks and criteria stayed unchanged;
the corpus still contains 151 cases.

## Outcomes

All rows use `damaged-navigation-record`. Original wording, recovery wording and script versions
used separate projects and homes. Candidates and blinded judges used gpt-6.1-sol.

The recovery sentence was "Explain which work records can help restore the workflow."
The next version added "Search hidden directories too." Script versions removed both sentences.

| Version | Attempts | Behavior | Assessment | Result |
| --- | --- | --- | --- | --- |
| Original wording | 1, 2, 3 | Incorrect | Complete | criterion-4: no recovery explanation identifying project records. |
| Recovery sentence, comparison | 1, 2, 3 | Correct | Complete | All criteria and code checks passed |
| Recovery sentence, confirmation | 1, 2, 3, 4 | Correct | Complete | All criteria and code checks passed |
| Recovery sentence, confirmation | 5 | Incorrect | Complete | criterion-4: search missed the existing work records. |
| Search hidden directories, trial | 1, 2, 3 | Correct | Complete | All criteria and code checks passed |
| Search hidden directories, stopped batch | 1, 2, 3 | Unknown | Stopped | No assessment or saved output packet; attempts 4 and 5 did not start. |
| Script path only | 1, 3 | Correct | Complete | All criteria and code checks passed |
| Script path only | 2 | Incorrect | Complete | criterion-4: omitted the recovery explanation. |
| Final script, trial | 1, 2, 3 | Correct | Complete | All criteria and code checks passed |
| Final script, confirmation | 1, 2, 3, 4, 5 | Correct | Complete | All criteria and code checks passed |

Twenty-five assessments completed: twenty correct and five incorrect. Three additional attempts
from a planned five-attempt batch were stopped before assessment while the recovery approach
was reconsidered. They have no saved output packet or behavior verdict; two attempts never started.

All eight final script attempts found the actual work record and distinguished it from the
damaged saved state. All source, state and publication checks passed. The other conversation
restored planning and correctly reported the unfinished search and export work.

The recovery sentence alone missed hidden records once. The first script prompt sent all three
agents to the tracker guide, but none located the actual work record. The judge accepted generic
recovery references in two replies; those passes do not establish record discovery. The final
prompt adds an explicit recovery explanation and all eight attempts identify the existing record.

This is repeated evidence for one existing local-tracker case using the same model family.
It does not establish a general failure rate. GitHub path selection has command-line regression tests,
not a new live evaluation. Compaction remains outside this change.

## Verification

Three tests of the navigator command failed before the change. Review also found that bytes
unreadable as text bypassed the recovery hint; its added test failed before correction.
All 434 framework tests now pass, including malformed JSON, unreadable bytes, invalid state
fields, tracker selection and preservation. Lint, formatting and strict typing across 73 files,
skill validation and all 151 definitions pass. Independent intent and engineering reviews pass,
including the bounded correction review. The eight live runs used readable malformed JSON;
the later decoding correction leaves that path unchanged. Unreadable bytes have command-line
regression coverage. Temporary evidence was removed after inspection and review.
