# Validation State

Check the completed work against the agreed requirements and look for regressions. Select and
run checks, inspect their results, and record conclusions here. Return to earlier states to
change requirements, production code, or tests.

## Define the evidence

Review all changes made for the task, its requirements and acceptance checks, implementation
test results, reported symptoms, and agreed documents or prototypes.

Confirm that the checks cover the accepted outcome and can be proven against the implementation.
Do not invent criteria or reinterpret a check to fit the result. Route incomplete,
contradictory, or infeasible intent to the earliest available state that can resolve it.

Choose a command or interaction that directly tests each requirement. Generate captures in
temporary directories outside the checkout. Delete them after inspection and required review, or
after any diagnosis or retry that still needs them. Use configured repository commands. Choose
checks for the changed code, its dependencies, and risk:

- formatting with no drift;
- every configured linter with no findings;
- every configured type checker passing;
- no `Any` unless no sensible typed alternative exists;
- focused tests and affected regression suites;
- broader regression, build, packaging, or integration checks required by the change;
- direct execution of the accepted behavior.

Use implementation test results to choose checks. Checking an internal detail, mock, or similar
behavior does not prove that the requested behavior works.

## Run and inspect

Run the selected checks against the completed work. Every check must pass. Treat failing or
flaky tests as implementation failures, including unrelated or pre-existing failures. Record
missing proof and its impact when a check cannot run; unavailable evidence is not a pass.

For a reported symptom, repeat the same action through the same interface with the relevant data
and environment, and observe the expected result directly.

For GUI changes, use the rendered interface. Perform the exact triggering action on the exact
target and observe the resulting interface state. Capture and inspect screenshots of each
relevant visual state. Also inspect the available DOM, accessibility tree, or component
hierarchy for identity, state, semantics, and layout relationships. Structural and visual
inspection are both required. Automated assertions, unattended scripts, and generated files do
not replace direct operation and inspection.

Exercise themes, display sizes, intermediate states, and data conditions that can affect the
change. Inspect alignment, hierarchy, contrast, wrapping, overflow, clipping, gaps, and style
leakage. When an accepted prototype exists, replay its recorded flows and compare the result
with the prototype and its agreed requirements.

## Handle failures

- Keep incorrectly selected, invoked, observed, or recorded checks in validation.
- Return incorrect or missing behavior, inadequate or failing tests, flaky tests, and defects in
  repository validation tooling to implementation.
- Route missing acceptance criteria, contradictory sources, or unresolved requirements to the
  earliest available state that can resolve them.

Use the displayed route before changing production code, tests, or tools. Reuse check results
only when the correction cannot affect them.

## Record current evidence

Record exact commands, concise outcomes, failures, limitations, inspected flows, and visual
observations in the existing record. Keep reusable checks. Give reviewers temporary evidence
paths when needed; saved conclusions must make sense after captures are deleted. Delete raw
outputs after inspection and required review, before delivery, unless I explicitly requested
retention. This includes screenshots, logs, traces, and per-run JSON. Ignoring them does not
satisfy cleanup. Avoid capturing secrets and redact sensitive values from evidence shared for
inspection or review.

When behavior, tests, tooling, dependencies, or the environment change, invalidate affected
evidence and rerun the affected checks and their dependent checks.

## Continue

Continue to delivery when every acceptance check passes against the finished change, selected
quality and regression checks pass, and required reproduction and interface inspection are done.
No implementation defect, missing proof, or unresolved product or architecture decision may
remain.

Remain in validation while its evidence process is incomplete or invalid. Return to the state
that can correct problems outside validation.
