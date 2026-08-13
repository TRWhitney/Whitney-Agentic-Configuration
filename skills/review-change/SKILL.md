---
name: review-change
description: Use when full-production work or a risk-escalated focused change needs intent and engineering review before completion; do not use for active prototype iteration.
---

# Review Change

Inspect a final production change from intent and engineering perspectives with independence proportionate to its completion profile, then drive findings to resolution.

## Establish scope

Pin the review base and final diff. Gather the request, specification, active work item, accepted decisions and prototypes, repository instructions, verification evidence, and relevant documentation.

If the diff is empty or the base is ambiguous, resolve that before dispatch. Define exact file and Git boundaries in both briefs.

## Select review depth

- For `focused-production`, perform concise intent and engineering passes locally. Escalate to clean contexts only for a concrete risk such as broad coupling, security impact, consequential visual fidelity, or difficult-to-observe behavior.
- For `full-production`, prefer two clean read-only contexts when the user permits subagents and capacity exists.
- When subagents are not authorized or available, perform both passes locally. Keep their evidence separate and do not claim clean-context independence.

Any reviewer, local or delegated, must not edit files, change Git state, run destructive commands, or commit during the review pass.

## Review axes

### Intent reviewer

The **Intent reviewer** compares the diff and final behavior with the user's request, specification, accepted decisions, accepted prototype contract, documentation impact, and verification evidence. Require findings for missing or incorrect behavior, scope creep, visual mismatch, unproven acceptance checks, and stale or missing durable knowledge.

### Engineering reviewer

The **Engineering reviewer** compares the diff with repository standards and inspects architecture, dependency boundaries, maintainability, types, error handling, test quality, security implications, and unnecessary complexity. Require evidence by file and line and distinguish objective violations from judgment calls.

Use [review-briefs.md](references/review-briefs.md) as the review contract. When clean contexts are authorized, neither receives the primary agent's conclusions or suspected defects. If only one slot exists, run them sequentially.

## Adjudicate and remediate

The primary agent validates every finding against the source artifacts. Fix objective defects automatically, rerun affected `$verify-change` checks, and repeat the relevant review pass when remediation is material. Do not blindly merge or count duplicate findings.

Ask the user only when a validated finding exposes a new product, UX, architecture, or scope decision. Keep unresolved judgment calls distinct from defects.

## Completion

Complete when the review depth matches the selected profile and observed risk, both review axes have reported, all validated objective defects are resolved with current verification evidence, any required user decision is settled or explicitly blocking, and no review pass modified files or Git state.
