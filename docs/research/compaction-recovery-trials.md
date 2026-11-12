# Compaction recovery trials

## Method

Candidates and separate blinded judges use gpt-6.1-sol, SDK/runtime 0.163.0, 1800/1200-second
allowances and disabled token guards. Requests and model settings stay fixed. Grading repairs start
fresh comparisons; code-only repairs recheck retained outputs. Baselines use frozen original
instructions. Trials use isolated source copies and homes. Compaction requires the native completed
item and matching completed turn. The 154-case corpus is not rerun. Same-family judging limits
generalization.

## Behavior

C/F/U mean correct, incorrect and unknown against selected criteria. Assessment completion is
separate.

| Stage | [Agent-created planning](../../evals/cases/agent-created-state-compaction.json) | [Supplied planning](../../evals/cases/explicit-compaction.json) | [Pending review](../../evals/cases/pending-evidence-through-compaction.json) | [Requested summary](../../evals/cases/wayfinding-counts.json) |
| --- | --- | --- | --- | --- |
| Original baseline | F* | F | C | Not run |
| Early manual probes | Not run | C/F | Not run | Not run |
| V1 | F* | F | C | Not run |
| V2 | F*/F*/F* | C/F*/C | C/C/C | Not run |
| Summary comparison, baseline; V2 | Not run | Not run | Not run | C/C/C; C/C/C |
| Record-link baseline | F | Not run | Not run | Not run |
| V3 | F*/C/F | C/C/C | C/C/C | C/C/C |
| V4 | C/F*/F | Not run | Not run | Not run |
| V5 | C*/C/F* | C/C/F* | C/C/C | C/C/C |
| Grouping comparison, baseline; V5 | F; C/C/C | Not run | Not run | Not run |
| Decision-question baseline | Not run | F | Not run | Not run |
| V6 | F*/C/C | C/C/C | C/C/C | C/C/C |
| Continuation baseline | F | Not run | Not run | Not run |
| V7 | C/C/C | C/C/C | C/C/C | C/C/C |

Early supplied-planning failures omit the first decision question. V2 limits summaries to requested
summaries. The first five starred F planning outputs update the original index but leave
navigation's record field empty. Their original passing assessments are unsupported. A new private
check requires the existing record link; regressions reject missing and wrong links.

V3 clarifies the record-binding command. Its third attempt creates a second index after searching
without hidden files. V4 adds hidden-file search and reuse. Its third attempt omits alternatives and
the feature-ticket link. A filename-only check wrongly rejects its valid decision map. The repaired
check accepts other names and rejects empty records; private criteria check their roles.

V5 clarifies links and option consequences. Its starred C retains a rejected judgment solely about
grouping independent choices, which accepted guidance permits. The clarified criterion passes five
independently authored calibration examples and three fresh candidates. Inspection also finds
missing pending questions in earlier summaries. Starred F entries retain their original favorable
assessments. V6 makes the question requirement explicit; its first agent-created attempt still
describes the choice without asking. V7 explicitly resumes the unresolved question after compaction.
The repaired criterion rejects that frozen failure and accepts the two complete replies.

The [failure report](evaluation-failures.md) retains the earlier duplicate-index failure. V7
agent-created attempts 2 and 3 omit the next question before compaction, despite the reply command
rejecting its absence. Both ask it after recovery. This ungraded continuation finding limits broader
wayfinding claims.

## Native recovery and limits

CLI, process and session-flag probes fail to enable hooks through this app-server. The per-thread
`config.bypass_hook_trust` setting works after inventorying the isolated subject hook. Judges keep
hooks disabled. A native probe records the compact hook before the next response. Early manual
probes do not prove hook execution.

Hook context is separate from commands. A capture-order repair drains completed hooks before model
actions; runtime timestamps retain execution order. A damaged-state probe preserves the invalid file
and stops without another model request. Local checks cover both applications' generated
configuration, identity, record restoration, preservation and repeated setup.

Explicit compaction is tested. Automatic thresholds, clearing and native Claude remain untested;
Claude Code is unavailable locally.

## Verification

All 81 primary assessments, five calibration judgments, three frozen-output audits and 62 comparison
judgments completed. Eighteen final comparison judgments agree. All 510 framework tests and 83
affected checks pass after correcting the package inventory. Quality checks pass. Both independent
reviews pass. The [tested diff](compaction-recovery-proposal.diff) is applied unchanged. Raw
evidence was deleted after review.

## Sources

[Codex hooks](https://learn.chatgpt.com/docs/hooks#sessionstart),
[Claude hooks](https://code.claude.com/docs/en/hooks#sessionstart),
[Claude identity](https://code.claude.com/docs/en/env-vars).
