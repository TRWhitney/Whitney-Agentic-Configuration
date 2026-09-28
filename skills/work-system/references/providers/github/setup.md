# GitHub tracking

Identify the destination repository from my request and the Git remote. Check access to its issues.
For a project without a Git checkout, initialize the repository and rerun this command first.
For a new project, save this at the settings path printed above, then resume the workflow:

```json
{"tracker": "github", "repository": "OWNER/REPO"}
```

Add `project_url` when I select a Projects board and check access to that board. If repository
tracking records remain, complete the conversion below, even if GitHub is already selected.

# Convert local work to GitHub

Keep each source until its destination content and links have been checked.

1. Inventory existing efforts and their accepted sources. Identify planning maps, research, and
   prototype notes to place in repository documentation. Follow its existing layout, or use
   `docs/planning/`, `docs/research/`, and `docs/prototypes/`. Keep documentation already there in place.
2. Save source IDs, content hashes, destination paths or URLs, and progress in
   `work-system-conversion.json` beside the settings file in Git metadata. Move any existing
   conversion ledger there and reuse its progress. Give tracking records hidden issue-body markers
   with their source IDs so an interrupted creation can be checked.
3. Copy misplaced documentation to its destination and update links. Match tracking source IDs
   against open and closed GitHub issues. Publish the specification and
   effort status in the parent issue, including its `Continuation` section. Publish decision and
   implementation tickets as sub-issues. Reuse existing matches and save each URL. Check uncertain
   responses and duplicate matches before creating another issue. Preserve hierarchy, blockers,
   statuses, and evidence links. Link the repository documentation rather than copying it into issues.
4. Read back the issues and destination documents and compare them with their sources. Check for
   edits made during conversion and include them before switching trackers. Verify rewritten links.
5. Save the GitHub project setting in Git metadata. Remove only source copies whose content and
   links have been verified at their destinations, including any superseded settings file.
   Remove emptied `.work` directories. Commit documentation moves and tracked file deletions with
   the outcome. Keep the conversion ledger in Git metadata. Report any remaining paths as unfinished
   conversion work.

Report the destination, issue links, checks, and any unfinished conversion work.
