---
name: review-change
description: Use when a completed repository change needs independent clean-context review for intent fidelity and engineering quality before commit or handoff.
---

# Review Change

Use two read-only subagents to inspect the same final change from independent perspectives, then drive findings to resolution.

## Establish scope

Pin the review base and final diff. Gather the request, specification, active work item, accepted decisions and prototypes, repository instructions, verification evidence, and relevant documentation.

If the diff is empty or the base is ambiguous, resolve that before dispatch. Define exact file and Git boundaries in both briefs.

## Dispatch clean contexts

Run two read-only subagents in parallel when capacity permits. Neither reviewer may receive the primary agent's conclusions or suspected defects. Both must not edit files, change Git state, run destructive commands, or commit.

### Intent reviewer

Ask the **Intent reviewer** to compare the diff and final behavior with the user's request, specification, accepted decisions, accepted prototype contract, documentation impact, and verification evidence. Require findings for missing or incorrect behavior, scope creep, visual mismatch, unproven acceptance checks, and stale or missing durable knowledge.

### Engineering reviewer

Ask the **Engineering reviewer** to compare the diff with repository standards and inspect architecture, dependency boundaries, maintainability, types, error handling, test quality, security implications, and unnecessary complexity. Require evidence by file and line and distinguish objective violations from judgment calls.

Use [review-briefs.md](references/review-briefs.md) as the minimum dispatch contract. If only one subagent slot exists, run the reviewers sequentially in separate clean contexts. If subagents are unavailable, report the limitation and perform separate passes locally without claiming clean-context independence.

## Adjudicate and remediate

The primary agent validates every finding against the source artifacts. Fix objective defects automatically, rerun affected `$verify-change` checks, and repeat the relevant review pass when remediation is material. Do not blindly merge or count duplicate findings.

Ask the user only when a validated finding exposes a new product, UX, architecture, or scope decision. Keep unresolved judgment calls distinct from defects.

## Completion

Complete when both review axes have reported, all validated objective defects are resolved with current verification evidence, any required user decision is settled or explicitly blocking, and no reviewer modified files or Git state.
