---
name: manage-work
description: Use when a request may modify a repository and must be classified as a fix, tweak, or significant feature before work begins.
---

# Manage Work

Route repository changes through the smallest complete workflow and keep that workflow moving without requiring the user to invoke each skill.

## Ownership

Own request classification, phase transitions, focus, progress visibility, and the work record. Specialist skills return their result to this orchestrator rather than invoking the next stage. Treat applicable `AGENTS.md` files as the authority for standing preferences; do not restate them in work artifacts.

## Establish the work

1. Read the user's request, applicable repository instructions, and relevant existing artifacts.
2. Inspect enough of the repository to distinguish facts from decisions. Find facts yourself. Ask the user only for judgment that can materially change behavior, UX, architecture, or scope.
3. Write concrete acceptance checks before editing production code.
4. Classify the request by its actual uncertainty and size, not by words such as "small" or "feature":
   - **Fix route**: existing intended behavior is broken, failing, throwing, slow, or regressed. Use `$diagnose-fix`, then `$implement-work` for completion gates.
   - **Tweak route**: the outcome and acceptance checks are clear, the work fits one focused context, and no consequential product or architecture decision is open. Use `$implement-work` directly. Let it create a short local plan when more than one step is needed.
   - **Significant-feature route**: the effort spans multiple contexts, introduces a substantial capability or subsystem, or contains unresolved product, UX, data, or architecture decisions. Use `$wayfind-work`; when its completion gate passes, advance automatically through `$plan-work` and `$implement-work`.

If one consequential answer would make a request a tweak, ask that one question. Otherwise prefer the significant-feature route over silently inventing decisions.

## Keep the work moving

- Advance automatically whenever the next action follows from accepted intent.
- Pause only for a genuine decision, new authority, or an external blocker.
- Keep discoveries outside the accepted scope in the work record rather than expanding the active effort.
- Use the repository's existing planning convention. When none exists, read [local-work-store.md](references/local-work-store.md) and use its local adapter.
- Create a durable work record for significant, multi-item, or multi-context work. Avoid ceremony for a single focused tweak.
- Show a compact status line during interactive planning or long execution. Name the current phase, completed items, available frontier, and blockers or fog. Keep detail in the local record.
- Use `$handoff-work` before a context boundary when unfinished work cannot be continued immediately.

## Finish the route

Let `$implement-work` run documentation, verification, independent review, remediation, and commit gates. Do not declare the request complete from an intermediate proxy such as code compiling or one test passing.

## Completion

Complete when every accepted work item is committed according to repository conventions, all completion evidence is green, the local work record reflects reality, and the final response identifies the outcome and proof without replaying the work log.
