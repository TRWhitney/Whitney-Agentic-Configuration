# Compaction hooks

Run the setup command from the installed work-system directory for each application:

```sh
python3 scripts/compaction.py configure --application codex
python3 scripts/compaction.py configure --application claude
```

Use `--dry-run` to inspect the proposed configuration. Use `--config-home PATH` for a separate
application home. Setup preserves unrelated settings and hooks. It uses this installed copy of
work-system, so keep that directory in place.

Codex uses `CODEX_HOME`, or `~/.codex`, and writes `hooks.json`. Review and trust the hook through
Codex's `/hooks` interface before relying on it. Changed hooks may require renewed trust.
Claude Code uses `CLAUDE_CONFIG_DIR`, or `~/.claude`, and writes `settings.json`.

Both configurations run `compaction.py resume` for `SessionStart` with source `compact`. The
command reads the event's conversation ID and runs the navigator to restore that conversation's
workflow, substate and work-record link. Read the linked record before continuing. If a runtime
provides no hook output, use the manual resume command from `SKILL.md`.

Normal navigator commands identify Codex conversations through `CODEX_THREAD_ID` and Claude
Code conversations through `CLAUDE_CODE_SESSION_ID`. Automatic Claude recovery requires that
variable. State stays under the selected application home in `work-system/state/`.

Keep the existing work record current during work. The recovery hook reads saved state; it
cannot reconstruct decisions or findings that were never saved. It creates no replacement work
record and retains no transcript copy.

If restoration fails, Codex stops the turn and reports the error. Claude receives an instruction
to stop and report it. Native Claude failure handling has not been verified here.

See [Codex hooks](https://learn.chatgpt.com/docs/hooks#sessionstart),
[Claude Code hooks](https://code.claude.com/docs/en/hooks#sessionstart), and
[Claude session identity](https://code.claude.com/docs/en/env-vars).
