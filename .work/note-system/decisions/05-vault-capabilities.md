# 05 Vault convention and capability discovery

**Status:** resolved
**Blocked by:** none
**Type:** task

## Question

Should every new vault session discover templates, attachment locations, enabled plugins, commands,
and relevant examples afresh, or may `note-system` maintain a vault-local capability record for
reuse and refresh it when configuration changes?

## Answer

Discover the current vault's conventions and relevant enabled capabilities at the beginning of the
work that needs them. Prefer live Obsidian CLI discovery when available and fall back to read-only
inspection of vault configuration, templates, existing notes, attachment settings, plugin
manifests, and examples. Cache findings only within the active workflow; do not add a persistent
capability inventory to the vault because it can become stale and the draft does not authorize an
additional vault-maintenance artifact.

Use only capabilities whose availability and relevant syntax or command behavior are established.
When an installed and enabled plugin or core capability provides a block or feature that fits the
material, use it when it improves the note and fall back to plain Markdown when it does not. Do not
install, enable, disable, or configure plugins as part of `note-system`.

## Evidence

Agent Client does not pass an Obsidian add-on inventory to the agent. Current Obsidian CLI releases
can enumerate installed and enabled plugins, commands, themes, and snippets, while filesystem
inspection remains a fallback.

The original expanded draft required use of the vault's established template, section vocabulary,
tags, metadata conventions, and attachment hierarchy rather than inventing parallel conventions.
It was removed from the repository root after decomposition.
