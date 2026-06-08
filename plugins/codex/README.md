# Jieli Codex Sync

Sync local Codex sessions to Jieli threads, redact common secrets before upload, provide a `jieli` skill for reading synced threads, and add best-effort `Jieli-Thread` trailers to Codex-created git commits.

## Configuration

Set a Jieli API key in the environment used to start Codex:

```bash
export JIELI_API_KEY="your-jieli-api-key"
```

Hosted Jieli defaults to `https://jieli.app`. For self-hosted Jieli, also set:

```bash
export JIELI_BASE_URL="https://your-jieli.example.com"
```

## Hooks

Codex discovers plugin hooks from `hooks/hooks.json`. After installing or enabling the plugin, review and trust the bundled hooks with `/hooks`.

The plugin syncs on:

- `SessionStart`
- `UserPromptSubmit`
- `PreCompact`
- `PostCompact`
- `Stop`

The `PreToolUse(Bash)` hook attempts to rewrite simple `git commit` commands by appending:

```text
--trailer "Jieli-Thread: https://jieli.app/threads/T-..."
```

It only rewrites simple commands that parse as `git commit`. It does not rewrite commands containing shell chaining, pipes, heredocs, subshells, backgrounding, or multiple lines. It does not install Git hooks and does not affect commits made outside Codex.

## Local State

Session mappings are stored at:

```text
~/.jieli/codex-sessions.json
```

Hook errors are appended to:

```text
~/.jieli/hooks.log
```

## Development

```bash
python3 -m unittest plugins/codex/tests/test_plugin_scripts.py
python3 /path/to/plugin-creator/scripts/validate_plugin.py plugins/codex
```
