# Local transcription fallback

## Conclusion

Use `whisper.cpp` as the sole local speech-to-text fallback in the first YouTube release. It has a
native cross-platform runtime, works without a Python inference stack, supports CPU-only use, and
directly emits timestamped VTT plus detailed JSON. Keep it optional: detect a preinstalled
`whisper-cli` and an explicitly configured model, but never install a runtime or download a model
during ingestion.

Prefer transcript evidence in this order:

1. authored captions;
2. platform-generated captions in the video's original language;
3. local `whisper.cpp` transcription.

Label the selected origin. Preserve local ASR output without silently correcting it, retain its
VTT and full JSON in the temporary workspace during processing, and record the engine version,
model identity, detected language, and relevant decoding settings in source metadata. Local ASR is
generated evidence, not guaranteed verbatim text.

The preparation path should convert audio with `ffmpeg` to 16-bit, 16 kHz, mono PCM WAV, then ask
`whisper-cli` for transcription rather than translation. A configurable model is necessary because
accuracy, memory, language coverage, and speed vary materially. The `small` multilingual model is
a reasonable documented baseline, not a hard-coded requirement.

## Alternatives

- `faster-whisper` supports segment and word timestamps and may suit a later high-throughput
  provider. Its Python, CTranslate2, model-hub, and optional CUDA surface is broader, and it does not
  provide a first-party file-writing CLI.
- OpenAI Whisper provides a strong timestamped CLI but brings PyTorch, Python-version, tokenizer,
  and `ffmpeg` dependencies. It is a less portable default for a skill invoked from heterogeneous
  Agent Client environments.

## Decisive evidence

- [`whisper.cpp` v1.9.2 runtime and platform documentation](https://github.com/ggml-org/whisper.cpp/blob/v1.9.2/README.md)
- [`whisper.cpp` CLI output and timestamp options](https://github.com/ggml-org/whisper.cpp/blob/v1.9.2/examples/cli/README.md)
- [`whisper.cpp` model sizes and checksums](https://github.com/ggml-org/whisper.cpp/blob/v1.9.2/models/README.md)
- [`yt-dlp` extractor subtitle schema](https://github.com/yt-dlp/yt-dlp/blob/2026.07.04/yt_dlp/extractor/common.py#L323-L337)
- [`yt-dlp` subtitle selection](https://github.com/yt-dlp/yt-dlp/blob/2026.07.04/yt_dlp/YoutubeDL.py#L2918-L2973)
- [`yt-dlp` subtitle writer](https://github.com/yt-dlp/yt-dlp/blob/2026.07.04/yt_dlp/YoutubeDL.py#L4098-L4149)
- [`faster-whisper` v1.2.1](https://github.com/SYSTRAN/faster-whisper/blob/v1.2.1/README.md)
- [OpenAI Whisper v20250625](https://github.com/openai/whisper/blob/v20250625/README.md)

`yt-dlp` exposes authored subtitles and automatic captions separately and writes tracks supplied by
the extractor. It does not generate speech-to-text when both are absent. Auto-translated caption
variants can appear among automatic captions, so the procedure must avoid silently substituting a
translation for original-language evidence.

## Remaining uncertainty

No local ASR model guarantees exact wording or timing. Transcript quality depends on the source
audio, language, selected model, and quantization. This is represented as provenance and
uncertainty in the source record rather than hidden through transcript cleanup.
