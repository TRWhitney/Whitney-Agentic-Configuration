# Prevent recurring repository mistakes

## Problem Statement

A fix can correct the reported example while leaving the same mistake possible elsewhere.
Project documentation can also lose track of which rules the code or checks enforce.

## Solution

Use separate triggered procedures in discovery, implementation, and validation. Discovery
collects the requirement, cause, and prior evidence. Implementation uses the first practical
prevention option in the approved order. Validation checks the evidence and routes any further
fix back to implementation. Delivery maintains the affected rule table through documentation.

## User Stories

1. As a maintainer, I want a correction of a missed requirement to prompt prevention where
   practical, so the same cause leads to fewer regressions.
2. As a contributor, I want to know what enforces a repository rule, so I can find the right
   code or check and recognize rules that still depend on judgment.

## Implementation Decisions

Adopt the split proposal approved in this conversation. Keep prevention available in fix and
tweak discovery, and fix, tweak, and novel-work implementation and validation. Use the existing
documentation procedure to maintain tables. Add an initial entry for procedure access in the
[project record](../../docs/project.md).

## Testing Decisions

Test navigator availability and deferred loading. Run behavioral cases for read-only discovery,
structural prevention and table maintenance, validation and return to implementation, and a
changed requirement that should not invoke prevention. Inspect actual commands and artifacts.

## Out of Scope

Scheduled cleanup and unrelated repository audits.
