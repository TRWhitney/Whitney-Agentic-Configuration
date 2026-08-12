# Specification and work-item formats

For the local adapter, store the specification as `spec.md` and items as `items/<NN>-<slug>.md` inside the active effort. Other adapters serialize the same fields using their own storage operations.

## Specification

```markdown
# <Outcome>

## Problem

## Accepted outcome

## Acceptance checks

## Decisions and accepted sources

## Implementation boundaries

## Testing seams

## Documentation impact

## Out of scope
```

Describe stable behavior and boundaries. Avoid speculative code, brittle file-by-file instructions, and details an implementer can discover safely.

## Work item

```markdown
# <NN> <Observable slice>

**Status:** ready | active | blocked | complete
**Blocked by:** <item links or none>

## Outcome

## Acceptance checks

## Accepted sources

## Verification

## Completion evidence
```

The frontier consists of ready items whose dependencies are complete. A blocked item remains outside the frontier even when its item dependencies are complete. Number items in dependency order for readability, but derive readiness from status and dependencies rather than numbering.
