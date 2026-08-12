---
name: prototype-decision
description: Use when a consequential UI, interaction, state, or workflow decision is easier to settle by reacting to a concrete throwaway artifact than prose.
---

# Prototype Decision

Create a focused artifact to settle one decision, then preserve the accepted result as a primary source of product intent.

## Ownership

Own exploration, direct prototype verification, settlement, and permanent preservation. Production implementation belongs to `$implement-work` after the acceptance contract is confirmed.

## Explore

1. State the single decision the prototype must answer and what evidence will settle it.
2. Choose the cheapest faithful form. Read [prototype-forms.md](references/prototype-forms.md) for UI and logic guidance.
3. Clearly mark prototype code as non-production and keep it isolated from production paths.
4. Skip automated tests for the throwaway artifact. Verify it directly against its question, including all relevant interactions and states.
5. For visual work, provide meaningfully different structures rather than cosmetic variants. Exercise responsive sizes and light and dark themes when the product supports them.
6. When the decision contains meaningful tunable dimensions, add compact tweak controls for the few high-impact levers rather than requiring code edits. Keep defaults easy to restore and show current values.
7. Provide an **Export preferences** action that copies or downloads an agent-readable Markdown record of the chosen variant, control values, qualitative likes and dislikes, and unresolved notes. Make the export self-contained enough to paste into a Codex conversation.
8. Let the user react and iterate until a direction is accepted.

## Settle

An accepted prototype is a binding primary source, not disposable inspiration. Settlement blocks planning until all of these steps pass:

1. Produce an acceptance contract that separates:
   - **Binding** qualities: visual hierarchy, density, spacing relationships, typography roles, color roles, component treatment, interactions, states, responsive behavior, light and dark treatment, and any intentional absences.
   - **Flexible** qualities: incidental copy, placeholder data, implementation technique, and details the user explicitly allows production to reinterpret.

2. Incorporate the exported preferences into the contract as evidence, translating raw knob values into the product qualities they express.
3. Show a concise interpretation to the user and surface ambiguity through one primary question at a time.
4. Obtain explicit confirmation that the contract captures what matters. Acceptance of a screenshot or variant alone is insufficient.
5. Record exact visual verification flows, viewports, themes, states, triggering actions, target elements, and post-action states.

## Preserve

Preserve the prototype through the active work adapter. For the local adapter, use the active effort's `prototypes/<prototype-slug>/` directory with:

- the runnable artifact or source;
- `acceptance-contract.md`;
- the exported preference record when the prototype exposes controls;
- visual references such as accepted screenshots;
- a short run instruction when execution is not self-evident.

Keep it clearly non-production. Link it from the decision, specification, and affected work items. Production planning and review must trace back to this preserved source.

## Completion

Complete when the question is answered, the prototype has been directly exercised, the binding and flexible qualities have the user's explicit confirmation, permanent artifacts are linked, and the acceptance contract no longer blocks planning.
