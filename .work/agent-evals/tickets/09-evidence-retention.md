# 09 Assess evidence retention

**What to build:** Cases that expose lost findings, premature evidence deletion, raw outputs in
Git, and cleanup that removes useful source material.

**Blocked by:** None.

**Status:** complete

- [x] Share outside-checkout evidence setup, observation, and private retention checks.
- [x] Add results, pending-review, diagnosis, explicit-retention, and short-compaction cases.
- [x] Extend the existing cleanup and accepted-prototype cases without duplicating them.
- [x] Reject raw evidence in staged files and new commits, including renamed and amended-away copies.
- [x] Test checks against correct work and plausible failures; run and inspect all seven cases.
- [x] Retain each live outcome, failed criterion, disagreement, and limit before removing raw outputs.

## Accepted sources

[Retention specification](../spec.md#evidence-retention).
[Authoring standards](../../../docs/eval-authoring.md).

## Completion evidence

All 349 infrastructure tests pass, with lint, typing, formatting, and 121 valid case definitions.
The retention checks initially rejected the missing API and case definitions, then passed.
Observed regression coverage includes ignored and archived copies, staging, amended-away
commits, preserved conclusions, actual review-service capture access, and the complete nightly
error reproduction. [Live outcomes](../../../docs/research/evidence-retention-evals.md)
retain every primary case, excluded fixture attempt, disputed judgment, and assessment limit.
Independent intent and engineering reviews pass after bounded correction reviews. The shared
check retains signatures for added and replaced evidence without changing the original baseline.
