# Commit Procedure

Preserve completed work as clear, reviewable repository history. Commit completed outcomes
liberally, while keeping each commit focused on one concrete outcome.

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

Partition the final work before staging:

1. Derive candidate commits from independently complete outcomes, not from the overall request,
   work session, plan, or affected subsystem.
2. Keep changes together when they must travel together to deliver one valid result. Include the
   implementation, tests, migrations, and documentation required by that result.
3. Split changes when either group could remain a complete, valid, independently describable
   outcome without the other. Being requested together or touching the same subsystem is not
   sufficient reason to combine them.
4. Draft a subject for each candidate outcome. If one subject would name a broad area, summarize
   the overall task, or omit an independently useful result, split the candidate before staging.

Repeat this partitioning until no candidate contains more than one independently complete outcome.
After staging each candidate, inspect the staged diff. Every staged change must be necessary for
its subject; unstage and repartition anything that is not.

- Treat changes by outcome, regardless of authorship or when they first appeared. Include my
  changes with yours when they contribute to the same outcome. When my changes do not, commit them
  separately. Do not disregard my changes because they predate this work.
- Fold work into an earlier local commit when it completes or corrects that same outcome.
- Squash local commits that describe the same outcome when they have not been pushed upstream.
  Do not rewrite published commits without my direction.

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

Start the text after the slug with an imperative verb, as if giving a command to the repository.
Name the practical result rather than only the edited file, component, mechanism, or general area.
A developer unfamiliar with the diff should be able to predict what became possible, corrected,
prevented, or different.

Do not use an umbrella subject to conceal multiple outcomes. If the practical result cannot be
named concretely within 50 characters, revisit the commit partition instead of making the subject
more abstract.

## Result

Include each commit identifier and subject, any intentionally uncommitted changes, and whether
history was squashed. If no commit was created, include the exact blocker and the action needed
to resolve it.
