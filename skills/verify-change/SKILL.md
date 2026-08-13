---
name: verify-change
description: Use when production work must be proven against acceptance checks, proportionate quality tooling, tests, and direct behavior before completion; do not use for active prototype iteration.
---

# Verify Change

Produce direct, current evidence that the active change satisfies its acceptance checks and repository quality gates.

## Build the verification matrix

Map every acceptance check to the strongest practical command, interaction, or artifact. Inspect repository scripts and configuration rather than guessing commands. Load the selected completion profile and include:

1. the repository formatter in check mode or apply it and confirm no drift;
2. every configured linter with no outstanding finding;
3. every configured type checker with no unjustified escape such as `Any`;
4. focused tests for the active behavior;
5. the regression suite justified by the completion profile and affected surface;
6. build or packaging checks when the changed output requires them;
7. direct execution of the requested behavior.

For `focused-production`, run configured formatter, linter, and type checks, focused tests, directly affected regression tests, and the requested behavior. Do not add broad state matrices, builds, or full suites without a concrete affected dependency, risk, or repository requirement.

For `full-production`, include the appropriate full regression suite, required builds or packaging checks, and the complete relevant visual matrix.

Run the matrix after documentation updates and remediation so evidence matches the final state. Correct failures caused by the change. Record unrelated pre-existing failures and their evidence without silently expanding the active outcome; escalate them only when repository instructions explicitly require remediation or they prevent trustworthy proof.

## Verify GUI behavior

Use a browser automation tool when the production change affects a GUI. Exercise the exact triggering action, exact target element, and exact post-action state from each acceptance check. Inspect both the DOM and screenshots.

Read [visual-verification.md](references/visual-verification.md) and apply its checklist for every GUI change.

Under `focused-production`, cover only viewports, themes, and states that can materially change the requested result. Under `full-production`, cover relevant narrow and wide viewports, light and dark modes, intermediate loading or error states, and data-dependent content that can shift alignment. In both profiles, check visual hierarchy, clipping, overflow, awkward gaps, alignment, contrast, and unexpected style leakage.

When an accepted prototype exists, reproduce its recorded flows and compare final screenshots side by side with its visual references and acceptance contract. Functional equivalence alone does not pass.

## Record evidence

Record exact commands and concise outcomes in the work item or effort verification section. Link screenshots and large artifacts. Do not claim a check ran when it was unavailable; identify the missing proof and its impact.

Redact secrets and sensitive values from commands, output, screenshots, traces, payloads, and linked artifacts before storing or quoting them. Preserve useful structure with descriptive placeholders rather than committing credentials or private data.

## Completion

Complete when every acceptance check has direct passing evidence, configured formatter, linter, and type checks are green, the profile-selected focused and regression tests pass, GUI evidence covers the exact required flow and visual contract, and no failure caused by the change remains. Report any unrelated pre-existing failures without representing them as passing or as caused by the change.
