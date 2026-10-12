# YouTube Acquisition Procedure

Acquire a YouTube video's transcript and representative visual evidence with the bundled
`scripts/prepare_youtube.py` tool. This procedure does not bypass access controls or authorize use
outside the source's applicable terms.

## Preflight and prepare

Choose an explicit empty temporary workspace outside the vault or checkout.
Run the tool with the video URL and workspace. It requires `yt-dlp`, `ffmpeg`, and `ffprobe` on
`PATH`. Do not install them automatically.

Use the user's cached browser login through yt-dlp's local configuration. The preparation tool
loads that configuration for metadata inspection, captions, and video downloads. Read the
existing yt-dlp configuration files in the acquisition environment before deciding whether a
cookie source is missing. An existing `--cookies-from-browser` entry selects the browser and
profile; an existing `--cookies` entry selects a cookie file. Use the configured source and run
the preparation tool without asking the user to select it again. If acquisition fails, diagnose
the reported error with that source. Ask which browser and profile contains the intended login
only after checking the configuration and confirming that no cookie source is configured.

The user configuration file is `${XDG_CONFIG_HOME}/yt-dlp/config` on Linux/macOS, with
`XDG_CONFIG_HOME` defaulting to `~/.config`, or `%APPDATA%\yt-dlp\config` on Windows. Preserve
existing options when adding the selected cookie source:

```text
--cookies-from-browser <browser>
--cookies-from-browser "<browser>:<absolute-profile-path>"
```

Use one of these entries. An explicit profile path selects the intended profile when several
exist. Zen uses yt-dlp's `firefox` reader with the absolute path to the Zen profile directory;
`firefox` alone searches Firefox's own profiles. Installed browsers and cookie databases are
candidates, not proof of the intended account. Keep the selected path in local configuration.

See [yt-dlp configuration](https://github.com/yt-dlp/yt-dlp#configuration) for supported locations
and [browser cookie options](https://github.com/yt-dlp/yt-dlp#filesystem-options) for browser,
profile, and container syntax.

For sandboxed acquisition, check configuration discovery and profile access inside the process's
runtime environment. Flatpak sets an app-specific `XDG_CONFIG_HOME` and excludes other apps'
`~/.var/app` directories even with home-directory access. The app's local yt-dlp configuration
can load an existing host configuration with `--config-locations "<absolute-config-path>"`.
Reading a browser profile in another app's directory also requires filesystem access to that
profile; read-only access is sufficient. A configured profile that is hidden by the sandbox is
an access problem, not a missing browser selection. See
[Flatpak filesystem access](https://docs.flatpak.org/en/latest/sandbox-permissions.html#filesystem-access).

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

For platform automatic captions, the tool removes confirmed rolling-display repeats from the
Markdown transcript using caption timing and structure. It preserves spoken repetition and
ambiguous cases, and leaves the raw caption evidence unchanged. Authored captions and local ASR
do not receive this cleanup.

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
result passes review, then delete disposable preparation outputs before delivery unless I
explicitly requested retention. Keep a failed workspace only while needed for diagnosis or retry.
