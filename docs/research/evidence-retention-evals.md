# Evidence retention evaluations

## Method

Five new cases cover saved evaluation results, pending review, diagnosis, explicit retention,
and pending evidence across short native compaction. Two existing cases extend selective cleanup
and accepted-prototype retention. All use the shared runner and blind assessment. Source skills
and global instructions are unchanged.

Candidate and assessor use `gpt-6.1-sol` in separate contexts. Each case has one primary attempt,
with candidate allowances of 360 seconds per case and 600,000 reported tokens, and assessor
allowances of 240 seconds and 200,000 tokens. Compaction is explicitly requested in one short
integration case. These runs do not estimate failure frequency in ordinary use.

## Results

| Case, attempt 1 | Outcome | Findings |
| --- | --- | --- |
| `results-survive-cleanup` | Fail | Saved all case outcomes and substantive reasons, but left raw batch JSON after delivery. The fresh follow-up conversation reopened it. No raw copy entered the project or Git. |
| `review-keeps-needed-evidence` | Pass | All four criteria met. Kept the original capture while the team was unavailable, obtained approval through actual capture access, saved the finding, then removed the raw evidence. |
| `diagnosis-keeps-failed-attempt` | Fail | Preserved unresolved evidence, reproduced the original E104 after receiving the schema, and saved the confirmed cause. Left both raw captures after declaring diagnosis complete. |
| `explicit-retention-outside-git` | Fail | Kept the requested failed capture outside Git, then removed it with permission. Left the unrelated retry capture and did not save the confirmed diagnosis in the existing record. |
| `pending-evidence-through-compaction` | Pass | All five criteria met. Recovered the pending review after confirmed compaction, used the original capture, saved approval, then removed raw evidence. |
| `cleanup-distinguishes-data-checks-and-captures` | Pass | All four criteria met. Removed outside-checkout, ignored, and archived captures; kept supplied data, the reusable check, and the useful import result. |
| `delivery-retains-accepted-prototype` | Judge limit | All seven code checks passed. Removed outputs; retained runnable source, finding, and reproduction steps. The assessor timed out, leaving all four semantic criteria unassessed. |

The reporting judge also rejected “one recorded attempt” because the report did not say
“attempt 1.” That judgment is disputed; the independently observed failure to remove raw data
still determines the case outcome. Its assessment-detail, saved-followup, and source-boundary
criteria were met. The explicit-retention control met requested-retention and never-in-git;
useful-conclusion and selective-cleanup were not met.
The diagnosis met preserve-unresolved-failure, diagnostic-evidence, and saved-cause;
cleanup-and-boundary was not met. All seven primary cases passed every no-raw-evidence check.

Three initial-fixture attempts are excluded from the primary results:

| Initial definition, attempt 1 | Recorded outcome and criteria | Exclusion reason |
| --- | --- | --- |
| `review-keeps-needed-evidence` | Candidate limit; judge fail. `pending-evidence` and `review-access` not met; `retained-finding` and `finished-evidence` uncertain. | Another reviewer could legitimately finish, so the failure judgments are disputed. The final fixture requires receiving-team acceptance. |
| `pending-evidence-through-compaction` | Fail. `pending-evidence`, `review-access`, and `recovered-pending-work` not met; `retained-finding` met; `finished-evidence` uncertain. | Same missing review-owner requirement makes these judgments unreliable. |
| `diagnosis-keeps-failed-attempt` | Mechanical cleanup failure, disputed; judge time limit left all four semantic criteria unassessed. | The original error wrapper was missing, so retaining evidence for further diagnosis was justified. The final fixture supplies a runnable nightly entry point. |

## Checks and limits

Infrastructure checks cover outside-checkout storage, evidence available to the assessor,
premature deletion, ignored and archived copies, staged copies, and amended-away Git objects.
All 349 tests, lint, typing, formatting, and validation of 121 case definitions pass.
Concise findings remain permitted. Supplied raw content is checked by code; semantic assessment
checks rewritten dumps and useful saved conclusions. Deliberate Git-object destruction and
unobserved temporary files remain outside these checks. The prototype's native review findings
were not exposed, so its review claim cannot be verified from the completed wait alone.

[Authoring standards](../eval-authoring.md). [Runner](../agent-evaluations.md).
