from __future__ import annotations

from typing import Optional

from openai import OpenAI

from .emotion import EmotionAnalyzer
from .intent import IntentDetector
from .strategy import StrategyPlanner
from .evaluation import ResponseEvaluator
from .models import HEIResponse, EvaluationResult


class HEI:
    """
    Human Emotion Intelligence - Main entry point.

    Usage:
        hei = HEI(api_key="sk-...")
        result = hei.analyze("I guess my startup is over.")
        print(result.strategy.suggested_approach)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        client: Optional[OpenAI] = None,
    ):
        if client:
            self.client = client
        else:
            self.client = OpenAI(api_key=api_key, base_url=base_url)

        self.model = model
        self.emotion_analyzer = EmotionAnalyzer(self.client, model)
        self.intent_detector = IntentDetector(self.client, model)
        self.strategy_planner = StrategyPlanner(self.client, model)
        self.evaluator = ResponseEvaluator(self.client, model)

    def analyze(self, message: str) -> HEIResponse:
        """
        Full analysis pipeline:
        Emotion → Intent → Strategy
        """
        emotion = self.emotion_analyzer.analyze(message)

        emotion_context = (
            f"{emotion.primary.value} (intensity {emotion.intensity}/10)"
            + (f", hidden: {emotion.hidden.value}" if emotion.hidden else "")
        )

        intent = self.intent_detector.detect(message, emotion_context)
        strategy = self.strategy_planner.plan(message, emotion, intent)

        return HEIResponse(
            emotion=emotion,
            intent=intent,
            strategy=strategy,
            raw_message=message,
            model_used=self.model,
        )

    def evaluate_response(
        self,
        original_message: str,
        generated_response: str,
        strategy,
    ) -> EvaluationResult:
        """Evaluate a generated response against the planned strategy."""
        return self.evaluator.evaluate(original_message, generated_response, strategy)
