# Architecture

## High-level Flow

```text
User Message
      │
      ▼
┌─────────────────────────────┐
│         HEI Core                │
│  (Python / TypeScript SDK)      │
└─────────────────────────────┘
      │
      ├──► Emotion Analyzer
      │         • Primary / Secondary / Hidden
      │         • Intensity (1-10)
      │         • Confidence
      │
      ├──► Intent Detector
      │         • seeking_comfort, venting, celebrating...
      │
      ├──► Strategy Planner
      │         • Target outcome
      │         • Tone controls
      │         • Things to avoid
      │         • Suggested approach
      │
      ▼
LLM (any model) generates response
      │
      ▼
Evaluation Engine
      • Empathy / Human-likeness / Safety / Clarity
      • Optional automatic rewrite
```

## Design Principles

1. **Model-agnostic** — Works with OpenAI, OpenRouter, Groq, local models, etc.
2. **Structured reasoning first** — Plan before generating
3. **Fail safely** — Validation + clear errors
4. **Explainable** — Every decision includes reasoning + confidence
5. **Non-claiming** — Never pretends to "know" emotions with certainty

## Key Classes

| Class | Responsibility |
|-------|----------------|
| `HEI` | Main entry point |
| `EmotionAnalyzer` | Detect emotions |
| `IntentDetector` | Infer why the user is speaking |
| `StrategyPlanner` | Decide how to respond |
| `ResponseEvaluator` | Score + optionally rewrite |
