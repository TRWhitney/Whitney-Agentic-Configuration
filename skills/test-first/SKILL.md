---
name: test-first
description: Use when production behavior is being added or changed and each observable slice must be developed through a red-green-refactor loop.
---

# Test First

Develop one observable vertical slice at a time through a stable public seam.

## Choose the seam

Write down the acceptance check and the highest stable public seam that can prove it. Prefer an existing seam. Select it autonomously unless a new public interface or unusually expensive harness would be a consequential architecture decision.

Tests must observe caller or user behavior rather than private structure. Read [test-design.md](references/test-design.md) when choosing doubles or reviewing test sensitivity.

## Run the loop

For each vertical slice:

1. **Red**: write one focused test from an independent expected result. Run it and observe the intended failure for missing or incorrect behavior.
2. **Green**: add only enough production behavior to pass the new test while preserving prior tests.
3. **Refactor**: improve names, duplication, boundaries, and dependency injection while all affected tests stay green.
4. Record the red and green commands when the work item requires completion evidence.
5. Repeat with the next behavior revealed by the acceptance checks and the previous cycle.

Use the formatter, linter, type checker, and narrow affected tests frequently for feedback, but leave the complete verification matrix to `$verify-change`.

Accepted prototypes are exempt from this loop only while they remain isolated prototype artifacts. Any production behavior derived from them enters through this loop.

## Completion

Complete when every acceptance behavior assigned to the active work item has a focused test at an agreed-by-rule public seam, each new test was observed red before green, refactoring left the focused suite green, and no test is coupled to incidental implementation structure.
