# API Reference

## Python

### `HEI`

Main entry point.

```python
from hei import HEI

hei = HEI(
    api_key: str | None = None,
    base_url: str | None = None,
    model: str = "gpt-4o-mini",
    client: OpenAI | None = None,
    timeout: float = 30.0,
    max_retries: int = 2,
)
```

#### Methods

##### `analyze(message: str) -> HEIResponse`

Runs the full pipeline: Emotion → Intent → Strategy.

Raises:
- `HEIValidationError` if message is empty / too long / invalid
- `HEIError` on LLM or unexpected failures

##### `evaluate_response(original_message, generated_response, strategy) -> EvaluationResult`

Scores a generated response.

##### `improve_response(original_message, generated_response, strategy, max_attempts=1) -> tuple[str, EvaluationResult]`

Evaluates and automatically rewrites if quality is low.

---

### Key Models

#### `EmotionResult`
- `primary`: PrimaryEmotion
- `secondary`: Optional[PrimaryEmotion]
- `hidden`: Optional[PrimaryEmotion]
- `intensity`: int (1-10)
- `confidence`: float (0-1)
- `reasoning`: str

#### `IntentResult`
- `primary_intent`: EmotionalIntent
- `secondary_intent`: Optional[EmotionalIntent]
- `confidence`: float
- `reasoning`: str

#### `StrategyResult`
- `current_emotion`: str
- `target_outcome`: str
- `recommended_strategy`: str
- `tone`: ToneConfig
- `things_to_avoid`: list[str]
- `suggested_approach`: str
- `reasoning`: str

#### `EvaluationResult`
- `empathy_score`: float (0-10)
- `human_likeness`: float (0-10)
- `safety_score`: float (0-10)
- `clarity_score`: float (0-10)
- `overall_score`: float (0-10)
- `feedback`: str
- `should_rewrite`: bool
- `rewrite_suggestion`: Optional[str]

---

## TypeScript

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({
  apiKey: string;
  baseURL?: string;
  model?: string;
  timeout?: number;      // ms, default 30000
  maxRetries?: number;   // default 2
});

const result = await hei.analyze(message: string);
const evaluation = await hei.evaluateResponse(...);
const { response, evaluation } = await hei.improveResponse(...);
```

Types are fully inferred via Zod schemas.
