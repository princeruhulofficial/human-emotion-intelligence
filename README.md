<p align="center">
  <h1 align="center">Human Emotion Intelligence (HEI)</h1>
  <p align="center">
    <strong>Give AI emotional intelligence, not just intelligence.</strong>
  </p>
  <p align="center">
    The Conversation Intelligence Layer for LLMs
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-MVP-blue?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Version-0.2.0-green?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-Ready-blue?style=flat-square" alt="TypeScript">
  <img src="https://img.shields.io/badge/MCP-Supported-purple?style=flat-square" alt="MCP">
  <img src="https://img.shields.io/badge/HTTP_API-Ready-orange?style=flat-square" alt="HTTP API">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

---

### What is HEI?

**Human Emotion Intelligence (HEI)** is an open-source **Conversation Intelligence Layer** that sits between your users and any LLM (GPT, Claude, Gemini, Grok, Llama, etc.).

Instead of prompting an LLM to "be empathetic", HEI first:

1. Detects emotion (including hidden emotions)
2. Understands emotional intent
3. Plans a response strategy
4. Evaluates and optionally rewrites the final answer
5. Remembers emotional context across turns

**Result:** AI responses that make people feel genuinely understood.

> Most AIs give generic empathy.  
> HEI gives structured emotional reasoning.

---

### Access Points (v0.2.0)

| Interface | Status | Use when |
|-----------|--------|----------|
| **Python SDK** | Ready | Backend services, notebooks, scripts |
| **TypeScript SDK** | Ready | Node.js / frontend agents |
| **MCP Server** | Ready | Claude Desktop, Cursor, Windsurf |
| **HTTP API** | Ready | API Gateway, microservices, any language |

---

### Quick Start (Python)

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
cp .env.example .env
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...")

result = hei.analyze("I guess my startup is over.", session_id="user_123")

print(result.emotion.primary)           # sadness
print(result.emotion.hidden)            # fear
print(result.intent.primary_intent)     # seeking_comfort
print(result.strategy.suggested_approach)
```

### MCP (Claude / Cursor)

```bash
pip install -e ".[mcp]"
export HEI_MCP_TOKEN=your-secret
python -m hei.mcp_server
```

### HTTP API (API Gateway ready)

```bash
pip install -e ".[api]"
export HEI_API_TOKEN=your-secret
uvicorn hei.api:app --host 0.0.0.0 --port 8000
```

---

### Core Features

- Emotion Detection (Primary + Secondary + Hidden + Intensity)
- Emotional Intent Detection
- Response Strategy Planner
- Evaluation + Auto Rewrite
- **Emotional Memory** (session timeline + mood shift)
- Model Agnostic (OpenAI, OpenRouter, Groq, local...)
- Production hardening (validation, auth, rate limits)

---

### Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [MCP Server](docs/mcp.md)
- [HTTP API / Gateway](docs/api-gateway.md)
- [Philosophy](docs/philosophy.md)
- [Changelog](CHANGELOG.md)

---

### Non-Goals

HEI will never claim to be a therapist, mind reader, or manipulation tool.  
We optimize for **feeling understood**, not emotional surveillance.

---

### License

MIT

---

<p align="center">
  Built with ❤️ by the Founding Team<br>
  <strong>v0.2.0</strong> — Shipped 19 July 2026
</p>
