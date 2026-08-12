# Review dispatch briefs

Give each reviewer only source artifacts and these shared boundaries:

- Work read-only.
- Do not edit, format, stage, commit, switch branches, or change repository state.
- Review only the pinned diff and behavior it affects.
- Cite every finding with file and line plus the violated source or observable consequence.
- Rank findings by impact; omit praise and implementation narration.
- State "no findings" when the axis is clean.

## Intent axis inputs

- User request and acceptance checks.
- Specification and active work item.
- Settled decisions and accepted prototype contract or references.
- Documentation-impact result.
- Verification commands and artifacts.

## Engineering axis inputs

- Applicable `AGENTS.md` and repository standards.
- Pinned diff and commit list.
- Relevant public interfaces and test files.
- Formatter, linter, type-checker, test, and build results.

Each report should separate blocking defects, non-blocking judgment calls, and missing evidence.
