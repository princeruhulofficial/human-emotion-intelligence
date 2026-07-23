<p align="center">
  <h1 align="center">Human Emotion Intelligence (HEI)</h1>
  <p align="center">
    <strong>Give AI emotional intelligence, not just intelligence.</strong>
  </p>
  <p align="center">
    Open-source Conversation Intelligence Layer for LLMs — emotion detection, intent understanding, response strategy, evaluation, and emotional memory.
  </p>
</p>

<p align="center">
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence/releases"><img src="https://img.shields.io/badge/Version-0.3.0-green?style=flat-square" alt="Version 0.3.0"></a>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence/actions"><img src="https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square" alt="CI"></a>
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/TypeScript-Ready-blue?style=flat-square" alt="TypeScript">
  <img src="https://img.shields.io/badge/MCP-Supported-purple?style=flat-square" alt="MCP Server">
  <img src="https://img.shields.io/badge/HTTP%20API-Ready-orange?style=flat-square" alt="HTTP API">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License">
</p>

---

## What is Human Emotion Intelligence (HEI)?

**HEI** is an open-source **AI emotion intelligence** and **conversation intelligence** layer that sits between users and any Large Language Model (GPT, Claude, Gemini, Grok, Llama, DeepSeek, and more).

Instead of relying on generic "be empathetic" prompts, HEI provides structured:

- **Emotion detection** (primary, secondary, hidden emotions + intensity)
- **Emotional intent detection** (seeking comfort, venting, celebrating, etc.)
- **Response strategy planning** (tone, what to avoid, suggested approach)
- **Response evaluation & rewrite** (empathy, human-likeness, safety)
- **Emotional memory** across turns (in-memory, SQLite, or Redis)

**Core value:** AI responses that make people *feel understood* — not just answered.

> Keywords: emotion AI, affective computing, empathetic LLM, conversation intelligence, emotional memory for AI agents, MCP emotion tools, AI empathy SDK

---

## Why HEI?

| Problem with raw LLMs | What HEI adds |
|----------------------|---------------|
| Generic empathy ("I'm sorry to hear that") | Structured emotion + intent reasoning |
| No memory of emotional state | Session-based emotional timeline + mood shift |
| Inconsistent tone | Explicit response strategy before generation |
| Hard to evaluate empathy | Scores + optional auto-rewrite |
| Rebuild emotion logic per product | One reusable SDK / API / MCP skill |

HEI is **not** a foundation model competitor. It is **infrastructure** — like auth or payments — for emotional intelligence.

---

## Access Points (v0.3.0)

| Interface | Best for | Status |
|-----------|----------|--------|
| [Python SDK](#quick-start-python) | Backend agents, research, pipelines | Ready |
| [TypeScript SDK](#typescript-sdk) | Node.js agents, web apps | Ready |
| [MCP Server](#mcp-server) | Claude Desktop, Cursor, Windsurf | Ready |
| [HTTP API](#http-api) | Any language, API Gateway | Ready |

---

## Quick Start (Python)

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
cp .env.example .env   # add OPENAI_API_KEY or OpenRouter key
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...")

result = hei.analyze(
    "I guess my startup is over.",
    session_id="user_123"
)

print(result.emotion.primary)        # e.g. sadness
print(result.emotion.hidden)         # e.g. fear
print(result.intent.primary_intent)  # e.g. seeking_comfort
print(result.strategy.suggested_approach)
print(hei.get_mood_shift("user_123").summary)
```

### Persistent emotional memory

```bash
export HEI_MEMORY_BACKEND=sqlite
export HEI_MEMORY_PATH=./data/hei_memory.db
```

```python
hei = HEI(api_key="sk-...", memory_backend="sqlite")
# Survives process restarts
```

Supported backends: `memory` (default) · `sqlite` · `redis`

---

## TypeScript SDK

```bash
cd packages/ts && npm install && npm run build
```

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({ apiKey: process.env.OPENAI_API_KEY! });

const r1 = await hei.analyze("I guess my startup is over.", "user_123");
const r2 = await hei.analyze("I'm trying to stay positive", "user_123");

console.log(hei.getMoodShift("user_123").summary);
```

---

## MCP Server

Use HEI as tools inside Claude Desktop, Cursor, or Windsurf:

```bash
pip install -e ".[mcp]"
export HEI_MCP_TOKEN=your-secret
python -m hei.mcp_server
```

Tools: `hei_analyze` · `hei_detect_emotion` · `hei_detect_intent` · `hei_get_mood_shift` · `hei_evaluate_response`

See [docs/mcp.md](docs/mcp.md).

---

## HTTP API

```bash
pip install -e ".[api]"
export HEI_API_TOKEN=your-secret
uvicorn hei.api:app --host 0.0.0.0 --port 8000
```

Endpoints: `/v1/analyze` · `/v1/emotion` · `/v1/intent` · `/v1/evaluate` · `/v1/mood-shift/{session_id}`

Ready for Nginx, Cloudflare, AWS API Gateway, Kong, Traefik. See [docs/api-gateway.md](docs/api-gateway.md).

---

## Core Features

- **Emotion Detection** — primary, secondary, hidden emotions + intensity (1–10)
- **Emotional Intent** — comfort, advice, validation, venting, celebration, and more
- **Strategy Planner** — tone config, things to avoid, suggested approach
- **Evaluation + Rewrite** — empathy, human-likeness, safety, clarity scores
- **Emotional Memory** — timeline, mood shift (improving / declining / intensifying)
- **Model-agnostic** — OpenAI, OpenRouter, Groq, local OpenAI-compatible endpoints
- **Production-minded** — validation, auth tokens, rate limits, CI, persistent stores

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Getting Started](docs/getting-started.md) | Install & first analysis |
| [Architecture](docs/architecture.md) | Pipeline design |
| [Emotional Memory](docs/memory.md) | SQLite / Redis backends |
| [API Reference](docs/api-reference.md) | Python SDK surface |
| [MCP Server](docs/mcp.md) | Claude / Cursor tools |
| [HTTP API / Gateway](docs/api-gateway.md) | REST + reverse proxy |
| [Philosophy](docs/philosophy.md) | Product principles |
| [Changelog](CHANGELOG.md) | Version history |

---

## Example: From generic to “gets me”

**User:** `I guess my startup is over.`

**Typical LLM:** *I'm sorry to hear that.*

**With HEI strategy:**  
*It sounds like you haven't just lost a company — months of effort, hope, and part of your identity may feel broken too. I could be wrong, but if that's close, we can name what was lost first, then think about next steps when you're ready.*

Users don't need emotion labels. They need to feel understood. HEI optimizes for that outcome.

---

## Non-goals

HEI will never claim to be a therapist, mind reader, or manipulation toolkit.  
We optimize for **feeling understood**, not emotional surveillance.

---

## License

MIT © Founding Team

---

<p align="center">
  <strong>Human Emotion Intelligence</strong> — the emotional intelligence infrastructure for AI<br>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence">github.com/princeruhulofficial/human-emotion-intelligence</a><br>
  <em>v0.3.0 · Shipped July 2026</em>
</p>
