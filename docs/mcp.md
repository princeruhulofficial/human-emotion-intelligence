# HEI MCP Server

HEI can run as a **Model Context Protocol (MCP)** server so that AI clients (Claude Desktop, Cursor, Windsurf, etc.) can call it as a set of tools.

## Available Tools

| Tool | Description |
|------|-------------|
| `hei_analyze` | Full pipeline: Emotion + Intent + Strategy |
| `hei_detect_emotion` | Detect primary / secondary / hidden emotions |
| `hei_detect_intent` | Detect emotional intent |
| `hei_get_mood_shift` | Detect mood changes in a session |
| `hei_evaluate_response` | Score a generated reply against a strategy |

## Installation

```bash
pip install -e ".[mcp]"
# or
pip install mcp
```

## Running the Server

```bash
export OPENAI_API_KEY=sk-...
# optional
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export HEI_MODEL=google/gemma-2-9b-it:free

python -m hei.mcp_server
```

## Claude Desktop Configuration

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hei": {
      "command": "python",
      "args": ["-m", "hei.mcp_server"],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "HEI_MODEL": "google/gemma-2-9b-it:free"
      }
    }
  }
}
```

## Cursor / Windsurf

Most MCP-compatible editors allow you to add a custom server with the same command:

```bash
python -m hei.mcp_server
```

Make sure the environment variables are set.

## Example Usage (from an Agent)

1. Call `hei_analyze` with the user message (and optional `session_id`).
2. Read the returned `strategy.suggested_approach` and `things_to_avoid`.
3. Generate your reply following that strategy.
4. (Optional) Call `hei_evaluate_response` to score your reply.

## Notes

- Emotional Memory works across tool calls when you pass the same `session_id`.
- The server is stateless except for the in-memory session store (resets when the process restarts).
