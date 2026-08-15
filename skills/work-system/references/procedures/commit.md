# Commit Procedure

Preserve completed work as clear, reviewable repository history. Commit and squash liberally,
while keeping each commit focused on one concrete outcome.

## Decide whether to commit

Commit only completed work whose prerequisites remain satisfied. Stop and report a concrete
blocker when:

- I appear to be reviewing the work or waiting to confirm it before commit.
- A significant design or behavior assumption still needs my input.
- Required verification is incomplete, invalid, or no longer matches the work.

The procedure remains required even when it returns a blocker instead of a commit.

## Compose the commits

Inspect the working tree, staged changes, relevant diffs, recent commits, current branch, and
upstream before deciding how to commit.

- Group changes by completed outcome, not authorship, file boundaries, or implementation order.
- Fold work into an earlier local commit when it completes or corrects that same outcome.
- Squash local commits that describe the same outcome when they have not reached the upstream.
  Do not rewrite published commits without my direction.
- Include my changes with yours when they contribute to the same outcome. Commit them separately
  when they form another complete outcome. Don't disregard this rule because the change was pre-existing before work.
- Draft a subject for each proposed commit. Split changes when one accurate subject would become
  vague or omit a distinct outcome; combine commits when their subjects describe the same one.

Preserve unrelated and unfinished changes exactly as found.

## Write the subject

Use the form `[Slug] Imperative outcome` and keep the entire subject under 50 characters.

| Slug | Use for |
| --- | --- |
| `[Feature]` | A significant new capability. |
| `[Fix]` | Correcting broken intended behavior. |
| `[Tweak]` | A minor behavior or repository improvement. |
| `[Refactor]` | A structural change that preserves behavior. |
| `[Optimization]` | A performance improvement. |
| `[Documentation]` | Primarily documentation work. Classify by the artifact's role, not its file extension. |
| `[Design]` | Pre-implementation design work for a feature. |
| `[Cleanup]` | Removing or tidying unused content. |
| `[Chore]` | Version bumps, scaffolding, and other non-development work. |

Start the description with an imperative verb, as if giving a command to the repository. Name
the practical result rather than only the edited file, component, mechanism, or general area. A
developer unfamiliar with the diff should be able to predict what became possible, corrected,
prevented, or different.

## Result

Include each commit identifier and subject, any intentionally uncommitted changes, and whether
history was squashed. If no commit was created, include the exact blocker and the action needed
to resolve it.
