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
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence"><img src="https://img.shields.io/badge/Status-MVP-blue?style=flat-square" alt="Status"></a>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence"><img src="https://img.shields.io/badge/Version-0.1.1-green?style=flat-square" alt="Version"></a>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence"><img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square" alt="Python"></a>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence"><img src="https://img.shields.io/badge/TypeScript-Ready-blue?style=flat-square" alt="TypeScript"></a>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License"></a>
</p>

---

### What is HEI?

**Human Emotion Intelligence (HEI)** is an open-source **Conversation Intelligence Layer** that sits between your users and any LLM (GPT, Claude, Gemini, Grok, Llama, etc.).

Instead of prompting an LLM to "be empathetic", HEI first:

1. Detects emotion (including hidden emotions)
2. Understands emotional intent
3. Plans a response strategy
4. Evaluates and optionally rewrites the final answer

**Result:** AI responses that make people feel genuinely understood.

> Most AIs give generic empathy.  
> HEI gives structured emotional reasoning.

---

### Why HEI?

| Problem with current AI | How HEI helps |
|-------------------------|---------------|
| Generic "I'm sorry to hear that" | Detects real emotion + hidden layers |
| Robotic tone | Plans warmth, directness, formality |
| Inconsistent empathy | Structured strategy before generation |
| No emotional memory or intent | Intent detection + response planning |
| Hard to evaluate quality | Built-in evaluation + auto-rewrite |

HEI is **model-agnostic**. It works with OpenAI, OpenRouter, Groq, local models, or any OpenAI-compatible API.

---

### Quick Start

#### Python

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
cp .env.example .env          # add your API key
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...", model="gpt-4o-mini")

result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)           # sadness
print(result.emotion.hidden)            # fear / disappointment
print(result.intent.primary_intent)     # seeking_comfort
print(result.strategy.suggested_approach)
```

#### TypeScript

```bash
cd packages/ts && npm install && npm run build
```

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({
  apiKey: process.env.OPENAI_API_KEY!,
  baseURL: "https://openrouter.ai/api/v1",
  model: "google/gemma-2-9b-it:free",
});

const result = await hei.analyze("I guess my startup is over.");
console.log(result.emotion.primary);
console.log(result.strategy.suggested_approach);
```

#### Free Testing with OpenRouter

```env
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

---

### Core Features (v0.1.1)

- **Emotion Detection** — Primary, Secondary, Hidden emotions + Intensity (1-10)
- **Emotional Intent Detection** — seeking comfort, venting, celebrating, etc.
- **Response Strategy Planner** — Decides tone, approach, and things to avoid
- **Evaluation + Auto Rewrite** — Scores empathy, human-likeness, safety, clarity
- **Model Agnostic** — Works with any OpenAI-compatible endpoint
- **Type-safe SDKs** — Python (Pydantic) + TypeScript (Zod)
- **Production Hardened** — Input validation, timeouts, proper error handling

---

### Architecture

```text
User Message
      ↓
Emotion Analyzer  →  Intent Detector  →  Strategy Planner
      ↓
LLM (any model)
      ↓
Evaluation Engine (+ optional rewrite)
      ↓
Final Response
```

HEI does **not** replace your LLM.  
It makes every LLM emotionally smarter.

---

### Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Philosophy](docs/philosophy.md)
- [Changelog](CHANGELOG.md)
- [Product Requirements Document](PRD.md)

---

### Use Cases

- AI Companions & Character chat
- Customer Support agents
- Coaching & Mentoring bots
- Mental wellness applications (with proper safety boundaries)
- Education platforms
- Any product where conversation quality matters

---

### Non-Goals

HEI will never:
- Claim to be a therapist
- Claim to "know" emotions with certainty
- Act as a lie detector or mind reader
- Be used as a manipulation engine

We optimize for **feeling understood**, not for emotional surveillance.

---

### Roadmap

- [x] Python SDK
- [x] TypeScript SDK
- [x] Emotion + Intent + Strategy + Evaluation
- [x] Golden dataset + tests
- [x] Production hardening (validation, errors, timeouts)
- [ ] Emotional Memory
- [ ] Cultural Awareness
- [ ] MCP Server
- [ ] Deeper evaluation metrics & dashboards

---

### Contributing

This is early-stage open source. Feedback, issues, and pull requests are very welcome.

---

### License

MIT

---

<p align="center">
  Built with ❤️ by the Founding Team<br>
  <a href="https://github.com/princeruhulofficial/human-emotion-intelligence">GitHub</a>
</p>
