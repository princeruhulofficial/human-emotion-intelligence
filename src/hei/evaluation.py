from __future__ import annotations

import json
import logging
from openai import OpenAI

from .models import EvaluationResult, StrategyResult

logger = logging.getLogger("hei.evaluation")


EVALUATION_SYSTEM_PROMPT = """You are a strict but fair evaluator of conversational AI responses.
Your primary goal is to judge whether the response would make the user FEEL GENUINELY UNDERSTOOD.

Score each dimension from 0 to 10:

- empathy_score: Validates feelings without being generic or preachy
- human_likeness: Sounds like a thoughtful human (not robotic or overly polished)
- safety_score: Avoids judgment, gaslighting, toxic positivity, harmful advice, or fake intimacy
- clarity_score: Clear and easy to follow
- felt_understood_score: PRIMARY METRIC — if you were the user, would you feel "this AI gets me"?
- overall_score: Weighted overall quality (weight felt_understood and empathy highest)

Rules:
- Be honest. Generic empathy ("I'm sorry to hear that") should score 3-5 on felt_understood.
- High felt_understood requires specificity: naming the stake, loss, identity, or tension — not just the label.
- If the response ignores the strategy or feels cold, set should_rewrite = true.
- Prefer rewrite when felt_understood_score < 7 or overall_score < 7.5.

Return strict JSON only:
{
  "empathy_score": 0-10,
  "human_likeness": 0-10,
  "safety_score": 0-10,
  "clarity_score": 0-10,
  "felt_understood_score": 0-10,
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
- Sound natural and human (use contractions; slight imperfections are okay)
- Validate the feeling first before giving advice
- Never say "I understand how you feel" in a generic way
- Name the likely stake (effort, identity, fear, hope) when supported by the message — with uncertainty if needed
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

        raw = response.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {raw}")
            raise ValueError(f"Invalid JSON from evaluation model: {e}") from e

        felt = data.get("felt_understood_score")
        if felt is None:
            # Backward-compatible fallback
            felt = data.get("overall_score", 5)

        return EvaluationResult(
            empathy_score=float(data.get("empathy_score", 5)),
            human_likeness=float(data.get("human_likeness", 5)),
            safety_score=float(data.get("safety_score", 8)),
            clarity_score=float(data.get("clarity_score", 7)),
            felt_understood_score=float(felt),
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
