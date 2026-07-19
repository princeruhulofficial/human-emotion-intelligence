"""
Basic usage example for Human Emotion Intelligence (HEI)

Supports:
- Official OpenAI
- OpenRouter (free models available)
- Any OpenAI-compatible endpoint (Groq, Together, local vLLM, etc.)
"""

import os
from dotenv import load_dotenv
from hei import HEI

load_dotenv()

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")  # None = official OpenAI
    model = os.getenv("HEI_MODEL", "gpt-4o-mini")

    if not api_key:
        print("Error: OPENAI_API_KEY not found.")
        print("Please copy .env.example to .env and add your key.")
        print("For free testing, use OpenRouter: https://openrouter.ai")
        return

    print(f"Using model : {model}")
    print(f"Base URL    : {base_url or 'https://api.openai.com/v1 (official)'}")
    print()

    hei = HEI(
        api_key=api_key,
        base_url=base_url,
        model=model,
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

        try:
            result = hei.analyze(msg)

            print(f"Primary Emotion : {result.emotion.primary.value} (intensity {result.emotion.intensity}/10)")
            if result.emotion.secondary:
                print(f"Secondary       : {result.emotion.secondary.value}")
            if result.emotion.hidden:
                print(f"Hidden Emotion  : {result.emotion.hidden.value}")
            print(f"Confidence      : {result.emotion.confidence:.0%}")
            print(f"Intent          : {result.intent.primary_intent.value}")
            print(f"\nStrategy        : {result.strategy.recommended_strategy}")
            print(f"Target Outcome  : {result.strategy.target_outcome}")
            print(f"Approach        : {result.strategy.suggested_approach}")
            if result.strategy.things_to_avoid:
                print(f"Things to avoid : {', '.join(result.strategy.things_to_avoid)}")
        except Exception as e:
            print(f"Error: {e}")

        print()


if __name__ == "__main__":
    main()
