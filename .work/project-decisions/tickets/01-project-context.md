# 01 Locate project agreements during repository work

**What to build:** Navigator lookup of `docs/project.md`, with its
reference available when starting or resuming repository workflows.

**Blocked by:** none

**Status:** complete

- [x] Resolve `docs/project.md` from the current project
  root, including nested directories, worktrees and non-Git projects.
- [x] Look up the document without creating metadata or changing tracker configuration and
  conversation state.
- [x] Show the current reference or its absence on project lookup, start and resume, including
  when no workflow is active.
- [x] Preserve references through existing hook recovery and delegated workflow startup.
- [x] Retain CLI regressions that expose missing or incorrect lookup before implementation and
  demonstrate the completed behavior afterward.

## Accepted sources

[Lookup and testing decisions](../spec.md#lookup).

## Completion evidence

CLI observations and retained tests demonstrate correct references and
preserved workflow/tracker state. Existing navigator, session, compaction and deployment checks pass.
