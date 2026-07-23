from __future__ import annotations

import json
from openai import OpenAI

from .models import AppraisalSignals, EmotionResult, PrimaryEmotion


EMOTION_SYSTEM_PROMPT = """You are a highly skilled emotion analyst grounded in psychology
(Plutchik-inspired categories + appraisal-style reasoning).

Detect the emotional state behind a message with precision and honesty.

Key principles:
- People often hide their real feelings ("I'm fine", "It's okay", "Whatever").
- Look for secondary and hidden emotions.
- Intensity is 1-10 (1 = barely noticeable, 10 = overwhelming).
- Prefer specific emotions over "neutral" when there is any signal.
- Be conservative with confidence when the message is ambiguous.
- Never claim certainty about inner states; inference only.

Appraisal (optional but preferred when the message implies stakes):
- goal_relevance: 0-1 how much this touches the user's goals/identity
- coping_potential: 0-1 how able they seem to act or cope
- agency: self | other | circumstances | unknown

Return ONLY valid JSON:
{
  "primary": "one of the allowed emotions",
  "secondary": "another emotion or null",
  "hidden": "hidden emotion or null",
  "intensity": 1-10,
  "confidence": 0.0-1.0,
  "reasoning": "1-2 sentence explanation",
  "appraisal": {
    "goal_relevance": 0.0-1.0,
    "coping_potential": 0.0-1.0,
    "agency": "self|other|circumstances|unknown"
  }
}

Allowed emotions:
happiness, trust, fear, surprise, sadness, disgust, anger, anticipation,
anxiety, excitement, hope, pride, shame, guilt, loneliness, frustration,
gratitude, curiosity, love, optimism, disappointment, burnout, neutral, mixed
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
                {
                    "role": "user",
                    "content": f'Analyze the emotional content of this message:\n\n"{message}"',
                },
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

        appraisal = None
        raw_app = data.get("appraisal")
        if isinstance(raw_app, dict):
            agency = str(raw_app.get("agency", "unknown")).lower()
            if agency not in {"self", "other", "circumstances", "unknown"}:
                agency = "unknown"
            appraisal = AppraisalSignals(
                goal_relevance=max(0.0, min(1.0, float(raw_app.get("goal_relevance", 0.5)))),
                coping_potential=max(0.0, min(1.0, float(raw_app.get("coping_potential", 0.5)))),
                agency=agency,
            )

        return EmotionResult(
            primary=safe_emotion(data.get("primary")) or PrimaryEmotion.NEUTRAL,
            secondary=safe_emotion(data.get("secondary")),
            hidden=safe_emotion(data.get("hidden")),
            intensity=max(1, min(10, int(data.get("intensity", 5)))),
            confidence=max(0.0, min(1.0, float(data.get("confidence", 0.5)))),
            reasoning=data.get("reasoning", ""),
            appraisal=appraisal,
        )
