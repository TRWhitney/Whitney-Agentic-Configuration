# Validation State

Produce current, direct evidence that the completed implementation satisfies every accepted check
and has not introduced relevant regressions. Validation owns the selection, execution, inspection,
and sufficiency of completion evidence. It does not own production changes, test corrections, or
changes to accepted intent.

## Define the evidence

Begin with the complete task-owned change, accepted outcome, concrete acceptance checks, testing
results, reported symptoms when applicable, and any accepted artifacts that constrain observable
behavior.

Confirm that the acceptance checks still describe the complete accepted outcome and can be proven
against the implementation. Do not invent missing criteria or reinterpret an accepted check to fit
the result. When the intended outcome is incomplete, contradictory, or no longer feasible, use the
earliest available route that can resolve it.

Map each acceptance check to the strongest practical command, interaction, or artifact. Use the
repository's configured commands rather than guessing them. Select validation tiers from the
changed surface, affected dependencies, and risk, including as applicable:

- formatting with no remaining drift;
- every configured linter with no outstanding finding;
- every configured type checker passing;
- no use of `Any` unless no sensible typed alternative exists;
- focused tests and affected regression suites;
- broader regression, build, packaging, or integration checks required by the changed surface;
- direct execution of the accepted behavior.

Focused test results from implementation inform this selection but do not establish completion
evidence by themselves. Do not substitute an implementation detail, test double, internal state,
or nearby behavior for the acceptance check itself.

## Run and inspect

Run the selected checks against the completed work. Every selected check must pass. Treat a red or
flaky test as an implementation failure rather than dismissing it as unrelated or pre-existing.
When a check cannot run, record the missing proof and its impact; unavailable evidence is not a
pass.

For a reported symptom, repeat the same action through the same interface with the relevant data
and environment, then prove the expected result directly.

For a GUI change, operate the rendered interface yourself with appropriate interaction tooling.
Perform the exact triggering action on the exact target and observe the post-action state in the
interface. Take screenshots while exercising each relevant visual state and inspect every
screenshot yourself. Also inspect the available structural representation, such as a DOM,
accessibility tree, or component hierarchy. Use structural inspection to evaluate element
identity, state, semantics, and layout relationships; use visual inspection to evaluate the actual
rendered appearance. Neither substitutes for the other. Automated assertions, unattended scripts,
and artifact generation do not substitute for direct operation and inspection.

Exercise the themes, display sizes, intermediate states, and data conditions that can materially
affect the changed behavior or layout. Inspect alignment, hierarchy, contrast, wrapping, overflow,
clipping, awkward gaps, and style leakage. When an accepted prototype exists, reproduce its
recorded flows and compare the result with its visual references and binding contract.

## Adjudicate failures

Classify each failure by the work responsible for resolving it:

- An incorrectly selected, invoked, observed, or recorded validation check remains in validation.
- Incorrect or missing behavior, an inadequate test, a failing or flaky test, or a defect in
  repository validation tooling belongs to implementation.
- Missing acceptance criteria, contradictory sources, or unresolved consequential intent belongs
  to the earliest available state that can resolve it.

Do not modify production code, tests, or repository tooling to make evidence pass while remaining
in validation. Use the corresponding available route and preserve evidence only when the
correction cannot affect it.

## Record current evidence

Record exact commands, concise outcomes, inspected flows, and visual observations. Link large
non-screenshot artifacts only when they are needed to understand the evidence. Screenshots are
temporary inspection aids: remove them after visual validation and do not commit or link them as
durable artifacts. Avoid capturing secrets and redact sensitive values from commands, output,
traces, payloads, and linked artifacts while preserving useful structure.

Invalidate any evidence affected by later changes to behavior, tests, tooling, dependencies, or
environment. Rerun the affected check and every dependent check whose result may have changed.

## Continue

Continue to delivery when every accepted check has current, direct passing evidence, every selected
quality and regression check passes, required symptom reproduction and interface inspection are
complete, the evidence applies to the complete task-owned change, and no implementation defect,
evidence gap, or unresolved consequential decision remains.

Remain in validation while the evidence process itself is incomplete or invalid. Return to the
responsible state for any failure outside validation's ownership.
