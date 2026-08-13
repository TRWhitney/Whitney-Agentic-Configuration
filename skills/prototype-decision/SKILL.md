---
name: prototype-decision
description: Use when a consequential UI, interaction, state, or workflow decision is easier to settle by reacting to a concrete throwaway artifact than prose.
---

# Prototype Decision

Create a focused artifact to settle one decision, then preserve the accepted result as a primary source of product intent.

## Ownership

Own exploration, direct prototype verification, settlement, and permanent preservation. Prototype iteration is a separate lane from production work. Do not route prototype iteration through `$diagnose-fix`, `$implement-work`, `$test-first`, `$verify-change`, `$review-change`, or `$document-change`. Production implementation belongs to `$implement-work` only after the acceptance contract is confirmed.

## Explore

1. State the single decision the prototype must answer and what evidence will settle it.
2. Choose the cheapest faithful form. Read [prototype-forms.md](references/prototype-forms.md) for UI and logic guidance.
3. Reuse the repository's established stack and tooling. When the stack is settled but the repository cannot yet host a faithful prototype, create the minimum shared host scaffold in normal repository locations. Put manifests, lockfiles, configuration, and shared tooling at their ordinary repository boundary; do not recreate the dependency tree inside the prototype directory.
4. Clearly mark the decision-bearing prototype behavior and disposable data as non-production. Isolate them with the cheapest suitable route, module, fixture, or feature flag rather than isolating shared dependencies or host infrastructure.
5. Skip automated tests for the throwaway artifact. Verify it directly against its question, including all relevant interactions and states.
6. Treat feedback that an iteration did not produce the intended effect as a signal to verify the current artifact and make the smallest decision-bearing revision. Do not expand scope, infrastructure, controls, instrumentation, or process unless the feedback specifically requires it.
7. For visual work, provide meaningfully different structures rather than cosmetic variants. Exercise responsive sizes and light and dark themes when the product supports them and they affect the decision.
8. Add support apparatus only when it directly improves the named decision; do not build it preemptively. This includes tweak controls, element identification with hover labels and stable names, and an **Export preferences** action. Keep the same names in feedback and exports. Prefer capturing qualitative feedback and preference records outside the prototype UI when an in-app mechanism is unnecessary.
9. Let the user react and iterate until a direction is accepted.

## Settle

An accepted prototype is a binding primary source, not disposable inspiration. Settlement blocks planning until all of these steps pass:

1. Produce an acceptance contract that separates:
   - **Binding** qualities: visual hierarchy, density, spacing relationships, typography roles, color roles, component treatment, interactions, states, responsive behavior, light and dark treatment, and any intentional absences.
   - **Flexible** qualities: incidental copy, placeholder data, implementation technique, and details the user explicitly allows production to reinterpret.

2. Incorporate any exported or externally recorded preferences into the contract as evidence, translating raw values into the product qualities they express.
3. Show a concise interpretation to the user and surface ambiguity through one primary question at a time.
4. Obtain explicit confirmation that the contract captures what matters. Acceptance of a screenshot or variant alone is insufficient.
5. Record exact visual verification flows, viewports, themes, states, triggering actions, target elements, and post-action states.

## Preserve

Preserve the prototype through the active work adapter. For the local adapter, use the active effort's `prototypes/<prototype-slug>/` directory for:

- the runnable artifact when it is self-contained, or source links when the prototype uses the repository's shared host;
- `acceptance-contract.md`;
- the preference record when one exists;
- visual references such as accepted screenshots;
- a short run instruction when execution is not self-evident.

Do not copy package manifests, installed dependencies, or shared scaffold into the preservation directory. Keep decision-bearing behavior clearly non-production. Link the prototype from the decision, specification, and affected work items so production planning and review can trace back to it.

## Completion

Complete when the question is answered, the prototype has been directly exercised, the binding and flexible qualities have the user's explicit confirmation, permanent artifacts are linked, and the acceptance contract no longer blocks planning.
