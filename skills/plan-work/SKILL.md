---
name: plan-work
description: Use when intent is settled and must be converted into a durable specification and dependency-aware implementation work items.
---

# Plan Work

Translate accepted intent into an executable local work graph. Synthesize existing decisions; do not restart discovery.

## Ownership

Own the implementation specification, work-item boundaries, dependencies, and initial frontier. Do not decide unsettled product behavior and do not implement the items.

## Build the specification

1. Load the request, decision record, accepted prototypes, relevant repository instructions, current architecture, and existing tests.
2. Identify the highest stable public seams through which acceptance can be tested. Prefer existing seams. Escalate only when introducing a new seam is itself a consequential architecture decision.
3. Write the specification and work items through the active work adapter using the fields in [spec-and-items.md](references/spec-and-items.md).
4. Link accepted prototypes as binding sources. Carry every confirmed invariant into acceptance checks and visual verification requirements.
5. Capture documentation impact and explicit exclusions.

Resolve discoverable facts independently. If planning exposes a genuine product, UX, data, or architecture decision, return control to `$manage-work` with that decision. It routes the rollback through `$wayfind-work` and resumes planning after settlement.

## Build the work graph

- Prefer narrow vertical slices that deliver observable behavior through all necessary layers.
- Size each item for one fresh context.
- Give every item independent acceptance checks and proof commands or flows.
- Add only dependencies that truly prevent an item from starting.
- Separate preparatory refactoring only when it makes the requested change safer or allows later slices to remain green.
- Keep incidental opportunities outside the active effort.

Validate that dependency identifiers exist and the graph is acyclic. At least one incomplete item must be on the initial frontier.

## Advance automatically

Write the approved intent through the active work adapter without asking for another plan review. Return control to `$manage-work` with the first frontier item. It advances automatically to `$implement-work`. The user has already supplied judgment during wayfinding; ask again only if planning discovered a new consequential decision.

## Completion

Complete when the specification traces every accepted decision to an acceptance check, every work item is independently verifiable, the dependency graph has a valid frontier, and `$implement-work` can begin without inventing intent.
