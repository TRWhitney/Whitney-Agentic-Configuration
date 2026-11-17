# Trustworthy performance investigation and measurement

## Problem Statement

Performance work needs concrete instructions for measuring complete, correct operations and
judging comparisons. Generic investigation and acceptance guidance does not specify that method.

## Solution

Add the approved standalone performance procedure. Offer it through triggered navigator access
in discovery, implementation, and validation, including delegated implementation. Keep its body
out of state output until loaded. Other states and research retain their existing instructions.

## User Stories

1. As an agent investigating or implementing performance work, I need a reliable measurement
   method before choosing or evaluating changes.
2. As an agent validating completed work, I need to distinguish demonstrated improvements,
   unmet requirements, and inconclusive comparisons.

## Implementation Decisions

Apply the approved procedure and single-run reporting clarification, including explained A/B
alternation, statistical handling of close results, arithmetic checks, intermediate optimization
choices, explicit inconclusive conditions, and baseline/result/difference reporting.
Use the existing procedure registration mechanism and preserve workflow ownership of changes.
Performance content is not embedded in research or general state guidance.

## Testing Decisions

Check authorized discovery, implementation, and validation access, deferred body loading, and
rejection in other states. Use realistic behavioral cases for investigation, implementation,
validation, and limited estimates or unrelated work. Inspect actual operations, results, and
assessment evidence. Independently authored calibration covers legitimate alternatives,
misleading measurements, and missing observations. Run repeated task attempts with frozen
criteria and retain concise findings plus reusable checks.

## Out of Scope

New workflow states, research rewrites, installed-skill deployment, and publication.

## Further Notes

Source adaptation: pstack benchmark-checklist and perf-issue at revision
74bcc61bd216687b1d6d480c28f109adfc9824ec.
