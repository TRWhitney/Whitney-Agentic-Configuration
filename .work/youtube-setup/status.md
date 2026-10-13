# YouTube setup

## Destination

[Standalone terminal configuration and check command](spec.md).

## Current state

Complete. [Standalone setup](../../docs/deployment.md#youtube-setup) and
[ticket](tickets/01-configuration.md) are validated and reviewed.

## Verification

- `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest`: 142 tests passed.
- `.venv/bin/ruff format --check .` and `.venv/bin/ruff check --no-cache .`: passed.
- `.venv/bin/mypy --cache-dir <temporary-directory> .`: 17 source files passed.
- `python3 scripts/sync_navigators.py --check` and `git diff --check`: passed.
- Read-only URL checks passed on the host and inside Obsidian with a temporary PATH adjustment.
- Terminal setup displayed the exact PATH override and left it unapplied when declined. The
  default read-only check correctly reports the current Obsidian PATH issue.
- Regressions cover original-cookie preservation, output-hook isolation, and switching back to
  an earlier profile. The real yt-dlp diagnostic test passed without executing saved hooks.
- Independent intent and engineering reviews passed after correcting check isolation and
  effective-selection comparison. No blocking findings remain.
