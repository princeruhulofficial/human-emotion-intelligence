from __future__ import annotations

import json
from typing import Optional
from openai import OpenAI

from .models import EvaluationResult, StrategyResult


EVALUATION_SYSTEM_PROMPT = """You are a strict but fair evaluator of conversational AI responses.
Your goal is to judge whether the response makes the user feel genuinely understood.

Score each dimension from 0 to 10:

- empathy_score: Does it validate feelings without being generic or preachy?
- human_likeness: Does it sound like a thoughtful human (not robotic or overly polished)?
- safety_score: Does it avoid judgment, gaslighting, toxic positivity, or harmful advice?
- clarity_score: Is the message clear and easy to follow?
- overall_score: Weighted overall quality for "feeling understood"

Rules:
- Be honest. Most generic empathy responses should score 4-6 on empathy.
- If the response ignores the strategy or feels cold, set should_rewrite = true.
- Only suggest a rewrite if overall_score < 7.5 or empathy_score < 7.

Return strict JSON only:
{
  "empathy_score": 0-10,
  "human_likeness": 0-10,
  "safety_score": 0-10,
  "clarity_score": 0-10,
  "overall_score": 0-10,
  "feedback": "2-4 sentences of honest feedback",
  "should_rewrite": true/false,
  "rewrite_suggestion": "null or a short direction for improvement"
}
"""


REWRITE_SYSTEM_PROMPT = """You are an expert at rewriting AI responses so the user feels deeply understood.

You will receive:
1. The original user message
2. The emotional strategy that should be followed
3. The previous response that needs improvement
4. Feedback on what was weak

Your job: Write a much better response that follows the strategy closely.

Guidelines:
- Sound natural and human (use contractions, slight imperfections are okay)
- Validate the feeling first before giving advice
- Never say "I understand how you feel" in a generic way
- Match the recommended tone (warmth, directness, etc.)
- Avoid toxic positivity or minimizing the emotion
- Keep it concise but warm

Return ONLY the rewritten response text. No JSON, no explanation.
"""


class ResponseEvaluator:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini"):
        self.client = client
        self.model = model

    def evaluate(
        self,
        original_message: str,
        generated_response: str,
        strategy: StrategyResult,
    ) -> EvaluationResult:
        prompt = f"""Original user message:
{original_message}

Strategy that should have been followed:
{strategy.model_dump_json(indent=2)}

Generated response to evaluate:
{generated_response}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EVALUATION_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content or "{}")

        return EvaluationResult(
            empathy_score=float(data.get("empathy_score", 5)),
            human_likeness=float(data.get("human_likeness", 5)),
            safety_score=float(data.get("safety_score", 8)),
            clarity_score=float(data.get("clarity_score", 7)),
            overall_score=float(data.get("overall_score", 6)),
            feedback=data.get("feedback", ""),
            should_rewrite=bool(data.get("should_rewrite", False)),
            rewrite_suggestion=data.get("rewrite_suggestion"),
        )

    def rewrite(
        self,
        original_message: str,
        previous_response: str,
        strategy: StrategyResult,
        feedback: str,
    ) -> str:
        """Generate a better response using the strategy + evaluation feedback."""
        prompt = f"""Original user message:
{original_message}

Strategy to follow:
{strategy.model_dump_json(indent=2)}

Previous (weak) response:
{previous_response}

Feedback on what needs improvement:
{feedback}

Now write a significantly better response.
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )

        return (response.choices[0].message.content or "").strip()
