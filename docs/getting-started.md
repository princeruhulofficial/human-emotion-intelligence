# Getting Started with HEI

This guide will get you from zero to a working HEI integration in under 5 minutes.

## 1. Installation

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e ".[dev]"
```

## 2. Set your API Key

```bash
cp .env.example .env
```

Open `.env` and add your key.

### Recommended for testing: OpenRouter (has free models)

```env
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

Get a free key at [openrouter.ai](https://openrouter.ai).

### Or use official OpenAI

```env
OPENAI_API_KEY=sk-...
HEI_MODEL=gpt-4o-mini
```

## 3. Run the example

```bash
python examples/basic_usage.py
```

You should see emotion, intent, and strategy output for several example messages.

## 4. Use it in your code

```python
from hei import HEI

hei = HEI(
    api_key="your-key",
    base_url="https://openrouter.ai/api/v1",  # optional
    model="google/gemma-2-9b-it:free"
)

result = hei.analyze("I guess my startup is over.")

print("Primary emotion :", result.emotion.primary)
print("Hidden emotion  :", result.emotion.hidden)
print("Intensity       :", result.emotion.intensity)
print("Intent          :", result.intent.primary_intent)
print("Strategy        :", result.strategy.recommended_strategy)
print("Approach        :", result.strategy.suggested_approach)
print("Avoid           :", result.strategy.things_to_avoid)
```

## 5. Improve an existing LLM response

```python
analysis = hei.analyze(user_message)

# Your own LLM call
raw_reply = call_your_llm(user_message)

final_reply, evaluation = hei.improve_response(
    original_message=user_message,
    generated_response=raw_reply,
    strategy=analysis.strategy,
    max_attempts=1
)

print(final_reply)
print("Empathy score:", evaluation.empathy_score)
```

## Next Steps

- Read the [Architecture](architecture.md) to understand the internal flow
- Check the [API Reference](api-reference.md)
- See the [Philosophy](philosophy.md) behind HEI
