from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .models import EmotionResult, PrimaryEmotion


EMOTION_SYSTEM_PROMPT = """You are an expert emotion analyst.
Your job is to carefully analyze the user's message and detect emotions with high accuracy.

Rules:
- Always return valid JSON only.
- Be honest about uncertainty. Use lower confidence when the signal is weak.
- Look for hidden emotions (e.g. "I'm fine" often hides sadness or frustration).
- Intensity is 1-10 (1 = very mild, 10 = extremely strong).
- Prefer specific emotions over "neutral" when possible.

Output format (strict JSON):
{
  "primary": "one of the allowed emotions",
  "secondary": "another emotion or null",
  "hidden": "hidden emotion or null",
  "intensity": 1-10,
  "confidence": 0.0-1.0,
  "reasoning": "short explanation"
}

Allowed primary emotions:
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
                {"role": "user", "content": f"Analyze this message:\n\n{message}"},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content or "{}")

        return EmotionResult(
            primary=PrimaryEmotion(data.get("primary", "neutral")),
            secondary=PrimaryEmotion(data["secondary"]) if data.get("secondary") else None,
            hidden=PrimaryEmotion(data["hidden"]) if data.get("hidden") else None,
            intensity=int(data.get("intensity", 5)),
            confidence=float(data.get("confidence", 0.5)),
            reasoning=data.get("reasoning", ""),
        )
