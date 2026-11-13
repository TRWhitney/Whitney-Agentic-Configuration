# PR verification limits

The fifth approved diff is applied unchanged. All six final PR attempts are correct, three per
task/control. Earlier failures and wrong judgments remain below.

## Method

Sources start at 0245e23. Tasks, private criteria, other instructions and settings stay fixed.
Candidates and a separate blinded judge use gpt-6.1-sol, 1800/1200-second allowances and disabled
token guards. Same-family judging remains a limitation. Only GitHub delivery text differs.
The tested diffs are the [first clause](pr-verification-limits-proposal.diff),
[direct wording](pr-verification-limits-next-proposal.diff), [update step](pr-verification-limits-third-proposal.diff),
[deadline](pr-verification-limits-fourth-proposal.diff), and [final wording](pr-verification-limits-fifth-proposal.diff).
No live GitHub operations or global deployment occurred.

## Inspected outcomes

C/I mean correct/incorrect, in attempt order. All 32 PR assessments completed. Automation returned
31 passes and 1 failure; inspection gives:

| Case | Baseline | First | Second | Third | Fourth | Fifth |
| --- | --- | --- | --- | --- | --- | --- |
| github-pr-description | I | I/I/I | I/I/I | C/I/I | I/C/C | C/C/C |
| github-pr-description-small | C | C/C/I | C/C/C | C/C/C | C/C/C | C/C/C |

Earlier batch failures violate revision-evidence: the agent requests hosted status after filing,
receives no requested result, and leaves the body unchanged. Some get an unsupported check
command. Requirements-only caveats and generic local-test disclaimers do not report unavailable
hosted results. Replies/work records contain information missing from the PR.

Third-wording main1 and fourth-wording main3 update their posted bodies after the lookup.
Fourth-wording main2 starts accurate. Fifth-wording main1 also updates after the lookup;
main2 already says hosted results were not obtained. Main3 directly states actual hosted
results are unknown, separately from requirements. That valid paraphrase does not claim jobs
are queued/running or merely remind the reader to assess checks later. No fixed phrase is required.
All final bodies preserve sections, supported examples, revision links and issue references.

## Corrected judgments

Initial inspection accepted the baseline main and first-wording main1/2. A uniform audit corrects
those passes to I and preserves them here: requirements were confused with results. The
[accepted distinction](unslop-writing-trials.md#failures-and-limits) already required result disclosure;
criteria did not change. Corrected counts do not establish deterioration between versions.

First-wording small3 omits known unavailable check status. Third-wording small3 receives an
incorrect automatic rejection for duplicate diff/review failures. Supplied history and unchanged
files establish its claims; no hosted-status request or remote-review success claim exists.
Primary and independent inspection agree it is C. Irrelevant metadata failures need no warning.

## Proof and limits

Complete outputs, filed bodies, relevant actions/artifacts and available child findings were
inspected. Sources/digests and recorded isolation match all 32 PR attempts. Final instructions
are actually returned in all six action records. All 25 calibration labels agree despite actual
false judgments. Eleven focused framework tests and quality checks pass; 160 definitions validate.
No full-corpus rerun is claimed. Independent intent and engineering review passed. Raw captures were deleted.

The earlier approved rename correction has three fresh correct attempts, separate from the
PR-only follow-ups. One interrupted unapproved comparison and three earlier unapproved rename
attempts were excluded and deleted; they establish no performance conclusion.
