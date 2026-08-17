# Agent Client and vault capability discovery

## Conclusion

Agent Client does not provide an ACP agent with an inventory of installed or enabled Obsidian core
plugins, community plugins, themes, snippets, or their capabilities. It provides the vault as the
working directory, terminal support, note-oriented context, and rendering of agent-side tool calls.
Skills, MCP servers, filesystem access, and discovery remain agent-side capabilities.

`note-system` must therefore discover only relevant live vault capabilities. Prefer the official
Obsidian CLI when it is installed and enabled; otherwise inspect `.obsidian` configuration,
manifests, templates, settings, and representative notes read-only. Discovery must not infer that
an installed plugin is enabled or that an enabled plugin exposes a particular command without
evidence.

## Decisive evidence

- [Agent Client ACP capabilities](https://rait-09.github.io/obsidian-agent-client/reference/acp-support.html#client-capabilities)
- [Agent Client session creation](https://github.com/RAIT-09/obsidian-agent-client/blob/55dc9e3a3d5bfa3e2b0535585e0ea096689eec85/src/acp/acp-client.ts#L498-L505)
- [Agent Client MCP behavior](https://rait-09.github.io/obsidian-agent-client/usage/mcp-tools.html)
- [Agent Client prompt injection](https://rait-09.github.io/obsidian-agent-client/usage/prompt-injection.html)
- [Agent Client note context](https://rait-09.github.io/obsidian-agent-client/usage/mentions.html)
- [Agent Client vault working directory](https://github.com/RAIT-09/obsidian-agent-client/blob/55dc9e3a3d5bfa3e2b0535585e0ea096689eec85/src/ui/ChatPanel.tsx#L229-L243)
- [Official Obsidian CLI plugin commands](https://github.com/obsidianmd/obsidian-help/blob/master/en/Extending%20Obsidian/Obsidian%20CLI.md#plugins)
- [Official Obsidian CLI theme and snippet commands](https://github.com/obsidianmd/obsidian-help/blob/master/en/Extending%20Obsidian/Obsidian%20CLI.md#themes-and-snippets)

This Agent Client conclusion is pinned to release 0.12.1, commit `55dc9e3`, released 2026-08-14.
The current official Obsidian CLI requires a compatible recent Obsidian installation, CLI support
enabled in settings, and a running or launchable Obsidian application.
