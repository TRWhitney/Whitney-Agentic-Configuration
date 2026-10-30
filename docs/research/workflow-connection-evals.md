# Connections and continued work

Four new cases and two extensions bring the corpus to 134 cases. Requests supply ordinary
product work; private criteria assess the engineering and workflow choices. Subject skills and
configuration are unchanged. These are reconstructed tasks, not conversation replays.

## Coverage

| Case | Existing coverage | Added condition |
| --- | --- | --- |
| [mocked-project-connection](../../evals/cases/mocked-project-connection.json) | `test-real-project-behavior` targets a mocked function under test; `regression-through-public-command` targets a broken command connection. | Real service runs, but mocked project storage conceals disagreement between saved and returned records. Retained tests must expose that disagreement. Replacing filesystem access is allowed. |
| [gui-shared-change-other-view](../../evals/cases/gui-shared-change-other-view.json) | `gui-accepted-design` checks two dialogs in one workspace. | Requested workspace geometry already matches, while its shared stylesheet changes an existing archive page. Both views need comparison; preferences must still persist between them. |
| [documentation-examples-run](../../evals/cases/documentation-examples-run.json) | `complete-local-workflow` updates a simple guide; `implementation-conflicts-with-documentation` catches a wrong behavior promise. | Program tests pass while both guide examples use a removed option. Completion requires usable examples against the finished command. |
| [feature-request-needs-planning](../../evals/cases/feature-request-needs-planning.json) | `incomplete-design` supplies planning state and open questions. | Ordinary sharing request supplies no workflow, design, tickets, or decision list. Agent must recognize missing product decisions before changing production. |
| [agent-created-state-compaction](../../evals/cases/agent-created-state-compaction.json) | Requires agent-created planning records and explicitly compacts. | Accepted empty-export answer changes after importer evidence. Restore the latest answer and the unfinished existing-file choice without restarting settled work. |
| [followup-keeps-process-out-of-prose](../../evals/cases/followup-keeps-process-out-of-prose.json) | Already tests leakage and retained facts during guide revisions. | Access-source discussion intervenes before another revision. Keep useful route facts and omit narration of research and author directions. |

## Grader checks

The storage check rejects the original saved-record shape and accepts the repair. Existing
mocked tests cannot establish the regression; a real round-trip test can. The export program's
private check passes initially, while both supplied guide commands fail. Updating their option
makes both commands execute successfully.

The shared browser check rejects only archive geometry in the unfinished fixture. Both the
requested workspace and notebook behavior pass. A scoped repair passes, including a different
internal scope name. A global rollback that restores the archive but loses the requested
workspace width fails. Useful documentation clarifications remain allowed; accepted contracts
are assessed by meaning. Browser checks compare both views at desktop and narrow widths and confirm
that an archive preference survives returning to the workspace. Candidate verification is
assessed separately from private browser observations.

## Outcomes

Candidates and separate blinded judges used `gpt-6.1-sol`. All six candidate conversations and
all six assessments completed without reaching a time or token guard. After inspection and
grading corrections, **five behaviors are correct and one is incorrect**.

| Case | Agent behavior | Finding |
| --- | --- | --- |
| `mocked-project-connection` | Correct | Replaced mocked project calls with real-file round-trip tests. Observed quantity assertions fail before the repair and pass afterward. Positive, zero and empty inventories pass. |
| `gui-shared-change-other-view` | Correct | Scoped the shared style, compared both views with their designs at desktop and narrow sizes, inspected captures, and verified preferences through switching and reloads. Private geometry and notebook checks pass. |
| `documentation-examples-run` | Correct | Both guide examples use `--output` and execute successfully. Kept the removed option rejected and verification reports outside the operator guide. |
| `feature-request-needs-planning` | Correct | Chose planning, discussed interface and offline conflict choices, recorded proposals as unaccepted, and left production unchanged. |
| `agent-created-state-compaction` | Incorrect | `criterion-2`: never recreated the linked decision map and feature record. Recovery itself passed: after actual compaction, resumed wayfinding, read saved work, retained the revised header-only answer, and asked about the remaining destination choice. |
| `followup-keeps-process-out-of-prose` | Correct | All three guide versions retain accepted route facts without process narration. The intervening comparison left the guide unchanged; final arrival advice adds the step-free route without narrating the source check. |

The prose run initially failed a code check comparing its revised guide with the starting draft.
That comparison was invalid after earlier accepted revisions. The corrected check passes on the
frozen output; adjacent snapshots also confirm no guide edit during the factual question. The
rubric and judge verdicts did not change. This false failure is excluded from behavior totals.

406 framework tests pass, along with lint, formatting, strict typing across 64 files, JavaScript
syntax, Markdown link checks, and all 134 case definitions. Framework tests are separate from the
six agent evaluations. The strengthened GUI grader also passes on the frozen candidate output;
no candidate or model assessment rerun was needed for the grading corrections. Independent
intent and engineering correction reviews pass. Raw evidence was removed after inspection and
review.

Each case has one live attempt. These results establish the observed behavior in these tasks,
not its frequency in longer production sessions. Candidate and judge use the same model family.
Native child-review findings remain unavailable; these cases do not claim to evaluate those
reviews. The prose case adds one substantive source discussion, not a lengthy implementation
session. The compaction case tests explicit compaction rather than context exhaustion.
