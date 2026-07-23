from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PrimaryEmotion(str, Enum):
    """Plutchik-inspired + product-useful labels (backward compatible)."""

    # Plutchik-ish core
    HAPPINESS = "happiness"  # ~joy
    TRUST = "trust"
    FEAR = "fear"
    SURPRISE = "surprise"
    SADNESS = "sadness"
    DISGUST = "disgust"
    ANGER = "anger"
    ANTICIPATION = "anticipation"

    # Extended / common in product use
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
    LOVE = "love"
    OPTIMISM = "optimism"
    DISAPPOINTMENT = "disappointment"
    BURNOUT = "burnout"
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


class ToneConfig(BaseModel):
    warmth: float = Field(default=0.7, ge=0.0, le=1.0)
    directness: float = Field(default=0.5, ge=0.0, le=1.0)
    formality: float = Field(default=0.4, ge=0.0, le=1.0)
    optimism: float = Field(default=0.5, ge=0.0, le=1.0)


class AppraisalSignals(BaseModel):
    """Lightweight OCC/appraisal-inspired signals (optional)."""

    goal_relevance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="How relevant the situation is to the user's goals (0-1)",
    )
    coping_potential: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Perceived ability to cope or act (0-1)",
    )
    agency: str = Field(
        default="unknown",
        description="Who/what is seen as causing the situation: self | other | circumstances | unknown",
    )


class EmotionResult(BaseModel):
    primary: PrimaryEmotion
    secondary: Optional[PrimaryEmotion] = None
    hidden: Optional[PrimaryEmotion] = None
    intensity: int = Field(ge=1, le=10, description="Emotion intensity from 1-10")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(description="Brief explanation of the detection")
    appraisal: Optional[AppraisalSignals] = Field(
        default=None,
        description="Optional appraisal dimensions for richer strategy planning",
    )


class IntentResult(BaseModel):
    primary_intent: EmotionalIntent
    secondary_intent: Optional[EmotionalIntent] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str


class StrategyResult(BaseModel):
    current_emotion: str
    target_outcome: str
    recommended_strategy: str
    tone: ToneConfig = Field(default_factory=ToneConfig)
    things_to_avoid: List[str] = Field(default_factory=list)
    suggested_approach: str
    reasoning: str


class EvaluationResult(BaseModel):
    empathy_score: float = Field(ge=0.0, le=10.0)
    human_likeness: float = Field(ge=0.0, le=10.0)
    safety_score: float = Field(ge=0.0, le=10.0)
    clarity_score: float = Field(ge=0.0, le=10.0)
    felt_understood_score: float = Field(
        default=5.0,
        ge=0.0,
        le=10.0,
        description="Primary product metric: would the user feel understood?",
    )
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
