# Prototype forms

## UI questions

Prefer variants embedded in the real surrounding page so navigation, density, data, and neighboring controls remain visible. Use the repository's normal application scaffold and dependency boundary. If that host does not exist but the stack is settled, create only enough shared scaffold at normal repository locations to render the prototype faithfully. Isolate prototype behavior with a clearly marked route, module, fixture, query parameter, or feature flag. Never create a second dependency tree under the prototype directory. Make initial alternatives disagree about structure, information hierarchy, and primary affordance. When applying explicit feedback to a selected direction, change the requested quality instead of introducing another alternative.

Use existing components and styling infrastructure where that improves fidelity. Stub mutations and keep prototype data disposable. During iteration, capture only the states, viewports, and themes capable of changing the requested result. At settlement, capture each accepted state at the representative combinations recorded in the contract.

When several values could plausibly define the result and live adjustment will materially improve the decision, expose a small adjustment panel for the decision-bearing levers, such as density, scale, spacing, contrast, information amount, motion, or layout proportions. Prefer named presets plus a few bounded controls over a large design-system editor. Include reset and make every choice visible.

When visual feedback actually becomes ambiguous because it depends on descriptions such as "the area on the left," consider a low-friction identification aid. Prefer an opt-in toggle that reveals short element names on hover and keyboard focus. Use persistent overlays when hover is unavailable. Keep the aid from shifting layout, obscuring important content, or intercepting prototype interactions. Reuse the exact names in qualitative feedback fields and the exported record so the user and agent share one vocabulary.

When a preference export will materially simplify settlement, provide an export action that produces Markdown with:

- prototype name and revision;
- selected structural variant;
- every control name and current value;
- liked elements and why they work;
- disliked elements and what should change;
- qualities that must remain invariant;
- open questions.

Generate the record from the live prototype state. Let the user edit qualitative fields before copying or downloading it. Treat this export as evidence for settlement, not as the acceptance contract itself. Otherwise, capture the same relevant evidence conversationally outside the prototype UI.

## Logic and state questions

Prefer a small interactive artifact that exposes full relevant state after every action. Keep the decision-bearing logic pure and separate from the presentation shell. Include guided scenarios for the happy path, awkward edge cases, and invalid transitions.

## Shared constraints

- One prototype answers one named question.
- Directly verify every path used to accept it. For an iteration, compare the decision-bearing result before and after, prove the requested delta, and inspect that unaffected qualities remain stable.
- Expose controls and preference export only when they improve the decision; avoid knobs unrelated to the prototype question.
- Keep dependencies and shared tooling at their normal repository boundary. Keep production integrations and persistence out unless they are the subject of the question.
- When an iteration misses its intended effect, invalidate the previous proof and establish why it missed before revising the smallest decision-bearing part. Stop editing when the same requested effect fails twice until the causal gap is understood.
- Preserve accepted artifacts; discard or clearly label rejected alternatives.
- Reimplement accepted behavior under production testing and error-handling standards.
