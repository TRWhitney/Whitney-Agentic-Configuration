# GitHub tracking

Identify the destination repository from my request and the Git remote. Check access to its issues.
For a new project, save this at the settings path printed above, then resume the workflow:

```json
{"tracker": "github", "repository": "OWNER/REPO"}
```

Add `project_url` when I select a Projects board and check access to that board. For a project with
active local work, complete the conversion below before saving the setting.

# Convert local work to GitHub

Keep local tracking active until the published records have been checked.

1. List active local efforts, their tickets, decisions, dependencies, and accepted sources. Include
   older records needed by active work. Identify the destination repository and any selected board.
2. Save source IDs, content hashes, destination URLs, and progress in `.work/conversion.json`.
   Put each source ID in a hidden issue-body marker so an interrupted creation can be checked.
3. Match source IDs against open and closed GitHub issues. Create missing records and save each URL.
   Check uncertain responses and duplicate matches before creating another issue. Add hierarchy,
   blockers, statuses, and evidence.
4. Read back the published records and compare them with the local sources. Check for local edits
   made during conversion and include them before switching trackers.
5. Save the GitHub project setting. Keep local originals as history with issue links. Include the
   conversion record and local history in the outcome commit.

Report the destination, issue links, checks, and any unfinished conversion work.
