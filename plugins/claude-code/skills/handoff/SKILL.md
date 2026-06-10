---
name: handoff
description: "Compress the current Claude Code session into a handoff prompt for a fresh agent, embedding the current Jieli thread id so the next agent can read_thread for full context. Use for context handoff, continuing in a new session, or when the context window is filling up."
---

# Handoff

Compress the current session into a self-contained handoff prompt that a fresh agent can start from. The handoff embeds the current Jieli thread id, so when the compressed summary is not enough the next agent can read the full transcript with the `jieli` skill instead of losing context.

## When to Use

Use this skill when:

- The user asks to hand off, hand over, or pass the work to another agent or a new session.
- The user asks to compress, compact, or summarize the context to keep working past the context window.
- The user wants a prompt they can paste into a fresh Claude Code (or other) session to continue this work.

Do not use this skill to read or search other threads; that is the `jieli` skill.

## Inputs

- Optional next goal: what the next agent should do first. If the user did not give one, derive it from the most recent request and any open follow-ups in this conversation.
- Base URL from `JIELI_BASE_URL`, `CLAUDE_PLUGIN_OPTION_BASE_URL`, or `~/.config/jieli/settings.json`. If omitted, use `https://jieli.app`. No API key is needed; the handoff only builds a thread URL and never calls the Jieli API.

## Procedure

### 1. Detect the current thread id

The session is auto-synced to Jieli by the sync hooks, and its thread id is `T-<session_id>`. Resolve it from the newest transcript for the current working directory:

```bash
BASE_URL="${JIELI_BASE_URL:-${CLAUDE_PLUGIN_OPTION_BASE_URL:-https://jieli.app}}"
BASE_URL="${BASE_URL%/}"
eval "$(python3 - "$PWD" <<'PY'
import sys, re, pathlib
cwd = sys.argv[1]
proj = pathlib.Path.home() / ".claude" / "projects" / re.sub(r"[^A-Za-z0-9]", "-", cwd)
files = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
print(f'THREAD_ID="T-{files[0].stem}"' if files else 'THREAD_ID=""')
PY
)"
echo "THREAD_ID=$THREAD_ID"
```

- If `THREAD_ID` is non-empty, set `URL="$BASE_URL/threads/$THREAD_ID"` and `OUT="${TMPDIR:-/tmp}/handoff-$THREAD_ID.md"`.
- If `THREAD_ID` is empty, sync may not be configured. Still produce the handoff prompt, but tell the user the thread id could not be detected; ask them to configure the plugin (so `read_thread` works for the next agent) or to paste the thread id / Jieli URL manually. Use `OUT="${TMPDIR:-/tmp}/handoff-unknown.md"` and drop the "read thread" line.

### 2. Compose the handoff context

You already hold the full conversation, so write the context yourself; do not call a model. Extract relevant context for continuing this work, written from my perspective in the first person ("I did…", "I told you…").

Consider what the next agent needs based on the goal below. Questions that might be relevant:

- What did I just do or implement?
- What instructions did I already give that are still relevant (e.g. follow patterns in the codebase)?
- What files did I say are important or am I actively working on (and should continue)?
- Did I provide a plan or spec that should be included?
- What constraints or preferences did I state (libraries, patterns, conventions)?
- What important technical details did I discover (APIs, methods, patterns)?
- What caveats, limitations, or open questions remain?

Rules for the relevant information:

- Extract only what matters for the specific goal. Skip questions that are not relevant. Pick a length appropriate to the complexity.
- Focus on capabilities and behavior, not a file-by-file changelog. Avoid excessive implementation details (variable names, storage keys, constants) unless critical.
- Plain text with bullets. No markdown headers, no bold/italic, no code fences. Use workspace-relative paths for files.

Rules for the relevant files:

- Workspace-relative paths only. Maximum 10. Put the most important files first. Directories are allowed when several files under them matter. Do not invent files or use absolute paths.

### 3. Assemble, write, and print

Assemble the handoff prompt in this exact shape (omit the "read thread" line and the `(URL)` if the thread id was not detected):

```
Continuing work from Jieli thread <THREAD_ID> (<URL>).
When you lack specific information, use the jieli skill to read thread <THREAD_ID>.

Relevant files: <path1> <path2> <path3> …

<relevant information bullets>

Next: <next goal / open follow-ups>
```

Write it to the temp file and confirm, substituting the composed body:

```bash
cat > "$OUT" <<'EOF'
<assembled handoff prompt>
EOF
echo "Wrote handoff to $OUT"
```

Then print the same handoff prompt in a fenced block in your reply so the user can copy it directly, and tell them the saved file path.

## Output

- A ready-to-paste handoff prompt (printed and saved to `$OUT`).
- The next agent pastes it into a fresh session; if it needs more than the summary, it uses the `jieli` skill to read `<THREAD_ID>` for the full transcript.

## Notes & Safety

- The current turn is uploaded to Jieli by the Stop/SessionEnd hooks after this turn ends, so `read_thread` covers history up to the previous sync. The handoff summary itself already carries the key context, so this gap is fine.
- Never include API keys, secrets, or tokens in the handoff prompt, even if they appear in the conversation.
