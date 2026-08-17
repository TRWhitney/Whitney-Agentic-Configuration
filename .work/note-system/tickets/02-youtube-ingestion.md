# 02 YouTube acquisition and visual inspection

**What to build:** A complete YouTube acquisition procedure that prepares faithful transcript
evidence, visually inspectable interval/scene storyboards, and provenance-linked evidence for the
core discovery and integration process without retaining bulk media.

**Blocked by:** [01 Core note-system process](01-core-process.md)

**Status:** complete

- [x] The ingestion workflow selects the YouTube procedure, acquires source evidence before
  discovery, and keeps temporary source preparation distinct from vault integration.
- [x] A deterministic Python CLI preflights `yt-dlp`, `ffmpeg`, and `ffprobe`; uses authored,
  original-language automatic, then configured local `whisper.cpp` transcripts in that order; and
  never installs or downloads dependencies.
- [x] A no-caption/no-ASR case fails before vault mutation with an actionable message, while a
  failed preparation preserves the explicit temporary workspace for diagnosis.
- [x] Transcript preparation retains cue order, wording, qualifications, and useful timestamps,
  records transcript origin/ASR provenance, and avoids editorial cleanup.
- [x] Regular-interval and scene-change frames, paginated contact sheets, and a timestamp manifest
  let the source-specific procedure inspect visual content alongside the transcript without
  making the general sourcing procedure specific to YouTube.
- [x] Acquisition-exclusive visual sourcing can turn a useful video candidate into a suitable
  temporary artifact or obtain candidates through other acquisition paths. Independent assessment
  during integration decides whether an artifact belongs in the vault. Accepted source visuals
  remain source/timestamp-linked, high-quality canonical attachments, and bulk temporary artifacts
  are removed after success.
- [x] Controlled unit/integration tests cover caption selection, transcript conversion, external
  command boundaries, frame selection/manifests, failure behavior, and the full workflow route.
- [x] The accepted draft is removed from the repository root after its content is represented, and
  full validation/deployment checks pass.

## Accepted sources

- [Specification](../spec.md)
- [Source record](../decisions/02-source-record.md)
- [Transcript fallback](../decisions/03-transcript-fallback.md)
- [Visual lifecycle](../decisions/04-visual-artifacts.md)
- [Transcription research](../research/transcription-fallback.md)
- [Core process ticket](01-core-process.md)

## Completion evidence

- Focused preparation tests pass for authored/automatic caption selection, ambiguous language
  refusal, faithful VTT conversion, no-caption failure, accurate local `whisper.cpp` language and
  model provenance, bounded scene-image writes, missing-frame failure, and controlled end-to-end
  manifest preparation.
- Installed FFmpeg 4.4.2 directly produced interval frames, scene-change frames, and a contact sheet
  from synthetic video.
- Full repository revalidation passed with 75 tests; fresh intent and engineering delivery reviews
  passed with no findings.
