from __future__ import annotations

import json
from openai import OpenAI

from .models import EmotionalIntent, IntentResult


INTENT_SYSTEM_PROMPT = """You are an expert at understanding emotional intent behind messages.

People rarely say exactly what they need. Your job is to infer the real intent.

Common intents:
- seeking_comfort
- seeking_advice
- seeking_validation
- venting
- celebrating
- complaining
- sharing
- asking_question
- negotiating
- unknown

Return strict JSON:
{
  "primary_intent": "...",
  "secondary_intent": "... or null",
  "confidence": 0.0-1.0,
  "reasoning": "short explanation"
}
"""


class IntentDetector:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def detect(self, message: str, emotion_context: str | None = None) -> IntentResult:
        user_content = f"Message: {message}"
        if emotion_context:
            user_content += f"\n\nDetected emotion context: {emotion_context}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content or "{}")

        return IntentResult(
            primary_intent=EmotionalIntent(data.get("primary_intent", "unknown")),
            secondary_intent=EmotionalIntent(data["secondary_intent"]) if data.get("secondary_intent") else None,
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
        )
