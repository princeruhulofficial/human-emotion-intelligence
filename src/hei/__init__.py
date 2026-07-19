"""
Human Emotion Intelligence (HEI)
Conversation Intelligence Layer for AI
"""

from .core import HEI, HEIError, HEIValidationError
from .memory import EmotionalMemory, MemoryTurn, MoodShift, MoodShiftType
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

__version__ = "0.2.0"
__all__ = [
    "HEI",
    "HEIError",
    "HEIValidationError",
    "EmotionalMemory",
    "MemoryTurn",
    "MoodShift",
    "MoodShiftType",
    "EmotionResult",
    "IntentResult",
    "StrategyResult",
    "EvaluationResult",
    "HEIResponse",
    "ToneConfig",
    "PrimaryEmotion",
    "EmotionalIntent",
]
