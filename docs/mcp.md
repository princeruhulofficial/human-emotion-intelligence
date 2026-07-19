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

## Security Features

| Feature | How to use |
|---------|-----------|
| **Optional Token Auth** | Set `HEI_MCP_TOKEN=your-secret`. Every tool call must then pass `token="your-secret"`. |
| **Rate Limiting** | Default 60 calls/minute. Override with `HEI_MCP_RATE_LIMIT=30`. |
| **Stricter Input Limits** | Messages capped at 4000 characters for MCP. |
| **Structured Logging** | All calls are logged with timestamp, tool name, and outcome. |

## Installation

```bash
pip install -e ".[mcp]"
```

## Running the Server

```bash
export OPENAI_API_KEY=sk-...
export HEI_MCP_TOKEN=my-secret-token          # optional but recommended
export HEI_MCP_RATE_LIMIT=60                  # optional
export OPENAI_BASE_URL=https://openrouter.ai/api/v1
export HEI_MODEL=google/gemma-2-9b-it:free

python -m hei.mcp_server
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "hei": {
      "command": "python",
      "args": ["-m", "hei.mcp_server"],
      "cwd": "/absolute/path/to/human-emotion-intelligence",
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "HEI_MCP_TOKEN": "my-secret-token",
        "OPENAI_BASE_URL": "https://openrouter.ai/api/v1",
        "HEI_MODEL": "google/gemma-2-9b-it:free"
      }
    }
  }
}
```

When `HEI_MCP_TOKEN` is set, the agent must pass the same token in every tool call:

```
hei_analyze(message="...", token="my-secret-token")
```

## Cursor / Windsurf

Same environment variables. Most editors let you add a custom MCP server with:

```bash
python -m hei.mcp_server
```

## Security Recommendations

1. **Always set `HEI_MCP_TOKEN`** in any shared or semi-trusted environment.
2. Keep the server on **localhost** unless you add proper network auth.
3. Never commit real API keys or tokens.
4. Use random, hard-to-guess `session_id` values in production.
5. Monitor the logs for repeated auth failures or rate-limit hits.

## Example Agent Flow

1. Call `hei_analyze` with the user message + `session_id` + `token`.
2. Read `strategy.suggested_approach` and `things_to_avoid`.
3. Generate your reply following that strategy.
4. (Optional) Call `hei_evaluate_response` to score the reply.

## Notes

- Emotional Memory works across tool calls when you reuse the same `session_id`.
- The in-memory store resets when the MCP process restarts.
- Rate limiting is per-token (or "anon" if no token is used).
