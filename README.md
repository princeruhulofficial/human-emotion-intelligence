# Human Emotion Intelligence (HEI)

**Give AI emotional intelligence, not just intelligence.**

[![Status](https://img.shields.io/badge/Status-MVP-blue)]()
[![Version](https://img.shields.io/badge/Version-0.1.0-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue)]()

HEI is a **Conversation Intelligence Layer** that sits between the user and any LLM.  
It analyzes emotion, detects intent, plans a response strategy, and evaluates the final output — so people feel genuinely understood.

> Instead of asking an LLM to "be empathetic", HEI provides structured emotional reasoning before generation.

## Supported Languages

| Language     | Status   | Location              |
|--------------|----------|-----------------------|
| **Python**   | Ready    | `src/hei/`            |
| **TypeScript** | Ready  | `packages/ts/`        |

## Quick Start (Python)

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
cp .env.example .env   # add your key
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...", model="gpt-4o-mini")
result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)          # sadness
print(result.emotion.hidden)           # fear
print(result.intent.primary_intent)    # seeking_comfort
print(result.strategy.suggested_approach)
```

## Quick Start (TypeScript)

```bash
cd packages/ts
npm install
npm run build
```

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({
  apiKey: process.env.OPENAI_API_KEY!,
  baseURL: "https://openrouter.ai/api/v1", // optional
  model: "google/gemma-2-9b-it:free",
});

const result = await hei.analyze("I guess my startup is over.");
console.log(result.emotion.primary);
console.log(result.strategy.suggested_approach);
```

## OpenRouter (Free Testing)

```env
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

## MVP Modules

1. **Emotion Detection** — Primary + Secondary + Hidden + Intensity
2. **Emotional Intent Detection**
3. **Response Strategy Planner**
4. **Response Evaluation + Auto Rewrite**

## Architecture

```text
User Message
      ↓
Emotion Analyzer
      ↓
Intent Detector
      ↓
Strategy Planner
      ↓
LLM (any model)
      ↓
Evaluation + Optional Rewrite
```

## Non-Goals

- Not a therapist
- Not a mind reader
- Not a manipulation tool
- Does not claim certainty about emotions

## Roadmap

- [x] Python SDK (MVP)
- [x] TypeScript SDK (MVP)
- [x] OpenRouter / any OpenAI-compatible support
- [x] Evaluation + Auto-Rewrite
- [x] Golden dataset
- [ ] Emotional Memory
- [ ] Cultural Awareness
- [ ] MCP Server
- [ ] Self-hosted improvements

## License

MIT

---

Built with ❤️ by the Founding Team
