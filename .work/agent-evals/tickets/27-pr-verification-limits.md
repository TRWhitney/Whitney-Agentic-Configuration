# 27 Keep verification limits in PR descriptions

**Status:** complete

## Accepted outcome

Keep completed checks, pending checks and unavailable results clear in the actual PR.
All five source versions were reviewed. The final wording includes “in chat or elsewhere”,
explicit results/requirements, and updating the description before sending the PR link.

## Outcome

The [fifth approved diff](../../../docs/research/pr-verification-limits-fifth-proposal.diff) is
applied exactly as tested. [Study](../../../docs/research/pr-verification-limits-trials.md)
records all 32 PR attempts, assessments, exclusions, corrected judgments and limitations.
Final task/control outcomes are C/C/C each. All 35 candidate assessments completed, including
three earlier correct rename attempts for the accepted criterion correction.

Sources and recorded isolation match all 35 attempts. All 25 calibration labels agree. Installed
final wording is returned in all six candidate action records. Actual hosted-result unknowns
are acceptable paraphrases; no fixed phrase or gratuitous edit is required when the body is
already accurate. Requirements-only caveats and generic local-test disclaimers are different.

## Completion

Eleven focused framework tests, Ruff lint/format, strict mypy and 160 definitions pass.
Changed documentation links resolve. Independent intent and engineering review pass with no
findings. No full-corpus rerun, global deployment or live GitHub work occurred.

The study preserves earlier failures, corrected judgments and excluded attempts. Raw trial
captures were deleted after inspection and required review. The approved rename criterion
correction and PR guidance are separate completed results and are committed separately.
