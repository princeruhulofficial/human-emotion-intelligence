from __future__ import annotations

import json
from openai import OpenAI

from .models import EmotionResult, IntentResult, StrategyResult


STRATEGY_SYSTEM_PROMPT = """You are an expert conversation strategist.
Your job is to plan how an AI should respond so the user feels genuinely understood.

You do NOT write the final response. You only create the strategy.

Return strict JSON:
{
  "current_emotion": "...",
  "target_outcome": "what emotional state or feeling we want the user to move toward",
  "recommended_strategy": "high-level approach",
  "tone": {
    "warmth": 0.0-1.0,
    "directness": 0.0-1.0,
    "formality": 0.0-1.0,
    "optimism": 0.0-1.0
  },
  "things_to_avoid": ["list of things the response should never do"],
  "suggested_approach": "concrete steps for the response",
  "reasoning": "why this strategy"
}
"""


class StrategyPlanner:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def plan(
        self,
        message: str,
        emotion: EmotionResult,
        intent: IntentResult,
    ) -> StrategyResult:
        context = f"""User message: {message}

Emotion analysis:
- Primary: {emotion.primary.value}
- Secondary: {emotion.secondary.value if emotion.secondary else None}
- Hidden: {emotion.hidden.value if emotion.hidden else None}
- Intensity: {emotion.intensity}/10
- Confidence: {emotion.confidence}

Intent analysis:
- Primary intent: {intent.primary_intent.value}
- Confidence: {intent.confidence}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": STRATEGY_SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content or "{}")

        return StrategyResult(
            current_emotion=data.get("current_emotion", emotion.primary.value),
            target_outcome=data.get("target_outcome", "feel understood"),
            recommended_strategy=data.get("recommended_strategy", "validate and support"),
            tone=data.get("tone", {"warmth": 0.7, "directness": 0.5, "formality": 0.4, "optimism": 0.5}),
            things_to_avoid=data.get("things_to_avoid", []),
            suggested_approach=data.get("suggested_approach", ""),
            reasoning=data.get("reasoning", ""),
        )
