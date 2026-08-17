# 03 Transcript fallback

**Status:** resolved
**Blocked by:** none
**Type:** research

## Question

What reliable local transcription path best preserves source-note fidelity when neither authored
nor automatic captions are available, and should it be included in the first YouTube procedure?

## Answer

Include a local `whisper.cpp` fallback in the first YouTube procedure. Prefer authored captions,
then original-language platform automatic captions, then local ASR. Detect a preinstalled
`whisper-cli` and an explicitly configured model; do not install dependencies or download models
during ingestion. If neither captions nor a configured local backend are available, stop before
writing a source note and report the exact setup requirement.

Use `ffmpeg` to produce the audio format required by the backend. Preserve timestamped VTT and full
JSON as temporary evidence, identify the transcript origin and model in source metadata, and never
silently clean local ASR into apparent verbatim source text.

## Evidence

[`yt-dlp` retrieves available subtitle tracks and automatic captions; it is not itself a
speech-to-text engine](../research/transcription-fallback.md). `whisper.cpp` provides the smallest
first-release runtime surface among the researched local options while producing the required
timestamped formats on Linux, macOS, and Windows.
