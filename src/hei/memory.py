from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

from .models import EmotionResult, IntentResult, PrimaryEmotion


@dataclass
class MemoryTurn:
    """One turn in a conversation session."""
    timestamp: float
    message: str
    primary_emotion: str
    secondary_emotion: Optional[str]
    hidden_emotion: Optional[str]
    intensity: int
    confidence: float
    intent: str
    reasoning: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "message": self.message,
            "primary_emotion": self.primary_emotion,
            "secondary_emotion": self.secondary_emotion,
            "hidden_emotion": self.hidden_emotion,
            "intensity": self.intensity,
            "confidence": self.confidence,
            "intent": self.intent,
            "reasoning": self.reasoning,
        }


class MoodShiftType(str, Enum):
    NONE = "none"
    IMPROVING = "improving"          # negative → more positive
    DECLINING = "declining"          # positive → more negative
    INTENSIFYING = "intensifying"    # same polarity but stronger
    STABILIZING = "stabilizing"      # high intensity → lower
    MIXED = "mixed"


@dataclass
class MoodShift:
    shift_type: MoodShiftType
    from_emotion: str
    to_emotion: str
    from_intensity: int
    to_intensity: int
    summary: str


# Simple polarity map for mood shift detection
POSITIVE = {"happiness", "excitement", "hope", "pride", "gratitude", "curiosity"}
NEGATIVE = {"sadness", "anger", "fear", "anxiety", "shame", "guilt", "loneliness", "frustration"}


class EmotionalMemory:
    """
    In-memory emotional timeline store.

    Keyed by session_id.
    Later this can be swapped for Redis / Postgres without changing the HEI API.
    """

    def __init__(self, max_turns_per_session: int = 50):
        self._store: Dict[str, List[MemoryTurn]] = {}
        self.max_turns = max_turns_per_session

    def add_turn(
        self,
        session_id: str,
        message: str,
        emotion: EmotionResult,
        intent: IntentResult,
    ) -> MemoryTurn:
        if session_id not in self._store:
            self._store[session_id] = []

        turn = MemoryTurn(
            timestamp=time.time(),
            message=message,
            primary_emotion=emotion.primary.value,
            secondary_emotion=emotion.secondary.value if emotion.secondary else None,
            hidden_emotion=emotion.hidden.value if emotion.hidden else None,
            intensity=emotion.intensity,
            confidence=emotion.confidence,
            intent=intent.primary_intent.value,
            reasoning=emotion.reasoning,
        )

        self._store[session_id].append(turn)

        # Keep only recent turns
        if len(self._store[session_id]) > self.max_turns:
            self._store[session_id] = self._store[session_id][-self.max_turns :]

        return turn

    def get_timeline(self, session_id: str) -> List[MemoryTurn]:
        return list(self._store.get(session_id, []))

    def get_last_turn(self, session_id: str) -> Optional[MemoryTurn]:
        timeline = self._store.get(session_id, [])
        return timeline[-1] if timeline else None

    def get_recent_emotions(self, session_id: str, n: int = 5) -> List[str]:
        timeline = self.get_timeline(session_id)
        return [t.primary_emotion for t in timeline[-n:]]

    def detect_mood_shift(self, session_id: str) -> MoodShift:
        timeline = self.get_timeline(session_id)

        if len(timeline) < 2:
            return MoodShift(
                shift_type=MoodShiftType.NONE,
                from_emotion="",
                to_emotion="",
                from_intensity=0,
                to_intensity=0,
                summary="Not enough turns to detect a shift.",
            )

        prev = timeline[-2]
        curr = timeline[-1]

        prev_pol = self._polarity(prev.primary_emotion)
        curr_pol = self._polarity(curr.primary_emotion)

        if prev_pol == "negative" and curr_pol == "positive":
            shift = MoodShiftType.IMPROVING
            summary = f"Mood improved from {prev.primary_emotion} to {curr.primary_emotion}."
        elif prev_pol == "positive" and curr_pol == "negative":
            shift = MoodShiftType.DECLINING
            summary = f"Mood declined from {prev.primary_emotion} to {curr.primary_emotion}."
        elif prev.primary_emotion == curr.primary_emotion and curr.intensity > prev.intensity + 2:
            shift = MoodShiftType.INTENSIFYING
            summary = f"{curr.primary_emotion} is intensifying ({prev.intensity} → {curr.intensity})."
        elif prev.primary_emotion == curr.primary_emotion and curr.intensity < prev.intensity - 2:
            shift = MoodShiftType.STABILIZING
            summary = f"{curr.primary_emotion} is stabilizing ({prev.intensity} → {curr.intensity})."
        else:
            shift = MoodShiftType.MIXED
            summary = f"Mood moved from {prev.primary_emotion} ({prev.intensity}) to {curr.primary_emotion} ({curr.intensity})."

        return MoodShift(
            shift_type=shift,
            from_emotion=prev.primary_emotion,
            to_emotion=curr.primary_emotion,
            from_intensity=prev.intensity,
            to_intensity=curr.intensity,
            summary=summary,
        )

    def get_context_for_strategy(self, session_id: str) -> str:
        """Return a short text summary of recent emotional context for the Strategy Planner."""
        timeline = self.get_timeline(session_id)
        if not timeline:
            return "No previous emotional context."

        recent = timeline[-4:]  # last few turns
        lines = []
        for t in recent:
            hidden = f", hidden={t.hidden_emotion}" if t.hidden_emotion else ""
            lines.append(
                f"- {t.primary_emotion} (intensity {t.intensity}){hidden} | intent={t.intent}"
            )

        shift = self.detect_mood_shift(session_id)
        shift_text = f"\nRecent mood shift: {shift.summary}" if shift.shift_type != MoodShiftType.NONE else ""

        return "Recent emotional timeline:\n" + "\n".join(lines) + shift_text

    def clear_session(self, session_id: str) -> None:
        if session_id in self._store:
            del self._store[session_id]

    def _polarity(self, emotion: str) -> str:
        if emotion in POSITIVE:
            return "positive"
        if emotion in NEGATIVE:
            return "negative"
        return "neutral"
