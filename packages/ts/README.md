# @hei/sdk — TypeScript SDK

**Human Emotion Intelligence** for TypeScript / JavaScript.

## Install

```bash
npm install @hei/sdk
# or
pnpm add @hei/sdk
```

## Quick Start

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({
  apiKey: process.env.OPENAI_API_KEY!,
  baseURL: process.env.OPENAI_BASE_URL, // optional (OpenRouter, Groq, etc.)
  model: "gpt-4o-mini",
});

const result = await hei.analyze("I guess my startup is over.");

console.log(result.emotion.primary);        // "sadness"
console.log(result.emotion.hidden);         // "fear"
console.log(result.intent.primary_intent);  // "seeking_comfort"
console.log(result.strategy.suggested_approach);
```

## Full Pipeline Example

```ts
const analysis = await hei.analyze(userMessage);

// Your LLM generates a response using the strategy...
const llmResponse = await yourLLM.generate({
  system: `Follow this strategy: ${JSON.stringify(analysis.strategy)}`,
  user: userMessage,
});

// Evaluate + auto-improve if needed
const { response: finalResponse, evaluation } = await hei.improveResponse(
  userMessage,
  llmResponse,
  analysis.strategy
);

console.log(finalResponse);
console.log("Empathy score:", evaluation.empathy_score);
```

## OpenRouter (Free models)

```ts
const hei = new HEI({
  apiKey: "sk-or-v1-...",
  baseURL: "https://openrouter.ai/api/v1",
  model: "google/gemma-2-9b-it:free",
});
```

## API

- `analyze(message)` → full Emotion + Intent + Strategy
- `evaluateResponse(...)` → scores a response
- `rewrite(...)` → generates a better version
- `improveResponse(...)` → evaluate + auto-rewrite if needed

## License

MIT
