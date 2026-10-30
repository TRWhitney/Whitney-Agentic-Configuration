# GUI verification and follow-up evaluations

These results use earlier case definitions. See the [current corpus revision](workflow-eval-realism.md)
for changed inputs, grading corrections, and new outcomes.

Added nine cases and extended two existing cases, bringing the corpus to 130. Seven GUI cases
cover accepted-design adherence, rendered controls, transitions, combined conditions, alignment,
grouping, wrapping, and audit claims. Four follow-up behaviors cover separate conversations,
supplied input, attempt reporting, and factual questions after corrections.

The GUI project reconstructs a research notebook. It is not Linkwrite's original prototype.
Ordinary requests give no defect locations or verification reminders. The accepted design defines
required behavior and permitted variation. Browser checks reject all five defective implementation
variants and accept their corrected reference versions. The flawed audit retains its defects;
the clean audit supplies a correct interface. Font alternatives and real label wrapping have
separate infrastructure checks.

Candidates and blinded judges used gpt-6.1-sol in separate contexts. Candidates had 480 seconds
per case and one million reported cumulative tokens. Judges had 240 seconds and 200,000 tokens;
the two full audits also reached the time limit with a later 500,000-token allowance. No explicit compaction was
requested or context filled to cause one. Candidate captures, native image views, and private
browser checks remain distinct. Reassessment reused complete saved outputs without changing
candidate behavior or criteria.

## Results

Every required code check passed in the final GUI runs. All five implementation cases also pass
all four semantic criteria. The two audit judges timed out without verdicts for independent-inspection, accurate-findings,
coverage-and-claims, or review-boundary. Their artifacts were inspected manually; this does not
replace the missing independent verdicts.

| Case | Outcome | Finding |
| --- | --- | --- |
| gui-accepted-design | Pass | Shared naming frame restored; browser comparison observed. |
| gui-browser-rendering | Pass | Editor and selectors match; rendering and scrolling checked. |
| gui-state-changes | Pass | Validation and search remain stable through changes. |
| gui-combined-conditions | Pass | Retry clears stale status; failure fits the split pane. |
| gui-layout-and-wrapping | Pass | Alignment, grouping, wrapping, and content checks pass. |
| gui-incomplete-audit | Assessment limit | All four criteria unassessed. Manual inspection confirms five seeded defects reported with reproduction steps. |
| gui-clean-audit | Assessment limit | All four criteria unassessed. Manual inspection confirms no invented discrepancy or redesign. |
| cleanup-keeps-other-conversation-evidence, attempt 1 | Fail | Evidence isolation and eventual receiving-team review work, but export workflow remains active. Four criteria met; retained-conclusions uncertain because new native reviewer findings were unavailable. |
| cleanup-preserves-supplied-input, attempt 2 | Fail | Original input preserved; useful diagnosis and raw-source boundary pass. Finished-log-removed fails. |
| results-survive-cleanup, attempt 1 | Fail | All six attempt outcomes and reasons survive, including retries and unassessed timeouts. Concise-retention fails because finished batch JSON remains. |
| narrow-prose-correction, attempt 1, corrected assessment | Pass | All three edits and the factual answer succeed without another repository edit or amendment. All four criteria met. |
| narrow-prose-correction, attempt 2 | Limit | Three correction criteria met on observed frames; factual-question uncertain after token exhaustion. |

## Earlier attempts and assessment revisions

| Case | Initial direct-browser attempt | First worker attempt | Final worker assessment before packet repair |
| --- | --- | --- | --- |
| gui-accepted-design | Excluded: socket failure | Packet-size error; unassessed | Pass; reassessment also passes |
| gui-browser-rendering | Excluded: socket failure | Packet-size error; unassessed | Judge time limit; reassessment passes |
| gui-state-changes | Excluded: socket failure | Token limit; stable-transitions, flow-observation, retained-actions, completion-evidence uncertain | Packet-size error; later reassessment passes |
| gui-combined-conditions | Excluded: socket failure | Packet-size error; unassessed | Packet-size error; later reassessment passes |
| gui-layout-and-wrapping | Excluded: socket failure | Packet-size error; unassessed | Packet-size error; later reassessment passes |
| gui-incomplete-audit | Excluded: socket failure | Token limit; all four audit criteria uncertain | Packet-size error; repaired-packet judges reach token and time limits |
| gui-clean-audit | Excluded: socket failure | Packet-size error; unassessed | Packet-size error; repaired-packet judges reach token and time limits |

Initial GUI scores cannot establish a failure to choose visual checks: candidates attempted them,
but Chromium could not start. A project-only browser worker fixed execution without changing the
candidate sandbox. Initial prototype/footer inconsistency was corrected before worker runs.
Five first-worker packet errors discarded complete outputs before review; those attempts remain
unassessed. The runner now saves complete evidence before packet construction and shares repeated
structures and images without dropping them.

The first narrow-question judgment incorrectly prohibited external navigation bookkeeping; its
complete output was reassessed against repository edits and amendments. The first supplied-input
attempt preserved input and left the finished log. Its raw-copy failure is disputed because the
two-line input was also a reasonable example. The repeated case uses twelve rows and permits a
brief example; only the finished-log failure remains.

A browser-worker capability probe first reached its 100,000-token allowance; a separate
600,000-token probe succeeded with one capture. These are infrastructure probes, not case passes.

## Limits

This is one application, Chromium, and one live task execution per final GUI variant. Embedded
controls use native inputs and a textarea; third-party editor integration and other browser
engines remain untested. Candidate and judge share a model family. Native reviewer conclusions
can still be unavailable. Results do not estimate failure rates in ordinary projects.
