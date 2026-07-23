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
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence/releases"><img src="https://img.shields.io/badge/Version-0.4.0-green?style=flat-square" alt="Version 0.4.0"></a>
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

- **Emotion detection** (Plutchik-aligned labels, secondary/hidden, intensity, optional appraisal)
- **Emotional intent detection**
- **Response strategy planning**
- **Response evaluation & rewrite** with **`felt_understood_score`** as the primary KPI
- **Emotional memory** with salience-aware context (in-memory, SQLite, or Redis)

**Core value:** AI responses that make people *feel understood* — not just answered.

---

## Quick Start (Python)

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
print(result.emotion.primary, result.emotion.appraisal)
print(hei.get_mood_shift("user_123").summary)
```

### Persistent memory

```bash
export HEI_MEMORY_BACKEND=sqlite
export HEI_MEMORY_PATH=./data/hei_memory.db
```

---

## Access Points

| Interface | Status |
|-----------|--------|
| Python SDK | Ready |
| TypeScript SDK | Ready |
| MCP Server | Ready |
| HTTP API | Ready |

```bash
pip install -e ".[mcp]"   # or .[api]
python -m hei.mcp_server
uvicorn hei.api:app --port 8000
```

---

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Emotional Memory](docs/memory.md)
- [Research Insights 2026](docs/research-insights-2026.md)
- [Roadmap v0.4](docs/roadmap-v0.4.md)
- [MCP](docs/mcp.md) · [HTTP API](docs/api-gateway.md) · [Philosophy](docs/philosophy.md)
- [Changelog](CHANGELOG.md)

---

## License

MIT

<p align="center"><strong>v0.4.0</strong> — Shipped July 2026</p>
