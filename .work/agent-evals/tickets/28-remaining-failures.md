# 28 Resolve remaining workflow failures

**Status:** complete

## Accepted outcome

Repair confirmed bugs that contradict accepted requirements. Keep reviews read-only and correction
reviews bounded. Derive consequences of accepted planning decisions without asking for redundant
approval, preserve planning context in factual replies, and continue unresolved discussion unless
postponed. Explain task decisions without using agent instructions as justification.

## Applied changes

- Review guidance requires fixing confirmed contradictions, including bugs outside the current
  change. Unslop makes obligations explicit through direct instructions or “must.” The
  [review study](../../../docs/research/remaining-failure-trials.md) preserves all 44 assessments,
  earlier failures, grading corrections and all fifteen final selected-criterion passes.
- Unslop also excludes instruction-based justifications while preserving requested instruction
  discussion. The [writing study](../../../docs/research/instruction-justification-trials.md)
  records fourteen candidates and fourteen joint judgments. All three main trials meet the new
  writing criterion; original full-case grades and later accepted interpretations remain visible.
- The exact approved [planning](../../../docs/research/planning-derived-answers-proposal.diff) and
  [wayfinding](../../../docs/research/wayfinding-open-decisions-proposal.diff) diffs are applied.
  Their [baseline](../../../docs/research/settled-planning-followup.md),
  [factual-answer](../../../docs/research/wayfinding-factual-reply-trials.md),
  [continuation](../../../docs/research/planning-continuation-trials.md) and
  [open-decision](../../../docs/research/open-decisions-trials.md) studies preserve the full history.

## Eval corrections

The deletion-repair check permits accurate search documentation while preserving the specification
and behavior checks. Its red/green regression accepts the valid saved repair and rejects six
unrepaired outputs. The quantity-label fixture no longer includes an unrelated search check;
its retained regression failed before correction and passes afterward.

The compaction case now assesses continuation after answers before compaction as well as recovery.
Its ambiguous “Leave the existing-file decision open” sentence is removed as approved. The
revised request has no new candidate runs. Old missing-question grades remain disputed, and the
old rejected-helper bypass is not treated as proof of a separate failure under the revised request.

The search fixture permits consistent accent-insensitive matching for scanned and typed queries
while preserving stored names. Approval is not required merely because this detail was unspecified.
The [corrected private criteria/checks](../../../docs/research/search-judgment-correction.diff)
accept implementation or honest clarification. The [correction report](../../../docs/research/search-judgment-correction.md)
records a nine-variant red/green regression and thirteen successful saved-output contract rechecks.
Original grading remains historical; these rechecks are not new model trials or assessments.

The booking answers sufficiently explain that an expired, unconfirmed hold gives no confirmed
booking or entry permission. Their failure grades for omitting a separate “released” statement
are rejected as overstrict. Both original grades and the accepted interpretation remain recorded.

## Validation and evidence

All 551 framework tests pass. Ruff lint and formatting, mypy across 95 source files, all 160 case
definitions, patch-identity checks and changed local links pass. The latest search regression
accepts two implementations and unchanged clarification while rejecting six behavioral regressions.
It also exposed and repaired an inherited quantity-check coincidence.

All 131 candidate assessments and 80 additional continuation/writing joint judgments completed.
Complete outputs, relevant actions, available child findings, source bytes/digests, definitions
and isolation were inspected. Individual accepted guide edits match their tested files. The final
combined instruction version and revised compaction request have not received new candidate trials.
Same-family judging remains a limitation. No full-corpus rerun or global deployment is claimed.

Raw evidence was inspected, independently reviewed and deleted before committing. Concise
findings and reusable checks remain; trial captures never entered Git.

## Delivery

Separate fresh-context whole-task intent and engineering reviews pass with no findings or
unresolved judgment. Both inspected the complete changes and retained trial evidence without
rerunning validation. Changes are committed by independent result; no accepted work remains.
History was not squashed.

Resume: `python3 -B /home/whitney-white/.codex/skills/work-system/scripts/navigate.py resume --conversation 01a1a41a-eb6b-7c70-bc4d-5db4fb112d7e`.
