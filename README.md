# Human Emotion Intelligence (HEI)

**Give AI emotional intelligence, not just intelligence.**

[![Status](https://img.shields.io/badge/Status-MVP-blue)]()
[![Version](https://img.shields.io/badge/Version-0.1.1-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue)]()

HEI is a **Conversation Intelligence Layer** that sits between the user and any LLM.  
It analyzes emotion, detects intent, plans a response strategy, and evaluates the final output — so people feel genuinely understood.

> Instead of asking an LLM to "be empathetic", HEI provides structured emotional reasoning before generation.

## Supported SDKs

| Language       | Status | Path              |
|----------------|--------|-------------------|
| **Python**     | Ready  | `src/hei/`        |
| **TypeScript** | Ready  | `packages/ts/`    |

## Quick Start (Python)

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
cp .env.example .env          # add your key
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...", model="gpt-4o-mini")
result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)           # sadness
print(result.emotion.hidden)            # fear
print(result.intent.primary_intent)     # seeking_comfort
print(result.strategy.suggested_approach)
```

## Quick Start (TypeScript)

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
```

## OpenRouter (Free models)

```env
OPENAI_API_KEY=sk-or-v1-...
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

## Core Features (v0.1.1)

- Emotion Detection (Primary + Secondary + Hidden + Intensity)
- Emotional Intent Detection
- Response Strategy Planner
- Evaluation + Automatic Rewrite
- Full input validation + proper error handling
- Works with any OpenAI-compatible endpoint

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Changelog](CHANGELOG.md)
- [Original PRD](PRD.md)

## Running Tests

```bash
# Unit tests (no API key)
pytest tests/test_validation.py -v

# Golden set (needs API key)
pytest tests/test_golden.py -v -s
```

## Non-Goals

- Not a therapist
- Not a mind reader
- Not a manipulation tool
- Does not claim certainty about emotions

## Roadmap

- [x] Python SDK
- [x] TypeScript SDK
- [x] Evaluation + Auto-Rewrite
- [x] Golden dataset + tests
- [x] Critical production hardening
- [ ] Emotional Memory
- [ ] Cultural Awareness
- [ ] MCP Server
- [ ] More comprehensive evaluation metrics

## License

MIT

---

Built with ❤️ by the Founding Team
