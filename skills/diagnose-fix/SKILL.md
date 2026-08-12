---
name: diagnose-fix
description: Use when intended behavior is reported broken, failing, throwing, slow, intermittent, or regressed and the cause is not already proven.
---

# Diagnose Fix

Prove the symptom and cause before changing production behavior, then hand the minimal regression slice to implementation.

## Ownership

Own symptom reproduction, minimization, causal investigation, and the pre-fix regression test. `$implement-work` owns the production fix and completion gates.

## Build a red-capable loop

1. Translate the report into an observable symptom: exact trigger, target, and wrong post-condition.
2. Reproduce it directly. Prefer, in order, a focused automated test, CLI or HTTP harness, browser flow, captured-input replay, or minimal throwaway harness.
3. Make one unattended command fail on the user's exact symptom. Tighten it until it is reasonably fast and deterministic. For an intermittent defect, raise and record the reproduction rate.
4. Minimize inputs and steps one at a time while preserving the same symptom.

Do not substitute a nearby error or implementation proxy. For GUI bugs, the loop must perform the exact triggering action against the exact target element and assert the exact post-action state.

Read [feedback-loops.md](references/feedback-loops.md) when selecting a harness or handling intermittency.

## Prove the cause

1. Generate several falsifiable hypotheses and rank them by evidence.
2. Test one discriminating prediction at a time with debugger inspection, targeted instrumentation, bisection, or differential comparison.
3. Tag temporary instrumentation with a unique searchable prefix.
4. State the causal chain that explains every necessary element of the minimized reproduction.

Share the hypothesis list as a concise progress update when the user's domain knowledge could cheaply change the ranking, while continuing independently unless their judgment is required.

## Establish the regression slice

Choose the highest stable public seam that reproduces the real failure pattern. Write the focused regression test and observe it fail before altering production code. If no honest seam can capture the defect, record that architectural constraint and preserve the red-capable loop as the required proof.

Return control to `$manage-work` with the proven cause, failing command, regression seam, and acceptance checks. It advances automatically to `$implement-work`, whose `$test-first` cycle begins from this existing red state.

## Completion

Complete when the exact symptom is reproducible by one recorded command, the causal explanation is supported by discriminating evidence, a focused regression test is red at a valid seam or the missing seam is documented, and implementation has a bounded fix target.
