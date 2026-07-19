from hei.models import (
    PrimaryEmotion,
    EmotionalIntent,
    EmotionResult,
    IntentResult,
    StrategyResult,
)


def test_emotion_result():
    result = EmotionResult(
        primary=PrimaryEmotion.SADNESS,
        secondary=PrimaryEmotion.FRUSTRATION,
        hidden=PrimaryEmotion.FEAR,
        intensity=8,
        confidence=0.87,
        reasoning="User is expressing loss with underlying fear",
    )
    assert result.primary == PrimaryEmotion.SADNESS
    assert result.intensity == 8
    assert 0 <= result.confidence <= 1


def test_intent_result():
    result = IntentResult(
        primary_intent=EmotionalIntent.SEEKING_COMFORT,
        confidence=0.81,
        reasoning="Looking for emotional support after setback",
    )
    assert result.primary_intent == EmotionalIntent.SEEKING_COMFORT
