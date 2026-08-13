# Prototype forms

## UI questions

Prefer variants embedded in the real surrounding page so navigation, density, data, and neighboring controls remain visible. Use a clearly marked route or query parameter when isolation is necessary. Make variants disagree about structure, information hierarchy, and primary affordance.

Use existing components and styling infrastructure where that improves fidelity. Stub mutations and keep prototype data disposable. Capture each accepted state at representative narrow and wide viewports in both supported themes.

When several values could plausibly define the result, expose a small adjustment panel for the decision-bearing levers, such as density, scale, spacing, contrast, information amount, motion, or layout proportions. Prefer named presets plus a few bounded controls over a large design-system editor. Include reset and make every choice visible.

When visual feedback might otherwise depend on descriptions such as "the area on the left," add a low-friction identification aid. Prefer an opt-in toggle that reveals short element names on hover and keyboard focus. Use persistent overlays when hover is unavailable. Keep the aid from shifting layout, obscuring important content, or intercepting prototype interactions. Reuse the exact names in qualitative feedback fields and the exported record so the user and agent share one vocabulary.

Provide an export action that produces Markdown with:

- prototype name and revision;
- selected structural variant;
- every control name and current value;
- liked elements and why they work;
- disliked elements and what should change;
- qualities that must remain invariant;
- open questions.

Generate the record from the live prototype state. Let the user edit qualitative fields before copying or downloading it. Treat this export as evidence for settlement, not as the acceptance contract itself.

## Logic and state questions

Prefer a small interactive artifact that exposes full relevant state after every action. Keep the decision-bearing logic pure and separate from the presentation shell. Include guided scenarios for the happy path, awkward edge cases, and invalid transitions.

## Shared constraints

- One prototype answers one named question.
- Directly verify every path used to accept it.
- Expose controls and preference export only when they improve the decision; avoid knobs unrelated to the prototype question.
- Keep production dependencies and persistence out unless they are the subject of the question.
- Preserve accepted artifacts; discard or clearly label rejected alternatives.
- Reimplement accepted behavior under production testing and error-handling standards.
