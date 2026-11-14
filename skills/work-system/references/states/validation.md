# Validation State

Check the completed work against the agreed requirements and look for regressions. Select and
run checks, inspect their results, and record conclusions here. Return to earlier states to
change requirements, production code, or tests.

## Define the evidence

Review all changes made for the task, its requirements and acceptance checks, implementation
test results, reported symptoms, applicable project and release requirements, and agreed
documents or prototypes.

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
missing proof and its impact when a check cannot run; unavailable evidence is not a pass. An
unavailable environment does not cancel an agreed support or release requirement.

For a reported symptom, repeat the same action through the same interface with the relevant data
and environment, and observe the expected result directly.

### Visual verification

For GUI changes, use the rendered interface. Perform the exact triggering action on the exact
target and observe the resulting interface state. Capture and inspect screenshots of each
relevant visual state. Also inspect the available DOM, accessibility tree, or component
hierarchy for identity, state, semantics, and layout relationships. Structural and visual
inspection are both required. Automated assertions, unattended scripts, and generated files do
not replace direct operation and inspection.

Select and inspect the required visual states:

1. Read the agreed requirements, accepted prototypes, and affected interface code. Make a
   working list of the display changes caused by each affected control, including changes while
   editing input. Use that list to check each affected requirement. Identify what must remain
   visible and usable, and which positions or sizes must stay unchanged. Include controls that
   reveal additional content or change what is displayed.
2. In each affected part of the interface, use realistic content that exercises its wrapping,
   scrolling, and formatting. Vary text length, item count, and content structure where supported.
   Keep that content in place through interactions that hide or restore it. Combine content and
   display conditions when they can affect one another.
3. Follow each affected task through success, failure, and recovery where supported. Inspect
   feedback when it appears, changes, and clears, including while editing input before submitting
   again. Inspect content when it becomes empty or returns.
   Observe each change before taking the next action. In automated flows, capture or query the
   rendered interface after each action that changes content, feedback, or layout. Inspect those
   observations, including the changed content and surrounding layout.
4. After repairs, repeat the checks those repairs could affect.

After the checks pass, compare the working list with the recorded actions and observations,
step by step. Inspect any required state that the next action replaced before it was observed.
Complete those inspections before finishing visual verification.

Exercise themes, display sizes, intermediate states, and data conditions that can affect the
change. Check that the affected tasks work from start to finish, including correcting errors and trying again. Inspect alignment, hierarchy, contrast, wrapping, overflow, clipping, gaps, and style
leakage. When an accepted prototype exists, open both it and the finished interface in a browser,
replay its recorded flows, and compare the result with the prototype and its agreed requirements.

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
paths when needed. Describe the results before deleting the captures.
Delete screenshots, logs, traces, per-run JSON, and other raw outputs after inspection and
required review, before delivery, unless I explicitly asked to keep them. Delete these files
even if Git ignores them. Avoid capturing secrets and redact sensitive values shared for inspection
or review.

When behavior, tests, tooling, dependencies, or the environment change, invalidate affected
evidence and rerun the affected checks and their dependent checks.

## Continue

Continue to delivery when every acceptance check passes against the finished change, selected
quality and regression checks pass, and required reproduction and interface inspection are done.
No implementation defect, missing proof, or unresolved product or architecture decision may
remain.

Remain in validation while its evidence process is incomplete or invalid. Return to the state
that can correct problems outside validation.
