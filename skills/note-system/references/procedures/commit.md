# Commit Procedure

Commit completed work. Each commit should deliver one clear result.

## Decide what to commit

For a vault, check whether it is tracked in Git. If it is not, report that commits do not apply.
Do not initialize a repository.

Include the entire repository working tree: my changes, pre-existing changes, and staged,
unstaged, or untracked files. Your task limits what you change, not which completed changes you
commit.

Run `git status --short --untracked-files=all` from the repository root before deciding that no
commit is needed. That is true only when the tree is clean or I explicitly exempted every
remaining change. If I told you to leave specific changes uncommitted, leave those changes and
commit the rest.

Do not commit a result when:

- I explicitly asked you to wait for confirmation before committing it.
- A design or behavior decision still needs my input.
- Required checks are unfinished, failed, or no longer cover the changed work.

Report the affected paths, exact blocker, and what must happen next. Keep delivery pending while
a blocker remains. You can still commit other completed, verified work unless I asked you to
pause committing. A change's age, author, or lack of relation to your task is not a blocker.

## Group and inspect the changes

Inspect the full working tree, staged and unstaged diffs, recent commits, current branch, and
upstream before grouping commits.

Before every commit, inspect generated file counts and sizes, untracked and ignored outputs, and
staged additions with `git diff --cached --stat` and `git diff --cached --numstat`. Open large
and binary additions. Remove temporary outputs created for this task, including session
transcripts, per-run JSON, screenshots, logs, duplicate snapshots, hash inventories, and
evidence manifests, unless I explicitly requested them. Requested source notes and selected
attachments are deliverables. Keep concise findings and reusable code or checks. Do not replace
deleted outputs with cleanup inventories or archives.

Keep unrelated file contents unchanged and commit completed work. Do not discard, overwrite,
stash, or newly ignore changes to make the tree appear clean. Ignoring temporary outputs or
promising later cleanup does not satisfy this check.

Group commits by result before staging:

1. Keep code, tests, migrations, and documentation together when they need each other to deliver
   one working result.
2. Split groups that each deliver a complete result on their own. Being part of one request,
   session, plan, or subsystem does not make them one result.
3. Draft a subject for each group. Split it again if the subject names only a broad area or
   leaves out another independently useful result.

After staging each group, read the staged diff. Unstage and regroup anything its subject does
not cover. Combine my changes with yours when they deliver the same result. Commit unrelated
completed results separately, including changes that predate this task.

Fold corrections or additions to the same result into an earlier local commit. Squash local
commits that deliver the same result if they have not been pushed. Do not rewrite published
commits without my direction.

## Check the final status

After the final commit and its hooks finish, run `git status --short --untracked-files=all` from
the repository root again. Its output must be empty unless I explicitly told you to leave
specific changes uncommitted. Check every remaining entry and commit other completed results as
needed. A diff limited to your task's files cannot replace this check.

If another entry remains, finish handling it or report its blocker and keep delivery pending.
Listing leftovers in a final response does not complete delivery. Leave existing ignored files
alone; check them separately for temporary outputs created by this task.

## Write the subject

Use `[Slug] Imperative outcome` and keep the entire subject under 50 characters.

| Slug | Use for |
| --- | --- |
| `[Feature]` | A significant new capability. |
| `[Fix]` | Correcting broken intended behavior. |
| `[Tweak]` | A minor behavior or repository improvement. |
| `[Refactor]` | Changing code structure without changing behavior. |
| `[Optimization]` | A performance improvement. |
| `[Documentation]` | Documentation work. Classify by the file's purpose, not its extension. |
| `[Design]` | Design work before implementing a feature. |
| `[Cleanup]` | Removing or tidying unused content. |
| `[Chore]` | Version bumps, scaffolding, and other non-development work. |

Start with an imperative verb after the slug. Name what becomes possible, corrected, prevented,
or different. A reader unfamiliar with the diff should understand the result.

If one subject cannot describe the result clearly within 50 characters, reconsider the grouping.
Do not hide multiple results behind an abstract subject.

## Result

Report each commit identifier and subject, the final status check, and whether you squashed
history. For uncommitted changes, cite my explicit exception or the blocker keeping delivery
pending. If no commit was needed, say the tree was already clean or only my explicit exceptions
remained. For a blocked commit, explain what must happen next.
