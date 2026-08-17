# Note System

## Destination

Create a stateful `note-system` skill that preserves source evidence and integrates useful
knowledge into an Obsidian vault through source-specific procedures, beginning with YouTube.

## Current state

Complete.

## Progress

- Inspected and decomposed the expanded temporary root draft.
- Confirmed the existing `work-system` navigator is self-contained and manifest-driven.
- Confirmed `ffmpeg` and `ffprobe` are available in the current environment; `yt-dlp` is not.
- Kept this repository task focused on `note-system` without turning its implementation boundary
  into runtime routing guidance.
- Re-grounded the plan in the draft's accepted source fidelity, visual-material, vault-convention,
  approval, and completion rules.
- Derived separate question, curation, and ingestion workflows with shared discovery, integration,
  and review states. Ingestion alone starts with source acquisition.
- Recorded the accepted specification and two dependency-ordered implementation tickets.
- Added the discoverable stateful skill, manifests, state/procedure/format guidance, navigator,
  deterministic YouTube preparation CLI, and focused tests.
- Removed the decomposed temporary root draft.
- Corrected review findings so explicit ASR languages control decoding, auto-detected languages
  come from backend output, scene-image writes are capped before extraction, missing frames fail
  rather than silently truncating provenance, and every public navigation authorization is tested.
- Restored the general visual policy; kept visual sourcing exclusive to Acquisition and artifact
  assessment in Integration; and allowed bounded research in Discovery, Acquisition, and
  Integration with no chained research delegation.
- Fresh intent and engineering delivery reviews passed with no findings.

## Frontier

None; both implementation tickets are complete.

## Blockers

None.

## Accepted sources

- The original temporary root draft, removed after its accepted guidance was decomposed into the
  delivered skill.
- [`work-system`](../../skills/work-system/SKILL.md)

## Verification

- Repository branch: `main`
- Starting commit: `1b67767`
- `uv run ruff format --check .`: 10 files already formatted.
- `uv run ruff check .`: passed.
- `uv run mypy .`: 9 source files passed in strict mode after review corrections.
- `uv run python -m unittest`: 75 tests passed, including a real FFmpeg synthetic-media smoke test.
- Skill-creator `quick_validate.py skills/note-system`: `Skill is valid!`.
- Repository deploy dry-run discovers both `note-system` and `work-system`.
- Direct navigator starts, acquisition/procedure/format loads, and completion route passed.
- Direct missing-dependency execution returned the actionable `yt-dlp` error with status 2 and did
  not create its requested workspace.
- `git diff --check`: passed.

## Out of scope

- Installing or configuring Obsidian, Agent Client, `yt-dlp`, or system media tools.
- Bypassing access controls or DRM.
- Implementing source procedures other than YouTube in the first deliverable.

## Continuation

No continuation. The complete outcome is ready to preserve in repository history.
