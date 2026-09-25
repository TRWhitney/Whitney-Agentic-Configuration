# Review State

Validate the complete vault change, clean temporary artifacts after success, and give me one terse
change log and decision queue. Review does not correct source, integration, or discovery
defects; return to the responsible state.

## Inspect the result

Check the actual changed files and relevant rendered or structural behavior when available:

- the source note remains faithful and independent;
- concept notes retain the template's mandatory sections, or the fallback sections if no template
  exists;
- definitions created, corrected, consolidated, or relinked pass the definition checks in the
  verification procedure;
- wikilinks, citations, source references, timestamps, and attachment targets resolve;
- Markdown tables contain no aliased wikilinks or embeds with unescaped pipe characters;
- new notes and retained attachments are filed in appropriate folders with descriptive filenames,
  without files dumped in the vault root, duplicate attachments, or files left awaiting sorting;
- original-source and external-verification provenance remain distinguishable;
- selected visuals are useful, canonical, high quality, and source/timestamp linked;
- each image used in a knowledge note supplements nearby body text and also appears in that
  note's Image Gallery, with both embeds referencing the same canonical attachment;
- no unapproved rename, merge, deletion, archive, material rewrite, or risky structural change
  occurred;
- every substantive exclusion, novel synthesis, uncertain placement, discrepancy, and structural
  proposal is represented in the decision queue.

Run `python3 <skill-directory>/scripts/check_markdown_tables.py FILE [FILE ...]` and pass every
task-owned Markdown file explicitly. Do not derive the file set from Git. Exit status 1 reports a
table-link violation; exit status 2 reports invalid input or an unreadable file.

After the result passes, remove downloaded video, audio, bulk frames, contact sheets, and other
temporary preparation artifacts. Do not remove a failed workspace needed for diagnosis or retry.

After review and cleanup pass, complete the required commit procedure.

## Continue

Continue to completion when review passes, the commit procedure has no blocker, and the report
is ready. Return to integration when I
resolve a queued decision or a source record has a defect, acquisition when source evidence must be
prepared again, or discovery for missing scope evidence. Use the displayed preparation route when
a visual needs to be obtained or corrected. If curation introduces a source that must be preserved,
use the route to ingestion.
