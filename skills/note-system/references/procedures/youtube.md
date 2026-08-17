# YouTube Acquisition Procedure

Acquire a YouTube video's transcript and representative visual evidence with the bundled
`scripts/prepare_youtube.py` tool. This procedure does not bypass access controls or authorize use
outside the source's applicable terms.

## Preflight and prepare

Choose an explicit empty temporary workspace outside the permanent note and attachment hierarchy.
Run the tool with the video URL and workspace. It requires `yt-dlp`, `ffmpeg`, and `ffprobe` on
`PATH`. Do not install them automatically.

Transcript priority is authored captions, original-language platform automatic captions, then
local transcription. For the fallback, supply both a preinstalled `whisper-cli` and an explicit
model path. Do not implicitly download a model. If the video's original language is ambiguous,
specify it rather than silently choosing a translated caption track.

```text
python3 <skill-directory>/scripts/prepare_youtube.py <url> --workspace <empty-directory>
python3 <skill-directory>/scripts/prepare_youtube.py <url> --workspace <empty-directory> \
  --language <language-code> --whisper-model <model-path>
```

The tool leaves a preparation manifest, raw source metadata, selected transcript evidence, a
Markdown transcript body, the downloaded video, interval frames, scene frames, and paginated
contact sheets. On failure it keeps the workspace and reports the failing boundary.

## Prepare source evidence

Inspect the manifest and transcript evidence. Preserve the transcript-origin label and local ASR
engine/model provenance. Do not clean automatic or local ASR text into apparent authored wording.

Do not rely solely on the transcript to decide whether something visually useful occurred. Inspect
both storyboard families alongside the transcript sufficiently to discover diagrams, slides,
comparisons, on-screen examples, object demonstrations, spatial relationships, or other meaningful
material that may never have been verbally described. Open promising frames at useful resolution
and inspect neighboring moments when motion, occlusion, or a transition makes a sample ambiguous.
Record useful candidate timestamps and keep the sampled frames temporary.

## Result

Include the preparation-manifest path, prepared transcript path, transcript origin and limitations,
visual coverage and candidates, and temporary workspace path. Keep the workspace until the complete
result passes review.
