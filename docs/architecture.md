# Architecture

## High-level Overview

HEI is deliberately designed as a **layer**, not a full agent or replacement for LLMs.

```text
                    ┌─────────────────────────────┐
User Message ──────►  │       HEI Intelligence Layer        │
                    │                                    │
                    │  1. Emotion Analyzer               │
                    │  2. Intent Detector                │
                    │  3. Strategy Planner               │
                    │                                    │
                    └─────────────────────────────┘
                                      │
                                      ▼
                               Your LLM (any)
                                      │
                                      ▼
                    ┌─────────────────────────────┐
                    │     Evaluation + Optional Rewrite  │
                    └─────────────────────────────┘
                                      │
                                      ▼
                               Final Response
```

## Module Responsibilities

| Module | Responsibility | Output |
|--------|----------------|--------|
| **Emotion Analyzer** | Detect primary, secondary, hidden emotions + intensity | `EmotionResult` |
| **Intent Detector** | Understand *why* the user is speaking | `IntentResult` |
| **Strategy Planner** | Decide how the AI should respond | `StrategyResult` |
| **Evaluation Engine** | Score the generated reply and optionally rewrite | `EvaluationResult` |

## Design Principles

1. **Model-agnostic**  
   Works with OpenAI, Anthropic (via compatible endpoints), OpenRouter, Groq, local vLLM, etc.

2. **Plan before generate**  
   Emotional reasoning happens *before* the LLM writes the final answer.

3. **Fail safely**  
   Strong input validation + clear custom exceptions (`HEIError`, `HEIValidationError`).

4. **Explainable**  
   Every decision includes `reasoning` and `confidence`.

5. **Non-claiming**  
   HEI never claims to "know" emotions with certainty. It always works with probabilistic inference.

## Data Flow Example

```text
Input: "I guess my startup is over."

→ Emotion Analyzer
   primary: sadness
   hidden: fear
   intensity: 8

→ Intent Detector
   primary_intent: seeking_comfort

→ Strategy Planner
   target_outcome: feel understood + slight hope
   tone: high warmth, medium directness
   things_to_avoid: ["toxic positivity", "immediate advice dump"]

→ Your LLM generates a reply using the strategy

→ Evaluation Engine scores it
   If score is low → automatic rewrite
```

## Why this architecture?

Most teams try to solve emotional quality with longer system prompts.  
That approach is brittle, hard to evaluate, and inconsistent across models.

HEI turns emotional intelligence into a **reusable, testable, model-agnostic layer**.
