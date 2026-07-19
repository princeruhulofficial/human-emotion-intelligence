"""
Human Emotion Intelligence (HEI)
Conversation Intelligence Layer for AI
"""

from .core import HEI
from .models import (
    EmotionResult,
    IntentResult,
    StrategyResult,
    EvaluationResult,
    HEIResponse,
)

__version__ = "0.1.0"
__all__ = [
    "HEI",
    "EmotionResult",
    "IntentResult",
    "StrategyResult",
    "EvaluationResult",
    "HEIResponse",
]
