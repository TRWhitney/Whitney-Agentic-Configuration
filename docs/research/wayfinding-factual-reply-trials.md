# Factual replies and native recovery

This intermediate trial of the factual-answer clarification still drops a required
prefix once and reopens a settled calculation once. Native recovery succeeds, but earlier replies
in two native attempts omit the next question.

## Method

The source includes approved review and unslop additions. Baselines use the old wayfinding text;
[the trial](wayfinding-factual-reply-proposal.diff) adds only “including factual answers”. Tasks,
private rubrics and gpt-6.1-sol candidate/separate blinded judge settings stay fixed within the
comparison. Allowances are 1800/1200 seconds with disabled token guards. Same-family judging
remains a limitation.

The [quantity fixture correction](quantity-label-fixture-proposal.diff) is applied first. Its
regression fails on the inherited search check before correction and passes afterward. The
corrected quantity case and requested-recap control receive fresh baselines; the two native
cases run actual compaction before the wording trial.

## Outcomes

C/I mean correct/incorrect against the selected criteria. All 22 new assessments completed:
four baselines and eighteen trial attempts. No unknown outcomes occur.

| Case | Baseline | Factual-answer trial |
| --- | --- | --- |
| choose-reversible-implementation-detail | C, corrected input | C/C/C |
| wayfinding-counts | C | C/C/C |
| agent-created-state-compaction | C* | C*/C*/C |
| explicit-compaction | C | C/C/C |
| wayfinding-code-question | I/I/I, preceding study | C/I/C |
| wayfinding-derives-settled-choices | C/C/C, preceding study | C/C/I |

The factual-answer failure calls the reply helper with an empty question, receives exit 2,
and sends an answer without the planning prefix instead of correcting the reply. Criterion-3
and the second-turn prefix check fail. The export decision stays open.

Capacity attempt 3 calculates peak occupancy correctly but records the rule as awaiting
agreement and asks for approval, postponing the actual staff choice. Derive-availability,
reserve-material-choice and consistent-planning-state fail. This is a genuine recurrence,
separate from the earlier incorrect label-based judgments.

*Recovery criteria pass, but continuation is incomplete before compaction. The native baseline
omits the next question after its first answer. Trial 1 omits it after both answer/revision;
trial 2 omits it after the first answer. These three trial omissions are real and ungraded.
All six trial compactions and recovery hooks complete, restore the original record, retain the
latest decision and ask the pending question afterward. Recovery passes do not establish a
complete discussion loop.

## Proposed next correction

Show [planning wording](planning-derived-answers-proposal.diff),
[same-reply wording](wayfinding-same-reply-proposal.diff), and
[feedback coverage](compaction-feedback-coverage-proposal.diff) before further trials. They are
unapplied at this stage. The added private criterion covers existing required behavior without changing requests;
its changed coverage needs a fresh comparison.

Complete outputs, relevant actions/records and available child findings were inspected, with
independent inspection. Sources, definitions and recorded isolation match all 22 new attempts.
Native completion/hook receipts are verified. Seventy-five framework tests, quality checks and
160 definitions pass. Raw evidence was reviewed and deleted. No full-corpus
or global-deployment claim is made.
