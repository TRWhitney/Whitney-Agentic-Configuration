---
name: manage-work
description: Use when a request may modify a repository and must be classified as a fix, tweak, or significant feature before work begins; return feedback on an active prototype to prototype exploration instead of reclassifying it.
---

# Manage Work

Route repository changes through the smallest complete workflow and keep that workflow moving without requiring the user to invoke each skill.

## Ownership

Own request classification, completion-profile selection, phase transitions, focus, progress visibility, and the work record. Specialist skills return their result to this orchestrator rather than invoking the next stage. Treat applicable `AGENTS.md` files as the authority for standing preferences; do not restate them in work artifacts.

The user's current explicit feedback controls the active outcome. When it conflicts with an older decision, prototype contract, plan, or general style preference, treat the feedback as an amendment and update the affected source of truth. Ask only when the conflict creates a consequential ambiguity that the feedback does not resolve.

## Establish the work

1. Read the user's request, applicable repository instructions, and relevant existing artifacts.
2. Inspect enough of the repository to distinguish facts from decisions. Find facts yourself. Ask the user only for judgment that can materially change behavior, UX, architecture, or scope.
3. Write concrete acceptance checks before editing production code.
4. Before classifying a repository edit, determine whether it changes an active throwaway prototype. Prototype status is a workflow fact, not a judgment inferred from the size or correctness of the requested edit.
5. Classify the request by its actual uncertainty and size, not by words such as "small" or "feature":
   - **Fix route**: existing intended behavior is broken, failing, throwing, slow, or regressed. Use `$diagnose-fix`, then `$implement-work` for completion gates.
   - **Tweak route**: the outcome and acceptance checks are clear, the work fits one focused context, and no consequential product or architecture decision is open. Use `$implement-work` directly. Let it create a short local plan when more than one step is needed.
   - **Significant-feature route**: the effort spans multiple contexts, introduces a substantial capability or subsystem, or contains unresolved product, UX, data, or architecture decisions. Use `$wayfind-work`; when its completion gate passes, advance automatically through `$plan-work` and `$implement-work`.

If one consequential answer would make a request a tweak, ask that one question. Otherwise prefer the significant-feature route over silently inventing decisions.

When an active prototype is answering a wayfinding decision, return feedback to `$prototype-decision`. Do not reclassify prototype iteration as a fix or tweak merely because the artifact changes repository files, behaves incorrectly, or needs a small host scaffold. Resume production routing only after the prototype is accepted or abandoned.

## Select the completion profile

- **Prototype-iteration profile**: use only `$prototype-decision`. Do not invoke production testing, documentation, verification, review, work-item, or commit gates for an iteration. Directly prove the requested prototype delta using that skill. Update durable records only when the decision is accepted, abandoned, or requires handoff.
- **Focused-production profile**: use `$implement-work` for a bounded production fix or tweak. Require focused TDD where behavior changes, configured formatter, linter, and type checks, affected tests, direct behavior proof, a documentation-impact decision, and a proportionate final review. Expand to the full profile only when discovered risk justifies it.
- **Full-production profile**: use the complete planned implementation, regression, visual, documentation, independent-review when authorized, remediation, evidence, and commit workflow for significant, broad, security-sensitive, or architecture-changing work.

Standing production quality rules do not apply to active prototype iteration unless they explicitly name prototypes. The prototype profile's direct proof is its completion gate.

Record the selected profile in a durable work item when one exists. For a single focused tweak, state it with the acceptance checks rather than creating a work record solely for the profile.

## Keep the work moving

- Advance automatically whenever the next action follows from accepted intent.
- Pause only for a genuine decision, new authority, or an external blocker.
- Keep discoveries outside the accepted scope in the work record rather than expanding the active effort.
- Use the repository's existing planning convention. When none exists, read [local-work-store.md](references/local-work-store.md) and use its local adapter.
- Create a durable work record for significant, multi-item, or multi-context work. Avoid ceremony for a single focused tweak.
- Show a compact status line during interactive planning or long execution. Name the current phase, completed items, available frontier, and blockers or fog. Keep detail in the local record.
- Use `$handoff-work` before a context boundary when unfinished work cannot be continued immediately.

## Finish the route

Let `$implement-work` apply the selected production completion profile. Do not declare the request complete from an intermediate proxy such as code compiling or one test passing. Do not escalate a profile merely because a broader gate exists; escalate only for a concrete risk, dependency, or repository requirement.

## Completion

Complete when every accepted work item is committed according to repository conventions, all completion evidence is green, the local work record reflects reality, and the final response identifies the outcome and proof without replaying the work log.
