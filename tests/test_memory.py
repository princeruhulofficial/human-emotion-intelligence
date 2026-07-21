"""Unit tests for Emotional Memory (no LLM needed)"""

import pytest
from hei.memory import EmotionalMemory, MoodShiftType
from hei.models import (
    EmotionResult,
    IntentResult,
    PrimaryEmotion,
    EmotionalIntent,
)


def make_emotion(primary: str, intensity: int = 5, hidden: str | None = None) -> EmotionResult:
    return EmotionResult(
        primary=PrimaryEmotion(primary),
        secondary=None,
        hidden=PrimaryEmotion(hidden) if hidden else None,
        intensity=intensity,
        confidence=0.85,
        reasoning="test",
    )


def make_intent(intent: str = "seeking_comfort") -> IntentResult:
    return IntentResult(
        primary_intent=EmotionalIntent(intent),
        secondary_intent=None,
        confidence=0.8,
        reasoning="test",
    )


@pytest.fixture
def memory():
    return EmotionalMemory()


def test_empty_timeline(memory):
    assert memory.get_timeline("s1") == []
    assert memory.get_last_turn("s1") is None


def test_add_and_get_timeline(memory):
    memory.add_turn("s1", "I failed", make_emotion("sadness", 8), make_intent())
    memory.add_turn("s1", "Maybe tomorrow", make_emotion("hope", 4), make_intent("sharing"))

    timeline = memory.get_timeline("s1")
    assert len(timeline) == 2
    assert timeline[0].primary_emotion == "sadness"
    assert timeline[1].primary_emotion == "hope"


def test_improving_mood_shift(memory):
    memory.add_turn("s1", "Everything is ruined", make_emotion("sadness", 9), make_intent())
    memory.add_turn("s1", "I got a new opportunity", make_emotion("hope", 7), make_intent("celebrating"))

    shift = memory.detect_mood_shift("s1")
    assert shift.shift_type == MoodShiftType.IMPROVING
    assert shift.from_emotion == "sadness"
    assert shift.to_emotion == "hope"


def test_declining_mood_shift(memory):
    memory.add_turn("s1", "I got the job!", make_emotion("excitement", 9), make_intent("celebrating"))
    memory.add_turn("s1", "They rescinded the offer", make_emotion("sadness", 8), make_intent())

    shift = memory.detect_mood_shift("s1")
    assert shift.shift_type == MoodShiftType.DECLINING


def test_intensifying(memory):
    memory.add_turn("s1", "I'm annoyed", make_emotion("anger", 4), make_intent("venting"))
    memory.add_turn("s1", "I'm furious", make_emotion("anger", 9), make_intent("venting"))

    shift = memory.detect_mood_shift("s1")
    assert shift.shift_type == MoodShiftType.INTENSIFYING


def test_none_with_single_turn(memory):
    memory.add_turn("s1", "Hello", make_emotion("neutral", 2), make_intent("sharing"))
    shift = memory.detect_mood_shift("s1")
    assert shift.shift_type == MoodShiftType.NONE


def test_strategy_context(memory):
    memory.add_turn("s1", "I failed", make_emotion("sadness", 8, "fear"), make_intent())
    memory.add_turn("s1", "Trying to stay positive", make_emotion("hope", 5), make_intent("sharing"))

    ctx = memory.get_context_for_strategy("s1")
    assert "sadness" in ctx
    assert "hope" in ctx
    assert "mood shift" in ctx.lower() or "improved" in ctx.lower()


def test_max_turns():
    mem = EmotionalMemory(max_turns_per_session=3)
    for i in range(5):
        mem.add_turn("s1", f"msg {i}", make_emotion("neutral", 3), make_intent())
    assert len(mem.get_timeline("s1")) == 3


def test_session_isolation(memory):
    memory.add_turn("s1", "sad", make_emotion("sadness", 7), make_intent())
    memory.add_turn("s2", "happy", make_emotion("happiness", 8), make_intent("celebrating"))

    assert memory.get_timeline("s1")[0].primary_emotion == "sadness"
    assert memory.get_timeline("s2")[0].primary_emotion == "happiness"


def test_clear_session(memory):
    memory.add_turn("s1", "hi", make_emotion("happiness", 6), make_intent("sharing"))
    memory.clear_session("s1")
    assert memory.get_timeline("s1") == []
