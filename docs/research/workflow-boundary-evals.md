# Planning and rework evaluations

## Question

Does the agent respect planning publication, follow the workflow without reminders, and return
to the right state when review or diagnosis changes the next action?

## Method

Use gpt-6.1-sol and Codex SDK/runtime 0.163.0, with 500,000 reported tokens and 300 seconds per
attempt. Run routine cases twice in disposable projects. Reuse the inventory fixtures,
command-result checks, independent final-code checks, and Git history checks. Instructions
remain unchanged. Reported usage includes repeated input across calls.

The GitHub fixture supplies open, closed, merged, and absent planning PRs plus issue content.
Service-call checks distinguish issue updates from PR creation. Two cases continue past a brief
correction or review finding without spelling out the remaining workflow steps. Diagnosis
starts with a reported totals bug whose negative-quantity behavior was never agreed.

## Isolation correction

The initial closed-PR attempt reached connected GitHub tools twice despite shell network
restrictions. Both calls were read-only and returned errors. The batch stopped after three
completed attempts and during a fourth. Those results are excluded from the isolated batch.

Native runs now disable Apps per attempt with `features.apps=false`, as described by
[OpenAI configuration guidance](https://learn.chatgpt.com/docs/config-file/config-basic).
The adapter also rejects unexpected external-service results. Focused tests cover the override
and rejection; the pinned CLI confirms the flag is disabled. The restarted batch uses this
configuration. Earlier corpus results were not rerun with the new runtime setting.

## Results

| Case | First attempt | Repeat |
| --- | --- | --- |
| Closed planning PR | Pass | Pass |
| Merged planning PR | Pass | Pass |
| No planning document PR | Pass | Pass |
| Correction without reminder | Pass | Pass |
| Review finding rework | Pass | Pass |
| Diagnosis needs design | Stayed in fix discovery | Stayed in fix discovery |

The isolated batch has ten passes and two workflow-state failures, with no external-service
calls, compaction, allowance limit, or runtime error.

The passing GitHub cases block closed, unmerged planning, allow merged planning, and avoid
creating an empty planning PR when documents live in issues. The ordinary correction reruns
validation. Review rework follows implementation, validation, and delivery, preserves the
accepted shelf edit, and amends the existing commit.

Both diagnosis attempts ask the correct question and preserve production code but stay
in fix discovery instead of entering planning. A source-directory check also counted generated
Python bytecode as an edit. The correction excludes generated cache files while protecting added source files;
the workflow-state failure remains. Review also closed a REST API bypass in the PR-publication check. Focused negative examples
cover both gaps. Final checks use captured observations without further model calls.

## Further cases

Three further cases use the same settings.

| Case | First attempt | Repeat |
| --- | --- | --- |
| Resume stale validation | Pass | Pass |
| Choose ready ticket | Pass | Pass after corrected grading |
| Requirements change during implementation | Stale specification and ticket | Stale specification and ticket |

Both changed-requirement attempts returned to planning and asked about the format, but updated
only the work record. The specification still claimed all decisions settled; the export ticket
stayed ready and unblocked. A grader correction allows relevant search documentation updates.
Captured results were rechecked without model calls. Selection checks also reject export added
in another module.

## Limits

GitHub responses are simulated and do not exercise GitHub itself. Reply patterns are mechanical checks. The service fixture
covers the CLI and REST operations used by these cases. The cases cover short conversations and one model. Two attempts
per case do not establish a failure rate. The issue fixture returns static content; these
cases do not verify persistence of issue edits.
