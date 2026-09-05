# Validation State

Prove that the completed implementation satisfies every accepted check without relevant
regressions. Validation selects, runs, inspects, and records completion evidence. Production
changes, test corrections, and changes to accepted intent belong to earlier states.

## Define the evidence

Review the complete task-owned change, accepted outcome, acceptance checks, implementation test
results, reported symptoms, and accepted artifacts that constrain behavior.

Confirm that the checks cover the accepted outcome and can be proven against the implementation.
Do not invent criteria or reinterpret a check to fit the result. Route incomplete, contradictory,
or infeasible intent to the earliest available state that can resolve it.

Map each accepted check to the strongest practical command, interaction, or artifact that proves
it directly.
Use configured repository commands. Select checks for the changed surface, dependencies, and risk:

- formatting with no drift;
- every configured linter with no findings;
- every configured type checker passing;
- no `Any` unless no sensible typed alternative exists;
- focused tests and affected regression suites;
- broader regression, build, packaging, or integration checks required by the change;
- direct execution of the accepted behavior.

Implementation test results inform this selection but do not alone prove completion. An internal
detail, test double, or nearby behavior does not prove the accepted behavior.

## Run and inspect

Run the selected checks against the completed work. Every check must pass. Treat failing or flaky
tests as implementation failures, including unrelated or pre-existing failures. Record missing
proof and its impact when a check cannot run; unavailable evidence is not a pass.

For a reported symptom, repeat the same action through the same interface with the relevant data
and environment, and observe the expected result directly.

For GUI changes, operate the rendered interface with appropriate interaction tooling. Perform the
exact triggering action on the exact target and observe the resulting interface state. Capture
and inspect screenshots of each relevant visual state. Also inspect the available DOM,
accessibility tree, or component hierarchy for identity, state, semantics, and layout
relationships. Structural and visual inspection are both required. Automated assertions,
unattended scripts, and generated artifacts do not replace direct operation and inspection.

Exercise themes, display sizes, intermediate states, and data conditions that can affect the
change. Inspect alignment, hierarchy, contrast, wrapping, overflow, clipping, gaps, and style
leakage. When an accepted prototype exists, replay its recorded flows and compare the result with
its visual references and binding contract.

## Adjudicate failures

- Keep incorrectly selected, invoked, observed, or recorded checks in validation.
- Return incorrect or missing behavior, inadequate or failing tests, flaky tests, and defects in
  repository validation tooling to implementation.
- Route missing acceptance criteria, contradictory sources, or unresolved consequential intent
  to the earliest available state that can resolve them.

Use the displayed route before changing production code, tests, or tooling. Preserve evidence
only when the correction cannot affect it.

## Record current evidence

Record exact commands, concise outcomes, inspected flows, and visual observations. Link large
non-screenshot artifacts only when needed to understand the evidence. Remove screenshots after
inspection; do not commit or link them as durable artifacts. Avoid capturing secrets and redact
sensitive values from commands, output, traces, payloads, and linked artifacts while preserving
useful structure.

When behavior, tests, tooling, dependencies, or the environment change, invalidate affected
evidence and rerun the affected checks and their dependent checks.

## Continue

Continue to delivery when every accepted check has current, direct passing evidence for the
complete task-owned change; selected quality and regression checks pass; required symptom
reproduction and interface inspection are complete; and no implementation defect, evidence gap,
or unresolved consequential decision remains.

Remain in validation while its evidence process is incomplete or invalid. Return to the
responsible state for failures outside validation's ownership.
