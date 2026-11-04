# Test quality trials

All 12 revised attempts passed the unchanged criteria. The [proposed diff](test-quality-proposal.diff)
routes refactoring to testing and places its detailed instructions there. Skill sources remain
unchanged pending review.

## Outcomes

C means correct, F incorrect. Entries identify every attempt in execution order. All 33 candidate assessments completed, including 16 new attempts. None are excluded.

| Case | Earlier baseline | Implementation screen | Implementation repeats | Fresh baseline | Procedure repeats |
| --- | --- | --- | --- | --- | --- |
| refactor-brittle-internal-test | F | C | C, C, C | F | C, C, C |
| mocked-project-connection | C | Not run | C, C, C | C | C, C, C |
| independent-test-expectation | C | Not run | C, C, C | C | C, C, C |
| test-real-project-behavior | C | Not run | C, C, C | C | C, C, C |

Both refactor baselines shared the writer and preserved output but retained mocked helper
calls, exact counts and redundant production calls. Neither ran tests before production edits.
Temporary output comparisons did not replace retained coverage. Behavioral-tests and
refactor-evidence failed. Child reviewers missed these failures; separate judges and parent
inspection identified them.

The earlier implementation paragraph corrected both failures in the screen and all three
repeats. Candidates ran original tests, replaced incidental call-count assertions with retained
public-output tests, passed them before and after refactoring, and removed redundant calls.
The screen also made 40 temporary comparisons. All nine related repeats retained meaningful
regressions, observed expected assertion failures before repair, and passed afterward.

The earlier placement was not adopted. The new trial keeps the same three sentences in testing,
adds refactoring to the implementation instruction and expands the tweak testing trigger.
Fix and novel-work implementation already require testing. Neither case expectations nor the
behavior-changing regression requirement changed.

All three revised refactors loaded testing, established the original passing baseline and
retained public-output tests passing before and after production edits. Attempt 2 still called
`_row` twice per item after removing its mocked assertions. All frozen criteria passed, but
redundant-call removal was inconsistent. All nine related repeats preserved failing regressions
before repair and passing retained tests afterward.

## Method and limits

Candidate and separate blinded judge used gpt-6.1-sol, with 1800/1200-second allowances and disabled
token guards. Requests, resolved fixtures, private criteria and settings stayed fixed. Each case's
complete outputs were reassessed together under shuffled labels. Both rounds
of joint assessments completed and agreed with the original judgments.

Separate disposable projects and homes loaded repository instruction copies with the declared
unslop dependency. All four cases are existing tasks; bug-fix cases provide related comparisons,
not additional refactor coverage. Inspection covered complete replies, retained tests and source,
relevant actions, test results and available child findings. No eval definitions changed.

Earlier comparison preparation failed three times before judging because a temporary
`inspect.py` helper shadowed Python's module. Renaming it allowed unchanged outputs and criteria
to be reassessed; no candidate was rerun or excluded.

Earlier raw evidence was deleted after independent intent and engineering reviews passed.
Independent intent and engineering reviews of the revised study also passed with no findings.
Current raw evidence was inspected and reviewed, then deleted before delivery. All 151
definitions and changed links pass. The earlier
466 framework and quality checks remain applicable because framework source is unchanged.
These small reconstructed tasks and same-family judges do not establish a production failure
rate or a full-corpus result. Native compaction remains deferred.

[Earlier failure](procedure-decision-evals.md#outcomes).
