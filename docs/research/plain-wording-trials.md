# Plain testing and validation wording trials

The [proposal](plain-wording-proposal.diff) replaces three passages in testing, implementation
and GUI validation. It was tested in an isolated instruction copy, then extended in the follow-up.
The baseline copy matches repository `e7ce24b`, before these wording changes.

## Outcomes

C/F mean correct and incorrect, in attempt order. Arrows retain the original judge verdict
followed by inspected conclusions. All 28 candidate assessments completed. No attempts were
excluded, and no cases were added.

| Existing task | Fresh baseline | Proposed wording | Failed criteria and observations |
| --- | --- | --- | --- |
| refactor-brittle-internal-test | C | C/C/C | None. Each refactor removes duplicate calls and retains required CSV-output checks. |
| mocked-project-connection | C | C/C/C | None. Real-file regressions fail the storage bug and pass the repair. |
| independent-test-expectation | C | C/C/C | None. Expected totals are independent of production. |
| test-real-project-behavior | C | C/C/C | None. Replaced mocks execute the real function. |
| interactive-prototype-comparison | F | F/F/C | Baseline direct-operation omits editing/save/recovery. Trial 1 acceptance overrides its unanswered production-storage question; trial 2 direct-operation omits narrow Blue mug and wide Field kit inspections. |
| new-interface-design | C | C/C/C → C/F/C | Trial 2 rendered-inspection-and-critique reads headers and checkout fragments, omitting return and other required structural content. |
| gui-accepted-design | C | C/C/C | None. Both app and accepted prototype are opened and their images viewed. |

The proposed refactors run the original passing tests, remove duplicate calls and mocked call
counts, and retain CSV-contract tests. The nine testing controls retain failing regressions
before repair and passing tests afterward. Testing baselines also pass, so these attempts do
not show improved reliability.

The original prototype baseline judgment additionally demands rejection reasons that were never
supplied. Read-only diagnosis confirms this grading error and the separate verification omission.
No requirements or criteria changed. Original judgments remain represented here.

Independent investigation confirms design C/F/C. These four design candidates load only planning,
interface-design and prototype guidance. None reads any of the three modified passages, so the
observed design failure cannot establish an effect of the proposal.

## Comparison and checks

Seven joint comparisons reuse all 28 candidates under shuffled labels. They retain the design
false pass and correct the invented prototype-reason failures. Independent testing-intent,
UI-intent and engineering reviews pass. All 151 definitions, proposal applicability and 197
local links and anchors pass. No skill, eval, test or runner source changed.

Candidate and separate blinded judge use gpt-6.1-sol, 1800/1200-second allowances and disabled
token guards. Requests, resolved fixtures, private criteria, framework and model settings remain
fixed. Installed instruction digests distinguish verified copies including external unslop.
These reconstructed tasks and same-family judges limit generalization. The full corpus was not
rerun; compaction remains deferred. Raw evidence was inspected and independently reviewed outside the checkout, then deleted.

## Follow-up trials

Seven new baselines and three wording versions add 64 candidates. The first follow-up keeps
the three replacements and adds prototype checks for whole tasks and content variation across
sizes. The second names cancellation; the final replaces "including their error cases" with
"including correcting errors and trying again". The
[complete tested diff](plain-wording-followup-proposal.diff) is applied unchanged.

| Existing task | New baseline | First follow-up | Cancellation named | Correct and retry | Failed criteria and observations |
| --- | --- | --- | --- | --- | --- |
| refactor-brittle-internal-test | C | C/C/C | C/C/C | C/C/C | None. Original baseline observed; duplicate calls and mocked counts removed; CSV contract retained. |
| mocked-project-connection | C | C/C/C | C/C/C | C/C/C | None. Real storage regressions fail before repair and pass afterward. |
| independent-test-expectation | C | C/C/C | C/C/C | C/C/C | None. Expected totals are independent of production. |
| test-real-project-behavior | C | C/C/C | C/C/C | C/C/C | None. Retained tests execute the real function. |
| interactive-prototype-comparison | F | C | C/C/F | C/C/C | Baseline direct-operation omits editing/save/recovery. Cancellation-named attempt 3 cancels immediately after feedback and never verifies post-error editability. |
| new-interface-design | F | C → F | C/C/C | C/C/C | Baseline runnable-choice omits unfinished equipment cancellation. First follow-up runnable-choice and rendered-inspection-and-critique omit volunteer cancellation and its different destination. |
| gui-accepted-design | C | C | C/C/C | C/C/C | None. App and prototype opened, images inspected. |

All candidate assessments completed. The first joint round reuses 43 candidates; the final
round reuses 28. All 71 reassessments completed. Independent testing-intent, UI-intent and
engineering reviews pass. All 151 definitions, 202 local links/anchors, skill validity and
applied-proposal identity pass.
The first design judge and read-only diagnosis miss the volunteer-cancellation omission;
independent investigation confirms it. Joint design judging also falsely passes that attempt
and its baseline. All three cancellation-named designs pass independent investigation, with
small search/change-event additions incompletely exercised. Independent prototype investigation
confirms C/C/F. These trials do not isolate each sentence's effect. Requests, fixtures, criteria
and settings remain fixed. Follow-up raw evidence was inspected and reviewed outside the
checkout, then deleted.

Application matches the final tested instruction digest, including external unslop. All 151
definitions and skill validity pass. No new candidate trials were run for application.
