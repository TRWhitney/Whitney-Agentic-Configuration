# YouTube setup

## Problem statement

YouTube acquisition depends on local browser cookies, an enabled JavaScript runtime, EJS solver
scripts, media commands, and access from the environment running Obsidian. Settings can work on
the host while remaining undiscoverable or inaccessible inside Flatpak.

## Solution

A standalone repository CLI checks the setup and offers configuration remedies through terminal
prompts. It preserves existing options and uses saved selections. Each write or Flatpak override
requires confirmation after displaying the proposed change. A read-only check mode reports
unresolved issues without prompting or changing settings.

## User stories

- A configuring user can select an existing browser profile and supported runtime, enable the
  official EJS solver, and configure an installed Obsidian Flatpak environment.
- A user can rerun setup without duplicate settings or repeated changes.
- A user can optionally test a YouTube URL without retaining source metadata or downloading media.

## Implementation decisions

- Use a standard-library Python script separate from skill deployment and source preparation.
- Discover conventional browser profiles and installed Deno/Node executables; also accept explicit
  selections. Profile presence does not establish the intended account.
- Check effective yt-dlp configuration and command execution. Preserve unrelated configuration.
- Inspect saved options through yt-dlp's help diagnostics. Execute checks with controlled
  options rather than saved output hooks. Cookie-file probes isolate the input in a temporary
  copy and delete it on exit; the original file remains unchanged.
- For Flatpak, offer host-config forwarding, access to the selected cookie location, and PATH
  repair for existing executable directories. Validate the resulting sandbox and report restarts.
- Report absent dependencies and unsupported environments as actionable prerequisites. System
  package installation, browser authentication, and Obsidian add-on configuration are outside scope.

## Testing decisions

Test declined remedies, existing settings, ambiguous browser candidates, runtime compatibility,
configuration forwarding, narrow permissions, PATH repair, inaccessible paths, repeat runs, and
network-probe failure through controlled external commands and temporary filesystem fixtures.
Run the read-only CLI on the current host and Obsidian sandbox with the known video URL.

## Out of scope

Vault writes, media downloads, credential exports, and guarantees about future YouTube behavior.
