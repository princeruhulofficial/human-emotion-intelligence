# Getting Started with HEI

## Installation

```bash
git clone https://github.com/princeruhulofficial/human-emotion-intelligence.git
cd human-emotion-intelligence
pip install -e ".[dev]"
```

## Configuration

Copy the example env file:

```bash
cp .env.example .env
```

### Using OpenRouter (Free)

```env
OPENAI_API_KEY=sk-or-v1-your-key
OPENAI_BASE_URL=https://openrouter.ai/api/v1
HEI_MODEL=google/gemma-2-9b-it:free
```

### Using Official OpenAI

```env
OPENAI_API_KEY=sk-...
HEI_MODEL=gpt-4o-mini
```

## Basic Usage (Python)

```python
from hei import HEI

hei = HEI(
    api_key="your-key",
    base_url="https://openrouter.ai/api/v1",  # optional
    model="google/gemma-2-9b-it:free"
)

result = hei.analyze("I guess my startup is over.")

print(result.emotion.primary)               # sadness
print(result.emotion.hidden)                # fear / disappointment
print(result.emotion.intensity)             # 7-9
print(result.intent.primary_intent)         # seeking_comfort
print(result.strategy.suggested_approach)
print(result.strategy.things_to_avoid)
```

## Improve an Existing Response

```python
analysis = hei.analyze(user_message)

# Your LLM generates something...
raw_reply = your_llm.generate(...)

final_reply, evaluation = hei.improve_response(
    original_message=user_message,
    generated_response=raw_reply,
    strategy=analysis.strategy,
    max_attempts=1
)

print(final_reply)
print("Empathy score:", evaluation.empathy_score)
```

## Running Tests

```bash
# Unit tests (no API key needed)
pytest tests/test_validation.py -v

# Golden set (needs API key)
export OPENAI_API_KEY=sk-...
pytest tests/test_golden.py -v -s
```
