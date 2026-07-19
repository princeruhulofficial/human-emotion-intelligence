from __future__ import annotations

import json
from openai import OpenAI

from .models import EmotionResult, PrimaryEmotion


EMOTION_SYSTEM_PROMPT = """You are a highly skilled emotion analyst with deep understanding of human psychology.

Your task is to detect the emotional state behind a message with precision and honesty.

Key principles:
- People often hide their real feelings ("I'm fine", "It's okay", "Whatever").
- Look for secondary and hidden emotions.
- Intensity is 1-10 (1 = barely noticeable, 10 = overwhelming).
- Always prefer specific emotions over "neutral" when there is any signal.
- Be conservative with confidence when the message is ambiguous.

Return ONLY valid JSON in this exact format:
{
  "primary": "one of the allowed emotions",
  "secondary": "another emotion or null",
  "hidden": "hidden emotion or null",
  "intensity": 1-10,
  "confidence": 0.0-1.0,
  "reasoning": "1-2 sentence explanation"
}

Allowed emotions:
happiness, sadness, anger, fear, anxiety, excitement, hope, pride, shame, guilt, loneliness, frustration, gratitude, curiosity, neutral, mixed
"""


class EmotionAnalyzer:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def analyze(self, message: str) -> EmotionResult:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EMOTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze the emotional content of this message:\n\n\"{message}\""},
            ],
            temperature=0.15,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content or "{}")

        def safe_emotion(value):
            if not value:
                return None
            try:
                return PrimaryEmotion(value)
            except ValueError:
                return None

        return EmotionResult(
            primary=safe_emotion(data.get("primary")) or PrimaryEmotion.NEUTRAL,
            secondary=safe_emotion(data.get("secondary")),
            hidden=safe_emotion(data.get("hidden")),
            intensity=max(1, min(10, int(data.get("intensity", 5)))),
            confidence=max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            reasoning=data.get("reasoning", ""),
        )
