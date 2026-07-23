from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .models import EmotionResult, IntentResult

logger = logging.getLogger("hei.memory")


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
    salience: float = 0.5  # 0-1 emotional importance for retrieval

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
            "salience": self.salience,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryTurn":
        return cls(
            timestamp=float(data["timestamp"]),
            message=data["message"],
            primary_emotion=data["primary_emotion"],
            secondary_emotion=data.get("secondary_emotion"),
            hidden_emotion=data.get("hidden_emotion"),
            intensity=int(data["intensity"]),
            confidence=float(data["confidence"]),
            intent=data["intent"],
            reasoning=data.get("reasoning", ""),
            salience=float(data.get("salience", 0.5)),
        )


class MoodShiftType(str, Enum):
    NONE = "none"
    IMPROVING = "improving"
    DECLINING = "declining"
    INTENSIFYING = "intensifying"
    STABILIZING = "stabilizing"
    MIXED = "mixed"


@dataclass
class MoodShift:
    shift_type: MoodShiftType
    from_emotion: str
    to_emotion: str
    from_intensity: int
    to_intensity: int
    summary: str


POSITIVE = {
    "happiness",
    "excitement",
    "hope",
    "pride",
    "gratitude",
    "curiosity",
    "trust",
    "love",
    "optimism",
    "anticipation",
    "surprise",
}
NEGATIVE = {
    "sadness",
    "anger",
    "fear",
    "anxiety",
    "shame",
    "guilt",
    "loneliness",
    "frustration",
    "disgust",
    "disappointment",
    "burnout",
}


def compute_salience(emotion: EmotionResult, intent: IntentResult) -> float:
    """Heuristic emotional salience for memory retrieval (0-1)."""
    intensity_n = emotion.intensity / 10.0
    conf = emotion.confidence
    hidden_boost = 0.15 if emotion.hidden else 0.0
    high_stakes_intents = {
        "seeking_comfort",
        "venting",
        "celebrating",
        "seeking_validation",
    }
    intent_boost = 0.1 if intent.primary_intent.value in high_stakes_intents else 0.0
    raw = 0.45 * intensity_n + 0.25 * conf + hidden_boost + intent_boost
    return max(0.0, min(1.0, raw))


class MemoryStore(ABC):
    @abstractmethod
    def load(self, session_id: str) -> List[MemoryTurn]:
        ...

    @abstractmethod
    def save(self, session_id: str, turns: List[MemoryTurn]) -> None:
        ...

    @abstractmethod
    def delete(self, session_id: str) -> None:
        ...


class InMemoryStore(MemoryStore):
    def __init__(self) -> None:
        self._data: Dict[str, List[MemoryTurn]] = {}

    def load(self, session_id: str) -> List[MemoryTurn]:
        return list(self._data.get(session_id, []))

    def save(self, session_id: str, turns: List[MemoryTurn]) -> None:
        self._data[session_id] = list(turns)

    def delete(self, session_id: str) -> None:
        self._data.pop(session_id, None)


class SQLiteStore(MemoryStore):
    def __init__(self, path: str = "hei_memory.db") -> None:
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS turns (
                    session_id TEXT NOT NULL,
                    idx INTEGER NOT NULL,
                    payload TEXT NOT NULL,
                    PRIMARY KEY (session_id, idx)
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id)"
            )

    def load(self, session_id: str) -> List[MemoryTurn]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT payload FROM turns WHERE session_id = ? ORDER BY idx ASC",
                (session_id,),
            ).fetchall()
        return [MemoryTurn.from_dict(json.loads(r[0])) for r in rows]

    def save(self, session_id: str, turns: List[MemoryTurn]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            conn.executemany(
                "INSERT INTO turns (session_id, idx, payload) VALUES (?, ?, ?)",
                [
                    (session_id, i, json.dumps(t.to_dict(), ensure_ascii=False))
                    for i, t in enumerate(turns)
                ],
            )

    def delete(self, session_id: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))


class RedisStore(MemoryStore):
    def __init__(self, url: str = "redis://localhost:6379/0", key_prefix: str = "hei:mem:") -> None:
        try:
            import redis  # type: ignore
        except ImportError as e:
            raise ImportError(
                "Redis backend requires the 'redis' package. Install with: pip install redis"
            ) from e

        self._client = redis.Redis.from_url(url, decode_responses=True)
        self.prefix = key_prefix

    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    def load(self, session_id: str) -> List[MemoryTurn]:
        raw = self._client.get(self._key(session_id))
        if not raw:
            return []
        data = json.loads(raw)
        return [MemoryTurn.from_dict(item) for item in data]

    def save(self, session_id: str, turns: List[MemoryTurn]) -> None:
        payload = json.dumps([t.to_dict() for t in turns], ensure_ascii=False)
        self._client.set(self._key(session_id), payload)

    def delete(self, session_id: str) -> None:
        self._client.delete(self._key(session_id))


class EmotionalMemory:
    def __init__(
        self,
        max_turns_per_session: int = 50,
        backend: str = "memory",
        sqlite_path: str = "hei_memory.db",
        redis_url: str = "redis://localhost:6379/0",
        store: Optional[MemoryStore] = None,
    ):
        self.max_turns = max_turns_per_session

        if store is not None:
            self._store = store
        else:
            backend = backend.lower().strip()
            if backend == "sqlite":
                self._store = SQLiteStore(sqlite_path)
                logger.info("EmotionalMemory using SQLite (%s)", sqlite_path)
            elif backend == "redis":
                self._store = RedisStore(redis_url)
                logger.info("EmotionalMemory using Redis (%s)", redis_url)
            else:
                self._store = InMemoryStore()
                logger.info("EmotionalMemory using in-memory store")

    @classmethod
    def from_env(cls, max_turns_per_session: int = 50) -> "EmotionalMemory":
        backend = os.getenv("HEI_MEMORY_BACKEND", "memory").lower()
        sqlite_path = os.getenv("HEI_MEMORY_PATH", "hei_memory.db")
        redis_url = os.getenv("HEI_REDIS_URL", "redis://localhost:6379/0")
        return cls(
            max_turns_per_session=max_turns_per_session,
            backend=backend,
            sqlite_path=sqlite_path,
            redis_url=redis_url,
        )

    def add_turn(
        self,
        session_id: str,
        message: str,
        emotion: EmotionResult,
        intent: IntentResult,
    ) -> MemoryTurn:
        turns = self._store.load(session_id)

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
            salience=compute_salience(emotion, intent),
        )
        turns.append(turn)

        if len(turns) > self.max_turns:
            turns = turns[-self.max_turns :]

        self._store.save(session_id, turns)
        return turn

    def get_timeline(self, session_id: str) -> List[MemoryTurn]:
        return self._store.load(session_id)

    def get_last_turn(self, session_id: str) -> Optional[MemoryTurn]:
        timeline = self.get_timeline(session_id)
        return timeline[-1] if timeline else None

    def get_recent_emotions(self, session_id: str, n: int = 5) -> List[str]:
        return [t.primary_emotion for t in self.get_timeline(session_id)[-n:]]

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

        prev, curr = timeline[-2], timeline[-1]
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
            summary = (
                f"Mood moved from {prev.primary_emotion} ({prev.intensity}) "
                f"to {curr.primary_emotion} ({curr.intensity})."
            )

        return MoodShift(
            shift_type=shift,
            from_emotion=prev.primary_emotion,
            to_emotion=curr.primary_emotion,
            from_intensity=prev.intensity,
            to_intensity=curr.intensity,
            summary=summary,
        )

    def get_context_for_strategy(self, session_id: str) -> str:
        timeline = self.get_timeline(session_id)
        if not timeline:
            return "No previous emotional context."

        # Prefer recent turns, weighted by salience
        recent = timeline[-8:]
        ranked = sorted(recent, key=lambda t: (t.salience, t.timestamp), reverse=True)[:4]
        ranked_chrono = sorted(ranked, key=lambda t: t.timestamp)

        lines = []
        for t in ranked_chrono:
            hidden = f", hidden={t.hidden_emotion}" if t.hidden_emotion else ""
            lines.append(
                f"- {t.primary_emotion} (intensity {t.intensity}, salience {t.salience:.2f})"
                f"{hidden} | intent={t.intent}"
            )

        shift = self.detect_mood_shift(session_id)
        shift_text = (
            f"\nRecent mood shift: {shift.summary}"
            if shift.shift_type != MoodShiftType.NONE
            else ""
        )
        return "Recent emotional timeline (salience-aware):\n" + "\n".join(lines) + shift_text

    def clear_session(self, session_id: str) -> None:
        self._store.delete(session_id)

    def _polarity(self, emotion: str) -> str:
        if emotion in POSITIVE:
            return "positive"
        if emotion in NEGATIVE:
            return "negative"
        return "neutral"
