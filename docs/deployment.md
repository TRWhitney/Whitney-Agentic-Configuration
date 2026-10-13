# Deployment

Run the deployment script from the repository root:

```bash
uv run python scripts/deploy.py
```

The script copies `config/global-agents.md`, the skills under `skills/`, and the
skills declared in `config/external-skills.json` into the Codex home. It records
content hashes in `.whitney-workflow-deployment.json` so later runs can update or
remove only content managed by this repository.

## YouTube setup

Configure YouTube acquisition from a host terminal with:

```bash
python3 scripts/configure_youtube.py
```

The script checks existing `yt-dlp`, `ffmpeg`, and `ffprobe` installations, browser-cookie
configuration, supported Deno/Node runtimes, and EJS solver availability. It offers detected
browser profiles and runtime paths when a selection is missing. Each configuration change shows
its destination and proposed options, then asks for confirmation. Declining leaves that setting
unchanged. Missing tool installations remain reported prerequisites.

An installed Obsidian Flatpak is checked automatically. Proposed remedies cover host-config
forwarding, read-only access to the selected cookie source, and PATH entries for existing tools.
Restart Obsidian after accepting a Flatpak permission or environment change. Use `--native-only`
to check just the host, or `--flatpak-app <app-id>` to select another Flatpak target.

Run a read-only check, optionally testing a particular video's access and format extraction:

```bash
python3 scripts/configure_youtube.py --check
python3 scripts/configure_youtube.py --check --url "VIDEO_URL"
```

Checks return status 1 for unresolved setup or access problems. A URL check downloads no media
and retains no metadata. Without a URL, a successful result confirms configuration and command
availability; browser-session validity and YouTube access remain untested. `--browser` and
`--runtime` can propose explicit yt-dlp specifications during interactive setup.
Configuration aliases and stdin-fed options require manual setup.

## External skills

Each external skill declaration names a Git submodule and the skill directory
inside it. A normal deployment initializes missing submodules at their committed
revisions. It does not follow upstream branches, which keeps deployments pinned
to the revisions recorded by this repository.

Update the external submodules and deploy their new skill versions with:

```bash
uv run python scripts/deploy.py --update-external-skills
```

This leaves each updated submodule revision as a repository change. Review and
commit that change to make the update reproducible in other clones. Add
`--dry-run` to inspect an update without changing the submodule or Codex home.

The deployment script will not overwrite an unowned or locally modified skill.
Use `--force` when intentionally replacing one, including the first deployment
of a skill that was previously installed by hand.

Remove every repository-managed skill while retaining the deployed global
instructions with:

```bash
uv run python scripts/deploy.py --purge-skills
```
