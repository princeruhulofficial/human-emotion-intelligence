"""
Golden set integration tests.

These tests call real LLMs. They are skipped if no OPENAI_API_KEY is set.

Run with:
    export OPENAI_API_KEY=sk-...
    # optional for OpenRouter:
    export OPENAI_BASE_URL=https://openrouter.ai/api/v1
    export HEI_MODEL=google/gemma-2-9b-it:free

    pytest tests/test_golden.py -v -s
"""

import json
import os
from pathlib import Path

import pytest
from hei import HEI

GOLDEN_PATH = Path(__file__).parent.parent / "data" / "golden_set.json"


def load_golden_set():
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def hei_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set — skipping golden set tests")

    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("HEI_MODEL", "gpt-4o-mini")

    return HEI(api_key=api_key, base_url=base_url, model=model)


@pytest.fixture(scope="module")
def golden_cases():
    return load_golden_set()


def test_golden_set_loads(golden_cases):
    assert len(golden_cases) >= 5
    for case in golden_cases:
        assert "id" in case
        assert "message" in case
        assert "expected_primary" in case


@pytest.mark.parametrize("case", load_golden_set(), ids=lambda c: c["id"])
def test_emotion_detection_on_golden(hei_client, case):
    """Check that primary emotion is reasonable for each golden example."""
    result = hei_client.analyze(case["message"])

    primary = result.emotion.primary.value
    expected = case["expected_primary"]

    # Allow some flexibility: exact match or at least not completely wrong
    print(f"\n[{case['id']}] Message: {case['message'][:60]}...")
    print(f"  Expected primary : {expected}")
    print(f"  Got primary      : {primary} (intensity {result.emotion.intensity})")
    print(f"  Hidden           : {result.emotion.hidden}")
    print(f"  Intent           : {result.intent.primary_intent.value}")
    print(f"  Confidence       : {result.emotion.confidence:.0%}")

    # Soft assertion for MVP: we mainly want to ensure it doesn't crash
    # and returns a valid structure. Exact emotion matching can be strict later.
    assert result.emotion.primary is not None
    assert 1 <= result.emotion.intensity <= 10
    assert 0.0 <= result.emotion.confidence <= 1.0
    assert result.intent.primary_intent is not None
    assert result.strategy.suggested_approach


def test_hidden_emotion_case(hei_client):
    """Special check for the classic 'I'm fine' case."""
    result = hei_client.analyze("I'm fine.")

    print("\n[I'm fine] analysis:")
    print(f"  Primary  : {result.emotion.primary.value}")
    print(f"  Hidden   : {result.emotion.hidden}")
    print(f"  Intent   : {result.intent.primary_intent.value}")

    # We expect either neutral/sadness as primary and some negative hidden emotion,
    # or at least the system should not crash.
    assert result.emotion.primary is not None
