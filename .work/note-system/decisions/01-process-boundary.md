# 01 Process boundary and workflow shape

**Status:** resolved
**Blocked by:** none
**Type:** discussion

## Question

Should `note-system` route all substantive work performed in an Obsidian vault, or only source
ingestion and the resulting knowledge integration?

## Answer

`note-system` owns knowledge-oriented work in an Obsidian vault, including source ingestion,
knowledge integration, curation, and structural maintenance.

The instruction to keep Obsidian and plugin development in the normal work process governs this
repository task. It is not a runtime routing rule for `note-system`.

Keep source-specific acquisition and preparation inside `note-system` as procedures. The YouTube
procedure is the first such path and is not a separately discoverable skill.

## Evidence

The original expanded draft primarily specified source preservation and concept-centered
integration while also defining broader maintenance behavior such as splits, merges, tag
consolidation, structural suggestions, and terminology cleanup. It was removed from the repository
root after decomposition into the delivered skill.

I accepted the broad knowledge-vault boundary and clarified that the plugin-development constraint
governs implementation work, not the skill's runtime behavior.
