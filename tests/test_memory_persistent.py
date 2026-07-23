"""Tests for persistent memory backends (SQLite). No LLM needed."""

import os
import tempfile
from pathlib import Path

import pytest

from hei.memory import EmotionalMemory, SQLiteStore, MoodShiftType
from hei.models import EmotionResult, IntentResult, PrimaryEmotion, EmotionalIntent


def make_emotion(primary: str, intensity: int = 5) -> EmotionResult:
    return EmotionResult(
        primary=PrimaryEmotion(primary),
        secondary=None,
        hidden=None,
        intensity=intensity,
        confidence=0.9,
        reasoning="test",
    )


def make_intent(intent: str = "seeking_comfort") -> IntentResult:
    return IntentResult(
        primary_intent=EmotionalIntent(intent),
        secondary_intent=None,
        confidence=0.8,
        reasoning="test",
    )


def test_sqlite_persists_across_instances():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "test.db")

        mem1 = EmotionalMemory(backend="sqlite", sqlite_path=db_path)
        mem1.add_turn("s1", "I failed", make_emotion("sadness", 8), make_intent())
        mem1.add_turn("s1", "Trying again", make_emotion("hope", 5), make_intent("sharing"))

        # New instance, same DB file
        mem2 = EmotionalMemory(backend="sqlite", sqlite_path=db_path)
        timeline = mem2.get_timeline("s1")

        assert len(timeline) == 2
        assert timeline[0].primary_emotion == "sadness"
        assert timeline[1].primary_emotion == "hope"

        shift = mem2.detect_mood_shift("s1")
        assert shift.shift_type == MoodShiftType.IMPROVING


def test_sqlite_clear_session():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "test.db")
        mem = EmotionalMemory(backend="sqlite", sqlite_path=db_path)
        mem.add_turn("s1", "hi", make_emotion("happiness", 6), make_intent("sharing"))
        mem.clear_session("s1")
        assert mem.get_timeline("s1") == []


def test_from_env_sqlite(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db_path = str(Path(tmp) / "env.db")
        monkeypatch.setenv("HEI_MEMORY_BACKEND", "sqlite")
        monkeypatch.setenv("HEI_MEMORY_PATH", db_path)

        mem = EmotionalMemory.from_env()
        mem.add_turn("env_s", "test", make_emotion("neutral", 3), make_intent("sharing"))

        mem2 = EmotionalMemory.from_env()
        assert len(mem2.get_timeline("env_s")) == 1


def test_in_memory_still_works():
    mem = EmotionalMemory(backend="memory")
    mem.add_turn("s1", "hello", make_emotion("curiosity", 4), make_intent("asking_question"))
    assert len(mem.get_timeline("s1")) == 1
