"""
Human Emotion Intelligence (HEI)
Conversation Intelligence Layer for AI
"""

from .core import HEI, HEIError, HEIValidationError
from .models import (
    EmotionResult,
    IntentResult,
    StrategyResult,
    EvaluationResult,
    HEIResponse,
    ToneConfig,
    PrimaryEmotion,
    EmotionalIntent,
)

__version__ = "0.1.1"
__all__ = [
    "HEI",
    "HEIError",
    "HEIValidationError",
    "EmotionResult",
    "IntentResult",
    "StrategyResult",
    "EvaluationResult",
    "HEIResponse",
    "ToneConfig",
    "PrimaryEmotion",
    "EmotionalIntent",
]
