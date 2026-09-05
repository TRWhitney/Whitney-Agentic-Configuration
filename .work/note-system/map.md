# Note System

## Destination

Deliver a discoverable, stateful skill that can safely process source material into an Obsidian
knowledge vault. The first complete source path accepts a YouTube URL, preserves a transcript-based
source note, inspects representative visual frames, and integrates selected knowledge and visuals
under the vault's established conventions.

## Notes

The expanded draft is an input to decomposition, not the final root skill. Core invariants should
remain concise; state guidance, source-specific acquisition, analysis procedures, output formats,
and deterministic media preparation should load only when relevant.

## Decisions so far

- [Process boundary and workflow shape](decisions/01-process-boundary.md): `note-system` owns
  knowledge-oriented vault work and source procedures; repository implementation boundaries do not
  become runtime routing rules.
- [Source record and transcript fidelity](decisions/02-source-record.md): Preserve the transcript
  as faithful source evidence; transform only format control data without rewriting or restructuring
  the source body.
- [Transcript fallback](decisions/03-transcript-fallback.md): Prefer authored and platform captions,
  then use an explicitly configured local `whisper.cpp` backend without installing at ingestion
  time.
- [Visual artifact lifecycle](decisions/04-visual-artifacts.md): Prepare visuals during ingestion's
  acquisition or curation's visual preparation, then assess them during integration. Keep
  candidates temporary and retain only useful, canonical, provenance-linked visuals in the vault.
- [Vault convention and capability discovery](decisions/05-vault-capabilities.md): Discover live
  vault conventions and capabilities when needed without creating a persistent inventory.
- [Workflow model and approval loop](decisions/06-workflow-model.md): Route questions, curation,
  and ingestion separately; ingestion acquires its source before entering shared discovery,
  integration, review, and approval behavior.
- The first deliverable includes one complete YouTube ingestion path; other source types remain
  future procedures.

## Not yet specified

- None.

## Out of scope

- A general-purpose media library or downloader.
- Automatic installation, enablement, or configuration of Obsidian plugins.
- Building or modifying Obsidian or Obsidian plugins as part of this repository task.
- Procedures for articles, books, research papers, or conversations in the first deliverable.
