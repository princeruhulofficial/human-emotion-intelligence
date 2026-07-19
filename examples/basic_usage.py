"""
Basic usage example for Human Emotion Intelligence (HEI)
"""

import os
from dotenv import load_dotenv
from hei import HEI

load_dotenv()

def main():
    # Initialize HEI (uses OPENAI_API_KEY from environment by default)
    hei = HEI(
        api_key=os.getenv("OPENAI_API_KEY"),
        # base_url="https://api.groq.com/openai/v1",  # example for other providers
        model="gpt-4o-mini",
    )

    messages = [
        "I guess my startup is over.",
        "I'm fine.",
        "I just got the job!!!",
        "Nobody even asked how I was today.",
    ]

    for msg in messages:
        print("=" * 60)
        print(f"User: {msg}")
        print("-" * 60)

        result = hei.analyze(msg)

        print(f"Primary Emotion : {result.emotion.primary.value} (intensity {result.emotion.intensity}/10)")
        if result.emotion.hidden:
            print(f"Hidden Emotion  : {result.emotion.hidden.value}")
        print(f"Confidence      : {result.emotion.confidence:.0%}")
        print(f"Intent          : {result.intent.primary_intent.value}")
        print(f"\nStrategy        : {result.strategy.recommended_strategy}")
        print(f"Target Outcome  : {result.strategy.target_outcome}")
        print(f"Approach        : {result.strategy.suggested_approach}")
        print(f"Things to avoid : {', '.join(result.strategy.things_to_avoid)}")
        print()


if __name__ == "__main__":
    main()
