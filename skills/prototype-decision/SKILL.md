---
name: prototype-decision
description: Use when a consequential UI, interaction, state, or workflow decision is easier to settle by reacting to a concrete throwaway artifact than prose.
---

# Prototype Decision

Create a focused artifact to settle one decision, then preserve the accepted result as a primary source of product intent.

## Ownership

Own exploration, direct prototype verification, settlement, and permanent preservation. Prototype iteration is a separate lane from production work. Do not route prototype iteration through `$diagnose-fix`, `$implement-work`, `$test-first`, `$verify-change`, `$review-change`, or `$document-change`. Production implementation belongs to `$implement-work` only after the acceptance contract is confirmed.

The user's latest explicit feedback amends earlier prototype choices and is the controlling source for the next iteration. Preserve earlier qualities only where the current feedback leaves them unaffected. Do not use a prior contract or general visual preference to resist an explicit requested change.

## Explore

1. State the single decision the prototype must answer and what evidence will settle it. For an iteration, translate the latest explicit feedback into one observable delta and name the unaffected qualities that must remain stable. Do not ask for confirmation when the feedback is already unambiguous.
2. Choose the cheapest faithful form. Read [prototype-forms.md](references/prototype-forms.md) for UI and logic guidance.
3. Reuse the repository's established stack and tooling. When the stack is settled but the repository cannot yet host a faithful prototype, create the minimum shared host scaffold in normal repository locations. Put manifests, lockfiles, configuration, and shared tooling at their ordinary repository boundary; do not recreate the dependency tree inside the prototype directory.
4. Clearly mark the decision-bearing prototype behavior and disposable data as non-production. Isolate them with the cheapest suitable route, module, fixture, or feature flag rather than isolating shared dependencies or host infrastructure.
5. Skip automated tests and production completion gates for the throwaway artifact. Verify each iteration directly against its observable delta. For visual feedback, inspect the rendered result before and after the edit, prove the changed property, and confirm the unaffected qualities remain stable. Exercise only the states, themes, and viewports that can materially affect the requested delta.
6. Use meaningfully different structures when creating initial alternatives for an unsettled visual direction. When applying explicit feedback, make the smallest decision-bearing revision to the requested quality without inventing a new structural alternative.
7. Add support apparatus only when it directly improves the named decision; do not build it preemptively. This includes tweak controls, element identification with hover labels and stable names, and an **Export preferences** action. Keep the same names in feedback and exports. Prefer capturing qualitative feedback and preference records outside the prototype UI when an in-app mechanism is unnecessary.
8. Let the user react and iterate until a direction is accepted.

## Break repeated-failure loops

When the user reports that an iteration did not produce the intended effect:

1. Mark the iteration as failed and invalidate the previous verification. Inspect the current rendered artifact and execution path before editing again; distinguish a wrong edit from a stale build, wrong route, overridden style, or misunderstood target.
2. Restate the observable delta using the user's current words, identify the causal explanation for the miss, and make the smallest revision supported by that evidence.
3. If the same requested effect fails twice, do not make another edit until the cause of the repeated failure and the missing workflow control are identified. Report both plainly. Ask the user only if an unresolved judgment is genuinely required.
4. Do not claim that the instructions were sufficient after they permitted the repeated failure. Strengthen the acceptance check or workflow control before another attempt.

Do not respond to a failed iteration by expanding scope, infrastructure, controls, instrumentation, or process unless the causal evidence requires it.

## Settle

An accepted prototype is a binding primary source, not disposable inspiration. Settlement blocks planning until all of these steps pass:

1. Produce a proportionate acceptance contract covering only the named decision and the surrounding qualities that must remain invariant. Separate:
   - **Binding** qualities: visual hierarchy, density, spacing relationships, typography roles, color roles, component treatment, interactions, states, responsive behavior, light and dark treatment, and any intentional absences.
   - **Flexible** qualities: incidental copy, placeholder data, implementation technique, and details the user explicitly allows production to reinterpret.

2. Incorporate any exported or externally recorded preferences into the contract as evidence, translating raw values into the product qualities they express.
3. Show a concise interpretation to the user. Ask a question only for material ambiguity; group tightly related ambiguities when answering them together is easier for the user.
4. Obtain explicit confirmation that the contract captures what matters. A clear acceptance after the concise interpretation counts as confirmation; do not require an additional ceremony turn. Acceptance of a screenshot or variant alone is insufficient only when binding and flexible qualities remain materially ambiguous.
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
