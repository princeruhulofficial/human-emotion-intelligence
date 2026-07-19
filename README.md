# Human Emotion Intelligence (HEI)

**Give AI emotional intelligence, not just intelligence.**

[![Status](https://img.shields.io/badge/Status-MVP-blue)]()
[![Version](https://img.shields.io/badge/Version-0.1.0-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()

HEI is a **Conversation Intelligence Layer** that sits between the user and any LLM.  
It analyzes emotion, detects intent, plans a response strategy, and evaluates the final output — so people feel genuinely understood.

> Instead of asking an LLM to "be empathetic", HEI provides structured emotional reasoning before generation.

## Quick Start

### 1. Install

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e .
```

### 2. Setup API Key

```bash
cp .env.example .env
```

Edit `.env` and add your key.

#### Option A: OpenRouter (Free models available — Recommended for testing)

1. Go to [https://openrouter.ai](https://openrouter.ai) and create a free account
2. Generate an API key
3. Put in `.env`:

```env
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

Popular free models on OpenRouter:
- `google/gemma-2-9b-it:free`
- `meta-llama/llama-3.2-3b-instruct:free`
- `microsoft/phi-3-mini-128k-instruct:free`

#### Option B: Official OpenAI

```env
OPENAI_API_KEY=sk-...
# OPENAI_BASE_URL=   (leave empty)
HEI_MODEL=gpt-4o-mini
```

### 3. Run Example

```bash
python examples/basic_usage.py
```

### Code Example

```python
from hei import HEI

hei = HEI(
    api_key="sk-or-v1-...",
    base_url="https://openrouter.ai/api/v1",
    model="google/gemma-2-9b-it:free"
)

result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)           # sadness
print(result.emotion.hidden)            # fear / disappointment
print(result.intent.primary_intent)     # seeking_comfort
print(result.strategy.suggested_approach)
```

## MVP Modules (v0.1)

1. **Emotion Detection** — Primary + Secondary + Hidden + Intensity
2. **Emotional Intent Detection**
3. **Response Strategy Planner**
4. **Response Evaluation + Optional Rewrite**

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
Evaluation Engine
```

## Why HEI?

Most AIs give generic empathy.  
HEI plans the emotional strategy first, then lets the LLM execute it.

**Result:** Responses that make people feel understood.

## Non-Goals

- Not a therapist
- Not a mind reader
- Not a manipulation tool
- Does not claim to "know" emotions with certainty

## Roadmap

- [x] Core Emotion + Intent + Strategy (MVP)
- [x] OpenRouter / any OpenAI-compatible support
- [ ] Emotional Memory
- [ ] Cultural Awareness
- [ ] Personality Layer
- [ ] TypeScript SDK
- [ ] MCP Server

## License

MIT

---

Built with ❤️ by the Founding Team
