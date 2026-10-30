# Verification and repair evaluations

## Question

Does the agent handle failed or unavailable checks and reproduce a reported bug before repair?

## Method

Run each case twice with gpt-6.1-sol and Codex SDK/runtime 0.163.0. Routine attempts allow 350,000
reported tokens and 240 seconds; local completion allows 500,000 and 300 seconds. The instruction digest matches the
[earlier study](workflow-eval-baseline.md). Instructions remain unchanged.

The cases share name-search code and seven prepared checks. The defect makes STRASSE fail to
match Straße because lowercasing does not perform Unicode case folding. One case starts in
validation; another starts in bug discovery with the failing input. Both stop before delivery.
The unavailable-verification case has correct code but lacks a required release verifier.

## Results

The initial six captured attempts pass the final checks. Reported tokens include repeated input across
calls and do not measure current context size.

| Case | First attempt | Repeat | Reported tokens, first / repeat |
| --- | --- | --- | --- |
| Failed verification | Pass | Pass | 178,208 / 174,703 |
| Unavailable verification | Pass | Pass | 169,148 / 169,554 |
| Reproducible bug | Pass | Pass | 186,699 / 200,091 |
| Write a regression test | Pass after corrected grading | Pass after corrected grading | 172,266 / 151,685 |
| Rerun after correction | Pass | Pass | 332,096 / 326,718 |
| Complete local work | Pass | Pass | 281,270 / 320,429 |

All four repair attempts observed the Unicode assertion fail, repaired the code, passed all
seven unchanged checks, saved findings, and remained in validation. Both bug-discovery attempts
recorded the cause before implementation. Both unavailable-verification attempts ran the local
checks and unavailable verifier, recorded the missing evidence, and refused completion on a
follow-up question. No runtime error, allowance limit, or compaction occurred.

The original graders rejected two valid ticket-status updates and one valid refusal to call
work complete. Corrected checks allow status updates while preserving ticket requirements and
check the refusal separately from missing-tool wording. Rechecking used captured observations
and project files without further model calls. Offline regressions cover these corrections.

## Further cases

Regression-test writing starts with the search defect and no test. The grader runs the authored
unittest suite against repaired and initial code, requiring success and assertion failure
respectively. Its initial isolated interpreter removed project imports. The correction uses
normal project imports and has a focused regression check. Captured observations are rechecked
without further model calls.

The correction case runs validation, changes the accepted message, and requires fresh evidence
for the new message. Local completion checks code, documentation, the work record, a clean
commit, and cleared workflow state. Native review activity is inspected separately.
Review added a missing execution requirement, verified against both captures.
One completion run used independent review; the repeat reported a reviewer tool error and used
the documented self-review fallback. None of the added attempts compacted context.

## Shared checks and limits

Command sequences now check exit codes and optional output in execution order. A prepared
Python check runs its saved starting script against current project code, so changing the
visible test cannot hide a broken repair. Cases also preserve the visible prepared checks.

A shell command's exit code covers the whole command. It does not establish every individual
command's result. The cases pair recorded output with independent final behavior checks.
The new cases also cover authored regression tests, checking corrections, and local delivery.
They do not test finding an unknown reproduction or delivery through GitHub. Two attempts per
case do not establish a failure rate. Earlier behavior failures remain unchanged.
