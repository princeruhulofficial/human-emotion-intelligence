# @hei/sdk — TypeScript SDK

**Human Emotion Intelligence** for TypeScript / JavaScript.

## Install

```bash
npm install @hei/sdk
# or from monorepo
cd packages/ts && npm install && npm run build
```

## Quick Start

```ts
import { HEI } from "@hei/sdk";

const hei = new HEI({
  apiKey: process.env.OPENAI_API_KEY!,
  baseURL: process.env.OPENAI_BASE_URL, // optional (OpenRouter, etc.)
  model: "gpt-4o-mini",
});

// Without memory
const result = await hei.analyze("I guess my startup is over.");

// With Emotional Memory (session)
const r1 = await hei.analyze("I guess my startup is over.", "user_123");
const r2 = await hei.analyze("I'm trying to stay positive", "user_123");

const shift = hei.getMoodShift("user_123");
console.log(shift.summary);

const timeline = hei.memory.getTimeline("user_123");
```

## Emotional Memory API

```ts
hei.memory.getTimeline(sessionId)
hei.memory.detectMoodShift(sessionId)
hei.memory.getContextForStrategy(sessionId)
hei.memory.clearSession(sessionId)
hei.getMoodShift(sessionId)  // convenience
```

## Full Pipeline + Improve

```ts
const analysis = await hei.analyze(userMessage, sessionId);

// Your LLM generates a response using the strategy...
const llmResponse = await yourLLM.generate({ ... });

const { response: finalResponse, evaluation } = await hei.improveResponse(
  userMessage,
  llmResponse,
  analysis.strategy
);
```

## OpenRouter (Free models)

```ts
const hei = new HEI({
  apiKey: "sk-or-v1-...",
  baseURL: "https://openrouter.ai/api/v1",
  model: "google/gemma-2-9b-it:free",
});
```

## Tests

```bash
npm test
```

## License

MIT
