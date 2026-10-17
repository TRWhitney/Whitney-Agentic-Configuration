# Prototype Procedure

Build a runnable prototype to help settle one open decision. Let me operate it and try the
proposed behavior. An agreed prototype defines requirements for later production work; it is not
production implementation.

## Define the question

State the question, alternatives worth comparing, and what we need to observe to decide. Choose
the simplest runnable form that shows the behavior or constraint. Do not prototype a broad topic
that cannot be stated as one answerable question.

For visual decisions, compare different layouts, hierarchies, or main interactions rather than
cosmetic variants. Include enough interaction to try the flow, transition, or response in
question. If the visual choice has no product interaction, provide a way to switch between its
variants or states inside the prototype.

Images, screenshots, videos, static mockups, and descriptions can support the comparison. They
cannot replace a prototype that lets us inspect behavior, state, responsiveness, and
interaction.

## Build and try it

- Reuse the project's stack, components, and tools when they help show the proposed behavior. If
  there is no suitable place to run it, add only the setup needed for the question. Keep
  dependencies and shared tools in their normal project locations.
- Label prototype behavior and sample data as non-production. Use a separate route, module,
  fixture, query parameter, or feature flag to keep them out of production use. Use normal Git
  history rather than a separate history for the prototype.
- Build only what affects the decision. Leave out production hardening, storage, compatibility,
  and surrounding features unless the question needs them.
- Try the relevant interactions, states, themes, and display sizes yourself. Do not add
  production regression tests or count these checks as production implementation tests or
  validation.
- Launch and operate every interaction relevant to the decision before presenting it. Provide
  complete run instructions and any non-sensitive sample data so I can try it without rebuilding
  the environment or code.
- Add adjustment controls, stable labels, or preference export only when they help comparison or
  feedback. Keep them limited to the question. Use the same names in the prototype and notes.
- Provide a way to identify regions and controls by stable names so we can discuss them. Prefer
  a prototype-only toggle showing names on hover and keyboard focus without changing the layout
  or behavior being compared. Use the same names in recorded feedback.
- Iterate with my feedback until we agree or the prototype is inconclusive. If feedback says an
  effect is missing, inspect the running prototype and code before editing again. State the
  expected change, find why the last attempt missed it, and make the smallest correction
  supported by what you found. After two failed attempts at the same effect, diagnose the cause
  and the process that missed it before trying again.

State whether the result supports an alternative, rejects it, or remains inconclusive. Do not
turn an inconclusive result into an agreed decision.

## Record the decision and save the source

Treat an agreed prototype as a requirement for production work. Record what production must
match and what it may change:

- Required behavior, hierarchy, relationships, interactions, states, responsive layout, themes,
  and things intentionally left out.
- Flexible placeholder content, sample data, implementation choices, and details I allowed you
  to change.

Show me this interpretation and obtain explicit confirmation that it captures what matters.
Record the flows, states, actions, target elements, and results we used to accept the prototype.

Save notes in the repository's existing prototype documentation or
`docs/prototypes/<prototype-slug>.md`. Include the agreed requirements, preferences, supporting
findings, and complete run instructions. Link the runnable source. Keep that source in the
repository, separate from production use.

After inspection and required review, delete rejected alternatives and temporary captures before
delivery. Keep useful comparisons and rejection reasons in the existing notes. Save raw captures
only if I explicitly request them. Keeping runnable source does not require archiving
screenshots, logs, duplicate packages, or per-run outputs.

Production work still needs its own tests, error handling, and validation. Agreement on the
prototype does not make its code ready for production.

## Result

Report the question, decision or inconclusive result, agreed requirements, direct observations,
links to saved files, limitations, and remaining uncertainty.
