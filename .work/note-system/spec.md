# Stateful Obsidian Knowledge-Vault Process

## Problem Statement

The repository has a comprehensive but monolithic draft for agents incorporating sources into an
Obsidian vault. It is an untracked root file, does not participate in skill discovery, loads every
instruction regardless of the current task, and does not provide resumable workflow boundaries or
deterministic source preparation. Agent Client supplies the vault working directory and note
context, but it does not inventory Obsidian add-ons for the agent.

## Solution

Create one implicitly discoverable `note-system` skill for knowledge-oriented work in Obsidian
vaults. Keep its root concise and route prompts through manifest-defined workflows with a navigator
equivalent to the established `work-system` interface:

- `question`: `discovery` -> `answer` -> complete;
- `curate`: `discovery` -> `integration` -> `review` -> complete;
- `ingest`: `acquisition` -> `discovery` -> `integration` -> `review` -> complete.

Curation can move from integration or review to `visual-preparation`, then return to integration
for assessment. Any curation state can route a newly introduced source to `ingest.acquisition`.

Only the active state and explicitly selected procedures or formats should enter context. Workflow
manifests classify procedure and format availability, and the navigator provides their load
commands; state and procedure prose do not duplicate that dispatch responsibility.

Discovery identifies the vault root, the requested scope, relevant conceptual neighborhood,
established templates and examples, attachment location, naming/link/tag/metadata conventions, and
capabilities suggested by the prompt, relevant vault examples, or available source evidence.
Prefer live Obsidian CLI evidence; fall back to read-only vault inspection. Never install, enable,
disable, or configure an Obsidian add-on and do not persist a capability inventory. When ordinary
vault inspection leaves a bounded factual question whose answer would materially improve
Discovery, an allowed research procedure can investigate it without changing the vault or deciding
how knowledge should be organized. A fresh-context subagent may handle suitable external research,
but an agent that received delegated work performs its own research rather than delegating again.
The same bounded research procedure is allowed during Acquisition and Integration when factual
investigation would materially improve the active work.

Acquisition prepares source evidence and newly sourced visual candidates in an explicit temporary
workspace without writing to the vault. It precedes discovery so the later states can work from the
acquired material rather than predict what it will contain. Source-specific procedures own the
inspection needed to discover evidence carried by their source. Visual sourcing separately finds,
captures, extracts, or creates requested candidates from source media, reference imagery, or
generation without deciding whether an artifact belongs in the vault. It can also correct a
temporary copy of a candidate for reassessment. Curation uses its visual-preparation state for this
work without requiring a new source record unless an independent source is introduced.

When introducing a source, integration first preserves an independent, faithful source record,
then changes knowledge notes.
Metadata may be normalized, but the source body retains wording, order, qualifications, and useful
timestamps without summary, deduplication, restructuring, inline annotation, silent correction, or
later-source revision. Obvious filler may be ignored during knowledge integration but remains in
the archive.

The first acquisition procedure accepts one YouTube URL. A deterministic standard-library Python
tool should:

- preflight external commands before changing the vault;
- use `yt-dlp` to inspect metadata, download the video, and prefer authored captions followed by
  original-language platform automatic captions;
- use an explicitly configured, preinstalled `whisper.cpp` CLI and model only when captions are
  absent, marking this output as local ASR and preserving its backend/model provenance;
- stop with actionable setup guidance before writing a source note when no transcript path exists;
- use `ffmpeg`/`ffprobe` to extract regular-interval and scene-change frames, make paginated contact
  sheets, and write a machine-readable manifest connecting frames to timestamps;
- prepare a Markdown transcript body without editorially altering the selected caption/ASR cues;
- use an explicit temporary workspace, preserve it for diagnosis on failure, and remove it after
  successful review.

The agent does not rely solely on the transcript to decide whether something visually useful
occurred. It inspects both regular and scene-derived sheets alongside the transcript sufficiently
to discover diagrams, slides, comparisons, examples, demonstrations, or other meaningful material
that may not have been verbally described. Bulk frames, sheets, audio, and downloaded video remain
temporary.

Integration treats the vault as a concept network rather than a source-summary collection. It
prefers fitting material into existing conceptual scope and creates a note only for a concept with
independent explanatory value, substance, and practical importance. It preserves useful broad and
narrow relationships, meaningful overlap, existing viewpoints of uncertain provenance, claim
type/strength/scope, disagreements, terminology, and source traceability. It uses tailored prose in
multiple relevant notes rather than identical duplication, contextually useful wikilinks, existing
tags and section vocabulary, minimal purposeful metadata, and the established note template.
When an installed and enabled Obsidian plugin or core capability provides blocks or features that
fit the material, integration uses its verified syntax when it improves the note and otherwise
falls back to plain Markdown.

Visuals are used sparingly but proactively when they materially improve understanding. Suitable
visuals include source screenshots that preserve diagrams, slides, comparisons, examples, or
demonstrations; reference photographs when visual distinction matters; and occasional generated
informational diagrams or infographics when they explain something more effectively than prose.
Decorative imagery, images added merely because they are available, and unnecessary image
saturation are avoided. Visibly watermarked content is not used.

Integration assesses available visual artifacts without acquiring new ones. Assessment judges a
candidate's material value, fidelity, factual support, context, legibility, quality, provenance,
usage constraints, and canonical reuse without obtaining or changing the artifact. A suitable
artifact is then retained once in the established attachment hierarchy, with source and timestamp
provenance where appropriate, and reused across notes rather than duplicated.

Routine low-risk, additive, and reversible changes proceed autonomously. The agent completes all
safe work, then batches decisions requiring approval: substantive exclusions, novel synthesis
presented as established knowledge, material rewrites of specifically worded prose, note renames,
merges, deletion/archive, and structural changes that risk existing intent. Minor uncertainty uses
the safest reversible interpretation and is reported afterward. Review can return to integration
after a decision is resolved.

Review verifies source fidelity, link and attachment targets, retained standard sections, template
and metadata conformity, citation/source distinctions, selected-visual provenance, absence of
unintended note operations, and temporary-artifact cleanup. Completion is a terse change log and
decision queue containing only material creations, updates, discrepancies, suggestions,
uncertainties, syntheses, exclusions, and approval requests.

## User Stories

1. I want an agent in Agent Client to discover the right knowledge-vault process, so that vault
   work follows established conventions.
2. I want each source archived faithfully before its ideas are integrated, so that I can
   distinguish what the source said from what the vault knows.
3. I want a YouTube video inspected through transcript and representative frames, so that diagrams,
   comparisons, examples, and demonstrations are not lost.
4. I want safe curation to proceed without repeated interruption, so that only material judgments
   reach me in a concise review.
5. I want vault questions to remain read-only, so that asking for understanding does not implicitly
   authorize note changes.

## Implementation Decisions

- Follow [Process boundary and workflow shape](decisions/01-process-boundary.md).
- Follow [Source record and transcript fidelity](decisions/02-source-record.md).
- Follow [Transcript fallback](decisions/03-transcript-fallback.md) and its
  [research](research/transcription-fallback.md).
- Follow [Visual artifact lifecycle](decisions/04-visual-artifacts.md).
- Follow [Vault convention and capability discovery](decisions/05-vault-capabilities.md) and the
  [Agent Client research](research/agent-client-capabilities.md).
- Follow [Workflow model and approval loop](decisions/06-workflow-model.md).
- Reuse the established manifest and standard-library navigator architecture without coupling the
  two skills at runtime.
- Source-specific paths are internal procedures, not separately discoverable skills.
- External media and ASR tools are detected dependencies. The skill never installs them or
  downloads a speech model implicitly.

## Testing Decisions

- Extend repository structure tests so both root skills are discoverable while nested references
  remain non-discoverable and all local Markdown links resolve.
- Validate every note-system workflow manifest, state transition, procedure/format authorization,
  and exact navigator resume command through the navigator's public CLI.
- Exercise YouTube preparation with temporary directories and controlled fake executables for
  metadata, caption selection, failure behavior, command construction, transcript conversion, and
  manifest generation. Test pure caption and frame-selection behavior directly.
- When available, use the installed `ffmpeg` to run a small synthetic-media smoke test; absence of
  optional real network/media dependencies must not make the repository suite fail.
- Run skill validation, formatting, lint, typing, the full unit suite, and deploy dry-run checks.

## Out of Scope

- Building or modifying Obsidian or Obsidian plugins as part of this repository task.
- Installing or configuring Agent Client, Obsidian, community plugins, `yt-dlp`, `ffmpeg`,
  `whisper.cpp`, or speech models.
- Bypassing access controls or DRM.
- A general-purpose media library or permanent frame/storyboard archive.
- First-release acquisition procedures for articles, books, papers, or conversations.
- Automatic destructive or identity-changing note operations.

## Further Notes

The root draft is an accepted planning source, not a deliverable. Remove it from the repository root
only after its operative guidance is represented by the skill and the completed work record.
