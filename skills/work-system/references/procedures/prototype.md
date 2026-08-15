# Prototype Procedure

Create a focused artifact that makes one unresolved decision easier to settle. An accepted
prototype is a source of intent, but it is not production implementation.

## Frame the decision

State the question, the possibilities worth comparing, and the observable evidence that will
settle it. Choose the cheapest form with enough fidelity to expose the relevant behavior or
constraint. Do not prototype a broad area whose uncertainty cannot be expressed as one answerable
question.

For an unsettled visual direction, compare meaningfully different structures, hierarchies, or
primary interactions rather than cosmetic variants. For logic or state questions, prefer a small
interactive artifact that exposes the relevant state and makes important transitions observable.

## Build and iterate

- Reuse the repository's established stack, components, and tooling when they improve fidelity.
  If a suitable host does not exist, add only the shared scaffold needed to exercise the question.
  Keep dependencies and shared tooling at their normal repository boundary.
- Mark decision-bearing prototype behavior and disposable data as non-production. Isolate them
  from production paths with an appropriate route, module, fixture, query parameter, or feature
  flag. This is separation of purpose and execution path, not a separate Git history.
- Build only what affects the decision. Omit production hardening, persistence, compatibility,
  and surrounding features unless they are part of the question.
- Exercise the decision-bearing behavior directly. Use the interactions, states, themes, and
  viewports that can materially change the result. Do not add production regression coverage or
  treat prototype checks as implementation testing or validation.
- Add tweak controls, element identification, stable labels, or preference export only when they
  make comparison or feedback materially easier. Keep those aids bounded to the prototype
  question and use the same names in the artifact and recorded feedback.
- Let me react and iterate until the direction is accepted or the prototype is inconclusive.
  When feedback describes a missed effect, inspect the current artifact and execution path before
  editing again. Restate the observable change, identify why the prior attempt missed it, and make
  the smallest supported revision. If the same effect fails twice, determine the causal and
  workflow gap before another attempt.

Classify the result as supporting a possibility, rejecting it, or remaining inconclusive. Do not
turn an inconclusive result into an accepted decision.

## Settle and preserve

Treat an accepted prototype as a binding primary source, not disposable inspiration. Record a
proportionate acceptance contract that distinguishes:

- **Binding qualities:** the behavior, hierarchy, relationships, interactions, states, responsive
  treatment, themes, and intentional absences that production work must preserve.
- **Flexible qualities:** placeholder content, disposable data, implementation technique, and
  details I have allowed production work to reinterpret.

Show me a concise interpretation and obtain my explicit confirmation that the contract captures
what matters. Record the exact flows, states, actions, target elements, and resulting conditions
used to accept the prototype.

Preserve the accepted artifact in the effort's `prototypes/` directory when it is self-contained.
When it relies on the repository's shared host, preserve the isolated source in its normal
repository location and link it from the prototype record. Include the accepted source, contract,
recorded preferences, visual evidence, and run instructions when applicable. Keep accepted
prototype work uncommitted while the workflow is active so it can be committed with the completed
outcome during delivery in normal repository history; do not create a dedicated branch merely
because it is a prototype. Discard or clearly label rejected alternatives.

Production implementation remains separate work and must meet its own testing, error handling,
and verification requirements. Prototype acceptance does not make prototype code production-ready.

## Result

Include the question, accepted decision or inconclusive verdict, acceptance contract, direct
evidence, retained artifact links, limitations, and unresolved uncertainty.
