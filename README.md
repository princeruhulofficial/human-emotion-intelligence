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
  <img src="https://img.shields.io/badge/Version-0.3.0-green?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-Ready-blue?style=flat-square" alt="TypeScript">
  <img src="https://img.shields.io/badge/MCP-Supported-purple?style=flat-square" alt="MCP">
  <img src="https://img.shields.io/badge/HTTP_API-Ready-orange?style=flat-square" alt="HTTP API">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

---

### What is HEI?

**Human Emotion Intelligence (HEI)** is an open-source **Conversation Intelligence Layer** that sits between your users and any LLM.

Instead of prompting an LLM to "be empathetic", HEI first detects emotion, understands intent, plans a response strategy, evaluates the reply, and remembers emotional context across turns.

> Most AIs give generic empathy.  
> HEI gives structured emotional reasoning.

---

### Access Points (v0.3.0)

| Interface | Status | Notes |
|-----------|--------|-------|
| **Python SDK** | Ready | Full features + persistent memory |
| **TypeScript SDK** | Ready | Memory parity with Python |
| **MCP Server** | Ready | Claude Desktop, Cursor, Windsurf |
| **HTTP API** | Ready | API Gateway compatible |

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

print(result.emotion.primary)
print(result.strategy.suggested_approach)
print(hei.get_mood_shift("user_123").summary)
```

### Persistent Memory

```bash
export HEI_MEMORY_BACKEND=sqlite
export HEI_MEMORY_PATH=./data/hei_memory.db
```

```python
hei = HEI(api_key="sk-...", memory_backend="sqlite")
```

### MCP / HTTP API

```bash
pip install -e ".[mcp]"   # or .[api]
python -m hei.mcp_server
uvicorn hei.api:app --port 8000
```

---

### Core Features

- Emotion Detection (Primary + Secondary + Hidden + Intensity)
- Emotional Intent Detection
- Response Strategy Planner
- Evaluation + Auto Rewrite
- Emotional Memory (in-memory / SQLite / Redis)
- Model Agnostic (OpenAI, OpenRouter, Groq, local...)
- Production hardening (validation, auth, rate limits, CI)

---

### Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Emotional Memory](docs/memory.md)
- [API Reference](docs/api-reference.md)
- [MCP Server](docs/mcp.md)
- [HTTP API / Gateway](docs/api-gateway.md)
- [Philosophy](docs/philosophy.md)
- [Changelog](CHANGELOG.md)

---

### License

MIT

---

<p align="center">
  Built with ❤️ by the Founding Team<br>
  <strong>v0.3.0</strong> — Shipped 23 July 2026
</p>
