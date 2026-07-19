from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PrimaryEmotion(str, Enum):
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    HOPE = "hope"
    PRIDE = "pride"
    SHAME = "shame"
    GUILT = "guilt"
    LONELINESS = "loneliness"
    FRUSTRATION = "frustration"
    GRATITUDE = "gratitude"
    CURIOSITY = "curiosity"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class EmotionalIntent(str, Enum):
    SEEKING_COMFORT = "seeking_comfort"
    SEEKING_ADVICE = "seeking_advice"
    SEEKING_VALIDATION = "seeking_validation"
    VENTING = "venting"
    CELEBRATING = "celebrating"
    COMPLAINING = "complaining"
    SHARING = "sharing"
    ASKING_QUESTION = "asking_question"
    NEGOTIATING = "negotiating"
    UNKNOWN = "unknown"


class EmotionResult(BaseModel):
    primary: PrimaryEmotion
    secondary: Optional[PrimaryEmotion] = None
    hidden: Optional[PrimaryEmotion] = None
    intensity: int = Field(ge=1, le=10, description="Emotion intensity from 1-10")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of the detection")


class IntentResult(BaseModel):
    primary_intent: EmotionalIntent
    secondary_intent: Optional[EmotionalIntent] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class StrategyResult(BaseModel):
    current_emotion: str
    target_outcome: str
    recommended_strategy: str
    tone: dict = Field(
        default_factory=lambda: {
            "warmth": 0.7,
            "directness": 0.5,
            "formality": 0.4,
            "optimism": 0.5,
        }
    )
    things_to_avoid: List[str] = Field(default_factory=list)
    suggested_approach: str
    reasoning: str


class EvaluationResult(BaseModel):
    empathy_score: float = Field(ge=0.0, le=10.0)
    human_likeness: float = Field(ge=0.0, le=10.0)
    safety_score: float = Field(ge=0.0, le=10.0)
    clarity_score: float = Field(ge=0.0, le=10.0)
    overall_score: float = Field(ge=0.0, le=10.0)
    feedback: str
    should_rewrite: bool = False
    rewrite_suggestion: Optional[str] = None


class HEIResponse(BaseModel):
    """Full structured output from HEI analysis + planning"""
    emotion: EmotionResult
    intent: IntentResult
    strategy: StrategyResult
    raw_message: str
    model_used: Optional[str] = None
