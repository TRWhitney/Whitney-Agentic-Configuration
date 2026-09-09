# Deployment

Run the deployment script from the repository root:

```bash
uv run python scripts/deploy.py
```

The script copies `config/global-agents.md`, the skills under `skills/`, and the
skills declared in `config/external-skills.json` into the Codex home. It records
content hashes in `.whitney-workflow-deployment.json` so later runs can update or
remove only content managed by this repository.

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
