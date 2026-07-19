# Human Emotion Intelligence (HEI)

**Give AI emotional intelligence, not just intelligence.**

[![Status](https://img.shields.io/badge/Status-MVP-blue)]()
[![Version](https://img.shields.io/badge/Version-0.1.0-green)]()
[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()

HEI is a **Conversation Intelligence Layer** that sits between the user and any LLM.  
It analyzes emotion, detects intent, plans a response strategy, and evaluates the final output — so people feel genuinely understood.

> Instead of asking an LLM to "be empathetic", HEI provides structured emotional reasoning before generation.

## Quick Start

```bash
pip install -e .
export OPENAI_API_KEY=sk-...
python examples/basic_usage.py
```

```python
from hei import HEI

hei = HEI(api_key="sk-...")

result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)          # sadness
print(result.emotion.hidden)           # fear / disappointment
print(result.intent.primary_intent)    # seeking_comfort
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
- [ ] Emotional Memory
- [ ] Cultural Awareness
- [ ] Personality Layer
- [ ] TypeScript SDK
- [ ] MCP Server
- [ ] Self-hosted option improvements

## License

MIT

---

Built with ❤️ by the Founding Team
