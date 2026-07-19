from __future__ import annotations

import json
from openai import OpenAI

from .models import EvaluationResult, StrategyResult


EVALUATION_SYSTEM_PROMPT = """You are a strict but fair evaluator of conversational responses.
Score how well a response follows the given strategy and makes the user feel understood.

Return strict JSON:
{
  "empathy_score": 0-10,
  "human_likeness": 0-10,
  "safety_score": 0-10,
  "clarity_score": 0-10,
  "overall_score": 0-10,
  "feedback": "honest short feedback",
  "should_rewrite": true/false,
  "rewrite_suggestion": "only if should_rewrite is true, otherwise null"
}
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
