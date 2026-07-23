from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

from openai import OpenAI, APIError, APITimeoutError, RateLimitError

from .emotion import EmotionAnalyzer
from .intent import IntentDetector
from .strategy import StrategyPlanner
from .evaluation import ResponseEvaluator
from .memory import EmotionalMemory, MoodShift
from .models import HEIResponse, EvaluationResult, StrategyResult

logger = logging.getLogger("hei")


class HEIError(Exception):
    """Base exception for HEI"""
    pass


class HEIValidationError(HEIError):
    """Raised when input validation fails"""
    pass


class HEI:
    """
    Human Emotion Intelligence - Main entry point.

    Usage:
        hei = HEI(api_key="sk-...")

        # Without memory
        result = hei.analyze("I guess my startup is over.")

        # With emotional memory (in-memory by default)
        result = hei.analyze("I guess my startup is over.", session_id="user_123")

        # Persistent memory via env:
        #   HEI_MEMORY_BACKEND=sqlite
        #   HEI_MEMORY_PATH=./data/hei.db
        hei = HEI(api_key="sk-...", memory=EmotionalMemory.from_env())
    """

    MAX_MESSAGE_LENGTH = 8000

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        client: Optional[OpenAI] = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        memory: Optional[EmotionalMemory] = None,
        memory_backend: Optional[str] = None,
    ):
        if client:
            self.client = client
        else:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                max_retries=max_retries,
            )

        self.model = model
        self.emotion_analyzer = EmotionAnalyzer(self.client, model)
        self.intent_detector = IntentDetector(self.client, model)
        self.strategy_planner = StrategyPlanner(self.client, model)
        self.evaluator = ResponseEvaluator(self.client, model)

        if memory is not None:
            self.memory = memory
        elif memory_backend or os.getenv("HEI_MEMORY_BACKEND"):
            backend = memory_backend or os.getenv("HEI_MEMORY_BACKEND", "memory")
            self.memory = EmotionalMemory(
                backend=backend,
                sqlite_path=os.getenv("HEI_MEMORY_PATH", "hei_memory.db"),
                redis_url=os.getenv("HEI_REDIS_URL", "redis://localhost:6379/0"),
            )
        else:
            self.memory = EmotionalMemory()

    def _validate_message(self, message: str) -> str:
        if message is None:
            raise HEIValidationError("message cannot be None")
        if not isinstance(message, str):
            raise HEIValidationError("message must be a string")

        cleaned = message.strip()
        if not cleaned:
            raise HEIValidationError("message cannot be empty")

        if len(cleaned) > self.MAX_MESSAGE_LENGTH:
            raise HEIValidationError(
                f"message too long ({len(cleaned)} chars). Max allowed: {self.MAX_MESSAGE_LENGTH}"
            )

        return cleaned

    def analyze(
        self,
        message: str,
        session_id: Optional[str] = None,
    ) -> HEIResponse:
        """
        Full analysis pipeline:
        Emotion → Intent → Strategy

        If session_id is provided, emotional memory is used and updated.
        """
        message = self._validate_message(message)

        try:
            emotion = self.emotion_analyzer.analyze(message)

            emotion_context = (
                f"{emotion.primary.value} (intensity {emotion.intensity}/10)"
                + (f", hidden: {emotion.hidden.value}" if emotion.hidden else "")
            )

            intent = self.intent_detector.detect(message, emotion_context)

            memory_context = None
            if session_id:
                memory_context = self.memory.get_context_for_strategy(session_id)

            strategy = self.strategy_planner.plan(
                message=message,
                emotion=emotion,
                intent=intent,
                memory_context=memory_context,
            )

            if session_id:
                self.memory.add_turn(
                    session_id=session_id,
                    message=message,
                    emotion=emotion,
                    intent=intent,
                )

            return HEIResponse(
                emotion=emotion,
                intent=intent,
                strategy=strategy,
                raw_message=message,
                model_used=self.model,
            )
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"LLM API error during analyze: {e}")
            raise HEIError(f"Failed to analyze message: {e}") from e
        except Exception as e:
            logger.exception("Unexpected error during analyze")
            raise HEIError(f"Unexpected error: {e}") from e

    def get_mood_shift(self, session_id: str) -> MoodShift:
        """Convenience method to detect mood shift for a session."""
        return self.memory.detect_mood_shift(session_id)

    def evaluate_response(
        self,
        original_message: str,
        generated_response: str,
        strategy: StrategyResult,
    ) -> EvaluationResult:
        """Evaluate a generated response against the planned strategy."""
        original_message = self._validate_message(original_message)
        if not generated_response or not generated_response.strip():
            raise HEIValidationError("generated_response cannot be empty")

        try:
            return self.evaluator.evaluate(original_message, generated_response, strategy)
        except (APIError, APITimeoutError, RateLimitError) as e:
            logger.error(f"LLM API error during evaluate: {e}")
            raise HEIError(f"Failed to evaluate response: {e}") from e

    def improve_response(
        self,
        original_message: str,
        generated_response: str,
        strategy: StrategyResult,
        max_attempts: int = 1,
    ) -> Tuple[str, EvaluationResult]:
        """
        Evaluate a response and automatically rewrite it if quality is low.

        Returns:
            (final_response, evaluation)
        """
        original_message = self._validate_message(original_message)
        if not generated_response or not generated_response.strip():
            raise HEIValidationError("generated_response cannot be empty")

        current_response = generated_response
        evaluation = self.evaluate_response(original_message, current_response, strategy)

        attempts = 0
        while evaluation.should_rewrite and attempts < max_attempts:
            attempts += 1
            logger.info(f"Rewriting response (attempt {attempts}/{max_attempts})")

            current_response = self.evaluator.rewrite(
                original_message=original_message,
                previous_response=current_response,
                strategy=strategy,
                feedback=evaluation.feedback,
            )
            evaluation = self.evaluate_response(original_message, current_response, strategy)

        return current_response, evaluation
