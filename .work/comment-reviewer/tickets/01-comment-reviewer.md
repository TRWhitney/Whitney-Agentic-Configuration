# 01 Add a dedicated comment reviewer

**What to build:** Add the comment axis and its dedicated instructions to complete review.

**Blocked by:** none

**Status:** complete

- [x] Complete review assigns a separate comment reviewer even without a comment edit.
- [x] The reviewer applies the approved removal rules, exceptions, and reporting.
- [x] Behavioral evals cover dispatch, useful findings, and read-only review.

[Specification](../spec.md)

## Verification

The documentation-only case passed. A separate comment reviewer reported no findings
and the parent completed delivery. The receipt case was initially inconclusive because the
comment reviewer's report was missing from the recording. The rerun passed with the same
rubric and complete child actions. The reviewer found four removals, named the suppressed
type mismatch, kept the verified gateway constraint, and quoted the unverified firmware
claim for follow-up. The parent honored the request to hold edits.

The 87 focused tests and all 190 eval definitions passed. Lint, formatting, typing,
whitespace, and skill structure checks passed.

```sh
uv run --group eval python -m evals run \
  --model gpt-6.1-sol --judge-model gpt-6.1-sol --tag comment-reviewer \
  --repeat 1 --timeout 900 --judge-timeout 700
```

Independent intent, engineering, and comment reviews passed.
