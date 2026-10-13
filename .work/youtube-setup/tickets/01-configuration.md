# 01 Interactive YouTube configuration

**What to build:** A standalone terminal setup and check command for native yt-dlp and an optional
Obsidian Flatpak target, with confirmed configuration remedies and an optional source-access test.

**Blocked by:** none

**Status:** complete

- [x] Existing browser and runtime selections are honored; missing selections have useful choices.
- [x] Declining a remedy leaves configuration and permissions unchanged.
- [x] Accepted remedies preserve unrelated options and do not duplicate themselves on repeat runs.
- [x] Flatpak checks cover configuration discovery, selected-cookie access, and executable PATH.
- [x] Check mode is read-only and returns failure when prerequisites remain unresolved.
- [x] Optional URL validation reports access without retaining metadata or downloading media.
- [x] Focused tests, repository checks, direct configuration checks, and independent review pass.
- [x] Deployment documentation describes the standalone command.

## Accepted sources

- [Specification](../spec.md)
- [YouTube procedure](../../../skills/note-system/references/procedures/youtube.md)
- [yt-dlp configuration](https://github.com/yt-dlp/yt-dlp#configuration)
- [EJS setup](https://github.com/yt-dlp/yt-dlp/wiki/EJS)
- [Flatpak filesystem permissions](https://docs.flatpak.org/en/latest/sandbox-permissions.html#filesystem-access)

## Completion evidence

25 focused cases cover configuration, prompts, environment-specific command checks, immutable
cookie files, isolated output hooks, effective profile changes, and preserved UTF-16 settings.
The full suite passed with 142 tests. Formatting, lint, strict typing, navigator drift, and diff
checks passed. Direct host and Flatpak URL checks passed; a real yt-dlp help diagnostic preserved
a fixture cookie file and ignored saved execution hooks. The terminal PATH remedy respected
refusal. Independent intent and engineering correction reviews passed with no blocking findings.
