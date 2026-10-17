# Diagnose Procedure

Reproduce the bug, check the intended behavior, and identify the cause before changing code.

## Reproduce the symptom

Reproduce the reported symptom through the same action, interface, data, and relevant
environment described to you. Record the expected and actual behavior and the conditions that
distinguish them. Do not substitute a nearby failure, code inspection, or a check of an internal
helper for direct evidence.

For a GUI symptom, exercise the exact triggering action and target element, observe the exact
post-action state, and capture visual evidence when the symptom is visual. DOM evidence may
support the reproduction but cannot replace visual inspection.

If the symptom does not reproduce, vary supported environmental and state conditions and broaden
search terms before concluding it is absent. Report the unresolved reproduction instead of
inventing a cause.

## Find the cause and choose a regression check

Use repository history, existing tests, logs, traces, and read-only inspection to isolate the
smallest conditions that produce the symptom. Trace those conditions to the first incorrect
state, value, transition, or broken requirement shown by those findings. Distinguish confirmed
facts from remaining hypotheses.

Identify the behavior and conditions a focused regression test must cover to fail before the fix
and pass afterward. Also state how to repeat the reported action and check that it works.

Do not change production or test code, select a speculative solution, or add regression coverage
during diagnosis.

## Result

Include the reproduction steps and evidence, intended behavior and its source, supported cause,
remaining uncertainty, proposed regression test, and direct acceptance check. If diagnosis is
incomplete, include the missing evidence and the next bounded investigation.
