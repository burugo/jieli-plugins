# Jieli Plugins

Plugins for syncing AI coding sessions to [Jieli](https://jieli.app).

## Claude Code Install

Add the marketplace in Claude Code:

```text
/plugin marketplace add jieliapp/plugins
```

Install the plugin:

```text
/plugin install claude-code@jieli
```

Then get an API key from [https://jieli.app](https://jieli.app) and configure it for Claude Code.

When Claude Code opens the plugin configuration screen, set:

```text
Jieli API key = your-jieli-api-key
```

Reload plugins:

```text
/reload-plugins
```

You can also set it through your shell environment before starting Claude Code:

```bash
export JIELI_API_KEY="your-jieli-api-key"
```

For self-hosted Jieli, also set:

```bash
export JIELI_BASE_URL="https://your-jieli.example.com"
```

## Codex Install

Add the marketplace in Codex:

```bash
codex plugin marketplace add jieliapp/plugins
```

Install the plugin:

```bash
codex plugin add codex@jieli
```

Then enable the plugin and trust its hooks with `/hooks`.

Set a Jieli API key in the environment used to start Codex:

```bash
export JIELI_API_KEY="your-jieli-api-key"
```

For self-hosted Jieli, also set:

```bash
export JIELI_BASE_URL="https://your-jieli.example.com"
```

## What It Does

- Syncs Claude Code sessions to Jieli threads.
- Syncs local Codex sessions to Jieli threads.
- Uploads pasted local images as Jieli attachments.
- Adds `Claude-Code-Thread-ID` trailers to Claude-created git commits.
- Adds best-effort `Jieli-Thread` trailers to simple Codex-created `git commit` commands.
- Provides the `jieli` skill for reading Jieli thread links from Claude Code.
- Provides the `jieli` skill for reading Jieli thread links from Codex.
- Redacts common secrets before upload.

## Development

```bash
make test
make validate
```
