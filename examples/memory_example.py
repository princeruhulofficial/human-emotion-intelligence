"""
Emotional Memory example

Shows how HEI remembers emotional context across turns in a session.
"""

import os
from dotenv import load_dotenv
from hei import HEI

load_dotenv()

def main():
    hei = HEI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("HEI_MODEL", "gpt-4o-mini"),
    )

    session_id = "demo_user_001"

    turns = [
        "I guess my startup is over.",
        "I've been working on this for two years...",
        "I'm trying to stay positive though.",
        "Maybe I can start something new.",
    ]

    for i, msg in enumerate(turns, 1):
        print("=" * 60)
        print(f"Turn {i}: {msg}")
        print("-" * 60)

        result = hei.analyze(msg, session_id=session_id)

        print(f"Emotion   : {result.emotion.primary.value} (intensity {result.emotion.intensity})")
        if result.emotion.hidden:
            print(f"Hidden    : {result.emotion.hidden.value}")
        print(f"Intent    : {result.intent.primary_intent.value}")
        print(f"Strategy  : {result.strategy.recommended_strategy}")
        print(f"Approach  : {result.strategy.suggested_approach[:120]}...")

        shift = hei.get_mood_shift(session_id)
        if shift.shift_type.value != "none":
            print(f"\nMood shift detected: {shift.summary}")

        print()

    print("=" * 60)
    print("Full Emotional Timeline")
    print("=" * 60)
    for t in hei.memory.get_timeline(session_id):
        print(f"[{t.primary_emotion} | {t.intensity}/10] {t.message[:50]}...")


if __name__ == "__main__":
    main()
