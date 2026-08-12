---
name: verify-change
description: Use when changed repository work must be proven against acceptance checks, quality tooling, complete tests, and direct visual behavior before review or completion.
---

# Verify Change

Produce direct, current evidence that the active change satisfies its acceptance checks and repository quality gates.

## Build the verification matrix

Map every acceptance check to the strongest practical command, interaction, or artifact. Inspect repository scripts and configuration rather than guessing commands. Include:

1. the repository formatter in check mode or apply it and confirm no drift;
2. every configured linter with no outstanding finding;
3. every configured type checker with no unjustified escape such as `Any`;
4. focused tests for the active behavior;
5. the appropriate full test suite for regression confidence;
6. build or packaging checks when the changed output requires them;
7. direct execution of the requested behavior.

Run the matrix after documentation updates and remediation so evidence matches the final state. Treat any failing or flaky test encountered as part of the active problem until corrected or shown to require authority outside the task.

## Verify GUI behavior

Use a browser automation tool when the change affects a GUI. Exercise the exact triggering action, exact target element, and exact post-action state from each acceptance check. Inspect both the DOM and screenshots.

Read [visual-verification.md](references/visual-verification.md) and apply its checklist for every GUI change.

Cover relevant narrow and wide viewports, light and dark modes, intermediate loading or error states, and data-dependent content that can shift alignment. Check visual hierarchy, clipping, overflow, awkward gaps, alignment, contrast, and unexpected style leakage.

When an accepted prototype exists, reproduce its recorded flows and compare final screenshots side by side with its visual references and acceptance contract. Functional equivalence alone does not pass.

## Record evidence

Record exact commands and concise outcomes in the work item or effort verification section. Link screenshots and large artifacts. Do not claim a check ran when it was unavailable; identify the missing proof and its impact.

Redact secrets and sensitive values from commands, output, screenshots, traces, payloads, and linked artifacts before storing or quoting them. Preserve useful structure with descriptive placeholders rather than committing credentials or private data.

## Completion

Complete when every acceptance check has direct passing evidence, formatter, linter, type checker, focused tests, and full test suite are green where configured, GUI evidence covers the exact flow and visual contract, and no known red or flaky check remains.
