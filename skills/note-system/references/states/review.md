# Review State

Validate the complete vault change, delete temporary files after success, and give me one terse
change log and decision queue. Review does not correct source, integration, or discovery
defects; return to the responsible state.

## Inspect the result

Check the actual changed files and relevant rendered or structural behavior when available:

- the source note remains faithful and independent;
- concept notes retain the template's mandatory sections, or the fallback sections if no
  template exists;
- definitions created, corrected, consolidated, relinked, or tagged pass the definition checks
  in the verification procedure and have no tags unless I explicitly requested them;
- templates and plugin example notes have no tags, and plugin guidance remains untagged unless I
  explicitly requested tags for it;
- every substantial subject in each changed eligible note was checked against the established
  tag vocabulary, and every applicable tag was added with its established meaning, spelling, and
  nested form;
- each eligible note has multiple tags when it develops multiple substantial subjects covered by
  the vocabulary; each single-tag note has a specific explanation in the task result showing
  that a complete subject pass found no second applicable established tag;
- repeated single-tag results trigger another discovery and integration pass unless the
  individual explanations demonstrate that the notes each develop only one covered substantial
  subject;
- when backfilling tags, every note in the requested scope was considered, subject coverage and
  spelling are consistent, and excluded notes remain untagged;
- no unapproved new tag was applied, and proposed tags are in the decision queue;
- wikilinks, citations, source references, timestamps, and attachment targets resolve;
- Markdown tables contain no aliased wikilinks or embeds with unescaped pipe characters;
- new notes and retained attachments are filed in folders suited to their subjects with
  descriptive filenames, without files dumped in the vault root, duplicate attachments, or files
  left awaiting sorting;
- readers can distinguish the original source from facts checked elsewhere;
- selected visuals are useful, clear, saved once for reuse, and linked to their source or
  timestamp;
- image content was inspected, and relevant enabled plugins or core capabilities were used when
  they represent that content more usefully without losing valuable visual context or source
  evidence;
- each image used in a knowledge note supplements nearby body text and also appears in that
  note's Image Gallery, with both embeds referencing the same attachment file;
- no unapproved rename, merge, deletion, archive, material rewrite, or risky structural change
  occurred;
- every substantive exclusion, novel synthesis, uncertain placement, discrepancy, and structural
  proposal is represented in the decision queue.

Run `python3 <skill-directory>/scripts/check_markdown_tables.py FILE [FILE ...]` and pass every
task-owned Markdown file explicitly. Do not derive the file set from Git. Exit status 1 reports
a table-link violation; exit status 2 reports invalid input or an unreadable file.

Inspect temporary evidence before disposal; review does not require committing it or saving full
run histories unless I explicitly requested it. Keep concise findings in the existing record,
without reviewer transcripts, evidence manifests, or cleanup inventories.

After the result passes, remove downloaded video, audio, bulk frames, contact sheets, raw
metadata, and other temporary preparation files before commit or delivery unless I explicitly
requested retention. Ignoring outputs does not satisfy cleanup. Keep a failed workspace only
while needed for diagnosis or retry, then delete it. Keep requested source notes and selected
attachments.

After review and cleanup pass, complete the required commit procedure. For a Git-tracked vault,
apply it to the entire working tree, including my pre-existing changes and unrelated completed
work. Commit each completed result and verify the entire working tree is clean before completion
unless I explicitly instructed you to leave specific changes uncommitted. Changes outside your
task still need commits.

## Continue

Continue to completion when review passes, the commit procedure has no blocker, its final
repository-wide working-tree check passes or the vault is not Git-tracked, and the report is
ready. Return to integration when I resolve a queued decision, a source record has a defect, or
tag assignments need correction. Return to discovery when scope evidence, the subject inventory,
or relevant tag usage is incomplete. Return to acquisition when source evidence must be prepared
again. Use the displayed preparation route when a visual needs to be obtained or corrected. If
curation introduces a source that needs its own source note, use the route to ingestion.
